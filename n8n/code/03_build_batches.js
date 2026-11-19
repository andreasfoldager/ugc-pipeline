// Build Claude batches: groups the UGC into batches of `batch_size` and builds one
// Anthropic Messages API request per batch. The next node (HTTP Request) runs once per batch.
// Fewer, bigger calls = lower cost and latency than one call per review.

const settings = $('Settings').first().json;
const csvText = $('Get products.csv').first().json.data;

// --- tiny CSV parser (handles quoted fields with commas) ---
function parseCsv(text) {
  const rows = [];
  let row = [], field = '', inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') inQuotes = false;
      else field += c;
    } else if (c === '"') inQuotes = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); field = '';
      if (row.some((v) => v !== '')) rows.push(row);
      row = [];
    } else field += c;
  }
  row.push(field);
  if (row.some((v) => v !== '')) rows.push(row);
  const [header, ...data] = rows;
  return data.map((r) => Object.fromEntries(header.map((h, i) => [h.trim(), (r[i] || '').trim()])));
}

const catalogue = parseCsv(csvText);

// Compact catalogue for the prompt: only what matching needs.
// Brand is included so Claude knows e.g. "Fjordhus" is one of the shop's own brands.
const catalogueBlock = catalogue
  .map((p) => `${p.sku} | ${p.brand} | ${p.name} | ${p.variant} | ${p.keywords}`)
  .join('\n');

const SYSTEM_PROMPT = __SYSTEM_PROMPT__;

// __ITEMS__ is replaced with the batch. The validator reuses this template for retries.
const userTemplate = [
  'Product catalogue (sku | brand | name | variant | keywords):',
  catalogueBlock,
  '',
  'UGC items to process (JSON array):',
  '__ITEMS__',
  '',
  'Return {"results": [...]} with exactly one result per item, in the same order.',
].join('\n');

// Only send Claude what it needs (no handles or dates).
const forPrompt = (u) => ({
  id: u.id,
  source: u.source,
  language_hint: u.language_hint,
  rating: u.rating,
  text: u.text,
  pii_detected_by_regex: u.pii_detected,
});

const all = $input.all().map((i) => i.json);
const batches = [];
for (let i = 0; i < all.length; i += settings.batch_size) {
  batches.push(all.slice(i, i + settings.batch_size));
}

return batches.map((batch, index) => ({
  json: {
    batch_index: index,
    ugc_items: batch,
    catalogue,
    user_template: userTemplate,
    request_body: {
      model: settings.model,
      max_tokens: settings.max_tokens,
      output_config: { effort: settings.effort },
      system: SYSTEM_PROMPT,
      messages: [
        { role: 'user', content: userTemplate.split('__ITEMS__').join(JSON.stringify(batch.map(forPrompt), null, 1)) },
      ],
    },
  },
}));
