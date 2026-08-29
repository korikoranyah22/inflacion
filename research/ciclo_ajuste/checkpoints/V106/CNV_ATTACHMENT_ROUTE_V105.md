# CNV attachment route — V105

## New evidence
V105 upgrades the route evidence without promoting any bank numerically.

1. **Official target rows revalidated.** CNV's own company/registry pages again resolve Mariva #3122483/#3165651, HSBC #3121099/#3163537, and BMA #3119515/#3171909 with the intended individual basis and 2023 endpoint dates.
2. **Mariva 9M PublicView is live-indexed.** The current AIF PublicView title resolves presentation #3122483 and Banco Mariva S.A. at the same GUID already inherited from V103.
3. **BMA target distinction independently survives.** CNV lists ordinary FY #3171909 on 2024-03-21 and a separate later individual FY filing #3177414 on 2024-04-05. The latter is not substituted.
4. **Current AIF search crawling materializes attachment rows.** Other PublicViews currently expose filename + size rows under `Descargar`, proving the attachment layer is operational and crawl-resolvable even though a simple static page fetch only returns the client-side shell.
5. **The attachment metadata contract is independently documented.** Almanac's current CNV AIF dataset schema explicitly separates `presentation_guid` from `pdf_blob_guid`, describes the latter as the attachment JSON `guid`, and records attachment filename, size, and AIF-provided hash. It states that the blob GUID enables programmatic PDF re-download.
6. **Live JavaScript path is reachable but not preserved in this execution channel.** A direct reader request to `/js/Presentations/presentations.js` reaches a resource identified as `application/javascript`; the reader refuses that content type. Container networking cannot persist the bytes, so V105 does not pretend the JS was recovered.

## What is still missing
- exact attachment JSON request path/verb/parameters;
- target attachment/blob GUIDs for the six bank filings;
- original CNV attachment bytes and local SHA-256;
- therefore no strict promotion.

## Rule
Do not invent or pattern-guess the endpoint. Only record/replay an observed request contract or preserve an original attachment obtained through a verifiable official route.
