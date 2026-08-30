# V106 - ingest of eleven original issuer PDFs

## Result

All eleven P0 issuer URLs inherited from V105 returned original PDF binaries on 2026-08-29. The files are stored under `research/ciclo_ajuste/inputs/issuer_retrieval/v106/binaries/` and catalogued in `data/fuentes/FUENTES.csv` without changing the stable source IDs.

Every binary passed four independent checks:

- first five bytes are `%PDF-`;
- Poppler `pdfinfo` parsed the complete document and page count;
- SHA-256 was calculated from the stored bytes;
- the material separated/individual pages were rendered and visually compared with the V97/V99/V101/V102 audits.

No new hash matched a previously catalogued source. The operation therefore adds eleven unique physical originals rather than duplicate carriers.

## Promotion consequence

The only remaining gate for Hipotecario, Columbia, BACS, Banco Municipal de Rosario, BTF and VOII was physical preservation. Their Q4 arithmetic is not recalculated or cosmetically rounded; V106 changes only the evidence/promotion state.

The six entities become strict, raising the panel from 24 to 30 entities and coverage from 59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644% to 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%.

`CLOSED_NETWORK_GATE` remains `NO`: majority asset coverage does not prove bilateral closure or bound the missing counterparty flows.
