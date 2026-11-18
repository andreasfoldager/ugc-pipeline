// Format CS rows: the columns a customer-service agent needs.
// This queue is internal, so it keeps the full original text, including contact details.
const catalogue = $('Build Claude batches').first().json.catalogue;
const names = Object.fromEntries(catalogue.map((p) => [p.sku, p.name]));

return $input.all().map(({ json: r }) => ({
  json: {
    id: r.id,
    cs_reason: r.cs_reason,
    sku: r.matched_sku || '',
    product: names[r.matched_sku] || '',
    sentiment: r.sentiment,
    language: r.language,
    contains_pii: r.contains_pii,
    source: r.source,
    author_handle: r.author_handle,
    created_at: r.created_at,
    text: r.text,
  },
}));
