# Handover — Ciclo de ajuste V99 → V100

## Frozen strict state

```text
ANALYTIC_CHECKPOINT = V99
STRICT_COVERAGE = 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
EXACT_ASSET_NUMERATOR = 57803557.512 million ARS
SYSTEM_ASSET_DENOMINATOR = 96697695.5 million ARS
EXACT_ENTITIES = 24
CLOSED_NETWORK_GATE = NO
SEP_TO_DEC_FACTOR = 1.532908152197492
```

V99 makes no strict promotion solely because newly resolved Banco Hipotecario lacks physically preserved issuer binaries.

## New resolved analytical object — Banco Hipotecario

The V88 expense-presentation blocker is closed. FY separated Note20 and FY separated Annex Q prove an exact presentation reclassification: Note20 can omit an explicit pass line while Annex Q separately identifies nonzero pass expense. Therefore Sep `521022=158,630k` no longer conflicts with the entity-specific same-year FY crosswalk.

Candidate Q4:

```text
BCRA income      = 165476115.693522542312472k
BCRA expense     = 0E-15k
Other-FI income  = 91602.783981951682168k
Other-FI expense = 283522.779816911844040k
```

Do not recompute or reinterpret. Promotion is mechanical after source preservation.

## First actions V100

1. Preserve Banco Hipotecario direct official PDFs:
   - `https://www.hipotecario.com.ar/media/BHSA_ESTADOS_FINANCIEROS_AL_30-09-2023.pdf`
   - `https://www.hipotecario.com.ar/media/BHSA_-_ESTADOS_FINANCIEROS_AL_31-12-2023.pdf`
   Verify magic bytes + SHA and promote if content matches V99.
2. Preserve Columbia `10184.pdf` + `10253.pdf`; promote mechanically if verified.
3. If both sets close, candidate strict state is **26 entities / 61.374786601817206698581560302023950508727480480649096751225058926042348134346180%**; closed-network gate remains NO.
4. Continue Mariva/HSBC attachment recovery afterward.

## Source-audit correction

V99 formally catalogs the two Hipotecario direct issuer PDFs that had lived only in historical `SOURCE_REFERENCES_V88.md` / source census. This intentionally increases the known physical-gap count rather than hiding it. Source completeness must be recomputed from the master catalog after the two new pending rows.

## Never break

- no mass-mapping six-digit raw accounts;
- same-entity/same-year only;
- stock != flow;
- source-preservation != analytical sufficiency;
- no strict promotion without physically preserved evidence used for the promotion.
