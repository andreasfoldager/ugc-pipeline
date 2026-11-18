"""Checks a pipeline run against the definition of done.

Download ugc_results.json and product_ugc.json from the n8n run into one folder, then:
    python3 tools/check_run.py path/to/folder
"""
import csv, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
run = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "output")

expected = {e["id"]: e for e in json.loads((ROOT / "data/ugc_expected.json").read_text())}
ugc = {u["id"]: u for u in json.loads((ROOT / "data/ugc.json").read_text())}
skus = {r["sku"] for r in csv.DictReader(open(ROOT / "data/products.csv", encoding="utf-8"))}
results = {r["id"]: r for r in json.loads((run / "ugc_results.json").read_text())}
products = json.loads((run / "product_ugc.json").read_text())

EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE = re.compile(r"(?:\+\d{2}[\s-]?)?(?:\d[\s-]?){7,10}\d")
fails, notes = [], []

# 1. every item ran end to end
missing = set(expected) - set(results)
errors = [i for i, r in results.items() if r["route"] == "error"]
if missing: fails.append(f"missing from results: {sorted(missing)}")
if errors: fails.append(f"validation errors: {errors}")

for i, e in expected.items():
    r = results.get(i)
    if not r or r["route"] == "error":
        continue
    tags = e["seeded"]
    # 2. PII caught and never auto-published
    if any(t.startswith("pii") for t in tags):
        if not r.get("contains_pii"): fails.append(f"{i}: seeded PII not flagged")
        if r["queue"] == "webshop": fails.append(f"{i}: PII item reached the webshop")
    # 3. complaints reach customer service
    if any(t.startswith("cs_") for t in tags) and r["route"] != "customer_service":
        fails.append(f"{i}: seeded complaint routed to {r['route']}")
    # 4. no invented SKUs; uncertain matches go to a human
    if r.get("matched_sku") and r["matched_sku"] not in skus:
        fails.append(f"{i}: invented SKU {r['matched_sku']}")
    if r["route"] not in e["acceptable_routes"]:
        notes.append(f"{i}: route {r['route']} (expected {' / '.join(e['acceptable_routes'])})  «{ugc[i]['text'][:60]}»")
    elif r["route"] == "approved" and r["matched_sku"] not in e["acceptable_skus"]:
        fails.append(f"{i}: approved with wrong SKU {r['matched_sku']} (expected {e['acceptable_skus']})")
    if r.get("guardrails"):
        notes.append(f"{i}: guardrail: {'; '.join(r['guardrails'])}")

# 5. quotes are real excerpts, in the right language, with no PII
norm = lambda s: re.sub(r"\s+", " ", s.lower()).strip()
for p in products:
    for q in p["top_quotes"]:
        src = ugc[q["ugc_id"]]
        frags = [f.strip(" .,!?;:\"'") for f in re.split(r"…|\.\.\.", norm(q["text"])) if f.strip(" .,!?;:\"'")]
        if not all(f in norm(src["text"]) for f in frags): fails.append(f"{p['sku']}: quote not an excerpt of {q['ugc_id']}")
        if EMAIL.search(q["text"]) or PHONE.search(q["text"]): fails.append(f"{p['sku']}: quote contains PII")
        if q["lang"] != results[q["ugc_id"]]["language"]: notes.append(f"{p['sku']}: quote lang {q['lang']} vs item {results[q['ugc_id']]['language']}")
        if results[q["ugc_id"]]["queue"] != "webshop": fails.append(f"{p['sku']}: quote from non-approved item {q['ugc_id']}")

routes = {}
for r in results.values():
    routes[r["route"]] = routes.get(r["route"], 0) + 1
print(f"{len(results)}/60 items · routes: {routes} · {len(products)} products with UGC")
print(f"\nFAILURES ({len(fails)})" if fails else "\nAll definition-of-done checks passed.")
for f in fails: print("  ✗", f)
if notes:
    print(f"\nWorth a look ({len(notes)}): judgement calls, not failures")
    for n in notes: print("  •", n)
sys.exit(1 if fails else 0)
