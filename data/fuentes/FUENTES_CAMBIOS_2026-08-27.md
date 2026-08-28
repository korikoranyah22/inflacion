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


## Patch Ciclo del Ajuste · post V70

- `FUENTES.csv`: **136 entradas**.
- Nueva tanda: `FUENTES_NUEVAS_2026-08-27_V70.csv`.
- `ciclo_ajuste/REFERENCIAS_CICLO_AJUSTE_V70.md` pasa a ser el mapa vigente; V51 queda marcado como snapshot histórico.
- Se incorporan fuentes V64–V70 para contrapartes de pases, base individual regulatoria y mapping producto→sector.
- Se incluyen `AUDITORIA_CICLO_AJUSTE_V70.md`, `VEREDICTO_CICLO_AJUSTE_V70.md` y paneles reproducibles con hashes.
- Nueva auditoría global: `data/derivados/AUDITORIA_COBERTURA_FUENTES_V195.md`.
- `index.html`: sólo se agregan accesos/documentación de trazabilidad; no se modifican series ni gráficos.

### Gates preservados

```text
7_7PP_AS_STRICT_BCRA_FLOOR = REVOKED
IEF_7_7PP_BCRA_SHARE = N/D
STOCK_AS_PASS_FLOW_COUNTERPARTY_PROXY = REJECTED
SUBSET_INTERBANK_NETTING_AS_SYSTEM_TEST = REJECTED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
CLOSED_PASS_NETWORK = NOT_ACHIEVED
```
