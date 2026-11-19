"""Generates the sample data for the UGC pipeline demo.

Everything here is invented: the shop (Hverdagsbutikken), brands, products,
handles, emails and phone numbers. Writes:
  data/products.csv        mini PIM export
  data/ugc.json            60 UGC items
  data/ugc_expected.json   ground truth used by tools/check_run.py
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# sku, name, brand, category, variant, keywords, url_slug
PRODUCTS = [
    ("HB-10234", "Shower Gel Sensitive 500 ml", "Lune", "Personal care > Shower", "500 ml, Fragrance-free",
     "shower gel; sensitive; parfumefri; duschgel; duschtvål; dusjsåpe; uden parfume", "shower-gel-sensitive-500ml"),
    ("HB-10235", "Shower Gel Sensitive 250 ml", "Lune", "Personal care > Shower", "250 ml, Fragrance-free",
     "shower gel; sensitive; parfumefri; duschgel; travel size; rejse", "shower-gel-sensitive-250ml"),
    ("HB-10236", "Shower Gel Fresh Citrus 500 ml", "Lune", "Personal care > Shower", "500 ml, Citrus",
     "shower gel; citrus; frisk; duschgel; citron", "shower-gel-fresh-citrus-500ml"),
    ("HB-10310", "Shampoo Volume 400 ml", "Lune", "Personal care > Hair", "400 ml, Volume",
     "shampoo; volumen; volym; fint hår; sjampo", "shampoo-volume-400ml"),
    ("HB-10311", "Shampoo Anti-Dandruff 400 ml", "Lune", "Personal care > Hair", "400 ml, Anti-dandruff",
     "shampoo; skæl; anti-skæl; mjäll; flass; sjampo", "shampoo-anti-dandruff-400ml"),
    ("HB-10312", "Conditioner Volume 400 ml", "Lune", "Personal care > Hair", "400 ml, Volume",
     "conditioner; balsam; volumen; volym", "conditioner-volume-400ml"),
    ("HB-10402", "Hand Cream Intensive 100 ml", "Havbris", "Personal care > Skin", "100 ml, Intensive",
     "hand cream; håndcreme; handkräm; håndkrem; tørre hænder", "hand-cream-intensive-100ml"),
    ("HB-10403", "Body Lotion Aloe 400 ml", "Havbris", "Personal care > Skin", "400 ml, Aloe vera",
     "body lotion; bodylotion; aloe; kropslotion; after sun", "body-lotion-aloe-400ml"),
    ("HB-10405", "Day Cream SPF 15 50 ml", "Havbris", "Personal care > Skin", "50 ml, SPF 15",
     "day cream; dagcreme; dagkräm; spf; solfaktor", "day-cream-spf15-50ml"),
    ("HB-10450", "Toothpaste Whitening 75 ml", "Smil", "Personal care > Oral care", "75 ml, Whitening",
     "toothpaste; tandpasta; tandkräm; tannkrem; whitening; hvide tænder", "toothpaste-whitening-75ml"),
    ("HB-10451", "Toothpaste Sensitive 75 ml", "Smil", "Personal care > Oral care", "75 ml, Sensitive",
     "toothpaste; tandpasta; tandkräm; tannkrem; sensitive; ømme tænder; ising", "toothpaste-sensitive-75ml"),
    ("HB-10501", "Mascara Volume Black", "Glimt", "Cosmetics > Eyes", "Black, Volume",
     "mascara; volumen; sort; svart", "mascara-volume-black"),
    ("HB-10502", "Mascara Waterproof Black", "Glimt", "Cosmetics > Eyes", "Black, Waterproof",
     "mascara; vandfast; waterproof; vattenfast; vannfast", "mascara-waterproof-black"),
    ("HB-10520", "Lip Balm Vanilla", "Glimt", "Cosmetics > Lips", "4.8 g, Vanilla",
     "lip balm; læbepomade; läppbalsam; leppepomade; vanilje; vanilj", "lip-balm-vanilla"),
    ("HB-20101", "Dishwasher Tablets All-in-1 40 pcs", "Ren Hverdag", "Cleaning > Dishes", "40 pcs",
     "dishwasher tablets; opvasketabletter; opvasketabs; maskindisk; oppvaskmaskin", "dishwasher-tablets-40"),
    ("HB-20102", "Dishwasher Tablets All-in-1 80 pcs", "Ren Hverdag", "Cleaning > Dishes", "80 pcs",
     "dishwasher tablets; opvasketabletter; opvasketabs; maskindisk; storpak", "dishwasher-tablets-80"),
    ("HB-20110", "Dish Soap Lemon 500 ml", "Ren Hverdag", "Cleaning > Dishes", "500 ml, Lemon",
     "dish soap; opvaskemiddel; diskmedel; oppvaskmiddel; citron; sitron", "dish-soap-lemon-500ml"),
    ("HB-20120", "Multi-Surface Cleaner Spray 750 ml", "Ren Hverdag", "Cleaning > Surfaces", "750 ml",
     "cleaner; rengøringsspray; universalrengøring; allrengöring; spray", "multi-surface-cleaner-750ml"),
    ("HB-20130", "Laundry Detergent Color 1.5 l", "Ren Hverdag", "Cleaning > Laundry", "1.5 l, Color",
     "laundry detergent; vaskemiddel; tvättmedel; colorvask; farvet tøj", "laundry-detergent-color-1-5l"),
    ("HB-20131", "Laundry Detergent Sensitive 1.5 l", "Ren Hverdag", "Cleaning > Laundry", "1.5 l, Fragrance-free",
     "laundry detergent; vaskemiddel; tvättmedel; sensitiv; parfumefri; uden parfume", "laundry-detergent-sensitive-1-5l"),
    ("HB-30201", "Microfiber Cloths 6-pack", "Fjordhus", "Household > Cleaning tools", "6 pcs",
     "microfiber; mikrofiber; klude; trasor; kluter", "microfiber-cloths-6"),
    ("HB-30210", "Kitchen Towel 4 rolls", "Fjordhus", "Household > Paper", "4 rolls",
     "kitchen towel; køkkenrulle; hushållspapper; tørkerull", "kitchen-towel-4"),
    ("HB-30220", "Tea Lights Unscented 50 pcs", "Fjordhus", "Household > Candles", "50 pcs, 4 h",
     "tea lights; fyrfadslys; värmeljus; telys; lys", "tea-lights-50"),
    ("HB-30230", "Storage Boxes 3-pack", "Fjordhus", "Household > Storage", "3 pcs, with lids",
     "storage boxes; opbevaringskasser; förvaringslådor; oppbevaringsbokser", "storage-boxes-3"),
    ("HB-40101", "Salted Liquorice 250 g", "Knasekompagniet", "Snacks > Sweets", "250 g, Salty",
     "liquorice; saltlakrids; salmiak; saltlakrits; salt lakris", "salted-liquorice-250g"),
    ("HB-40102", "Sweet Liquorice 250 g", "Knasekompagniet", "Snacks > Sweets", "250 g, Sweet",
     "liquorice; sød lakrids; söt lakrits; søt lakris", "sweet-liquorice-250g"),
    ("HB-40110", "Potato Chips Sea Salt 175 g", "Knasekompagniet", "Snacks > Chips", "175 g, Sea salt",
     "chips; crisps; kartoffelchips; potatischips; havsalt", "potato-chips-sea-salt-175g"),
    ("HB-40120", "Dark Chocolate 70% 100 g", "Knasekompagniet", "Snacks > Chocolate", "100 g, 70% cocoa",
     "chocolate; mørk chokolade; mörk choklad; mørk sjokolade", "dark-chocolate-70-100g"),
]

A, CS, RV, RJ, HM = "approved", "customer_service", "review", "rejected", "needs_human_match"

# id, source, lang, text, rating, handle, date, media, acceptable_skus, acceptable_routes, seeded tags
# acceptable_skus: first entry is the "best" answer; None means "no SKU" is acceptable.
UGC = [
    ("ugc_001", "review", "da", "Bedste parfumefri shower gel jeg har prøvet, min hud klør ikke længere. Den store flaske på 500 ml holder i evigheder.", 5, "@hudhanne", "2026-10-02", False, ["HB-10234"], [A], []),
    ("ugc_002", "instagram", "da", "Endelig en shower gel uden parfume der ikke koster en formue 🙌 #sensitivhud #hverdagsbutikken", None, "@morgenkaffe_mette", "2026-10-03", True, ["HB-10234", "HB-10235", None], [A, HM], ["near_duplicate"]),
    ("ugc_003", "review", "sv", "Bra duschtvål för känslig hud, ingen doft alls. Lite tunn konsistens men räcker länge.", 4, "@linnea_testar", "2026-10-04", False, ["HB-10234", "HB-10235", None], [A, HM], ["near_duplicate"]),
    ("ugc_004", "review", "en", "Bought the small 250 ml sensitive shower gel for travel, really gentle on my eczema.", 5, "@nomad_notes", "2026-10-05", False, ["HB-10235"], [A], ["near_duplicate"]),
    ("ugc_005", "review", "da", "Citrus duften er frisk, men den forsvinder hurtigt. Helt okay shower gel.", 3, "@peter_p_dk", "2026-10-05", False, ["HB-10236"], [A], []),
    ("ugc_006", "tiktok", "da", "den nye volumen shampoo fra lune giver altså fylde 😍 håret står helt op", None, "@haartok_dk", "2026-10-06", True, ["HB-10310", None], [A, HM], ["vague"]),
    ("ugc_007", "review", "no", "Sjampoen mot flass hjalp ikke i det hele tatt etter tre uker. Skuffet.", 2, "@ola_tester", "2026-10-07", False, ["HB-10311"], [A], []),
    ("ugc_008", "qa", "da", "Kan man bruge anti-skæl shampooen hver dag, eller er den for stærk?", None, "@spoergejoergen", "2026-10-07", False, ["HB-10311"], [A], ["question"]),
    ("ugc_009", "review", "en", "The volume conditioner made my hair greasy after one wash.", 1, "@greasy_gale", "2026-10-08", False, ["HB-10312"], [A], []),
    ("ugc_010", "review", "da", "den nye shampoo dufter godt", 4, "@kort_og_godt", "2026-10-08", False, [None, "HB-10310", "HB-10311"], [HM], ["vague"]),
    ("ugc_011", "review", "da", "Håndcremen redder mine hænder om vinteren. Trækker hurtigt ind og fedter ikke.", 5, "@vinterhaender", "2026-10-09", False, ["HB-10402"], [A], []),
    ("ugc_012", "review", "sv", "Bästa handkrämen, mina händer var helt spruckna efter jobbet på lagret.", 5, "@lagerlisa", "2026-10-09", False, ["HB-10402"], [A], []),
    ("ugc_013", "instagram", "en", "winter survival kit: the intensive hand cream from @hverdagsbutikken, tea and wool socks", None, "@cosy_corner", "2026-10-10", True, ["HB-10402"], [A], []),
    ("ugc_014", "review", "da", "Aloe lotionen er dejlig let og god efter en dag i solen.", 4, "@solskinsstine", "2026-10-10", False, ["HB-10403"], [A], []),
    ("ugc_015", "review", "da", "Fik udslæt over hele armen efter at have brugt aloe bodylotionen. Det klør stadig efter to dage.", 1, "@roed_arm", "2026-10-11", False, ["HB-10403"], [CS], ["cs_reaction"]),
    ("ugc_016", "review", "en", "Nice light day cream with SPF, works well under makeup.", 4, "@makeup_mira", "2026-10-11", False, ["HB-10405"], [A], []),
    ("ugc_017", "review", "no", "Tannkremen for sensitive tenner fungerer, mye mindre ising når jeg drikker kaldt.", 4, "@kaldt_vann", "2026-10-12", False, ["HB-10451"], [A], []),
    ("ugc_018", "review", "sv", "Whitening-tandkrämen smakar konstigt och jag ser ingen skillnad.", 2, "@vita_tander", "2026-10-12", False, ["HB-10450"], [A], []),
    ("ugc_019", "tiktok", "en", "this 30 kr waterproof mascara does NOT budge in the rain 🌧️", None, "@rainy_lashes", "2026-10-13", True, ["HB-10502"], [A], []),
    ("ugc_020", "review", "da", "Mascaraen er fin, men klumper lidt.", 3, "@vipper_vibe", "2026-10-13", False, [None, "HB-10501", "HB-10502"], [HM], ["vague", "near_duplicate"]),
    ("ugc_021", "review", "da", "Vanilje læbepomaden dufter som kage 😄 min datter elsker den", 5, "@kagemor", "2026-10-14", False, ["HB-10520"], [A], []),
    ("ugc_022", "review", "da", "Opvasketabletterne gør glassene skinnende rene, også på kort program.", 5, "@glasklart", "2026-10-14", False, ["HB-20101", "HB-20102", None], [A, HM], ["near_duplicate"]),
    ("ugc_023", "review", "en", "The 80-pack of dishwasher tablets is great value for a family of five.", 4, "@family_of_five", "2026-10-15", False, ["HB-20102"], [A], ["near_duplicate"]),
    ("ugc_024", "review", "da", "Pakken med 40 opvasketabs var gået i stykker da den kom, tabletterne lå løst i kassen.", 1, "@oedelagt_pakke", "2026-10-15", False, ["HB-20101"], [CS], ["cs_damaged"]),
    ("ugc_025", "review", "sv", "Diskmedlet med citron löser fett bra och doftar fräscht.", 4, "@diskdrottning", "2026-10-16", False, ["HB-20110"], [A], []),
    ("ugc_026", "review", "da", "Sprayflasken holdt op med at virke efter en uge, men selve rengøringsmidlet er fint.", 2, "@spray_sur", "2026-10-16", False, ["HB-20120"], [A, CS], ["borderline_cs"]),
    ("ugc_027", "review", "da", "Sensitiv vaskemiddel uden parfume, endelig noget min søns hud kan tåle.", 5, "@vasketoejsmor", "2026-10-17", False, ["HB-20131"], [A], ["cross_category_trap"]),
    ("ugc_028", "review", "no", "Colorvaskemiddelet holder fargene fine, og 1,5 liter rekker lenge.", 4, "@fargerik", "2026-10-17", False, ["HB-20130"], [A], []),
    ("ugc_029", "review", "en", "Microfibre cloths leave zero streaks on the windows.", 5, "@streakfree", "2026-10-18", False, ["HB-30201"], [A], []),
    ("ugc_030", "instagram", "da", "Fredagsrengøring ✨ mikrofiberklude fra Fjordhus og en god podcast", None, "@fredagsfix", "2026-10-18", True, ["HB-30201"], [A], []),
    ("ugc_031", "review", "da", "Køkkenrullen er okay, men lidt tynd.", 3, "@papirpelle", "2026-10-19", False, ["HB-30210"], [A], []),
    ("ugc_032", "review", "sv", "Värmeljusen brinner länge, ungefär 4 timmar.", 4, "@ljusalva", "2026-10-19", False, ["HB-30220"], [A], []),
    ("ugc_033", "review", "en", "Storage boxes stack nicely, the lids are a bit loose though.", 4, "@tidy_tom", "2026-10-20", False, ["HB-30230"], [A], []),
    ("ugc_034", "tiktok", "da", "saltlakrids test 🧂 de her er SÅ salte, 10/10", None, "@slikanmelder", "2026-10-20", True, ["HB-40101"], [A], []),
    ("ugc_035", "review", "sv", "Den söta lakritsen är mjuk och god, försvann på en kväll.", 5, "@godisgodis", "2026-10-21", False, ["HB-40102"], [A], []),
    ("ugc_036", "review", "no", "Lakrisen var grei, men jeg foretrekker den salte.", 3, "@lakrisløve", "2026-10-21", False, [None, "HB-40102"], [HM, A], ["vague"]),
    ("ugc_037", "review", "en", "Sea salt crisps are crunchy and not too greasy.", 4, "@crisp_critic", "2026-10-22", False, ["HB-40110"], [A], []),
    ("ugc_038", "review", "da", "70% chokoladen er virkelig god til prisen.", 5, "@kakaokim", "2026-10-22", False, ["HB-40120"], [A], []),
    ("ugc_039", "qa", "da", "Jeg bestilte to dunke vaskemiddel for 12 dage siden og har stadig ikke fået noget. Ordrenummer 48213.", None, "@venter_stadig", "2026-10-23", False, [None, "HB-20130", "HB-20131"], [CS], ["cs_missing_order"]),
    ("ugc_040", "review", "sv", "Fick en allergisk reaktion av handkrämen, svullna fingrar. Har slutat använda den.", 1, "@svullen_sara", "2026-10-23", False, ["HB-10402"], [CS], ["cs_reaction"]),
    ("ugc_041", "review", "da", "Super håndcreme, mine knoer er ikke længere revnede! Skriv til mig på mette.fiktiv@example.com hvis du vil høre mere om min hudpleje.", 5, "@hudpleje_mette", "2026-10-24", False, ["HB-10402"], [RV], ["pii_email"]),
    ("ugc_042", "qa", "da", "Hvornår kommer den store shower gel sensitive på lager igen? Ring på 21 34 56 78", None, "@lagerjagt", "2026-10-24", False, ["HB-10234"], [RV, CS], ["pii_phone"]),
    ("ugc_043", "review", "no", "Fint oppvaskmiddel med sitron. Kontakt meg på +47 912 34 567 så selger jeg deg det billigere.", 4, "@billigsalg", "2026-10-25", False, ["HB-20110"], [RV, RJ], ["pii_phone", "spam"]),
    ("ugc_044", "review", "en", "My order never arrived and nobody answers. Email me at j.testesen@example.org, order 55190.", 1, "@where_is_it", "2026-10-25", False, [None], [CS], ["pii_email", "cs_missing_order"]),
    ("ugc_045", "review", "da", "Gode chips med havsalt! Jeg bor på Kastanjevej 12, 8660 Skanderborg, hvis nogen vil bytte lakrids 😂", 4, "@chipsbytter", "2026-10-26", False, ["HB-40110"], [RV], ["pii_address_no_regex"]),
    ("ugc_046", "instagram", "da", "hvem gider overhovedet handle i det her lorte sted lol", None, "@sur_bruger", "2026-10-26", False, [None], [RJ], ["rude"]),
    ("ugc_047", "tiktok", "en", "follow me for crypto tips 🚀🚀 link in bio", None, "@moon_money", "2026-10-27", False, [None], [RJ], ["spam"]),
    ("ugc_048", "review", "sv", "Ni är idioter allihop, sämsta butiken i världen.", 1, "@arg_anna", "2026-10-27", False, [None], [RJ, RV], ["rude"]),
    ("ugc_049", "qa", "da", "Har I åbent 2. juledag?", None, "@juleshopper", "2026-10-28", False, [None], [HM, RV], ["no_product"]),
    ("ugc_050", "review", "en", "Friendly staff at the Aarhus store, always tidy.", 5, "@happy_shopper", "2026-10-28", False, [None], [HM], ["no_product"]),
    ("ugc_051", "review", "da", "Shower gel Sensitive i 500 ml er blevet min faste. Ingen tørhed overhovedet.", 4, "@fast_kunde", "2026-10-29", False, ["HB-10234"], [A], ["near_duplicate"]),
    ("ugc_052", "review", "da", "Volumen-shampooen og balsammen sammen = perfekt hår", 5, "@perfekt_haar", "2026-10-29", True, ["HB-10310", "HB-10312", None], [A, HM], ["two_products"]),
    ("ugc_053", "review", "sv", "Vattenfast mascara som faktiskt håller hela dagen.", 4, "@heldagslook", "2026-10-30", False, ["HB-10502"], [A], []),
    ("ugc_054", "review", "no", "Beste håndkremen jeg har prøvd til prisen.", 5, "@prisbevisst", "2026-10-30", False, ["HB-10402"], [A], []),
    ("ugc_055", "review", "da", "Chokoladen er lidt for bitter til mig, men min mand elsker den.", 3, "@soed_tand", "2026-10-31", False, ["HB-40120"], [A], []),
    ("ugc_056", "review", "da", "Opvasketabletterne i 80 stk pakken holder en hel måned hos os.", 4, "@maanedsmor", "2026-10-31", False, ["HB-20102"], [A], ["near_duplicate"]),
    ("ugc_057", "tiktok", "da", "lifehack: mikrofiberklude + eddike på badeværelset 🔥", None, "@rengoeringsrebel", "2026-11-01", True, ["HB-30201"], [A], []),
    ("ugc_058", "review", "en", "Toothpaste is fine. Nothing special.", 3, "@meh_mike", "2026-11-01", False, [None, "HB-10450", "HB-10451"], [HM], ["vague"]),
    ("ugc_059", "review", "da", "Vanilje lip balm er altid i min taske.", 5, "@taskefund", "2026-11-02", False, ["HB-10520"], [A], []),
    ("ugc_060", "qa", "sv", "Är salmiaklakritsen glutenfri?", None, "@glutenfri_gustav", "2026-11-02", False, ["HB-40101"], [A], ["question"]),
]

assert len(UGC) == 60 and len({u[0] for u in UGC}) == 60
skus = {p[0] for p in PRODUCTS}
for u in UGC:
    for s in u[8]:
        assert s is None or s in skus, (u[0], s)

with open(DATA / "products.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["sku", "name", "brand", "category", "variant", "keywords", "url_slug"])
    w.writerows(PRODUCTS)

ugc = [
    {"id": i, "source": s, "language_hint": l, "text": t, "rating": r,
     "author_handle": h, "created_at": d, "media": m}
    for (i, s, l, t, r, h, d, m, *_rest) in UGC
]
(DATA / "ugc.json").write_text(json.dumps(ugc, ensure_ascii=False, indent=2), encoding="utf-8")

expected = [
    {"id": u[0], "acceptable_skus": u[8], "acceptable_routes": u[9], "seeded": u[10]}
    for u in UGC
]
(DATA / "ugc_expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(PRODUCTS)} products, {len(ugc)} UGC items")
