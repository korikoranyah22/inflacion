# Auditoría — ¿Qué explica la mora? Pobreza, desempleo, ingreso, crédito y originación

**Corte:** 25-08-2026  
**Base del dashboard:** `index_matchup_credito_mora_deudores_en_tasas.html`  
**Objetivo:** ejecutar de forma adversarial la hipótesis de que el salto de mora desde 2024 responde a capacidad de pago, expansión/originación del crédito o una interacción entre ambas.

## 1. Regla metodológica principal

No se acepta como inferencia causal la frase “la pobreza/desocupación bajó mientras la mora subió, por lo tanto el deterioro económico no importa”. Los denominadores no coinciden:

- pobreza: personas/hogares;
- desempleo: PEA;
- mora: personas que accedieron al crédito o saldos de crédito.

Además, el shock de ingreso, la toma/refinanciación de crédito y el default pueden aparecer separados por meses.

## 2. Corrección de una etiqueta previa

En el tab **Del shock a la mora**, `ratesMoneyRows.monto_personales` se estaba presentando como “stock real”. Eso era incorrecto para esta construcción: el bloque monetario usa el **capital de préstamos personales operado/desembolsado en el mes**, reexpresado a pesos de julio de 2026. Se corrigieron:

- título del small multiple;
- hover;
- selector del laboratorio de rezagos;
- nota APB;
- texto de auditoría interno.

El flujo mensual no identifica destino del crédito y no equivale al stock de cartera.

## 3. Secuencia documentada

### Ingreso / capacidad

El índice real de **Total salarios** del dashboard, nov-2023=100, cae hasta aproximadamente **83,3 en marzo de 2024**. Posteriormente recupera, mientras la mora continúa aumentando. Esto es compatible con un shock inicial con rezagos, pero refuta una explicación lineal simple basada sólo en el nivel contemporáneo del salario agregado.

### Expansión del crédito

BCRA, Informe Monetario Mensual diciembre 2024:

- crédito al consumo: **+70,2% real** durante 2024 vs dic-2023;
- préstamos personales: **+144,1% real interanual**;
- tarjetas: **+40,9% real**.

Fuente: https://www.bcra.gob.ar/publicaciones/informe-monetario-mensual-diciembre-2024/

BCRA, Inclusión Financiera 1S-2025:

- **19,5 millones** de personas con financiamiento en el sistema ampliado a jun-2025;
- **+1 millón neto** de deudores vs dic-2024;
- saldo promedio por deudor **+19% real** en el semestre;
- personas en situación regular: **86,5%**, caída de **2,5 pp** vs dic-2024;
- deterioro mayor en PNFC (**−4 pp**) que en EEFF (**−2 pp**).

Fuente: https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-primer-semestre-2025/

### Mora

BCRA:

- hogares, dic-2024: **2,5%**;
- hogares, nov-2025: **8,8%**;
- hogares, may/jun-2026: **12,8%**.

Fuentes:
- https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-diciembre-2024/
- https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-noviembre-2025/
- https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-junio-de-2026/

PNFC, feb-2026:

- irregularidad total: **26,9%**;
- personales: **34,1%**;
- tarjetas: **19,4%**;
- cartera Fintech: **+47% real interanual**.

Fuente: https://www.bcra.gob.ar/publicaciones/informe-de-proveedores-no-financieros-de-credito-junio-de-2026/

## 4. Oferta / originación

La Encuesta de Condiciones Crediticias (ECC) es **cualitativa**, agregada y cubre entidades bancarias participantes; no es una base de scores individuales.

Secuencia utilizada:

- **1T-2024:** sesgo restrictivo en estándares para familias.
- **2T-2024:** flexibilización de montos máximos en casi todas las líneas a hogares y aumento de demanda.
- **3T-2024:** montos máximos se flexibilizan en todas las líneas; spreads bajan en tarjetas y otros créditos al consumo.
- **2T-2025:** montos máximos vuelven a flexibilizarse en casi todas las líneas; simultáneamente aparecen restricciones en algunos spreads/comisiones.
- **3T–4T-2025:** giro restrictivo de estándares a familias.

Fuentes:
- https://www.bcra.gob.ar/encuesta-condiciones-crediticias-ecc/
- https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/0624-ECC_%20Resultados.pdf
- https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/0924-ECC_Resultados.pdf
- https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/0225-ECC_%20Resultados.pdf

Interpretación permitida: hubo una fase de expansión acompañada por flexibilización parcial de términos/condiciones y luego un endurecimiento.  
Interpretación **no** permitida: demostrar “mala originación” individual sin cohortes, score, cuota/ingreso y default posterior.

## 5. Pobreza y desempleo

Últimos datos oficiales integrados al corte:

- pobreza 2S-2025: **28,2% de las personas**;
- desempleo 1T-2026: **7,8% de la PEA**;
- subocupación 1T-2026: **11,1%**.

Fuentes:
- https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-46-152
- https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-58

### Correlación pobreza ↔ mora bancaria personales + tarjetas

Promedios semestrales 2022-I → 2025-II, n=8:

| Período | Pobreza % | Mora P+T % |
|---|---:|---:|
| 2022-I | 36,5 | 3,577 |
| 2022-II | 39,2 | 2,869 |
| 2023-I | 40,1 | 3,038 |
| 2023-II | 41,7 | 2,710 |
| 2024-I | 52,9 | 2,602 |
| 2024-II | 38,1 | 2,523 |
| 2025-I | 31,6 | 3,895 |
| 2025-II | 28,2 | 8,541 |

**Pearson contemporáneo: r ≈ −0,689, n=8.**

Esto describe una divergencia agregada. No puede interpretarse como “menos pobreza causa más mora” ni como prueba de que el ingreso de los deudores sea irrelevante. Con tan pocos semestres, los resultados por rezago son extremadamente inestables.

### Correlación desempleo ↔ mora bancaria personales + tarjetas

Promedios trimestrales 2022-1T → 2026-1T, n=17:

**Pearson contemporáneo: r ≈ +0,385, n=17.**

No es una relación fuerte, pero tampoco es “cero”. Además, desempleo no captura caída salarial, informalidad, volatilidad de ingresos ni carga financiera entre personas ocupadas.

## 6. Rezagos mensuales exploratorios

Objetivo: mora bancaria de personales + tarjetas.  
Ventana base para tasa: 2022→may-2026.  
El flujo real de personales sólo está disponible en esta construcción desde dic-2023.

| Variable adelantada a la mora | lag 0 | lag 1 | lag 3 | lag 6 | lag 9 | lag 12 |
|---|---:|---:|---:|---:|---:|---:|
| Tasa real bancaria | 0,429 | 0,451 | 0,517 | 0,605 | **0,614** | 0,577 |
| Tasa real Fintech observada | 0,481 | 0,506 | 0,545 | **0,574** | 0,523 | 0,490 |
| Salario real · nivel | −0,302 | −0,272 | −0,171 | 0,019 | 0,169 | 0,253 |
| Flujo real personales | −0,200 | −0,133 | −0,047 | 0,200 | 0,587 | **0,845** |

Para el máximo del flujo a 12 meses: **n=18**. Se probaron varios rezagos, por lo que el valor es sugerente pero especialmente vulnerable a selección ex post / muestra corta.

## 7. Auditoría de regresión

Modelo exploratorio:

`mora_t = f(salario_real_(t-k), tasa_real_(t-k), log(flujo_personales_(t-k)))`

R² por rezago común:

| Rezago | Niveles | Primeras diferencias |
|---:|---:|---:|
| 0 | 0,395 | 0,213 |
| 3 | 0,433 | 0,328 |
| 6 | 0,482 | **0,348** |
| 9 | 0,461 | 0,271 |
| 12 | **0,678** | 0,122 |

La gran mejora aparente en niveles a 12 meses no sobrevive al pasar a primeras diferencias. Esto es una alerta de tendencia/fase común y multicolinealidad. Los modelos se usan sólo para pesar hipótesis, no para afirmar causalidad.

## 8. Grado de evidencia

| Afirmación | Veredicto |
|---|---|
| “La pobreza no explica la mora.” | **No respaldada como descarte causal** |
| “El desempleo no explica la mora.” | **Débil / no respaldada** |
| “La caída del poder adquisitivo explica la mora.” | **Compatible con los datos pero no demostrada** |
| “La expansión del crédito explica la mora.” | **Bastante respaldada como mecanismo contribuyente** |
| “La mala originación explica la mora.” | **Compatible con los datos pero no demostrada** |
| “Fintech/no bancarios son responsables principales.” | **No puede determinarse** |
| “Los bancos son responsables principales.” | **No puede determinarse** |
| “La causa fue prestar a gente que no debía recibir crédito.” | **No respaldada / no determinable con datos públicos** |
| H6 — interacción capacidad + crédito + precio + selección | **Síntesis más respaldada, sin descomposición causal** |

## 9. Datos faltantes

Para separar causalmente capacidad de pago de originación faltan, idealmente a nivel de deudor/cohorte y anonimizados:

- ingreso individual;
- cuota/ingreso y deuda/ingreso;
- fecha de originación;
- score / reglas vigentes al otorgamiento;
- historial laboral y tipo de empleo;
- refinanciaciones;
- evolución individual de saldos;
- default por cohorte y producto.

No se sustituyen con inferencias narrativas.

## 10. Veredicto final

> Los datos no justifican usar la divergencia entre pobreza o desempleo agregados y mora como evidencia de que el deterioro económico fue irrelevante. La secuencia 2024–2026 es compatible con una interacción: un shock fuerte sobre ingresos y capacidad de compra, seguido por una expansión extraordinaria del crédito —con flexibilización parcial de condiciones de otorgamiento— y, con rezago, un marcado deterioro de la regularidad y la mora. La expansión/originación parece haber contribuido, pero con datos públicos no puede separarse causalmente de la capacidad de pago ni asignarse una responsabilidad principal a bancos o fintech.

## 11. QA técnico

- nuevo tab: `tab-mora-causal`;
- 37 botones / 37 paneles, sin destinos rotos;
- 0 IDs HTML duplicados;
- 16 scripts inline pasan `node --check`;
- gráfico de rezagos: datos embebidos derivados del dashboard;
- scatter pobreza y desempleo: denominadores explicitados;
- ninguna correlación se etiqueta como causal.
