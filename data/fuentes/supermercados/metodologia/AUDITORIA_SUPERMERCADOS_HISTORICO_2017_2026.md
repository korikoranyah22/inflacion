# Auditoría — Historia de supermercados 1996–2026 por eras

Fecha: 04-09-2026.

## Qué se integró
- Archivo mensual histórico de INDEC: 216 meses, ene-1996 → dic-2013, con índices real y nominal base abril de 2008=100.
- Vista larga anual de ventas reales: 1996–2013 y 2017–jun-2026 como dos tramos independientes, sin empalme; cada tramo se rebasa a 100 en su propio año inicial.
- Núcleo mensual moderno real + nominal: 114 meses, ene-2017 → jun-2026, base 2017=100.
- Profundidad de primeros semestres 2017–2026.
- Medios de pago: snapshots 2020–2025 + jun-2026.
- Operaciones y ticket nominal: snapshots dic-2017–dic-2025 + jun-2026.
- Estructura del canal: bocas y superficie en un tramo histórico 2008–2016 y un tramo moderno dic-2017–jun-2026. El cambio/ampliación de panel queda visible y no se interpreta como aperturas.
- Composición nominal por rubros: dic-2023, dic-2024 y abr-2026.
- Foto territorial 1S-2026 con referencias explícitamente publicadas.
- Storytelling: “Cuando descubrimos que consumo tampoco era una sola cosa”.

## Validaciones clave
- La serie histórica contiene 216 meses únicos: ene-1996 → dic-2013.
- La serie moderna contiene 114 meses únicos: ene-2017 → jun-2026.
- La vista larga contiene 28 observaciones anuales: 18 del tramo histórico y 10 del moderno; 2026 es parcial y promedia enero–junio.
- 1S-2026 nivel real medio: 79.8358.
- 1S-2026 vs 1S-2025: -2.82%.
- 1S-2026 vs promedio 1S 2017–2025: -9.22%.
- Panel anterior, 2008 → nov-2014: bocas +39,1%; superficie +32,5%.
- Núcleo moderno, dic-2017 → dic-2025: bocas +5,9%; superficie +3,3%.
- Milei, dic-2023 → dic-2025: bocas -0,2%; superficie +0,9%.
- Participaciones de medios de pago suman 100% (salvo diferencias de redondeo nulas).

## Observado vs derivado
- 1996–2013: índices mensuales observados en el XLS oficial; el promedio anual y el rebase a promedio 1996=100 son derivados.
- 2019–abr-2026: índices portados de publicaciones INDEC.
- 2017–2018: índices nominales normalizados desde ventas oficiales y real reconstruido desde las ventas constantes publicadas; estado marcado como DERIVADO.
- may–jun-2026: índices incorporados/derivados desde variaciones interanuales y montos corrientes oficiales disponibles en el dashboard; están marcados como DERIVADOS.
- 2017–2026 en la vista larga: promedio anual y rebase a promedio 2017=100 derivados; 2026 conserva la marca de período parcial.
- Ticket real: proxy derivado usando el índice de precios implícito de la encuesta. No equivale a cantidad física.
- Estructura 2008–1S 2013: valores observados de la tabla anual/semestral de INDEC. Nov-2013, nov-2014 y dic-2016 provienen de los cuadros de los informes mensuales correspondientes. Las fechas exactas se conservan en el CSV.
- Estructura 2017–2026: snapshots observados en la serie oficial moderna. Bocas y superficie son medidas del canal relevado; no identifican qué decil recibió o perdió ingreso.

## Lo que deliberadamente NO se fabricó
1. No se empalmó 1996–2013 con 2014+; INDEC documenta una discontinuidad por cambio de ponderadores y deflactores desde enero de 2014.
2. No se usó 2014–2016 como puente para ventas reales: sus publicaciones atraviesan cambios de deflactor y la encuesta amplía su panel desde enero de 2017. En estructura se muestran nov-2014 y dic-2016 como observaciones del panel anterior, pero se corta la línea antes del núcleo 2017+.
3. No se creó un heatmap provincial 2017–2026 sin integrar una serie real homogénea por jurisdicción.
4. No se interpretó tarjeta de crédito como deuda revolvente.
5. No se interpretó número de operaciones como personas únicas.
6. No se construyó una serie real larga por rubro sin deflactores compatibles.
7. No se interpretó la expansión de bocas o superficie como redistribución del ingreso. Esa hipótesis requiere EPH por decil, empleo y transferencias.

## Fuentes primarias
- INDEC · Serie histórica de ventas de supermercados 1996–2013: https://www.indec.gob.ar/ftp/nuevaweb/cuadros/14/sh_ventas-super.xls
- INDEC · Archivo histórico / discontinuidad: https://www.indec.gob.ar/indec/web/Institucional-Indec-InformacionDeArchivo-1
- INDEC · Encuesta de supermercados: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-1-34
- INDEC · Anuario con estructura 2008–2012 y 1S-2013: https://biblioteca.indec.gob.ar/bases/minde/63ae2012.pdf
- INDEC · Informes de estructura nov-2013, nov-2014 y dic-2016: https://sitioanterior.indec.gob.ar/uploads/informesdeprensa/super_01_14.pdf · https://sitioanterior.indec.gob.ar/uploads/informesdeprensa/super_01_15.pdf · https://sitioanterior.indec.gob.ar/uploads/informesdeprensa/super_02_17.pdf
- Informes mensuales de la Encuesta de Supermercados 2017–2026.

## Estado de evidencia
- Serie histórica 1996–2013: A para el dato mensual oficial; B para agregación anual y rebase, con transformación reproducible.
- Real/nominal moderno: A/B (observado y reconstrucción identificada).
- Medios de pago / estructura: A en observaciones incorporadas; los dos paneles estructurales no se empalman.
- Ticket real proxy: DERIVADO.
- Territorio histórico largo: N/D.
- Transición 2014–2016: no integrada como serie comparable; se representa como discontinuidad.
- Lectura distributiva desde estructura comercial: N/D; la visualización la separa explícitamente del dato observado.

## QA técnico final
- HTML: 0 IDs duplicados.
- Navegación: botones y paneles sin destinos rotos.
- JavaScript inline: todos los scripts pasan `node --check`.
- Serie histórica: 216 meses únicos, ene-1996 → dic-2013.
- Serie moderna: 114 meses únicos, ene-2017 → jun-2026.
- Vista larga: 28 puntos anuales; bases y período parcial rotulados en gráfico y CSV.
- Medios de pago: todos los snapshots suman 100,0%.
- Storytelling: capítulo y enlace interno presentes.
- La vista se verificó visualmente en navegador local de escritorio.
