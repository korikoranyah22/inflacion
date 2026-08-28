# AUDITORÍA V56 — Series values + NIIF bridge

## 1. Pregunta de V56

¿Los códigos detallados recuperados en V55 sobreviven en el catálogo moderno, y podemos usar sus valores Sep–Dic 2023 para reconciliar los componentes Q4-2023?

## 2. Gate de continuidad

**PASS a nivel de serie publicada.**

Los 23 códigos `1150–1162` y `1183–1192` aparecen en la copia oficial moderna de `Series_estadisticas.xlsx`, todos con periodicidad **Mensual** y ubicación TXT **DIN1**. La copia tiene SHA256 `3d9a98fa443b833ebb34c814863c1259a89d4ab8d59570578ee030c00288b5d0` y el repositorio fuente registra consulta `2026-08-21`.

Esto reduce sustancialmente el riesgo de que el bridge V55 se haya vuelto irrelevante después de NIIF.

### Límite

No elevar esto a `UNDERLYING_ACCOUNT_EQUIVALENCE = EXACT`. El ID de la serie publicada puede conservarse aunque el BCRA haya cambiado relaciones internas del plan de cuentas, agregaciones o reglas de compilación. Las notas metodológicas tampoco son textualmente idénticas en todos los casos.

## 3. Gate de valores

**FAIL por runtime, no por inexistencia documental.**

- `din1_ser.txt` está publicado por BCRA, pero el navegador corta el archivo por tamaño.
- El runtime de contenedor no resolvió DNS hacia la API.
- Los XLS alternativos no pudieron materializarse como bytes.
- La API v4 actual sí documenta consulta individual por `IdVariable` y rango de fechas; se deja `fetch_bcra_v4_values.py` para una ejecución con red.

## 4. Reconciliación

No se ejecutó la reconciliación numérica de:

- títulos `+7.3 pp`;
- ingresos por intereses `+2.1 pp`;
- CER `-0.2 pp`;
- FX `+11.3 pp`.

La ausencia de valores significa que cualquier share nuevo sería imputado, no observado.

## 5. Contrapartes

No cambia el piso estricto de V54/V55:

```text
Pases → BCRA = 7.7 pp = 26.83%
Contraparte no resuelta = 21.0 pp = 73.17%
```

No confundir continuidad de código con cuantificación de incidencia.
