# HANDOVER V105 → V106 — exact AIF attachment request extraction + original-byte preservation

## Frozen state
```text
checkpoint = V105
strict entities = 24
strict coverage = 59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%
asset numerator = 57,803,557.512 million ARS
system denominator = 96,697,695.5 million ARS
closed-network gate = NO
Sep→Dec factor = 1.532908152197492
```

## V105 new findings
- Official CNV rows revalidate Mariva #3122483/#3165651, HSBC #3121099/#3163537, BMA #3119515/#3171909 at the intended individual basis and endpoint dates.
- Mariva #3122483 is freshly live-indexed at PublicView GUID `c23edd68-9bf4-4b3d-a1d8-9cde4770d45c`.
- BMA registry independently confirms #3171909 and later separate #3177414; never substitute #3177414.
- Current PublicView examples show attachment filename/size rows are materialized by crawler/indexing.
- Current Almanac `cnv.ons.colocaciones` schema documents `pdf_blob_guid` as the AIF attachments-JSON `guid`, plus filename/size/hash and programmatic PDF re-download semantics.
- Direct reader access to `/js/Presentations/presentations.js` identifies `application/javascript`, but body preservation still fails in this channel.
- No exact attachment request contract, target blob GUID, or original target binary recovered; no promotion.

## V106 priorities
1. Ingest any manually supplied promotion-blocking issuer PDFs, SHA-256, FUENTES update, promote mechanically.
2. Payoff: Hipotecario > Columbia > BACS > BMR > BTF > VOII.
3. Obtain one observed attachment-click request (HAR/DevTools/crawler code) or exact current `presentations.js` body; record path + verb + parameters without guessing.
4. Replay only the observed contract against the six exact PublicView targets and preserve original attachment bytes/hash.
5. Keep BMA FY #3171909; exclude #3177414 as substitute.
6. Keep Banco Rioja mismatch hold until 158,789k difference + compatible 9M opening are explained.
7. Never mass-map six-digit accounts.
8. Regenerate audits/manifests/tree/package after any discovery/promotion checkpoint.
