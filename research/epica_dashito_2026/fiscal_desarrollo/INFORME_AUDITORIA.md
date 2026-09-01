# Análisis empírico — fiscal, balances sectoriales, inversión-empleo e infraestructura

**Fecha de corte:** 2026-08-31  
**Ítems de la épica:** 3–4, 17–25 y 36–40  
**Regla de lectura:** se distingue dato observado, identidad, input administrativo, proyección y outcome. Ningún resultado causal se identifica sólo por simultaneidad.

## Resultado ejecutivo

1. **La incidencia salarial fue desigual.** Con IPC nacional e índices INDEC, desde noviembre de 2023 el salario real privado registrado tocó un mínimo de 87.87 en 2024-03 y a junio de 2026 seguía -3.55% respecto de la base. El público tocó 78.14 y seguía -16.52%. El no registrado arroja un salto extremo y queda marcado para revisión metodológica, no como mejora consolidada.

2. **Hubo desahorro/fragilidad observada, pero no una cuenta sectorial completa de hogares.** El uso declarado de ahorros subió de 27.6% a 40.1% entre 1S-2018 y 1S-2024 (+12.5 pp). El stock BCRA cayó 20,6% real en 1S-2024 y luego se informó +21,7% semestral; empalmados mecánicamente darían 96.63 (base dic-2023=100), no 105,5 como la variación interanual reportada. La brecha de 8.87 pp impide unir ambas publicaciones sin revisar revisiones/perímetros.

3. **Superávit fiscal no implica por identidad déficit de hogares.** El resultado financiero del SPN mejoró 4.700 pp del PIB entre 2023 y 2024. A la vez, la cuenta corriente pasó de USD 20.956 M de déficit en 2023 a USD 6.285 M de superávit en 2024. La identidad permite que el sector privado agregado tenga capacidad de financiamiento si el saldo externo compensa el superávit público; estos datos no separan hogares de empresas ni igualan perímetros/monedas para cerrar una cuenta exacta.

4. **La actividad se recuperó sin recomponer en igual dirección el empleo privado registrado.** Entre nov-2023 y abr-2026, EMAE desestacionalizado +5.15% y EMAE per cápita +4.69%; asalariados privados registrados -3.94% (251.500 menos). Es coexistencia, no prueba de que capital “cause” menos empleo ni elasticidad sectorial.

5. **RIGI: empleo anunciado/proyectado, no empleo realizado.** Los 16 proyectos aprobados informados el 11/06/2026 sumaban USD 29.892 M y 54.495 empleos directos+indirectos: 1823 por USD 1.000 M. Ese total equivale mecánicamente a 21.7% de la pérdida neta de asalariados privados registrados desde nov-2023, pero los universos, horizontes y estados no son comparables. Pampa urea ilustra el problema: 3.500 empleos directos+indirectos de construcción y 300 operativos permanentes para USD 2.700 M.

6. **El flujo fiscal mejoró mientras el flujo de inversión pública cayó; el patrimonio no está medido.** Índice real de inversión pública 2023=100: 2024=24.90, 2025=18.18. Esto prueba menor flujo ejecutado, no depreciación física. Para un resultado fiscal ajustado se necesitan stock de activos, mantenimiento necesario y tasas de depreciación por clase.

## Balances sectoriales: qué puede y qué no puede cerrarse

La identidad relevante, con signos explícitos, es:

`(S-I)_privado = (G-T) + CC`

donde `G-T` es déficit público y `CC` la cuenta corriente. Un superávit público hace `G-T<0`, pero no obliga a `(S-I)_privado<0` si la cuenta corriente es suficientemente positiva. El repositorio permite verificar fiscal, cuenta corriente y señales de hogares; no contiene una cuenta no financiera trimestral que separe hogares, sociedades no financieras y sociedades financieras. Por eso la parte “qué correspondió a empresas” queda N/D.

## Incidencia y auditor de relatos

- El cuadro de incidencia se entrega como matriz no aditiva. No se suman salarios, personas, inversión, rentabilidad y transferencias.
- “Aprobado RIGI” es input administrativo; “inversión comprometida” es compromiso; “empleo asociado” es proyección; “empleo SIPA” es observado.
- 741.71 km de corredores figuran en operación y 2613.53 km al incluir adjudicados. Son km concesionados, no construidos ni rehabilitados.
- En infraestructura, el descenso presupuestario es flujo. No autoriza a cuantificar el deterioro del stock sin inventario físico comparable.
- Para los ítems 21, 22, 24, 25, 36, 39 y 40 se prioriza N/D con requerimiento de dato, en vez de inferir outcomes desde normas, anuncios o caja.

## Neutralidad de Ingresos Brutos

Con recaudación `R=t·B`, si la alícuota cae una fracción `r`, neutralidad exige `B_1/B_0=1/(1-r)`. Las bajas de 10%, 25% y 50% exigen, mecánicamente, aumentos de base de 11,11%, 33,33% y 100%. Con alícuota cero no existe base finita que preserve la recaudación del mismo impuesto. Esto no pronostica formalización ni actividad.

## Fuentes primarias y corte

- INDEC: salarios, IPC, EMAE y balanza de pagos.
- Secretaría de Trabajo/SIPA: trabajadores registrados.
- OPC sobre E-Sidif: inversión pública 2024–2025.
- INDEC EPH y BCRA: uso/stock de ahorro de hogares.
- Ministerio de Economía/Presidencia: RIGI; por ser fuente promotora, sus empleos se tratan como proyección.
- Vialidad/Argentina.gob.ar: estado administrativo de concesiones.

Las URLs, fechas, unidades, límites y confianza están en `matriz_dato_fuente_confianza.csv`. La cobertura y los faltantes por ítem están en `matriz_brechas_epica.csv`.

## Qué falta para causalidad

1. Microdatos longitudinales de hogares con ingreso, ahorro, deuda y consumo.
2. Cuentas por sector institucional separando hogares y sociedades.
3. Ejecución física/financiera y empleo realizado por proyecto RIGI, con horizonte y permanencia.
4. Panel sectorial de inversión, horas, empleo, masa salarial y productividad.
5. Inventario físico y depreciación del capital público.
6. Diseños contrafactuales preespecificados para shock vs gradualismo; no basta comparar antes/después.
