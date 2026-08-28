# PROMPT CODEX V71 — REGULATORY ARCHIVE RECOVERY AND PUBLIC BANK 9M AQ

Continuar desde `FRONTERA_CICLO_AJUSTE_V70_BNA_9M_SOURCE_AUDIT_AND_PUBLIC_BANK_RETRIEVAL_GATE.zip`.

## Objetivo

Romper el cuello de acceso documental, no inferir flujos faltantes. Recuperar Anexo Q 9M **separado/individual** para bancos de alto peso.

## Prioridad

1. Banco Nación — attachment separado AGN/BNA/BCRA.
2. Banco Provincia — `Anexo_Q_sep`/EEFF unificado 30/09/2023.
3. Banco Ciudad — separado/individual 30/09/2023 y FY compatible.
4. Credicoop — primary 30/09/2023.
5. Luego BBVA/Santander sólo por rutas nuevas.

## BNA: regla nueva congelada

`BALANCE CONDENSADO SEPT 2023.pdf` es **CONTROL_ONLY**. Aunque es fuente primaria 9M, incluye filiales del exterior, subsidiarias y entes estructurados y no contiene Anexo Q. No usarlo contra FY individual.

## Si aparece 9M compatible

Aplicar exclusivamente:

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

y exigir cuatro patas de la misma base.

## Gates

- `SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING`
- `STOCK_AS_PASS_FLOW_COUNTERPARTY_PROXY = REJECTED`
- consolidado = control
- asset coverage = retrieval diagnostic only
- `IEF_7_7PP_BCRA_SHARE = N/D` hasta bridge compatible
- HTML prohibido

## Output

Crear V71 completa con auditoría, paneles, evidence ledger, QA, manifest, veredicto, handover y prompt siguiente.
