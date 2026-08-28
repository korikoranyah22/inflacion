# Auditoría V55 — materialización de bytes y reconciliación de subcuentas

## 1. Byte gate

Los endpoints XLS/XLSX oficiales listados en V54 siguen sin poder descargarse desde el runtime. El navegador web puede verificar su existencia y tipo MIME, pero no exponer sus bytes; el downloader tampoco consiguió materializarlos.

Se realizó una búsqueda dentro de todos los ZIP aportados por la usuaria. `inflacion-backup(2).zip` contiene una copia local de `es_series.txt`. Se extrajo sin modificar y se calculó:

```text
bytes = 5827774
sha256 = 46089e8501001529f6a089e9981fb72f1e5f46e8817504ddc76f18996f28dd2b
```

Este gate **pasa sólo para el esquema de series**, no para los valores 2023.

## 2. Hallazgo de esquema

El archivo local permite reconstruir el diccionario de `Cuadro de resultados` (códigos 1150–1192 relevantes). La estructura revela que el detalle histórico distingue fuentes contables que el informe agregado combina.

### Intereses

```text
1151 total ganado
1153 préstamos + actualización de capital indexado
1154 pases activos
1155 ventas FX a futuro
1156 otras financiaciones

1157 total pagado
1158 depósitos + actualización de capital indexado
1159 pases pasivos
1160 compras FX a futuro
```

Esto puede separar **fuente contable**, no sector económico del prestatario/depositante.

### Inversiones

```text
1184 inversiones totales
1185 títulos públicos
1186 participaciones/fideicomisos/otros privados
1187 obligaciones negociables
1188 obligaciones subordinadas
1189 opciones
1190 participaciones permanentes
```

`1185` mezcla renta, FX, ajustes/actualización, venta y previsión. No es una cuenta “Tesoro pagó X”.

### FX

`1192` mezcla venta y actualización mensual de activos/pasivos en oro y FX, actualización de operaciones a término liquidables en pesos y swaps. Esto refuerza la revocación V54 de etiquetar íntegramente `+11,3 pp` como valuación.

## 3. Intento de reconciliación

No se ejecutó una reconciliación numérica falsa. Para reconciliar Q3 vs Q4 2023 hacen falta observaciones mensuales de los códigos anteriores o equivalentes NIIF. Sin esos valores no puede demostrarse que su suma llegue exactamente a los targets congelados `+7,3`, `+2,1`, `-0,2`, `+11,3 pp`.

## 4. Gate temporal/NIIF

La página oficial actual del BCRA indica que el TXT de catálogo está actualizado hasta 2021. Por eso la existencia de una cuenta en `es_series.txt` **no prueba por sí sola** que la misma equivalencia haya seguido vigente sin cambios en 2023. La continuidad debe validarse con los valores/metadata modernos o el archivo `baldethis` actual.

## 5. Resultado distributivo

No se eleva ningún nuevo share de hogares, Tesoro o mercado. Se conserva:

```text
STRICT_DIRECT_COUNTERPARTY = pases → BCRA = 7.7 pp
UNRESOLVED_COUNTERPARTY = 21.0 pp
HOUSEHOLD_DIRECT_POINT_ESTIMATE = N/D
```

La investigación gana precisión de arquitectura de datos, no una nueva cifra distributiva.
