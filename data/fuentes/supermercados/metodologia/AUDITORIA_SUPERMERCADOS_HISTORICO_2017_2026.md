# Auditoría — Historia de supermercados 2017–2026

Fecha: 25-08-2026.

## Qué se integró
- Núcleo mensual real + nominal 2017–jun-2026, base 2017=100.
- Profundidad de primeros semestres 2017–2026.
- Medios de pago: snapshots 2020–2025 + jun-2026.
- Operaciones, ticket nominal, bocas y empleo: snapshots dic-2020–dic-2025 + jun-2026.
- Composición nominal por rubros: dic-2023, dic-2024 y abr-2026.
- Foto territorial 1S-2026 con referencias explícitamente publicadas.
- Storytelling nuevo: “Cuando descubrimos que consumo tampoco era una sola cosa”.

## Validaciones clave
- 1S-2026 nivel real medio: 79.8358.
- 1S-2026 vs 1S-2025: -2.82%.
- 1S-2026 vs promedio 1S 2017–2025: -9.22%.
- La serie moderna contiene 114 meses: ene-2017 → jun-2026.
- Participaciones de medios de pago suman 100% (salvo diferencias de redondeo nulas).

## Observado vs derivado
- 2019–abr-2026: índices portados de publicaciones INDEC.
- 2017–2018: índices nominales normalizados desde ventas oficiales y real reconstruido desde las ventas constantes publicadas; estado marcado como DERIVADO.
- may–jun-2026: índices incorporados/derivados desde variaciones interanuales y montos corrientes oficiales disponibles en el dashboard; están marcados como DERIVADOS.
- Ticket real: proxy derivado usando el índice de precios implícito de la encuesta. No equivale a cantidad física.

## Lo que deliberadamente NO se fabricó
1. No se empalmó 1996–2013 con 2014+; INDEC documenta una discontinuidad por cambio de ponderadores/deflactores.
2. No se creó un heatmap provincial 2017–2026 sin integrar una serie real homogénea por jurisdicción.
3. No se interpretó tarjeta de crédito como deuda revolvente.
4. No se interpretó número de operaciones como personas únicas.
5. No se construyó una serie real larga por rubro sin deflactores compatibles.

## Fuentes primarias
- INDEC · Encuesta de supermercados: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-1-34
- INDEC · Archivo histórico / discontinuidad: https://www.indec.gob.ar/indec/web/Institucional-Indec-InformacionDeArchivo-1
- Informes mensuales de la Encuesta de Supermercados 2017–2026.

## Estado de evidencia
- Real/nominal moderno: A/B (observado y reconstrucción identificada).
- Medios de pago / estructura: A en snapshots incorporados.
- Ticket real proxy: DERIVADO.
- Territorio histórico largo: N/D.
- Historia numérica 1996–2016: no integrada en esta pasada; sólo se conserva la arquitectura por eras y la advertencia metodológica.

## QA técnico final
- HTML: 0 IDs duplicados.
- Navegación: 37 botones de tab / 37 paneles; 0 destinos rotos.
- JavaScript inline: 16/16 scripts pasan `node --check`.
- Serie moderna: 114 meses únicos, ene-2017 → jun-2026.
- Medios de pago: todos los snapshots suman 100,0%.
- Storytelling: capítulo y enlace interno presentes.
- QA visual automatizado no ejecutado: el entorno no habilita navegador local; se realizó QA estático/estructural.
