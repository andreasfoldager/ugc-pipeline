// Local test server: lets the whole n8n workflow run without a Claude API key.
//   GET  /data/<file>      serves products.csv and ugc.json
//   POST /v1/messages      fake Anthropic Messages API, answers from data/ugc_expected.json
// It deliberately misbehaves to exercise the validator:
//   - every response starts with a thinking block (only text blocks are the answer)
//   - the batch starting at ugc_021 comes back wrapped in ```json fences and chatter
//   - the batch containing ugc_041 is cut off mid-JSON on the first try (forces the retry path)
//   - ugc_012 gets an invented SKU, ugc_029 gets a rewritten (non-verbatim) quote
// Usage: node tools/mock_server.js [port]
const http = require('http');
const fs = require('fs');
const path = require('path');

const DATA = path.join(__dirname, '..', 'data');
const expected = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(DATA, 'ugc_expected.json'))).map((e) => [e.id, e]));
const port = Number(process.argv[2] || 8787);
let calls = 0;
const seen = new Set();

function fake(item) {
  const e = expected[item.id];
  const route = e.acceptable_routes[0];
  const sku = e.acceptable_skus.find((s) => s) || null;
  const tags = e.seeded;
  const pii = tags.some((t) => t.startsWith('pii'));
  const rating = item.rating;
  const negative = tags.includes('rude') || tags.includes('spam') || (rating !== null && rating <= 2) || route === 'customer_service';
  const sentiment = negative ? 'negative' : rating === 3 ? 'neutral' : 'positive';
  const firstSentence = item.text.split(/(?<=[.!?])\s+/)[0];
  const quotable = route === 'approved' && !tags.includes('question');
  const r = {
    id: item.id,
    language: item.language_hint,
    matched_sku: route === 'rejected' ? null : sku,
    match_confidence: route === 'needs_human_match' ? 0.45 : sku ? (e.acceptable_skus.length > 1 ? 0.72 : 0.93) : 0,
    match_reason: sku ? `mock match to ${sku}` : 'no specific product',
    sentiment,
    topics: route === 'customer_service' ? ['complaint'] : ['quality'],
    moderation: route === 'rejected' ? 'reject' : route === 'review' ? 'review' : 'approve',
    moderation_reason: route === 'rejected' ? 'abusive or spam' : route === 'review' ? 'contains personal data' : '',
    contains_pii: pii,
    needs_customer_service: route === 'customer_service',
    cs_reason: route === 'customer_service' ? 'mock: needs follow-up' : '',
    quote_score: quotable ? Math.min(0.95, 0.4 + firstSentence.length / 150) : 0,
    suggested_quote: quotable ? firstSentence : '',
    quote_language: quotable ? item.language_hint : '',
  };
  if (item.id === 'ugc_012') r.matched_sku = 'HB-99999';
  if (item.id === 'ugc_029') r.suggested_quote = 'Microfiber cloths that leave no streaks at all';
  return r;
}

http.createServer((req, res) => {
  if (req.method === 'GET' && req.url.startsWith('/data/')) {
    const file = path.join(DATA, path.basename(req.url));
    if (!fs.existsSync(file)) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' });
    return res.end(fs.readFileSync(file));
  }
  if (req.method === 'POST' && req.url === '/v1/messages') {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      calls++;
      const json = JSON.parse(body);
      const problems = [];
      if (!req.headers['x-api-key']) problems.push('missing x-api-key');
      if (!req.headers['anthropic-version']) problems.push('missing anthropic-version');
      if ('temperature' in json) problems.push('temperature is not allowed on 5.5 models');
      if (problems.length) {
        res.writeHead(400, { 'content-type': 'application/json' });
        return res.end(JSON.stringify({ type: 'error', error: { type: 'invalid_request_error', message: problems.join(', ') } }));
      }
      const content = json.messages[0].content;
      const m = content.match(/UGC items to process \(JSON array\):\n([\s\S]*?)\n\nReturn/);
      const items = JSON.parse(m[1]);
      const ids = items.map((i) => i.id);
      let text = JSON.stringify({ results: items.map(fake) });
      let stop = 'end_turn';
      if (ids[0] === 'ugc_021') text = 'Here are the results:\n```json\n' + text + '\n```\nLet me know if you need anything else.';
      if (ids.includes('ugc_041') && !seen.has('ugc_041')) { text = text.slice(0, 900); stop = 'max_tokens'; }
      ids.forEach((id) => seen.add(id));
      console.log(`call ${calls}: ${ids[0]}..${ids[ids.length - 1]} (${ids.length} items)${stop === 'max_tokens' ? ' [truncated]' : ''}`);
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({
        id: `msg_mock_${calls}`, type: 'message', role: 'assistant', model: json.model,
        content: [{ type: 'thinking', thinking: '', signature: 'mock' }, { type: 'text', text }],
        stop_reason: stop,
        usage: { input_tokens: Math.round(content.length / 3.5), output_tokens: Math.round(text.length / 3.5) },
      }));
    });
    return;
  }
  res.writeHead(404); res.end();
}).listen(port, () => console.log(`mock server on http://localhost:${port}`));
