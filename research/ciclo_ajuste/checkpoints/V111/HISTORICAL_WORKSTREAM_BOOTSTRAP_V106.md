# Historical workstream bootstrap V106 - 2001 to 2026

## Version reconciliation

The master handover expected V106 to pre-exist, but the verified checkout head at session start was V105. Repository state therefore controlled: this checkpoint is V106, not a synthetic jump to V107. The historical branch requested for the next cycle is opened here because V106 also contains a material microbank promotion.

## What was imported

The bootstrap re-indexes, without changing the inherited verdicts, the pre-V52 work carried by:

- `MATRIZ_SIGNO_INCIDENCIA_2002_2026_V41.csv`;
- `MAPA_HIPOTESIS_POST_FALSADORES_V41.csv`;
- `MATRIZ_V22_AMORTIGUADORES_2018_2024.csv`;
- `MATRIZ_V21_AMORTIGUADORES_2023_2025.csv`;
- `TIMELINE_V30_SHOCK_BUFFER_RECOVERY_CREDITO.csv`;
- `MATRIZ_PUENTE_CONSUMO_DEUDA_2023_2026.csv`;
- `LEAD_LAG_AUDIT_V45.csv`;
- `EPISODE_ABNORMAL_VERDICTS_V49.csv`;
- `FALSIFICADORES_COMPONENTS_V50.csv`;
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V51.csv`;
- `BUFFER_STRESS_USE_V44.csv`, `BANK_NET_EXPOSURE_TO_PN_V44.csv`, and `BANK_CUMULATIVE_OUTCOME_V48.csv`.

The new CSVs are an index into those findings, not a replacement for the underlying carriers. Numeric cells are populated only where a cited inherited artifact supplies the value.

## Frozen episode treatment

| Episode | Current use | Bootstrap verdict |
|---|---|---|
| 2001–2003 | Deep documentary branch | `NOT_ENOUGH_EVIDENCE`; also a warning against the simplified “households lose, banks win” story |
| 2008–2009 | External control | `FALSIFIER` of the universal cycle |
| 2014 | Domestic shock | `PARTIAL_MATCH`; household onset and some lag structure survive, causal bank attribution does not |
| 2015–2016 | Regulatory laboratory | Not forced into a shock; A5590/A5853/A5928 establish policy-sign heterogeneity |
| 2018–2019 | Mixed domestic crisis/program episode | `FAILS_ONSET` for the clean shock-to-mora chain; other components remain mixed/partial |
| 2020–2021 | Health exception | `SPECIAL_REGIME`; not pooled without explicit forbearance/accounting controls |
| 2023–2026 | Maximum-resolution case | `PARTIAL_MATCH`/`MIXED`; dissaving precedes a late credit bridge and mora, while provisions and profitability do not follow a simple mora-first order |

## Largest historical gap

The repo contains no comparable primary-source reconstruction for 2001–2003. The only catalogued long-run item visibly reaching 2002 is a BCRA personal-loan-rate workbook; that is insufficient to characterize the episode. V106 therefore creates a source queue before attempting narrative.

The 2001 branch must establish:

1. event chronology and alternative t0 definitions;
2. household income/employment/poverty/deposit incidence;
3. credit, restructuring, mora and provisioning;
4. bank losses, capital, liquidity and recovery;
5. legal and accounting mechanisms allocating losses among depositors, debtors, banks, BCRA and Treasury;
6. realized public compensation or fiscal absorption, mechanism by mechanism.

No claim of direct household-to-bank transfer, deliberate coordination or socialization is promoted by this bootstrap.

## Methodological controls carried forward

- 2008 remains an external falsifier.
- COVID remains non-comparable absent an explicit special-regime design.
- The May-2018 t0 retains its negative mora-onset lag; t0 is not moved to improve the narrative.
- Q4-2023 is not a clean post-10-December treatment window.
- Component gaps are accounting bridges, not household transfers or causal net benefits.
- Registered and broad wage recovery clocks remain separate.
- Exact, supported, partial, proxy, N/D, not-comparable and falsified states are not collapsed.

## Outputs

- `HISTORICAL_EPISODE_MATRIX_2001_2026_V106.csv` provides the first common episode-variable index.
- `HISTORICAL_EVIDENCE_COVERAGE_V106.csv` records quality and gaps by episode and variable family.
- `HISTORICAL_SOURCE_QUEUE_V106.csv` opens the primary-source recovery queue, led by 2001–2003.

This is a bootstrap, not a declaration of a robust historical pattern.
