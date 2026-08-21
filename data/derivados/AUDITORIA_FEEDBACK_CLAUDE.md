# Prompt de traspaso · correcciones de los tres feedbacks de Claude

Usá este documento como prompt para portar al dashboard rediseñado **todos los cambios realizados desde el primer feedback de Claude**. La instancia de destino puede haber empezado desde una versión anterior: no alcanza con copiar textos o estilos sueltos. Hay que trasladar las reglas, cálculos, cautelas y fuentes únicas de datos descritas acá.

## Objetivo

Incorporá todas las correcciones listadas sin modificar resultados que Claude ya auditó como consistentes. Priorizá una sola fuente de verdad para cada cifra repetida: gráficos, cards, prosa, tablas, CSV y “Lo que te robó Milei” deben consumir el mismo resultado derivado.

La implementación de referencia está en:

- `index.html`
- `data/dashboard_kawaii_133_aporte_grandes_fortunas.html`
- `data/derivados/audit_claude_feedback_consistency.py`

Las dos copias HTML están sincronizadas; la diferencia admisible entre ellas son únicamente las rutas relativas del tab Grandes fortunas.

## Cambios obligatorios

### 1. Inversión (FBCF): corregir el error duro y eliminar el hardcode

El texto viejo decía que 2025 había quedado `≈5,2%` debajo de 2023. Eso contradice el array `investmentReal`:

- 2023: nivel `100,000`
- 2024: crecimiento `−17,2%`, nivel `82,800`
- 2025: crecimiento `+16,2%`, nivel `96,214`

La comparación correcta es:

```text
96,214 / 100 − 1 = −3,786%
```

Mostrar **≈3,8% debajo de 2023**.

No escribas manualmente `−17,2%`, `+16,2%` ni `3,8%` en la card. La card debe consumir el mismo `investmentReal` que alimenta el gráfico. En la implementación actual esto se resuelve con `renderInvestmentSummary()` y los destinos:

- `investment2024GrowthKpi`
- `investment2025GrowthKpi`
- `investment2025LevelContext`

### 2. Inflación presidencial: aplicar una convención uniforme a diciembre de 2019

La versión anterior dejaba diciembre de 2019 fuera de Macri y de Alberto, aunque el IPC INDEC mensual existe. Aplicar la misma regla usada para diciembre de 2023: cuando el dato mensual no puede dividirse por días, el mes de asunción se atribuye al gobierno entrante.

Períodos corregidos:

- Alberto Fernández: **dic-2019 → nov-2023**, 48 meses, diciembre de asunción incluido.
- Javier Milei: **dic-2023 → jul-2026**, 32 meses, diciembre de asunción incluido.

Resultados presidenciales actuales:

- Alberto: **≈930,7% acumulado**, **≈4,98% mensual equivalente**.
- Milei: **≈328,8% acumulado**, **≈4,65% mensual equivalente**.

La tabla, gráfico, tooltips y CSV descargable deben usar los mismos períodos. La nota metodológica debe decir explícitamente que diciembre de 2019 se atribuye a Alberto y diciembre de 2023 a Milei.

Diciembre de 2015 permanece fuera de la comparación porque el tramo histórico armonizado usado no permite aislarlo homogéneamente. Explicarlo como una excepción de datos, no como una regla política diferente.

### 3. Diciembre de 2023: distinguir preguntas y ventanas, no forzar números iguales

El dashboard usa diciembre de 2023 de tres maneras legítimas, pero no deben compartir un rótulo ambiguo:

1. **Inflación imputada al mandato:** `dic-2023 → jul-2026`, con diciembre atribuido al entrante. Resultado actual: **≈328,8%**.
2. **Variación desde el cierre de diciembre de 2023:** base `dic-23 = 100`; mide `ene-2024 → jul-2026`. Con el vector IPC actual el resultado es **+241,8%**.
3. **Cards BCRA por presidencia:** usan meses completos; Milei es `ene-2024 → jul-2026`, con diciembre de 2023 excluido.

Rótulos recomendados/actuales:

- `Mandato Milei · dic-2023 imputado al entrante → jul-2026`
- `IPC jul-26 vs dic-23 = 100`
- `Milei ene-2024→jul-2026 · meses completos`

No reemplaces 328,8% por 241,8% ni viceversa: contestan preguntas distintas. Conservá la sensibilidad que excluye diciembre de 2023 y explicá qué ventana usa.

### 4. Néstor Kirchner: corregir el conteo de meses

No mostrar simplemente `≈55 meses`. Distinguir:

- **56 meses calendario** entre mayo de 2003 y diciembre de 2007.
- **55 variaciones** desde el mes base.

Rótulo actual: `56 meses calendario · 55 variaciones desde la base`.

Aplicar la distinción también al tooltip y al CSV presidencial.

### 5. Pinza banco versus plazo fijo: conservar precisión y explicar el redondeo

La aparente discrepancia `3,29 − (−0,37) = 3,67` proviene de mostrar operandos redondeados. La cuenta auditada usa valores completos:

```text
3,292465 − (−0,374889) = 3,667354 pp reales
```

Mostrar el resultado como **3,67 pp**, aclarando que la cuenta usa precisión completa y que las cards pueden redondear los componentes.

No cambiar la semántica ya auditada de la pinza:

- saldo contra la norma histórica: positivo = favorable para el hogar; negativo = desfavorable;
- diferencial entre ventanas: `post_shock − espejo`;
- diferencial positivo = mejora respecto de la ventana espejo;
- diferencial negativo = empeoramiento;
- seguir negativo no significa necesariamente haber empeorado.

Conservar banco, plazo fijo y Fintech como componentes explícitos. No llamar al agregado “impacto del hogar promedio”, porque crédito y ahorro pertenecen a universos diferentes. Usar **balance conjunto de crédito y ahorro minorista** o **balance ampliado** cuando también incluya Fintech.

### 6. Asistencia durante Macri: alinear la card con la comparación calculada

El recorte real de `≈9,29%` corresponde a **2017 → 2019**, no a 2016 → 2019.

La card debe mostrar:

- 2017 · máximo: **34,54 billones**
- 2019: **31,33 billones**
- texto: `Desde el máximo de 2017, la crisis 2018–2019 produjo un recorte real acumulado de ≈9,29%.`

### 7. Mercado Libre: una sola conversión para todas las apariciones

La versión anterior mostraba dos cifras para la misma operación: `$223,08 mil M` y `$218,95 mil M`. La segunda era un texto viejo.

El beneficio documentado 2024→1T26 debe salir de una única función derivada. La implementación actual usa `meliRecentConversion()`:

1. convierte cada período con su A3500 promedio;
2. reexpresa cada subtotal con IPC nacional;
3. usa junio de 2026 como mes monetario de referencia;
4. suma los tramos 2024, 2025 y 1T-2026.

Deben consumir esa misma salida:

- KPI de Mercado Libre;
- prosa explicativa;
- tabla de conversión;
- card/tabla de “Lo que te robó Milei”;
- cualquier CSV derivado que incluya el monto.

No dupliques `$223,08 mil M` como literal. Con los datos actuales la salida se muestra redondeada a ese valor, pero debe calcularse en tiempo de ejecución. Mantener explícita la referencia **pesos de junio de 2026**.

### 8. La casta: derivar nominal, IPC y resultado real desde el mismo vector

Eliminar los valores escritos manualmente `+134,2%`, `+241,5%` y `−31,4%`. La implementación actual usa:

```text
castaInflationVsSalary.authorities[-1] = 234,2089
castaInflationVsSalary.cpi[-1]         = 341,7984
```

Fórmulas:

```text
suba_nominal = 234,2089 − 100 = +134,2089%
suba_ipc     = 341,7984 − 100 = +241,7984%
resultado_real = 234,2089 / 341,7984 − 1 = −31,477474%
```

Mostrar:

- **+134,2% nominal**
- **+241,8% IPC desde cierre dic-2023**
- **−31,5% real**

El `+241,5%`/`−31,4%` citado por Claude era internamente coherente con un vector IPC anterior. Con la serie actual corresponde `+241,8%`/`−31,5%`. No copies ninguno de esos números como hardcode: usar `castaSummary()` y `castaPct()` o una implementación equivalente.

Propagar el resultado real derivado a:

- cards del tab La casta;
- gráfico comparativo por mandato;
- card de autoridades superiores del PEN en “Lo que te robó Milei”;
- tabla de atribución del mismo tab.

### 9. Grandes fortunas: eliminar la abreviatura monetaria ambigua `B`

En castellano argentino `B` puede confundirse entre *billion* anglosajón y billón español. No usarla para montos visibles.

Convención:

- `$1.000 M` o `$1 mil M` para `10^9`;
- `$1 billón` para `10^12`;
- `$4,98 billones` para `4,98 × 10^12`.

Revisar:

- selector de umbral;
- nombres de tramos;
- ejes;
- tooltips;
- cards;
- tablas;
- CSV y documentación visible.

En particular, el tooltip de participación debe decir `Máximo $ X billones`, no `Máximo $ X B`.

### 10. “Lo que te robó Milei”: hacer auditable la escala de 13,8 millones

La cuenta usa **13,8 millones de asalariados urbanos**, no toda la PEA. Mostrar los insumos que permiten reconstruirla:

- asalariados registrados;
- asalariados no registrados;
- ingreso medio ponderado de EPH 3T-2023;
- salario-base inferido a noviembre de 2023 mediante Total índice de salarios;
- masa salarial-base mensual;
- reexpresión a pesos de junio de 2026.

Incluir la cautela: es un supuesto de escala construido desde EPH e índices, no una nómina observada. La relación es lineal: si el salario-base supuesto cambia 10%, la estimación monetaria cambia 10%.

### 11. “Lo que te robó Milei”: preservar la reconciliación y evitar doble conteo

La cuenta salarial auditada es:

```text
agujero salarial bruto        $18,43 billones
menos recuperación observada  $ 6,08 billones
saldo salarial neto           $12,35 billones
```

Sólo el agujero bruto y la recuperación observada forman esa cuenta. Banco, plazo fijo, Fintech, privilegios fiscales, Mercado Libre, SIDE, autoridades PEN, Senado y grandes fortunas son escenarios, controles o alivios contrafactuales separados; no deben sumarse automáticamente al “robo” ni duplicar componentes.

Cuando se muestre “si devolvieran” o “si se solucionara”, presentar el monto como **alivio potencial que descontaría del saldo restante**, con recorrido visible del remanente. Mantener claramente separados:

- daño salarial observado;
- recuperación salarial ya ocurrida;
- devolución hipotética de bancos;
- devolución hipotética de Fintech;
- otras partidas contrafactuales;
- aporte voluntario de grandes fortunas como escenario de financiación separado.

El diferencial Fintech entre ventanas responde “¿mejoró o empeoró?”; no es automáticamente el monto de devolución. Para la devolución se usa la exposición/saldo que corresponda, sin confundirla con el cambio respecto de la ventana espejo.

### 12. No repetir cifras derivadas como texto independiente

Regla general para el rediseño:

- FBCF: una estructura (`investmentReal`) y una función de resumen.
- Mercado Libre: una conversión (`meliRecentConversion()`) compartida.
- La casta: un resumen (`castaSummary()`) compartido.
- Pinza financiera: valores completos para calcular, redondeo sólo al presentar.
- Períodos presidenciales: una única estructura compartida por tabla, gráfico, tooltip y CSV.

Si el diseño necesita repetir una cifra, repetí el nodo de salida o invocá la función; no copies el número literal.

## Resultados auditados que no deben “corregirse”

Claude verificó estas cuentas y no encontró error. Conservarlas salvo que cambie una fuente de datos documentada:

- **Cuenta salarial:** 18,43 − 6,08 = 12,35 billones.
- **Grandes fortunas:** suma por tramos = `4.748.104.628.254,49`; meta = `4,98 billones`; aportantes estimados = `44.966,56`. El escenario actual no alcanza la meta bajo el tope seleccionado.
- **Privilegios fiscales:** 0,882 + 0,350 = 1,232 billones; 1,23 + 3,67 = 4,90 billones; Mercado Libre documentado en USD: 57 + 64 + 13 = 134 M.
- **SIDE:** 97,135 + 49,3 = 146,435 mil M, aproximadamente +50,7% de crédito vigente frente al inicial. Crédito presupuestario no equivale automáticamente a gasto ejecutado.
- **Deuda pública:** ratio 78,1% → 73,4% = −4,7 pp mientras el stock en USD sube aproximadamente 6,3%; no es una contradicción porque cambia el denominador.
- **Poder adquisitivo, tasas Fisher, pobreza, Gini, canastas CABA/GBA y consumo:** los cálculos revisados cerraron.

Tampoco son errores:

- que Total salarios no sea un promedio simple de registrado y no registrado;
- que hogares tipo de INDEC e IDECBA no sean idénticos;
- que los tramos metodológicamente distintos de Gini no se conecten como una sola serie homogénea.

Conservar los rótulos que explican esas diferencias.

## Criterios de aceptación

Antes de dar el rediseño por terminado, verificar:

1. La card FBCF calcula `≈3,8% debajo de 2023` desde `investmentReal`.
2. Alberto incluye diciembre de 2019 y la regla queda explicada.
3. Los tres usos de diciembre de 2023 tienen rótulos distintos y correctos.
4. Néstor muestra 56 meses calendario / 55 variaciones.
5. La pinza usa operandos completos y presenta 3,67 pp.
6. La card de asistencia de Macri compara 2017 con 2019.
7. Mercado Libre no contiene totales constantes duplicados.
8. La casta deriva +134,2%, +241,8% y −31,5% del mismo vector.
9. No existe notación monetaria visible del tipo `$1 B`, `$3 B` o equivalente.
10. La escala de 13,8 millones y el salario-base pueden auditarse desde la interfaz.
11. La cuenta 18,43 − 6,08 = 12,35 permanece reconciliada y sin doble conteo.
12. Los escenarios de devolución se muestran como contrafactuales que reducen un saldo, no como daño observado adicional.
13. El HTML no contiene errores de sintaxis y todos los controles dinámicos se renderizan.
14. La versión root y la copia versionada permanecen sincronizadas.

## Auditoría automática de referencia

En la implementación actual se ejecuta desde la raíz del repositorio:

```powershell
python data/derivados/audit_claude_feedback_consistency.py
```

El control falla si:

- reaparecen `5,2%`, `$218,95 mil M`, `+241,5%`, `≈241,7%` o `−31,4%` en los contextos corregidos;
- una card deja de consumir su estructura derivada;
- se pierden las convenciones de diciembre de 2019/2023;
- vuelve un monto visible expresado con la `B` ambigua;
- `index.html` y la copia v133 se desincronizan.

Si el rediseño cambia IDs o arquitectura, adaptar la auditoría a los nuevos componentes sin eliminar las invariantes que controla.
