# Source references — V81

## Binario BCRA auditado

- `research/ciclo_ajuste/inputs/bcra/2023-09/InfBanc_Anexo.xlsx`
- SHA-256: `9b1b48b18039389889ee7d480a9c6d8958fb99630f169339e46ab953e7133251`
- Nota V81: el directorio refleja el contexto de recuperación, no la fecha de corte interna del anexo. El contenido del XLSX llega a enero-2026.

## BCRA — páginas y normativa

- Informe sobre Bancos, enero de 2026:
  `https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-enero-de-2026/`
  - publicación 20/03/2026;
  - expone `Anexo (XLSX)`;
  - confirma anexos estadísticos para sistema y grupos.

- URL estática del anexo:
  `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/InfBanc_Anexo.xlsx`

- Informe sobre Bancos, septiembre de 2023:
  `https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-septiembre-2023/`
  - publicación 23/11/2023;
  - la página migrada lista Informe, Normativa, Glosario y Series de Datos.

- Comunicación A 7749:
  `https://www.bcra.gob.ar/Pdfs/comytexord/A7749.pdf`
  - página 66: códigos `0301060100`, `0301060200`, `0302030100`, `0302030200`.

- Información sobre entidades financieras:
  `https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/`

- Catálogo de datos:
  `https://www.bcra.gob.ar/catalogo_de_datos/informacion-institucional-de-entidades-financieras/`

## BNA / AGN

- AGN Memoria 2024: trabajo 187, BNA, estados intermedios consolidados y separados al 30/09/2024.
  `https://www.agn.gob.ar/sites/default/files/Transparencia/Memorias%20AGN/2024/HTML/index.html`

- BNA resumen 9M-2024:
  `https://www.bna.com.ar/Downloads/Institucional_MemoriayBalances_BALANCE%20CONDENSADO%20SEP%202024.pdf`
  - control/resumen; no four-leg.

## IPC interno del repo

- `data/fuentes/tasas/indec/serie_ipc_divisiones.csv`
  - IPC Nacional 2026-01 = 10413.0309
  - IPC Nacional 2023-12 observado = 3533.1922
  - por regla congelada del proyecto se conserva 3533.2 para transformaciones V60+.

## Regla

Fuentes agregadas/control-only no cruzan el gate individual/separado.
