# Auditoría de cobertura y organización de fuentes · v194

Fecha de revisión: **27 de agosto de 2026**.  
Archivo auditado: `index.html`.

## Resultado

- Pestañas detectadas: **37**.
- Pestañas con al menos una referencia visible: **37**.
- Pestañas sin referencia visible: **0**.
- Catálogo maestro `FUENTES.csv`: **106 entradas**.
- Entradas con URL de origen: **94**.
- Entradas con archivo local: **59**.
- Archivos locales faltantes según manifiesto: **0**.
- Hashes SHA-256 incompatibles: **0**.
- Rutas `data-source-path` únicas usadas por el HTML: **17**.
- Rutas `data-source-path` inexistentes: **0**.

## Qué cambió respecto de v149

1. `FUENTES.csv` pasa a ser el **manifiesto canónico consolidado**: incorpora la tanda del 25/08 y la del 27/08 sin cambiar el esquema consumido por los builders.
2. Los archivos `FUENTES_NUEVAS_*` quedan como snapshots históricos de incorporación.
3. Se agregan referencias oficiales para la rama **ciclo de ajuste / buffers / canales bancarios** (2014, 2018, 2023–24).
4. Se agrega la rama **ahorro y stock de hogares**, con EPH 2018/2024 y BCRA 2024/2025.
5. Se incorpora `data/fuentes/README.md` como puerta de entrada humana y `FUENTES_POR_TEMA.md` como índice.
6. El registro visible del dashboard apunta ahora a esta auditoría y muestra corte 27/08/2026.

## Reglas de clasificación

- **Primaria:** publicación/norma del organismo de origen.
- **Dato:** serie, archivo, dataset o manifiesto reproducible.
- **Auditoría:** método, cálculo o nota reproducible del proyecto.
- Referencias externas no oficiales deben estar expresamente rotuladas como tales.

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

`FUENTES_VALIDACION_2026-08-27.csv` registra el estado archivo por archivo. La actualización no modifica el contenido de los archivos fuente ya hashados.

## Salvedades metodológicas nuevas

- El uso de ahorros EPH mide **incidencia de estrategia**, no monto de consumo financiado con stock.
- El stock financiero BCRA es de personas humanas dentro de productos observados; `PH financiera != hogar EPH`.
- Recuperación agregada del stock en 2S-2024 no identifica que los mismos hogares hayan recompuesto su colchón.
- En bancos, FX, títulos, pases, CER, fondeo e incobrabilidad son componentes distintos; no sumar gross positives como utilidad neta.
- Q4-2023 no es una ventana post-10/12 limpia.
- `DIRECT_HOUSEHOLD_TO_BANK_TRANSFER` permanece N/D salvo identidad contractual/contable compatible.
