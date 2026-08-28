# FUENTES V56 — Series values + NIIF bridge

## Fuente local oficial cacheada

- BCRA `Series_estadisticas.xlsx`
  - URL canónica: `https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Series_estadisticas.xlsx`
  - copia dentro del repositorio entregado por la usuaria: consulta `2026-08-21`
  - SHA256: `3d9a98fa443b833ebb34c814863c1259a89d4ab8d59570578ee030c00288b5d0`
  - uso V56: verificar continuidad del **ID de serie publicado**, periodicidad y ubicación TXT.

- BCRA `es_series.txt`
  - SHA256: `46089e8501001529f6a089e9981fb72f1e5f46e8817504ddc76f18996f28dd2b`
  - catálogo TXT legacy, cuya página oficial actual aclara que está actualizado hasta 2021.

## Fuente oficial web verificada en V56

- BCRA, *Consulta de series estadísticas en formato TXT*. Define el formato `código;fecha;valor`, presenta el Excel como complemento del catálogo TXT y ubica los balances/resultados en `din1_ser.txt`.
- BCRA, API Estadísticas Monetarias v4.0. La documentación vigente expone `GET /estadisticas/v4.0/monetarias/{IdVariable}` con parámetros `desde`, `hasta`, `limit` y `offset`.

## Gate pendiente

No se materializaron los valores 2023 de `din1_ser.txt` ni respuestas API. Por lo tanto V56 **no publica valores ni shares sectoriales nuevos**.
