# Auditoría V107 — mapa primario E0 2001–2003

## Punto de partida

V106 dejó correctamente cerrado el panel microbancario en 30 entidades y abrió la rama histórica, pero su bootstrap describió de manera incompleta el acervo local E0. V107 revisó el repositorio antes de buscar fuentes nuevas.

## Censo local corregido

El repositorio ya preservaba siete fuentes BCRA con cobertura 2001–2003:

1. tasas mensuales de préstamos;
2. detalle histórico de balances/resultados;
3. préstamos/depósitos privados por tipo de titular;
4. préstamos/depósitos públicos por jurisdicción;
5. tenencias de títulos públicos por emisor;
6. archivo diario de activos/títulos/préstamos;
7. archivo diario de pasivos/depósitos, conservado como ZIP restaurable.

Los cinco XLS fueron abiertos con el proveedor ACE OLEDB sin reescribir los originales. Se inspeccionaron hojas, dimensiones, filas 2001–2003, notas y quiebres. Los TXT se censaron por bytes/líneas y quedan pendientes de diccionario/normalización.

## Recuperación oficial V107

Se preservaron cuatro PDF BCRA y seis HTML InfoLeg. Para cada uno se verificaron ruta oficial, tamaño, firma/formato, SHA-256 y contenido identificatorio. En los PDF se inspeccionaron páginas renderizadas relevantes; el informe BCRA 2003 se conserva, pero sus fuentes internas impiden extracción textual limpia, por lo que no se incorporan cifras de ese documento.

## Evidencia material

- `baldethis.xls` contiene balances, clasificación de deudores, resultados, capital y datos físicos, con quiebres explícitos en 2002–2003.
- `perser_priv.xls` permite distinguir personas físicas y jurídicas en préstamos/depósitos, aunque mide capital/principal y aplica imputaciones.
- `titpubser.xls` registra instrumentos vinculados con compensaciones y un cambio contable en agosto de 2003.
- El Informe al Congreso 2002 documenta cronología y mecánica institucional.
- El BEF 1S 2004 registra caída real de depósitos de 42% hasta el piso, caída real de 37% del patrimonio neto consolidado durante dos años, pérdidas récord en 2002 y recuperación parcial durante 2003.
- InfoLeg congela los textos de los decretos 1570/2001, 214/2002, 471/2002 y 905/2002 y de las leyes 25.561 y 25.796.

## Clasificación de evidencia

Las seis familias E0 pasan a `PRIMARY_PARTIAL`:

- `shock`: cronología legal presente; múltiples relojes de t0 pendientes;
- `households`: depósitos/préstamos por titular presentes; faltan salarios, empleo, pobreza y consumo;
- `credit`: stocks/tasas/deudores presentes; faltan puentes comparables entre quiebres;
- `risk`: portadores primarios presentes; faltan relojes exactos de mora/previsiones/quebrantos;
- `banks`: estrés agregado y recuperación parcial documentados; falta heterogeneidad por entidad;
- `state_bcra`: mecanismos legales presentes; falta monto fiscal realizado y asignación final.

## Restricciones

- No existe un `t0` único de E0.
- Un stock contable, un bono autorizado y un pago fiscal realizado no son equivalentes.
- El receptor jurídico de una compensación no es necesariamente el beneficiario económico neto.
- La caída del agregado bancario refuta una ganancia inmediata universal, pero no prueba quién soportó cada pérdida.
- Los depósitos totales no se rotulan como hogares; para esa pregunta debe utilizarse el desglose por titular.
- No se formula una narrativa causal antes de completar el mapa social y fiscal.

## Estado de integridad

El catálogo queda en 215 entradas, 210 copias físicas y 210 hashes exactos. Las ocho brechas anteriores no aumentan: una es el PDF FY de Banco Rioja y siete son acciones discovery. La aritmética V106 se replica sin cambios en los archivos de estado V107.
