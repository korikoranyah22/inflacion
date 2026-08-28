# V53 — Cuantificación de contrapartes

Continuación directa de V52. No modifica HTML y no reabre V34–V51.

## Resultado corto

- Q4-2023: **66.2%** del subtotal positivo bruto puede clasificarse sin solapamiento:
  - 26.8% pases → BCRA;
  - 39.4% FX → canal de valuación.
- El **33.8%** restante sigue mixto: títulos 25.4%, intereses 7.3%, otros 1.0%.
- Títulos: exposición BCRA/Tesoro/mercado confirmada, **share exacto N/D**.
- Intereses: hogares/empresas tienen contrato directo posible, **share sectorial N/D**.
- CER/UVA: hogares aparecen como deudores y como depositantes; Q4 abnormal CER = -0.2 pp.
- FX: gross legs mejor mapeados, pero no aparece pagador hogar identificable.
- `DIRECT_HOUSEHOLD_TO_BANK_TRANSFER` agregado sigue no identificado.

## Bound clave

```text
household direct gross-revenue,
strict isolated Q4 positive bucket
= [0, 2.1 pp]
= [0, 7.32%]
```

No es estimación: es techo de bucket.

## Archivos

- `SECURITIES_ISSUER_VALUATION_SPLIT_V53.csv`
- `INTEREST_INCOME_SECTOR_SPLIT_V53.csv`
- `CER_ASSET_LIABILITY_SECTOR_MAP_V53.csv`
- `FX_GROSS_COUNTERPARTY_MAP_V53.csv`
- `HOUSEHOLD_DIRECT_FLOW_BOUND_V53.csv`
- `AUDITORIA_CUANTIFICACION_CONTRAPARTES_V53.md`
- `VEREDICTO_CUANTIFICACION_CONTRAPARTES_V53.md`
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V53.csv`
- `FUENTES_V53.md`
- `PROMPT_CODEX_V54_RAW_BCRA_MICRODATA.md`
- `qa_v53.py`
- `MANIFEST_V53.json`
- `BASE_V52.zip`

## Regla de lectura

Los máximos por categoría son **marginal envelopes** que se superponen. No sumarlos.

La partición disjunta es sólo:

```text
7.7 BCRA passes
11.3 FX valuation
9.7 mixed/N-D
= 28.7 pp
```
