# Auditoría de cobertura y organización de fuentes · v195

Fecha de revisión: **27 de agosto de 2026**.  
Archivo auditado: `index.html`.

## Resultado

- Pestañas detectadas: **37**.
- Pestañas con al menos una referencia visible: **37**.
- Pestañas sin referencia visible: **0**.
- Catálogo maestro `FUENTES.csv`: **136 entradas**.
- Entradas con URL de origen: **116**.
- Entradas con archivo local: **67**.
- Archivos locales faltantes según manifiesto: **0**.
- Hashes SHA-256 incompatibles: **0**.
- Rutas `data-source-path` únicas usadas por el HTML: **19**.
- Rutas `data-source-path` inexistentes: **0**.

## Qué cambia respecto de v194

1. La rama `ciclo_ajuste` deja de tener V51 como mapa vigente: `REFERENCIAS_CICLO_AJUSTE_V70.md` incorpora los cierres V52–V70 y V51 queda como snapshot histórico.
2. El manifiesto incorpora fuentes primarias/regulatorias para ICBC, Banco de Valores, Macro, Supervielle, Santander, Nación, Provincia, Credicoop y Ciudad, además de BCRA para el gate producto→sector.
3. Se incorporan localmente auditoría, veredicto, ledger y paneles V70 con SHA-256 reproducible.
4. El bloque bancario del dashboard expone accesos al mapa documental y al veredicto V70; no se modifican series ni gráficos.
5. El registro visible apunta a esta auditoría V195 y mantiene el mismo esquema de clasificación primaria / dato / auditoría.

## Revocaciones y gates que la trazabilidad debe preservar

```text
7_7PP_AS_STRICT_BCRA_FLOOR = REVOKED
IEF_7_7PP_BCRA_SHARE = N/D
STOCK_AS_PASS_FLOW_COUNTERPARTY_PROXY = REJECTED
SUBSET_INTERBANK_NETTING_AS_SYSTEM_TEST = REJECTED
HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
```

La cobertura estricta V70 (`ICBC + Banco de Valores + Banco Macro`) es **11,260968% de los activos bancarios** y se usa como diagnóstico documental. `asset_share != pass_flow_weight`.

## Reglas de clasificación

- **Primaria:** publicación/norma del organismo o emisor de origen.
- **Dato:** serie, archivo, dataset, anexo o manifiesto reproducible.
- **Auditoría:** método, cálculo, veredicto o nota reproducible del proyecto.
- Mirrors de filings regulatorios quedan rotulados explícitamente como copias de filing, no como host primario del emisor.

## Inventario por pestaña

| Pestaña | refs | primaria | dato | auditoría | estado |
|---|---:|---:|---:|---:|---|
| La historia del dashboard | 3 | 0 | 0 | 3 | ok |
| Poder adquisitivo | 18 | 14 | 4 | 0 | ok |
| Tasas e inflación | 9 | 7 | 1 | 1 | ok |
| Inflación por presidencia | 3 | 3 | 0 | 0 | ok |
| Pobreza: nivel absoluto | 4 | 4 | 0 | 0 | ok |
| Asistencia social / transferencias | 7 | 6 | 1 | 0 | ok |
| Desigualdad (Gini) | 6 | 5 | 1 | 0 | ok |
| Más allá de la pobreza | 6 | 4 | 2 | 0 | ok |
| ¿Cuánto necesita una familia? | 6 | 6 | 0 | 0 | ok |
| Riesgo país | 2 | 1 | 0 | 1 | ok |
| Índice Big Mac | 5 | 3 | 1 | 1 | ok |
| Precios mayoristas | 5 | 1 | 3 | 1 | ok |
| Salud y educación | 6 | 5 | 0 | 1 | ok |
| Consumo | 35 | 27 | 8 | 0 | ok |
| Trabajo | 9 | 9 | 0 | 0 | ok |
| Inversión | 4 | 4 | 0 | 0 | ok |
| Vivienda | 21 | 19 | 2 | 0 | ok |
| Crecimiento | 5 | 4 | 1 | 0 | ok |
| Actividad real · ¿crecimiento o rebote? | 6 | 3 | 1 | 2 | ok |
| Morosidad · ¿la gente puede pagar sus deudas? | 8 | 0 | 7 | 1 | ok |
| Del shock a la mora | 2 | 2 | 0 | 0 | ok |
| ¿Qué explica la mora? | 7 | 7 | 0 | 0 | ok |
| Anatomía de la mora | 1 | 1 | 0 | 0 | ok |
| Jóvenes y crédito | 1 | 1 | 0 | 0 | ok |
| Péndulo del poder económico | 11 | 4 | 1 | 6 | ok |
| Resultado fiscal | 5 | 5 | 0 | 0 | ok |
| Balanza comercial | 4 | 3 | 1 | 0 | ok |
| BCRA · reservas y dólar | 5 | 4 | 0 | 1 | ok |
| Espiral de deuda | 4 | 4 | 0 | 0 | ok |
| Programa y escenarios | 13 | 13 | 0 | 0 | ok |
| Grandes fortunas | 5 | 4 | 0 | 1 | ok |
| Lo que te robó Milei | 20 | 14 | 4 | 2 | ok |
| Privilegios fiscales | 11 | 10 | 0 | 1 | ok |
| La casta | 21 | 19 | 1 | 1 | ok |
| Rutas · ¿Público o privado? | 6 | 6 | 0 | 0 | ok |
| Vacaciones · Turismo | 6 | 6 | 0 | 0 | ok |
| Deuda pública | 5 | 5 | 0 | 0 | ok |

## Integridad local

`FUENTES_VALIDACION_2026-08-27.csv` registra el estado archivo por archivo después del patch V70.

- faltantes: `ninguno`
- hash mismatch: `ninguno`
- rutas HTML rotas: `ninguna`

## Salvedades metodológicas consolidadas

- Q4-2023 no es una ventana post-10/12 limpia.
- Pases BCRA y pases con otras entidades financieras deben separarse a nivel de flujo; no usar stock al cierre como proxy.
- Estados consolidados de grupos no se suman al panel sistémico individual.
- Un producto de crédito minorista no identifica por sí solo al sector institucional hogar.
- `DIRECT_HOUSEHOLD_TO_BANK_TRANSFER` no se eleva desde sobrecosto, rentabilidad o simultaneidad: requiere identidad contractual/contable compatible.
- `+7,7 pp` del IEF sigue sin reparto BCRA/interbancario identificado a nivel sistema.
