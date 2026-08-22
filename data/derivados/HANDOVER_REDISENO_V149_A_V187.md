# Handover consolidado para el rediseño · v149 a v180

Fecha de corte: 22 de agosto de 2026.  
Dashboard fuente: `index.html`.  
Snapshot vigente: `data/dashboard_kawaii_180_slider_pendulo_mobile.html`.  
Documento base anterior: `data/derivados/AUDITORIA_ESCALAS_LOG_Y_JERARQUIA_VISUAL_V148.md`.

## Cómo usar este documento

Tomá este archivo como prompt incremental completo para portar al dashboard rediseñado todo lo realizado desde **v149 hasta v180 inclusive**. El estado funcional final está en `index.html`; el snapshot v180 es una copia byte a byte de ese archivo al corte.

No reemplaza los handovers anteriores del Péndulo, feedback de Claude, EMAE, morosidad, rutas o turismo. Documenta el delta posterior a v148. En caso de conflicto con la auditoría v148 o con una nota intermedia de este mismo historial, **manda siempre el estado final descrito aquí y reproducido por v176**.

## Resumen ejecutivo para la instancia de rediseño

Portá estas familias como un solo paquete, sin seleccionar únicamente las correcciones visuales más recientes:

1. Escalas Lineal/Log opcionales y completas en Poder adquisitivo y Tasas e inflación.
2. Controles pegados al gráfico que modifican, incluida la base de EMAE.
3. Registro homogéneo de fuentes y trazabilidad en las 33 pestañas.
4. Leyendas Plotly completas, horizontales y sin scroll interno.
5. Menús temáticos y tabs con desplazamiento horizontal visible y rueda vertical convertida sólo mientras exista recorrido lateral.
6. Sistema tipográfico transversal, kickers rectangulares y jerarquía estable.
7. Reflow real de anotaciones, mandatos, ejes y márgenes al cambiar de ancho; no alcanza con redimensionar el canvas.
8. Compactación vertical y corrección de etiquetas en pobreza, asistencia social, Gini, estructura social, familia, salud, consumo, trabajo, inversión, vivienda, EMAE, morosidad, Péndulo y BCRA.
9. Preservación de huecos metodológicos: no inventar continuidad entre tramos sin observaciones.
10. Aceptación final en 33/33 tabs a 390 × 844 y 1280 × 900, sin desborde horizontal; las 32 pestañas estadísticas conservan además la auditoría de gráficos de v169.

## 1. Corrección obligatoria a la auditoría v148

La auditoría v148 decía que `Poder adquisitivo` y `Tasas e inflación` permanecían exclusivamente lineales. Esa regla fue revisada: ambos gráficos ofrecen una vista Log opcional, pero la versión final **no elimina series**.

Ahora ambos gráficos ofrecen dos versiones opcionales:

- `Lineal`: lectura completa de niveles, diferenciales y saldos.
- `Log`: lectura proporcional en el eje izquierdo para las series positivas y comparables; las series monetarias con signo permanecen visibles en un segundo eje lineal.

La vista inicial sigue siendo siempre `Lineal`. No se transforman los datos, no se suman constantes, no se reemplazan ceros y el tiempo permanece lineal. En ambas pestañas la leyenda y las trazas son las mismas en Lineal y Log: cambia la escala del eje izquierdo, mientras los saldos con signo conservan un eje derecho lineal.

La interfaz debe explicar de manera visible qué eje cambia de escala y por qué los saldos mantienen un eje lineal. No ocultar contenido silenciosamente.

## 2. Poder adquisitivo · Lineal / Log

Gráfico afectado: `#powerChart`.

### Vista Lineal

- Conserva todas las series del índice real.
- En base `nov-2023 = 100`, conserva además las dos series acumuladas del eje derecho:
  - `Excedente acumulado previo · ventana espejo`.
  - `Pérdida neta acumulada desde shock`.
- Mantiene el eje derecho, sus ticks y sus anotaciones.

### Vista Log

- Conserva las mismas diez entradas y trazas de la vista Lineal.
- Los índices reales positivos usan el eje izquierdo semilogarítmico.
- `Excedente acumulado previo · ventana espejo` y `Pérdida neta acumulada desde shock` permanecen visibles en el eje derecho lineal.
- El eje derecho conserva negativos, cero, positivos y sus anotaciones; no se transforman ni se invierten los saldos.
- Usa ticks legibles `50, 60, 75, 100, 125, 150, 200, 250`.
- Usa un rango logarítmico explícito equivalente a `45–250`. En Plotly, el `range` del eje Log se expresa en `log10`; no reutilizar el rango lineal como si fueran exponentes.
- El selector comunica `Log · mismas series` y la ayuda explica la combinación de ejes.

### Interacciones que deben convivir

- El selector de base `nov-2023 = 100 / ene-2017 = 100` sigue funcionando en ambas escalas.
- El checkbox de foco desde 2015 es independiente de la escala.
- Cambiar base, cambiar foco, redimensionar la ventana o volver a abrir el tab no debe ocultar trazas ni alterar el signo de los saldos.
- Volver a Lineal cambia la proyección del eje izquierdo, no la composición de la leyenda.

Implementación actual de referencia:

- Configuración: `CHART_SCALE_CONFIG.powerChart`.
- Aplicación: `applyPowerChartScale(type, el)`.
- Decoraciones: `powerMandateDecorations(mobile, base)`.

## 3. Tasas e inflación · Lineal / Log

Gráfico afectado: `#nominalChart` dentro del tab `Tasas e inflación`.

### Vista Lineal

Conserva las ocho trazas actuales:

1. Inflación acumulada del año calendario.
2. Préstamos personales bancarios · TNA promedio.
3. Plazo fijo 30–59 días · TNA promedio.
4. Fintech PNFC personales · TNA promedio.
5. Diferencial nominal banco − plazo fijo.
6. Saldo ampliado de la ventana espejo.
7. Saldo ampliado post-shock.
8. Diferencial post-shock vs espejo.

También conserva el eje monetario derecho.

### Vista Log

- Conserva las mismas ocho trazas de la vista Lineal; no desaparece ningún campo de la leyenda.
- Las primeras cinco trazas —inflación, tres TNA y diferencial banco − PF— permanecen en el eje izquierdo Log. En la foto de datos actual, el diferencial anual es siempre positivo y por eso admite esta proyección.
- Los tres saldos monetarios con signo permanecen en el eje derecho **lineal**. No se les aplica logaritmo, no se altera el signo y el cero sigue visible.
- Usa ticks `1, 3, 10, 30, 100, 300` y rango explícito equivalente a `1–300`.
- Texto visible del estado: `Vista mixta: las cinco series de tasas y brecha usan Log; los tres saldos conservan el eje derecho lineal. No falta ningún campo del Lineal.`
- Los tooltips continúan mostrando valores reales; Log sólo cambia la proyección vertical.

La tira contextual debe desactivar una confusión frecuente: en el eje izquierdo, más arriba significa una tasa o brecha de mayor magnitud, no necesariamente un resultado “mejor”. En el eje derecho, `+$` favorece al hogar y `−$` lo perjudica.

### Anotaciones de 2023

Se preservan en ambas escalas:

- `10/12/2023 · asume Milei`.
- `Hasta 30/11/2023 · ≈148,1% acumulado bajo Alberto`.
- `Diciembre 2023 · shock de +25,5% bajo Milei`.

En Plotly, al usar eje Log, las coordenadas `y` de las dos anotaciones vinculadas a valores de inflación deben convertirse a `Math.log10(valor)`; los valores de las series no se convierten manualmente.

El checkbox de foco desde 2015 debe seguir siendo independiente de la escala.

Implementación actual de referencia:

- Configuración: `CHART_SCALE_CONFIG.nominalChart`.
- Aplicación: `applyNominalChartScale(type, el)`.
- Decoraciones: `annualMandateDecorations(mobile)`.

## 4. Controles de escala compartidos

Los controles se generan inmediatamente antes del gráfico mediante `installChartScaleControls()`.

Requisitos visuales y accesibles:

- Botones `Lineal` y `Log` con `aria-pressed`.
- Estado activo inequívoco.
- Ayuda breve que explique magnitud absoluta vs cambio proporcional.
- En `Poder adquisitivo`, la ayuda aclara que los índices usan Log y los saldos con signo siguen visibles en el eje derecho lineal.
- En `Tasas e inflación`, la ayuda aclara que **ninguna serie se oculta**: tasas y brecha usan Log, mientras los saldos siguen en el eje derecho lineal.
- Estado textual persistente junto al control.
- En mobile el bloque puede envolver contenido, pero los botones deben seguir visibles y tocables.
- No usar persistencia en `localStorage`: el estado vuelve a Lineal al recargar.

## 5. Corrección de etiquetas superpuestas

### Notas fuera del área de datos

Se sacaron del lienzo Plotly las notas metodológicas que competían con etiquetas presidenciales y callouts. Ahora viven en tiras HTML inmediatamente antes de los gráficos:

- `#powerChartContext`: metodología de empalmes y base activa.
- `#ratesNominalContext`: regla de franjas presidenciales, orientación semántica de ambos ejes y disponibilidad Fintech desde abril de 2019.
- Clase compartida: `.chart-context-strip`.

El texto de base de Poder adquisitivo se actualiza al alternar nov-2023 / ene-2017.

### Etiquetas presidenciales

- En ventanas mayores a 1100 px se permiten los nombres completos.
- A 1100 px o menos se usan etiquetas compactas: `Duhalde`, `Néstor`, `CFK`, `Macri`, `Alberto`, `Milei`.
- Esto responde al ancho real disponible en tarjetas de dos columnas; no debe depender solamente del breakpoint mobile de 720 px.

### Callouts

- La etiqueta de pandemia se desplazó para no chocar con el acumulado espejo.
- El callout del espejo en Poder adquisitivo se movió hacia abajo.
- Los tres hitos de 2023 en Tasas se distribuyeron a izquierda, centro y derecha, preferentemente dentro del área del gráfico y sin invadir la fila presidencial.
- Al cambiar a Log no deben desaparecer las anotaciones de noviembre y diciembre por usar coordenadas lineales incorrectas.

## 6. EMAE · controles pegados al gráfico afectado

Tab: `Actividad real · ¿crecimiento o rebote?`.

Los controles:

- `#emaeBase`.
- `#emaeOriginalToggle`.

se retiraron del encabezado general del tab y se trasladaron al panel `A. Nivel mensual de actividad`, inmediatamente antes de `#emaeMainChart`.

El nuevo bloque usa `.emae-chart-controls` y lleva la lectura:

> Ajustes de los gráficos A y B  
> La base y la serie original también se aplican al gráfico por habitante.

La aclaración es importante porque ambos controles modifican `#emaeMainChart` y `#emaePcChart`, aunque se ubiquen junto al primero.

Responsive obligatorio:

- Más de 1100 px: explicación y controles en una barra horizontal compacta.
- Hasta 1100 px: explicación arriba y controles en una segunda fila.
- Hasta 768 px: selector y checkbox apilados, cada uno a ancho completo.
- El bloque debe quedar visualmente unido al gráfico y no volver al hero.

No se duplicaron IDs ni listeners. Los listeners existentes de `change` continúan llamando a `renderEmae()`.

## 7. Invariantes generales a preservar

- Link visible al repositorio en el hero: `https://github.com/korikoranyah22/inflacion`.
- El filtrado temático superior no elimina tabs; sólo cambia cuáles botones se muestran.
- Los filtros desde 2015 sólo cambian el rango visible, nunca los cálculos o tarjetas.
- Los saldos monetarios mantienen su semántica desde el lado del hogar.
- No confundir `sigue negativo` con `empeoró`.
- No mover controles lejos del gráfico que modifican.
- No introducir nombres de compañeros, autores internos o placeholders personales en la documentación del rediseño.

## 8. Matriz mínima de aceptación

### Poder adquisitivo

- [ ] Lineal completa: índices + eje derecho + dos acumulados.
- [ ] Log mixta: las mismas diez series del Lineal; índices en el eje izquierdo Log y acumulados con signo en el eje derecho lineal.
- [ ] Lineal desde 2015: etiquetas sin superposición.
- [ ] Log desde 2015: etiquetas sin superposición.
- [ ] Cambio de base en Lineal y Log.
- [ ] Alternar Lineal / Log no cambia la leyenda ni oculta campos.
- [ ] El `Saldo acumulado post-shock` permanece visible en Log y conserva su signo.

### Tasas e inflación

- [ ] Lineal completa: ocho trazas y eje derecho.
- [ ] Log mixta: las mismas ocho trazas; cinco en el eje izquierdo Log y tres saldos en el eje derecho lineal.
- [ ] Lineal desde 2015: hitos 2023 legibles.
- [ ] Log desde 2015: hitos 2023 legibles y correctamente anclados.
- [ ] Alternar Lineal / Log no cambia la leyenda ni oculta campos.
- [ ] Los saldos negativos continúan debajo de cero y los positivos encima; no se transforman ni se invierten.

### EMAE

- [ ] No hay selector en el hero.
- [ ] Existe una sola instancia de `#emaeBase` y `#emaeOriginalToggle`.
- [ ] Ambos están inmediatamente antes del gráfico A.
- [ ] Cambiar base actualiza títulos, ejes y tooltips de A y B.
- [ ] Activar Original muestra la traza en A y B.
- [ ] Layout correcto a 1440, 1024 y 390 px.

## 9. Rueda vertical convertida en scroll horizontal en los menús

Las dos tiras horizontales de navegación:

- `.dash-topic-buttons` (`Explorar por tema`).
- `.tabs` (pestañas del dashboard).

aceptan la rueda vertical del mouse como desplazamiento horizontal cuando el puntero está encima.

Contrato de interacción:

- Si el menú no tiene overflow horizontal, la rueda sigue desplazando la página normalmente.
- Si existe contenido lateral y todavía queda recorrido en la dirección de la rueda, se llama a `preventDefault()` y se actualiza `scrollLeft`.
- Al llegar al inicio o al final, la rueda deja de ser capturada y la página recupera inmediatamente su scroll vertical.
- Si el trackpad entrega `deltaX`, se respeta el eje dominante.
- `Ctrl + rueda` y `Meta + rueda` no se capturan para no interferir con el zoom.
- Se contemplan `deltaMode` en píxeles, líneas y páginas.
- El listener usa `{passive:false}` y se marca una sola vez mediante `data-horizontal-wheel-bound`.

Implementación actual de referencia: `bindHorizontalWheelMenus()`.

Pruebas mínimas:

- [ ] Rueda sobre temas: cambia su `scrollLeft` y no cambia `window.scrollY`.
- [ ] Rueda sobre pestañas: cambia su `scrollLeft` y no cambia `window.scrollY`.
- [ ] En el extremo del menú, la siguiente rueda vuelve a cambiar `window.scrollY`.
- [ ] El gesto horizontal del trackpad continúa funcionando.

## 10. Fuentes normalizadas y auditoría de cobertura · v149

Las 32 pestañas deben presentar una misma ficha conceptual de respaldo, aunque conserven el contenido y los componentes visuales propios de cada módulo.

### Estructura común

- Kicker `Fuentes y trazabilidad`.
- Título `Respaldo visible de esta pestaña`.
- Conteo de referencias temáticas.
- Corte de auditoría.
- Enlace a la auditoría global.
- Leyenda para distinguir:
  - publicación o institución de origen;
  - dato, serie o archivo;
  - auditoría, método o cálculo.

La normalización no reemplaza ni oculta las notas metodológicas existentes. Añade una cabecera compartida y clasifica visualmente los enlaces.

### Cobertura completada

- `Morosidad`: seis archivos/informes BCRA, auditoría reproducible y manifiesto general.
- `Lo que te robó Milei`: mapa propio de la cuenta salarial, pinza, Mercado Libre, SIDE, Senado y auditorías.
- `Grandes fortunas`: enlace WID visible y rutas locales corregidas.
- `EMAE`: enlace directo a su auditoría reproducible.
- `Péndulo`: ficha global por capa con auditorías de finanzas, vivienda, fiscal, activos y CFT/rentabilidad.
- `Rutas` y `Turismo`: sus bloques especiales adoptan la misma cabecera sin perder las explicaciones originales.

### Rutas locales

Los enlaces locales nuevos usan `data-source-path`. `sourceProjectAsset(path)` resuelve la ruta de forma distinta según se abra:

- `index.html` desde la raíz;
- un snapshot `data/dashboard_*.html`.

No volver a escribir esos enlaces como rutas relativas rígidas: rompería una de las dos ubicaciones.

### Implementación

- CSS: `#source-register-v149-style`.
- JS: `#source-register-v149-script`.
- Ficha por tab: `.source-register`.
- Estado: `data-source-coverage="ok"`.
- Auditoría detallada: `data/derivados/AUDITORIA_COBERTURA_FUENTES_V149.md`.

### Aceptación

- [ ] 32 tabs y 32 fichas de fuentes.
- [ ] Cero fichas con `data-source-coverage="missing"`.
- [ ] Ningún enlace de la ficha queda en `href="#"`.
- [ ] Las 16 rutas `data-source-path` existen.
- [ ] Morosidad muestra ocho referencias temáticas.
- [ ] Lo que te robó Milei muestra once referencias temáticas.
- [ ] La ficha responde en escritorio y 390 px.
- [ ] Las rutas locales funcionan desde raíz y desde snapshot.

## 11. Estado verificado de la fuente

- `index.html`: 7.662.027 bytes.
- `data/dashboard_kawaii_149_fuentes_normalizadas.html`: copia byte a byte de `index.html`.
- SHA-256 de ambos al corte: `10f6d4b11cf04a589d0f9ba573ea867826afeb4c01c55b7a9ff1633b8e85f1eb`.
- Trece bloques JavaScript internos analizados sin errores de sintaxis.
- Prueba visual realizada en escritorio y a 390 px.
- Prueba de ejecución: 32 registros, cero faltantes, cero enlaces vacíos; rutas verificadas desde raíz y snapshot.

Si la arquitectura del rediseño cambia IDs o deja de usar Plotly, reproducí la conducta y las invariantes, no necesariamente la implementación literal.

## 12. Leyendas sin scroll y Log completo de Poder adquisitivo · v150

### Regla global de leyendas

- En celular ninguna rutina responsive cambia una leyenda Plotly a orientación vertical.
- Las leyendas con varias series usan orientación horizontal y se envuelven dentro del margen superior del gráfico.
- No ocultar el scrollbar con CSS: la aceptación exige que todas las entradas sean visibles y accesibles, no sólo que desaparezca la barra.
- La prueba móvil recorrió las 32 pestañas y 66 gráficos con leyenda a 390 px: cero scrollbars internos visibles.

### Poder adquisitivo · vista Log

- La leyenda conserva las diez entradas de la vista Lineal.
- Los índices reales positivos usan el eje izquierdo semilogarítmico.
- `Excedente acumulado previo · ventana espejo` y `Pérdida neta acumulada desde shock` permanecen en el eje derecho lineal.
- El eje derecho sigue mostrando valores negativos, cero y positivos: los saldos no se transforman, no se invierten y no desaparecen.
- El selector dice `Log · mismas series` y explica explícitamente la combinación de ejes.

### Aceptación

- [ ] Poder adquisitivo Lineal y Log muestran la misma leyenda de diez series.
- [ ] `Pérdida neta acumulada desde shock` es visible en Log.
- [ ] En Log, el eje izquierdo muestra ticks proporcionales y el derecho mantiene escala lineal con signo.
- [ ] Ninguno de los 66 gráficos con leyenda genera scrollbar interno a 390 px.
- [ ] Escritorio conserva las diez series y ambos ejes sin scrollbar.

### Estado verificado

- `index.html`: 7.662.055 bytes.
- `data/dashboard_kawaii_150_leyendas_sin_scroll_y_log_completo.html`: copia byte a byte de `index.html`.
- SHA-256 de ambos: `ff13a43660f2210b840921cbb816f6c5463ccd4d2b53022e56aac453f57559ea`.
- Trece bloques JavaScript internos presentes.

- Prueba de ejecución: 32 pestañas, 66 gráficos con leyenda, cero scrollbars visibles; Poder Log con diez series y saldo post-shock presente.

## 13. Scroll horizontal separado de los botones · v151

En celular las tiras `.dash-topic-buttons` y `.tabs` conservan el desplazamiento horizontal, pero reservan una canaleta inferior propia para la barra.

- `scrollbar-gutter: stable` evita que la barra invada el contenido.
- `overflow-y: hidden` impide pequeños saltos verticales dentro de la tira.
- Los botones temáticos reservan `11px` inferiores; las pestañas, `14px`.
- La barra WebKit mide `6px`, con pista transparente y pulgar redondeado.
- La rueda vertical convertida en desplazamiento horizontal sigue usando `bindHorizontalWheelMenus()`.

Prueba a 390 px:

- 15 px libres entre el borde inferior de los botones temáticos y el inicio de la barra.
- 19 px libres entre el borde inferior de las pestañas y el inicio de la barra.
- Ningún texto, borde o estado activo queda tapado.

Estado:

- `index.html`: 7.662.478 bytes.
- Snapshot: `data/dashboard_kawaii_151_scroll_menus_con_gutter.html`.
- SHA-256 de ambos: `7faa4fe3fb317d148575974381ee2360a9d1d5a06a42f837726dd62ac64606f7`.

## 14. Carril horizontal visible en las pestañas · v152

La canaleta de v151 evitaba la superposición, pero la pista transparente hacía que el control pareciera ausente. En v152:

- `.tabs` usa `scrollbar-color: #765c7f #eadfeb`.
- La pista WebKit es lavanda y recorre todo el ancho disponible.
- El pulgar es violeta, redondeado y conserva `6px` de alto.
- `.dash-topic-buttons` adopta la misma lógica con menor contraste.
- El padding inferior de v151 se conserva: la barra sigue separada de los botones.

Prueba a 490 px:

- ancho visible de `.tabs`: 443 px;
- ancho desplazable: 3.481 px;
- recorrido horizontal efectivo: 3.038 px;
- carril y pulgar visibles debajo de la pestaña activa.

Estado:

- `index.html`: 7.662.727 bytes.
- Snapshot: `data/dashboard_kawaii_152_scroll_horizontal_visible.html`.
- SHA-256 de ambos: `d31a1e2a4e88d7b3daad2fd3c7fcc3861dd06734c48c7f348a74c9c0cf38a07c`.

## 15. Etiquetas responsive del gráfico de pobreza · v153

El gráfico ya no conserva las anotaciones de escritorio cuando la ventana se achica. `povertyResponsiveMode()` distingue tres composiciones: `desktop`, `compact` y `mobile`.

### Composición compacta y móvil

- Los mandatos se abrevian a `Duhalde`, `Néstor`, `CFK`, `Macri`, `Alberto` y `Milei`.
- Las seis etiquetas alternan entre dos alturas para evitar colisiones.
- Duhalde se ancla hacia la derecha y Milei hacia la izquierda, manteniendo ambos extremos dentro del SVG.
- La nota superior sobre franjas y fuentes se omite porque ya está explicada en la leyenda metodológica inferior.
- El corte de fuente se resume como `INDEC oficial` y se ubica dentro del área trazada.
- Los callouts recientes se acortan en móvil a `Base`, `Pico` y `Último` y siempre apuntan hacia el interior.
- La leyenda usa nombres abreviados y orientación horizontal.

### Reflow real

`responsiveRelayout()` compara el modo actual con `povertyRenderMode`. Si cambia el ancho, vuelve a componer trazas y anotaciones; no deja nombres largos ni offsets de escritorio heredados.

Pruebas realizadas:

- 390 px: todas las etiquetas y callouts dentro del gráfico, sin solapamientos.
- 490 px: cero anotaciones fuera de los límites laterales.
- Escritorio → 490 px: los nombres completos cambian correctamente a abreviados después del resize.

Estado:

- `index.html`: 7.664.040 bytes.
- Snapshot: `data/dashboard_kawaii_153_pobreza_etiquetas_responsive.html`.
- SHA-256 de ambos: `5a0fde1c96b3187252fd39df9992ccaf77018a6ae8f673b821f13033bb5afca0`.

## 16. Asistencia social: etiquetas y espacio superior responsive · v154

Los gráficos `socialLongChart` y `socialChangeChart` ahora usan `socialResponsiveMode()` con modos `desktop`, `compact` y `mobile`.

### Cambios visuales

- Los mandatos se abrevian en anchos reducidos: `Duhalde`, `Néstor`, `CFK`, `Macri`, `Alberto` y `Milei`.
- En móvil alternan entre dos alturas; en compacto usan una fila corta.
- Los extremos se anclan hacia adentro para no salir del SVG.
- Se elimina la etiqueta genérica duplicada de pandemia en compacto/móvil.
- Los callouts `Pandemia · IFE + ATP`, `2024 · 31,13`, `Fin IFE/ATP` y `2024 · −14,19%` usan offsets interiores.
- El margen superior baja de `135px` a `72px` en móvil y a `80px` en compacto.
- La misma recomposición se ejecuta al redimensionar una ventana ya abierta.

Pruebas:

- 390 px: título y gráfico más próximos, sin etiquetas superpuestas.
- 490 px: cero colisiones entre anotaciones en ambos gráficos y cero etiquetas fuera de los límites laterales.
- Escritorio → 490 px: los nombres completos se sustituyen correctamente por abreviaturas.

Estado:

- `index.html`: 7.664.553 bytes.
- Snapshot: `data/dashboard_kawaii_154_asistencia_social_responsive.html`.
- SHA-256 de ambos: `f89a61d21ea4007ed6246e15bbfcf0364d08f890cecc77cd6f0e8bfa02fc49aa`.

## 17. Gini histórico: cabecera y etiquetas responsive · v155

`giniChart` ahora usa `giniResponsiveMode()` con composiciones `desktop`, `compact` y `mobile`.

### Cambios

- El margen superior móvil baja de `155px` a `112px`.
- La leyenda permanece horizontal y abrevia sus dos series largas en anchos reducidos.
- Los mandatos se abrevian y alternan entre dos alturas en móvil.
- Duhalde y Milei se anclan hacia adentro en los extremos del eje.
- La advertencia institucional se resume como `⚠ 2T07–2015 · leer con reservas` y pasa al interior del área trazada.
- Los rótulos metodológicos verticales se acortan a `EPH puntual`, `hiato` y `cobertura`.
- `responsiveRelayout()` actualiza anotaciones y nombres de leyenda al achicar una ventana ya renderizada.

Pruebas:

- 390 px: cero colisiones y cero etiquetas fuera del gráfico.
- Escritorio → 490 px: nombres presidenciales y leyenda se compactan correctamente.
- El gráfico comparativo inferior conserva todos sus rótulos dentro del contenedor.

Estado:

- `index.html`: 7.665.541 bytes.
- Snapshot: `data/dashboard_kawaii_155_gini_responsive.html`.
- SHA-256 de ambos: `cecf46d589a965c7620e2672f09a61b6c8a74937f2f33fb7dddece4e48e2457c`.

## 18. Kicker de cabecera: menos píldora y más aire · v156

Se normalizó el componente `.kicker` que acompaña a los títulos de las tarjetas. No se modificaron badges pequeños ni componentes especializados como `.pend-kicker` o `.rates-public-kicker`.

### Cambios visuales

- El radio baja de `999px` a `12px`: las frases de varias líneas pasan de una píldora angosta a un rectángulo suave.
- El padding base sube de `6px 10px` a `8px 13px`.
- Se fija `line-height: 1.35`, `box-sizing: border-box` y `overflow-wrap: anywhere` para sostener frases largas sin tocar el borde.
- Hasta 980 px el ancho máximo aumenta de `160px` a `190px`.
- Hasta 720 px la cabecera reparte el espacio de forma flexible: el título puede encogerse sin desbordar y el kicker usa hasta `min(42%, 168px)` con `8px 11px` de padding.
- Hasta 420 px conserva el 42% disponible y `7px 9px` de padding; ya no queda encerrado en el límite fijo anterior de `104px`.

### Alcance y pruebas

- Auditoría DOM: 129 kickers de cabecera distribuidos en las 32 pestañas.
- 390 × 844 px: cero textos cortados, cero salidas laterales y cero solapamientos con el título.
- 1280 × 900 px: los mismos tres controles terminan en cero problemas.
- Caso señalado, `comparaciones más compatibles · mismo trimestre cuando es posible`: 120,5 px de ancho, 70 px de alto, radio de 12 px y padding de `7px 9px` a 390 px.

Estado:

- `index.html`: 7.665.791 bytes.
- Snapshot: `data/dashboard_kawaii_156_kickers_responsive.html`.
- SHA-256 de ambos: `a6605c73e01f5ac610c3a9902df541e542608f09d7fbaef79869857602d0127f`.
- Trece bloques JavaScript internos presentes.

## 19. Estratos de ingresos en CABA: cabecera y mandatos responsive · v157

El gráfico `structureCabaChart` deja de usar la composición móvil heredada que reservaba 165 px superiores y alineaba todos los mandatos en una sola fila.

### Cambios

- Se incorpora `structureCabaResponsiveMode()` con modos `desktop`, `compact` y `mobile` según ventana y ancho real del gráfico.
- El margen superior móvil baja de `165px` a `120px`.
- La leyenda es horizontal en todos los modos y abrevia en compacto/móvil `No pobre vulnerable` y `Sector medio “clase media”` como `Vulnerables` y `Sector medio`.
- `structureCabaAnnotations()` compone de nuevo las etiquetas presidenciales:
  - abrevia los nombres en compacto y móvil;
  - alterna dos alturas en móvil;
  - ancla CFK hacia la derecha desde el inicio y Milei hacia la izquierda desde el final;
  - agrega fondo, borde y padding para separarlas de las áreas apiladas.
- `responsiveRelayout()` actualiza margen, leyenda, nombres y anotaciones al cambiar el ancho de una ventana ya abierta.

### Pruebas

- 390 px: la leyenda comienza 11 px debajo de la cabecera; los cuatro mandatos quedan dentro del gráfico, sin colisiones.
- 490 px: hueco cabecera–leyenda de 25,4 px, ninguna etiqueta fuera del contenedor.
- 1280 px: regresan los nombres completos; cero colisiones y cero salidas laterales.

Estado:

- `index.html`: 7.667.592 bytes.
- Snapshot: `data/dashboard_kawaii_157_estratos_caba_responsive.html`.
- SHA-256 de ambos: `bffd07c93db00fc1e4b350a6082c9f48fc2fa30d1e98be37cb3622ccb840daf1`.
- Trece bloques JavaScript internos presentes.

## 20. Movilidad de pobreza UCA: cabecera compacta · v158

Se corrige el segundo gráfico del tab `Más allá de la pobreza`, que todavía conservaba 150 px de margen superior y una leyenda vertical en móvil.

### Cambios

- `structureMobilityChart` usa leyenda horizontal en todos los anchos.
- En compacto/móvil, los nombres se abrevian a `Nunca pobre`, `Salió`, `Entró` y `Pobre ambos`; el hover conserva las descripciones completas.
- `structureMobilityTopMargin()` adapta el espacio a las filas reales de la leyenda:
  - hasta 420 px: `98px`;
  - entre 421 y 720 px: `82px`;
  - escritorio: `105px`.
- El kicker `panel UCA · mismas personas/hogares · 2024 → 2025` recibe la variante `.structure-panel-kicker`:
  - radio de `9px`;
  - padding móvil de `8px 10px`;
  - ancho máximo flexible de `min(44%, 180px)`.
- `responsiveRelayout()` actualiza nombres, margen y leyenda cuando cambia el ancho de la ventana.

### Pruebas

- 390 px: separación cabecera–leyenda de 19,8 px.
- 490 px: separación de 20,6 px, frente a los 38,8 px que quedaban antes del ajuste adaptativo.
- 1280 px: nombres completos, sin desbordes.
- En los tres anchos: kicker sin overflow, título sin superposición y leyenda dentro del gráfico.

Estado:

- `index.html`: 7.668.463 bytes.
- Snapshot: `data/dashboard_kawaii_158_movilidad_uca_responsive.html`.
- SHA-256 de ambos: `197b8be49f4431e6663a849a29dcfd2e5b4160c1d46386763734cf14f328884a`.
- Trece bloques JavaScript internos presentes.

## 21. Kicker UCA/NSE rectangular · v159

El rótulo `UCA · 2025 · pobreza monetaria vs. estrés económico por NSE del hogar` adopta la clase `.structure-panel-kicker`, igual que el panel de movilidad UCA.

- Radio: `9px` en lugar de los `12px` generales.
- Padding móvil: `8px 10px`.
- Ancho máximo móvil: `min(44%, 180px)`.
- Prueba a 390 px: sin corte, desborde ni superposición con el título.

Estado:

- `index.html`: 7.668.485 bytes.
- Snapshot: `data/dashboard_kawaii_159_kicker_uca_nse.html`.
- SHA-256 de ambos: `84385c24e02b1e2e944d6cfa5539e5104cdd184f37a96c6388e5a5b43ab77802`.
- Trece bloques JavaScript internos presentes.

## 22. Comparador GBA–CABA: subtítulo separado de los valores · v160

En `familyGeoChart`, la anotación `jul-2026 · hogares de referencia distintos` estaba en `y=.98`, dentro de la misma franja ocupada por los valores externos `$1,565 M` y `$1,618 M`.

### Cambios

- La anotación pasa al margen superior del gráfico:
  - móvil: `y=1.10`;
  - escritorio: `y=1.08`;
  - `yanchor: bottom`.
- El margen superior aumenta de `55px` a `72px` en móvil y de `45px` a `58px` en escritorio para alojar el subtítulo fuera del área de datos.
- `responsiveRelayout()` conserva esta separación al cambiar el tamaño de la ventana.

### Pruebas

- 390 px: 40 px entre el subtítulo y el valor de barra más cercano.
- 490 px: 40,3 px.
- 1280 px: 37,5 px.
- Cero colisiones y cero etiquetas fuera del SVG en los tres anchos.

Estado:

- `index.html`: 7.668.684 bytes.
- Snapshot: `data/dashboard_kawaii_160_geo_gba_caba_etiquetas.html`.
- SHA-256 de ambos: `a056bdf7a48159735f08df595468d028a8f88ad93d08307e8de574ba7369f871`.
- Trece bloques JavaScript internos presentes.

## 23. Sistema tipográfico transversal · v161

Se hizo una auditoría completa de la tipografía renderizada en los 32 tabs y se agregó una única capa final de normalización: `#typography-system-v161`. La intención no es igualar todo, sino sostener una jerarquía semántica estable entre portada, títulos de tab, títulos de tarjeta, secciones, texto de lectura, notas, metadatos, controles, tablas y cifras.

### Diagnóstico de partida

- 28 bloques CSS internos.
- 778 declaraciones de `font-size` y 81 tamaños declarados distintos.
- 293 combinaciones renderizadas de tamaño, interlineado y peso en escritorio.
- Variantes efectivas de Arial, Inter y monospace mezcladas entre módulos antiguos y nuevos.
- Textos HTML de 7–9,8 px concentrados especialmente en Péndulo, Rutas, Turismo y Morosidad.

### Escala y reglas incorporadas

- Familia de interfaz única: `Inter, ui-rounded, "Segoe UI", system-ui, sans-serif`.
- Familia técnica única: `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` para código y fórmulas.
- Escala base de escritorio:
  - display/portada: `clamp(32px, 4.3vw, 58px)`;
  - título de página: `32px`;
  - título de tab: `24px`;
  - título de tarjeta: `21px`;
  - sección: `18px`;
  - subtítulo: `14px`;
  - cuerpo: `14px`;
  - lectura continua: `13px`;
  - apoyo: `12px`;
  - metadato: `11px`;
  - microtexto: `10px`;
  - tabla: `11px`.
- Escala móvil específica: página `26px`, tab `21px`, tarjeta `18px`, sección `17px`, cuerpo `13px`, lectura `12px`, apoyo `11,5px` y tabla `10,5px`.
- Piso de legibilidad HTML: `10px`. Las anotaciones de Plotly conservan sus tamaños propios porque dependen del espacio interno del gráfico.
- Controles y botones pasan a Inter, `12px`, peso fuerte e interlineado común.
- KPI, montos, métricas, tablas, fuentes, badges y notas reciben tamaños por función, no por tab.
- Los títulos preservan pesos altos y un interlineado compacto; las notas y lecturas usan un interlineado más abierto.
- Se mantienen excepciones semánticas necesarias, como las celdas móviles de Inflación por presidencia en `14px`.

### Compatibilidad de módulos heredados

- Se elevaron a la nueva escala los microtextos de Péndulo, Rutas, Turismo, Morosidad, Tasas, Poder adquisitivo, Grandes fortunas y Lo que te robó Milei.
- Los valores grandes, títulos, botones y spans internos heredan el rol de su contenedor para evitar que una regla de microtexto achique cifras o corazones de encabezado.
- `Actividad real` recibió además `min-width:0`, ancho máximo y `box-sizing` en sus paneles: un hijo de grid heredado expandía el hero a unos 1.098 px en móvil y el `overflow:hidden` global ocultaba el problema.
- En móvil, los encabezados de Actividad, Rutas y Turismo separan badge/kicker y título con un margen constante.

### Auditoría responsive final

Se abrieron y recorrieron los 32 tabs en cada ancho:

- `390 × 844 px`: cero desbordes del documento, cero textos fuera de su contenedor, cero recortes, cero cruces título/kicker y cero textos HTML menores a 10 px.
- `490 × 900 px`: cero desbordes, salidas laterales, recortes o cruces de encabezado.
- `1280 × 900 px`: cero desbordes, recortes y textos HTML menores a 10 px.

La comprobación distingue los gráficos y contenedores horizontalmente desplazables intencionales de un desborde real de página.

Estado:

- `index.html`: 7.678.305 bytes.
- Snapshot: `data/dashboard_kawaii_161_tipografia_normalizada.html`.
- SHA-256 de ambos: `772984fd61add79a74910b19855cda69a06ec5461ff61f6becdfab1da5805275`.
- Trece bloques JavaScript internos presentes.

## 24. Salud y educación: gráfico principal sin aire sobrante · v162

Se compactaron los márgenes internos de `healthEducationChart`, tanto en su render inicial como en `resizeHealthEducationCharts()`.

### Cambios

- Margen superior móvil: `175px → 116px`.
- Margen superior de escritorio: `130px → 96px`.
- Margen inferior: `78/72px → 44px` en ambos modos.
- No se redujo la altura del gráfico ni el área disponible para las series: el espacio recuperado pasa al área de datos.
- Se mantienen separadas la leyenda de tres filas, los rótulos presidenciales y el eje X.

### Pruebas

- 390 px: 20 px entre cabecera y leyenda; 20 px entre el eje X y la nota metodológica.
- 490 px: 20 px en ambos extremos.
- 1280 px: 21 px entre cabecera y leyenda; 27 px entre eje y nota.
- Cero desborde horizontal en los tres anchos.

Estado:

- `index.html`: 7.678.281 bytes.
- Snapshot: `data/dashboard_kawaii_162_salud_educacion_espaciado.html`.
- SHA-256 de ambos: `7180ff47bde19ac9a3994961f9aedf572159b84ee397888f1fe1bad621a5fe74`.
- Trece bloques JavaScript internos presentes.

## 25. Salud y educación: categorías de ejecución responsive · v163

El gráfico `healthEducationExecutionChart` usaba categorías diferentes según el ancho detectado al renderizar. Si se abría en escritorio y luego se achicaba la ventana, `resizeHealthEducationCharts()` reducía el margen izquierdo pero no reemplazaba las etiquetas largas: los textos quedaban cortados a ambos lados.

### Cambios

- Las categorías de datos permanecen estables y completas:
  - `Educación + cultura + ciencia y técnica`;
  - `Salud total GPC`;
  - `Atención pública de la salud`.
- El eje Y usa `tickvals` estables y cambia sólo la presentación móvil a:
  - `Educación`;
  - `Salud total`;
  - `Salud pública`.
- Los tooltips conservan las denominaciones completas.
- La actualización de `ticktext` también se ejecuta al redimensionar una ventana ya abierta.

### Pruebas

- Apertura directa a 490 px: las tres etiquetas quedan dentro del gráfico.
- Recorrido 1280 → 490 px: las etiquetas largas cambian a las breves sin recargar la página.
- Cero desborde horizontal.

Estado:

- `index.html`: 7.678.635 bytes.
- Snapshot: `data/dashboard_kawaii_163_salud_etiquetas_ejecucion.html`.
- SHA-256 de ambos: `d54cf43a0e067a2918516ee1323177637293fc69e63fd8527dee4f8fb05869aa`.
- Trece bloques JavaScript internos presentes.

## 26. Salud y educación: rótulo 1T-2026 legible · v164

La anotación `1T 2026 parcial` de `healthEducationBridgeChart` estaba dentro del área de datos, en dos líneas, con 8 px en móvil y anclada al último punto del extremo derecho.

### Cambios

- Se crea `heProvPartialAnnotation()` para compartir exactamente la misma composición entre render y resize.
- El rótulo pasa al margen inferior derecho mediante coordenadas de papel.
- Texto en una sola línea: `◆ 1T 2026 · parcial`.
- Tamaño estable de 11 px, fondo casi opaco, borde visible y padding de 5 px.
- `xanchor:'right'` evita que el texto se salga por el extremo final del eje.

### Pruebas

- 390, 490 y 1280 px: caja completamente dentro del gráfico.
- Cero desborde horizontal.
- No tapa las líneas, los diamantes de 2026 ni las etiquetas del eje X.

Estado:

- `index.html`: 7.678.687 bytes.
- Snapshot: `data/dashboard_kawaii_164_salud_1t2026_legible.html`.
- SHA-256 de ambos: `716c28cde9b069a3bbcfcfc5e34b5718ede6f2d2fd4d2205a94aaab10b45a0c8`.
- Trece bloques JavaScript internos presentes.

## 27. Consumo: composición vertical y etiquetas responsive · v165

El gráfico principal de Consumo acumulaba demasiado aire entre la cabecera, la leyenda, el área de datos y el pie. En móvil, además, los rótulos presidenciales, la pandemia, la referencia `2023 = 100` y el dato parcial de 2026 competían por el extremo superior/derecho.

### Cambios

- Altura del gráfico: `500px` en escritorio y `440px` en móvil.
- Márgenes internos:
  - móvil: `l 48 · r 12 · t 120 · b 48`;
  - escritorio: `l 72 · r 28 · t 104 · b 58`.
- La leyenda pasa a disposición horizontal también en móvil y ocupa una franja propia por encima de los mandatos.
- Los rótulos presidenciales se acercan al área de datos, reducen tamaño/padding en móvil y permanecen separados entre sí.
- La etiqueta de pandemia baja a una segunda altura dentro del gráfico.
- `base 2023 = 100` pasa a ser una referencia interna, a la derecha y fuera de la franja de mandatos.
- El dato coyuntural deja de quedar anclado fuera del último año y se convierte en una caja interna legible: `1T-2026 parcial · +2,7% ia · +0,8% t/t`.
- `renderConsumption()` y `resizeConsumptionChart()` comparten la misma geometría y las mismas anotaciones; el resultado se mantiene al redimensionar sin recargar.

### Pruebas

- 390, 490 y 1280 px: cero intersecciones entre anotaciones.
- Todas las anotaciones quedan dentro del rectángulo del gráfico en los tres anchos.
- Cero desborde horizontal de la página.
- La cabecera y el pie quedan contiguos al contenedor del gráfico; el aire visible restante pertenece únicamente a la leyenda, los ejes y sus etiquetas.

Estado:

- `index.html`: 7.679.146 bytes.
- Snapshot: `data/dashboard_kawaii_165_consumo_responsive_etiquetas.html`.
- SHA-256 de ambos: `53b1bec799bd8d846459952c508b0df956bd507109dea289cb47bc14c23c25f0`.
- Trece bloques JavaScript internos presentes.

## 28. Consumos físicos: menos aire y rótulos contenidos · v166

El gráfico `physicalCategoryChangeChart` conservaba un margen superior de `92px` en móvil aunque no tiene leyenda. Eso separaba visualmente la cabecera del contenido y dejaba la aclaración metodológica flotando en una franja demasiado alta.

### Cambios

- Margen superior: `92px → 44px` en móvil y `72px → 50px` en escritorio.
- La aclaración `Misma pregunta…` queda centrada y contenida en el ancho del gráfico.
- El valor negativo del vino se dibuja dentro de la barra para que no se pegue al nombre de la categoría.
- Se incorpora `physicalCategoryAnnotation()` como composición compartida.
- `resizeConsumptionCategoryCharts()` actualiza márgenes y anotación al cruzar el breakpoint, además de redimensionar el lienzo.

### Pruebas

- 390, 490 y 1280 px: aclaración completamente visible y sin desborde horizontal.
- Recorrido 390 → 1280 → 490 px sin recargar: se mantiene la geometría responsive correcta.
- En 390 px quedan aproximadamente 22 px entre el final de la cabecera y la aclaración.
- Todos los valores de las barras permanecen dentro del contenedor.

Estado:

- `index.html`: 7.679.707 bytes.
- Snapshot: `data/dashboard_kawaii_166_consumos_fisicos_espaciado.html`.
- SHA-256 de ambos: `6fb3ce408f750f54f5d82dbab468e22a8c4eb3f883510987b1369e5389e285af`.
- Trece bloques JavaScript internos presentes.

## 29. Lácteos y huevos: compactación vertical responsive · v167

El gráfico `dairyEggChart` reservaba `145px` arriba y `68px` abajo en móvil. La leyenda quedaba alejada de la cabecera y las etiquetas del eje X demasiado separadas de las tarjetas de lectura.

### Cambios

- Altura: `455px → 440px` en escritorio y `430px → 410px` en móvil.
- Márgenes:
  - móvil: `t 145 → 110` y `b 68 → 36`;
  - escritorio: `t 105 → 55` y `b 58 → 42`.
- La leyenda horizontal de escritorio baja de `y 1.14` a `1.06`; en móvil conserva su disposición vertical.
- La nota de 2026 pasa a estar centrada dentro del borde superior del área de datos.
- En móvil se abre en dos líneas: distingue estimación de lácteos, referencia vigente de huevos y aclara que no es un cierre anual.
- Se crea `dairyEggAnnotation()` y el resize actualiza altura CSS, márgenes, leyenda y anotación al cruzar el breakpoint.

### Pruebas

- 390 px: 12 px entre cabecera y leyenda, 14 px entre leyenda y nota, y 36 px entre el eje X y la primera tarjeta.
- 490 y 1280 px: leyenda y nota completamente contenidas.
- Recorrido 390 → 1280 → 490 px sin recargar: la disposición responde correctamente.
- Cero desborde horizontal.

Estado:

- `index.html`: 7.680.362 bytes.
- Snapshot: `data/dashboard_kawaii_167_lacteos_huevos_espaciado.html`.
- SHA-256 de ambos: `59c12ff498bbd08e307b48f9370c72fbbfa268d463f2cae7d83e6b9967350c79`.
- Trece bloques JavaScript internos presentes.

## 30. Autos 0 km: dos tramos, ancho útil y eje legible · v168

El gráfico histórico de patentamientos usaba el año calendario como distancia continua. Como sólo hay datos verificados para 2002–2007 y 2024–2026, casi todo el ancho representaba años vacíos; los puntos quedaban comprimidos en ambos extremos y las etiquetas del eje se superponían.

### Cambios

- Se reemplaza la distancia cronológica continua por posiciones visuales discretas para los dos tramos verificados.
- Entre 2007 y 2024 se mantiene un casillero explícito `⋯`, por lo que el gráfico no sugiere continuidad ni inventa observaciones.
- La explicación del hueco pasa a una caja dentro del espacio vacío: `sin datos · 2008–2023`.
- Los tooltips conservan los años reales mediante `customdata`.
- En móvil, los cierres recientes usan `2024`, `’25` y `’26*` para evitar colisiones sin perder la secuencia.
- El dato parcial `339k YTD` se ubica a la izquierda del rombo final y queda dentro del gráfico.
- La leyenda recibe una separación adicional respecto de la descripción, pero se acerca al área de datos.
- Altura del gráfico: `410px` en escritorio y `390px` en móvil.
- Márgenes móvil: `l 44 · r 20 · t 88 · b 40`; se elimina el título vertical del eje Y en móvil para ampliar el área útil.
- `resizeConsumptionCategoryCharts()` actualiza ticks, márgenes, leyenda y anotación al cruzar el breakpoint.

### Pruebas

- 390, 490 y 1280 px: cero superposiciones entre etiquetas del eje X.
- Cero superposiciones entre valores de puntos y la caja del período sin datos.
- Leyenda y anotación completamente contenidas.
- Recorrido 390 → 1280 → 490 px sin recargar: conserva la composición correcta.
- Cero desborde horizontal.

Estado:

- `index.html`: 7.681.597 bytes.
- Snapshot: `data/dashboard_kawaii_168_autos_historia_responsive.html`.
- SHA-256 de ambos: `0d7d897ccf7d7041b1da0bb9967ba30110d5e5aa9d59dd524e26a9287137c1ee`.
- Trece bloques JavaScript internos presentes.

## 31. Barrido responsive global de las 32 pestañas · v169

Se hizo una revisión transversal de todos los tabs en móvil (`390 × 844`) y escritorio (`1280 × 900`). La búsqueda automatizada recorrió cada gráfico Plotly y comprobó tres fallas repetidas: textos fuera del lienzo, intersecciones entre anotaciones y solapamientos entre etiquetas del eje X. Después se inspeccionaron visualmente muestras de los paneles más densos.

### Patrones globales corregidos

- Se compactaron alturas y márgenes verticales en los gráficos de consumos, trabajo, vivienda, BCRA y morosidad que todavía reservaban aire propio de escritorio al verse en móvil.
- Los redimensionadores ahora recalculan no sólo el lienzo, sino también márgenes, leyendas, ticks, notas y etiquetas de mandatos cuando se cruza el breakpoint.
- Se escalonaron nombres presidenciales en series largas cuando dos períodos cortos quedaban demasiado próximos.
- Los textos extensos de ejes categóricos usan abreviaturas sólo en móvil; escritorio conserva la denominación completa.
- Las anotaciones políticas o metodológicas próximas al borde se movieron al interior del área segura del gráfico.

### Ajustes por familia

- **Consumos:** carnes apiladas, historia larga, vino, autos históricos, lácteos/huevos, combustibles, bienes durables y comparaciones físicas comparten una composición más compacta. Las etiquetas de totales se separaron de las líneas y se añadieron franjas de mandatos a las series históricas que las necesitaban.
- **Trabajo y vivienda:** se redujo el aire superior/inferior y se adaptaron etiquetas de mandatos y pandemia.
- **BCRA:** reservas, intervención, factores y tasas reciben alturas y márgenes móviles homogéneos; las etiquetas de gobiernos quedan contenidas.
- **Morosidad:** se compactaron los ocho gráficos, se acortaron snapshots categóricos en móvil y se apartó el último dato de la etiqueta de Milei.
- **Pobreza, asistencia social y Gini:** se corrigieron llamadas, leyendas, barras categóricas y comparaciones por mandato; la nota de pandemia se abrevia en móvil.
- **Estructura social y familia:** las regiones pasan a `Pamp.` y `Patag.` en móvil para evitar choques, sin modificar datos ni tooltips.
- **Inversión:** Duhalde y Néstor se muestran en alturas alternadas en móvil.
- **EMAE:** los cortes por mandato usan rótulos cortos en pantallas angostas.
- **Péndulo:** se escalonaron bandas históricas y promedios de Alberto/Milei para conservar todas las lecturas sin superposición.

### Verificación

- Auditoría móvil completa: 32/32 tabs sin textos fuera del gráfico, anotaciones superpuestas ni ticks encimados.
- Auditoría de escritorio completa: 32/32 tabs con el mismo resultado.
- Revisión visual adicional en asistencia social y consumos históricos.
- Validación sintáctica: 13 bloques JavaScript internos compilables.

Estado:

- `index.html`: 7.690.278 bytes.
- Snapshot: `data/dashboard_kawaii_169_barrido_responsive_global.html`.
- SHA-256 de ambos: `ea926642bd098354d319b64bdc741580b4d55a67f960ffa255a5bb30030c484a`.
- Trece bloques JavaScript internos presentes.

## 32. Storytelling · la historia detrás del dashboard · v170

Se incorpora una pestaña editorial llamada **La historia del dashboard**. No es un resumen estadístico nuevo ni una nueva cuenta: organiza en primera persona el recorrido que llevó desde el primer gráfico salarial hasta la lectura transversal del shock, la recuperación, la pinza financiera, la pobreza, el Péndulo y las alternativas distributivas.

### Estructura narrativa

- Hero con autoría explícita de Miyu Rory y una introducción breve sobre el propósito del proyecto.
- Navegación horizontal y pegajosa por capítulos; en móvil conserva desplazamiento lateral y no fuerza saltos de línea ilegibles.
- Cinco cifras de orientación, todas provenientes de cálculos ya auditados en otros tabs:
  - pérdida bruta: `$18,43 B`;
  - recuperado después: `$6,08 B`;
  - brecha salarial restante: `$12,35 B`;
  - diferencial financiero: `$3,92 B`;
  - faltante luego de contrafactuales auditados: `$4,98 B`.
- Nueve capítulos: origen, primer gráfico salarial, tasas y morosidad, pobreza, Péndulo, costo del shock, crecimiento del dashboard, alternativas/riqueza y conclusión.
- Llamadas a acción que abren los tabs especializados mediante `activateTab(...)`; el relato no duplica los cálculos ni sus controles.
- Cierre editorial: ordenar las cuentas y decidir quién paga son preguntas distintas.

### Reglas semánticas que deben conservarse

- El relato está escrito en primera persona y no debe convertirse en una voz institucional impersonal.
- Los importes funcionan como mojones narrativos, no como componentes automáticamente sumables.
- `$3,92 B` no se presenta como ganancia bancaria ni como dinero apropiado por una única entidad: es el diferencial auditado entre ventanas del balance ampliado de crédito y ahorro minorista.
- Bancos y fintech permanecen distinguidos cuando las fuentes, universos o períodos no coinciden.
- La caída de pobreza y el movimiento del Péndulo se presentan como hallazgos que contradijeron una expectativa inicial; no se reescribe retroactivamente la pregunta.
- Los huecos, límites metodológicos y resultados incómodos se conservan visibles.

### Componentes de interfaz

- Estilos encapsulados en `#storytelling-v170-style` y bajo `#tab-story`.
- Botón superior con `data-tab="tab-story"` y rótulo `La historia del dashboard`.
- El tab forma parte del grupo temático `Destacados`.
- Timeline vertical con numeración, tarjetas de giro narrativo, citas, principios editoriales y botones a los módulos relacionados.
- Breakpoints específicos a 900, 720 y 430 px: hero de una columna, KPIs 2×n y luego 1×n, capítulos más compactos y navegación horizontal.

### Fuentes y trazabilidad

El panel de fuentes del tab declara que se trata de un relato editorial y enlaza:

- el repositorio público;
- la auditoría global de cobertura de fuentes;
- la auditoría de escalas Log y jerarquía visual.

El handover permanece como documentación interna del proceso de rediseño y no debe mostrarse como fuente dentro del dashboard público.

La normalización de fuentes debe contabilizar **33 pestañas**, con 33 fichas válidas y cero faltantes. Los números del relato conservan como fuente efectiva los tabs temáticos y sus auditorías.

### Pruebas de aceptación

- El tab debe abrirse desde el menú principal y permanecer visible dentro de `Destacados`.
- Los nueve capítulos y los cinco indicadores deben estar presentes.
- Los botones internos deben activar el tab temático correcto.
- A 390 × 844 y 1280 × 900 no debe existir desborde horizontal del documento.
- La navegación de capítulos puede desplazarse lateralmente en móvil sin tapar contenido.
- La ficha de fuentes debe terminar con `data-source-coverage="ok"`.

Estado final de v170:

- `index.html`: 7.714.301 bytes.
- Snapshot: `data/dashboard_kawaii_170_storytelling.html`.
- SHA-256 de ambos: `9018071ce1c2a516a53096447fd4d2bba72e8b0fd16b12ac4826de33f68bf64a`.
- Trece bloques JavaScript internos presentes y compilables.
- Auditoría responsive del nuevo tab: 390 × 844 y 1280 × 900 sin desborde horizontal.
- Registro de fuentes: 33 fichas, cero faltantes; la ficha de Storytelling queda en estado `ok`.

## 33. Storytelling como pestaña inicial · v171

- `tab-story` pasa a ser el único botón y panel con clase `active` en el HTML inicial.
- `tab-power` deja de estar activo al cargar, pero conserva intactos sus datos, controles y acceso desde el menú o desde el relato.
- La navegación temática continúa iniciando en `Destacados`, grupo que contiene a Storytelling.
- Una carga limpia abre efectivamente `tab-story`; no se depende de un clic simulado, estado persistido ni redirección posterior.

Estado final de v171:

- `index.html`: 7.714.301 bytes.
- Snapshot: `data/dashboard_kawaii_171_storytelling_inicio.html`.
- SHA-256 de ambos: `e3f01a7ad268474a28b91469317a51cde296352e513a51d081eacdc3496720fb`.
- Trece bloques JavaScript internos presentes y compilables.
- Prueba de carga limpia: botón activo `tab-story`, panel activo `tab-story`, grupo activo `featured` y `tab-power` oculto hasta seleccionarlo.

## 34. Rueda vertical → desplazamiento horizontal en los menús · v172

La barra de tabs y el selector temático ya mostraban scrollbar horizontal, pero el gesto de rueda podía quedar neutralizado por el `scroll-snap` o no llegar al listener del contenedor.

- El listener pasa a captura global sobre `document` y sólo actúa si el origen del gesto está dentro de `.tabs` o `.dash-topic-buttons`.
- Se normalizan `deltaX`, `deltaY`, `wheelDelta`, `detail` y `deltaMode` para mouse tradicional, trackpad y navegadores con eventos heredados.
- Los movimientos demasiado pequeños reciben un paso mínimo de 28 px.
- `scroll-snap-type` se suspende mientras gira la rueda y se restaura 170 ms después, evitando que el carrusel vuelva al mismo botón.
- En los extremos, la rueda vuelve a desplazarse verticalmente por la página: no se captura un gesto que ya no puede mover el menú.
- Ctrl/⌘ + rueda se conserva para zoom y no se intercepta.

Estado final de v172:

- `index.html`: 7.715.130 bytes.
- Snapshot: `data/dashboard_kawaii_172_scroll_rueda_tabs.html`.
- SHA-256 de ambos: `a9556291c193e11576ac1f22e877fd8551f9e3bff1305b612e23d0e321174829`.
- Trece bloques JavaScript internos presentes y compilables.

## 35. Barrido de botoneras horizontales · v173

Se recorrieron las 33 pestañas a 390 × 844 y se inventariaron todos los elementos con `overflow-x` efectivo. Además de los dos menús superiores, se encontraron tres botoneras que necesitaban el mismo comportamiento:

- navegación por capítulos de Storytelling: `.story-nav`;
- selector de capas del Péndulo: `.pend-layer-nav`;
- selector interno de vista del Péndulo: `.pend-controls-near-chart .pend-control`.

Todas quedan centralizadas en `HORIZONTAL_WHEEL_MENU_SELECTOR` y usan el mismo conversor de rueda vertical a movimiento horizontal. El barrido también encontró tablas y lienzos de gráficos con desplazamiento lateral; no se incorporan al selector porque no son botoneras y capturar su rueda impediría el desplazamiento vertical normal de la página.

Estado final de v173:

- `index.html`: 7.715.271 bytes.
- Snapshot: `data/dashboard_kawaii_173_scroll_rueda_botoneras.html`.
- SHA-256 de ambos: `bf498420f74d2f655a2e7de33da165395be333ce281f64019e17ec450bd0b629`.
- Trece bloques JavaScript internos presentes y compilables.
- Cobertura móvil confirmada: navegación temática, tabs principales, Storytelling y las dos familias de controles del Péndulo quedan registradas con `data-horizontal-wheel-bound="1"`.

## 36. Fuentes públicas de Storytelling · v174

- Se elimina del registro visible de Storytelling el enlace al handover consolidado.
- El handover continúa existiendo como documentación interna para la instancia de rediseño, pero no se presenta como evidencia ni fuente pública.
- La ficha editorial conserva tres referencias temáticas: repositorio público, auditoría global de fuentes y auditoría visual/metodológica.
- La auditoría de cobertura se actualiza para declarar explícitamente esta separación.

Estado final de v174:

- `index.html`: 7.715.118 bytes.
- Snapshot: `data/dashboard_kawaii_174_fuentes_publicas_storytelling.html`.
- SHA-256 de ambos: `0bc2fc67075c2026ee8760b2af169eb8425c1d3f081f0480e3ed79cfb23f4c99`.
- Trece bloques JavaScript internos presentes y compilables.
- Storytelling conserva `data-source-coverage="ok"` y no contiene enlaces ni rótulos visibles con la palabra `handover`.

## 37. Etiquetas móviles de Tasas e inflación · Log y Lineal · v175

- El corte del 10/12 se muestra en móvil como una caja compacta sin flecha; la franja superior ya identifica a Milei.
- La llamada `ene–nov 148,1%` se desplaza a la izquierda y abajo.
- La llamada `dic-23 +25,5%` se desplaza a la derecha y arriba.
- Las posiciones conservan el sistema de coordenadas correcto para el eje Log; las anotaciones siguen ancladas a sus valores.
- Escritorio mantiene los textos completos y la composición anterior.

Estado final de v175:

- `index.html`: 7.715.082 bytes.
- Snapshot: `data/dashboard_kawaii_175_tasas_log_etiquetas_mobile.html`.
- SHA-256 de ambos: `2c08ccc18c1c64365db9e25ea56c2981a5987b3c399d4fc852d92e1221354c6e`.
- Trece bloques JavaScript internos presentes y compilables.
- Pruebas geométricas a 390 y 320 px: cero intersecciones y cero anotaciones fuera del gráfico en las vistas Log y Lineal.

## 38. Referencia cero del gráfico de tasas reales · v176

- `0 = iguala la inflación` sube 34 px en móvil y 28 px en escritorio.
- El texto cambia a marrón oscuro `#704300`.
- Se incorpora fondo crema semitransparente, borde ámbar y anclaje izquierdo para separarlo de las series.
- La línea de cero conserva su posición y significado.

Estado final de v176:

- `index.html`: 7.715.210 bytes.
- Snapshot: `data/dashboard_kawaii_176_tasas_cero_legible.html`.
- SHA-256 de ambos: `344852421c140104b6f80335fb25ec91bc0b634fbdcecb5b71cce046730895b8`.
- Trece bloques JavaScript internos presentes y compilables.
- Verificación a 390 px y 1280 px: 28 px libres entre el rótulo y la línea, sin salir del lienzo.

## 39. Pobreza absoluta · compactación vertical móvil · v177

- Se reduce el alto móvil de `#povertyChart` de 540 a 440 px.
- El margen superior móvil baja de 245 a 185 px y el inferior de 72 a 38 px.
- La reducción conserva prácticamente intacta la altura útil del área de datos: se elimina espacio vacío, no información.
- La leyenda queda a 34 px del título en 390 px y a 32 px en 320 px.
- El bloque completo de la tarjeta se acorta 100 px respecto de v176; la guía metodológica queda a 8 px del contenedor del gráfico.
- Se actualiza también la rama de `Plotly.relayout` para que un cambio de ancho no restaure los márgenes anteriores.

Estado final de v177:

- `index.html`: 7.715.257 bytes.
- Snapshot: `data/dashboard_kawaii_177_pobreza_espaciado_mobile.html`.
- SHA-256 de ambos: `39b38a6c9a6b720f9a60d31d2f07529f27b2bddce984cc32173ecb4513d6c9ff`.
- Trece bloques JavaScript internos presentes y compilables.
- Verificación a 390 y 320 px: ninguna anotación sale del gráfico; mandatos, llamadas de pobreza y leyenda permanecen separados.

## 40. EMAE · separación del resumen de cicatriz · v178

- Se agrega un margen superior de 14 px únicamente cuando una `.emae-grid-3` sigue directamente a `.emae-head`.
- El ajuste separa la descripción de “Cicatriz acumulada desde nov-2023” de la primera tarjeta sin alterar el espaciado de la grilla situada debajo del gráfico espejo.
- En móvil las tres tarjetas continúan apiladas y mantienen la separación uniforme existente entre sí.

Estado final de v178:

- `index.html`: 7.715.308 bytes.
- Snapshot: `data/dashboard_kawaii_178_emae_espaciado_cicatriz.html`.
- SHA-256 de ambos: `5d2001d90cb0980604d74122a28dc165d64ce745c44efb4d065cbbceb36bcd1c`.
- Verificación visual a 390 px: 14 px entre encabezado y primera tarjeta, sin desbordes ni cambios en el gráfico.

## 41. EMAE · fuentes y descargas normalizadas · v179

- El panel heredado de “Descargas, método y trazabilidad” adopta el componente transversal `.sources-box`.
- Las cinco descargas CSV usan el tratamiento rosado `.download-link` y conservan sus funciones embebidas.
- Las cinco fuentes temáticas y el manifiesto general se presentan como fichas `.source-link`, sin viñetas ni enlaces azules sueltos.
- Se agrega una nota de cobertura que distingue las publicaciones INDEC, el complemento histórico de población del Banco Mundial y los cálculos documentados por la auditoría EMAE.
- El registro automático informa seis referencias visibles y mantiene `data-source-coverage="ok"`.
- Los botones de navegación hacia Crecimiento, Trabajo y Consumo permanecen separados de las fuentes.

Estado final de v179:

- `index.html`: 7.715.822 bytes.
- Snapshot: `data/dashboard_kawaii_179_fuentes_emae_normalizadas.html`.
- SHA-256 de ambos: `2e41cfd72f560f3eda08ab8b0834a94e45fdaecfa0a493d1fc718eec9165662c`.
- Verificación a 390 y 1280 px: cero fichas fuera del panel; cinco descargas y seis fuentes visibles.

## 42. Péndulo principal · slider temporal móvil · v180

- El gráfico principal deja de depender del scrollbar horizontal nativo en pantallas de hasta 720 px.
- Se incorpora un slider visible que recorre ventanas de once años entre 1993 y 2026.
- La apertura móvil prioriza 2015–2026 para mostrar el tramo moderno; el extremo izquierdo permite leer 1993–2004 y las posiciones intermedias dejan visible el hueco metodológico 2008–2015.
- El slider controla `xaxis.range` de Plotly, no el desplazamiento del lienzo: el eje Y permanece siempre visible.
- La ventana elegida se conserva al alternar Índice del péndulo, Participación % y Cambio desde inicio del mandato, y también al cambiar el universo de la serie.
- En escritorio el slider se oculta y se restaura automáticamente la historia completa 1993–2026.

Estado final de v180:

- `index.html`: 7.717.345 bytes.
- Snapshot: `data/dashboard_kawaii_180_slider_pendulo_mobile.html`.
- SHA-256 de ambos: `bbedff64ecbf79d0480fa9797cc4e564a3bf1cfa12a6f2a899e05700c83a2014`.
- Verificación a 390 px: gráfico y contenedor miden 333 px, sin overflow horizontal; slider operativo en ambos extremos y tras rerender.
- Verificación a 1280 px: slider oculto, ocho marcas temporales desde 1996 hasta 2024 y serie completa visible.

## 43. Péndulo · margen exterior estable desde el reparto del ingreso · v181

- En móvil, las tarjetas secundarias de Producción —desde “¿Quién se queda con el ingreso generado?”— recuperan un retiro lateral propio de 4 px dentro de la columna.
- La regla se aplica a esa tarjeta y a todas las que siguen en el mismo panel, sin estrechar el encabezado ni el gráfico principal.
- El documento usa `overflow-x: clip` para impedir que un desplazamiento horizontal residual desplace toda la página y esconda el margen izquierdo.
- Los contenedores internos del Péndulo quedan limitados explícitamente al ancho disponible.
- Los gráficos anchos conservan su scroll horizontal interno y agregan contención de sobrepaso para que ese gesto no se propague al documento.

Estado final de v181:

- `index.html`: 7.718.021 bytes.
- Snapshot: `data/dashboard_kawaii_181_gutter_pendulo_mobile.html`.
- SHA-256 de ambos: `982c7ee8c816e3246e71789f9466f881e48ca02700318184e2387d8898bb2b0a`.
- Verificación a 480 px: tarjetas 1–2 mantienen 10 px de retiro exterior; tarjetas 3–8 quedan a 14 px por lado; ancho del documento = ancho útil y `scrollX = 0`.

## 44. Deuda pública · leyenda de acreedores separada del gráfico · v182

- La leyenda de “¿A quién le debemos?” deja de crecer hacia el área apilada del 100%.
- Se fija una disposición horizontal que puede ocupar dos filas en móvil.
- La leyenda queda anclada por su borde inferior, de modo que las filas adicionales se expanden hacia arriba.
- El margen superior reserva 122 px en móvil y 92 px en escritorio; el gráfico conserva su altura útil y el texto deja de cruzarse con la barra.

Estado final de v182:

- `index.html`: 7.718.029 bytes.
- Snapshot: `data/dashboard_kawaii_182_glosario_deuda_sin_superponer.html`.
- SHA-256 de ambos: `95830ef9e4fca8218105afad5cd3c8a5b2df360783f35a59374941211ab31e40`.
- Verificación geométrica: la leyenda termina 5,4 px antes del área de datos en la tarjeta comparativa; no existe intersección.

## 45. Cuenta madre · rueda convertida en scroll horizontal · v183

- La tabla “Cómo entra cada componente en la cuenta madre” se incorpora al manejador horizontal compartido por las botoneras.
- Con el cursor sobre la tabla, la rueda vertical desplaza las columnas lateralmente cuando existe overflow.
- Al alcanzar el inicio o el final, el evento deja de capturarse y la página vuelve a desplazarse normalmente.
- El scroll táctil y la barra horizontal continúan disponibles.
- Se agrega contención de sobrepaso y reserva estable para la barra, evitando que el gesto se propague accidentalmente al documento.

Estado final de v183:

- `index.html`: 7.718.109 bytes.
- Snapshot: `data/dashboard_kawaii_183_scroll_rueda_tabla_cuenta_madre.html`.
- SHA-256 de ambos: `3461d9dee53c3fe1e6e5b91d19d550c4c4795a5246f56c8786f594167c704c16`.
- Verificación de enlace: `.milei-cost-table-wrap` queda detectado y marcado por el manejador al cargar la página.

## 46. Cuenta madre · retiro lateral estable desde la tabla · v184

- La tarjeta “Cómo entra cada componente en la cuenta madre” se marca como inicio del tramo secundario final.
- En pantallas de hasta 720 px, esa tarjeta y todos sus hermanos posteriores reciben 4 px de retiro adicional por lado.
- El ajuste alcanza el cuadro de escalas, el mapa de fuentes y el pie editorial final.
- Las tarjetas anteriores conservan su ancho original.
- La regla limita explícitamente ancho y caja para impedir que tablas o enlaces vuelvan a empujar el borde fuera de la ventana.

Estado final de v184:

- `index.html`: 7.718.532 bytes.
- Snapshot: `data/dashboard_kawaii_184_gutter_cierre_cuenta_madre.html`.
- SHA-256 de ambos: `5fcd921ea5e55624d4a4389257da03362260bd63644a3e644b02434d02c5244c`.
- Verificación estructural: el corte selecciona exactamente la tabla, un cuadro de auditoría posterior, el panel de fuentes y el footer; el documento no presenta overflow horizontal.

## 47. Seguimiento social 2025–2026 · microajuste de leyenda · v185

- Se reduce sólo la separación entre la leyenda y el área de datos de “¿Qué pasó después de 2024?”.
- La posición relativa pasa de `1.12` a `1.09` en móvil y `1.10` en escritorio.
- El cambio también se replica en el relayout responsive para que un redimensionamiento no restaure el hueco anterior.
- La leyenda continúa anclada por abajo y no invade las barras.

Estado final de v185:

- `index.html`: 7.718.577 bytes.
- Snapshot: `data/dashboard_kawaii_185_social_reciente_gap_minimo.html`.
- SHA-256 de ambos: `a9bcaa1c8908f3790e359315a12ec52e1c3349cd9d7f14aff69698e67ce731cc`.
- Verificación geométrica: reducción aproximada de 7 px en escritorio y 10 px en móvil, sin superposición.

## 48. Gini histórico · etiquetas en carriles responsive · v186

- Se separan las seis etiquetas presidenciales en dos carriles alternados cuando el ancho es reducido.
- La advertencia `2007–2015 · con reservas` deja de competir con los nombres de los mandatos: queda en un carril propio, dentro del área del gráfico y con texto abreviado en móvil.
- El rótulo de pandemia se compacta y desciende dentro del gráfico para no cruzarse con las etiquetas presidenciales.
- Los tres cambios metodológicos de la base dejan de mostrarse como textos verticales sobre los años en móvil y tablet. Pasan a pequeñas etiquetas horizontales internas: `2003 · EPH continua`, `reinicio 2016` y `cobertura 2019`.
- Se incrementa de manera controlada el margen superior del gráfico móvil, se reduce el inferior y se reposiciona la leyenda para reservar espacio real a los dos carriles de mandatos.
- Las reglas verticales de cambio presidencial terminan antes del borde superior del área de datos; la regla de cobertura 2019 también evita los carriles metodológicos inferior y superior.
- El relayout responsive replica márgenes, posición de leyenda y anotaciones, evitando que el arreglo se pierda tras redimensionar.

Estado final de v186:

- `index.html`: 7.719.381 bytes.
- Snapshot: `data/dashboard_kawaii_186_gini_etiquetas_carriles_mobile.html`.
- SHA-256 de ambos: `28e40658f32f0e9aaeb8857582f73d05156faa94018c3ee12f36d8b37693ea4c`.
- Verificación funcional: Plotly carga el gráfico con 11 anotaciones; en escritorio no hay cruces geométricos entre las etiquetas presidenciales, la advertencia institucional y la pandemia. La lógica móvil usa carriles verticales y textos metodológicos horizontales compactos.

## 49. Cambio de Gini por mandato · valores sin invadir rótulos · v187

- En el gráfico horizontal “Cómo cambió el Gini dentro de cada mandato”, los valores negativos grandes ya no se dibujan por fuera del extremo izquierdo.
- Los dos resultados de `−0,040` se centran dentro de sus respectivas barras, con tipografía oscura legible tanto sobre relleno sólido como sobre el patrón rayado.
- Los cambios pequeños conservan la etiqueta exterior, donde cuentan con espacio y ayudan a leer la dirección respecto de cero.
- Se definen por separado tipografía interior y exterior para que el comportamiento se mantenga estable en móvil y escritorio.

Estado final de v187:

- `index.html`: 7.719.570 bytes.
- Snapshot: `data/dashboard_kawaii_187_gini_valores_dentro_barras.html`.
- SHA-256 de ambos: `18284243119239aa1fda44f107314d73741caf570568c33d6fa355438545ce40`.
- Verificación visual: ambos `−0,040` quedan dentro del área de sus barras y no intersectan los nombres ni los períodos de los mandatos.
