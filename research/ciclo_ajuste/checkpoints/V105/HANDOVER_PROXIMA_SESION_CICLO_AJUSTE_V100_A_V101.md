# Handover — Ciclo de ajuste V100 → V101

## Frozen strict state
```text
ANALYTIC_CHECKPOINT = V100
STRICT_COVERAGE = 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
EXACT_ASSET_NUMERATOR = 57803557.512 million ARS
SYSTEM_ASSET_DENOMINATOR = 96697695.5 million ARS
EXACT_ENTITIES = 24
CLOSED_NETWORK_GATE = NO
SEP_TO_DEC_FACTOR = 1.532908152197492
```

## Do not reopen
- Hipotecario analytical bridge: resolved V99, independently revalidated V100. Only original-binary preservation remains.
- Columbia arithmetic bridge: resolved V97. Only original-binary preservation remains.
- BMA ordinary FY target is **#3171909**. Do not use #3177414 as ordinary FY; it is the special merger balance.

## V101 priority
1. Preserve Hipotecario two official PDFs and promote mechanically if SHA/magic/content verification passes.
2. Preserve Columbia two PDFs and promote mechanically.
3. Recover Mariva attachments #3122483/#3165651.
4. Recover HSBC attachments #3121099/#3163537.
5. Recover BMA #3119515/#3171909 and perform same-entity crosswalk.
6. Continue Corrientes/BNA/Santander/BSE/CMF/Chubut holds without weakening gates.

Candidate if Hipotecario only closes: **61.186841531295851823066455601312649689774664795398355692975123693614808017839474% / 25**.
Candidate if Hipotecario + Columbia close: **61.374786601817206698581560302023950508727480480649096751225058926042348134346180% / 26**.
