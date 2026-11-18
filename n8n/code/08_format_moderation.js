// Format moderation rows: everything a human needs to decide on rejected, review,
// needs-human-match and error items, with the reason the pipeline held each one back.
return $input.all().map(({ json: r }) => ({
  json: {
    id: r.id,
    queue_reason: r.route,
    moderation: r.moderation || '',
    moderation_reason: r.moderation_reason || '',
    suggested_sku: r.matched_sku || '',
    match_confidence: r.match_confidence ?? '',
    match_reason: r.match_reason || '',
    contains_pii: r.contains_pii ?? '',
    guardrails: (r.guardrails || []).join('; '),
    problems: r.problems || '',
    source: r.source,
    author_handle: r.author_handle,
    created_at: r.created_at,
    text: r.text,
  },
}));
