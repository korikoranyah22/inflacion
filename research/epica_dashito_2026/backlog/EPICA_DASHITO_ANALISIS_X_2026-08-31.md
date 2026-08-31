# ÉPICA — De la estabilización al bienestar
## Backlog de análisis para Dashito Argento a partir de las discusiones en X

### Objetivo

Convertir el dashboard en un banco de pruebas para afirmaciones económicas concretas que aparecen una y otra vez en X.

La idea no es sumar gráficos por sumar, sino conectar módulos que ya existen y responder preguntas abiertas y contrastables:

- ¿bajó la inflación pero mejoró el bienestar?
- ¿quién pagó el ajuste?
- ¿cuánto del superávit fiscal se explica por mejoras genuinas y cuánto por deterioro/traslado de costos?
- ¿cuántos hogares llegan a fin de mes con ingresos corrientes, sin quemar ahorros, endeudarse ni vender patrimonio?
- ¿la baja de pobreza es una recuperación consolidada o una salida frágil?
- ¿el crédito fue inclusión o un puente caro hacia la mora?
- ¿las reservas son propias, líquidas y suficientes?
- ¿el superávit comercial elimina la restricción externa?
- ¿el dólar, la base monetaria y la inflación se mueven mecánicamente juntos?
- ¿las inversiones anunciadas están llegando al empleo?
- ¿bajar impuestos amplía realmente la base lo suficiente para financiar las funciones públicas?
- ¿una lista de reformas es una lista de logros o una lista de inputs?

### Registro de hipótesis de partida

Las intuiciones, sospechas e hipótesis personales que dieron origen a cada investigación deben conservarse en el **storytelling** como parte de la historia del proyecto. Allí importa saber qué pensaba o esperaba encontrar la autora antes de abrir los datos.

Los tabs analíticos, en cambio, deben traducir ese punto de partida a preguntas más generales. La hipótesis de origen no se trata como un examen binario; el análisis debe mostrar:

- qué dimensiones pueden medirse;
- qué evidencia aporta cada fuente;
- qué interpretaciones son compatibles con los datos;
- qué explicaciones alternativas siguen abiertas;
- qué información falta para distinguirlas.

Ejemplo Caputo/dólares del colchón: el storytelling registra la intuición inicial —capacidad invertible concentrada, incentivos privados distintos de los objetivos oficiales y una posible urgencia macroeconómica—. El análisis se formula de manera neutral: ¿cómo se distribuye la capacidad de ahorro?, ¿qué atributos ofrece cada canal?, ¿qué objetivos declara la política?, ¿qué mecanismos y restricciones intervienen?

---

# Regla transversal de toda la épica

Cada análisis nuevo debe separar explícitamente:

1. **stock vs flujo**
2. **bruto vs neto**
3. **nominal vs real**
4. **personas vs pesos**
5. **hogares vs empresas**
6. **promedio vs distribución**
7. **correlación vs causalidad**
8. **acción de gobierno vs resultado**
9. **dato observado vs proyección**
10. **identidad contable vs interpretación distributiva**
11. **medida oficial vs estimación**
12. **efecto agregado vs incidencia por grupo**

Cada tab debe cerrar con:

- Qué muestran los datos.
- Qué NO muestran.
- Qué interpretaciones son compatibles con los datos.
- Qué dato faltaría para afirmar causalidad.
- Fuente primaria.
- CSV descargable.
- Fórmula reproducible.
- Fecha de corte.
- Comparador histórico o ventana espejo cuando corresponda.

---

# P0 — Núcleo de la nueva épica

## 1. Hogares bajo presión — “¿Quién llega a fin de mes sin comerse el futuro?”

### Pregunta central
¿Qué proporción de hogares cubre sus gastos corrientes sólo con ingresos corrientes?

### Construir
Un indicador de **estrés financiero del hogar** que clasifique, sin doble conteo:

- llega con ingresos corrientes;
- quema ahorros;
- toma deuda;
- vende pertenencias;
- combina dos o más estrategias;
- recorta consumo esencial;
- cae en mora.

### Cortes
- decil/quintil de ingreso;
- bajo / medio / alto;
- propietario / inquilino;
- registrado / informal;
- región;
- presencia de niños;
- edad del jefe/a de hogar.

### Métricas
- % sin estrategia extraordinaria;
- % que usa al menos una;
- % que usa 2+;
- tasa de ahorro;
- capacidad de ahorro;
- deuda de subsistencia;
- mora posterior.

### Visuales
- barras mutuamente excluyentes;
- Sankey: ingreso insuficiente → ahorro/deuda/venta → mora;
- matriz ingreso × estrategia;
- evolución trimestral.

### Punto narrativo
No decir “la mitad es pobre”. El indicador mide **fragilidad financiera**, no pobreza.

---

## 2. Runway de la clase media — “¿Cuánto tiempo puede esperar una familia?”

### Pregunta
¿Cuánto cuesta realmente “darle tiempo” a un programa económico según el colchón inicial del hogar?

### Construir
Escenarios de 3, 6, 12 y 24 meses para hogares tipo:

- sin ahorro;
- 1 salario de ahorro;
- 3 salarios;
- 6 salarios;
- propietario;
- inquilino;
- con deuda de tarjeta;
- con crédito personal.

### Inputs
- salario real;
- canasta;
- alquiler;
- servicios;
- CFTEA/tasa efectiva;
- ahorro inicial;
- inflación de esenciales.

### Output
Mes en que:
- se agota el ahorro;
- aparece deuda;
- deuda/ingreso supera umbral;
- entra en mora.

### Frase que debe poder testear
> “La paciencia también es un privilegio económico.”

---

## 3. Del superávit fiscal al balance de los hogares — balances sectoriales

### Pregunta
¿Puede el Estado tener superávit y los hogares ahorrar? Sí. ¿Qué ocurrió efectivamente en Argentina?

### Construir
Un tab de **balances sectoriales**:

- Sector público.
- Hogares.
- Empresas.
- Sector externo.

### Objetivo
Separar:
- identidad contable;
- cambio en ingreso disponible;
- ahorro;
- inversión;
- endeudamiento;
- deterioro patrimonial.

### Visual
Puente:
**resultado fiscal → ingreso privado → ahorro/inversión → cuenta corriente**

### Debe contestar
- por qué un superávit fiscal NO implica matemáticamente desahorro de hogares;
- si durante este episodio los hogares efectivamente desahorraron;
- qué parte correspondió a empresas;
- qué rol jugó el sector externo.

### Importantísimo
No atribuir causalidad al Gobierno sólo por simultaneidad. Mostrar incidencia observada y, aparte, escenarios causales.

---

## 4. Incidencia del ajuste — “¿Quién pagó?”

### Pregunta
¿Cómo se distribuyó el costo inicial y la recuperación posterior?

### Componentes
- salarios privados registrados;
- salarios públicos;
- no registrados;
- jubilaciones base;
- jubilaciones con bonos;
- hogares endeudados;
- ahorristas;
- bancos;
- fintech;
- empresas;
- Estado nacional;
- provincias;
- subsidios;
- transferencias.

### Output
Una **matriz de incidencia**, no una suma ingenua.

Columnas:
- shock inicial;
- recuperación;
- saldo;
- confianza causal;
- fuente.

### Evitar
“Banco ganó X = hogar perdió X” salvo que exista una identidad demostrable.

---

## 5. Pobreza baja, fragilidad alta — “¿La mejora se consolidó?”

### Pregunta
¿Cómo puede caer la pobreza mientras persisten ahorro quemado, deuda, mora y malestar material?

### Construir
Un índice de **salida frágil de la pobreza**.

Estados:
1. indigente;
2. pobre;
3. no pobre vulnerable;
4. clase media frágil;
5. clase media estable;
6. capacidad de ahorro.

### Cruzar
- línea de pobreza;
- ingreso real;
- ahorro;
- deuda;
- mora;
- consumo;
- transferencias;
- alquiler.

### Visual
Transiciones trimestrales:
**pobre → vulnerable → media frágil → media estable**

### Objetivo narrativo
Pobreza y bienestar no son sinónimos.

---

# P0 — Restricción externa, dólar y reservas

## 6. Reservas: bruto, neto, líquido y propio

### Pregunta
¿Cuánto de “USD 50.000 M de reservas” es realmente poder de fuego propio?

### Separar
- oro;
- divisas;
- títulos internacionales;
- depósitos;
- repos;
- DEG;
- swap China;
- encajes en dólares;
- depósitos del Tesoro;
- préstamos oficiales;
- otros pasivos de reserva.

### Mostrar cuatro cifras
1. reservas brutas;
2. reservas netas según metodología explícita;
3. reservas líquidas;
4. reservas propias/libres bajo escenario conservador.

### Cobertura
- meses de importaciones;
- vencimientos próximos 12 meses;
- depósitos privados en USD;
- base monetaria;
- deuda FX próxima.

### Visual clave
Waterfall:
**Brutas → menos obligaciones → netas → menos ilíquidos → líquidas utilizables**

---

## 7. Anatomía de la acumulación de reservas

### Pregunta
¿Por qué puede comprar dólares el BCRA y aun así caer la reserva bruta?

### Descomponer flujo mensual
- compras BCRA;
- pagos de deuda;
- desembolsos FMI/BM/BID;
- variación de depósitos;
- valuación de oro/activos;
- swaps/repos;
- intereses;
- intervención.

### Output
“De dónde salió cada dólar que entró a reservas”.

### Métrica nueva
**Acumulación orgánica vs acumulación financiada**.

---

## 8. ¿Por qué compra dólares y qué hace después con ellos?

### Pregunta
¿Cuánta reserva queda en efectivo y cuánta se invierte?

### Analizar
- composición de cartera;
- títulos soberanos internacionales;
- depósitos remunerados;
- repos;
- duración;
- liquidez;
- rendimiento;
- riesgo de tasa.

### Escenarios
- mayor duración;
- mayor liquidez;
- cartera actual.

### Output
Rendimiento esperado vs riesgo de liquidación.

---

## 9. Dólar, base monetaria e inflación — no son la misma variable

### Pregunta
¿Cuánto pass-through existe y con qué rezago?

### Series
- TC mayorista;
- M2/base monetaria;
- demanda privada de dólares;
- compras BCRA;
- IPC general;
- núcleo;
- regulados;
- alimentos;
- expectativas;
- actividad;
- salarios.

### Métodos
- correlaciones con rezagos;
- ventanas por régimen;
- local projections / VAR exploratorio;
- event studies de devaluaciones.

### Debe poder demostrar
- relación ≠ identidad;
- dólar puede subir con inflación descendiendo;
- expansión monetaria no se traduce 1:1 a IPC;
- el pass-through cambia según contexto.

---

## 10. Tipo de cambio real y “atraso”

### Pregunta
¿Qué evidencia permite llamar atrasado/caro/barato al peso?

### Incorporar
- TCRM/BCRA;
- REER;
- Big Mac raw y ajustado;
- productividad;
- salarios en USD;
- cuenta corriente;
- reservas;
- términos de intercambio.

### Evitar
“Hay superávit comercial → no puede haber atraso”.

### Output
Semáforo de señales, no un único “dólar de equilibrio”.

---

## 11. Sector externo completo — comercio ≠ cuenta corriente

### Construir
Un puente de balanza de pagos:

**Bienes  
− Servicios/turismo  
− Intereses  
− Dividendos  
+ Transferencias  
= Cuenta corriente**

Luego:

**Cuenta corriente  
+ Cuenta capital/financiera  
+ errores  
= variación de reservas**

### Debe responder
- por qué puede haber gran superávit comercial y cuenta corriente pequeña/negativa;
- cuánto drena turismo;
- cuánto drenan intereses/dividendos;
- qué cambia al liberar giros;
- cuánto aporta energía.

---

# P0/P1 — Crédito, bancos, fintech y mora

## 12. ¿Cuántos argentinos están endeudados y cuántos están en problemas?

### Tres universos separados
- personas con alguna deuda;
- hogares que se endeudan para gastos cotidianos;
- personas/hogares en mora.

### No sumar
Morosos + endeudados + quemadores de ahorro como si fueran poblaciones distintas.

### Output
Diagrama de conjuntos / flujos con bases compatibles.

---

## 13. Deuda de subsistencia

### Pregunta
¿Cuánto crédito nuevo financia consumo corriente y no inversión/bienes durables?

### Señales
- tarjeta;
- personales;
- adelantos;
- refinanciación;
- pago mínimo;
- deuda recurrente;
- gasto esencial.

### Métricas
- servicio de deuda / ingreso;
- saldo tarjeta / salario;
- cuota / ingreso;
- refinanciaciones;
- rotación;
- atraso.

---

## 14. Inclusión financiera o monetización de la exclusión

### Pregunta
¿El acceso nuevo al crédito mejora bienestar o sólo incorpora prestatarios caros?

### Cruzar
- acceso;
- tasa/CFTEA;
- ingreso;
- informalidad;
- score;
- mora;
- refinanciación.

### Output
Mapa:
**quién obtiene crédito × cuánto paga × qué resultado tiene 3/6/12 meses después**

---

## 15. Bancos: costo al hogar ≠ ganancia bancaria

### Extender tab actual
- ROA/ROE;
- margen financiero;
- costo de fondeo;
- encajes;
- previsiones;
- impuestos;
- capital;
- mora;
- castigos.

### Objetivo
Distinguir:
- costo crediticio alto;
- transferencia económica;
- rentabilidad contable;
- solvencia.

---

## 16. Hipotecarios financiados con FGS

### Pregunta
¿Quién captura el spread y quién carga el riesgo?

### Mostrar
- costo de fondeo FGS;
- tasa que cobra banco;
- spread bruto;
- costos;
- riesgo crediticio;
- riesgo UVA;
- quién absorbe pérdida;
- retorno esperado del FGS.

### Comparador
PRO.CRE.AR vs esquema actual:
- canal;
- intermediario;
- riesgo;
- subsidio;
- spread;
- beneficiario.

---

# P1 — Trabajo, inversión y RIGI

## 17. RIGI: dólares anunciados vs empleos reales

### Pregunta
¿Cuánto empleo genera cada USD 1.000 M invertidos?

### Separar
- anunciado;
- aprobado;
- iniciado;
- ejecutado;
- operativo.

### Empleo
- construcción temporal;
- directo permanente;
- indirecto;
- proveedor local.

### Métricas
- empleo / USD 1.000 M;
- permanente / total;
- inversión por puesto permanente;
- import content;
- exportaciones esperadas;
- divisas netas.

### Comparador
Empleo perdido desde nov-2023 vs empleo proyectado RIGI, dejando claro horizonte y universos.

---

## 18. Capital intensivo vs trabajo intensivo

### Pregunta
¿Puede crecer inversión y PIB sin recuperar empleo?

### Sectores
- minería;
- hidrocarburos;
- data centers/IA;
- industria;
- construcción;
- comercio;
- servicios.

### Output
Burbuja:
**inversión × productividad × empleo × masa salarial**

---

## 19. “El capital llega más rápido que el trabajo”

### Tab-resumen
Cruzar:
- inversión;
- empleo;
- salario real;
- participación laboral;
- consumo;
- productividad.

### Indicador
Elasticidad empleo/inversión por sector.

---

# P1 — Impuestos, Estado y federalismo

## 20. Ingresos Brutos: bajar alícuota ≠ recaudar lo mismo

### Pregunta
¿Cuánto debería crecer la base para compensar una baja/eliminación?

### Simulación
Para reducciones de:
- 10%;
- 25%;
- 50%;
- 100%.

Calcular expansión de base necesaria para neutralidad fiscal.

### Incorporar
- elasticidad de formalización;
- evasión;
- efecto cascada;
- traslado a precios;
- actividad.

### Resultado
Curva de neutralidad fiscal, sin asumir una Laffer mágica.

---

## 21. Separar Buenos Aires / 27 distritos: quién paga qué

### Escenario fiscal
Transferir:
- docentes;
- hospitales;
- seguridad;
- justicia;
- administración.

### Pregunta
¿Se achica el Estado o cambia el CUIT que paga?

### Output
Matriz Nación / provincia / municipios:
- función;
- costo;
- fuente de ingreso;
- déficit/superávit resultante.

---

## 22. PyMEs: presión tributaria, anticipos y liquidez

### Analizar
- anticipos;
- retenciones/percepciones;
- saldo a favor;
- plazos de devolución;
- capital de trabajo;
- tasa implícita del dinero inmovilizado.

### Caso de estudio
Regímenes provinciales como Misiones, con extremo cuidado jurídico:
cautelar ≠ sentencia de fondo.

---

# P1 — Estado, infraestructura y “déficit cero”

## 23. Superávit con depreciación del capital público

### Pregunta
¿Puede mejorar el flujo fiscal mientras se deteriora el stock de infraestructura?

### Cruzar
- resultado fiscal;
- inversión pública;
- mantenimiento;
- rutas;
- hospitales;
- escuelas;
- equipamiento.

### Métrica
Resultado fiscal convencional vs resultado ajustado por inversión/mantenimiento.

### Objetivo
Mostrar que **flujo fiscal y patrimonio estatal son preguntas distintas**.

---

## 24. Liquidez pública vs prestación

### Casos
- hospitales;
- organismos con FCI/títulos;
- fondos con inversiones financieras.

### Pregunta
¿Cuándo invertir excedentes es gestión normal y cuándo revela una prioridad discutible?

### Mostrar
- caja necesaria;
- compromisos próximos;
- inversiones;
- salarios/gastos pendientes;
- rendimiento.

---

## 25. Salud y educación: gasto → capacidad → resultado

### Extender
No sólo % PIB.

Agregar:
- salarios reales;
- vacantes;
- personal;
- obras;
- insumos;
- ejecución;
- matrícula;
- prestaciones.

---

# P1 — Asistencia social y “planeros”

## 26. Planes sociales comparables entre gobiernos

### Problema
Las placas virales mezclan:
- personas;
- beneficios;
- hogares;
- AUH;
- Alimentar;
- planes laborales;
- programas distintos.

### Construir
Serie apples-to-apples:
- beneficiarios únicos;
- prestaciones;
- hogares;
- gasto real;
- % población;
- % hogares.

### Debe poder contestar
“¿Hay más planes?” con una respuesta que especifique exactamente qué se está contando.

---

## 27. Transferencias y reducción efectiva de pobreza

### Pregunta
¿Cuánto reduce pobreza/indigencia cada bloque de transferencias?

### Escenarios
- ingreso observado;
- sin AUH;
- sin Alimentar;
- sin jubilaciones;
- sin transferencias.

### Output
Impacto distributivo por decil.

---

# P1 — Costo de vida

## 28. IPC promedio vs inflación que vive cada hogar

### Canastas
- inquilino;
- propietario;
- jubilado;
- familia con niños;
- joven;
- hogar pobre;
- clase media.

### Rubros
- alimentos;
- alquiler;
- servicios;
- salud;
- transporte;
- educación.

### Output
“Tu inflación” por perfil.

### Objetivo
Mostrar por qué IPC general y costo de vida percibido pueden divergir sin que uno de los dos sea “falso”.

---

## 29. Esenciales vs IPC núcleo/general

### Pregunta
¿La desinflación se concentra en rubros postergables mientras los esenciales corren distinto?

### Construir
Índice de esenciales y participación en presupuesto por decil.

---

# P1 — Deuda pública y financiamiento externo

## 30. “La deuda bajó” — auditor de definiciones

### Mostrar simultáneamente
- deuda bruta;
- deuda neta;
- consolidada Tesoro+BCRA;
- intra-sector público;
- privados;
- organismos internacionales;
- moneda extranjera;
- deuda/PIB.

### Objetivo
Que el usuario pueda cambiar metodología y ver por qué dos personas pueden afirmar “subió” y “bajó” usando universos distintos.

---

## 31. Nueva deuda vs reducción de stock

### Pregunta
¿Cómo puede un gobierno tomar préstamos y reducir alguna medida neta de deuda al mismo tiempo?

### Puente
stock inicial
+ nuevas emisiones
+ desembolsos
− amortizaciones
± valuación
± tipo de cambio
− activos/neteo
= stock final.

---

## 32. Muro de vencimientos 2027–2031

### Mostrar
- capital;
- intereses;
- moneda;
- acreedor;
- legislación;
- reservas líquidas;
- superávit externo esperado.

### Escenarios
- rollover normal;
- rollover caro;
- mercado cerrado;
- apoyo oficial.

---

## 33. Apoyo externo: FMI, EE.UU., BM/BID

### Pregunta
¿Cuánto de la estabilidad/ reservas proviene de generación propia y cuánto de financiamiento oficial?

### Timeline
- desembolsos;
- swaps;
- compras/intervenciones;
- vencimientos;
- condicionalidades.

---

# P2 — Comparaciones históricas y causalidad

## 34. Laboratorio de shocks argentinos

### Episodios
- 2014;
- 2018;
- 2020;
- 2023/24.

### Ventanas
-12 a +36 meses.

### Variables
- dólar;
- IPC;
- salario real;
- consumo;
- pobreza;
- reservas;
- deuda;
- tasa;
- empleo;
- cuenta corriente.

### Pregunta
¿Cuándo una devaluación fue corrección de atraso, shock externo, crisis de deuda, pandemia o combinación?

---

## 35. 2018 vs 2026 — comparación correcta

### Evitar
Comparar sólo inflación y dólar.

### Incluir
- poder adquisitivo;
- empleo;
- confianza;
- reservas netas;
- deuda;
- cuenta corriente;
- salario real;
- consumo;
- pobreza.

### Objetivo
Distinguir:
“macro más estable” de “población materialmente mejor”.

---

## 36. Shock vs gradualismo

### Pregunta
¿La magnitud y velocidad del ajuste de 2023/24 eran inevitables?

### Construir
Contrafactuales transparentes:
- salto observado;
- corrección escalonada;
- menor salto + mayor tasa;
- mayor financiamiento;
- mayor ajuste fiscal gradual.

### No afirmar
Que un contrafactual “habría ocurrido”.
Mostrar costos/beneficios bajo supuestos.

---

# P2 — “Inputs no son outcomes”

## 37. Auditor de logros de gobierno

### Origen
Las listas virales de:
“cerró / eliminó / desreguló / privatizó / tomó deuda / aprobó”.

### Para cada medida
- acción;
- objetivo declarado;
- mecanismo esperado;
- indicador de resultado;
- dato antes;
- dato después;
- confianza causal;
- efectos distributivos;
- estado: temprano / medible / no medible.

### Semáforo
- input realizado;
- output operativo;
- outcome positivo;
- outcome negativo;
- evidencia insuficiente.

### Regla
Nunca llamar “logro” a un verbo por definición.

---

# P2 — Instituciones económicas y calidad del dato

## 38. Quién controla los números

### Casos
- Oficina de Presupuesto del Congreso;
- auditorías;
- cambios de metodología;
- acceso a información;
- organismos regulatorios.

### Objetivo
Documentar cambios que afecten independencia, capacidad técnica o transparencia.

### Mantener aparte
No convertirlo en un tab partidario; medir:
- mandato;
- facultades;
- cambios normativos;
- producción de informes;
- tiempos/publicaciones.

---

## 39. Campaña, financiamiento y rendición

### Si se incorpora
Hacerlo como módulo institucional separado, no macroeconómico.

### Campos
- ingresos declarados;
- gastos;
- observaciones de auditor;
- estado procesal;
- aprobado / observado / pendiente;
- no confundir observación con delito.

---

# P2 — RIGI, IA y soberanía económica

## 40. RIGI tecnológico / data centers / IA

### Preguntas
- inversión;
- energía;
- agua;
- empleo permanente;
- importaciones;
- exportaciones;
- exenciones;
- infraestructura cedida;
- propiedad de datos/activos;
- impacto territorial.

### Objetivo
Medir la diferencia entre:
“entra capital”
y
“se genera capacidad productiva local duradera”.

---

# Sidecar recomendado — Observatorio de afirmaciones de X

No lo mezclaría con los tabs macro principales. Lo haría como una capa de navegación: **“Frases que exploramos”**.

Cada tarjeta tendría:

- afirmación textual;
- categoría;
- variables necesarias;
- lectura provisional;
- evidencia que aporta información relevante;
- evidencia que complejiza o limita esa lectura;
- grado de confianza;
- enlace a tabs.

### Afirmaciones para cargar

1. “Más base monetaria = más inflación.”
2. “Si sube el dólar, necesariamente sube la inflación.”
3. “Superávit comercial = superávit de cuenta corriente.”
4. “Si hay superávit comercial no puede haber atraso cambiario.”
5. “Reservas brutas = dólares libres.”
6. “Comprar dólares suma reservas uno a uno.”
7. “Tomar deuda significa necesariamente que el stock de deuda sube.”
8. “Si baja deuda/PIB, bajó la deuda.”
9. “Superávit fiscal implica que las familias tienen déficit.”
10. “Bajar impuestos siempre aumenta la recaudación.”
11. “Acceso al crédito = inclusión financiera.”
12. “Más inversión = más empleo.”
13. “RIGI repone el empleo perdido.”
14. “Bajar pobreza = recuperación completa del bienestar.”
15. “Si el IPC baja, el costo de vida baja igual para todos.”
16. “Tener tránsito / restaurantes llenos demuestra que sobra dinero.”
17. “Más planes sociales = más dependencia”, sin controlar universos.
18. “El mercado asigna correctamente todos los costos sociales.”
19. “Cerrar/desregular/privatizar es un logro por definición.”
20. “2018 estaba peor que 2026” sin definir variable.
21. “La mora es sólo un problema entre privados.”
22. “Los bancos sólo prestan el dinero de los ahorristas.”
23. “Los bancos crean dinero, por lo tanto crean inflación.”
24. “No tener 100% de depósitos líquidos = insolvencia.”
25. “Riesgo país / otro riesgo país = probabilidad electoral.”
26. “Turismo emisivo y energía pueden evaluarse sólo con balanza comercial.”
27. “Dividendos liberados prueban que no quedan restricciones cambiarias.”

---

# Arquitectura recomendada

## En vez de 15 tabs nuevos aislados

Crear 5 “super-tabs” que conecten lo existente:

### A. Hogares
- supervivencia;
- runway;
- deuda de subsistencia;
- salida frágil de pobreza;
- costo de vida personalizado.

### B. Dólares
- reservas netas;
- anatomía de flujos;
- cartera BCRA;
- cuenta corriente;
- TC real;
- pass-through.

### C. Quién paga
- balances sectoriales;
- incidencia del ajuste;
- bancos/fintech;
- impuestos;
- asistencia.

### D. Desarrollo
- RIGI;
- inversión;
- empleo;
- productividad;
- infraestructura;
- capital intensivo.

### E. Auditor de relatos
- claims de X;
- inputs vs outcomes;
- comparadores históricos;
- definiciones alternativas.

---

# Priorización propuesta

## Sprint 1 — El bolsillo real
1. Hogares que llegan sin estrategias extraordinarias.
2. Runway / quema de ahorros.
3. Endeudados vs endeudamiento de subsistencia vs morosos.
4. Pobreza vs fragilidad.
5. IPC personalizado/esenciales.

## Sprint 2 — El dólar que realmente hay
6. Reservas bruto/neto/líquido.
7. Anatomía de acumulación.
8. Cuenta corriente completa.
9. Tipo de cambio real.
10. Dólar/base monetaria/inflación.

## Sprint 3 — Quién pagó el ajuste
11. Balances sectoriales.
12. Matriz de incidencia.
13. Bancos/fintech.
14. FGS hipotecarios.
15. Asistencia social comparable.

## Sprint 4 — Inversión vs desarrollo
16. RIGI: anunciado/aprobado/ejecutado.
17. Empleo temporal/permanente.
18. Capital intensivo.
19. Estado de infraestructura.
20. Inversión pública vs superávit.

## Sprint 5 — Fiscal/deuda/instituciones
21. Auditor de definiciones de deuda.
22. Muro 2027–2031.
23. Apoyo FMI/EE.UU./multilaterales.
24. IIBB y formalización.
25. Federalismo y reasignación de funciones.

## Sprint 6 — Laboratorio de relatos
26. Input → output → outcome.
27. 2018 vs 2026.
28. Laboratorio de shocks.
29. Contrafactual shock/gradualismo.
30. Observatorio de afirmaciones de X.

---

# Definition of Done de la épica

La épica se considera terminada cuando el dashboard puede responder, con datos y sin slogans:

1. ¿La gente vive mejor?
2. ¿Quién está usando ahorros para sobrevivir?
3. ¿Quién se endeudó y quién cayó en mora?
4. ¿Quién pagó el ajuste?
5. ¿Quién se benefició?
6. ¿La baja de pobreza es robusta?
7. ¿Las reservas son realmente utilizables?
8. ¿El frente externo es sostenible?
9. ¿El dólar está atrasado o sólo estable?
10. ¿La inversión genera trabajo?
11. ¿El superávit preserva o descapitaliza activos públicos?
12. ¿La deuda bajó según qué definición?
13. ¿Bajar impuestos financia el mismo Estado?
14. ¿Las políticas anunciadas produjeron outcomes?
15. ¿Qué puede afirmarse sobre los relatos virales, con qué alcance y con qué límites?

---

# Nota de alcance

Temas de X como propaganda política, agresiones a periodistas, Peter Thiel como actor político, regulación de IA, financiamiento de campañas o doctrina partidaria son relevantes, pero no los metería en el núcleo macroeconómico.

Los trataría en dos sidecars:

- **Instituciones y poder**: OPC, campaña, regulación, lobby, infraestructura estratégica.
- **Observatorio de relatos**: propaganda, slogans y afirmaciones verificables.

Así el dashboard económico no se vuelve una enciclopedia política, pero tampoco pierde el contexto que explica por qué ciertas métricas importan.
