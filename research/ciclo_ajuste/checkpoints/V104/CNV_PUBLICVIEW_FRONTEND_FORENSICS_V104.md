# CNV PublicView frontend forensics — V104

## Result
V104 adds **independent forensic evidence from the real AIF PublicView frontend** without claiming recovery of any target bank attachment.

A Hybrid Analysis browser capture submitted on **2025-04-30 16:49:52 UTC** visited:

`https://aif2.cnv.gov.ar/Presentations/publicview/08674C30-2755-49FF-B958-A6D13B74E117`

Report:
https://hybrid-analysis.com/sample/ac87b43af4c0dbf25d023fe4ce82067902593276ae57d244701dea2b55fd8258/681254b0322cb01225073c1b

The report records **69 HTTP traffic entries**, an extracted copy of the PublicView HTML, and the exact JavaScript dependency footprint loaded by the page. This is useful because it replaces an open-ended “guess the attachment API” search with a concrete frontend extraction target.

## High-value observed resources
| Resource | HTTP | bytes | Why it matters |
|---|---:|---:|---|
| `/js/Presentations/presentations.js` | 200 | 4,192 | presentation-specific code; highest-value route-discovery target |
| `/lib/jquery-file-download/jquery.fileDownload.js` | 200 | 20,099 | explicit browser file-download helper |
| `/Engine/js/fb.fileutils.js` | 200 | 2,404 | common file utility layer |
| `/Engine/js/fbhtmlcontrols/fb.publicuploader.js` | 200 | 10,737 | public file-control layer |
| `/Engine/js/CNV.environment.js` | 200 | 3,272 | CNV frontend environment/config |
| `/Engine/js/appconfig.js` | 200 | 2,092 | application configuration |

All six were served as JavaScript and were observed from the same PublicView page. Exact headers/ETags are preserved in `CNV_PUBLICVIEW_FRONTEND_FORENSICS_V104.csv`.

The public traffic preview also exposes the beginning of the actual `presentations.js` response body. Its decoded prefix declares `viewModel`, sets `hasExpirations = false`, and begins a `Presenta...` function. The preview is truncated before the relevant handler/request construction, so V104 records this only as **proof that response-body code was captured**, not as endpoint recovery.

## Extracted historical HTML artifact
Hybrid Analysis records an extracted HTML artifact for the same PublicView:
- bytes: **77,570**;
- SHA-256: `33ca3bed35d68eff021ee21a92444b0d0fc8d86ec9931c34b2d0aedd9427f1ba`;
- type: HTML / UTF-8;
- public download state: disabled in the report.

The report also advertises a PCAP (~13 MiB) and memory strings, but those downloads are access-restricted in the public channel used here.

## What the capture does and does not prove
It proves that a live PublicView uses the observed presentation-specific/download/file-control stack. It **does not** expose the bank-target attachment endpoint by itself: the capture is a passive/default browser run and no attachment-click request was observed in the accessible trace.

Therefore V104 does **not** infer a URL pattern, does **not** synthesize a blob GUID, and does **not** promote Mariva, HSBC or BMA.

## Exact target set remains inherited from V103
- Mariva #3122483 / #3165651
- HSBC #3121099 / #3163537
- BMA #3119515 / ordinary FY #3171909

BMA special merger balance **#3177414 remains excluded**.

During V104 the direct CNV fetch channel for those targets was unavailable. Their exact identities are therefore **inherited from V103**, not represented as newly live-revalidated in V104.

## Next deterministic route
1. Recover the exact **4,192-byte** historical/current `presentations.js` body, or the hashed 77,570-byte PublicView HTML artifact / PCAP.
2. Locate the attachment click handler and request construction.
3. Replay only after the endpoint contract is observed, against the six already-fixed presentation GUIDs.
4. Preserve original attachment bytes + SHA-256 before any strict promotion.

No screenshots, re-rendered PDFs, guessed endpoints, or mass six-digit account mappings are admissible substitutes.
