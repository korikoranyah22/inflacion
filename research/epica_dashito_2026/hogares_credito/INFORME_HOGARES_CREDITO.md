# Análisis empírico — Hogares, crédito, transferencias y costo de vida

**Fecha de corte:** 2026-08-31  
**Ítems ejecutados:** 1, 2, 5, 12–16 y 26–29 de la épica.  
**Alcance:** evidencia ya archivada en el repositorio; no se modificaron archivos fuente ni `index.html`.

## Resultado ejecutivo

La evidencia sí permite sostener cinco resultados descriptivos de confianza alta o media-alta:

1. **Fragilidad extendida, pero no una clasificación exhaustiva.** En 2025-S1, 37,4% de los hogares urbanos declaró gastar ahorros, 40,8% usó ahorros o vendió pertenencias, 25,5% solicitó préstamos a instituciones o familiares/amigos y 50,9% compró en cuotas o fiado. Son respuestas superpuestas: no se suman. La publicación agregada no permite calcular qué proporción cubrió todo sólo con ingreso corriente.
2. **Pobreza y estrés crediticio divergieron.** La pobreza de personas bajó de 52,9% en 2024-S1 a 28,2% en 2025-S2 (−24,7 puntos), mientras la mora bancaria media de personales + tarjetas subió de 2,602% a 8,541% del saldo (+5,939 puntos; 3,28 veces). Esto prueba que pobreza corriente y fragilidad financiera no son sinónimos; no prueba una causa de la mora.
3. **La inclusión en personales se expandió antes del fuerte deterioro.** Dentro del régimen CENDEU comparable desde julio de 2024, la cobertura de préstamos personales pasó de 23,10% a 32,20% de la población adulta a diciembre de 2025 (+9,09 puntos). En otro universo, la mora bancaria de hogares llegó a 12,80% del saldo en mayo de 2026 y la mora PNFC a 26,9% del saldo en febrero de 2026. La secuencia es compatible con inclusión seguida de tensión, pero no enlaza cohortes individuales.
4. **Costo al hogar y ganancia bancaria no son la misma magnitud.** El ROA del sistema agregado fue positivo pero cayó de 5,42% en diciembre de 2023 a 1,02% en diciembre de 2025, mientras la cartera irregular de consumo subió de 2,75% a 9,18%. El corte publicado en mayo de 2026 —con indicadores a marzo— registra ROA de 1,07% e irregularidad de consumo de 12,58%; 50 de 73 entidades tenían resultado estimado positivo y 23 negativo. No hay una identidad que permita llamar a la mora “ganancia bancaria”.
5. **La inflación vivida depende de las ponderaciones.** Entre diciembre de 2023 y julio de 2026, el IPC nacional acumuló 241,8%; vivienda/agua/electricidad/gas, 530,6%; regulados, 415,9%; núcleo, 221,7%; y alimentos, 209,3%. Hay esenciales por encima y por debajo del promedio. Sin ponderaciones observadas por perfil o decil no existe un único índice serio de “tu inflación”.

La matriz completa, con 27 filas etiquetadas como `observado`, `proxy`, `escenario` o `no disponible`, está en `matriz_evidencia.csv`.

## Regla de universos y doble conteo

Estas bases responden preguntas distintas y se mantuvieron separadas:

| Universo | Unidad | Último dato usado | Lectura válida |
|---|---|---:|---|
| Hogares EPH que solicitaron préstamos | hogares | 25,5% en 2025-S1 | conducta declarada de manutención |
| Personas adultas con préstamo personal reportable | personas | 32,20% en 2025-12 | cobertura CENDEU con umbral de $25.000 |
| Mora bancaria de hogares | pesos/saldo | 12,80% en 2026-05 | cartera irregular / financiaciones a familias |
| Mora PNFC total | pesos/saldo | 26,9% en 2026-02 | saldo con atraso mayor a 90 días / saldo PNFC |
| Pobreza | personas | 28,2% en 2025-S2 | ingreso familiar frente a línea de pobreza |

No se sumaron porcentajes entre filas. Una misma persona puede tener más de un proveedor; un hogar puede usar ahorros, préstamo y cuotas simultáneamente; y un porcentaje de saldo irregular no es un porcentaje de personas morosas.

## Ítems 1, 2 y 5 — presión, runway y salida frágil

### 1. Hogares bajo presión

El dosier EPH de INDEC permite medir incidencia, no exclusividad:

- gastó ahorros: **37,4%** de los hogares en 2025-S1;
- usó ahorros o vendió pertenencias: **40,8%**; por estrato, bajo 42,8%, medio 40,6% y alto 37,1%;
- solicitó préstamos a instituciones o familiares/amigos: **25,5%**; por estrato, bajo 30,4%, medio 23,9% y alto 18,6%;
- compró en cuotas o fiado: **50,9%**.

El mínimo matemático para la unión de esos tres grandes bloques publicados —préstamos; ahorro/venta; cuotas/fiado— es 50,9%, y el máximo es 100%. Ese intervalo es demasiado ancho para publicar “% con al menos una estrategia” o su complemento “% que llega sólo con ingresos”. Hacen falta microdatos EPH o una tabla de cruces. Tampoco se publican en el dosier recorte de consumo esencial ni mora posterior.

**Qué muestran:** una extensión alta de estrategias de deuda/descapitalización y un gradiente de préstamos más intenso en el estrato bajo.  
**Qué no muestran:** pobreza, pesos de ahorro consumidos, servicio deuda/ingreso, exclusividad ni transición a mora.  
**Lectura compatible con los datos:** la fragilidad financiera puede alcanzar hogares no pobres y coexistir con ingresos laborales.
**Dato faltante para causalidad:** panel hogar–ingreso–gasto–estrategia–deuda–mora.

### 2. Runway de clase media

El modelo queda especificado, pero no estimado como hecho observado:

```text
déficit_t = gasto_esencial_t + servicio_deuda_t - ingreso_corriente_t
runway_sin_interés = ceil(ahorro_inicial / max(déficit_mensual, 0))
deuda_t = max(0, deuda_(t-1) × (1 + tasa_efectiva_mensual) + déficit_t - ahorro_disponible_t)
```

El repositorio contiene salarios, IPC y tasas agregadas, pero no su combinación por hogar con alquiler, canasta, ahorro inicial y CFTEA contractual. Reemplazarlos por supuestos produciría escenarios; por eso no se publican meses de agotamiento como observación.

### 5. Pobreza baja, fragilidad alta

La divergencia 2024-S1→2025-S2 es descriptivamente fuerte:

```text
pobreza: 52,9% → 28,2% = −24,7 pp
mora bancaria personales + tarjetas, media semestral:
2,602% → 8,541% = +5,939 pp = 3,28 veces
```

Los denominadores son distintos. El resultado muestra que “bajó pobreza” y “se consolidó el bienestar financiero” no son equivalentes, pero no identifica quién salió de pobreza, quién se endeudó ni quién cayó en mora. Sin panel no pueden construirse las transiciones pobre→vulnerable→media frágil→estable pedidas por la épica.

## Ítems 12–16 — crédito, mora, inclusión y bancos

### 12. Endeudados versus hogares que se financian versus mora

- **Personas:** 32,20% de los adultos tenía un préstamo personal reportable en diciembre de 2025. La comparación válida empieza en julio de 2024, cuando cambió el umbral CENDEU de $1.000 a $25.000.
- **Hogares:** 25,5% solicitó préstamos en 2025-S1 según EPH; incorpora instituciones y familiares/amigos.
- **Mora sobre saldo:** bancos 12,80% de financiaciones a familias en mayo de 2026; PNFC 26,9% de saldo con más de 90 días en febrero de 2026.

No hay una base pública integrada que entregue la intersección entre estos conjuntos. En particular, `morosos + endeudados + quemadores de ahorro` sería doble conteo.

### 13. Deuda de subsistencia

El 50,9% que compró en cuotas o fiado es un **proxy de financiación de gastos de manutención**, no una medida de deuda de subsistencia en pesos. La fuente no separa alimento, alquiler o servicios de bienes durables; tampoco identifica pago mínimo, refinanciación recurrente, saldo/salario ni cuota/ingreso.

### 14. Inclusión o monetización de exclusión

La cobertura de personales creció 9,09 puntos dentro de un tramo comparable, y después se observan niveles de mora muy superiores. La secuencia es compatible con una interacción entre expansión, selección, precio y capacidad de pago. No permite decidir si el acceso mejoró bienestar o incorporó prestatarios caros, porque faltan cohortes con tasa, ingreso, informalidad, score y resultado a 3/6/12 meses.

### 15. Bancos

Los datos agregados muestran simultáneamente rentabilidad positiva, caída de rentabilidad y deterioro de cartera. También existen previsiones y capital que absorben riesgo. El costo crediticio del hogar puede ser alto sin convertirse peso por peso en utilidad: entre ambos aparecen costo de fondeo, encajes, gastos, impuestos, previsiones, castigos y capital.

La tabla por entidad tampoco autoriza a atribuir el resultado total a personales: en el corte de mayo de 2026, 50 entidades mostraban signo positivo y 23 negativo, y sus estados no separan el margen causal del producto.

### 16. Hipotecarios financiados con FGS

Se cierra como **no disponible**. No se localizó un contrato verificable que identifique costo de fondeo FGS, tasa al banco/prestatario, spread bruto, costos, riesgo crediticio/UVA, absorción de pérdidas y retorno esperado del fondo. PRO.CRE.AR es un canal público histórico distinto y no llena esa brecha. Sin esos documentos, afirmar quién captura el spread sería especulación.

## Ítems 26–29 — transferencias e inflación por hogar

### 26. Planes comparables

EPH informa que 14,6% de hogares declaró “planes sociales, subsidios y ayuda en dinero” en 2025-S1, frente a 4,5% en 2003-S2. La categoría es deliberadamente más amplia que un programa y la cobertura geográfica pasó de 28 a 31 aglomerados. No equivale a beneficiarios únicos, prestaciones ni gasto real; sirve como incidencia de una fuente de manutención, no para afirmar sin más “hay más planes”.

### 27. Transferencias y pobreza

La comunicación oficial según la cual AUH + Tarjeta Alimentar llegó a cubrir 100% de la CBA de un hogar tipo en 2024 —desde 54,8% en diciembre de 2023— es una medida de **generosidad normativa**. No es el efecto sobre la tasa de pobreza. La microsimulación “sin AUH/sin Alimentar/sin jubilaciones” requiere microdatos EPH, identificación o imputación de transferencias, reglas de compatibilidad y recálculo ponderado contra CBA/CBT; esos insumos no están integrados localmente.

### 28 y 29. IPC por perfil y esenciales

La variación acumulada se reprodujo como:

```text
variación_rubro = (índice_rubro,jul-2026 / índice_rubro,dic-2023 - 1) × 100
```

| Índice nacional | Variación dic-2023→jul-2026 |
|---|---:|
| Nivel general | 241,8% |
| Vivienda, agua, electricidad, gas y otros combustibles | 530,6% |
| Regulados | 415,9% |
| Núcleo | 221,7% |
| Alimentos y bebidas no alcohólicas | 209,3% |

La evidencia no sostiene una respuesta binaria “esenciales siempre corren más” o “la desinflación sólo fue en postergables”: vivienda/regulados superaron mucho al promedio, mientras alimentos quedaron por debajo en esta ventana. El resultado final para un inquilino, propietario, jubilado o decil depende de sus ponderaciones. Sin una fuente para esos pesos, cualquier “tu inflación” debe rotularse escenario.

## Estado por ítem

| Ítem | Estado | Resultado utilizable |
|---:|---|---|
| 1 | parcial fuerte | incidencias EPH observadas; falta cruce mutuamente excluyente |
| 2 | escenario especificado | fórmula reproducible; faltan inputs por hogar |
| 5 | parcial fuerte | divergencia pobreza–mora; sin transiciones individuales |
| 12 | fuerte por universos separados | personas, hogares y saldos sin sumarlos |
| 13 | proxy | cuotas/fiado para manutención; sin destino ni servicio/ingreso |
| 14 | parcial | expansión de cobertura + deterioro posterior; sin cohortes |
| 15 | fuerte agregado | rentabilidad, irregularidad y heterogeneidad; sin margen por producto |
| 16 | brecha | falta contrato FGS verificable |
| 26 | parcial | incidencia EPH amplia; sin deduplicación de programas |
| 27 | proxy/brecha | cobertura normativa CBA; sin microsimulación causal |
| 28 | escenario listo | divisiones IPC observadas; faltan ponderaciones por perfil |
| 29 | parcial | núcleo/regulados/rubros observados; falta índice esencial por decil |

## Reproducibilidad y fuentes

Ejecutar desde la raíz del repositorio:

```powershell
& "C:\Users\miyur\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" "research\epica_dashito_2026\hogares_credito\auditar_hogares_credito.mjs"
```

El script lee las series locales, recalcula variaciones y promedios, verifica anclas numéricas, genera `matriz_evidencia.csv`, la importa con `artifact-tool`, inspecciona su contenido y realiza un render de control en memoria. La extracción manual del dosier EPH se conserva como filas con página exacta y fuente primaria; no se simula una unión no publicada.

Fuentes primarias:

- [INDEC — Estrategias de manutención 2025](https://www.indec.gob.ar/ftp/cuadros/publicaciones/dosier_estrategias_manutencion_2025.pdf)
- [INDEC — Pobreza e indigencia](https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-46-152)
- [INDEC — IPC](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31)
- [BCRA — Inclusión financiera, segundo semestre de 2025](https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-segundo-semestre-de-2025/)
- [BCRA — Informe sobre Bancos](https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-junio-de-2026/)
- [BCRA — Proveedores no financieros de crédito](https://www.bcra.gob.ar/publicaciones/informe-de-proveedores-no-financieros-de-credito-junio-de-2026/)
- [Ministerio de Capital Humano — AUH + Alimentar y CBA](https://www.argentina.gob.ar/node/450359)

## Cierre

Los datos permiten afirmar que la mejora de pobreza convivió con uso masivo de estrategias de manutención no corrientes, expansión del crédito personal y fuerte deterioro posterior de la mora. No permiten asignar esa trayectoria a una causa única, contar hogares únicos en todos los universos, medir bienestar individual después del crédito ni construir transferencias/IPC personalizados sin microdatos y ponderaciones adicionales.
