# Dólares, reservas y sector externo — análisis empírico

**Fecha de corte:** 31 de agosto de 2026  
**Últimos datos efectivos:** reservas, 26/08/2026; ITCRM y tipo de cambio mayorista, 28/08/2026; inflación, julio de 2026; balanza de pagos, I trimestre de 2026; comercio de bienes, enero-julio de 2026.  
**Alcance:** ítems 6-11 de la épica y piezas verificables de 30-35. No se editó el dashboard ni ningún archivo preexistente.

## Resultado ejecutivo

1. **USD 50.784 millones es el stock bruto, no poder de fuego libre.** En fechas cercanas se identifican aproximadamente USD 34.831 millones entre cuentas en moneda extranjera de entidades en el BCRA, depósitos del Gobierno, letras del BCRA en moneda extranjera, el REPO internacional y el tramo activado del swap con China. Equivalen al **68,59%** de las reservas brutas, pero **no se restan para fabricar una cifra de reservas netas**: las fechas, reglas de valuación, vencimientos, activos de contrapartida y posibles afectaciones no están publicados en una plantilla sincronizada.

2. **Comprar dólares y acumular reservas no son la misma operación.** En julio el BCRA compró USD 2.163 millones, pero pagó USD 4.476 millones de capital e intereses de títulos públicos. Las reservas igualmente subieron USD 2.729 millones porque también entraron fondos de organismos internacionales, nuevas emisiones, depósitos bancarios y valuación. Los ingresos clasificados aquí como financiamiento o saldos de terceros sumaron USD 4.991 millones, **183% del aumento bruto observado**.

3. **El superávit de bienes no eliminó la restricción externa.** En el I trimestre de 2026, bienes aportó USD 6.339 millones, pero servicios restó USD 4.028 millones e ingreso primario restó USD 4.676 millones. Con ingreso secundario de USD 714 millones, la cuenta corriente cerró en **déficit de USD 1.651 millones**. El superávit de bienes cubrió sólo 72,8% del drenaje conjunto de servicios e ingreso primario.

4. **El peso está en una zona históricamente apreciada según el ITCRM, pero eso no determina un “dólar de equilibrio”.** El ITCRM fue **85,77** el 28/08/2026 —base 17/12/2015=100—, percentil **24,25** de la historia diaria desde 1997. Está 23,2% debajo del promedio 2008-2017 y 21,3% debajo del promedio 2018-2023, pero 12,6% por encima del promedio 1997-2001. Comercio, productividad, reservas utilizables y términos del intercambio deben leerse junto al índice.

5. **El pass-through existe, tiene rezagos y cambia de régimen; no es una identidad.** Para 2018-2026 la correlación contemporánea entre depreciación mensual del mayorista e IPC fue 0,517 y a un mes 0,466. El OLS distribuido sin controles arroja una suma de coeficientes 0-3 meses de 0,610 para toda la muestra, pero va de 0,145 en 2018-2019 a 0,701 en diciembre de 2023-marzo de 2025 y -0,156 en abril de 2025-julio de 2026. El último resultado usa apenas 16 observaciones y **no demuestra pass-through negativo**; demuestra inestabilidad y falta de identificación causal. Hay contraejemplos directos: en abril de 2025 el mayorista subió 8,74% mientras la inflación bajó de 3,7% a 2,8%; en junio de 2026 subió 5,03% mientras la inflación bajó de 2,1% a 1,9%.

## 1. Reservas: bruto observado y claims identificables

La API del BCRA informa **reservas internacionales brutas por USD 50.784 millones al 26/08/2026**. El siguiente puente organiza stocks identificables, no una metodología oficial de neteo:

| Stock / claim | USD millones | Fecha | Tratamiento |
|---|---:|---|---|
| Reservas internacionales brutas | 50.784 | 26/08/2026 | Stock oficial |
| Cuenta corriente ME de entidades en BCRA | 16.133 | 26/08/2026 | Encajes/depósitos privados aproximados |
| Depósitos del Gobierno en ME en BCRA | 2.809 | 26/08/2026 | Fondos del Tesoro aproximados |
| Letras emitidas por BCRA en ME | 4.890 | 26/08/2026 | Pasivo en moneda extranjera aproximado |
| REPO con bancos internacionales | 6.000 | 03/07/2026 | Financiamiento garantizado, vence en septiembre de 2028 |
| Tramo activado del swap PBoC | 5.000 | 05/08/2026 | Swap activado; el acuerdo total es RMB 130.000 millones |

Los tres rubros diarios publicados en pesos se convirtieron al tipo de cambio mayorista del 26/08/2026. Esa conversión es una aproximación de comparabilidad, no la cotización contable oficial de cada contrato. El REPO y el swap se toman de comunicados del BCRA y se mantienen como memo items.

### Las cuatro etiquetas pedidas, con precisión compatible con las fuentes

| Concepto | Resultado al corte | Por qué |
|---|---|---|
| Brutas | **USD 50.784 M** | Serie diaria oficial BCRA |
| Netas | **s/d oficial reproducible** | Falta un criterio único y una plantilla sincronizada de todos los pasivos/activos de reserva |
| Líquidas | **s/d** | Falta apertura corriente de oro, DEG, títulos, depósitos, activos gravados y plazos de realización |
| Propias/libres | **s/d** | Falta identificar simultáneamente propiedad, disponibilidad jurídica, colateral y vencimientos |

Como cobertura mecánica, las brutas equivalen a **8,4 meses** del promedio mensual de importaciones de bienes de enero-julio de 2026 (`50.784 / (42.286 / 7)`). No es una medida de suficiencia líquida: usa importaciones devengadas de bienes y un numerador bruto que incluye claims de terceros y financiamiento.

**Qué muestran los datos:** el titular bruto convive con pasivos y saldos afectados de magnitud material.  
**Qué no muestran:** cuánto puede vender inmediatamente el BCRA sin afectar encajes, garantías, swaps o vencimientos.  
**Lectura compatible con los datos:** el poder de fuego disponible bajo condiciones específicas es menor que el stock bruto.
**Dato necesario:** planilla oficial de reservas y liquidez en moneda extranjera, con todos los componentes a igual fecha.

## 2. Anatomía de julio: stock versus flujo

Las reservas pasaron de USD 44.870 millones al inicio implícito de julio a USD 47.599 millones al cierre: **+USD 2.729 millones**.

| Componente publicado | USD millones |
|---|---:|
| Compras de moneda extranjera del BCRA | +2.163 |
| Capital e intereses de organismos internacionales | +2.621 |
| Nuevas emisiones de títulos del Gobierno | +1.063 |
| Aumento de tenencias ME de entidades en BCRA | +1.307 |
| Valuación de activos de reserva | +110 |
| Pagos de capital e intereses de títulos públicos | -4.476 |
| Ventas ME del Tesoro | -146 |
| Pagos netos SML | -67 |
| Residual de conciliación | +154 |
| **Variación bruta observada** | **+2.729** |

El residual no se oculta: el resumen ejecutivo del BCRA enumera los principales factores, no un ledger exhaustivo. Las compras del BCRA fueron **USD 2.313 millones menores** que los pagos de títulos. A la vez, organismos, emisiones y depósitos de entidades aportaron USD 4.991 millones. Por eso una compra positiva no permite anticipar el signo de la variación de reservas.

La métrica “orgánica versus financiada” queda operacionalizada así:

- **Compra de mercado:** compras BCRA.
- **Financiamiento oficial/mercado:** organismos internacionales + emisiones del Gobierno.
- **Saldos de terceros:** aumento de tenencias de entidades.
- **No transaccional:** valuación.
- **Usos:** deuda, ventas del Tesoro y SML.

No se llama “orgánico” a todo lo que no sea deuda: las compras pueden provenir de liquidaciones estacionales o regulación, y los depósitos bancarios no son reservas propias.

## 3. Sector externo: comercio, servicios e ingresos

### Cuenta corriente, I trimestre de 2026

La identidad MBP6 cierra exactamente:

`6.339 - 4.028 - 4.676 + 714 = -1.651 millones de USD`

| Cuenta | USD millones |
|---|---:|
| Bienes | +6.339 |
| Servicios | -4.028 |
| Ingreso primario | -4.676 |
| Ingreso secundario | +714 |
| **Cuenta corriente** | **-1.651** |

Los datos muestran los límites de equiparar “superávit comercial” con “superávit externo”. Los intereses, utilidades/dividendos y otras rentas están en ingreso primario; turismo y otros servicios, en servicios. El informe de INDEC no permite aislar aquí dividendos de intereses sólo con el resumen, por lo que no se inventa esa separación.

### Comercio enero-julio de 2026

INDEC informó exportaciones de bienes por USD 58.365 millones, importaciones por USD 42.286 millones y saldo de USD 16.080 millones. La resta de totales redondeados da USD 16.079 millones; la diferencia de USD 1 millón es redondeo oficial.

Una proxy amplia de energía —exportaciones de combustibles y energía menos importaciones de combustibles y lubricantes— da **USD 6.853 millones**, 42,62% del saldo comercial. Es una aproximación porque las dos categorías no tienen universo NCM perfectamente simétrico.

No se compara el superávit enero-julio con la cuenta corriente del I trimestre como si fueran la misma ventana. La balanza de pagos del II trimestre aún es el dato faltante para extender el puente.

### Turismo: tres universos distintos

- ETI 2025, pasos relevados: USD 3.110,0 millones receptivos menos USD 7.164,2 millones emisivos = **-USD 4.054,2 millones**.
- Balance cambiario, marzo de 2026: “Viajes y Pasajes” = **-USD 393 millones**.
- El BCRA indicó que aproximadamente 70% de los egresos de marzo fue cancelado con fondos propios. Por eso gasto turístico externo no equivale uno a uno a venta de reservas.

ETI mide gasto bajo su cobertura; balance cambiario registra caja; balanza de pagos registra devengado. No se suman entre sí.

## 4. Tipo de cambio real: semáforo, no precio de equilibrio

El ITCRM del BCRA sube cuando hay depreciación real y baja cuando hay apreciación real. El último dato, 85,77, se compara así con la misma serie diaria:

| Ventana | ITCRM medio | Último vs. media |
|---|---:|---:|
| 1997-2001 | 76,21 | +12,6% |
| 2002-2007 | 161,05 | -46,7% |
| 2008-2017 | 111,65 | -23,2% |
| 2018-2023 | 108,97 | -21,3% |
| 2024-28/08/2026 | 90,81 | -5,6% |

**Semáforo:**

- Rojo/amarillo: ITCRM en el cuarto inferior de la historia y cuenta corriente deficitaria en el I trimestre.
- Verde parcial: fuerte superávit comercial de bienes y aporte amplio de energía.
- Sin dato suficiente: reservas utilizables, productividad relativa, salarios unitarios, términos del intercambio futuros y elasticidades de comercio.

Conclusión: hay evidencia de apreciación real relativa a varios comparadores, pero no base para publicar un único “dólar justo”.

## 5. Dólar, dinero e inflación

### Método

- Tipo de cambio: último dato hábil mensual del mayorista BCRA; variación logarítmica mensual.
- Dinero: base monetaria y M2 privado al último dato hábil mensual; variación logarítmica.
- Inflación: variación mensual informada por la API del BCRA.
- Ventana: enero de 2018-julio de 2026. El OLS con cuatro rezagos efectivos comienza en abril de 2018.
- Regresión: `IPC_t = a + b0·ΔTC_t + b1·ΔTC_t-1 + b2·ΔTC_t-2 + b3·ΔTC_t-3 + error_t`.

### Resultados descriptivos

| Ventana/régimen | n | Suma b0…b3 | R² |
|---|---:|---:|---:|
| 2018-2026 | 100 | 0,610 | 0,644 |
| 2018-2019 | 21 | 0,145 | 0,536 |
| 2020-noviembre 2023 | 47 | 0,966 | 0,756 |
| Diciembre 2023-marzo 2025 | 16 | 0,701 | 0,953 |
| Abril 2025-julio 2026 | 16 | -0,156 | 0,555 |

La suma se interpreta como puntos porcentuales de IPC asociados en la regresión a 1% de depreciación distribuida en 0-3 meses. Es una asociación condicional al propio modelo, sin errores robustos ni controles.

Las correlaciones simples máximas con IPC fueron 0,517 para el TC contemporáneo, 0,215 para base monetaria y 0,380 para M2 privado. No existe traducción 1:1 entre dinero, dólar e inflación en estas series.

**Qué muestran:** co-movimiento, rezago e inestabilidad entre ventanas.  
**Qué no muestran:** causalidad ni un coeficiente estructural para simular política.  
**Lectura compatible con los datos:** el pass-through varía con el régimen, las expectativas, la actividad y la composición del IPC.
**Dato/método necesario:** núcleo, regulados, alimentos, REM, actividad y salarios; local projections/VAR con identificación y errores robustos.

## 6. Deuda y apoyo externo: piezas verificables, no auditor completo

Tres piezas afectan la lectura de reservas:

- REPO BCRA por USD 6.000 millones, refinanciado hasta septiembre de 2028, a SOFR + 4%, con BONAR de la cartera del BCRA como respaldo.
- Swap PBoC por RMB 130.000 millones; tramo activado informado de RMB 35.000 millones, equivalente a USD 5.000 millones.
- Julio de 2026: USD 2.621 millones de organismos internacionales y USD 1.063 millones de nuevas emisiones del Gobierno entraron al puente de reservas.

Esto demuestra que financiamiento nuevo y aumento de reservas pueden coexistir. No alcanza para responder si “la deuda bajó”: falta consolidar Tesoro+BCRA, separar intra-sector público, residencia, moneda, valuación, activos neteables y amortizaciones.

No se construyó el muro 2027-2031 ni la comparación 2018-2026 completa. Publicarlos con los datos disponibles habría mezclado vencimientos contractuales no inventariados con stocks de distinta cobertura.

## Brechas y prioridad de próxima iteración

La matriz completa está en `gaps_matrix.csv`. Las tres brechas críticas son:

1. Plantilla oficial sincronizada para pasar de brutas a netas/líquidas/propias.
2. Balanza de pagos del II trimestre de 2026 para comparar ventanas homogéneas con comercio.
3. Base contractual consolidada Tesoro+BCRA para vencimientos 2027-2031.

Los ítems 8, 30-33 y 35 permanecen parciales o abiertos. Eso es un resultado del análisis, no un cero: la evidencia pública obtenida no permite cerrarlos sin una precisión que las fuentes no respaldan.

## Reproducción y controles

Desde la raíz del repositorio:

```powershell
python research\epica_dashito_2026\dolares_externo\build_analysis.py
python research\epica_dashito_2026\dolares_externo\verify_analysis.py
```

Requiere Python 3 y acceso a la API pública del BCRA; usa únicamente la biblioteca estándar. El XLSX oficial de ITCRM se preserva localmente como `source_bcra_itcrm.xlsx`. El constructor vuelve a descargar las series de la API, genera los CSV y ejecuta seis pruebas.

Resultado al corte: **6/6 controles aprobados**:

- identidad exacta de cuenta corriente;
- conciliación exacta del flujo de reservas de julio con residual explícito;
- diferencia de redondeo comercial dentro de USD 1 millón;
- fechas de reservas e ITCRM no posteriores al corte;
- ninguna cifra etiquetada como reserva neta/líquida oficial.

## Archivos de evidencia

- `evidence_sources.csv`: fuentes primarias, URL, fecha y cautela.
- `bcra_api_raw.csv`: extracción larga de la API con URL por observación.
- `reserve_claims_audit.csv`: stock bruto y claims identificables.
- `reserve_flow_july_2026.csv`: anatomía y residual de julio.
- `bop_bridge_q1_2026.csv`: puente MBP6.
- `trade_tourism_evidence.csv`: comercio, energía proxy y turismo.
- `itcrm_daily.csv` e `itcrm_benchmarks.csv`: serie y comparadores reales.
- `monthly_money_fx_ipc_panel.csv`, `lag_correlations.csv`, `pass_through_distributed_ols.csv` y `counterexamples_fx_up_inflation_down.csv`: pass-through reproducible.
- `gaps_matrix.csv`: qué falta y por qué importa.
- `qa_results.json`: pruebas y métricas derivadas.
- `verify_analysis.py`: verificación offline de identidades, cobertura y consistencia informe/CSV.

## Fuentes primarias principales

- [API de estadísticas monetarias del BCRA](https://api.bcra.gob.ar/estadisticas/v4.0/monetarias)
- [Documentación API BCRA v4](https://www.bcra.gob.ar/archivos/Catalogo/Content/files/pdf/principales-variables-v4.pdf)
- [ITCRM BCRA](https://www.bcra.gob.ar/indices-de-tipo-de-cambio-multilateral/)
- [Balance cambiario BCRA, julio de 2026](https://www.bcra.gob.ar/publicaciones/informe-de-evolucion-del-mercado-de-cambios-y-balance-cambiario-julio-de-2026/)
- [REPO BCRA 2026](https://www.bcra.gob.ar/noticias/bcra-repo-renovacion-total-hasta-2028/)
- [Swap BCRA-PBoC 2026](https://www.bcra.gob.ar/noticias/el-banco-central-de-la-republica-argentina-y-el-banco-de-la-republica-popular-de-china-renuevan-su-acuerdo-de-swap-y-extienden-el-plazo-de-3-a-5-anos/)
- [INDEC, cuentas internacionales I trimestre de 2026](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-35-45)
- [INDEC, comercio de bienes julio de 2026](https://www.indec.gob.ar/ftp/ica_digital/ica_d_08_26E158B1D119/)
- [INDEC, turismo internacional 2025](https://www.indec.gob.ar/uploads/informesdeprensa/eti_01_26212234D387.pdf)
