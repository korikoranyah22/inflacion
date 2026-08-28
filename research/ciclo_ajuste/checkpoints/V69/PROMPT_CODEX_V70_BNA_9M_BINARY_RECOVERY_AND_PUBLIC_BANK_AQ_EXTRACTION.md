# PROMPT CODEX V70 — BNA 9M BINARY RECOVERY AND PUBLIC BANK AQ EXTRACTION

Continuar desde `FRONTERA_CICLO_AJUSTE_V69_PUBLIC_BANK_SOURCE_PATH_AND_COVERAGE_PRIORITY.zip`.

## Objetivo

Aumentar la cobertura Q4 exacta en la base sistémica individual mediante recuperación **binaria/documental**, no inferencia.

## Orden

1. Banco Nación 30/09/2023 separado.
2. Banco Provincia 30/09/2023 separado.
3. Credicoop 30/09/2023 separado.
4. Banco Ciudad 30/09/2023 y FY separado.
5. BBVA individual.
6. Santander sólo si surge una fuente alternativa nueva.

## BNA

Fuente oficial identificada:
- AGN Informe 210/2023, Actuación 298/2023.
- Período 01/01/2023–30/09/2023.
- Estados intermedios consolidados condensados y separados condensados.
- Attachments detectados pero actualmente 502.

FY individual exacto ya congelado:
- income BCRA 766,170,919k
- income otherFI 0
- expense BCRA 0
- expense otherFI 0

Si se recupera 9M compatible:
`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

No usar el FY consolidado como sustituto.

## Cobertura

BNA = 22.015263% activos bancarios.
Su incorporación exacta llevaría el footprint estricto de 11.260968% a 33.276231%.
Esto es diagnóstico de retrieval, NO ponderación de flujo.

## Reglas congeladas

- `SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING`
- `STOCK_AS_PASS_FLOW_COUNTERPARTY_PROXY = REJECTED`
- consolidado = control, no sumable
- producto != sector hogar
- Q4-2023 != post-10/12 limpio
- `IEF_7_7PP_BCRA_SHARE = N/D` hasta bridge compatible
- HTML prohibido

## Outputs V70

Crear paneles equivalentes a V69, además de:
- `BNA_9M_BINARY_RECOVERY_V70.csv`
- `BNA_Q4_AQ_BRIDGE_V70.csv` sólo si corresponde
- `PUBLIC_BANK_AQ_EXTRACTION_V70.csv`
- auditoría, veredicto, evidence ledger, manifest, QA
- handover/prompt V71 según cuello restante.
