# Manuscrito base para una acción colectiva sobre crédito bancario de consumo

**Versión:** V0.7 — borrador forense con panel público longitudinal 2023–2026  
**Fecha de corte:** 30 de agosto de 2026  
**Período de investigación:** 1 de enero de 2023 al 30 de agosto de 2026  
**Objeto material:** préstamos personales y otras financiaciones bancarias a personas consumidoras  
**Estado:** borrador de trabajo; no apto para presentación sin completar demandantes, demandados, contratos, clase, competencia y prueba documental.

> **Advertencia de uso.** Este texto no acusa indistintamente a “todos los bancos” ni afirma que toda tasa superior a la inflación sea ilícita. Organiza, para el período iniciado el 1 de enero de 2023, una hipótesis colectiva verificable: cláusulas estandarizadas, información deficiente sobre el costo financiero total, cargos no debidos y/o intereses injustificados y desproporcionadamente superiores al costo medio para operaciones comparables. El universo histórico de investigación no equivale automáticamente al período reclamable: cada remedio y cohorte debe someterse a su regla de exigibilidad y prescripción. Debe ser revisado y firmado por un/a abogado/a matriculado/a antes de cualquier presentación.

---

## 1. Tesis y demostración integrada de la justicia del reclamo

### 1.1. Qué se reclama —y qué no se reclama

El crédito de consumo es un servicio sujeto a la Constitución Nacional, la Ley 24.240 de Defensa del Consumidor (LDC) y el Código Civil y Comercial de la Nación (CCyC), aunque el proveedor también esté regulado por el Banco Central. El precio del crédito puede ser elevado y seguir siendo lícito: la inflación, el costo de fondeo, la mora, las previsiones, los gastos, los impuestos, la liquidez y el capital regulatorio son costos que deben reconocerse cuando sean reales, atribuibles y demostrables.

El reclamo no postula que toda tasa superior a la inflación sea ilegal, que la rentabilidad bancaria sea ilícita, que el tribunal deba fijar una tasa general para la economía ni que la persona consumidora deba conservar el capital sin devolverlo. Sostiene algo más preciso:

1. el precio total debe haber sido informado antes de contratar, de forma cierta, visible y comprensible;
2. no pueden cobrarse importes no previstos, servicios no prestados o costos omitidos o mal incorporados al CFT;
3. la tasa y la capitalización pueden ser reducidas si exceden, sin justificación y desproporcionadamente, el costo medio para deudores y operaciones similares; y
4. probado el exceso, el banco conserva el capital y el costo legítimo, mientras que lo cobrado de más se imputa al capital y, una vez extinguido éste, se restituye.

La justicia del reclamo reside en esa simetría: **ni gratuidad para el deudor ni inmunidad para el proveedor**. Se exige el cumplimiento del precio informado, la explicación del precio aplicado y la devolución exclusiva de aquello que resulte jurídicamente indebido.

### 1.2. La pregunta matemática correcta: reconstruir flujos, no comparar rótulos

TNA, TEA, CFT, cuota, tasa real y ROA contestan preguntas diferentes. No deben sumarse ni intercambiarse.

- La **TNA** anualiza convencionalmente una tasa periódica, pero no incorpora por sí sola el efecto de la capitalización.
- La **TEA** mide el factor efectivo de interés durante un año bajo la periodicidad informada.
- El **CFT** incorpora, además del interés, comisiones, seguros, impuestos y demás cargos computables. El propio BCRA lo caracteriza como el indicador de cuánto se pagará realmente.
- La **tasa real** compara un factor financiero con la variación del poder adquisitivo; no representa por sí sola la suma de cuotas pagadas.
- El **ROA** mide rentabilidad contable sobre activos; no es una tasa contractual ni el margen de una cartera de préstamos personales.

Para un contrato individual, la medida correcta comienza por el dinero neto efectivamente recibido por la persona, \(D\), y todos los pagos obligatorios \(Q_t\). La tasa efectiva mensual \(i_m\) es la que iguala ambos lados:

\[
D=\sum_{t=1}^{n}\frac{Q_t}{(1+i_m)^t}
\]

Luego:

\[
CFTEA=(1+i_m)^{12}-1
\]

En \(Q_t\) deben incluirse cuota, interés, seguro, comisión, impuesto, gasto de otorgamiento y todo pago exigido para obtener o mantener el crédito. Si un cargo se retiene al desembolsar, reduce \(D\), aunque la deuda nominal se calcule sobre un capital mayor. Esta ecuación permite detectar costos invisibilizados por una TNA aparentemente idéntica.

**Ejemplo pedagógico, no contrato observado.** Si se toman $100.000 a doce meses con TNA de 65,71%, sin otros cargos y mediante cuota francesa:

\[
i_m=0{,}6571/12=0{,}0547583
\]

\[
TEA=(1+0{,}0547583)^{12}-1=89{,}5988\%
\]

La cuota teórica es:

\[
C=100\,000\times\frac{0{,}0547583}{1-(1+0{,}0547583)^{-12}}=11\,587{,}34
\]

Las doce cuotas suman $139.048,04 y el interés nominal total del flujo asciende a $39.048,04. Que la TEA sea 89,60% y la suma nominal de intereses sea 39,05% del capital **no es una contradicción**: el capital se devuelve gradualmente y la TEA expresa el rendimiento anual equivalente sobre los saldos pendientes.

Supóngase ahora que se mantienen exactamente esas cuotas y deuda nominal, pero se retienen $10.000 al desembolso por un cargo obligatorio. La persona recibe sólo $90.000. La nueva tasa se obtiene resolviendo:

\[
90\,000=\sum_{t=1}^{12}\frac{11\,587{,}34}{(1+i_m)^t}
\]

El resultado aproximado es \(i_m=7{,}42196\%\) mensual y:

\[
(1+0{,}0742196)^{12}-1=136{,}11\%
\]

El ejemplo muestra por qué el análisis jurídico debe partir del dinero neto recibido y de todos los pagos, no de la TNA impresa en forma aislada.

### 1.3. Cómo se mide la carga real —y cuál es su límite

Para comparar una TEA \(i\) con inflación interanual \(\pi\) se utiliza la relación de Fisher:

\[
r=\frac{1+i}{1+\pi}-1
\]

En julio de 2026, la TNA promedio BCRA de préstamos personales fue 65,71%, equivalente bajo capitalización mensual a una TEA de 89,5988%. La inflación interanual nacional reconstruida desde la serie INDEC fue 33,8257%. Por tanto:

\[
r=\frac{1+0{,}895988}{1+0{,}338257}-1=41{,}6759\%
\]

El resultado significa que el factor anual de interés superó en aproximadamente 41,68% al factor de precios de ese período. **No significa** que cada deudor haya transferido 41,68% real de su capital: para medir el esfuerzo efectivo deben deflactarse el desembolso y cada cuota según su fecha, considerar la amortización y vincular el servicio de la deuda con el ingreso disponible.

Para cada integrante de la clase deberán calcularse adicionalmente:

\[
Esfuerzo_t=\frac{cuotas\ totales\ del\ período_t}{ingreso\ neto\ disponible_t}
\]

y el valor real de los pagos:

\[
PagoReal_t=\frac{Q_t}{IPC_t/IPC_0}
\]

No se propone un umbral universal de esfuerzo sin prueba. La distribución por deciles, medianas y percentiles permitirá distinguir una carga general de una afectación concentrada en hogares de ingreso bajo, personas jubiladas, asalariadas o refinanciadas.

### 1.4. Cómo se prueba la desproporción económica

La inflación es un control de poder adquisitivo, pero el artículo 771 CCyC ordena otro comparador: el costo medio del dinero para deudores y operaciones similares en el lugar de contratación. Por eso, cada contrato debe ubicarse en una celda homogénea por fecha, moneda, monto, plazo, garantía, canal, perfil de riesgo, relación salarial y mora esperada.

Para cada celda se calcularán mediana, promedio ponderado, percentiles y dispersión de CFT efectivamente contratado. La distancia multiplicativa entre el contrato observado y el comparador puede expresarse como:

\[
BrechaRelativa_j=\frac{1+CFT_{observado,j}}{1+CFT_{comparable,j}}-1
\]

Esta medida es preferible a restar porcentajes muy altos porque compara factores de acumulación. La brecha no decide el caso por sí sola. Primero identifica un extremo; después el banco puede justificarlo mediante riesgo y costos atribuibles.

La explicación económica mínima de un precio de crédito debe conciliar, en importes monetarios atribuibles a la misma cohorte y período:

\[
Ingresos\ cobrados = fondeo + pérdida\ crediticia + operación + impuestos + liquidez/capital + margen
\]

La expresión es una conciliación de importes, no una suma mecánica de tasas. Cada componente debe medirse sobre bases y períodos compatibles, evitando computar dos veces mora y previsiones o confundir costo de capital con gasto realizado. El margen residual sólo puede estimarse después de conciliar cobros con contabilidad y recuperos:

\[
Margen\ neto\ atribuible = ingresos\ de\ la\ cohorte-costo\ de\ fondeo-pérdidas-gastos-impuestos-capital\ atribuible
\]

Este método protege también al banco: una tasa extrema puede resultar explicable en una cartera excepcionalmente riesgosa; una tasa menos llamativa puede ser ilícita si esconde cargos no informados. La conclusión depende de la prueba, no del adjetivo utilizado para describirla.

### 1.5. Cómo se calcula el exceso y la restitución

Una vez fijada judicialmente la tasa o costo admisible \(i_t^*\), la cuenta se reconstruye desde el origen. Para cada período:

\[
B_t^*=\max\{0,\ B_{t-1}^*(1+i_t^*)+Cargos_t^*-Pago_t\}
\]

Los intereses o cargos efectivamente cobrados por encima de los admitidos se imputan primero a reducir el saldo de capital contrafactual. Cuando ese saldo llega a cero, los pagos posteriores que carezcan de causa restitutoria forman el crédito de la persona consumidora. Esta liquidación evita dos errores: calcular daños multiplicando una tasa por un saldo sin respetar la amortización y ordenar una devolución que desconozca el capital legítimamente prestado.

Los resultados deben presentarse por persona y también agregados por cohorte, con conciliación entre:

1. capital neto entregado;
2. pagos efectivamente debitados;
3. interés y cargos contractuales;
4. cuenta contrafactual bajo el criterio judicial;
5. exceso imputado a capital;
6. restitución final, si corresponde; y
7. saldo todavía debido, si lo hubiera.

### 1.6. Por qué el reclamo es económicamente y políticamente justo

La Constitución no opone mercado y protección del consumidor. Su artículo 42 protege simultáneamente los intereses económicos, la información adecuada y veraz, la libertad de elección, el trato equitativo y la defensa de la competencia frente a distorsiones. Una elección sólo es económicamente libre cuando el precio total puede conocerse y compararse antes de obligarse.

En el crédito estandarizado existe una asimetría estructural: el banco diseña la fórmula, clasifica el riesgo, controla el flujo digital, conserva los registros y conoce su costo interno; la persona decide muchas veces bajo urgencia y sólo observa una cuota o TNA. Cuando el costo real se oculta o una misma práctica dispersa perjuicios pequeños entre miles de contratos, el litigio individual suele costar más que la reparación. La acción colectiva corrige esa falla de acceso a justicia sin presumir responsabilidad.

La dimensión política —en sentido constitucional, no partidario— consiste en impedir que una infraestructura esencial para salarios, pagos y consumo quede fuera del control de legalidad por la sola dispersión del daño. Revisar una cláusula común no equivale a administrar el sistema financiero: preserva la competencia por precio total, exige trazabilidad a una actividad profesional regulada y distribuye el costo del incumplimiento hacia quien diseñó y controló la práctica.

El remedio propuesto es proporcional:

- mantiene la obligación de devolver el capital;
- reconoce fondeo, riesgo, gastos, impuestos y margen razonable que sean acreditados;
- no utiliza la rentabilidad del sistema como presunción de abuso individual;
- elimina solamente cargos sin causa, información deficiente y excesos injustificados probados; y
- devuelve a cada persona únicamente el resultado de su liquidación.

### 1.7. Demostración jurídica: norma, hecho, prueba y consecuencia

La pretensión deberá exponerse como cuatro silogismos separados, para que ninguna debilidad contamine a los demás:

| Pretensión | Regla | Hecho que debe probarse | Consecuencia solicitada |
|---|---|---|---|
| Información | Arts. 4 y 36 LDC; arts. 1388 y 1389 CCyC; regulación BCRA | Omisión, inexactitud o presentación incomprensible de TEA, CFT, pagos, amortización o extras en una versión común | Nulidad o integración; costo omitido por no escrito; reliquidación |
| Cargos | Arts. 35 y 37 LDC; art. 1388 CCyC | Cargo no solicitado, no previsto, duplicado o sin servicio efectivo | Cese, imputación al capital y restitución |
| Intereses | Arts. 10, 770 y 771 CCyC | Tasa o capitalización desproporcionada frente a operaciones semejantes y no justificada por costos/riesgo | Reducción judicial, imputación del exceso y repetición |
| Tutela colectiva | Arts. 42 y 43 CN; arts. 52–55 LDC; doctrina de la CSJN | Contrato o práctica estandarizada, universo identificable y predominio de cuestiones comunes | Cese común y liquidación individual desde registros del banco |

La ganancia neta no es requisito para probar información omitida, cargo indebido o interés reducible. Su análisis tiene una función distinta: impedir que el banco denomine “costo” a una renta residual que no puede conciliar, medir el beneficio de una práctica declarada ilícita y controlar la razonabilidad de su justificación. Incluso una entidad con pérdida agregada puede haber aplicado una cláusula abusiva; incluso una entidad rentable puede haber cobrado correctamente una cartera.

### 1.8. Estado actual de la prueba

La información pública aporta indicios fuertes, pero todavía no reemplaza los contratos ni la pericia:

- La serie acompañada contiene **43 meses, desde enero de 2023 hasta julio de 2026**. El promedio descriptivo de las tasas reales mensuales calculadas desde la TNA fue **+18,33% en 2023**, **−29,22% en 2024**, **+43,27% en 2025** y **+45,56% entre enero y julio de 2026**. La trayectoria no es monotónica y exige analizar contratos y comparadores por cohorte.
- En julio de 2026, la TNA promedio de préstamos personales informada por el BCRA fue **65,71%**; capitalizada mensualmente equivale a una TEA aproximada de **89,60%**. Frente a una inflación interanual de **33,83%**, representa una tasa real anual de **41,68%**, antes de cargos.
- Una estimación auxiliar que incorpora IVA sobre intereses —pero no cargos contractuales— arroja **115,95%** efectivo anual y **61,36%** real. No es el CFT completo de ningún contrato.
- El BCRA informó para junio de 2023 un promedio de **321% de CFT máximo ofrecido** entre quince entidades de la muestra indicada en su Informe de Inclusión Financiera. Es una estadística de ofertas máximas, no de costos pagados.
- La información declarada al Régimen de Transparencia y preservada al 30 de agosto de 2026 contiene 505 líneas bancarias en pesos con CFTEA positivo, pertenecientes a 46 bancos según el criterio de selección expuesto en el anexo. Los valores son muy heterogéneos y los extremos deben autenticarse; no prueban cobro ni ganancia.
- La base abierta de inclusión financiera muestra que la cobertura de préstamos personales subió de **28,96% de la población adulta en enero de 2023 a 31,09% en junio de 2024**. Desde julio de 2024 el BCRA elevó de $1.000 a $25.000 el saldo mínimo reportable a la Central de Deudores; por eso el nuevo tramo comienza en 23,10% y llega a **32,20% en diciembre de 2025**, sin empalmar ambas series como si fueran homogéneas.
- Los archivos contables abiertos por entidad permiten avanzar desde el resultado total hacia el producto: contienen el saldo de préstamos personales y la cuenta específica **511107/515107 “Intereses por préstamos personales”**. En la suma de entidades, ese ingreso bruto representó 2,61% de los ingresos financieros en 2023, 4,31% en 2024 y 13,65% en 2025. Es ingreso bruto acumulado, no ganancia neta de la cartera.
- En el agregado oficial AA000, los préstamos personales pasaron de **1,95% del activo en diciembre de 2023 a 4,75% en diciembre de 2024, 6,23% en diciembre de 2025 y 6,31% en mayo de 2026**. En paralelo, la irregularidad de la cartera de consumo pasó de 2,75% a 2,51%, 9,18% y 12,58%, respectivamente. La expansión del producto y el deterioro posterior del riesgo deben explicarse juntos.
- El resultado neto estimado del agregado AA000 fue positivo en los siete cortes examinados entre septiembre de 2023 y mayo de 2026, aunque el ROA descendió desde 6,94% en junio de 2024 hasta 1,07% en mayo de 2026. En el cruce específico de 46 entidades de mayo de 2026, 32 mostraron resultado neto estimado positivo y 14 negativo. La diversidad temporal e institucional refuta la equivalencia entre tasa publicada y ganancia neta y justifica obtener contabilidad por producto.
- La irregularidad de financiaciones a familias fue **12,8%** y las previsiones equivalieron al **86,3%** de la cartera irregular. Riesgo y pérdidas deben incorporarse antes de atribuir margen.
- La regulación obliga a conservar reclamos, reintegros, denuncias, reportes directivos y auditorías. Los informes públicos 2023–2025 muestran cientos de miles de reclamos mensuales y altas proporciones informadas como resolución favorable, pero cambian de ventana y revisan universos: sirven para localizar la prueba, no como tasa de infracción. Los registros desagregados pueden demostrar patrón, conocimiento, universo y correcciones con documentos anteriores al litigio.

Por eso, la demanda más defendible no es abstracta contra la banca en general. Debe dirigirse contra entidades identificadas y formar **subclases por banco, producto, contrato tipo y cohorte temporal**. El objeto inicial y justo es obtener la documentación común, detener prácticas verificadas y liquidar sólo los excesos que resulten probados.

### 1.9. Protocolo de análisis que deberá seguir la pericia

| Etapa | Información de entrada | Operación | Resultado controlable |
|---|---|---|---|
| 1. Identificación | Banco, producto, versión y fechas | Agrupar contratos que compartan la misma cláusula o regla de cobro | Cohorte homogénea y universo contable |
| 2. Flujo individual | Desembolso, retenciones, cuotas y cargos | Ordenar todos los movimientos por fecha y signo | Flujo neto completo por contrato |
| 3. Costo efectivo | Flujo individual | Resolver la tasa interna y anualizarla | CFTEA efectivamente soportado |
| 4. Carga real | Flujo e IPC | Deflactar cada movimiento y calcular esfuerzo sobre ingreso disponible | Costo real y distribución del esfuerzo |
| 5. Comparación | Contratos semejantes del mismo momento | Calcular costo medio, mediana, percentiles y brecha relativa | Medida de desproporción potencial |
| 6. Justificación | Fondeo, riesgo, mora, gastos, impuestos y capital | Conciliar cada componente con contabilidad y evitar duplicaciones | Costo y margen atribuibles a la cohorte |
| 7. Prueba jurídica | Documento, información suministrada y resultado económico | Aplicar por separado los tests de información, cargos, capitalización y art. 771 | Determinación de ilicitud por práctica y período |
| 8. Cuenta contrafactual | Criterio de tasa/cargo fijado por el tribunal | Recalcular saldo desde el origen e imputar exceso a capital | Saldo legítimo o crédito restitutorio individual |
| 9. Conciliación colectiva | Resultados individuales y libros de la entidad | Sumar por cohorte y conciliar con totales regulatorios | Monto colectivo verificable sin promediar daños |
| 10. Falsación | Escenarios alternativos y datos adversos | Repetir cálculos con comparadores y asignaciones razonables | Identificación de hipótesis confirmadas, debilitadas o refutadas |

---

## 2. Carátula y comparecencia — campos a completar

**SEÑOR/A JUEZ/A [FUERO Y JURISDICCIÓN]:**

**[ASOCIACIÓN DE CONSUMIDORES AUTORIZADA / CONSUMIDOR/A AFECTADO/A / DEFENSORÍA / AUTORIDAD LEGITIMADA]**, con domicilio real en **[●]**, constituyendo domicilio procesal y electrónico en **[●]**, con patrocinio letrado de **[●]**, en representación de la clase definida en el capítulo 4, contra **[BANCO O BANCOS IDENTIFICADOS, CUIT Y DOMICILIO]**, a V.S. decimos:

### 2.1. Objeto

Venimos a promover acción colectiva de consumo en tutela de derechos individuales homogéneos, con fundamento en los artículos 42 y 43 de la Constitución Nacional; 4, 8 bis, 35 a 38, 52 a 55 de la LDC; 9, 10, 771, 984 a 989, 1092 a 1122 y 1384 a 1389 del CCyC; y la jurisprudencia de la Corte Suprema citada en este escrito, a fin de que:

1. se declare la nulidad o ineficacia de las cláusulas estandarizadas que omitan o informen incorrectamente la TEA, el CFT, cargos, seguros, amortización o totalidad de pagos;
2. se tengan por no escritos los cargos no previstos, no informados dentro del CFT o correspondientes a servicios no prestados;
3. se determine, mediante pericia económica y contable, si las tasas y capitalizaciones aplicadas excedieron sin justificación y desproporcionadamente el costo medio del dinero para operaciones comparables;
4. se reduzcan, en los casos y períodos en que ello se pruebe, los intereses conforme al artículo 771 CCyC;
5. se recalcule la deuda, imputando primero al capital los intereses pagados en exceso;
6. se restituyan a las personas integrantes de la clase las sumas indebidamente percibidas, por los mismos medios de cobro o mediante un mecanismo judicialmente controlado;
7. se ordene el cese de las prácticas declaradas ilícitas y la corrección futura de contratos, publicidad, estados de cuenta y mecanismos de débito;
8. se preserve y exhiba la información necesaria para identificar la clase, calcular el daño y medir la rentabilidad neta atribuible a cada cartera impugnada; y
9. subsidiariamente, cuando la prueba individual y corporativa revele los extremos exigidos por el artículo 175 bis del Código Penal, se extraigan testimonios y remitan al Ministerio Público Fiscal, sin anticipar en esta acción una imputación penal no demostrada.

### 2.2. Reserva sobre la vía procesal

La vía —ordinaria, sumarísima, amparo colectivo u otra prevista en la jurisdicción— deberá seleccionarse después de definir la urgencia, la complejidad pericial, el domicilio de los consumidores, las entidades demandadas y las reglas procesales locales. El prototipo no supone que el amparo sea siempre la vía idónea para una controversia contable extensa.

---

## 3. Hechos comunes propuestos

### 3.1. Contratación masiva y unilateral

Las financiaciones alcanzadas fueron comercializadas mediante contratos de adhesión, formularios, aplicaciones o recorridos digitales predispuestos por cada demandada. Las personas consumidoras no negociaron individualmente la fórmula financiera, los cargos, el sistema de amortización, la capitalización, las consecuencias de mora ni los mecanismos de cobro.

**Prueba mínima requerida:** contrato tipo por versión y fecha; pantallas completas del flujo de alta; publicidad; simulación precontractual; comprobante entregado; tabla de amortización; política de cargos; grabación o registro de consentimiento.

### 3.2. El CFT, no la TNA, expresa el costo que debe poder comprenderse

El propio BCRA explica que el CFT incluye intereses, comisiones, seguros y otros cargos y que es el indicador de cuánto se pagará realmente. La información de una TNA aislada no permite conocer el desembolso total ni comparar ofertas con distinta capitalización o estructura de cargos.

La hipótesis a verificar en cada contrato tipo es que uno o más componentes fueron:

- omitidos;
- presentados de manera tardía o poco visible;
- expresados con una métrica distinta de la exigida;
- incluidos incorrectamente en el CFT;
- cobrados sin prestación efectiva; o
- alterados unilateralmente sin base contractual válida.

El texto ordenado vigente del BCRA sobre tasas de interés exige que, en todo documento donde aparezcan tasas o importes de intereses, se consignen la tasa anual contractual, la TEA, el carácter fijo o variable y el CFT. Este último debe incorporar el efecto de intereses, comisiones y cargos computables —incluido el IVA sobre intereses para consumidores finales— y exhibirse de modo destacado: al menos al doble del tamaño de la restante información o mediante tipografía/color resaltado. Cuando una publicidad menciona cuotas, su importe o una tasa, el CFT debe mostrarse con tipografía al menos cinco veces mayor que la TNA y la cuota publicitada debe incluir los conceptos a cargo del prestatario.

La consecuencia regulatoria de omitir tasa y/o CFT no es meramente formal: las normas de protección del BCRA limitan el CFT máximo aplicable a la tasa promedio de depósitos a plazo fijo de 30 a 59 días informada por el propio Banco Central a la fecha contractual. Esta regla debe articularse con el remedio del artículo 36 LDC y someterse al tribunal según el documento omitido y el período aplicable.

### 3.3. Último corte cuantitativo: carga real elevada

Para julio de 2026, la serie oficial del BCRA registra una TNA promedio de 65,71% para préstamos personales. Bajo capitalización mensual:

\[
TEA=(1+0,6571/12)^{12}-1=89,5988\%
\]

Con inflación interanual nacional de 33,8257%:

\[
tasa\ real=(1+0,895988)/(1+0,338257)-1=41,6759\%
\]

El cálculo demuestra una carga real positiva y sustancial en el promedio agregado. **No demuestra por sí solo abuso jurídico**, porque todavía debe compararse con el costo medio de operaciones similares y con la justificación concreta de riesgo y costos.

El cálculo auxiliar expuesto en el anexo, que incorpora IVA del 21% sobre intereses y capitaliza mensualmente, arroja 115,9462%. Su tasa real frente al IPC de doce meses es 61,3638%. Debe identificarse siempre como **estimación no contractual**, no como el CFT observado en un préstamo.

### 3.4. Trayectoria 2023–2026 y necesidad de cohortes temporales

Para evitar seleccionar solamente el último año, se reconstruyeron todos los meses disponibles desde enero de 2023 hasta julio de 2026 con una regla constante: TNA promedio BCRA convertida a TEA mediante capitalización mensual y tasa real ex post mediante la inflación interanual nacional del INDEC. El resumen de promedios de las magnitudes mensuales es:

| Año | Meses | TNA promedio | TEA calculada promedio | Inflación interanual promedio | Tasa real TEA promedio |
|---:|---:|---:|---:|---:|---:|
| 2023 | 12 | 102,34% | 171,05% | 127,95% | +18,33% |
| 2024 | 12 | 85,91% | 136,32% | 236,80% | −29,22% |
| 2025 | 12 | 73,46% | 104,18% | 44,47% | +43,27% |
| 2026 | 7 | 67,90% | 93,58% | 33,00% | +45,56% |

Son promedios descriptivos de observaciones mensuales; **no son tasas contractuales anuales, no ponderan por cantidad de deudores y no acreditan un cobro individual**. El cambio de signo es jurídicamente relevante: en 2024 la inflación superó ampliamente la TEA promedio durante gran parte del año, mientras que en 2023 y especialmente en 2025–2026 la carga real agregada fue positiva. Una demanda honesta deberá formar cohortes por fecha de contratación, versión contractual, producto y momento de cada cobro, en vez de extrapolar el corte de julio de 2026 hacia atrás.

### 3.5. Indicio histórico sobre el nivel del CFT ofrecido

El Informe de Inclusión Financiera del BCRA correspondiente al primer semestre de 2023 informó para junio de ese año un CFT máximo ofrecido promedio de 321% en una muestra de quince entidades financieras con mayor cantidad de deudores que reportaban préstamos personales al Régimen de Transparencia. La cifra sirve para demostrar que la TNA puede subestimar enormemente el precio financiero visible para el consumidor y justifica obtener los CFT contractuales. No permite afirmar que una persona pagó 321%, que todos los bancos cobraron lo mismo ni que la cifra siguió vigente en 2026.

### 3.6. Declaraciones vigentes por banco y producto

El 30 de agosto de 2026 se obtuvieron por dos vías independientes las declaraciones oficiales del Régimen de Transparencia. Ambas copias contienen 2.404 registros de préstamos personales. El BCRA explica que la información es presentada por las entidades como declaración jurada y se actualiza cuando cambian las condiciones del producto; también aclara que la exactitud es responsabilidad de la entidad informante.

El criterio de selección detallado en el anexo —entidad bancaria, moneda “Pesos” y CFTEA positivo— identifica 505 líneas correspondientes a 46 bancos. No constituye una clasificación jurídica definitiva de demandados y no pondera por cantidad de clientes ni volumen. El código institucional se utiliza sólo para excluir proveedores que no pertenecen al universo bancario aquí examinado.

Entre las líneas declaradas aparecen los siguientes CFTEA máximos:

| Entidad | Producto/segmento | Fecha de información | TEA máxima | CFTEA máximo |
|---|---|---:|---:|---:|
| Banco Masventas S.A. | Convenio VGA / AMPROMM, relación de dependencia o seguridad social, 12 meses | 08/06/2026 | 6.493,13% | 13.476,52% |
| Banco Sáenz S.A. | Préstamo personal para consumo, 3 meses | 18/11/2025 | 887,74% | 1.419,46% |
| Banco del Sol S.A. | Préstamo en pesos, empleados públicos, 36 meses | 11/02/2026 | 686,35% | 999,99% |
| Brubank S.A.U. | Riesgo alto/medio alto/muy alto, 12 meses | 21/08/2026 | 483,45% | 719,39% |
| Banco Columbia S.A. | PCD, seguridad social, 36 meses | 24/08/2026 | 421,00% | 637,00% |
| Banco de Servicios Financieros Carrefour S.A.U. | Préstamo personal riesgo D, 36 meses | 24/08/2026 | 349,05% | 501,84% |
| Banco Supervielle S.A. | Préstamos personales, acreditación de sueldo, 72 meses | 21/08/2026 | 315,12% | 448,63% |
| Ualá Bank S.A.U. | Préstamo personal | 14/08/2026 | 307,35% | 436,38% |
| Banco Galicia y Buenos Aires S.A. | Préstamo personal, 72 meses | 12/06/2026 | 283,00% | 398,00% |
| Banco Nación Argentina | Libre destino tramo IV, 72 meses | 14/08/2026 | 140,40% | 186,76% |

La distribución no ponderada de las 505 líneas tiene mediana de 159,12%, percentil 75 de 234,82% y percentil 90 de 373,07%. **No es una media de mercado:** una entidad puede declarar decenas de líneas similares y quedar sobrerrepresentada. La utilidad jurídica principal de esta fuente es individualizar bancos, productos, segmentos y máximos declarados para pedir contratos, versiones históricas, cantidad de altas y tasas efectivamente aplicadas.

Los cuatro registros de 13.476,52% de Banco Masventas aparecen en las dos copias oficiales obtenidas por separado. La coincidencia descarta un error introducido al convertir los datos, pero no descarta un error de la declaración remitida por la entidad. Debe pedirse al BCRA y al banco que autentiquen, rectifiquen o expliquen esos valores y que informen si hubo contratos celebrados bajo esas líneas.

### 3.7. Rentabilidad bancaria agregada y límite de inferencia

En mayo de 2026 el BCRA informó un ROA del sistema financiero de 1,1% acumulado en doce meses y de 2,2% anualizado en tres meses. El dato permite afirmar que el sistema mostró **rentabilidad contable agregada positiva**. No permite afirmar:

- el monto nominal de ganancia de cada entidad;
- que toda la rentabilidad provino de hogares;
- que la diferencia entre tasa e inflación fue apropiada íntegramente por los bancos; o
- que una cartera particular fue rentable.

El propio informe reportó una mora de 12,8% para financiaciones a familias y previsiones por 86,3% de la cartera irregular. Esos costos deben considerarse, junto con fondeo, encajes, gastos, impuestos y capital, antes de cuantificar ganancia neta.

### 3.8. Primer cruce por entidad: oferta máxima versus resultado total

Se acompañó la información oficial **Información sobre entidades financieras — mayo de 2026** y se cotejaron, mediante el código institucional del BCRA, las 46 entidades seleccionadas. Los estados de resultados tienen corte mayo de 2026; los indicadores de ROA y ROE disponibles tienen corte marzo de 2026. Para evitar llamar ganancia a una magnitud más amplia, se calculó:

\[
resultado\ neto\ estimado\ sin\ ORI = resultado\ integral\ acumulado - otro\ resultado\ integral.
\]

Cuando el otro resultado integral no aparece informado para una entidad, se lo trató provisoriamente como cero y esa ausencia quedó identificada en la planilla acompañada. Es un cálculo verificable sobre datos remitidos al BCRA, no una atribución del resultado al producto ni una pericia contable.

Resultados seleccionados —resultado acumulado estimado, en millones de pesos—:

| Entidad | CFTEA máximo declarado | Resultado neto estimado ene–may 2026 | ROA a mar-2026 |
|---|---:|---:|---:|
| Banco Masventas S.A. | 13.476,52% | −2.679,29 | −17,97% |
| Banco Sáenz S.A. | 1.419,46% | −3.183,05 | −6,64% |
| Banco del Sol S.A. | 999,99% | −29.334,37 | −1,83% |
| Brubank S.A.U. | 719,39% | +2.884,01 | +2,44% |
| Banco de Servicios Financieros Carrefour S.A.U. | 501,84% | −41.141,40 | −10,12% |
| Banco Industrial S.A. | 425,20% | +32.327,31 | +2,22% |
| Banco Galicia y Buenos Aires S.A. | 398,00% | +156.115,26 | −0,05% |
| Banco Nación Argentina | 186,76% | +431.404,82 | +1,81% |

La aparente divergencia entre algún resultado enero–mayo y el ROA a marzo no es una contradicción: son magnitudes y ventanas temporales distintas. En el conjunto, 32 entidades muestran resultado estimado positivo y 14 negativo. Entre las diez entidades con mayor CFTEA máximo, tres tienen resultado positivo y siete negativo.

Este hallazgo tiene dos consecuencias probatorias:

1. una tasa o CFTEA extrema puede ser abusiva, estar mal informada o requerir reducción aun si el banco pierde dinero en el agregado; y
2. la existencia de resultado positivo en una entidad tampoco demuestra que ese resultado provenga de préstamos personales.

Por ello, el cruce es un mapa para seleccionar demandados, formular oficios y controlar consistencia. La prueba decisiva sigue siendo la contabilidad de gestión por producto, cohorte y contrato, conciliada con estas presentaciones regulatorias.

### 3.9. Panel público longitudinal: alcance, saldo, ingreso bruto y riesgo

La excavación de datos públicos permitió cerrar parcialmente dos vacíos que el corte único de mayo de 2026 dejaba abiertos: la trayectoria desde 2023 y la atribución contable al producto. Se preservaron seis archivos históricos del BCRA y el corte de mayo de 2026. Para cada entidad se extrajeron saldos, resultados, previsiones, indicadores y el balance detallado. Este último contiene una cuenta explícita de **intereses por préstamos personales** —511107 en pesos y 515107 en moneda extranjera—, que permite medir ingreso financiero bruto del producto sin confundirlo con el resultado neto de la entidad.

El cuadro siguiente combina tres universos que deben mantenerse separados: (i) cobertura de personas con préstamos personales en todo el sistema financiero ampliado —entidades financieras y proveedores no financieros—; (ii) agregado contable AA000 del sistema financiero regulado; y (iii) suma de cuentas de resultados de las entidades individuales. Los porcentajes están redondeados; los archivos acompañados conservan la precisión original.

| Corte | Cobertura de personales sobre adultos | Umbral CENDEU | Personales / activo AA000 | Intereses personales / ingresos financieros, suma de entidades | ROA AA000 | Irregularidad de consumo AA000 |
|---:|---:|---:|---:|---:|---:|---:|
| Dic. 2023 | 29,91% | $1.000 | 1,95% | 2,61% | 5,42% | 2,75% |
| Jun. 2024 | 31,09% | $1.000 | 2,53% | 2,53% | 6,94% | 2,73% |
| Jul. 2024 | 23,10% | $25.000 | N/D | N/D | N/D | N/D |
| Dic. 2024 | 26,63% | $25.000 | 4,75% | 4,31% | 4,10% | 2,51% |
| Jun. 2025 | 30,32% | $25.000 | 6,40% | 13,64% | 1,41% | 5,03% |
| Dic. 2025 | 32,20% | $25.000 | 6,23% | 13,65% | 1,02% | 9,18% |
| May. 2026 | N/D | N/D | 6,31% | 13,57% | 1,07% | 12,58% |

La discontinuidad de julio de 2024 no representa una pérdida repentina de ocho puntos de deudores. La Comunicación BCRA “A” 8001 elevó el saldo mínimo reportable a la Central de Deudores de $1.000 a $25.000. Por ello se calculan dos tramos: enero de 2023–junio de 2024 y julio de 2024–diciembre de 2025. Dentro del primero, la cobertura creció 2,13 puntos porcentuales desde enero de 2023; dentro del segundo, aumentó 9,09 puntos desde julio de 2024. Comparar junio con julio sin corregir el cambio de base sería un error.

Los informes semestrales permiten traducir parte de esa cobertura a personas y comportamiento:

- en diciembre de 2023, 30,2% de los adultos tenía préstamos personales; la cantidad de deudores había aumentado 6,3% durante el año, pero el saldo promedio real por deudor cayó 45% hasta $249.000;
- en junio de 2024 había más de 11,2 millones de personas con préstamos personales —31,2% de la población adulta— y el saldo promedio real había crecido 7% desde diciembre y 27% desde marzo;
- en junio de 2025 los préstamos personales alcanzaban nuevamente a 11,2 millones bajo la nueva base, 14,5% más que en diciembre de 2024; el saldo promedio real aumentó 22% en el semestre, con 23,7% en entidades financieras y 13,6% en proveedores no financieros; y
- en diciembre de 2025 había 11,9 millones de deudores de préstamos personales, 22,1% más que un año antes.

El riesgo tampoco fue constante. En diciembre de 2023, 94,3% de los deudores de entidades financieras estaba en situación regular y el saldo regular representaba 97,2% del total. En diciembre de 2024 la regularidad de personas en entidades financieras era 94,5%. Durante 2025 se produjo un deterioro: el Informe sobre Bancos cerró el año con 9,3% de mora en hogares, explicada principalmente por personales y prendarios, mientras el indicador contable específico de consumo llegó a 9,18% y luego a 12,58% en mayo de 2026. Esta trayectoria impide dos atajos opuestos: ni todo el CFT puede justificarse con una mora que era baja en 2023–2024, ni puede ignorarse el costo de riesgo que aumentó en 2025–2026.

El panel también mejora el análisis de “ganancia”. La suma de intereses brutos por préstamos personales pasó de $1,637 billones corrientes en 2023 a $3,905 billones en 2024 y $10,095 billones en 2025. Esos importes no son comparables en términos reales sin deflactar y no son ganancia: antes del resultado quedan egresos financieros, incobrabilidad, administración, servicios, impuestos, otras partidas y capital. En Banco Masventas, por ejemplo, los datos públicos muestran el límite con especial claridad:

| Período | Interés bruto de personales | Ingreso financiero total | Egreso financiero | Incobrabilidad | Administración | Resultado neto estimado sin ORI |
|---:|---:|---:|---:|---:|---:|---:|
| 2023 | $1.246,86 M | $8.963,17 M | $6.016,08 M | $167,20 M | $3.110,42 M | −$403,03 M |
| 2024 | $1.876,87 M | $7.428,53 M | $4.924,26 M | $251,32 M | $6.578,93 M | −$3.286,84 M |
| 2025 | $1.321,36 M | $7.489,23 M | $4.877,10 M | $782,59 M | $8.108,03 M | −$3.976,90 M |
| Ene.–may. 2026 | $1.332,03 M | $3.425,55 M | $2.898,57 M | $467,17 M | $3.608,93 M | −$2.679,29 M |

Son pesos corrientes y partidas acumuladas al cierre indicado. La tabla no asigna egresos al préstamo personal ni demuestra que esa cartera haya perdido: demuestra que **el ingreso bruto del producto ya es público, pero la ganancia neta del producto no lo es**. Para obtenerla debe asignarse fondeo, pérdida esperada y observada, gastos, impuestos y capital por cartera y cohorte, y conciliar el resultado con las cifras regulatorias. Tampoco una pérdida total sanea un cargo indebido, una omisión informativa o un interés desproporcionado.

### 3.10. Débitos de cuotas y falsa equivalencia con un embargo

Un débito bancario o un Cobro de Cuotas con Transferencia (CCT) **no es un embargo judicial**. El embargo requiere orden judicial. El régimen CCT anunciado por el BCRA exige, entre otras condiciones, consentimiento expreso, información previa y posibilidad de revocación. Sólo corresponderá impugnar débitos concretos cuando falte consentimiento válido, se frustre la revocación, se incumpla el aviso, se exceda la cuota autorizada o se utilice una apariencia de reclamo judicial.

La afirmación pública “embargan el sueldo sin juicio” no debe incorporarse como hecho. Sí puede investigarse si, en la práctica, una entidad capturó fondos sin consentimiento eficaz o mediante mecanismos contractuales abusivos.

### 3.11. El sistema regulatorio conserva el rastro del patrón

La hipótesis colectiva no depende únicamente de reunir contratos aportados por víctimas. Las normas vigentes obligan a cada entidad a:

1. registrar en una base única y centralizada los reclamos que requieren análisis y las quejas por incumplimiento o prestación defectuosa, cualquiera sea el canal;
2. conservar esa base durante diez años;
3. mantener registros separados de reintegros y de denuncias judiciales o administrativas de consumo;
4. elevar al menos trimestralmente reportes con temas, cantidades, montos, productos, sucursales, plazos, comparación histórica y propuestas correctivas;
5. someter el sistema de atención y esos registros a auditoría interna; y
6. analizar causas generadoras cuando de los eventos pueda inferirse la afectación de un conjunto de usuarios.

Además, cuando constata un cobro indebido, la entidad debe verificar si la misma situación alcanzó a otros usuarios y reintegrarles. El BCRA tiene acceso regulatorio a esos registros, manuales, reportes y auditorías. Por ello, una negativa genérica de inexistencia de patrón puede contrastarse con documentación contemporánea creada bajo deber regulatorio, con pedidos simultáneos al banco y al BCRA.

El Informe sobre Protección a las Personas Usuarias de Servicios Financieros 2025 refuerza la relevancia —no la conclusión— de esa prueba. El universo informado por entidades registró 769,5 mil reclamos mensuales promedio y una resolución favorable consolidada de 64%; “Préstamos” alcanzó 60% y “Cargos/comisiones no procedentes o mal aplicados”, 74%. El denominador es 140,5 millones de relaciones usuario–entidad —una misma persona cuenta nuevamente si opera con otra entidad— y el indicador consolidado fue 0,55 reclamos cada 100. La publicación consolida entidades financieras, proveedores de pagos, emisores de tarjetas y otros prestamistas, y no separa contratos personales ni demandados. No prueba frecuencia de abuso; sí justifica requerir el desglose regulatorio preexistente.

### 3.12. Caso de autenticación prioritaria: Banco Masventas

La fuente pública del BCRA contiene cuatro líneas de convenios “VGA / AMPROMM”, actualizadas el 8 de junio de 2026, con CFTEA máximo de 13.476,52%. La página pública de Banco Masventas preservada el 30 de agosto enlazaba un tarifario con vigencia 5 de agosto de 2026. Ese PDF muestra, para los préstamos personales listados de cuenta sueldo y cliente general, CFTEA con IVA entre 102,43% y 274,40%; no contiene las denominaciones VGA o AMPROMM. El máximo extremo del BCRA es unas 49 veces el máximo personal visible en ese tarifario posterior.

La diferencia **no demuestra un cobro ni una falsedad**: puede responder a productos específicos no publicados en el tarifario general, a cambio de vigencia, a una convención de reporte o a un error. Sí crea una inconsistencia objetiva y verificable que exige que banco y regulador informen:

- definición exacta de cada producto y convenio;
- fórmula, capital de referencia, plazo y componentes del CFTEA;
- versiones históricas remitidas, rectificaciones y responsables de la declaración jurada;
- cantidad de ofertas, altas y contratos efectivamente celebrados bajo cada línea; y
- tasas y CFT contractuales efectivamente aplicados.

El sitio oficial también publica un formulario de solicitud identificado como **F.0132-Agosto/20** y un resumen F.0268, ambos ofrecidos desde una página fechada 27 de diciembre de 2023. El primero contiene casilleros para TNA, TEM, TEA y CFTEA, sistema francés, mora, punitorios, débitos y cambios de condiciones; el resumen genérico declara “ninguno” en comisiones, pero remite las tasas al sitio web y no contiene, en la copia pública en blanco, capital, total a pagar, cantidad, periodicidad y vencimiento de cuotas. Son modelos históricos, no contratos completados ni prueba de uso en 2026. Su valor es delimitar una orden de exhibición de todas las versiones, anexos, resúmenes personalizados, pantallas y constancias de entrega entre 2020 y 2026.

---

## 4. Clase y subclases propuestas

### 4.1. Definición inicial

> Todas las personas humanas que actuaron como destinatarias finales y contrataron con **[BANCO DEMANDADO]**, desde el **1 de enero de 2023** hasta **[FECHA DE CORTE DE LA CLASE]**, préstamos personales o financiaciones comprendidas en **[PRODUCTO/CONTRATO TIPO]**, a quienes se aplicó la cláusula, fórmula o práctica común identificada como **[●]**, sin perjuicio de delimitar subclases reclamables según exigibilidad, prescripción y versión normativa aplicable.

### 4.2. Subclases posibles

1. **Información:** contratos sin TEA/CFT completo, tabla de pagos o detalle de extras.
2. **Cargos:** personas a quienes se cobraron comisiones, seguros o conceptos no previstos, no prestados o incorrectamente incluidos en el CFT.
3. **Interés desproporcionado:** cohortes cuya tasa/CFT excedió injustificada y desproporcionadamente el comparador de operaciones similares que establezca la pericia.
4. **Mora y capitalización:** contratos con fórmula común de punitorios, anatocismo o capitalización contraria al artículo 770 CCyC.
5. **Débito no consentido:** cuotas debitadas sin consentimiento trazable, luego de revocación válida o por monto distinto del autorizado.
6. **Temporales y regulatorias:** contratos o cobros agrupados por versión contractual y por la regulación vigente al producirse el hecho —como mínimo, cohortes atravesadas por las Comunicaciones BCRA “A” 7744, “A” 8203 y “A” 8433—, evitando aplicar retrospectivamente una modificación posterior.

### 4.3. Exclusiones

Quedan inicialmente fuera:

- créditos destinados de manera comprobable a una actividad empresarial y no al consumo final;
- contratos negociados individualmente sin cláusula común relevante;
- productos garantizados o con estructura de riesgo materialmente distinta, salvo subclase propia;
- quienes hayan obtenido sentencia firme individual sobre el mismo objeto; y
- débitos válidamente consentidos respecto de los cuales no exista otra infracción.

### 4.4. Por qué no conviene una única clase contra “todos los bancos”

La acción colectiva exige una causa fáctica común. Bancos, productos, riesgos, cargos y contratos diferentes pueden impedir la homogeneidad. La estrategia más sólida es demandar a cada entidad por su propia conducta común, o agrupar entidades sólo cuando exista una práctica o cláusula sustancialmente idéntica y evidencia de coordinación o uniformidad regulatoria relevante. La diversidad de montos no destruye la clase; la ausencia de un hecho común sí puede hacerlo.

---

## 5. Admisibilidad colectiva

### 5.1. Derechos individuales homogéneos

Conforme a **“Halabi, Ernesto c/ PEN”**, Fallos 332:111, la tutela colectiva de derechos individuales homogéneos requiere, en términos sustanciales:

1. una causa fáctica común;
2. una pretensión concentrada en los efectos comunes; y
3. que el ejercicio individual no aparezca plenamente justificado o que exista un fuerte interés estatal en la tutela.

Aquí, la causa común no debe formularse como “el crédito es caro”, sino como la aplicación masiva de una misma cláusula, fórmula, omisión informativa o cargo a una cartera identificable.

### 5.2. Contratos de adhesión y montos individualmente pequeños

En **“PADEC c/ Swiss Medical S.A.”**, Fallos 336:1236, la Corte reconoció la aptitud de una asociación para impugnar cláusulas predispuestas con efectos sobre un conjunto de consumidores. En **“Consumidores Financieros Asociación Civil para su defensa c/ Banco Itaú Buen Ayre Argentina S.A.”**, Fallos 337:753, trató una acción contra un banco por cargos de “riesgo contingente” y una TEA alegadamente irrazonable; consideró relevante la conducta común y el reducido incentivo para litigios individuales.

Estos fallos sostienen la **vía colectiva y la legitimación**, no prueban automáticamente que cualquier tasa aquí analizada sea abusiva. La cuestión de fondo deberá acreditarse.

### 5.3. Representación adecuada, publicidad y registro

Antes de presentar se deberá:

- verificar el Registro Público de Procesos Colectivos para evitar duplicidad;
- describir con precisión la clase y el hecho común;
- acreditar la idoneidad del representante y del patrocinio;
- proponer un mecanismo de notificación y exclusión;
- preservar los reclamos individuales diferenciados; y
- solicitar inscripción conforme a las Acordadas CSJN 32/2014 y 12/2016.

---

## 6. Derecho de fondo

### 6.1. Constitución Nacional

El artículo 42 protege los intereses económicos de consumidores y usuarios, su derecho a información adecuada y veraz, libertad de elección y trato equitativo y digno. El artículo 43 reconoce legitimación colectiva al afectado, al Defensor del Pueblo y a asociaciones registradas para derechos de incidencia colectiva.

### 6.2. Deber de información y crédito para consumo

Los artículos 4 y 36 LDC obligan a informar de modo cierto, claro y detallado. En operaciones financieras para consumo, el documento debe contener, bajo pena de nulidad, monto financiado, TEA, total de intereses o CFT, amortización, cantidad y monto de pagos y gastos extras. Si se omite la TEA, la ley prevé ajustar los intereses a la tasa pasiva anual promedio difundida por el BCRA vigente al contratar.

Los artículos 1388 y 1389 CCyC complementan esa tutela: ninguna suma no prevista puede exigirse; no pueden cobrarse comisiones o costos por servicios no prestados; los costos omitidos o incorrectamente incluidos en el CFT se tienen por no escritos; y son nulos los contratos de crédito sin la información legal esencial.

### 6.3. Cláusulas abusivas, buena fe y abuso del derecho

Los artículos 9 y 10 CCyC imponen buena fe y vedan el ejercicio abusivo de derechos. Los artículos 37 y 38 LDC, junto con los artículos 984 a 989 y 1117 a 1122 CCyC, permiten tener por no convenidas cláusulas predispuestas que desnaturalizan obligaciones, restringen derechos, amplían injustificadamente los del proveedor o generan un desequilibrio significativo.

La mera transparencia formal no sanea necesariamente una cláusula sustancialmente abusiva. A la inversa, una tasa elevada no basta: deben identificarse la desproporción, la falta de justificación y el comparador correcto.

La Corte Suprema, en **“Prevención, Asesoramiento y Defensa del Consumidor c/ BankBoston N.A.”**, Fallos 340:172, caracterizó al consumidor bancario como sujeto de vulnerabilidad estructural frente a contratos predispuestos. Precisó que la aprobación del cobro de una comisión por el BCRA no impide el control judicial de abusividad y que una cláusula inicialmente lícita puede devenir abusiva por la evolución económica del cargo. También descartó que las cláusulas abusivas queden saneadas por consentimiento tácito. El precedente no resuelve el precio de un préstamo personal, pero neutraliza dos defensas anticipables: “lo permitió el regulador” y “el cliente no objetó”.

### 6.4. Reducción judicial de intereses

El artículo 771 CCyC permite reducir intereses cuando la tasa fijada o el resultado de capitalizarlos excede **sin justificación y desproporcionadamente** el costo medio del dinero para deudores y operaciones similares en el lugar de contratación. Los intereses pagados en exceso se imputan al capital y, extinguido éste, pueden repetirse.

La Suprema Corte bonaerense, en **“Asociación Mutual Asís c/ Cubilla”**, admitió que el pagaré de consumo sea integrado con la documentación causal sólo si el conjunto satisface el artículo 36 LDC; además señaló expresamente que los intereses son revisables por abuso o desproporción conforme al artículo 771. El precedente no fija un umbral numérico, pero confirma que ni la abstracción del pagaré ni el carril ejecutivo clausuran el control consumeril del contrato y sus intereses.

El test propuesto para la pericia es:

1. identificar la tasa y todos los cargos efectivamente cobrados;
2. convertirlos a una métrica anual comparable, explicitando capitalización;
3. seleccionar operaciones comparables por fecha, monto, plazo, riesgo, garantía, canal y perfil;
4. medir la distancia respecto del costo medio y su persistencia;
5. requerir al banco la justificación contable y actuarial de esa distancia; y
6. determinar si el exceso fue desproporcionado e injustificado.

La inflación es un control económico relevante para medir carga real, pero **no reemplaza** el comparador legal de operaciones similares.

### 6.5. Capitalización y mora

El artículo 770 CCyC limita el anatocismo y exige examinar separadamente intereses compensatorios, moratorios, punitorios, cargos por gestión y capitalización. La pericia deberá reconstruir la trayectoria completa de la deuda y detectar si cargos denominados de otra manera cumplen económicamente la función de interés.

### 6.6. Cobranza digna y débitos

El artículo 8 bis LDC exige trato digno y prohíbe que las cobranzas extrajudiciales adopten apariencia de reclamo judicial. El artículo 35 prohíbe propuestas no solicitadas que generen cargos automáticos y obliguen al consumidor a darse de baja. Estas normas son pertinentes sólo si los hechos muestran intimidación, falsa judicialización o ausencia de consentimiento; no convierten en ilícito un débito correctamente autorizado.

### 6.7. Usura penal: hipótesis condicionada

El artículo 175 bis del Código Penal exige más que una tasa alta: requiere aprovechamiento de la necesidad, ligereza o inexperiencia de una persona, intereses o ventajas evidentemente desproporcionados —o garantías extorsivas— y el elemento subjetivo correspondiente.

Por ello:

- no se afirmará que “CFT mayor que inflación” equivale a usura penal;
- se investigarán criterios de segmentación, urgencia financiera conocida, refinanciaciones compulsivas, información ocultada y garantías desproporcionadas;
- sólo ante evidencia concreta se solicitará la intervención penal correspondiente; y
- la nulidad, reducción y restitución de consumo pueden prosperar aunque no se configure delito.

### 6.8. Prescripción y corte temporal: separar remedios antes de definir la clase

No debe afirmarse un único plazo para toda la acción. Desde la entrada en vigor del CCyC, el artículo 50 LDC regula la prescripción de **sanciones** de la ley, no formula un plazo general para todas las acciones civiles de consumo. El análisis debe distinguir al menos:

1. nulidad o ineficacia de cláusulas y revisión del contrato;
2. restitución o repetición de cobros con causa contractual;
3. reducción e imputación del exceso de intereses del artículo 771;
4. indemnización de daños; y
5. multa civil, sanciones administrativas y efectos preventivos.

Como hipótesis de trabajo —sujeta a la causa concreta y la jurisdicción—, el artículo 2560 CCyC establece un plazo genérico de cinco años cuando no existe otro, aunque desde enero de 2026 admite que la legislación local prevea uno diferente; el artículo 2561 fija tres años para la indemnización de daños; y el artículo 2562 contempla plazos de dos años para supuestos específicos como nulidad relativa o revisión de actos jurídicos. La demanda deberá justificar por qué cada remedio encuadra —o no— en esas categorías, sin trasladar automáticamente el plazo de uno a los demás.

El cómputo tampoco debe presumirse único. El artículo 2554 parte de la exigibilidad y las cuotas son prestaciones sucesivas, pero la fecha de conocimiento, los efectos continuados, la exigibilidad de cada cobro, los actos interruptivos o suspensivos y las reglas procesales locales requieren análisis caso por caso. La estrategia conservadora es:

- formar cohortes temporales alternativas;
- identificar por integrante fecha de contrato, cuota, reclamo y eventual mediación;
- demandar primero los períodos indiscutiblemente vivos;
- plantear separadamente restitución, daños y tutela preventiva; y
- pedir preservación desde el inicio, porque el registro regulatorio de reclamos se conserva diez años aunque la pretensión individual pueda tener un corte menor.

La conservación decenal del RCCR es una regla de prueba, **no** un plazo de prescripción.

El corte de investigación en enero de 2023 cumple una función probatoria independiente del alcance final de la condena. Aunque una defensa de prescripción pudiera excluir total o parcialmente una pretensión patrimonial temprana, los contratos, reclamos, reintegros, versiones y decisiones internas de 2023 pueden seguir siendo relevantes para demostrar origen, continuidad, conocimiento, modificaciones, actos interruptivos y efectos actuales de una práctica. Esa relevancia no revive por sí sola una acción prescripta.

### 6.9. Derecho intertemporal y normativa aplicable a cada cohorte

La Constitución, la LDC y el CCyC rigen como marco sustantivo durante todo el período investigado. Las comunicaciones y textos ordenados del BCRA, en cambio, deben reconstruirse según la fecha del contrato, la modificación, el cargo, el débito y la información suministrada. Para este tramo se preservaron tres hitos oficiales:

1. la Comunicación “A” 7744, fechada el 17 de abril de 2023, cuyas páginas internas registran vigencias desde el 28 de febrero y el 18 de abril de 2023;
2. la Comunicación “A” 8203, con vigencia indicada al 27 de febrero de 2025; y
3. la Comunicación “A” 8433, con vigencia indicada al 7 de mayo de 2026.

Estas comunicaciones permiten reconstruir obligaciones sobre contrato, resumen, costo financiero, cargos, comunicaciones y registros en sus respectivas etapas. Una versión posterior sólo podrá usarse respecto de hechos anteriores cuando reproduzca un deber ya vigente por otra fuente; no como fundamento retroactivo automático. Para cada caso deberá elaborarse una matriz con: fecha de alta, versión del contrato y flujo digital, fecha y naturaleza de cada modificación, fecha de cada cobro, norma vigente, reclamo, respuesta, exigibilidad y remedio pretendido.

---

## 7. Ganancia neta atribuible al banco

### 7.1. Qué debe demostrarse

La tasa o el CFT son el precio/costo del crédito para el deudor. La ganancia neta del banco es un resultado contable después de costos y pérdidas. Para una cohorte de préstamos personales, la reconstrucción mínima es:

\[
\begin{aligned}
Resultado\ neto\ atribuible ={}& intereses\ devengados\ y\ cobrados \\
&+ comisiones,\ seguros\ y\ cargos\ retenidos \\
&+ punitorios\ y\ recuperos \\
&- costo\ de\ fondeo\ asignable \\
&- pérdidas\ crediticias\ y\ previsiones \\
&- encajes\ y\ costos\ de\ liquidez \\
&- gastos\ operativos\ asignables \\
&- impuestos \\
&- costo\ de\ capital\ regulatorio\ pertinente \\
&\pm otros\ resultados\ directamente\ atribuibles.
\end{aligned}
\]

### 7.2. Por qué importa jurídicamente

La ganancia neta no es un requisito textual del artículo 771, pero puede ser relevante para:

- valorar la justificación ofrecida para la tasa;
- distinguir cobertura de riesgo de extracción de renta;
- cuantificar restituciones por cargos específicos;
- graduar una eventual multa civil, si procediera;
- demostrar conocimiento, persistencia y escala de una práctica; y
- refutar defensas genéricas de costo cuando la contabilidad interna muestre márgenes extraordinarios.

### 7.3. Información que debe exhibir cada demandada

Por producto, contrato tipo y cohorte mensual:

1. capital originado, saldo, plazo, tasa y CFT;
2. flujo de cobros por interés, capital, cargos, seguros y mora;
3. tasa de fondeo aplicada internamente y metodología de transferencia de fondos;
4. calificación de riesgo, probabilidad de incumplimiento y pérdida esperada al originar;
5. mora, castigos, recuperos y refinanciaciones observados;
6. previsiones contables y regulatorias;
7. costos operativos y de adquisición asignados;
8. impuestos, encajes, liquidez y capital atribuidos;
9. ingreso neto y margen ajustado por riesgo de la cartera;
10. actas de comité de precios, modelos, manuales y versiones que expliquen la fijación de tasas; y
11. conciliación entre esos datos y estados contables auditados/información remitida al BCRA.

### 7.4. Uso correcto del ROA público

El ROA del sistema es contexto y control de plausibilidad. No debe multiplicarse mecánicamente por el saldo de préstamos personales ni sumarse a la tasa o al CFT. La pericia debe trabajar con la contabilidad de la entidad y la cartera específica.

El cruce público por entidad permite una segunda prueba de plausibilidad: cotejar oferta máxima, resultado integral, saldo e ingreso bruto por intereses de préstamos personales, activos, previsiones, ROA, ROE, tasa implícita de préstamos, margen financiero e irregularidad de consumo. La cuenta pública de intereses personales cierra una parte del vacío de atribución al producto, pero ninguna de esas columnas, aislada o combinada sin asignación causal, sustituye el margen neto de la cartera. Sí permite detectar inconsistencias, priorizar pedidos y comprobar si la explicación interna reconcilia con lo informado al regulador.

---

## 8. Prueba ofrecida y diligencias preliminares

### 8.1. Documental pública ya identificada

1. Series mensuales oficiales BCRA de tasas de préstamos personales.
2. Serie oficial INDEC del IPC nacional.
3. Informe de Inclusión Financiera BCRA, primer semestre de 2023, gráfico 18.
4. Informes de Inclusión Financiera BCRA de los segundos semestres de 2023, 2024 y 2025 y de los primeros semestres de 2024 y 2025.
5. Informe sobre Bancos BCRA, diciembre de 2025 y mayo de 2026, más sus planillas oficiales.
6. Archivos abiertos BCRA de balances, resultados y balance detallado por entidad para septiembre y diciembre de 2023, junio y diciembre de 2024, junio y diciembre de 2025 y mayo de 2026.
7. Bases abiertas CENDEU de deudores por asistencia, edad y grupo institucional, separadas antes y después del cambio de umbral de julio de 2024.
8. texto ordenado BCRA sobre Protección de los Usuarios de Servicios Financieros y texto ordenado sobre Tasas de Interés en las Operaciones de Crédito;
9. Comunicaciones BCRA “A” 7744, “A” 8203 y “A” 8433, para reconstruir la regulación vigente dentro de 2023–2026;
10. Comunicación BCRA “A” 5402 como antecedente del requerimiento de monto, cantidad y tasa ponderada de préstamos personales efectivamente desembolsados por tramo de CFT, sujeta a verificar continuidad y reemplazos;
11. serie mensual y resumen anual verificables del costo agregado entre enero de 2023 y julio de 2026;
12. Informes sobre Protección a las Personas Usuarias de Servicios Financieros 2023, 2024 y 2025; y
13. formularios, resúmenes y tarifarios que cada demandada haya publicado, preservando fecha, URL y hash.

### 8.2. Documental en poder de las demandadas

Se solicitará exhibición de contratos, anexos, tablas, pantallas, registros de consentimiento, estados de cuenta, legajos de reclamo, diccionario de cargos, reglas de imputación, matrices de precios y la información contable enumerada en el capítulo 7, desde el 1 de enero de 2023 hasta la fecha de cumplimiento de la orden.

Además, por producto, versión y período, deberá requerirse específicamente:

1. Registro Centralizado de Consultas y Reclamos (RCCR), con motivo, producto, sucursal, estado, respuesta y documentación respaldatoria;
2. Registro de Reintegros de Importes (RRI), con causal y monto;
3. Registro de Denuncias ante Instancias Judiciales y/o Administrativas de Defensa del Consumidor (RDJA);
4. reportes trimestrales del responsable de atención y del Directivo/Comité de Protección, sus evaluaciones y actas de Directorio;
5. informes de auditoría interna y externa, observaciones del BCRA y planes correctivos;
6. análisis de causas generadoras de eventos con posible afectación colectiva;
7. verificaciones realizadas para identificar otros usuarios en la misma situación y reintegros automáticos efectuados; y
8. manuales de procedimiento, taxonomías de reclamo, reglas de deduplicación y cambios en su clasificación.

La orden deberá abarcar todas las versiones históricas y sus fechas de entrada y salida, no sólo la versión vigente. Para cada alta o modificación deberán conservarse el documento mostrado, sus anexos, la pantalla o plantilla, los parámetros de cálculo, los metadatos de aceptación y la constancia entregada al usuario.

La exhibición deberá proveerse con un diccionario de datos, historial de cambios y totales de control. Para proteger privacidad, puede comenzar anonimizada o seudonimizada, bajo reserva y con acceso pericial; la confidencialidad comercial no justifica ocultar la existencia del patrón ni los agregados necesarios para definir la clase.

El artículo 53 LDC dispone que los proveedores deben aportar al proceso todos los elementos de prueba en su poder y colaborar con el esclarecimiento. Esa regla no exime a la actora de identificar la práctica y aportar indicios; impide que el proveedor se beneficie ocultando datos exclusivamente bajo su control.

Como aplicación bancaria reciente de esa regla, la Cámara Nacional de Apelaciones en lo Comercial, Sala B, en **“Custo c/ Banco Santander Río”** (03/09/2025), ponderó contra la entidad la falta de acompañamiento del legajo del cliente y la negligencia en producir la pericia contable. Destacó que el banco estaba en mejor posición profesional y técnica y no podía limitarse a una negativa genérica. Aunque el caso versó sobre una cuenta corriente y no sobre el precio de un préstamo, refuerza el pedido de exhibición de documentos y datos internos que sólo controla la entidad.

### 8.3. Pericia económica, financiera y actuarial

Puntos propuestos:

1. identificar el desembolso neto realmente recibido y la fecha de cada flujo;
2. reconstruir todos los pagos exigidos, incluidos intereses, impuestos, seguros, comisiones, retenciones y cargos;
3. calcular la tasa interna mensual del flujo y convertirla a CFTEA, informando supuestos, redondeos y tratamiento de fechas irregulares;
4. comprobar la consistencia entre publicidad, resumen, contrato, tabla de amortización, débito y registración contable;
5. deflactar desembolso y pagos por IPC según su fecha, sin confundir tasa real con suma real pagada;
6. calcular el esfuerzo de cuota sobre ingreso disponible cuando la prueba permita hacerlo, con distribución por cohortes y no sólo promedio;
7. formar grupos comparables por fecha, monto, plazo, riesgo, garantía, canal, moneda y vinculación salarial;
8. establecer para cada grupo la mediana, el promedio ponderado, los percentiles y la dispersión del CFT contratado;
9. medir la brecha relativa, la persistencia y la sensibilidad a comparadores alternativos;
10. evaluar la justificación de riesgo y costos suministrada por el banco, controlando doble cómputo entre mora, previsiones y costo de capital;
11. explicar qué resultados refutarían la hipótesis de desproporción, además de los que la confirmarían;
12. reconstruir la cuenta contrafactual bajo cada tasa que indique el tribunal, imputando primero el exceso al capital;
13. liquidar por persona cualquier restitución posterior a la extinción del capital; y
14. conciliar la suma individual con los totales de la cartera y los estados de la entidad.

### 8.4. Pericia contable

Puntos propuestos:

1. conciliar cobros de la clase con libros y reportes regulatorios;
2. separar ingreso financiero, cargos, seguros, punitorios y recuperos;
3. verificar fondeo, previsiones, castigos, impuestos y gastos;
4. calcular resultado neto atribuible por producto y cohorte;
5. identificar cambios de metodología o de precio y su aprobación interna; y
6. cuantificar el beneficio obtenido con cargos declarados indebidos.

### 8.5. Informativa

Líbrese oficio al BCRA para que informe, en el período y nivel de desagregación legalmente disponible:

- tasas, CFT y cargos reportados por cada demandada;
- versiones de contratos e historial del Régimen de Transparencia desde el 1 de enero de 2023;
- cantidad de deudores y saldos de la cartera;
- reclamos y actuaciones sobre las prácticas impugnadas;
- información de mora, previsiones y resultados por entidad; y
- normativa y criterios de supervisión aplicables.

El oficio deberá pedir también, respecto de cada demandada y sin invadir el secreto individual innecesariamente:

- copias o extracción autenticada del RCCR, RRI y RDJA disponibles para la supervisión;
- reportes trimestrales, auditorías y acciones correctivas relacionadas con el producto o práctica;
- reclamos de asociaciones y actuaciones de oficio por afectación general;
- fecha, contenido, rectificación y metadatos de cada declaración del Régimen de Transparencia;
- definición técnica del CFTEA reportado y validaciones automáticas aplicadas; y
- universo de usuarios que el BCRA haya identificado a partir de reclamos o fiscalización.

El antecedente de la Comunicación “A” 5402 vuelve posible formular un requerimiento más preciso, sin afirmar que el régimen conserve hoy idéntica vigencia. El BCRA deberá informar: (i) fecha de derogación, sustitución o última recepción del Régimen Informativo sobre CFT de Préstamos Personales; (ii) comunicaciones sucesoras y tablas de equivalencia; (iii) política de retención; y (iv) si conserva, para 2023–2026, presentaciones por entidad y mes sobre préstamos **efectivamente desembolsados**, distribuidos por tramo de CFT, monto, cantidad y TNA promedio ponderada. Si existen, deberán remitirse en formato tabular autenticado; si no existen o fueron eliminadas, deberá indicarse la base normativa, fecha y responsable. La comunicación de 2013 acredita el diseño histórico del dato, no su disponibilidad actual.

En el caso Masventas deberá solicitarse en forma expresa la autenticación de las cuatro líneas VGA/AMPROMM con CFTEA 13.476,52%, su historia de cambios y cualquier comunicación de inconsistencia, contrastándolas con el tarifario bancario vigente desde el 5 de agosto de 2026.

### 8.6. Preservación de evidencia

Se solicitará ordenar a las demandadas la preservación de bases, logs, contratos versionados, comunicaciones, grabaciones, modelos de precios, registros contables, RCCR, RRI, RDJA, reportes directivos y auditorías desde el 1 de enero de 2023, incluyendo respaldos y versiones retiradas. La medida debe impedir borrado, reclasificación o rotación ordinaria sin paralizar la operatoria lícita. Debe exigir copia forense o exportación inalterable, hash, fecha de extracción, responsable y conciliación de totales.

### 8.7. Vía administrativa paralela sin renunciar a la judicial

Cada reclamante testigo deberá formular primero un reclamo trazable ante la entidad, conservar número, documentos y respuesta, y —si no hay solución en diez días hábiles o es insatisfactoria— presentar la segunda instancia ante el BCRA. Una asociación reconocida puede denunciar ante el Banco Central una afectación de intereses generales; el regulador puede identificar el universo, ejercer disciplina e iniciar acciones correctivas de oficio por urgencia, gravedad o impacto general.

La vía administrativa no reemplaza la demanda ni debe demorarla hasta poner en riesgo la prescripción. Sirve para fijar conocimiento, activar registros obligatorios, provocar una respuesta verificable y obtener un segundo canal de preservación. El propio texto ordenado aclara que la actuación ante el BCRA es sin perjuicio de las acciones judiciales.

---

## 9. Tutela preventiva y cautelar — propuesta calibrada

Hasta contar con evidencia suficiente, no corresponde pedir una suspensión indiscriminada de todas las cuotas. Sí puede solicitarse, respecto de la clase prima facie acreditada:

1. prohibición de cobrar cargos específicamente no previstos o no prestados;
2. prohibición de capitalizar o aplicar punitorios sobre la porción judicialmente controvertida;
3. abstención de informar como mora la porción disputada cuando el consumidor pague capital e importe no controvertido según mecanismo judicial;
4. habilitación inmediata de revocación de débitos y constancia trazable;
5. conservación de toda evidencia; y
6. información clara en estados de cuenta sobre capital, interés, cargos, CFT y saldo.

Cada medida exige acreditar verosimilitud, peligro en la demora, proporcionalidad y contracautela según la jurisdicción.

---

## 10. Reparación colectiva

El artículo 54 LDC permite que la sentencia establezca pautas para la reparación económica y ordena que las sumas se restituyan, en principio, por los mismos medios en que fueron percibidas. Se propone:

1. identificar integrantes desde los registros del banco, sin trámite de adhesión oneroso;
2. recalcular automáticamente cada cuenta según la regla judicial;
3. imputar el exceso primero a capital;
4. acreditar saldos a favor en cuenta activa o transferirlos a una cuenta informada;
5. localizar a exclientes mediante un mecanismo público y verificable;
6. emitir liquidación individual comprensible y canal de observación;
7. someter la ejecución a auditoría pericial; y
8. reservar vía incidental para daños diferenciados.

El mecanismo debe armonizarse con el punto 2.3.5 del texto ordenado BCRA: los cobros indebidos comprendidos se reintegran dentro de diez días hábiles desde el reclamo o cinco días hábiles desde su constatación por la entidad o la supervisión; generan gastos razonables e interés compensatorio equivalente a 1,5 veces la tasa promedio de depósitos a plazo fijo de 30 a 59 días; y, detectado el evento, la entidad debe verificar y reintegrar a otros usuarios en la misma situación. La misma norma contempla expresamente su aplicación a acuerdos colectivos homologados y sentencias, salvo incompatibilidad con lo ordenado judicialmente.

La multa civil del artículo 52 bis LDC se deja planteada **en subsidio** y su procedencia colectiva, destino y cuantificación deberán fundarse según la jurisprudencia de la jurisdicción y la gravedad probada; no se presume a partir de una tasa alta.

---

## 11. Defensas previsibles y respuesta probatoria

| Defensa probable | Respuesta jurídicamente sostenible |
|---|---|
| “La inflación justifica toda tasa nominal alta.” | La inflación se reconoce y se usa para medir carga real; el artículo 771 exige además comparar operaciones similares y evaluar justificación y proporcionalidad. |
| “La mora de hogares exige una prima elevada.” | La mora es material y debe incluirse. Se pide contrastar la prima ex ante con pérdidas y recuperos reales por cohorte, sin asumir que toda diferencia fue renta. |
| “El consumidor aceptó el contrato.” | La aceptación no convalida omisiones informativas, cargos no previstos ni cláusulas abusivas en contratos de adhesión. |
| “Cada cliente es distinto.” | Se proponen subclases por banco, producto y cohorte. Los montos individuales pueden liquidarse desde registros comunes; lo común debe ser la cláusula o práctica. |
| “El ROA es bajo o corresponde a otros negocios.” | Correcto: el ROA agregado no prueba rentabilidad de la cartera. Por eso se pide pericia contable atribuible, no una inferencia automática. |
| “El CFT fue publicado.” | Debe probarse qué versión se mostró, cuándo, con qué componentes y si coincide con lo efectivamente cobrado. |
| “El débito fue autorizado.” | Se requerirá trazabilidad de consentimiento, aviso, monto y revocación. Un débito válidamente autorizado no se impugna por ser débito. |
| “La regulación del BCRA fue cumplida o aprobó el cargo.” | El cumplimiento regulatorio debe probarse en los hechos y no desplaza la Constitución, la LDC ni el CCyC. BankBoston, Fallos 340:172, confirma que la aprobación del BCRA no excluye el control judicial de abusividad. |
| “El valor del Régimen de Transparencia es sólo un error de carga.” | Puede serlo. La actora no lo presentará como cobro: pedirá la historia de rectificaciones, fórmula, contratos alcanzados y responsable de la declaración jurada. La discrepancia con el tarifario propio vuelve necesaria la autenticación. |
| “La oferta máxima no prueba lo pagado.” | Correcto. El dato público selecciona productos y períodos; la pretensión de restitución requiere contratos, liquidaciones y movimientos efectivos. |
| “No existe patrón porque casi nadie reclamó.” | La ausencia de reclamo no convalida una práctica; además la entidad debe exhibir RCCR, RRI, RDJA, reportes y clasificación. Se usarán tasas por universo y no números brutos, sin equiparar reclamo con infracción. |
| “La acción está prescripta.” | Se separarán remedios, fechas de exigibilidad y cohortes. Art. 50 LDC regula sanciones; los plazos civiles posibles y las reglas locales se alegarán en forma diferenciada, sin usar los diez años de conservación como plazo sustantivo. |
| “Los datos son confidenciales o están sujetos a secreto.” | Se propone entrega seudonimizada, reserva, perito y totales agregados. La protección de datos no impide producir el hecho común ni la liquidación bajo control judicial. |

---

## 12. Petitorio — prototipo

Por lo expuesto, a V.S. solicitamos:

1. se nos tenga por presentados, parte y con domicilios constituidos;
2. se tenga por promovida la acción colectiva contra **[DEMANDADA/S]**;
3. se defina y certifique la clase o subclases propuestas, con las correcciones que correspondan;
4. se consulte e inscriba el proceso en el Registro Público de Procesos Colectivos;
5. se dé intervención al Ministerio Público Fiscal;
6. se ordene publicidad adecuada y un mecanismo de exclusión;
7. se disponga la preservación y exhibición de la prueba identificada;
8. se produzcan las pericias e informes ofrecidos;
9. oportunamente se declaren nulas, ineficaces o no escritas las cláusulas y cargos probados;
10. se reduzcan los intereses que satisfagan el test del artículo 771 CCyC;
11. se recalcule cada deuda y se restituyan las sumas indebidamente percibidas conforme al artículo 54 LDC;
12. se ordene el cese y corrección futura de las prácticas ilícitas;
13. se impongan, si la prueba y el derecho aplicable lo justifican, daños, multa civil, intereses y costas;
14. se mantenga la reserva de remitir antecedentes al Ministerio Público Fiscal si aparecieran elementos del artículo 175 bis del Código Penal; y
15. se ordene a cada demandada identificar y reintegrar a todas las personas en igual situación, conforme al punto 2.3.5 del texto ordenado BCRA, con auditoría y sin imponerles un trámite oneroso; y
16. se tenga presente la reserva del caso federal por encontrarse comprometidos los artículos 18, 42 y 43 de la Constitución Nacional.

**Proveer de conformidad,  
SERÁ JUSTICIA.**

---

## 13. Matriz de afirmaciones: qué está probado y qué falta

| Afirmación | Estado V0.7 | Evidencia actual | Paso para robustecerla |
|---|---:|---|---|
| Existe una serie agregada completa desde enero de 2023 hasta julio de 2026. | Sostenida como cálculo verificable | 43 meses de TNA BCRA + IPC INDEC + instrucciones de cálculo | Extenderla mensualmente y contrastar revisiones de las fuentes. |
| La tasa real TEA promedio fue positiva en 2023, negativa en 2024 y positiva en 2025–2026. | Sostenida a nivel agregado | Serie mensual y resumen anual acompañados | Desagregar por entidad, producto, riesgo, volumen y contrato; no inferir cobros individuales. |
| La deuda personal bancaria tuvo costo real positivo en julio de 2026. | Sostenida a nivel agregado | TNA BCRA + IPC INDEC + cálculo verificable | Repetir por entidad y producto. |
| El CFT puede ser mucho mayor que la TNA. | Sostenida conceptual e históricamente | Definición BCRA + IIF 2023 | Recolectar contratos/ofertas 2023–2026 por banco. |
| Existen ofertas bancarias vigentes con CFTEA máximos de varios cientos y, en casos extremos declarados, miles por ciento. | Sostenida como oferta reportada | Dos copias oficiales independientes preservadas el 30/08/2026 | Autenticar por oficio y obtener cantidad de contratos/tasas aplicadas. |
| Determinadas tasas fueron desproporcionadas según art. 771. | A demostrar | Indicios agregados | Comparador homogéneo y pericia por riesgo/plazo. |
| Hubo información omitida o cargos indebidos. | No demostrada en abstracto | Marco legal | Muestra de contratos, estados y reclamos. |
| El sistema bancario tuvo rentabilidad contable agregada positiva en los siete cortes examinados. | Sostenida en agregado para septiembre y diciembre de 2023; junio y diciembre de 2024; junio y diciembre de 2025; mayo de 2026 | Resultado neto estimado y ROA AA000 BCRA | Completar los meses intermedios y conciliar con estados auditados; no atribuir el resultado a personales sin contabilidad de cartera. |
| Existe una trayectoria contable pública por banco desde 2023. | Sostenida para siete cortes | Archivos abiertos BCRA de septiembre y diciembre 2023; junio y diciembre 2024; junio y diciembre 2025; mayo 2026 | Agregar cortes mensuales faltantes y controlar fusiones, cierres y cambios de código. |
| Puede medirse ingreso bruto por intereses de préstamos personales. | Sostenida por entidad y corte | Cuentas 511107 y 515107 del balance detallado BCRA | Validar devengamiento, transferencias de cartera y conciliación con notas auditadas. |
| La participación de personales en el activo creció y la irregularidad de consumo se deterioró desde 2025. | Sostenida en el agregado AA000 | Serie contable 2023–2026 | Deflactar saldos y desagregar altas, refinanciaciones y castigos por entidad. |
| La cobertura de préstamos personales aumentó dentro de cada tramo metodológico. | Sostenida | Base CENDEU por asistencia | No comparar junio/julio 2024 sin tratar el cambio de umbral de $1.000 a $25.000. |
| En las 46 entidades cotejadas, 32 tuvieron resultado neto estimado positivo y 14 negativo a mayo de 2026. | Sostenida como cálculo verificable | Información oficial BCRA + planilla conciliada por código de entidad | Validación pericial de ORI, unidades y cambios societarios. |
| La cartera de préstamos personales produjo ganancia neta extraordinaria. | No demostrada | Ninguna fuente pública suficiente | Contabilidad por cartera/cohorte y pericia. |
| El BCRA conserva para 2023–2026 CFT, monto y cantidad de préstamos efectivamente desembolsados por tramo. | No demostrada; antecedente identificado | Comunicación “A” 5402 de 2013 | Verificar vigencia/sustitución y pedir retención y presentaciones por oficio o acceso a información. |
| Toda brecha tasa–inflación fue ganancia bancaria. | Refutada como método | Mora, previsiones y costos | No utilizar esta afirmación. |
| Existió usura penal. | Hipótesis condicionada | Ninguna prueba subjetiva suficiente | Víctimas, segmentación, urgencia conocida, documentos internos. |
| CCT equivale a embargo sin juicio. | Refutada jurídicamente | Normativa BCRA + régimen de embargo judicial | Investigar sólo débitos sin consentimiento o revocación. |
| Las entidades poseen registros aptos para probar un patrón de reclamos y reintegros. | Sostenida como deber regulatorio | TO BCRA PUSF: RCCR, RRI, RDJA, reportes y auditoría | Obtenerlos del banco y BCRA; conciliar y controlar reclasificaciones. |
| Un cobro indebido detectado obliga a buscar y reintegrar a otros usuarios en igual situación. | Sostenida como regla regulatoria | TO BCRA PUSF 2.3.5.1 | Probar el evento generador y el universo; articular con sentencia colectiva. |
| El CFTEA 13.476,52% de Masventas fue efectivamente cobrado. | No demostrada | Oferta máxima declarada al BCRA | Contratos completados, movimientos, fórmula, altas y autenticación. |
| Existe una discrepancia pública entre el extremo BCRA de Masventas y su tarifario posterior. | Sostenida documentalmente | Declaración BCRA 08/06/2026 + tarifario propio vigente 05/08/2026 | Explicar productos, vigencia, alcance, rectificaciones y contratos. |
| Los reclamos BCRA prueban una tasa de infracción bancaria. | No sostenida | Estadística consolidada de reclamos y resolución | Usarla sólo como mapa probatorio; obtener denominadores y desglose por demandada/producto. |

---

## 14. Anexo pericial económico-financiero

### 14.1. Serie histórica enero de 2023–julio de 2026

| Año | Meses observados | TNA promedio | TEA calculada promedio | Inflación interanual promedio | Tasa real TEA promedio | Mínimo mensual real | Máximo mensual real |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 12 | 102,3355% | 171,0496% | 127,9481% | +18,3250% | +5,5994% | +37,4679% |
| 2024 | 12 | 85,9148% | 136,3171% | 236,8022% | −29,2163% | −49,9844% | +2,7118% |
| 2025 | 12 | 73,4569% | 104,1849% | 44,4672% | +43,2728% | +7,9810% | +70,2878% |
| 2026 | 7 | 67,8971% | 93,5823% | 32,9986% | +45,5596% | +41,6759% | +48,0752% |

Los valores anuales son promedios de magnitudes calculadas para cada mes; 2026 comprende sólo enero–julio. No representan el costo de un contrato anual ni una media ponderada por saldo o cantidad de deudores. La planilla mensual conserva además el volumen nominal BCRA y una estimación auxiliar de CFTEA con IVA, siempre rotulada como no contractual.

### 14.2. Corte julio de 2026

| Indicador | Valor | Naturaleza |
|---|---:|---|
| TNA promedio préstamos personales | 65,7100% | Observado BCRA |
| TEA de interés, capitalización mensual | 89,5988% | Cálculo desde TNA |
| IPC nacional, variación 12 meses | 33,8257% | Cálculo desde serie INDEC |
| Tasa real anual sobre TEA de interés | 41,6759% | Cálculo Fisher |
| CFTEA estandarizado con IVA sobre interés | 115,9462% | Estimación auxiliar |
| Tasa real anual de la estimación | 61,3638% | Cálculo; no contractual |

### 14.3. Fórmulas

```text
TEA_interés = (1 + TNA/12)^12 - 1
tasa_real_anual = (1 + TEA_interés) / (1 + inflación_12m) - 1
CFTEA_auxiliar = (1 + (TNA/12) × 1,21)^12 - 1
tasa_real_CFTEA_auxiliar = (1 + CFTEA_auxiliar) / (1 + inflación_12m) - 1
```

### 14.4. Qué no sumar

No se suman TNA, CFT y ROA. Tampoco se multiplica la brecha porcentual por cualquier saldo sin respetar flujos, amortización, mora y período. La planilla de trabajo incluye una referencia teórica de costos, riesgo y margen que **no es una tasa legal ni un cálculo de daños**.

### 14.5. Corte por banco del Régimen de Transparencia — 30/08/2026

| Métrica descriptiva | Resultado |
|---|---:|
| Registros totales coincidentes en las dos copias oficiales | 2.404 |
| Líneas bancarias en pesos con CFTEA positivo | 505 |
| Bancos identificados por el criterio de selección | 46 |
| CFTEA mínimo entre líneas | 28,07% |
| Mediana no ponderada | 159,12% |
| Percentil 75 no ponderado | 234,82% |
| Percentil 90 no ponderado | 373,07% |
| CFTEA máximo declarado | 13.476,52% |

La planilla acompañada conserva las 505 observaciones, no sólo los extremos. Añade la brecha CFTEA–TEA y una conversión real contra el IPC de julio de 2026. Esta última es un control analítico y no reemplaza la comparación jurídica del artículo 771 CCyC.

### 14.6. Cruce contable de las 46 entidades

| Métrica | Resultado | Corte |
|---|---:|---|
| Entidades con resultado neto estimado positivo | 32 | Resultado acumulado a mayo de 2026 |
| Entidades con resultado neto estimado negativo | 14 | Resultado acumulado a mayo de 2026 |
| Entidades positivas entre las diez de mayor CFTEA máximo | 3 | Ofertas al 30/08; resultados a mayo |
| Entidades negativas entre las diez de mayor CFTEA máximo | 7 | Ofertas al 30/08; resultados a mayo |

El resultado neto estimado resta el otro resultado integral cuando éste está informado. La planilla conserva también saldo de préstamos personales, activos, previsiones y los indicadores de ROA, ROE, tasa implícita de préstamos, margen financiero, incobrabilidad e irregularidad de consumo. Los balances cierran en mayo de 2026 y los indicadores en marzo de 2026. Las ofertas tienen fechas de actualización heterogéneas; por ello, el cotejo es exploratorio y no causal.

### 14.7. Panel contable público 2023–2026

El panel longitudinal contiene **523 filas entidad–corte** y siete fechas: septiembre y diciembre de 2023; junio y diciembre de 2024; junio y diciembre de 2025; y mayo de 2026. Para cada fila extrae, mediante código de cuenta y no por búsqueda textual:

1. resultado integral y otro resultado integral;
2. resultado neto estimado sin ORI;
3. saldo de préstamos personales;
4. intereses por préstamos personales en pesos y moneda extranjera —511107 + 515107—;
5. ingresos y egresos financieros totales;
6. cargo por incobrabilidad, ingreso por servicios y gastos de administración; y
7. ROA, ROE, tasa implícita, margen, incobrabilidad e irregularidad de consumo.

El control principal compara la suma de resultados estimados por entidad con el agregado oficial AA000. La diferencia fue cero en septiembre de 2023, diciembre de 2024, diciembre de 2025 y mayo de 2026; 0,01% en diciembre de 2023; 0,23% en junio de 2024; y −1,17% en junio de 2025. Las diferencias intermedias quedan conservadas y pueden deberse a cortes validados, entidades faltantes o consolidación; no fueron forzadas a cero.

| Corte | Entidades | Resultado positivo | Resultado negativo | Personales / activo AA000 | Interés bruto personales / ingreso financiero sumado | Irregularidad consumo AA000 |
|---:|---:|---:|---:|---:|---:|---:|
| Sep. 2023 | 77 | 55 | 22 | 2,62% | 3,01% | 3,05% |
| Dic. 2023 | 77 | 53 | 23 | 1,95% | 2,61% | 2,75% |
| Jun. 2024 | 76 | 48 | 27 | 2,53% | 2,53% | 2,73% |
| Dic. 2024 | 74 | 53 | 21 | 4,75% | 4,31% | 2,51% |
| Jun. 2025 | 73 | 53 | 19 | 6,40% | 13,64% | 5,03% |
| Dic. 2025 | 73 | 49 | 24 | 6,23% | 13,65% | 9,18% |
| May. 2026 | 73 | 50 | 23 | 6,31% | 13,57% | 12,58% |

En diciembre de 2023 y junio de 2024 hubo además una entidad con resultado exactamente cero según el criterio aplicado. Los ingresos y resultados semestrales o de mayo son acumulados al mes indicado; no se anualizaron. Las cifras nominales no se comparan entre años como crecimiento real.

### 14.8. Reclamos públicos 2023–2025 y revisiones

Los informes anuales permitieron extender el mapa de reclamos, pero revelaron revisiones y ventanas distintas:

| Publicación | Ventana informada | Reclamos del sistema | Resolución favorable total | Resolución favorable “Préstamos” |
|---|---|---:|---:|---:|
| Informe 2023 | Diciembre 2023 | 604.004 | 71% | N/D en el cuadro principal |
| Informe 2024 | Diciembre 2023 revisado | 637.314 | 70% | 59% |
| Informe 2024 | Diciembre 2024 | 703.175 | 66% | 83% |
| Informe 2025 | Promedio mensual 2025 | 769.500 | 64% | 60% |

El informe 2025 reproduce además 74% para “Préstamos” en 2024, cifra anual que no debe confundirse con el 83% del corte diciembre de 2024. La diferencia de 33.310 reclamos entre las dos publicaciones para diciembre de 2023 evidencia actualización del universo —principalmente proveedores de pagos— y obliga a citar versión y ventana. “Resolución favorable” describe el desenlace informado por sujetos obligados; no equivale a sentencia, infracción comprobada ni admisión de responsabilidad. La búsqueda pública no produjo el desglose necesario por banco, préstamo personal, versión contractual y causa; ese vacío permanece para oficio y exhibición.

### 14.9. Control cruzado específico de Masventas

| Fuente | Fecha/vigencia | Producto | CFTEA con IVA máximo visible |
|---|---:|---|---:|
| Régimen de Transparencia BCRA | Información 08/06/2026 | Convenios VGA/AMPROMM, 12 meses | 13.476,52% |
| Tarifario público Banco Masventas | Vigencia 05/08/2026 | Préstamos personales listados, cuenta sueldo/cliente general | 274,40% |

Las fuentes no prueban la misma línea ni la misma vigencia. La razón aproximada de 49,1 veces cuantifica la discrepancia pública, no un daño. El control correcto requiere recuperar el tarifario de junio, definir VGA/AMPROMM, reconstruir el cálculo para el capital de referencia y verificar contratos efectivamente celebrados.

---

## 15. Documentación digital acompañada y control de integridad

El siguiente inventario asigna una identificación forense provisoria a cada pieza. Al presentar la demanda deberá reemplazarse por la numeración definitiva de anexos, soporte, cantidad de páginas y constancia de obtención. La huella SHA-256 permite verificar que el documento examinado no cambió desde su preservación; **no prueba por sí sola su autenticidad, autoría ni veracidad**, cuestiones que se acreditarán mediante fuente oficial, oficio o reconocimiento. Los enlaces insertos en el nombre son sólo una facilidad de consulta de este borrador y no forman parte de la terminología de la presentación judicial.

| Anexo propuesto | Contenido y uso | SHA-256 |
|---|---|---|
| [E-1 — Serie BCRA de tasas](../01_FUENTES_ESTADISTICAS/E-1__preser_tas.xls) | Tasas y montos mensuales de préstamos personales | `063ba84b46b8c57162d3c9a87c722b2dc8cd3ca37a98c16105b55a4e5f4b9f53` |
| [E-2 — Serie INDEC de precios](../01_FUENTES_ESTADISTICAS/E-2__serie_ipc_divisiones.csv) | IPC nacional oficial | `2780c4d7ea3d7058c4042a275643d757a6bfaf55824a9ab1c540b59adc9033b4` |
| [E-3 — Informe de Inclusión Financiera 2023](../01_FUENTES_ESTADISTICAS/E-3__IIF-primer-semestre-2023.pdf) | CFT máximo ofrecido, gráfico 18 | `dbefef024f4a3c50ee006606059695b7545285cc0baee7c14c80a46d025d7972` |
| [C-1 — Serie analítica general](../02_CALCULOS_Y_METODOLOGIA/C-1__brecha_costo_credito_vs_cftea_referencia_2019_2026.csv) | Cálculos mensuales y estimación auxiliar de CFTEA | `1545c08643086726a8ea3ca076e6343774992c4c14372fc6e8fb2f4735740346` |
| [C-2 — Serie mensual 2023–2026](../02_CALCULOS_Y_METODOLOGIA/C-2__costo_credito_personal_historia_2023_2026.csv) | Cuarenta y tres observaciones mensuales verificables | `b56f8803de8e7bb59aee4780852ab308f2e561a2fe836be62f8b19eed9edfbf2` |
| [C-3 — Resumen anual 2023–2026](../02_CALCULOS_Y_METODOLOGIA/C-3__costo_credito_personal_resumen_anual_2023_2026.csv) | Promedios descriptivos de la serie mensual | `0136a7f10c7577e46e5dfcb90e841c1bff28321f9cdda5464652c68f238d76c8` |
| [C-4 — Instrucciones automatizadas de cálculo](../02_CALCULOS_Y_METODOLOGIA/C-4__build_credit_cost_history_2023_2026.ps1) | Regla exacta para regenerar C-2 y C-3 | `ca7c61083ac524a0659605b69be9fe7bc7c87c1a7f3cdf4054730bf3324bf7d1` |
| [M-1 — Memoria de metodología](../02_CALCULOS_Y_METODOLOGIA/M-1__AUDITORIA_CFTEA_REFERENCIA_Y_CARGA_CREDITO.md) | Alcance, supuestos y límites del cálculo | `7d4e27a3d728152d350574286073beda929a6736604badbb6f03b04767d1cefa` |
| [E-4 — Indicadores agregados de rentabilidad](../02_CALCULOS_Y_METODOLOGIA/E-4__bank_roa_snapshot_may2026.csv) | ROA oficial reconstruido por grupo | `d4790964b98cd68f2217205473a202e1b8d1799db3a3c2180f626dfedbd02da5` |
| [M-2 — Memoria de rentabilidad y CFT](../02_CALCULOS_Y_METODOLOGIA/M-2__AUDITORIA_CFT_RENTABILIDAD_V146.md) | Reglas de interpretación y controles | `8b2869c6b84a8b035d26b545c5b67c0e47e2ba244fa5dfc6f70ba15170991ae5` |
| [I-1 — Inventario general de fuentes](../08_INVENTARIO/I-1__FUENTES.csv) | Procedencia, fecha de obtención y huellas digitales | `e0619ee158028769719c6f720062b97b1812706b5d21b8d56140e230e3126871` |
| [T-1 — Primera copia del Régimen de Transparencia](../03_REGIMEN_DE_TRANSPARENCIA/T-1__prestamos_personales_api.json) | Declaraciones oficiales; 2.404 registros | `aab38581025d5b23e6285e702de4c6c2fde5cafcf7fa9f0ecebd4d147f259cfe` |
| [T-2 — Segunda copia del Régimen de Transparencia](../03_REGIMEN_DE_TRANSPARENCIA/T-2__PERSONALES.CSV) | Control independiente; 2.404 registros | `47c10e8023af4ddd2f45fd02a5aa1f5199520943870076fd20866c87487ebef0` |
| [T-3 — Diccionario oficial de campos](../03_REGIMEN_DE_TRANSPARENCIA/T-3__regimen-transparencia-v1.pdf) | Definiciones del Régimen de Transparencia | `3bfd512aa276dbe0142a22e0ca3c01a854f3b2b4e2e0af1252de77744e9021f9` |
| [T-4 — Selección de líneas bancarias](../03_REGIMEN_DE_TRANSPARENCIA/T-4__bcra_transparencia_bancos_prestamos_personales_2026-08-30.csv) | 505 líneas bancarias en pesos | `e59cb7e2899b2a5c0b74ea44c80bb1880805cc7b2356a366bc947d80b1bf7128` |
| [B-1 — Estados e indicadores por entidad](../04_BALANCES_BCRA/B-1__202605d.7z) | Balances, resultados e indicadores oficiales | `8163067025fb9be8b1fe37472ffcbebd72bc114122466ea8cd8a30ea2ccbf1a0` |
| [B-2 — Cotejo de ofertas y resultados](../04_BALANCES_BCRA/B-2__bcra_bancos_ofertas_y_resultados_2026-08-30.csv) | Planilla analítica de 46 bancos | `e3acb4f5f390095e1d1d4f0a2c488cdd2d1be2e1d55248ea4893dd1edbdcd04d` |
| [B-3 — Instrucciones de conciliación](../04_BALANCES_BCRA/B-3__build_bcra_bank_profitability_crosscheck.ps1) | Regla exacta del cotejo B-2 | `c8c3771c8282a9a6b34326140319018f2772df486c52002972afea823fa8215a` |
| [B-4 — Entidades septiembre de 2023](../04_BALANCES_BCRA/B-4__202309d.7z) | Archivo abierto mensual BCRA | `31a0a315444496d4336695b6bd48deb562456df10e47fbc46de3703a77528bdb` |
| [B-5 — Entidades diciembre de 2023](../04_BALANCES_BCRA/B-5__202312d.7z) | Archivo abierto mensual BCRA | `60ef86addba5e6646a2bfd42853ca077ea7970e9fa6effe54f1179049868f0d4` |
| [B-6 — Entidades junio de 2024](../04_BALANCES_BCRA/B-6__202406d.7z) | Archivo abierto mensual BCRA | `316c6c80f1206b08e13753bb4ac8b8ffe6239fbbf523dc7bddf9154e0e95385d` |
| [B-7 — Entidades diciembre de 2024](../04_BALANCES_BCRA/B-7__202412d.7z) | Archivo abierto mensual BCRA | `e0e80ca4ec62c9f517fe4540a125da5dfc9677f61d17cf2f06955bc16e49c07d` |
| [B-8 — Entidades junio de 2025](../04_BALANCES_BCRA/B-8__202506d.7z) | Archivo abierto mensual BCRA | `ed092702b18e24852df9d59d72b3956de3244081ebaf746d92d43de424027640` |
| [B-9 — Entidades diciembre de 2025](../04_BALANCES_BCRA/B-9__202512d.7z) | Archivo abierto mensual BCRA | `948af2d9eed7648e923a59c8ef194b5ce4a2ebc6d61ffec91a26bafb8b1e5c4b` |
| [B-10 — Panel bancario longitudinal](../02_CALCULOS_Y_METODOLOGIA/B-10__bcra_panel_bancos_2023_2026.csv) | 523 observaciones entidad–corte, con saldos, resultados e intereses personales | `a51b18b6787e2adf46367cdd8e588f1446f2a5172c29a478b8e6ae3a512c7a3d` |
| [B-11 — Resumen y conciliación del panel](../02_CALCULOS_Y_METODOLOGIA/B-11__bcra_panel_bancos_resumen_2023_2026.csv) | Universos, signos del resultado y control contra AA000 | `fbc179d0fa633ba02ae02acae1f7c0c4140399ef1873f02f98673682c75f3c1c` |
| [B-12 — Agregado del sistema AA000](../02_CALCULOS_Y_METODOLOGIA/B-12__bcra_sistema_financiero_2023_2026.csv) | Participación de personales, rentabilidad y riesgo en siete cortes | `4c231a99d4b1201e6629ac4fc9216f2726d1597e603f4b0805a14ea3a08548e7` |
| [B-13 — Instrucciones del panel longitudinal](../02_CALCULOS_Y_METODOLOGIA/B-13__build_bcra_historical_bank_panel.ps1) | Regla reproducible de extracción y conciliación | `0a191f7796283a0ea5a6a0cab1a1981d5d572028b486d6952c3fdb6f2b6ad7d0` |
| [IIF-1 — Base de asistencia crediticia](../05_INCLUSION_FINANCIERA/IIF-1__inclusion-financiera-deudores-sistema-financiero-ampliado-tipo-asistencia.txt) | Personas con préstamos personales y población adulta, por mes | `05ce35cd80e34800f72e1851a8d3f9832e0536886cbd1c00c8458bb8e12e6df6` |
| [IIF-2 — Base por edad](../05_INCLUSION_FINANCIERA/IIF-2__inclusion-financiera-deudores-sistema-financiero-ampliado-asistencia-rango-etario.txt) | Cobertura por asistencia y tramo etario | `702fbc43ed6accf1c280ff95c4a9c2e13be6e4cb973a78581647bbc70037e3ef` |
| [IIF-3 — Base por proveedor](../05_INCLUSION_FINANCIERA/IIF-3__inclusion-financiera-deudores-sistema-financiero-ampliado-grupo-institucional.txt) | Cobertura por grupo institucional | `e86c4e8811cd2038f6de3b1012c7931591474ba77cd118bcc44c879e0c9e253e` |
| [IIF-4 — Serie de cobertura de préstamos personales](../02_CALCULOS_Y_METODOLOGIA/IIF-4__bcra_inclusion_prestamos_personales_2023_2025.csv) | Cobertura mensual con separación explícita del quiebre de julio de 2024 | `c999bf10c70b8a2a019c790af9c46fb7d3a2c64f53b0bb6d5b9e05932133aece` |
| [IIF-5 — Serie de cobertura por proveedor](../02_CALCULOS_Y_METODOLOGIA/IIF-5__bcra_inclusion_proveedores_2023_2025.csv) | Cobertura mensual superpuesta por tipo de proveedor | `e1a7466679aaf791ee0b1301cebac67479518c129a2f4ec6ae7603d4758e2300` |
| [IIF-6 — Cortes etarios de préstamos personales](../02_CALCULOS_Y_METODOLOGIA/IIF-6__bcra_inclusion_prestamos_personales_edad_cortes_2023_2025.csv) | Cobertura por edad en cortes seleccionados | `d243531ded77a20c819000446839d81caccac6f92c732940a77900016fc3a83d` |
| [IIF-7 — Instrucciones para las series de inclusión](../02_CALCULOS_Y_METODOLOGIA/IIF-7__build_bcra_inclusion_credit_data.ps1) | Regla reproducible y tratamiento del cambio de umbral | `171a60b1b6b20bb02367b4210242a84e4442a6c085882707a53d026f26c67156` |
| [N-1 — Protección de usuarios, texto vigente](../06_NORMATIVA_Y_RECLAMOS/N-1__t-pusf.pdf) | Contratos, información, registros y reintegros | `48564cc714daa9a8c8bbd7115dfe006307ca7cb1c3d78b106c52555fe75a12ec` |
| [N-2 — Tasas de crédito, texto vigente](../06_NORMATIVA_Y_RECLAMOS/N-2__t-tasint.pdf) | TEA, CFT, cargos y publicidad | `9c752ec8721020af1d21dba27266efff3a8edebf2d4e852fefdee18cbe1eb43e` |
| [N-3 — Comunicación BCRA “A” 7744](../06_NORMATIVA_Y_RECLAMOS/N-3__A7744.pdf) | Hito regulatorio histórico 2023 | `d7651de395bd0e383890cde960d433088118e0de0b03680f72dd88ba19e8068c` |
| [N-4 — Comunicación BCRA “A” 8203](../06_NORMATIVA_Y_RECLAMOS/N-4__A8203.pdf) | Hito regulatorio histórico 2025 | `600603a3345514bd93a65268d21eab91441b9f0867de5d100c6aed91d2c7acbb` |
| [N-5 — Comunicación BCRA “A” 8433](../06_NORMATIVA_Y_RECLAMOS/N-5__A8433.pdf) | Hito regulatorio histórico 2026 | `32da719e7455704bdd72cb31a81e2853214903760848f5986c474510579ce5e5` |
| [N-6 — Informe anual de usuarios 2025](../06_NORMATIVA_Y_RECLAMOS/N-6__informe-anual-pusf-2025.pdf) | Reclamos, resoluciones y alcance | `ae57555690b0df659a333ac57bfb99b607ec6f95e6d2a9050b8b27695f34a1ca` |
| [N-7 — Marco institucional de usuarios 2025](../06_NORMATIVA_Y_RECLAMOS/N-7__marco-general-pusf-2025.pdf) | Organización del sistema de protección | `4e4cc1c763f122dc064c318ab8866bb431d40ef51c95e41a8bcf6c12f06eda0b` |
| [N-8 — Comunicación BCRA “A” 5402](../06_NORMATIVA_Y_RECLAMOS/N-8__A5402.pdf) | Antecedente del régimen mensual sobre CFT de préstamos efectivamente desembolsados | `6a2596b4d326f685aacc862c5adcfb4e3f2802a25957f92f01e67c9f7d1a1e82` |
| [R-1 — Informe anual de usuarios 2023](../06_NORMATIVA_Y_RECLAMOS/R-1__PUSF-Informe-2023.pdf) | Reclamos reportados, resolución y universo publicado inicialmente | `f5f360578a1b3ee77b7407845b96a15629f6b7ea1bcfc7db3bac8847b391a170` |
| [R-2 — Informe anual de usuarios 2024](../06_NORMATIVA_Y_RECLAMOS/R-2__PUSF-Informe-2024.pdf) | Revisión del corte 2023 y resultados de 2024 | `d6ebb13fb20fddd7c53f44c7964fc1552990dca4f045346f5417bebd0929786d` |
| [MV-1 — Formulario público de préstamo](../07_CASO_MASVENTAS/MV-1__F0132-SOLICITUD-PRESTAMOS-PERSONALES.pdf) | Modelo histórico F.0132 | `bef977b75f783f50ac7b099e206c1555ade2a281b48b0b9e5bd1df87a23337e5` |
| [MV-2 — Resumen público de préstamo](../07_CASO_MASVENTAS/MV-2__Resumen-Solicitud-Prestamo-Personal-F0268-012023.pdf) | Modelo genérico F.0268 | `e6007e6a65cf86cedb552a6d5ba8b6d0b615df7c21bebbfcbd9d0fe567e96bc6` |
| [MV-3 — Tarifario institucional](../07_CASO_MASVENTAS/MV-3__TASAS-05-08-2026.pdf) | Vigencia declarada desde 05/08/2026 | `c881e1e52a5545677194ee9f851f4c5c71c895fe85d349f5b990d0e7d0fe7874` |
| [MV-4 — Página institucional de origen](../07_CASO_MASVENTAS/MV-4__pagina-tasas-interes-cft-2026-08-30.html) | Constancia del enlace al tarifario | `3d764da0d39b7f53f4b2858abb6818283acf73637c5cc15decf3fc248d3425ed` |
| [MV-5 — Constancia del enlace obsoleto](../07_CASO_MASVENTAS/MV-5__respuesta-descarga-TASAS-04-06-26.html) | Control del intento de recuperación anterior | `39c7674e67118760089894bf956cd8bf6b2d9de6acd6e0c77b158325453b2223` |

---

## 16. Fuentes jurídicas y estadísticas oficiales

### Normativa

- [Constitución Nacional, texto oficial — arts. 42 y 43](https://www.argentina.gob.ar/normativa/nacional/804/texto).
- [Ley 24.240 de Defensa del Consumidor, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/ley-24240-638/actualizacion): arts. 4, 8 bis, 35–38 y 52–55.
- [Código Civil y Comercial, Ley 26.994, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/ley-26994-235975/actualizacion): arts. 9, 10, 770, 771, 984–989, 1092–1122 y 1384–1389.
- [Código Civil y Comercial, texto actualizado — prescripción](https://www.argentina.gob.ar/normativa/nacional/ley-26994-235975/actualizacion): arts. 2554 y 2560–2563; el art. 2560 fue modificado por Ley 27.799 con vigencia 02/01/2026.
- [Código Penal, texto actualizado — art. 175 bis](https://www.argentina.gob.ar/normativa/nacional/16546/actualizacion).
- [BCRA, Protección de los Usuarios de Servicios Financieros — texto ordenado vigente](https://www.bcra.gob.ar/archivos/Pdfs/Texord/t-pusf.pdf).
- [BCRA, Tasas de Interés en las Operaciones de Crédito — texto ordenado vigente](https://www.bcra.gob.ar/archivos/Pdfs/Texord/t-tasint.pdf).
- [BCRA, Comunicación “A” 7744 — versión histórica de 2023](https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A7744.pdf).
- [BCRA, Comunicación “A” 8203 — hito normativo de 2025](https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A8203.pdf).
- [BCRA, Comunicación “A” 8433 — hito normativo de 2026](https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A8433.pdf).
- [Acordada CSJN 32/2014 — Registro Público de Procesos Colectivos](https://www.csjn.gov.ar/documentos/descargar?ID=89518).
- [Registro y consulta de causas colectivas de la CSJN](https://w3.csjn.gov.ar/causas-en-tramite).

### Jurisprudencia colectiva

- [CSJN, “Halabi, Ernesto c/ PEN”, 24/02/2009, Fallos 332:111](https://www.csjn.gov.ar/archivo-cij/adj/pdfs/ADJ-0.734285001235492424.pdf).
- [CSJN, “PADEC c/ Swiss Medical S.A.”, 21/08/2013, Fallos 336:1236 — compendio oficial](https://sj.csjn.gov.ar/homeSJ/suplementos/suplemento/64/documento).
- [CSJN, “Consumidores Financieros Asociación Civil para su defensa c/ Banco Itaú Buen Ayre Argentina S.A.”, 24/06/2014, Fallos 337:753](https://www.csjn.gov.ar/archivo-cij/adj/pdfs/ADJ-0.931542001403618661.pdf).
- [CSJN, “Prevención, Asesoramiento y Defensa del Consumidor c/ BankBoston N.A.”, 14/03/2017, Fallos 340:172 — tomo oficial](https://sjconsulta.csjn.gov.ar/sj/verTomo?tomoId=428): vulnerabilidad estructural en contratos bancarios, control judicial aun ante aprobación del BCRA y falta de saneamiento por consentimiento tácito.

### Jurisprudencia de fondo e información en crédito de consumo

Los siguientes son fallos de cámaras provinciales: resultan persuasivos y específicos, pero no constituyen una regla nacional automática.

- [Cám. Civ. y Com. San Isidro, Sala I, “Banco Macro S.A. c/ Fraschini”, 26/12/2018](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=165516): ante la omisión de la TEA, confirmó la aplicación de la tasa pasiva anual promedio prevista por el artículo 36 LDC.
- [Cám. Civ. y Com. Mar del Plata, Sala II, “Finanpro S.R.L. c/ Alcaire Petto”, 09/10/2019](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=173519): exigió comparar operaciones semejantes; redujo compensatorios de una financiera no bancaria y ordenó aplicarlos sobre saldo, no sobre capital ya amortizado. El fallo registró además omisión del CFT en el título.
- [Cám. Civ. y Com. San Martín, Sala III, “Banco de la Provincia de Buenos Aires c/ Correa”, 22/05/2025](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=195069): por mayoría declaró inhábil el título ejecutivo porque no discriminaba de modo suficiente el monto y composición de los pagos, aun cuando mencionaba CFT y sistema de amortización.
- [Cám. II Civ. y Com. La Plata, Sala I, “Banco de la Provincia de Buenos Aires c/ Mugnolo”, 06/03/2025](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=194261): distinguió capital actualizado por CER de deuda nominal y morigeró la tasa pura del crédito UVA, mostrando que moneda y mecanismo de ajuste son indispensables para el test del artículo 771.
- [Cám. Civ. y Com. Azul, Sala II, “Credifín Azul S.R.L. c/ Montenegro”, 10/07/2019](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=170255): confirmó el rechazo de la ejecución frente a documentación contradictoria y abuso del proveedor; extendió la tutela consumeril a la fiadora de la operación de consumo.
- [SCBA, “Asociación Mutual Asís c/ Cubilla, María Ester”, causa C. 121.684, 14/08/2019](https://juba.scba.gov.ar/VerTextoCompleto.aspx?idFallo=170993): doctrina legal sobre integración del pagaré con la documentación causal, control del artículo 36 LDC y revisión de intereses por abuso o desproporción conforme al artículo 771 CCyC.
- [CNCom., Sala B, “Custo, Leandro c/ Banco Santander Río S.A.”, expediente 3455/2021, 03/09/2025](https://www.csjn.gov.ar/tribunales-federales-nacionales/d/sentencia-SGU-b853a037-e70e-4ba7-afb8-0542c3d7e2b8.pdf): en una relación bancaria de consumo aplicó el deber probatorio del artículo 53 LDC y valoró la falta de legajo y de pericia contable contra el banco; es pertinente para exhibición y carga dinámica, no para fijar una tasa justa.

### Estadística y regulación financiera

- [BCRA, serie oficial de tasas mensuales de préstamos personales](https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/preser_tas.xls).
- [BCRA, Boletín Estadístico de julio de 2026](https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/BoletinEstadistico/boldat202607.pdf).
- [BCRA, cómo comparar préstamos personales y qué contiene el CFT](https://www.bcra.gob.ar/prestamos-personales-comparar-costos-y-condiciones/).
- [BCRA, Informe de Inclusión Financiera — primer semestre de 2023](https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/IIF-primer-semestre-2023.pdf).
- [BCRA, Informe de Inclusión Financiera — segundo semestre de 2023](https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-segundo-semestre-2023/): alcance y saldo real de préstamos personales al cierre de 2023.
- [BCRA, Informe de Inclusión Financiera — primer semestre de 2024](https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-primer-semestre-2024/): expansión de prestatarios y saldo real hasta junio de 2024.
- [BCRA, Informe de Inclusión Financiera — segundo semestre de 2024](https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-segundo-semestre-del-2024/): cambio del umbral CENDEU desde julio de 2024 y métricas de regularidad.
- [BCRA, Informe de Inclusión Financiera — primer semestre de 2025](https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-primer-semestre-2025/): prestatarios, saldos reales y costo real del crédito personal.
- [BCRA, Informe de Inclusión Financiera — segundo semestre de 2025](https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-segundo-semestre-de-2025/): extensión de prestatarios hasta diciembre de 2025.
- [BCRA, bases abiertas de inclusión financiera](https://www.bcra.gob.ar/indicadores-inclusion-financiera/): deudores por asistencia, edad y grupo institucional.
- [BCRA, Informe sobre Bancos — mayo de 2026](https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-mayo-de-2026/).
- [BCRA, Informe sobre Bancos — diciembre de 2025](https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-diciembre-de-2025/): mora de hogares, previsiones y rentabilidad anual.
- [BCRA, información sobre entidades financieras y datos abiertos mensuales](https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/): estados e indicadores remitidos por cada entidad; su publicación no implica opinión del BCRA.
- [BCRA, Régimen de Transparencia de productos financieros](https://www.bcra.gob.ar/regimen-de-transparencia/): datos reportados por las entidades como declaración jurada y actualizados cuando cambian las condiciones.
- [BCRA, manual de la API de Régimen de Transparencia](https://www.bcra.gob.ar/archivos/Catalogo/Content/files/pdf/regimen-transparencia-v1.pdf): endpoint y campos de préstamos personales.
- [BCRA, Informe sobre Protección a las Personas Usuarias de Servicios Financieros 2025](https://www.bcra.gob.ar/publicaciones/informe-sobre-proteccion-a-las-personas-usuarias-de-servicios-financieros-2025/): reclamos de primera y segunda instancia, resolución favorable y límites del universo consolidado.
- [BCRA, Informe sobre Protección a las Personas Usuarias de Servicios Financieros 2023](https://www.bcra.gob.ar/publicaciones/informe-sobre-proteccion-a-las-personas-usuarias-de-servicios-financieros-2023/): primer corte anual preservado y advertencia sobre revisiones posteriores.
- [BCRA, Informe sobre Protección a las Personas Usuarias de Servicios Financieros 2024](https://www.bcra.gob.ar/publicaciones/informe-proteccion-personas-usuarias-2024/): revisión del universo de diciembre de 2023 y resultados por producto en 2024.
- [BCRA, Comunicación “A” 5402](https://www.bcra.gob.ar/Pdfs/comytexord/A5402.pdf): antecedente de declaración jurada mensual por tramos de CFT, monto, cantidad y TNA de préstamos personales efectivamente desembolsados; su vigencia o norma sucesora en 2023–2026 debe verificarse por oficio.
- [Banco Masventas, página institucional de tasas y CFT](https://www.bancomasventas.com.ar/Documentos/categoria/cargos-comisiones-y-tasas/tasas-de-interes-y-cft): origen del tarifario vigente preservado.
- [Banco Masventas, modelos públicos de préstamos personales](https://www.bancomasventas.com.ar/documentos/categoria/contratos/prestamos-personales): formulario F.0132 y resumen F.0268; modelos genéricos, no contratos individuales.
- [INDEC, serie oficial del IPC nacional](https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv).
- [BCRA, régimen de Cobro de Cuotas con Transferencia](https://www.bcra.gob.ar/noticias/cobro-cuotas-con-transferencia-cct/).
- [BCRA, Comunicación “A” 8406](https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A8406.pdf).
- [BCRA, oficios judiciales de embargo e inhibición](https://www.bcra.gob.ar/presentar-un-oficio-judicial-al-banco-central/).

---

## 17. Agenda de excavación para convertir el prototipo en una pieza probatoria fuerte

### Prioridad 1 — contratos reales e historia de versiones

- reunir al menos 30–50 contratos/altas por banco, producto y cohorte desde enero de 2023;
- preservar pantalla previa, contrato, comprobante, tabla de amortización y movimientos;
- recuperar todas las versiones de contratos, resúmenes, tarifarios y flujos digitales vigentes entre 2023 y 2026, con fechas de entrada y salida;
- anonimizar datos personales conservando un original bajo cadena de custodia;
- recalcular el CFT efectivamente pagado y comparar contra el informado.
- cruzar cada caso con número de reclamo, respuesta, eventual reintegro y clasificación en el RCCR/RRI/RDJA.

### Prioridad 2 — comparador del artículo 771

- preservar diariamente durante la primera semana y luego mensualmente el Régimen de Transparencia del BCRA por entidad/producto;
- requerir al BCRA el historial 2023–2026 que no aparece en la consulta pública actual y la identificación de toda norma sucesora de la Comunicación “A” 5402;
- pedir que informe si recibió y conserva, para cada entidad y mes de 2023–2026, monto, cantidad, TNA media y distribución por tramo de CFT de préstamos efectivamente desembolsados; si la respuesta es afirmativa, requerir copia desidentificada;
- construir celdas comparables por monto, plazo, garantía, canal y riesgo;
- identificar mediana, percentiles y persistencia de extremos;
- evitar un “techo justo” inventado: presentar sensibilidades y dejar la conclusión jurídica al tribunal.

### Prioridad 3 — ganancia neta por cartera

- completar los meses intermedios del archivo de estados e indicadores BCRA: ya se preservaron y procesaron siete cortes entre septiembre de 2023 y mayo de 2026;
- utilizar las cuentas públicas 511107 y 515107 como ingreso bruto por intereses de personales y conciliarlas con saldos, previsiones, mora y notas; no presentarlas como utilidad neta;
- solicitar por diligencia preliminar la contabilidad de gestión no pública;
- obtener fondeo, gastos, comisiones, recuperos, castigos y capital asignados por cartera/cohorte;
- estimar márgenes netos sólo cuando puedan conciliarse con estados auditados.

### Prioridad 4 — jurisprudencia de tasas e información bancaria

- relevar fallos de CSJN, cámaras nacionales y superiores tribunales provinciales sobre arts. 36 LDC, 771, 1388 y 1389 CCyC;
- registrar carátula, tribunal, sala, fecha, expediente, texto completo y firmeza;
- distinguir precedentes sobre admisibilidad colectiva de decisiones sobre el fondo;
- no usar resúmenes periodísticos como sustituto del fallo.

### Prioridad 5 — testimonios y patrón de vulnerabilidad

- documentar urgencia, ingresos, alternativas disponibles y comprensión de la oferta;
- registrar refinanciaciones, débitos, cobranza y reclamos;
- buscar patrón común sin exponer públicamente a las víctimas;
- usar esta prueba para trato indigno, aprovechamiento y eventual artículo 175 bis, no para reemplazar el análisis financiero.

---

## 18. Prueba de estrés y umbral para avanzar contra cada banco

Antes de incluir una entidad como demandada, el equipo deberá completar una ficha de decisión. La acción no avanza por reputación, tamaño, rentabilidad agregada ni tasa máxima publicada aisladamente.

### 18.1. Condiciones mínimas de avance

Debe existir, como mínimo:

1. **hecho común identificable:** una cláusula, pantalla, fórmula, cargo o práctica repetida y versionada;
2. **afectación real:** al menos casos testigo con contrato completado, cronograma y movimientos que demuestren aplicación o cobro;
3. **clase administrable:** banco, producto, versión y período definibles desde registros comunes;
4. **remedio vivo:** análisis separado de prescripción, exigibilidad y actos interruptivos;
5. **comparador defendible:** para artículo 771, operaciones semejantes y más de un escenario de sensibilidad;
6. **nexo contable:** si se alega beneficio, trazabilidad por cartera en lugar de ROA total;
7. **prueba bajo control de la demandada identificada:** documentos concretos cuya exhibición pueda ordenarse; y
8. **representación adecuada:** legitimado, ausencia de conflicto y plan de notificación/liquidación.

### 18.2. Semáforo probatorio

| Estado | Criterio | Decisión |
|---|---|---|
| Verde | Contrato tipo común + cobros efectivos + universo identificable + remedio no prescripto | Preparar demanda/diligencia preliminar específica. |
| Amarillo | Oferta o formulario público + inconsistencia objetiva, pero sin contratos o universo | Reclamos trazables, oficio, preservación y captación de casos; no acusar cobro. |
| Rojo | Sólo tasa agregada, captura de red social, ROA o diferencia contra inflación | No demandar con esa base; conservar como pista. |

Masventas permanece **amarillo**: la inconsistencia entre fuentes es fuerte y el rastro documental está identificado, pero faltan contratos completados bajo VGA/AMPROMM, tasas efectivamente aplicadas y universo. Una respuesta oficial que confirme contratos bajo el CFTEA extremo podría moverlo a verde; una rectificación documentada sin operaciones puede cerrar esa línea sin afectar otras hipótesis contractuales que se prueben.

### 18.3. Qué podría derrotar la demanda aun con tasas muy altas

- que el valor extremo sea un error de reporte nunca aplicado;
- que los contratos y resúmenes personalizados cumplan íntegramente y coincidan con cobros;
- que la cartera comparable justifique actuarialmente la diferencia;
- que no exista una versión/práctica común o que las diferencias individuales dominen el conflicto;
- que los remedios patrimoniales estén prescriptos para la cohorte elegida;
- que el representante no sea adecuado o ya exista un proceso colectivo superpuesto; o
- que el reclamo pretenda convertir una oferta máxima o una pérdida agregada del banco en una presunción automática de ilícito.

Anticipar estos resultados no debilita la denuncia: impide invertir recursos y legitimidad en una teoría que la prueba disponible no sostiene.

---

## 19. Regla de rigor probatorio del escrito

Cada afirmación nueva deberá clasificarse como:

- **hecho observado**;
- **cálculo verificable**;
- **inferencia**;
- **hipótesis a probar**; o
- **conclusión jurídica reservada al tribunal**.

No se publicará como “ganancia neta” una brecha de tasas. No se llamará “usura” a una diferencia frente al IPC sin analizar los elementos legales. No se llamará “embargo” a un débito consentido. La denuncia será más fuerte cuanto menos dependa de exageraciones y más obligue a la contraparte a responder con sus propios contratos y libros.
