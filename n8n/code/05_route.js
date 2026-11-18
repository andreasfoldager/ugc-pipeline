// Route items: the routing policy, in one readable place. The first rule that matches wins.
//   1. moderation = reject                 -> rejected           (moderation queue, reason kept)
//   2. needs_customer_service = true       -> customer_service   (CS queue)
//   3. moderation = review (PII etc.)      -> review             (moderation queue)
//   4. no SKU, or confidence below 0.6     -> needs_human_match  (moderation queue)
//   5. otherwise                           -> approved           (webshop)
// Items that failed validation twice go to the moderation queue as "error".
// `route` says why; `queue` says where it goes (the Switch node uses `queue`).

const settings = $('Settings').first().json;
const { ok, errors } = $input.first().json;

function routeOf(r) {
  if (r.moderation === 'reject') return ['rejected', 'moderation'];
  if (r.needs_customer_service) return ['customer_service', 'customer_service'];
  if (r.moderation === 'review') return ['review', 'moderation'];
  if (!r.matched_sku || r.match_confidence < settings.min_match_confidence) return ['needs_human_match', 'moderation'];
  return ['approved', 'webshop'];
}

const out = ok.map((r) => {
  const [route, queue] = routeOf(r);
  return { json: { ...r, route, queue } };
});
for (const e of errors) out.push({ json: { ...e, route: 'error', queue: 'moderation' } });

out.sort((a, b) => a.json.id.localeCompare(b.json.id));
return out;
