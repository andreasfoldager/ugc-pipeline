"""Assembles n8n/workflow.json from the Code-node sources in n8n/code and the prompt in prompts/.

Edit the .js / .md files, then run:  python3 tools/build_workflow.py
"""
import json, pathlib, uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE = ROOT / "n8n" / "code"


def code(name, **subs):
    src = (CODE / name).read_text(encoding="utf-8")
    for k, v in subs.items():
        src = src.replace(f"__{k}__", v)
    return src


SYSTEM_PROMPT = (ROOT / "prompts" / "system_prompt.md").read_text(encoding="utf-8").strip()

nodes, connections = [], {}


def node(name, type_, version, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid5(uuid.NAMESPACE_URL, name)), "name": name,
         "type": type_, "typeVersion": version, "position": pos}
    n.update(extra)
    nodes.append(n)
    return name


def code_node(name, pos, js):
    return node(name, "n8n-nodes-base.code", 2, pos, {"jsCode": js})


def connect(src, dst, out=0):
    outs = connections.setdefault(src, {"main": []})["main"]
    while len(outs) <= out:
        outs.append([])
    outs[out].append({"node": dst, "type": "main", "index": 0})


def get_file(name, pos, filename):
    return node(name, "n8n-nodes-base.httpRequest", 4.2, pos, {
        "url": "={{ $('Settings').first().json.data_base_url }}/" + filename,
        "options": {"response": {"response": {"responseFormat": "text", "outputPropertyName": "data"}}},
    })


def claude_call(name, pos, body_expr):
    return node(name, "n8n-nodes-base.httpRequest", 4.2, pos, {
        "method": "POST",
        "url": "={{ $('Settings').first().json.anthropic_url }}",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [{"name": "anthropic-version", "value": "2023-06-01"}]},
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify(" + body_expr + ") }}",
        "options": {"timeout": 300000},
    }, retryOnFail=True, maxTries=3, waitBetweenTries=5000, onError="continueRegularOutput")


def to_file(name, pos, params):
    return node(name, "n8n-nodes-base.convertToFile", 1.1, pos, params)


def sticky(text, pos, w, h, color):
    node(f"Note {len(nodes)}", "n8n-nodes-base.stickyNote", 1, pos,
         {"content": text, "width": w, "height": h, "color": color})


Y = 300
X = lambda i: 220 * i

# ---- 1. load + rules ----
node("Run pipeline", "n8n-nodes-base.manualTrigger", 1, [X(0), Y], {})
code_node("Settings", [X(1), Y], code("01_settings.js"))
get_file("Get products.csv", [X(2), Y], "products.csv")
get_file("Get ugc.json", [X(3), Y], "ugc.json")
code_node("PII pre-filter", [X(4), Y], code("02_pii_prefilter.js"))

# ---- 2. Claude ----
code_node("Build Claude batches", [X(5), Y], code("03_build_batches.js", SYSTEM_PROMPT=json.dumps(SYSTEM_PROMPT, ensure_ascii=False)))
claude_call("Claude: match & moderate", [X(6), Y], "$json.request_body")
code_node("Validate Claude output", [X(7), Y], code("04_validate.js", ATTEMPT="1"))
node("Anything to retry?", "n8n-nodes-base.if", 2.2, [X(8), Y], {
    "conditions": {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
        "conditions": [{
            "id": "b6c0c1d2-0000-4000-8000-000000000001",
            "leftValue": "={{ $json.retry_count }}",
            "rightValue": 0,
            "operator": {"type": "number", "operation": "gt"},
        }],
        "combinator": "and",
    },
    "options": {},
})
claude_call("Claude: retry", [X(9), Y - 160], "$json.retry_request_body")
code_node("Validate retry", [X(10), Y - 160], code("04_validate.js", ATTEMPT="2"))

# ---- 3. route + outputs ----
code_node("Route items", [X(11), Y], code("05_route.js"))


def rule(key, label):
    return {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, "rule-" + key)),
                "leftValue": "={{ $json.queue }}",
                "rightValue": key,
                "operator": {"type": "string", "operation": "equals"},
            }],
            "combinator": "and",
        },
        "renameOutput": True,
        "outputKey": label,
    }


node("Send to queue", "n8n-nodes-base.switch", 3.2, [X(12), Y], {
    "rules": {"values": [rule("webshop", "Webshop"), rule("customer_service", "Customer service"), rule("moderation", "Moderation")]},
    "options": {},
})
code_node("Aggregate per SKU", [X(13), Y - 200], code("06_aggregate_per_sku.js"))
to_file("product_ugc.json", [X(14), Y - 200], {"operation": "toJson", "options": {"fileName": "product_ugc.json", "format": True}})
code_node("Format CS rows", [X(13), Y], code("07_format_cs.js"))
to_file("cs_queue.csv", [X(14), Y], {"options": {"fileName": "cs_queue.csv"}})
code_node("Format moderation rows", [X(13), Y + 200], code("08_format_moderation.js"))
to_file("moderation_queue.csv", [X(14), Y + 200], {"options": {"fileName": "moderation_queue.csv"}})
code_node("Build run summary", [X(12), Y + 420], code("09_run_summary.js"))
to_file("run_summary.md", [X(13), Y + 420], {"operation": "toText", "sourceProperty": "summary_md", "options": {"fileName": "run_summary.md"}})
to_file("ugc_results.json", [X(12), Y + 620], {"operation": "toJson", "options": {"fileName": "ugc_results.json", "format": True}})

for a, b in [("Run pipeline", "Settings"), ("Settings", "Get products.csv"), ("Get products.csv", "Get ugc.json"),
             ("Get ugc.json", "PII pre-filter"), ("PII pre-filter", "Build Claude batches"),
             ("Build Claude batches", "Claude: match & moderate"), ("Claude: match & moderate", "Validate Claude output"),
             ("Validate Claude output", "Anything to retry?"), ("Claude: retry", "Validate retry"),
             ("Validate retry", "Route items"), ("Aggregate per SKU", "product_ugc.json"),
             ("Format CS rows", "cs_queue.csv"), ("Format moderation rows", "moderation_queue.csv"),
             ("Route items", "Send to queue"), ("Route items", "Build run summary"),
             ("Build run summary", "run_summary.md"), ("Route items", "ugc_results.json")]:
    connect(a, b)
connect("Anything to retry?", "Claude: retry", 0)   # true
connect("Anything to retry?", "Route items", 1)     # false
connect("Send to queue", "Aggregate per SKU", 0)
connect("Send to queue", "Format CS rows", 1)
connect("Send to queue", "Format moderation rows", 2)

sticky("## 1. Load + rules first\nRead the PIM export and the UGC. Regex flags emails and phone numbers before any AI is involved.",
       [X(0) - 40, Y - 140], 1140, 320, 7)
sticky("## 2. Claude, then validation\n10 items per call, strict JSON. Output is untrusted until validated: bad JSON is retried once, invented SKUs and rewritten quotes are removed.",
       [X(5) - 40, Y - 320], 1320, 500, 4)
sticky("## 3. Route + outputs\nFirst matching rule wins: reject → customer service → review → needs human match → approved.",
       [X(11) - 40, Y - 320], 940, 920, 6)

workflow = {
    "name": "UGC → Product Page Pipeline (Hverdagsbutikken demo)",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"},
    "pinData": {},
    "meta": {"templateCredsSetupCompleted": False},
}
out = ROOT / "n8n" / "workflow.json"
out.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {out} with {len(nodes)} nodes")
