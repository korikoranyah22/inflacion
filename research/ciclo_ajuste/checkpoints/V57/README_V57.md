# README V57

V57 corrige el supuesto de que la continuidad de IDs históricos implicaba valores mensuales 2023. Desde enero de 2020 el BCRA discontinuó la publicación de resultados mensuales del viejo cuadro y publica resultados acumulados en moneda homogénea.

Esta versión reconstruye flujos trimestrales amplios Q3/Q4 2023 desde Jun/Sep/Dec acumulados, reexpresando por IPC antes de restar. Los factores son aproximados por redondeo del IPC publicado.

No hay nuevo share de contraparte: pases→BCRA permanece en 7,7 pp / 26,83%; 21,0 pp siguen sin partición directa.

`BASE_V56.zip` conserva la iteración anterior. `PROMPT_CODEX_V58_MODERN_XLSX_SUBACCOUNT_BRIDGE.md` define el próximo paso.
