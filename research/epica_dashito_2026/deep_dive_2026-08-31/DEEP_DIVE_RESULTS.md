# Profundización de preguntas abiertas · 2026-08-31

## Resultado ejecutivo

La búsqueda adicional permite cerrar dos preguntas en un perímetro definido, mejorar cuatro y confirmar que otras tres no pueden cerrarse todavía con información pública. El criterio fue conservar el nombre exacto de cada magnitud: una proyección no se presenta como realización y un residual de estrés no se presenta como reservas netas.

| Pregunta | Resultado nuevo | Estado después de profundizar |
|---|---|---|
| Estrategias de manutención mutuamente excluyentes | Calculadas desde microdatos EPH con `PONDIH` para 2025-S1, 2025-S2 y 2026-Q1 | Cerrada para las variables V13–V17 |
| Hogares que viven sólo de ingreso corriente | Se construyó un proxy observable de 25,8% en 2025-S1 y 24,5% en 2026-Q1 | Parcial: no mide suficiencia presupuestaria |
| Reservas netas/líquidas/propias | Se recuperó la definición NIR del programa, una estimación pública de ≈−USD 6.500 M en mayo y la planilla SDDS de activos y flujos | Parcial: no hay una cifra pública sincronizada con el stock bruto diario de agosto |
| Muro de deuda 2027–2031 | Perfil oficial de servicios de la Administración Central: USD 243.188 M | Cerrada para ese perímetro; no para sector público consolidado |
| Empleo RIGI real y permanente | Se actualizaron 22 proyectos, USD 47.073 M y 95.950 empleos proyectados; ningún proyecto trae desglose temporal/permanente | Sigue abierta, con ausencia documentada |
| Cuenta corriente posterior a 2026-Q1 | Al corte, INDEC sólo publicó 2026-Q1 | Sigue abierta por calendario de publicación |
| Cuentas sectoriales completas | INDEC publica gobierno general, sociedades financieras parciales y resto del mundo; no hogares ni sociedades no financieras | Sigue abierta, con ausencia documentada |
| Stock/depreciación de capital público | Cuenta de Inversión 2024 aporta bienes de uso y amortización acumulada de la Administración Central | Parcial: inventario contable, no estado físico ni gobierno general completo |

## 1. Hogares: la superposición ya puede resolverse

La réplica del dosier de INDEC usa los registros de hogares de la EPH y el ponderador de ingreso total familiar `PONDIH`. El script reproduce los principales porcentajes oficiales de 2025-S1 dentro de 0,15 puntos porcentuales y luego calcula combinaciones que el informe agregado no publica.

### Perfiles excluyentes, total de aglomerados EPH

| Perfil | 2025-S1 | 2025-S2 | 2026-Q1 |
|---|---:|---:|---:|
| Ninguna estrategia V13–V17 | 29,3% | 29,5% | 28,2% |
| Sólo ahorros | 8,8% | 7,5% | 9,2% |
| Sólo préstamos | 3,5% | 4,0% | 3,5% |
| Sólo cuotas/fiado | 21,2% | 21,2% | 21,5% |
| Sólo venta de pertenencias | 1,0% | 1,1% | 0,9% |
| Combinación de dos o más canales | 36,2% | 36,8% | 36,6% |

Por lo tanto, el uso de al menos una estrategia fue **70,7% en 2025-S1** y **71,8% en 2026-Q1**. Esto reemplaza el intervalo previo 50,9%–100% por una estimación puntual reproducible.

El proxy más estricto de “sólo recursos monetarios corrientes” exige al menos una fuente monetaria corriente declarada, ninguna fuente en especie y ninguna de las estrategias V13–V17. Da **25,8% en 2025-S1** y **24,5% en 2026-Q1**. No prueba que el ingreso alcance para todos los gastos: la EPH no observa un presupuesto completo ni pregunta si el hogar llega a fin de mes sin atrasos.

Archivos reproducibles:

- `derived/eph_strategy_summary.csv`
- `derived/eph_exclusive_profiles.csv`
- `derived/eph_exact_bitmasks.csv`
- `analyze_eph_strategies.py`

## 2. Reservas: de una resta arbitraria a un puente de liquidez

El IPOM del BCRA define reservas líquidas como reservas brutas menos oro, DEG y la parte en yuanes del swap con China. La planilla de reservas y liquidez en moneda extranjera al 31/07/2026 informa:

| Componente | USD M |
|---|---:|
| Activos de reserva oficiales | 47.599,19 |
| Reservas en moneda extranjera | 38.433,62 |
| DEG | 908,14 |
| Oro | 8.046,37 |
| Otros activos de reserva | 211,06 |

La misma planilla informa flujos netos predeterminados de la autoridad monetaria por **USD 41.779,44 M** a un año. Si se toma el stock bruto y, como estrés estático, se supone que no hay nuevos ingresos, valuación ni rollover, el residual sería:

| Horizonte | Flujos acumulados | Residual del stock bruto |
|---|---:|---:|
| Hasta 1 mes | −USD 37.127,82 M | USD 10.471,37 M |
| Hasta 3 meses | −USD 37.371,31 M | USD 10.227,88 M |
| Hasta 1 año | −USD 41.779,44 M | USD 5.819,75 M |

El informe del FMI publicado en mayo de 2026 define las reservas internacionales netas (NIR) como reservas oficiales brutas menos pasivos oficiales de reserva, a tipos de cambio del programa. Entre esos pasivos incluye obligaciones en moneda extranjera de corto plazo, compras netas al Fondo desde el inicio del programa, forwards entregables, swaps, encajes bancarios en moneda extranjera, SEDESA, ALADI y otros depósitos de no residentes. El mismo informe contiene una estimación pública de **aproximadamente −USD 6.500 M**. No es una cifra sincronizada con las reservas brutas diarias de agosto: aunque el BCRA entrega NIR al Fondo semanalmente, no se localizó una serie pública de esa frecuencia.

**USD 5.819,75 M no es una estimación oficial de reservas netas.** Es un residual mecánico de estrés que ignora entradas nuevas, renovaciones y valuación. La cifra líquida exacta tampoco puede reconstruirse porque la planilla no separa la porción en yuanes del swap con la granularidad requerida por la definición del IPOM. Una cifra positiva cercana a USD 10.000 M necesita, por lo tanto, fecha, fórmula y fuente: no debe confundirse con los USD 10.471,37 M del residual a un mes.

Archivos reproducibles: `derived/bcra_reserve_liquidity_bridge.csv` y `derived/reserve_measure_definitions_2026-09-01.csv`.

## 3. Muro de deuda 2027–2031

La hoja A.3.6 del archivo trimestral oficial al 31/03/2026 permite cerrar el perfil estático de servicios de la **Administración Central**:

| Año | Servicios | Capital | Intereses |
|---|---:|---:|---:|
| 2027 | USD 82.712 M | USD 72.570 M | USD 10.141 M |
| 2028 | USD 49.790 M | USD 40.029 M | USD 9.762 M |
| 2029 | USD 35.216 M | USD 26.234 M | USD 8.982 M |
| 2030 | USD 30.429 M | USD 22.527 M | USD 7.902 M |
| 2031 | USD 45.041 M | USD 38.448 M | USD 6.592 M |
| **Total** | **USD 243.188 M** | **USD 199.808 M** | **USD 43.379 M** |

El pico es 2027. El cuadro es un perfil contractual estático a la fecha de corte, no descuenta rollover ni nuevas operaciones y no consolida BCRA, provincias, municipios o empresas públicas. Por eso cierra la pregunta 32 para Administración Central, pero no el “muro del sector público consolidado”.

Archivos reproducibles: `derived/debt_service_2026_2031.csv` y `derived/debt_wall_summary.csv`.

## 4. RIGI: actualización y límite del dato de empleo

El portal oficial, deduplicado por nombre de proyecto igual que su interfaz, contiene al 31/08/2026:

- **22 proyectos aprobados**;
- **USD 47.073 M** de inversión comprometida;
- **95.950 empleos directos e indirectos proyectados**;
- **2.038 empleos proyectados por USD 1.000 M**.

El campo destinado al tipo de empleo está vacío en los 22 proyectos. Las resoluciones respaldadas aprueban proyectos y planes de inversión, pero no publican una serie homogénea de empleo ejecutado, permanente, temporal o por proveedor local. La serie anual escondida en el portal suma **USD 26.966 M para 2026–2031** y su eje está expresado en millones de dólares: es un cronograma de inversión, no de empleo.

Archivos reproducibles:

- `derived/rigi_projects_deduplicated.csv`
- `derived/rigi_summary.csv`
- `derived/rigi_investment_schedule.csv`
- `sources/rigi/resoluciones_html/`

## 5. Cuentas sectoriales y sector externo: ausencia confirmada

Al corte del análisis, el último informe de balanza de pagos de INDEC es 2026-Q1, con cuenta corriente de −USD 1.651 M. No hay dato oficial posterior disponible para extender la serie.

En sectores institucionales, INDEC publica series 2016–2024 para gobierno general, subsectores seleccionados de sociedades financieras y resto del mundo. No publica todavía las cuentas completas de hogares ni sociedades no financieras. Por eso no es posible descomponer el saldo privado entre ambos sectores sin imponer un residual o mezclar perímetros.

## 6. Capital público: existe un stock contable parcial

El Anexo A de los Estados Contables de la Administración Central al 31/12/2024 informa, en millones de pesos de cierre:

| Concepto | Saldo bruto | Amortización acumulada | Valor residual |
|---|---:|---:|---:|
| Total bienes de uso | $920.447 M | $238.784 M | $681.662 M |
| Construcción en proceso, dominio privado | $89.896 M | $0 M | $89.896 M |
| Construcción en proceso, dominio público | $177.922 M | $0 M | $177.922 M |
| Bienes de dominio público | $1.085 M | $0 M | $1.085 M |

Esto es un inventario contable de la Administración Central y usa valores históricos/reexpresados según sus reglas. No es un inventario físico del gobierno general, no informa condición de rutas, escuelas u hospitales y no permite estimar por sí solo el deterioro real evitado o acumulado.

Archivo reproducible: `derived/public_capital_accounting_inventory.csv`. La página auditada se renderizó en `derived/rendered_pdfs/cuenta_inversion_2024_bienes_uso-158.png`.

## Respaldo y trazabilidad

`source_manifest.csv` enumera cada fuente guardada con URL, fecha de recuperación, tamaño y SHA-256. Los originales se conservan en `sources/`; los archivos de `derived/` se regeneran con los scripts de este directorio.

La matriz `gap_resolution_matrix.csv` separa lo cerrado, lo parcialmente cerrado y lo que sigue sin identificación pública.
