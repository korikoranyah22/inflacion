# Auditoría de escalas y jerarquía visual · v148

Fecha de implementación: 22 de agosto de 2026.

## Alcance

Esta revisión aplica las ideas de los prompts sobre escala semilogarítmica y legibilidad general sin modificar ningún dato, fórmula ni serie. El tiempo continúa en escala lineal y sólo puede cambiar la escala vertical de los gráficos expresamente auditados.

## Gráficos con selector Lineal / Log

El valor inicial es siempre **Lineal**. El tooltip conserva los valores reales en ambas vistas.

| Gráfico | Criterio | Disponibilidad de Log |
|---|---|---|
| Riesgo país | Los picos comprimen los períodos de menor riesgo y dificultan comparar cambios proporcionales. | Recomendada |
| Big Mac · dólar observado vs paridad implícita | La serie pasa por varios órdenes de magnitud entre 2002 y 2026. | Recomendada |
| Reservas brutas BCRA | La escala proporcional puede servir como lectura alternativa del stock. | Opcional, sólo en modo **Stock** |
| A3500 BCRA | El nivel nominal pasa por varios órdenes de magnitud. | Recomendada, sólo en modo **Nivel** |

Cada control explica en lenguaje simple:

- Lineal: la misma distancia vertical representa la misma cantidad absoluta.
- Log: la misma distancia vertical representa un cambio proporcional parecido.

Las marcas del eje logarítmico se escriben como números comunes (`100`, `1.000`, `10.000`) y no como potencias del tipo `10^x`.

## Protecciones metodológicas

- No se transforman los datos con logaritmos: sólo se cambia la proyección del eje Y de Plotly.
- Si la vista activa contiene cero o valores negativos, el botón Log se deshabilita.
- Al pasar de Stock a Variación mensual en reservas, la vista vuelve a Lineal y explica el motivo.
- Al pasar de Nivel a Variación mensual en A3500, ocurre lo mismo.
- No se ocultan observaciones, no se suman constantes y no se reemplazan ceros.
- Las anotaciones, líneas presidenciales y tooltips siguen vinculados a los valores originales.

## Familias que permanecen lineales

Se mantuvieron en escala lineal por razones semánticas o matemáticas:

- inflación, salarios, pobreza, Gini, EMAE, poder adquisitivo y tasas en rangos acotados;
- variaciones mensuales, tasas reales, balances, brechas y saldos que pueden cruzar cero;
- intervención cambiaria, factores monetarios, resultado fiscal, comercio y simulaciones con valores positivos y negativos;
- Big Mac de sobre/subvaluación, porque la distancia respecto de 0% es parte de la lectura;
- barras apiladas o comparaciones con base cero, donde Log distorsionaría la magnitud visual;
- gráficos de doble eje con unidades diferentes, para no sumar otra capa de ambigüedad.

## Jerarquía y navegación

La navegación superior ahora ofrece grupos temáticos:

- Destacados
- Hogares
- Precios y dólar
- Actividad
- Estado y deuda
- Poder económico
- Ver todo

El filtro no cambia ni elimina pestañas. La pestaña activa siempre permanece visible aunque se cambie de grupo. En mobile, tanto los grupos como las pestañas se recorren horizontalmente para evitar una pared vertical de botones.

También se hicieron estos ajustes:

- menor sombra general y superficies más nítidas;
- contraste reforzado en textos secundarios;
- patrón de fondo suavizado mediante una capa clara, sin reemplazar el SVG original;
- controles de escala compactos, próximos al gráfico y con objetivos táctiles adecuados;
- estados `aria-pressed`, ayuda accesible y botón Log deshabilitado cuando corresponde.

## Verificación

- Sintaxis: 12 bloques JavaScript analizados, 0 errores.
- Escritorio: 1440 px, sin overflow global.
- Mobile: 390 px, sin overflow global.
- BCRA Stock + Log: ticks verificados como `10.000`, `20.000`, `40.000`, `80.000`.
- BCRA Variación mensual: Log deshabilitada y retorno automático a Lineal verificados.

## Archivos

- Dashboard publicado/local: `index.html`
- Snapshot: `data/dashboard_kawaii_148_escalas_log_y_jerarquia_visual.html`

## Adenda v175 · etiquetas de Tasas e inflación en ancho reducido

- La vista Log conserva las ocho series, pero las llamadas de noviembre/diciembre de 2023 y el corte del 10/12 se redistribuyen en móvil.
- El rótulo del corte se abrevia a `10/12` porque la franja superior ya identifica a Milei.
- `ene–nov 148,1%` se desplaza hacia la izquierda y abajo; `dic-23 +25,5%`, hacia la derecha y arriba.
- Se conserva la posición correcta de los valores sobre el eje Log y no se altera la versión de escritorio.
- Verificación geométrica a 390 y 320 px: cero intersecciones entre anotaciones y cero textos fuera del lienzo, tanto en Log como en Lineal.

## Adenda v176 · referencia de tasa real cero

- El rótulo `0 = iguala la inflación` del gráfico real mensual se eleva respecto de la línea de cero.
- Usa texto marrón oscuro sobre fondo crema semitransparente y borde ámbar, en lugar del naranja de bajo contraste.
- Conserva 28 px de separación visual respecto de la línea y permanece contenido tanto a 390 px como en escritorio.
