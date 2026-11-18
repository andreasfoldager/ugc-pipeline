// Build run summary: totals per route, top products, complaint topics, items for a human,
// guardrail hits and token cost. Written to run_summary.md.

const settings = $('Settings').first().json;
const catalogue = $('Build Claude batches').first().json.catalogue;
const names = Object.fromEntries(catalogue.map((p) => [p.sku, p.name]));
const items = $input.all().map((i) => i.json);
const retryCount = $('Validate Claude output').first().json.retry_count;

// Token usage from the Claude calls (the retry node only exists in the run if it was needed)
const usageOf = (nodeName) => {
  try {
    return $(nodeName).all().map((i) => i.json.usage || {});
  } catch (e) {
    return [];
  }
};
const usage = [...usageOf('Claude: match & moderate'), ...usageOf('Claude: retry')];
const tokensIn = usage.reduce((a, u) => a + (u.input_tokens || 0), 0);
const tokensOut = usage.reduce((a, u) => a + (u.output_tokens || 0), 0);
const cost = (tokensIn * settings.price_input_per_mtok + tokensOut * settings.price_output_per_mtok) / 1e6;

const count = (pred) => items.filter(pred).length;
const routes = ['approved', 'customer_service', 'review', 'rejected', 'needs_human_match', 'error'];
const perRoute = Object.fromEntries(routes.map((r) => [r, count((i) => i.route === r)]));

// Top 5 products by positive approved UGC
const pos = {};
for (const i of items) if (i.route === 'approved' && i.sentiment === 'positive') pos[i.matched_sku] = (pos[i.matched_sku] || 0) + 1;
const topProducts = Object.entries(pos).sort((a, b) => b[1] - a[1]).slice(0, 5);

// Most common complaint topics: negative items + customer-service items
const complaintTopics = {};
for (const i of items) {
  if (i.sentiment === 'negative' || i.route === 'customer_service') {
    for (const t of i.topics || []) complaintTopics[t] = (complaintTopics[t] || 0) + 1;
  }
}
const topComplaints = Object.entries(complaintTopics).sort((a, b) => b[1] - a[1]).slice(0, 5);

const needsHuman = items.filter((i) => i.queue !== 'webshop');
const guardrailHits = items.filter((i) => (i.guardrails || []).length);
const piiRegex = count((i) => i.pii_detected_by_regex);
const piiClaudeOnly = count((i) => i.contains_pii && !i.pii_detected_by_regex);

const short = (t, n = 70) => (t.length > n ? t.slice(0, n - 1) + '…' : t);
const lines = [];
lines.push('# UGC pipeline run summary', '');
lines.push(`Run: ${new Date().toISOString().slice(0, 16).replace('T', ' ')} UTC · model ${settings.model} · ${items.length} items`, '');
lines.push('## Totals per route', '', '| Route | Items |', '|---|---|');
for (const r of routes) lines.push(`| ${r} | ${perRoute[r]} |`);
lines.push('');
lines.push(`- Personal data: ${piiRegex} caught by regex, ${piiClaudeOnly} more caught only by Claude`);
lines.push(`- Items retried after a bad response: ${retryCount}`);
lines.push(`- Guardrail corrections: ${guardrailHits.length}`);
lines.push(`- Tokens: ${tokensIn.toLocaleString('en')} in / ${tokensOut.toLocaleString('en')} out (about $${cost.toFixed(3)})`, '');

lines.push('## Top 5 products by positive UGC', '');
if (!topProducts.length) lines.push('_none_');
topProducts.forEach(([sku, n], idx) => lines.push(`${idx + 1}. **${names[sku]}** (${sku}): ${n} positive`));
lines.push('');

lines.push('## Most common complaint topics', '');
if (!topComplaints.length) lines.push('_none_');
for (const [t, n] of topComplaints) lines.push(`- ${t} (${n})`);
lines.push('');

lines.push('## Needs a human', '', '| Item | Queue | Why | Text |', '|---|---|---|---|');
for (const i of needsHuman) {
  const why = i.route === 'customer_service' ? i.cs_reason
    : i.route === 'needs_human_match' ? (i.match_reason || 'no confident match')
    : i.route === 'error' ? i.problems
    : i.moderation_reason;
  lines.push(`| ${i.id} | ${i.route} | ${short(String(why || ''), 60).replace(/\|/g, '/')} | ${short(i.text).replace(/\|/g, '/')} |`);
}
lines.push('');

if (guardrailHits.length) {
  lines.push('## Guardrail corrections', '');
  for (const i of guardrailHits) lines.push(`- ${i.id}: ${i.guardrails.join('; ')}`);
  lines.push('');
}

const topSku = topProducts[0] ? names[topProducts[0][0]] : 'n/a';
return [{
  json: {
    summary_md: lines.join('\n'),
    notification: `${items.length} UGC items processed: ${perRoute.approved} approved, ${perRoute.customer_service} for customer service, ${needsHuman.length - perRoute.customer_service} need review. Top product: ${topSku}.`,
    per_route: perRoute,
    tokens_in: tokensIn,
    tokens_out: tokensOut,
  },
}];
