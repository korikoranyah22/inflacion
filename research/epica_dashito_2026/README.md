# Ejecución paralela · épica “De la estabilización al bienestar”

Fecha de corte de la corrida: **2026-08-31**.

## Alcance interpretado

El pedido del usuario fue **ejecutar el análisis en paralelo**. El documento adjunto se trató como especificación temática y criterio de calidad, no como una instrucción autónoma para modificar indiscriminadamente el dashboard.

Especificación recibida:

- archivo: `EPICA_DASHITO_ANALISIS_X_2026-08-31.md`;
- SHA-256: `9C1187A99B9EE226373B5A6C308E3A0CC88AC524000FB1E45E8E44C5263608F0`.

La primera corrida se organizó en tres frentes independientes:

1. `hogares_credito`: fragilidad, estrategias de manutención, deuda, mora, inclusión y costo de vida;
2. `dolares_externo`: reservas, flujos, sector externo, tipo de cambio, deuda y comparadores;
3. `fiscal_desarrollo`: balances, incidencia, inversión, empleo, infraestructura, impuestos e inputs/outcomes.

## Punto de partida auditado

El dashboard no parte de cero:

- `index.html` contiene **37 pestañas**;
- el catálogo vivo `data/fuentes/FUENTES.csv` contiene **527 registros**, 494 con URL y 522 con archivo local;
- hay **30 temas** y **104 denominaciones institucionales** en el catálogo;
- el snapshot de `index.html` usado para esta corrida tiene SHA-256 `C4B44AB1C0BCFB6BB617C85765BA020D6C0419D12FB097ADA9997C82CAD098DC`.

La matriz inicial cruza las 40 preguntas de la épica contra el tablero existente. Su diagnóstico de arranque es:

| Estado inicial | Preguntas | Lectura |
|---|---:|---|
| `strong_partial` | 4 | Hay evidencia sustantiva, pero falta algún corte o cierre metodológico. |
| `partial` | 26 | Hay piezas relevantes; todavía no identifican por completo la pregunta. |
| `scenario_ready` | 4 | Se puede simular, siempre que los supuestos queden visibles. |
| `gap` | 5 | Falta una fuente o desagregación decisiva. |
| `out_of_core` | 1 | Conviene mantenerlo como módulo institucional separado. |

Esto evita convertir la épica en 40 pestañas redundantes: primero se reutiliza evidencia y sólo se abre un módulo nuevo cuando la pregunta no puede resolverse conectando lo que ya existe.

## Entregables

- `MASTER_RESULTS.md`: síntesis consolidada de hallazgos y brechas.
- `execution_matrix.csv`: mapa completo de las 40 preguntas, pestañas existentes y gate de decisión.
- `claims_registry.csv`: 27 afirmaciones de X separadas en validez lógica y verificación empírica.
- `hogares_credito/`: informe, evidencia y cálculos del frente de hogares.
- `dolares_externo/`: informe, evidencia y cálculos del frente externo.
- `fiscal_desarrollo/`: informe, evidencia y cálculos de incidencia y desarrollo.
- `deep_dive_2026-08-31/`: profundización de brechas, microdatos EPH, planilla SDDS, vencimientos, RIGI, capital público y respaldo íntegro de fuentes.
- `validate_outputs.py`: control estructural de los 40 análisis, 27 claims y tres paquetes.

## Regla de lectura

Cada resultado debe rotularse como una de estas categorías:

- **observado**: proviene directamente de una fuente o de una transformación reproducible;
- **proxy**: aproxima la pregunta, pero no mide exactamente el concepto;
- **escenario**: depende de supuestos que el usuario puede cambiar;
- **no identificado**: los datos disponibles no permiten sostener la afirmación;
- **no comparable**: difieren unidad, universo, período o definición.

`No identificado` no equivale a cero ni a ausencia del fenómeno. `Correlacionado` tampoco equivale a causado.

## Validación

Desde la raíz del repositorio:

```powershell
python research/epica_dashito_2026/validate_outputs.py
```

La validación final exige:

- ids 1–40 exactamente una vez;
- claims 1–27 exactamente una vez;
- un informe Markdown y al menos un CSV por frente.

## Decisión de integración

Esta corrida no modifica `index.html`. El repositorio tiene trabajo previo y cambios activos; integrar visualizaciones antes de cerrar universos y fórmulas aumentaría el riesgo de publicar dobles conteos o falsas identidades. Los paquetes de evidencia quedan listos para una segunda etapa de integración por super-tabs.
