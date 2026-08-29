# HANDOVER V104 → V105 — PublicView click-route extraction + original-byte rescue

## Frozen state
```text
checkpoint = V104
strict entities = 24
strict coverage = 59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%
asset numerator = 57,803,557.512 million ARS
system denominator = 96,697,695.5 million ARS
closed-network gate = NO
Sep→Dec factor = 1.532908152197492
```

## V104 new finding
- Independent Hybrid Analysis browser capture proves a real AIF PublicView loaded `/js/Presentations/presentations.js` (4,192 bytes in the captured 2025 instance), `jquery.fileDownload.js`, `fb.fileutils.js`, and `fb.publicuploader.js`.
- The same report records a 77,570-byte extracted PublicView HTML artifact, SHA-256 `33ca3bed35d68eff021ee21a92444b0d0fc8d86ec9931c34b2d0aedd9427f1ba`.
- Passive/default browser traffic did not include an attachment click, so exact download endpoint/blob GUID is still unrecovered.
- Hybrid artifact/response downloads are protected in the public channel; current direct CNV target fetch also failed in this execution channel.
- Exact Mariva/HSBC/BMA targets remain inherited from V103, not freshly revalidated in V104.

## V105 priorities
1. Any manually supplied promotion-blocking issuer PDFs: ingest original bytes, SHA-256, update FUENTES and promote mechanically.
2. Payoff order: Hipotecario > Columbia > BACS > BMR > BTF > VOII.
3. Recover/inspect the exact AIF `/js/Presentations/presentations.js` body or the hashed captured PublicView HTML/PCAP; identify the attachment click handler/request contract.
4. If browser DevTools/HAR is available, click one attachment on any public PublicView and capture the resulting request; only then replay against Mariva #3122483/#3165651, HSBC #3121099/#3163537, BMA #3119515/#3171909.
5. Preserve BMA ordinary FY #3171909; never substitute special merger balance #3177414.
6. Keep Banco Rioja on mismatch hold until the 158,789k difference and compatible 9M opening are explained.
7. Never mass-map six-digit accounts.
8. Regenerate source audit/manifests/tree/package after any source promotion or discovery checkpoint.
