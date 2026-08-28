# Arqueología de fuentes — batch 3 (V32 / V48 / V50 / V52–V59)

Fecha: 2026-08-28

## Resultado

- material subido: **13** archivos (11 ZIP + 2 MD)
- carriers ZIP únicos por SHA-256: **9**; las tres copias V59 son byte-idénticas
- miembros top-level V52–V59 comparados con los checkpoints actuales: **125 / 125 byte-idénticos**
- binarios fuente recursivos únicos hallados en V52–V59/V32: **1**
- binarios fuente nuevos por SHA-256: **0**
- `Series_estadisticas.xlsx` reaparece en V56 pero ya estaba preservado exactamente
- referencias históricas a binarios directos identificadas: **30**
- ya preservadas/reconciliadas: **8**
- segunda cola binaria accionable: **35**
- registro completo de preservación pendiente: **68** items = **35** binarios accionables + **33** páginas/referencias sin binario directo identificado

## Reconciliaciones locales

Se vinculó `bcra_entidades_dic2023_red_pases` con el `202312e.pdf` que ya estaba físicamente dentro de `research/ciclo_ajuste/inputs/bcra/2023-12/`. También se incorporaron al catálogo maestro cinco assets BCRA históricos ya existentes en el repo: `202309e.pdf`, `Glosario.pdf`, `InfBanc_Anexo.xlsx`, `Infbanc0923.xlsx` y `InfBanc0923.pdf`. Todos quedaron con SHA-256 calculado sobre el archivo local.

## Backfill round 2

`SOURCE_BACKFILL_REQUEST_V96_ROUND2.csv` contiene únicamente URLs binarias directas que todavía no tienen el binario exacto preservado. `tool_round2/` es una copia de la herramienta Windows que completó la corrida anterior, con esta nueva cola cargada.

La referencia histórica V57 a `bolmetes.pdf` expone `https://www.bcra.gob.ar/pdfs/publicacionesestadisticas/bolmetes.pdf`; se usa como candidato alternativo al endpoint `web2` que devolvió 401. El `boldat202505.pdf` que falló por DNS sigue en la cola.

## Estado de investigación

Esta operación es exclusivamente de preservación y arqueología. V96 sigue congelado en **24 entidades exactas**, cobertura strict **59.777595746322620480650441147276358824911189326119979767253088259998915899707248%** y gate **NO**. P0/P1 permanecen en cero; la nueva cola se etiqueta P2 histórica/source-completeness.

## Ampliación desde RAW manifests

V54/V55 documentaban endpoints binarios que no habían entrado en el extractor inicial: `perser_priv.xls`, `perser_pub.xls`, `titpubser.xls`, `finuva_mensual.xls`, `depuva_mensual.xls`, `Infbanc1218.xls`, `baldethis.xls`, `din3_ser.txt` y `din4_ser.txt`. Se sumaron a round 2. También se tiparon como PDF los endpoints directos sin extensión de BAPRO FY, BAPRO Disciplina de Mercado y Credicoop FY. La cola accionable final queda en **35**.
