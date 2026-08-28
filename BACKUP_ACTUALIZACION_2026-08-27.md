# Actualización y organización de fuentes — 27-08-2026

## Cambios

- Consolidado `data/fuentes/FUENTES.csv`: **106 entradas**.
- Se integró el snapshot `FUENTES_NUEVAS_2026-08-25.csv` al manifiesto maestro.
- Nueva tanda: `FUENTES_NUEVAS_2026-08-27.csv`.
- Nuevo índice humano: `data/fuentes/README.md` y `FUENTES_POR_TEMA.md`.
- Nueva rama documental: `data/fuentes/ciclo_ajuste/`.
- Nueva rama documental: `data/fuentes/hogares/`.
- Nueva validación de archivos/hashes: `FUENTES_VALIDACION_2026-08-27.csv`.
- Nueva auditoría global: `data/derivados/AUDITORIA_COBERTURA_FUENTES_V194.md`.
- `index.html`: sólo se actualizó el registro de fuentes (corte, auditoría y acceso al catálogo); no se tocaron series ni gráficos.

## Integridad

- archivos locales faltantes: **0**;
- hashes incompatibles: **0**;
- rutas locales de fuentes rotas en el HTML: **0**.

## Política de snapshots

Los `FUENTES_NUEVAS_YYYY-MM-DD.csv` no se borran: funcionan como historial. `FUENTES.csv` es el estado canónico actual.


## Patch post-V70 · contrapartes bancarias y trazabilidad

- `FUENTES.csv`: **136 entradas**.
- Nueva tanda: `data/fuentes/FUENTES_NUEVAS_2026-08-27_V70.csv`.
- `REFERENCIAS_CICLO_AJUSTE_V70.md` pasa a ser el mapa vigente; V51 queda como snapshot histórico.
- Se incorporan fuentes primarias/regulatorias V64–V70 para ICBC, Valores, Macro, Supervielle, Santander, Nación, Provincia, Credicoop y Ciudad, más las fuentes BCRA para el gate producto→sector.
- Se incorporan auditorías reproducibles V70 y paneles machine-readable con hashes.
- `index.html`: sólo cambia trazabilidad visible (links al mapa/veredicto V70 + auditoría global V195); **no se cambian series, datos ni gráficos**.
- Claims revocados quedan expresos: `7,7 pp = BCRA`, floor 26,83%, stock=flujo, producto=hogar y submuestra abierta=sistema no deben reaparecer.
