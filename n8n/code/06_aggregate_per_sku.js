// Aggregate per SKU: turns approved UGC into one record per product, ready for a product page.
// Top quotes = highest quote_score from Claude, with a small bonus for items that have media.

const catalogue = $('Build Claude batches').first().json.catalogue;
const bySkuInfo = Object.fromEntries(catalogue.map((p) => [p.sku, p]));
const MEDIA_BONUS = 0.1;

const groups = {};
for (const { json: r } of $input.all()) {
  (groups[r.matched_sku] = groups[r.matched_sku] || []).push(r);
}

const products = Object.entries(groups).map(([sku, items]) => {
  const ratings = items.map((r) => r.rating).filter((v) => typeof v === 'number');
  const sentiment = { positive: 0, neutral: 0, negative: 0 };
  const topicCount = {};
  for (const r of items) {
    sentiment[r.sentiment]++;
    for (const t of r.topics) topicCount[t] = (topicCount[t] || 0) + 1;
  }
  const top_quotes = items
    .filter((r) => r.suggested_quote && r.quote_score > 0)
    .sort((a, b) => (b.quote_score + (b.media ? MEDIA_BONUS : 0)) - (a.quote_score + (a.media ? MEDIA_BONUS : 0)))
    .slice(0, 3)
    .map((r) => ({
      text: r.suggested_quote,
      lang: r.quote_language,
      source: r.source,
      author: r.author_handle,
      rating: r.rating,
      media: r.media,
      ugc_id: r.id,
    }));

  const info = bySkuInfo[sku] || {};
  return {
    json: {
      sku,
      name: info.name,
      brand: info.brand,
      category: info.category,
      url_slug: info.url_slug,
      ugc_count: items.length,
      avg_rating: ratings.length ? Math.round((ratings.reduce((a, b) => a + b, 0) / ratings.length) * 10) / 10 : null,
      rating_count: ratings.length,
      sentiment,
      top_topics: Object.entries(topicCount).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([t]) => t),
      top_quotes,
    },
  };
});

products.sort((a, b) => b.json.ugc_count - a.json.ugc_count || a.json.sku.localeCompare(b.json.sku));
return products;
