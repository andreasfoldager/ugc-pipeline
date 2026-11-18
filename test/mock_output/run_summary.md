# UGC pipeline run summary

Run: 2026-11-18 21:48 UTC · model claude-sonnet-5-5 · 60 items

## Totals per route

| Route | Items |
|---|---|
| approved | 41 |
| customer_service | 5 |
| review | 4 |
| rejected | 3 |
| needs_human_match | 7 |
| error | 0 |

- Personal data: 4 caught by regex, 1 more caught only by Claude
- Items retried after a bad response: 10
- Guardrail corrections: 3
- Tokens: 10,815 in / 6,939 out (about $0.091)

## Top 5 products by positive UGC

1. **Shower Gel Sensitive 500 ml** (HB-10234): 4 positive
2. **Hand Cream Intensive 100 ml** (HB-10402): 3 positive
3. **Microfiber Cloths 6-pack** (HB-30201): 3 positive
4. **Shampoo Volume 400 ml** (HB-10310): 2 positive
5. **Mascara Waterproof Black** (HB-10502): 2 positive

## Most common complaint topics

- quality (8)
- complaint (5)

## Needs a human

| Item | Queue | Why | Text |
|---|---|---|---|
| ugc_010 | needs_human_match | mock match to HB-10310 | den nye shampoo dufter godt |
| ugc_012 | needs_human_match | mock match to HB-10402 | Bästa handkrämen, mina händer var helt spruckna efter jobbet på lagre… |
| ugc_015 | customer_service | mock: needs follow-up | Fik udslæt over hele armen efter at have brugt aloe bodylotionen. Det… |
| ugc_020 | needs_human_match | mock match to HB-10501 | Mascaraen er fin, men klumper lidt. |
| ugc_024 | customer_service | mock: needs follow-up | Pakken med 40 opvasketabs var gået i stykker da den kom, tabletterne … |
| ugc_036 | needs_human_match | mock match to HB-40102 | Lakrisen var grei, men jeg foretrekker den salte. |
| ugc_039 | customer_service | mock: needs follow-up | Jeg bestilte to dunke vaskemiddel for 12 dage siden og har stadig ikk… |
| ugc_040 | customer_service | mock: needs follow-up | Fick en allergisk reaktion av handkrämen, svullna fingrar. Har slutat… |
| ugc_041 | review | contains personal data | Super håndcreme, mine knoer er ikke længere revnede! Skriv til mig på… |
| ugc_042 | review | contains personal data | Hvornår kommer den store shower gel sensitive på lager igen? Ring på … |
| ugc_043 | review | contains personal data | Fint oppvaskmiddel med sitron. Kontakt meg på +47 912 34 567 så selge… |
| ugc_044 | customer_service | mock: needs follow-up | My order never arrived and nobody answers. Email me at j.testesen@exa… |
| ugc_045 | review | contains personal data | Gode chips med havsalt! Jeg bor på Kastanjevej 12, 8660 Skanderborg, … |
| ugc_046 | rejected | abusive or spam | hvem gider overhovedet handle i det her lorte sted lol |
| ugc_047 | rejected | abusive or spam | follow me for crypto tips 🚀🚀 link in bio |
| ugc_048 | rejected | abusive or spam | Ni är idioter allihop, sämsta butiken i världen. |
| ugc_049 | needs_human_match | no specific product | Har I åbent 2. juledag? |
| ugc_050 | needs_human_match | no specific product | Friendly staff at the Aarhus store, always tidy. |
| ugc_058 | needs_human_match | mock match to HB-10450 | Toothpaste is fine. Nothing special. |

## Guardrail corrections

- ugc_012: invented SKU "HB-99999" removed
- ugc_029: quote was not a verbatim excerpt, removed
- ugc_044: PII found, moderation raised to review
