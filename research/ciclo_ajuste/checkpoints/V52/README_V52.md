# V52 — Contrapartes e incidencia

Continuación directa de V51. Esta carpeta no modifica el HTML ni reabre V34–V51.

## Resultado corto

- pases: contraparte directa **BCRA**;
- títulos: **mixto** (BCRA/Tesoro/valuación), share exacto N/D;
- FX: **valuación de posición**, no transferencia bilateral identificada;
- CER/UVA: **mixto** por instrumento/sector;
- interés/fees de crédito hogar: **sí pueden ser contrato directo hogar→banco**, pero el abnormal share agregado no está cuantificado;
- mora/incobrabilidad: costo bancario/offset, no pago al banco;
- `DIRECT_HOUSEHOLD_TO_BANK_TRANSFER` agregado sigue no identificado;
- `TAXPAYER_IDENTITY` para pases queda rechazado.

## Archivos

- `COMPONENT_COUNTERPARTY_MAP_V52.csv`
- `INCIDENCE_CHAIN_V52.csv`
- `HOUSEHOLD_LINK_CLASSIFICATION_V52.csv`
- `FALSIFICADORES_INCIDENCE_V52.csv`
- `AUDITORIA_CONTRAPARTES_V52.md`
- `VEREDICTO_CONTRAPARTES_V52.md`
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V52.csv`
- `PROMPT_CODEX_V53_COUNTERPARTY_QUANTIFICATION.md`
- `qa_v52.py`
- `MANIFEST_V52.json`

## Diagnóstico Q4-2023

Sólo para los subcomponentes positivos del margen dentro de la misma ventana homogénea:

- gross-positive = 28.7 pp;
- pases BCRA = 7.7 pp = 26.8% piso conocido;
- FX valuación = 11.3 pp = 39.4%;
- títulos mixed = 7.3 pp = 25.4%;
- interés mixed = 2.1 pp = 7.3%.

No interpretar esos porcentajes como share del ROA neto ni como efecto causal post-10/12.
