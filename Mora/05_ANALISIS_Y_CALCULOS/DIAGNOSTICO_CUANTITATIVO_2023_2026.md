# Diagnóstico cuantitativo del endeudamiento y la mora, 2023–2026

## Resultado central

La evidencia oficial muestra un deterioro extraordinario de la capacidad de pago de los hogares, con especial intensidad en préstamos personales y crédito no bancario. Esto justifica una intervención preventiva y de reestructuración. No demuestra, por sí solo, que toda tasa individual sea abusiva ni que el costo del crédito sea la única causa de la mora.

| Indicador | Inicio comparable | Último dato | Variación |
|---|---:|---:|---:|
| Mora bancaria de hogares, % del saldo | 2,70 % (nov. 2023) | 12,80 % (may. 2026) | +10,10 puntos; 4,75 veces |
| Mora bancaria en personales + tarjetas, % del saldo | 2,39 % (nov. 2023) | 14,52 % (may. 2026) | +12,13 puntos; 6,07 veces |
| Mora PNFC total mayor a 90 días, % del saldo | 10,8 % (nov. 2023) | 26,9 % (feb. 2026) | +16,1 puntos; 2,49 veces |
| Mora PNFC en préstamos personales, % del saldo | 21,8 % (nov. 2023) | 34,1 % (feb. 2026) | +12,3 puntos |
| Personas con préstamos personales, % de población adulta dentro del tramo metodológico vigente | 23,10 % (jul. 2024) | 32,20 % (dic. 2025) | +9,09 puntos |

Fuentes locales: [morosidad_hogares.csv](datos/morosidad_hogares.csv), [morosidad_pnfc.csv](datos/morosidad_pnfc.csv), [bcra_inclusion_prestamos_personales_2023_2025.csv](datos/bcra_inclusion_prestamos_personales_2023_2025.csv).

## 1. Qué mide cada número

- La mora bancaria de hogares es cartera irregular dividida por financiaciones a familias. Mide **saldo**, no cantidad de personas.
- La mora PNFC es cartera con atraso mayor a noventa días dividida por el saldo de esa categoría. También mide **saldo**, pero corresponde a otro universo y no debe compararse como si fuera idéntico al bancario.
- La cobertura de préstamos personales mide personas informadas sobre población adulta. Desde julio de 2024 la Central de Deudores elevó el umbral reportable de $1.000 a $25.000; por eso junio y julio de 2024 no son comparables entre sí.
- “Stock irregular” no equivale a “nuevos morosos”: cambia por pagos, nuevas originaciones, refinanciaciones, castigos, ventas y reclasificaciones.

Estas precauciones están desarrolladas en [AUDITORIA_MOROSIDAD.md](AUDITORIA_MOROSIDAD.md). Los once controles automáticos disponibles tienen estado `PASS` en [TESTS_MOROSIDAD.json](TESTS_MOROSIDAD.json).

## 2. Trayectoria bancaria

La serie mensual muestra tres etapas:

1. Noviembre de 2023: mora de hogares de 2,70 % y de personales + tarjetas de 2,39 %.
2. Diciembre de 2024: todavía 2,55 % para hogares y 2,50 % para personales + tarjetas.
3. Aceleración durante 2025 y 2026: 9,33 % y 10,57 % en diciembre de 2025; 12,80 % y 14,52 % en mayo de 2026.

El promedio pre-shock de la serie de hogares es 3,38 %. Mayo de 2026 se ubicó 9,42 puntos por encima. La suma de excesos mensuales respecto de ese promedio, comparada en ventanas de treinta meses, fue 53,71 puntos-por-mes más desfavorable en diciembre de 2023–mayo de 2026 que en su ventana espejo.

El informe oficial del BCRA de mayo de 2026 confirma una mora de 12,8 % en familias y 7,7 % en el sector privado total. También informa previsiones equivalentes a 86,3 % de la cartera irregular, capital regulatorio de 30,7 % de los activos ponderados por riesgo, irregularidad neta de previsiones equivalente a 2,2 % de la responsabilidad patrimonial computable y ROA de doce meses de 1,1 %.

La lectura conjunta es importante: existe un problema severo para los hogares, pero el agregado financiero conserva capacidad de absorción. Esa capacidad sistémica no prueba rentabilidad, abuso ni responsabilidad de cada entidad o contrato; sí reduce el argumento de que toda reestructuración razonable sea incompatible con la estabilidad.

## 3. Proveedores no financieros y fintech

El informe del BCRA publicado en junio de 2026 muestra, para febrero:

- $13,9 billones de saldo PNFC;
- alrededor de 12,1 millones de personas financiadas;
- más de 7 millones de clientes fintech;
- tasa nominal anual promedio de 144 % en préstamos personales OPNFC y 87 % en tarjetas de emisoras no bancarias;
- 26,9 % de irregularidad total;
- 34,1 % en préstamos personales y 19,4 % en tarjetas; y
- deudores PNFC equivalentes al 85 % de las personas deudoras del sistema financiero, aunque con saldo equivalente al 18 % de la deuda bancaria de personas humanas.

La extensión de personas y la severidad de la mora hacen indispensable una cobertura universal. Una ley limitada a bancos o tarjetas dejaría fuera una porción central del problema.

## 4. Costo real del crédito

La serie construida con tasas oficiales de préstamos personales y una aproximación conservadora del costo total arroja:

| Año | Inflación interanual promedio | TEA calculada promedio | Tasa real TEA promedio | CFTEA aproximado promedio | Tasa real CFTEA aproximada |
|---|---:|---:|---:|---:|---:|
| 2023 | 127,95 % | 171,05 % | 18,33 % | 231,97 % | 44,33 % |
| 2024 | 236,80 % | 136,32 % | −29,22 % | 183,02 % | −15,60 % |
| 2025 | 44,47 % | 104,18 % | 43,27 % | 136,02 % | 65,69 % |
| 2026, ene.–jul. | 33,00 % | 93,58 % | 45,56 % | 121,39 % | 66,47 % |

La tasa real se calcula como:

`r_real = ((1 + tasa_nominal_efectiva) / (1 + inflación_12m)) - 1`

El CFTEA es una aproximación auditada, no el precio efectivo de todos los contratos. El cambio decisivo es temporal: en 2024 la inflación licuó el costo real promedio; al desacelerar los precios durante 2025–2026, tasas nominales todavía altas se convirtieron en costos reales fuertemente positivos.

En la exploración mensual, la correlación máxima entre tasa real de personales y mora bancaria de personales + tarjetas es `r = 0,488` con seis meses de rezago y 83 observaciones. Es una asociación temporal moderada, no una prueba causal. Ingreso real, desempleo, servicios, composición de cartera, originación, refinanciaciones y regulación también importan.

Fuentes: [costo_credito_personal_resumen_anual_2023_2026.csv](datos/costo_credito_personal_resumen_anual_2023_2026.csv) y [costo_credito_personal_historia_2023_2026.csv](datos/costo_credito_personal_historia_2023_2026.csv).

## 5. Rentabilidad y responsabilidad

El agregado oficial del sistema financiero exhibe ROA positivo en los cortes revisados: 5,42 % en diciembre de 2023, 4,10 % en diciembre de 2024, 1,02 % en diciembre de 2025 y 1,1 % en los doce meses a mayo de 2026 según el informe mensual.

Esto no autoriza a atribuir la ganancia neta del sistema a préstamos personales ni a identificar qué entidad obtuvo rentas de una persona deudora. Los estados agregados no separan el margen causal de esa línea. La conclusión jurídicamente sostenible es más acotada:

1. el sistema agregado permaneció rentable y capitalizado mientras la mora de hogares escaló;
2. los proveedores profesionales fijan precio, evalúan riesgo, provisionan y controlan la originación;
3. por eso deben internalizar las consecuencias de una evaluación irresponsable o de cargos ilegales; y
4. el Estado no necesita comprar cartera privada para crear un procedimiento de reestructuración y segunda oportunidad.

Fuente: [bcra_sistema_financiero_2023_2026.csv](datos/bcra_sistema_financiero_2023_2026.csv).

## 6. Traducción de la evidencia al diseño legal

| Evidencia | Respuesta normativa |
|---|---|
| Mora bancaria de hogares multiplicada por 4,75 desde nov. 2023 | régimen transitorio para deudas originadas o agravadas desde 2023 |
| Personales + tarjetas llegan a 14,52 % | pago máximo según ingreso y mínimo vital; eliminación de punitorios; salida judicial |
| Mora PNFC de 26,9 % y 34,1 % en personales | cobertura obligatoria de PNFC, fintech, PSP, cesionarios y cobradores |
| Tasas reales muy positivas en 2025–2026 | información de CFTEA, referencia por mercado y tope relativo verificable |
| Asociación tasa real–mora, no causalidad probada | sanción individual graduada por prueba y relación causal; no quita automática de capital |
| Solvencia agregada preservada | reestructuración privada sin compra pública de deudas |
| Quiebre estadístico de julio de 2024 | obligación de publicar metodología, revisiones y rupturas de comparabilidad |

## 7. Qué datos faltan

Todavía no hay una serie pública mensual y homogénea que combine, por hogar:

- ingreso neto, gastos esenciales y servicio total de deuda;
- CFTEA contractual efectivo por proveedor y producto;
- atrasos de 1–30, 31–60, 61–90 y más de 90 días para todo el universo;
- refinanciaciones, curas, ventas, castigos y cobros;
- deuda simultánea bancaria, PNFC, fintech, servicios y alquiler; y
- causas del incumplimiento con diseño que permita inferencia causal.

Por eso el proyecto crea un tablero abierto y obliga a publicar distribuciones de operaciones efectivamente originadas. La falta de esos datos no invalida el diagnóstico de mora; sí impide afirmar con rigor una única causa o cuantificar hoy el universo exacto de hogares elegibles.

