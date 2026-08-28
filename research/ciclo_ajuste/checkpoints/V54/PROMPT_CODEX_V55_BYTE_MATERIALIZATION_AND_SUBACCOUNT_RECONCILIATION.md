# Prompt Codex — V55 · materialización de bytes y reconciliación de subcuentas BCRA

## Estado V54 congelado

```text
RAW_OFFICIAL_ENDPOINTS = VERIFIED
RAW_SOURCE_BYTES_MATERIALIZED = FALSE
SHA256_GATE = FAILED_RUNTIME_NETWORK

BCRA_DIRECT_COUNTERPARTY_FLOOR = 7.7 PP = 26.83%
UNRESOLVED_COUNTERPARTY_MASS = 21.0 PP = 73.17%

V53_66_20_STRICT_CLASSIFIED_AS_JOINT_PARTITION = REVOKED
V53_MARKET_VALUATION_FLOOR_39_37 = REVOKED
V53_HOUSEHOLD_[0,2.1]PP_STRICT_CEILING = REVOKED

HOUSEHOLD_DIRECT_POINT_ESTIMATE = N/D
```

## Misión

Ejecutar la fase que V54 no pudo completar por bloqueo de bytes.

### 1. Materializar y versionar

Descargar exactamente los endpoints listados en `RAW_SOURCE_MANIFEST_V54.csv`. Para cada archivo:

- conservar bytes sin alterar;
- registrar timestamp UTC de descarga;
- tamaño en bytes;
- SHA256;
- MIME real;
- nombre local inmutable;
- URL fuente.

Prioridad:

1. `baldethis.xls`
2. `Infbanc1223.xlsx`
3. `.7z` mensual de Información sobre Entidades Financieras para 2023-09 a 2023-12
4. `titpubser.xls`
5. `perser_priv.xls` / `perser_pub.xls`
6. `finuva_mensual.xls` / `depuva_mensual.xls`

Si el runtime sigue sin red, **no improvisar**: usar bytes adjuntados por el usuario o terminar con `BYTE_GATE_FAILED`.

### 2. Reconstruir diccionario de subcuentas

Buscar campos/cuentas capaces de separar:

```text
securities:
  BCRA / Treasury national / provincial / private
  coupon/accrual / TIR / sale / price/valuation / impairment / ORI

interest income:
  household / company / public / financial / other

CER/UVA:
  public CER securities / household UVA loans / corporate indexed assets
  household UVA deposits / other indexed liabilities

FX:
  remeasurement / spot trading / forwards-derivatives / ORI
  gross assets and liabilities by counterparty where available
```

### 3. Reconciliar primero, asignar después

Para Q3 y Q4 2023 construir una identidad que llegue a las cuentas congeladas:

```text
securities gap = +7.3 pp
interest income gap = +2.1 pp
CER gap = -0.2 pp
FX gap = +11.3 pp
```

Tolerancia de reconciliación: declarar explícitamente escala, denominador y rounding. Si no reconcilia, no usar el split.

### 4. No reintroducir errores revocados

Prohibido:

- usar +2.1 pp como ceiling sectorial sin restricciones de signo;
- llamar a +11.3 pp “market valuation” completo;
- mezclar `counterparty` con `accounting_mode` en una sola partición;
- usar stock por emisor como share de resultado;
- tratar apreciación de bono Tesoro como pago contemporáneo del Tesoro;
- transformar pases BCRA en “lo pagó el contribuyente”.

## Output obligatorio

- `RAW_BYTES_MANIFEST_V55.csv`
- `SUBACCOUNT_DICTIONARY_V55.csv`
- `SECURITIES_RECONCILIATION_V55.csv`
- `INTEREST_SECTOR_RECONCILIATION_V55.csv`
- `CER_GROSS_RECONCILIATION_V55.csv`
- `FX_MODE_RECONCILIATION_V55.csv`
- `COUNTERPARTY_AXIS_V55.csv`
- `ACCOUNTING_MODE_AXIS_V55.csv`
- `AUDITORIA_RECONCILIACION_V55.md`
- `VEREDICTO_RECONCILIACION_V55.md`
- `EVIDENCE_LEDGER_CICLO_AJUSTE_V55.csv`
- `README_V55.md`
- `MANIFEST_V55.json`
- QA script

No tocar HTML.
