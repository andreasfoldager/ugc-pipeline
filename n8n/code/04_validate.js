// Validate Claude output: AI output is untrusted until it has been checked.
// The same code runs in two nodes: "Validate Claude output" (ATTEMPT 1) and "Validate retry" (ATTEMPT 2).
//  1. Parse the JSON (tolerates code fences or stray text around it).
//  2. Check every required field and allowed value.
//  3. Apply hard guardrails that don't depend on the model behaving:
//     - a SKU that isn't in the catalogue is removed (never show a wrong product)
//     - a quote that isn't a verbatim excerpt of the original text is removed (never alter reviews)
//     - a quote containing an email or phone number is removed
//     - any PII means the item can't be auto-approved
//  4. Items that fail go to a retry (attempt 1) or to the error list (attempt 2).

const ATTEMPT = __ATTEMPT__;

const batches = $('Build Claude batches').all();
const catalogue = batches[0].json.catalogue;
const SKUS = new Set(catalogue.map((p) => p.sku));

const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i;
const PHONE = /(?:\+\d{2}[\s-]?)?(?:\d[\s-]?){7,10}\d/;
const LANGS = ['da', 'sv', 'no', 'en'];

// ---------- parsing ----------
function parseResponse(body) {
  if (!body || body.error) {
    const msg = body && body.error ? (body.error.message || JSON.stringify(body.error)) : 'empty response';
    return { results: null, problem: `API error: ${msg}` };
  }
  const blocks = Array.isArray(body.content) ? body.content : [];
  // The model may return thinking blocks before the answer: only the text blocks are the answer.
  let text = blocks.filter((b) => b.type === 'text').map((b) => b.text).join('\n');
  if (!text) return { results: null, problem: 'no text in response' };
  text = text.replace(/```(?:json)?/gi, '');
  const start = text.search(/[\[{]/);
  const end = Math.max(text.lastIndexOf('}'), text.lastIndexOf(']'));
  if (start === -1 || end <= start) return { results: null, problem: 'no JSON found in response' };
  try {
    const parsed = JSON.parse(text.slice(start, end + 1));
    const results = Array.isArray(parsed) ? parsed : parsed.results;
    if (!Array.isArray(results)) return { results: null, problem: 'JSON has no "results" array' };
    return { results, problem: null };
  } catch (e) {
    const cut = body.stop_reason === 'max_tokens' ? ' (response was cut off at max_tokens)' : '';
    return { results: null, problem: `invalid JSON${cut}: ${e.message}` };
  }
}

// ---------- excerpt check ----------
const norm = (s) => String(s).normalize('NFC').toLowerCase().replace(/\s+/g, ' ').trim();
function isExcerpt(quote, original) {
  const text = norm(original);
  const fragments = norm(quote)
    .replace(/^["'“”«»]+|["'“”«»]+$/g, '')
    .split(/\s*(?:…|\.\.\.)\s*/)
    .map((f) => f.replace(/^[\s.,!?;:]+|[\s.,!?;:]+$/g, ''))
    .filter(Boolean);
  return fragments.length > 0 && fragments.every((f) => text.includes(f));
}

// ---------- per-item check ----------
function check(r, ugc) {
  const problems = [];
  const num = (v) => (typeof v === 'number' ? v : Number(v));
  const conf = num(r.match_confidence);
  const qScore = num(r.quote_score);

  if (r.matched_sku !== null && typeof r.matched_sku !== 'string') problems.push('matched_sku must be a string or null');
  if (!Number.isFinite(conf) || conf < 0 || conf > 1) problems.push('match_confidence must be 0-1');
  if (!['positive', 'neutral', 'negative'].includes(r.sentiment)) problems.push(`bad sentiment "${r.sentiment}"`);
  if (!['approve', 'review', 'reject'].includes(r.moderation)) problems.push(`bad moderation "${r.moderation}"`);
  if (typeof r.contains_pii !== 'boolean') problems.push('contains_pii must be boolean');
  if (typeof r.needs_customer_service !== 'boolean') problems.push('needs_customer_service must be boolean');
  if (!Number.isFinite(qScore) || qScore < 0 || qScore > 1) problems.push('quote_score must be 0-1');
  if (typeof r.suggested_quote !== 'string') problems.push('suggested_quote must be a string');
  if (problems.length) return { valid: false, problems };

  const guardrails = [];
  let sku = r.matched_sku ? r.matched_sku.trim() : null;
  let confidence = conf;
  if (sku && !SKUS.has(sku)) {
    guardrails.push(`invented SKU "${sku}" removed`);
    sku = null;
    confidence = 0;
  }

  let quote = r.suggested_quote.trim();
  let quoteScore = qScore;
  if (quote && !isExcerpt(quote, ugc.text)) {
    guardrails.push('quote was not a verbatim excerpt, removed');
    quote = '';
  }
  if (quote && (EMAIL.test(quote) || PHONE.test(quote))) {
    guardrails.push('quote contained personal data, removed');
    quote = '';
  }
  if (!quote) quoteScore = 0;

  const pii = ugc.pii_detected || r.contains_pii === true;
  let moderation = r.moderation;
  let moderationReason = r.moderation_reason || '';
  if (pii && moderation === 'approve') {
    guardrails.push('PII found, moderation raised to review');
    moderation = 'review';
    moderationReason = moderationReason || 'contains personal data';
  }

  return {
    valid: true,
    record: {
      id: ugc.id,
      source: ugc.source,
      rating: ugc.rating,
      media: ugc.media,
      author_handle: ugc.author_handle,
      created_at: ugc.created_at,
      text: ugc.text,
      language: LANGS.includes(r.language) ? r.language : ugc.language_hint,
      matched_sku: sku,
      match_confidence: Math.round(confidence * 100) / 100,
      match_reason: r.match_reason || '',
      sentiment: r.sentiment,
      topics: (Array.isArray(r.topics) ? r.topics : []).map((t) => String(t).toLowerCase().trim()).filter(Boolean).slice(0, 3),
      moderation,
      moderation_reason: moderationReason,
      contains_pii: pii,
      pii_detected_by_regex: ugc.pii_detected,
      needs_customer_service: r.needs_customer_service,
      cs_reason: r.cs_reason || '',
      quote_score: Math.round(quoteScore * 100) / 100,
      suggested_quote: quote,
      quote_language: quote ? (r.quote_language || r.language || '') : '',
      guardrails,
      attempt: ATTEMPT,
    },
  };
}

// ---------- main ----------
let ok = [];
let errors = [];
let expectedGroups;
if (ATTEMPT === 1) {
  expectedGroups = batches.map((b) => b.json.ugc_items); // one HTTP response per batch, same order
} else {
  const first = $('Validate Claude output').first().json;
  ok = [...first.ok];
  errors = [...first.errors];
  expectedGroups = [first.retry];
}

const retry = [];
$input.all().forEach((response, i) => {
  const expected = expectedGroups[i] || [];
  const { results, problem } = parseResponse(response.json);
  const byId = new Map((results || []).filter((r) => r && r.id).map((r) => [r.id, r]));
  for (const ugc of expected) {
    const r = byId.get(ugc.id);
    const res = r ? check(r, ugc) : { valid: false, problems: [problem || 'item missing from response'] };
    if (res.valid) ok.push(res.record);
    else if (ATTEMPT === 1) retry.push({ ...ugc, problems: res.problems });
    else errors.push({ id: ugc.id, source: ugc.source, author_handle: ugc.author_handle, created_at: ugc.created_at, text: ugc.text, problems: res.problems.join('; ') });
  }
});

// Build one retry request for everything that failed, reusing the original prompt.
let retry_request_body = null;
if (retry.length) {
  const b0 = batches[0].json;
  const items = retry.map((u) => ({
    id: u.id, source: u.source, language_hint: u.language_hint, rating: u.rating, text: u.text,
    pii_detected_by_regex: u.pii_detected,
  }));
  const note = '\n\nThis is a retry: your previous answer for these items could not be used ('
    + [...new Set(retry.flatMap((u) => u.problems))].join('; ')
    + '). Return only the JSON object, exactly as specified.';
  retry_request_body = {
    ...b0.request_body,
    messages: [{ role: 'user', content: b0.user_template.split('__ITEMS__').join(JSON.stringify(items, null, 1)) + note }],
  };
}

return [{ json: { ok, retry, errors, retry_count: retry.length, retry_request_body } }];
