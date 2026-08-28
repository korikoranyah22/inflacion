# Fuentes del repositorio

**Catálogo canónico:** `data/fuentes/FUENTES.csv`  
**Corte:** 27 de agosto de 2026  
**Entradas registradas:** 136

## Jerarquía

1. **Fuente primaria / normativa:** INDEC, BCRA, ARCA, Boletín Oficial, ministerios u organismos equivalentes.
2. **Archivo o serie reproducible:** XLS/XLSX/CSV/TXT/ZIP/PDF descargado y, cuando existe copia local, SHA-256.
3. **Auditoría / método propio:** explica transformaciones, empalmes, universos y límites causales.
4. **Referencia externa/contextual:** sólo cuando no existe una serie primaria abierta equivalente; debe quedar rotulada como secundaria.

## Archivos

- `FUENTES.csv`: manifiesto maestro y compatible con los scripts existentes.
- `FUENTES_NUEVAS_2026-08-25.csv`: snapshot histórico de la tanda incorporada el 25/08.
- `FUENTES_NUEVAS_2026-08-27.csv`: tanda inicial de ahorro/stock de hogares + ciclo de ajuste/bancos.
- `FUENTES_NUEVAS_2026-08-27_V70.csv`: patch documental V64–V70 de contrapartes, pases, base individual y mapping hogar.
- `FUENTES_VALIDACION_2026-08-27.csv`: existencia local y SHA-256 actual.
- `FUENTES_POR_TEMA.md`: índice humano agrupado por tema.
- `ciclo_ajuste/REFERENCIAS_CICLO_AJUSTE_V51.md`: snapshot histórico del mapa al cierre V51.
- `ciclo_ajuste/REFERENCIAS_CICLO_AJUSTE_V70.md`: mapa causal/documental vigente y claims revocados V52–V70.
- `ciclo_ajuste/AUDITORIA_CICLO_AJUSTE_V70.md` + `VEREDICTO_CICLO_AJUSTE_V70.md`: cierre autoritativo del patch.
- `hogares/REFERENCIAS_AHORRO_STOCK_2018_2025.md`: desahorro y stock financiero.

## Regla de no doble conteo

Una misma fuente puede alimentar distintas vistas, pero el catálogo no convierte componentes heterogéneos en una sola identidad. En particular:

```text
costo hogar != ingreso bruto banco != utilidad neta
resultado contable != efecto causal
valuación != transferencia
stock != flujo
producto != sector hogar
submuestra abierta != sistema cerrado
```

## Compatibilidad

`FUENTES.csv` conserva el esquema de columnas original para no romper los builders que lo consumen. Los snapshots `FUENTES_NUEVAS_*` se mantienen como historial de incorporación.
