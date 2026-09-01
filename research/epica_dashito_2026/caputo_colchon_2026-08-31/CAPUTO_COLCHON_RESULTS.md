# Resultados · preguntas sobre los “dólares del colchón”

Fecha de corte: **31/08/2026**.

## Síntesis de alcance

La intuición inicial de Miyu queda registrada en el Storytelling del dashboard. Este módulo la traduce a preguntas abiertas sobre distribución, alternativas de inversión, transmisión bancaria y objetivos de política. La frase suministrada se conserva como **paráfrasis de trabajo**: no fue localizada literalmente en las transcripciones oficiales revisadas. Sí se encontró el argumento de que los dólares fuera del sistema podrían entrar a los bancos, ampliar el crédito empresarial y, por esa vía, favorecer la actividad y el empleo.

El beneficio macroeconómico buscado y el incentivo privado del ahorrista son dimensiones diferentes. Al 27/08/2026, las referencias del BCRA eran 0,22% TNA para caja de ahorro USD y 2,05% para plazos de 60 días o más; la letra del Tesoro estadounidense a 52 semanas rendía 4,14% el 28/08/2026. La comparación es ilustrativa: antes de elegir hay que considerar comisiones, impuestos, custodia, liquidez, acceso y riesgo de precio.

La brecha bruta entre la T-Bill y el plazo fijo era **2,09 puntos porcentuales**. Ese es el costo incremental anual combinado que igualaría ambas referencias antes de diferencias tributarias individuales y riesgo de precio. El dataset de escenarios no estima comisiones reales: permite observar cómo cambia la comparación cuando el usuario explicita un supuesto de costo.

## Capacidad potencial para invertir

INDEC muestra que el 20% de mayores ingresos concentra 50,1% del ingreso corriente y el 40% inferior, 14,5%. Esto respalda la idea de una capacidad concentrada, pero no identifica quién posee dólares: la EPH mide ingresos, no riqueza ni efectivo atesorado. Como contexto, 71,778% de los hogares usó al menos una estrategia extraordinaria de sostenimiento en 2026-T1; tampoco es una medición directa de falta de ahorro.

La estadística bancaria por tramos agrega una pieza más cercana, aunque todavía no identifica personas únicas. En junio de 2026, al sumar cajas de ahorro y plazos fijos de personas físicas residentes en moneda extranjera, los instrumentos con saldo en el tramo de 10.000 o más representaban **1,14% de las cuentas-instrumento y reunían 77,89% del saldo**. El tramo de 100.000 o más representaba **0,067% de las cuentas-instrumento y 29,12% del saldo**. Una cuenta no es una persona: un mismo titular puede tener varias cuentas o ambos instrumentos, y el universo no incluye efectivo fuera del sistema. El resultado prueba concentración dentro de los depósitos bancarios observados, no cuántos argentinos tienen dólares para invertir.

La trayectoria histórica evita otra equivalencia engañosa. Entre diciembre de 2023 y junio de 2026 el stock combinado aumentó en 28,31 millones de cuentas-instrumento, pero sólo 336.516 de la variación neta correspondieron al tramo de 10.000 o más. Aritméticamente, **98,81% del aumento neto del número de cuentas quedó debajo de ese umbral**. Esto no prueba que hayan aparecido 28 millones de nuevos ahorristas: el stock mezcla aperturas, cierres y posibles cambios de reporte. Sí demuestra que “más cuentas” no puede leerse como “más personas con dólares invertibles”. Al mismo tiempo, la proporción del saldo en el tramo de 10.000 o más subió 7,77 puntos y la del tramo de 100.000 o más, 4,51 puntos: la base se amplió por abajo mientras la concentración del dinero se mantuvo alta y aumentó.

## Objetivos y mecanismos declarados

La cadena pretendida es: depósito USD → fondeo bancario → crédito a una empresa → liquidación del préstamo en el mercado de cambios → fondos en pesos/FX adicional → eventual inversión, empleo y recaudación. Cada flecha es contingente. Depositar no convierte automáticamente el dinero en reservas del BCRA ni en capital productivo.

El mapa reproducible separa siete etapas y, para cada una, registra evidencia disponible, estado y pregunta abierta. La presentación informa aproximadamente USD 40.300 millones de depósitos privados y estima USD 5.800 millones de capacidad crediticia disponible: por eso el análisis distingue stock bancarizado, fondeo potencial, decisión bancaria, demanda empresarial y resultado observado.

La profundización agrega una distinción decisiva. Los préstamos en dólares representaban 61% de los depósitos. Si se usa como referencia la práctica prudente histórica descripta por el propio ministro —prestar alrededor de 65% y mantener unos 10 puntos adicionales de liquidez además del encaje—, el margen calculado con los stocks redondeados es cercano a **USD 1.595 millones**. Si se usa el máximo regulatorio teórico de 75%, la estimación oficial asciende a **USD 5.800 millones**. “Capacidad ociosa” no tiene entonces un único valor: depende de si el comparador es una conducta prudente o el límite normativo.

## Auditoría de porcentajes y denominadores

Los porcentajes cercanos no forman una sola identidad contable. El IPOM informa que, en el promedio poselectoral hasta junio, 75% de los dólares comprados para atesoramiento quedó dentro del sistema financiero local, unos USD 1.100 millones por mes. En las palabras iniciales del 6 de agosto, el presidente del BCRA elevó la referencia a “aproximadamente 80%”, después de datos hasta julio, pero no publicó el puente de cálculo que permite reproducir el cambio. Ese 75% de retención local no tiene relación matemática con el otro 75%: el máximo teórico de depósitos que un banco podría prestar luego del encaje de 25%.

El resto de las referencias también usa perímetros distintos: 61% es préstamos privados sobre depósitos privados al 13 de agosto; 65% es una práctica prudente histórica; 17% es la capacidad prestable ociosa estimada por el IPOM en junio; y 48,6% es una medida más amplia de liquidez agregada en moneda extranjera del sistema bancario en junio. Por eso no corresponde sumar 61% y 48,6%, ni restar 17% de cualquiera de ellos. El archivo `percentage_denominator_audit.json` preserva numerador, denominador, fecha, alcance y advertencia de cada cifra.

## Banco local y mercado de capitales

El propio IPOM reconoce que el mercado de capitales es un canal alternativo para ofrecer al ahorrista doméstico una tasa competitiva en dólares. También explica por qué la política busca sostener el canal bancario: lo considera un sustituto imperfecto para financiar firmas de menor escala, con menos capacidad de cumplir exigencias de información pública y fuera de los centros con mayor profundidad de mercado. La discusión no es entonces “banco o comitente” como si uno fuera inválido. Para el ahorrista son opciones con rendimiento, liquidez, costos y riesgos diferentes; para la política cumplen funciones de originación y distribución distintas.

Según el IPOM, el mercado de capitales aportó en el primer semestre de 2026 financiamiento bruto equivalente a USD 20.000 millones y el segmento en dólares representó 43%. La cifra incluye ON, fideicomisos financieros, pagarés, cheques de pago diferido, facturas, acciones y fondos cerrados, valuados al MEP: no debe leerse como stock comparable con depósitos o préstamos bancarios.

## Qué líneas absorbieron el crédito en dólares

La API del BCRA permite abrir el stock por línea. Entre el 29/12/2023 y el 27/08/2026, los préstamos privados en dólares pasaron de USD 3.412 millones a USD 25.367 millones. Los **documentos a sola firma** explicaron USD 16.603 millones, o **75,62% del aumento total**, y representaban 74,07% del stock final. “Otros préstamos” explicaron 13,10% de la expansión; prendarios, 5,28%; hipotecarios, 2,73%; tarjetas, 2,03%; y otros adelantos, 1,12%.

Esto afina el destino financiero, pero todavía no identifica el sector productivo ni el uso final. “Documento a sola firma” es una forma contractual que puede financiar actividades diferentes. La evidencia muestra una expansión fuertemente comercial/documentaria, no que tres cuartas partes hayan ido a construcción, automotrices o inversión nueva.

## Qué actividades concentraban el stock

La planilla trimestral por actividad permite avanzar un paso, con corte anterior a la nueva medida. Al 30/06/2026, el stock de préstamos de efectivo en moneda extranjera ascendía a USD 24.145,64 millones. **Producción primaria reunía 42,38% e industria manufacturera 31,34%**: juntas concentraban **73,72%**. Comercio mayorista y minorista representaba 10,64%; servicios, 6,88%; electricidad, gas y agua, 5,77%; personas físicas en relación de dependencia, 2,01%; y construcción, apenas 0,60%.

La apertura siguiente muestra dónde estaba la masa principal: agricultura, ganadería, caza y silvicultura explicaban 27,01%; alimentos y bebidas, 15,10%; minería y canteras, 15,04%; y comercio mayorista, 9,41%. Entre marzo y junio, producción primaria explicó 47,71% del aumento del stock e industria, 28,39%. La concentración es consistente con el universo tradicional de firmas con ingresos vinculados al comercio exterior, pero la tabla clasifica por actividad principal del deudor y no por destino del dinero.

La estructura de prestamistas también estaba concentrada en bancos: los privados nacionales tenían 38,80% del stock, los extranjeros 36,89%, los públicos 22,47% y las entidades financieras no bancarias 1,84%.

## Quiénes concentraron las operaciones nuevas

La apertura mensual por tipo de prestatario aporta una aproximación al tamaño. En julio de 2026 se registraron USD 3.175,13 millones de operaciones brutas de préstamos de efectivo en moneda extranjera: **otras personas jurídicas concentraron 74,59%**, las personas jurídicas PyME 20,83% y las personas físicas 4,59%. En documentos a sola firma —USD 2.574,84 millones— las participaciones fueron 77,72%, 18,22% y 4,06%.

El contraste aparece también en monto y plazo. Para otras personas jurídicas, el tramo promedio ponderado de los documentos fue **USD 5–10 millones**, el plazo promedio 150 días y 53,49% del monto se concertó a menos de 90 días. Para PyMEs, el tramo promedio fue USD 0,5–0,75 millones, el plazo promedio 422 días y sólo 7,67% quedó debajo de 90 días. El tramo es un código ordinal ponderado, no un préstamo promedio ni una distribución de operaciones.

El patrón es compatible con financiamiento corporativo grande y de corto plazo, pero no prueba su uso. Un documento puede financiar capital de trabajo, comercio exterior, refinanciación, inventarios, sustitución de otra deuda o inversión. El BCRA no publica en estas tablas un cruce simultáneo entre actividad, tamaño, línea, proyecto y destino final.

## Demanda y condiciones antes de la medida

La Encuesta de Condiciones Crediticias de 2026-T2 agrega contexto sobre otro posible cuello de botella. Los bancos percibieron una caída de la demanda empresaria, más intensa en PyMEs (índice de difusión de -29,7%) que en grandes empresas (-16,4%). Para 2026-T3 esperaban una leve suba entre grandes empresas (11,7%), una nueva baja PyME (-9,4%) y estándares especialmente más restrictivos para PyMEs (-24,9%). A la vez, informaron menores spreads sobre el fondeo, pero plazos y garantías más restrictivos.

La encuesta no es específica de moneda extranjera y no debe combinarse contablemente con los flujos anteriores. Sí debilita una explicación de “sólo faltan depósitos”: demanda, elegibilidad, garantías y plazo también aparecen como restricciones observables.

## Tasa activa, tasa pasiva y margen ilustrativo

En julio de 2026, la tasa promedio de nuevas operaciones de documentos a sola firma en dólares fue 3,824% TNA y la de plazos fijos en dólares a 30–44 días, 1,124%. La brecha cotizada fue **2,70 puntos porcentuales**, frente a 5,39 puntos en julio de 2025. Es una compresión importante, pero no un margen contable del banco.

Si se aplica sólo como escenario la tasa activa de julio sobre 61%, 65% o 75% de cada dólar depositado y se resta la tasa pasiva, el carry bruto ilustrativo es 1,21, 1,36 o 1,74 puntos respectivamente. Antes de interpretar ganancia faltan mezcla de fondeo, plazos, capital, liquidez, costos operativos, comisiones, mora y pérdidas crediticias. La comparación sugiere que atraer depósitos no es suficiente: el banco también necesita activos prestables con rendimiento y riesgo compatibles.

## Qué hicieron efectivamente las personas

El Balance Cambiario de julio aporta una observación de flujo. Las personas humanas realizaron compras netas por USD 4.124 millones. Para el subconjunto de billetes y divisas sin fines específicos, el BCRA estimó que aproximadamente **USD 1.000 millones quedaron depositados en bancos locales**, otros **USD 1.000 millones aumentaron activos externos** y unos **USD 900 millones** cubrieron consumos con tarjeta. El dato no distribuye el stock de riqueza ni identifica instrumentos, pero muestra que el canal local y el externo coexistieron en magnitudes similares durante ese mes.

Esos montos de julio no reproducen por sí solos el 75% poselectoral ni el “aproximadamente 80%” de la conferencia: son flujos netos de un solo mes, con destinos redondeados y un universo diferente. La conclusión segura es más acotada: durante julio coexistieron ahorro bancario local, acumulación de activos externos y pagos corrientes.

## Qué limita el crédito nuevo

La ampliación del universo elegible no elimina el control prudencial. Para las financiaciones a clientes antes no admitidos, el BCRA fijó un cupo agregado de 15% de los depósitos en dólares por entidad, una exigencia de capital equivalente a 125% de una financiación comparable, un cómputo de exposición de 1,25 veces y evaluación de repago bajo movimientos del tipo de cambio. Esto vuelve más precisa la cadena: el depósito es fondeo potencial, pero el banco enfrenta cupos, capital, exposición y riesgo cambiario antes de decidir el préstamo.

La Comunicación A 8467, emitida el 18/08/2026, precisó quién puede acceder al nuevo cupo: **otras personas jurídicas que no encuadren en los destinos antes admitidos**. No habilita a los hogares como prestatarios de ese cupo. También exige que el banco preste especial atención al flujo de fondos y al patrimonio del deudor para evaluar si puede absorber aumentos de sus obligaciones cuando sus ingresos no acompañen al tipo de cambio.

## Primer corte posterior a la A 8467

Entre el 18 y el 27 de agosto, los depósitos privados en dólares aumentaron de USD 40.655 millones a USD 40.843 millones: **USD 188 millones**. Los plazos fijos explicaron USD 187 millones, mientras las cajas de ahorro disminuyeron USD 5 millones. En el mismo período, los préstamos privados en dólares pasaron de USD 25.217 millones a USD 25.367 millones: **USD 150 millones**. El ratio préstamos/depósitos apenas cambió de **62,03% a 62,11%**.

La composición publicada tampoco muestra una irrupción concentrada en documentos a sola firma: entre esos dos cortes, las tarjetas aumentaron USD 149 millones y “otros préstamos”, USD 134 millones, mientras los documentos disminuyeron USD 86 millones. Las líneas seleccionadas no reconcilian exactamente con el total por líneas menores y posibles reclasificaciones, de modo que no se fuerzan participaciones causales.

Además, de los USD 833 millones que el stock total de préstamos había aumentado entre el 31 de julio y el 27 de agosto, USD 683 millones —**82,0%**— ya se habían acumulado al día de emisión de la comunicación. Esto no separa movimientos ocurridos dentro del 18 de agosto ni establece cuál habría sido la trayectoria sin la norma. Sí evita atribuir automáticamente toda la expansión mensual al nuevo cupo.

El corte diario permite describir stocks agregados, no identificar dólares físicos que ingresaron desde fuera del sistema, depositantes únicos, transferencias desde cuentas o comitentes, prestatarios bajo A 8467 ni el uso final de sus préstamos. La comunicación no crea en sus dos páginas un identificador público del cupo. Por eso este primer corte es una **línea de base de seguimiento**, no una estimación de efecto causal.

## Calendario de prueba

El calendario del BCRA anuncia el Informe Monetario del 9/09 y el Boletín Estadístico del 14/09, primeras oportunidades para revisar agregados de agosto. El Informe sobre Bancos del 18/09 probablemente corresponda a julio si se mantiene el rezago reciente; el del 16/10 sería la primera ventana probable sobre mora bancaria general de agosto. La asignación de período a fecha es una inferencia, no una promesa del calendario.

Incluso entonces, la mora seguirá sin distinguir el cupo A 8467. La Central de Deudores es mensual, informa entidad, saldo y situación, pero no moneda, uso final ni identificador del programa. Además, la situación 2 comienza después de más de 31 días de atraso: entre la emisión y el último stock diario disponible sólo transcurrieron nueve días. Actividad, plazo, mora y destino final seguirán requiriendo publicaciones diferentes y no existe hoy un cruce público que los reúna.

Las fuentes permiten observar objetivos como formalizar activos, profundizar el crédito y favorecer el crecimiento sin expandir el gasto o la emisión. También muestran por qué fondeo, demanda, elegibilidad y uso deben analizarse por separado. La pregunta siguiente ya no es solamente si crecen los agregados, sino si futuras publicaciones permiten distinguir quién usa el cupo, en qué condiciones y con qué resultados.

## Preguntas abiertas y límites

- La PII registra USD 259,305 mil millones de moneda y depósitos de “otros sectores”, pero mezcla hogares, empresas e ISFLSH: no es una medición del “colchón” de las familias.
- El informe bancario de junio muestra que el crédito privado en moneda extranjera crecía 53,2% interanual frente a 27,4% de los depósitos, y una liquidez agregada en moneda extranjera de 48,6%. Son datos de otra fecha y definición: describen aceleración y colchón sistémico, pero no deben equipararse mecánicamente con el ratio préstamos/depósitos del 13 de agosto ni con el 17% de capacidad ociosa del IPOM.
- La tabla de tramos sólo permite medir concentración entre cuentas y saldos bancarios; no identifica titulares únicos, efectivo, cuentas en el exterior ni tenencias en comitentes.
- El aumento del número de cuentas se concentró aritméticamente debajo del tramo de 10.000, pero la fuente no permite distinguir aperturas genuinas de cambios de perímetro o cuentas automáticas de bajo saldo.
- La apertura por actividad y prestatario muestra concentración sectorial y por categoría jurídica, pero el BCRA no publica en estas tablas un cruce simultáneo entre actividad, tamaño, línea y uso final.
- El stock por actividad termina en junio y la encuesta en 2026-T2: ambos anteceden al anuncio del 13/08 y no miden el nuevo cupo.
- “Otras personas jurídicas” es la categoría complementaria a PyMEs en la planilla de operaciones; no equivale perfectamente a “grandes empresas” en la encuesta.
- El plazo corto y el tramo alto son compatibles con financiamiento corporativo de corto plazo, pero no identifican por sí solos capital de trabajo ni descartan inversión.
- La brecha entre tasa activa y pasiva no es el margen neto del banco; sólo se usa como escenario mecánico y conserva todos sus costos y riesgos fuera del cálculo.
- La CNV exige que los agentes informen comisiones, derechos, gastos e impuestos de cada operación. Por eso no existe un único “costo de comitente” generalizable; el simulador conserva el costo como supuesto explícito del usuario.
- La garantía de depósitos rige hasta ARS 50 millones por persona/entidad desde el 01/04/2026; los depósitos en moneda extranjera se convierten al tipo de referencia aplicable.
- ¿Qué peso relativo tienen la formalización, el crédito, la actividad, la recaudación y otros objetivos no explicitados en estas fuentes?
- Las motivaciones personales del ministro quedan fuera del alcance empírico; el módulo se limita a declaraciones, incentivos, restricciones y mecanismos observables.
- El módulo es análisis económico y de incentivos, no recomendación financiera individual.
