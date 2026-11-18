// Settings: the one place to change how the pipeline runs.
// Nothing secret lives here. The Claude API key is stored in an n8n credential
// (Header Auth, header name "x-api-key") so it never ends up in the exported workflow.
return [{
  json: {
    // Folder that holds products.csv and ugc.json (e.g. the raw GitHub URL of /data in your repo)
    data_base_url: 'https://raw.githubusercontent.com/YOUR_GITHUB_USER/ugc-pipeline/main/data',

    anthropic_url: 'https://api.anthropic.com/v1/messages',
    model: 'claude-sonnet-5-5',   // 'claude-haiku-5-5' is cheaper and faster
    effort: 'low',                // the task is simple; low effort keeps each call quick
    max_tokens: 8000,

    batch_size: 10,               // UGC items per Claude call
    min_match_confidence: 0.6,    // below this, a human confirms the product match

    // Rough price per million tokens, only used for the cost line in run_summary.md
    price_input_per_mtok: 2,
    price_output_per_mtok: 10,
  },
}];
