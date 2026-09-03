(() => {
  'use strict';

  if (document.getElementById('epica-stage2-v1')) return;

  const style = document.createElement('style');
  style.id = 'epica-stage2-v1';
  style.textContent = `
.epica-shell.incidence{--epica-accent:#a56531;--epica-accent-soft:#fff6e8;--epica-ink:#644727;--epica-muted:#806b50}
.epica-shell.development{--epica-accent:#386a8c;--epica-accent-soft:#edf7ff;--epica-ink:#35576d;--epica-muted:#647a88}
.epica-shell.narratives{--epica-accent:#7b5792;--epica-accent-soft:#f8f1fc;--epica-ink:#5e456b;--epica-muted:#796783}
.epica-actor-grid{display:grid;min-width:0;max-width:100%;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}
.epica-actor-card{min-width:0;padding:13px;border:1px solid #e5dde5;border-radius:16px;background:#fff}
.epica-actor-card small{display:block;color:var(--epica-muted);font-size:8px;font-weight:950;text-transform:uppercase;letter-spacing:.04em}
.epica-actor-card b{display:block;margin:5px 0;color:var(--epica-ink);font-size:20px;line-height:1.05}
.epica-actor-card p{margin:0;color:var(--epica-muted);font-size:9px;line-height:1.5}
.epica-stage-lane{display:grid;min-width:0;max-width:100%;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.epica-stage-card{position:relative;min-width:0;padding:12px;border:1px solid #dfe3e8;border-radius:15px;background:#fbfdff}
.epica-stage-card:not(:last-child):after{content:'→';position:absolute;right:-8px;top:50%;z-index:2;transform:translateY(-50%);color:#8ba0ae;font-weight:950}
.epica-stage-card small{display:block;color:#718592;font-size:8px;font-weight:950;text-transform:uppercase}.epica-stage-card b{display:block;margin:5px 0;color:#35576d;font-size:14px}.epica-stage-card p{margin:0;color:#6f818c;font-size:8px;line-height:1.45}
.epica-narrative-grid{display:grid;min-width:0;max-width:100%;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.epica-narrative-card{display:grid;min-width:0;gap:7px;padding:14px;border:1px solid #e4d9e9;border-radius:16px;background:#fff}
.epica-narrative-card[hidden]{display:none}.epica-narrative-card small{color:#8a7195;font-size:8px;font-weight:950;text-transform:uppercase;letter-spacing:.035em}.epica-narrative-card h3{margin:0;color:#5e456b;font-size:14px;line-height:1.3}.epica-narrative-card p{margin:0;color:#77657f;font-size:9px;line-height:1.5}.epica-narrative-origin{padding:8px 9px;border-radius:10px;background:#faf7fc}.epica-narrative-status{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:auto}.epica-narrative-status button{border:0;background:transparent;color:#7b5792;font:inherit;font-size:9px;font-weight:950;cursor:pointer}
@media(max-width:900px){.epica-actor-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.epica-stage-lane{grid-template-columns:repeat(2,minmax(0,1fr))}.epica-stage-card:nth-child(2):after{display:none}}
@media(max-width:720px){.epica-actor-grid,.epica-narrative-grid,.epica-stage-lane{grid-template-columns:1fr}.epica-stage-card:not(:last-child):after{content:'↓';right:50%;top:auto;bottom:-12px;transform:translateX(50%)}.epica-stage-card:nth-child(2):after{display:block}.epica-narrative-status{align-items:flex-start;flex-direction:column}.epica-narrative-status button{min-height:42px;padding:8px 0}}
`;
  document.head.appendChild(style);

  const tabs = document.getElementById('dash-main-tabs');
  const caputoButton = tabs?.querySelector('[data-tab="tab-epica-caputo-colchon"]');
  const caputoPanel = document.getElementById('tab-epica-caputo-colchon');
  if (!tabs || !caputoButton || !caputoPanel) return;

  caputoButton.insertAdjacentHTML('beforebegin', `
    <button class="tab-btn" type="button" data-tab="tab-epica-incidence">Quién paga · incidencia</button>
    <button class="tab-btn" type="button" data-tab="tab-epica-development">Desarrollo · inversión y trabajo</button>
    <button class="tab-btn" type="button" data-tab="tab-epica-narratives">Relatos · preguntas y alcance</button>
  `);

  caputoPanel.insertAdjacentHTML('beforebegin', `
  <section id="tab-epica-incidence" class="tab-panel">
    <div class="epica-shell incidence">
      <header class="epica-hero"><div><span class="epica-eyebrow">▦ Super-tab C · incidencia</span><h2>¿Qué cambió para cada actor?</h2><p>El equilibrio fiscal, los salarios, el ahorro de los hogares, la inversión pública y la situación bancaria no comparten unidad ni denominador. Este mapa los presenta juntos para comparar incidencias, sin sumarlos ni convertir coexistencias en causalidad.</p></div><aside class="epica-status-card"><div><strong>Matriz deliberadamente no aditiva</strong><small>Cada tarjeta conserva actor, período, medida y límite causal. No existe un total válido de “ganadores menos perdedores”.</small></div><div class="epica-status-row"><span class="epica-chip observed">cambios observados</span><span class="epica-chip proxy">universos distintos</span><span class="epica-chip open">cuenta sectorial incompleta</span></div></aside></header>
      <div class="epica-kpis"><article class="epica-kpi"><small>Salario real privado registrado</small><b>−3,55%</b><span>jun-26 vs nov-23</span></article><article class="epica-kpi"><small>Salario real público</small><b>−16,52%</b><span>jun-26 vs nov-23</span></article><article class="epica-kpi"><small>Empleo privado registrado</small><b>−251.500</b><span>nov-23 a abr-26</span></article><article class="epica-kpi"><small>Resultado financiero SPN</small><b>+4,70 pp</b><span>PIB · 2024 vs 2023</span></article><article class="epica-kpi"><small>Inversión pública real</small><b>18,18</b><span>índice 2023=100 · 2025</span></article></div>
      <section class="epica-panel"><div class="epica-panel-head"><div><h3>Mapa de incidencia observable</h3><p>No ordena actores moralmente: muestra qué indicador cambió y hasta dónde llega la evidencia.</p></div><span class="epica-chip observed">medidas con perímetro</span></div><div class="epica-actor-grid"><article class="epica-actor-card"><small>Trabajo privado registrado</small><b>96,45</b><p>Índice salarial real, base nov-2023=100. Promedio sectorial: no describe toda la distribución.</p></article><article class="epica-actor-card"><small>Trabajo público</small><b>83,48</b><p>Índice salarial real a junio de 2026. Agrega Nación y provincias con trayectorias heterogéneas.</p></article><article class="epica-actor-card"><small>Hogares</small><b>71,8%</b><p>Usó alguna estrategia V13–V17 en 2026-T1. No mide montos ni identifica una causa única.</p></article><article class="epica-actor-card"><small>Estado nacional</small><b>+4,70 pp PIB</b><p>Mejora del resultado financiero 2024 frente a 2023. Es flujo fiscal, no bienestar ni patrimonio.</p></article><article class="epica-actor-card"><small>Capital público</small><b>−81,82%</b><p>Cambio real del flujo de inversión 2025 frente a 2023. No equivale a deterioro físico medido.</p></article><article class="epica-actor-card"><small>Bancos y deudores</small><b>9,18%</b><p>Irregularidad de consumo a dic-2025, mientras el ROA agregado fue 1,02%. Costo, mora y utilidad no son transferencias peso por peso.</p></article></div></section>
      <div class="epica-grid equal"><section class="epica-panel"><div class="epica-panel-head"><div><h3>Qué puede leerse en conjunto</h3><p>Coexistencias documentadas que abren preguntas distributivas.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Consolidación fiscal y salarios</b><p>La mejora fiscal coexistió con pérdidas reales salariales desiguales. La matriz no asigna cuánto de una cosa causó la otra.</p></div><div class="epica-answer caution"><b>Flujo y patrimonio</b><p>Menor inversión pública afecta el flujo de reposición; el estado físico del capital requiere inventario y depreciación por activo.</p></div><div class="epica-answer open"><b>Sector privado sin desagregar</b><p>Las cuentas disponibles no separan hogares y sociedades no financieras, por lo que no cierran una cuenta distributiva completa.</p></div></div></section><section class="epica-panel"><div class="epica-panel-head"><div><h3>Seguir cada dimensión</h3><p>Los tabs originales conservan series y metodología.</p></div></div><div class="epica-bridge"><button type="button" onclick="activateTab('tab-work')">Salarios y trabajo →</button><button type="button" onclick="activateTab('tab-fiscal')">Resultado fiscal →</button><button type="button" onclick="activateTab('tab-morosidad')">Mora →</button><button type="button" onclick="activateTab('tab-social')">Transferencias →</button><button type="button" onclick="activateTab('tab-investment')">Inversión →</button><button type="button" onclick="activateTab('tab-power')">Distribución →</button></div><div class="epica-formula" style="margin-top:10px"><b>Regla de lectura:</b> actor + variable + unidad + período + perímetro. Si alguno cambia, las cifras se muestran lado a lado pero no se suman.</div></section></div>
      <section class="sources-box"><h3>Datos y respaldo</h3><div class="source-links"><a class="download-link" download href="research/epica_dashito_2026/fiscal_desarrollo/matriz_incidencia.csv">⬇ CSV · matriz de incidencia</a><a class="download-link" download href="research/epica_dashito_2026/fiscal_desarrollo/hallazgos_cuantitativos.csv">⬇ CSV · métricas y fórmulas</a><a class="download-link" download href="research/epica_dashito_2026/hogares_credito/matriz_evidencia.csv">⬇ CSV · hogares y crédito</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61">📊 INDEC · salarios</a><a class="source-link" target="_blank" rel="noopener" href="https://opc.gob.ar/ejecucion-presupuestaria/">🏛️ OPC · ejecución</a></div><div class="sources-note"><b>Corte:</b> 31/08/2026. La confianza causal permanece baja cuando sólo hay coexistencia temporal. Las fuentes locales y sus límites figuran en cada fila descargable.</div></section>
    </div>
  </section>

  <section id="tab-epica-development" class="tab-panel">
    <div class="epica-shell development">
      <header class="epica-hero"><div><span class="epica-eyebrow">⌁ Super-tab D · desarrollo</span><h2>¿Cuándo la inversión se convierte en trabajo y capacidad?</h2><p>Una aprobación, un compromiso y un cronograma son etapas relevantes, pero no equivalen a desembolso, obra terminada, empleo permanente ni productividad. El tab hace visible esa cadena.</p></div><aside class="epica-status-card"><div><strong>Inputs, ejecución y resultados separados</strong><small>RIGI al 31/08/2026 · empleo privado a abril · EMAE a abril · inversión pública hasta 2025.</small></div><div class="epica-status-row"><span class="epica-chip observed">actividad y empleo</span><span class="epica-chip proxy">proyectos y cronogramas</span><span class="epica-chip open">empleo ejecutado N/D</span></div></aside></header>
      <div class="epica-kpis"><article class="epica-kpi"><small>EMAE desestacionalizado</small><b>+5,15%</b><span>abr-26 vs nov-23</span></article><article class="epica-kpi"><small>Empleo privado registrado</small><b>−3,94%</b><span>−251.500 personas</span></article><article class="epica-kpi"><small>Proyectos RIGI aprobados</small><b>22</b><span>portal deduplicado</span></article><article class="epica-kpi"><small>Inversión comprometida</small><b>USD 47.073 M</b><span>no ejecución observada</span></article><article class="epica-kpi"><small>Empleos proyectados</small><b>95.950</b><span>0 con desglose completo</span></article></div>
      <div class="epica-toolbar" role="group" aria-label="Dimensión de desarrollo"><span>Explorar la cadena</span><button class="epica-toggle active" type="button" data-epica-development-view="activity" aria-pressed="true">Actividad y empleo</button><button class="epica-toggle" type="button" data-epica-development-view="rigi" aria-pressed="false">Cronograma RIGI</button><button class="epica-toggle" type="button" data-epica-development-view="capital" aria-pressed="false">Capital público</button></div>
      <div class="epica-grid"><section class="epica-panel"><div class="epica-panel-head"><div><h3 id="epicaDevelopmentTitle">Actividad y empleo registrado desde noviembre de 2023</h3><p id="epicaDevelopmentSubtitle">Índices comparables con base 100 en noviembre de 2023.</p></div><span id="epicaDevelopmentBadge" class="epica-chip observed">coexistencia observada</span></div><div id="epicaDevelopmentChart" class="epica-chart tall" role="img" aria-label="Actividad, empleo, cronograma RIGI y capital público"></div></section><aside class="epica-panel"><div class="epica-panel-head"><div><h3>Cómo leer la divergencia</h3><p>Las etapas y los universos importan.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Actividad y trabajo</b><p>EMAE y empleo privado registrado evolucionaron en sentidos distintos. Es compatible con rezagos o recuperación capital-intensiva, no una elasticidad causal estimada.</p></div><div class="epica-answer caution"><b>RIGI</b><p>USD 47.073 M y 95.950 empleos son compromisos y proyecciones. El portal no publica una serie homogénea de ejecución o permanencia.</p></div><div class="epica-answer open"><b>Capital público</b><p>El flujo real cayó fuertemente. El inventario contable parcial no informa condición física de rutas, escuelas u hospitales.</p></div></div></aside></div>
      <section class="epica-panel"><div class="epica-panel-head"><div><h3>La cadena que debe completarse</h3><p>Cada etapa necesita un indicador y una fecha propios.</p></div><span class="epica-chip proxy">mapa de seguimiento</span></div><div class="epica-stage-lane"><article class="epica-stage-card"><small>1 · input</small><b>Aprobación</b><p>Norma, resolución, proyecto y monto anunciado.</p></article><article class="epica-stage-card"><small>2 · ejecución</small><b>Desembolso y obra</b><p>Flujo financiero, avance físico y proveedores.</p></article><article class="epica-stage-card"><small>3 · output</small><b>Capacidad instalada</b><p>Producción, infraestructura o servicio operativo.</p></article><article class="epica-stage-card"><small>4 · outcome</small><b>Empleo y productividad</b><p>Puestos permanentes, salarios, exportaciones y encadenamientos.</p></article></div><div class="epica-bridge" style="margin-top:11px"><button type="button" onclick="activateTab('tab-investment')">Inversión existente →</button><button type="button" onclick="activateTab('tab-emae')">Actividad →</button><button type="button" onclick="activateTab('tab-work')">Trabajo →</button><button type="button" onclick="activateTab('tab-trade')">Exportaciones →</button><button type="button" onclick="activateTab('tab-roads')">Infraestructura →</button></div></section>
      <section class="sources-box"><h3>Datos y respaldo</h3><div class="source-links"><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_summary.csv">⬇ CSV · resumen RIGI</a><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_investment_schedule.csv">⬇ CSV · cronograma anual</a><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/public_capital_accounting_inventory.csv">⬇ CSV · capital público</a><a class="source-link" target="_blank" rel="noopener" href="https://www.argentina.gob.ar/economia/rigi">🏗️ Portal RIGI</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-9-48">📈 INDEC · EMAE</a></div><div class="sources-note"><b>Corte:</b> 31/08/2026. El cronograma está expresado en USD millones de inversión y no se interpreta como empleo. Los originales y resoluciones están respaldados en el manifiesto SHA-256.</div></section>
    </div>
  </section>

  <section id="tab-epica-narratives" class="tab-panel">
    <div class="epica-shell narratives">
      <header class="epica-hero"><div><span class="epica-eyebrow">◇ Super-tab E · relatos</span><h2>¿Qué pregunta abre cada frase?</h2><p>Las afirmaciones públicas no se convierten en un examen binario. Cada una se traduce a una pregunta medible, una lectura lógica, evidencia disponible y límites que siguen abiertos.</p></div><aside class="epica-status-card"><div><strong>Observatorio conectado con la evidencia</strong><small>27 frases de origen enlazadas a las 40 preguntas de la épica.</small></div><div class="epica-status-row"><span class="epica-chip observed">7 con evidencia lista</span><span class="epica-chip proxy">1 escenario</span><span class="epica-chip open">18 en exploración</span></div></aside></header>
      <div class="epica-kpis"><article class="epica-kpi"><small>Preguntas de la épica</small><b>40</b><span>matriz de ejecución</span></article><article class="epica-kpi"><small>Frases registradas</small><b>27</b><span>puntos de partida</span></article><article class="epica-kpi"><small>Evidencia lista</small><b>7</b><span>perímetro definido</span></article><article class="epica-kpi"><small>En exploración</small><b>18</b><span>faltan piezas</span></article><article class="epica-kpi"><small>Regla editorial</small><b>4 capas</b><span>pregunta · dato · lectura · límite</span></article></div>
      <div class="epica-toolbar" role="group" aria-label="Familia de preguntas"><span>Filtrar preguntas</span><button class="epica-toggle active" type="button" data-epica-narrative-category="all" aria-pressed="true">Todas</button><button class="epica-toggle" type="button" data-epica-narrative-category="macro" aria-pressed="false">Macro y dólares</button><button class="epica-toggle" type="button" data-epica-narrative-category="households" aria-pressed="false">Hogares y crédito</button><button class="epica-toggle" type="button" data-epica-narrative-category="development" aria-pressed="false">Estado y desarrollo</button></div>
      <section class="epica-narrative-grid" id="epicaNarrativeGrid" aria-live="polite"></section>
      <div class="epica-grid equal"><section class="epica-panel"><div class="epica-panel-head"><div><h3>Cómo se lee una tarjeta</h3><p>La frase se conserva como contexto, no como conclusión.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Pregunta abierta</b><p>Define qué relación o magnitud se quiere observar.</p></div><div class="epica-answer good"><b>Lectura actual</b><p>Resume lo compatible con los datos dentro de un perímetro explícito.</p></div><div class="epica-answer open"><b>Límite</b><p>Expone qué dato o definición falta para distinguir interpretaciones.</p></div></div></section><section class="epica-panel"><div class="epica-panel-head"><div><h3>Volver al recorrido</h3><p>Las hipótesis personales permanecen en Storytelling.</p></div></div><div class="epica-bridge"><button type="button" onclick="activateTab('tab-story')">Hipótesis de partida →</button><button type="button" onclick="activateTab('tab-epica-households')">Hogares →</button><button type="button" onclick="activateTab('tab-epica-dollars')">Dólares →</button><button type="button" onclick="activateTab('tab-epica-incidence')">Quién paga →</button><button type="button" onclick="activateTab('tab-epica-development')">Desarrollo →</button></div></section></div>
      <section class="sources-box"><h3>Matrices y trazabilidad</h3><div class="source-links"><a class="download-link" download href="research/epica_dashito_2026/claims_registry.csv">⬇ CSV · frases y preguntas</a><a class="download-link" download href="research/epica_dashito_2026/execution_matrix.csv">⬇ CSV · 40 análisis</a><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/gap_resolution_matrix.csv">⬇ CSV · brechas y estado</a></div><div class="sources-note"><b>Regla:</b> una lectura lógica no reemplaza la evidencia empírica. <code>ready</code>, <code>under_review</code> y <code>scenario_ready</code> describen la madurez del dato, no una evaluación de la persona que formuló la frase.</div></section>
    </div>
  </section>
  `);

  let developmentView = 'activity';
  let narrativeCategory = 'all';
  const plotConfig = {responsive:true,displaylogo:false,displayModeBar:false};
  const narrativeRows = [
    {category:'macro',origin:'“Superávit comercial = superávit de cuenta corriente”',question:'¿Qué componentes conectan el saldo de bienes con la cuenta corriente?',status:'evidencia lista',kind:'observed',reading:'Bienes aportó USD 6.339 M en 2026-Q1, pero servicios e ingreso primario llevaron la cuenta corriente a −USD 1.651 M.',limit:'El dato posterior a 2026-Q1 aún no estaba publicado al corte.',tab:'tab-epica-dollars'},
    {category:'macro',origin:'“Reservas brutas = dólares libres”',question:'¿Qué parte del stock tiene disponibilidad observable y bajo qué condiciones?',status:'en exploración',kind:'open',reading:'La planilla SDDS permite separar composición y flujos predeterminados; el residual de estrés no es una cifra oficial de reservas netas.',limit:'Falta una plantilla sincronizada para netas, líquidas y propias.',tab:'tab-epica-dollars'},
    {category:'households',origin:'“Bajar pobreza = recuperación completa del bienestar”',question:'¿Qué dimensiones faltan para describir la recuperación de los hogares?',status:'en exploración',kind:'open',reading:'Pobreza, uso de ahorro, deuda y mora pueden moverse de forma diferente porque miden personas, hogares y saldos distintos.',limit:'No existe un panel público que siga al mismo hogar.',tab:'tab-epica-households'},
    {category:'households',origin:'“Acceso al crédito = inclusión financiera”',question:'¿Cuándo el crédito amplía oportunidades y cuándo agrega fragilidad?',status:'en exploración',kind:'open',reading:'La cobertura de préstamos personales aumentó y luego creció la irregularidad; la secuencia no identifica causalidad individual.',limit:'Faltan cohortes con tasa, ingreso, destino y resultado.',tab:'tab-morosidad'},
    {category:'development',origin:'“Más inversión = más empleo”',question:'¿Cómo se pasa de una inversión aprobada a empleo ejecutado y permanente?',status:'en exploración',kind:'open',reading:'El portal RIGI informa compromisos y empleos proyectados, pero no una serie homogénea de ejecución ni permanencia.',limit:'Se necesitan avances por proyecto, proveedores y puestos observados.',tab:'tab-epica-development'},
    {category:'development',origin:'“Bajar impuestos siempre aumenta la recaudación”',question:'¿Qué expansión de base compensa cada reducción de alícuota?',status:'escenario',kind:'proxy',reading:'Con recaudación R=t·B, una baja de 10%, 25% o 50% requiere una base 11,11%, 33,33% o 100% mayor para neutralidad.',limit:'La identidad no pronostica formalización ni actividad.',tab:'tab-fiscal'},
    {category:'development',origin:'“Cerrar, desregular o privatizar es un logro por definición”',question:'¿Qué output y qué resultado aparecen después de cada medida?',status:'evidencia lista',kind:'observed',reading:'La acción administrativa es un input. Capacidad, cobertura, precio, calidad y distribución requieren indicadores posteriores.',limit:'Cada política necesita objetivo, línea de base y ventana propios.',tab:'tab-program'}
  ];

  function plotBase(mobile) {
    return {paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'#fff',font:{family:'Inter,system-ui,sans-serif',size:mobile?9:10,color:'#506b7c'},margin:{l:mobile?52:64,r:18,t:28,b:mobile?92:68},hoverlabel:{bgcolor:'#fff',bordercolor:'#cbd9e2',font:{color:'#35576d'}}};
  }

  function setDevelopmentMeta(title,subtitle,badge,kind) {
    document.getElementById('epicaDevelopmentTitle').textContent=title;
    document.getElementById('epicaDevelopmentSubtitle').textContent=subtitle;
    const badgeEl=document.getElementById('epicaDevelopmentBadge');
    badgeEl.textContent=badge; badgeEl.className=`epica-chip ${kind}`;
  }

  function renderDevelopment() {
    const target=document.getElementById('epicaDevelopmentChart');
    if (!target || !window.Plotly) return;
    const mobile=window.innerWidth<=720;
    let traces,layout;
    if (developmentView==='rigi') {
      setDevelopmentMeta('Cronograma de inversión declarado por sector','Portal RIGI · USD millones · no es ejecución ni empleo.','plan de inversión','proxy');
      const years=[2024,2025,2026,2027,2028,2029,2030,2031];
      traces=[
        {type:'bar',name:'Energía',x:years,y:[37,252,162,36,0,0,0,0],marker:{color:'#e7b65e'}},
        {type:'bar',name:'Petróleo y gas',x:years,y:[48,1802,2724,1632,1309,953,1033,915],marker:{color:'#477b9c'}},
        {type:'bar',name:'Minería',x:years,y:[527,1473,2579,3875,4128,3278,2450,1503],marker:{color:'#7c6aa6'}},
        {type:'bar',name:'Otros',x:years,y:[0,174,204,130,40,21,2,0],marker:{color:'#a9bbc7'}}
      ];
      layout={...plotBase(mobile),barmode:'stack',legend:{orientation:'h',y:1.14},yaxis:{title:'USD millones programados',gridcolor:'#e5eef4',fixedrange:true},xaxis:{dtick:1,fixedrange:true},hovermode:'x unified'};
    } else if (developmentView==='capital') {
      setDevelopmentMeta('Flujo real de inversión pública','Índice 2023=100 · ejecución presupuestaria, no condición física.','flujo observado','observed');
      traces=[{type:'bar',x:['2023','2024','2025'],y:[100,24.90,18.18],text:['100','24,90','18,18'],textposition:'outside',cliponaxis:false,marker:{color:['#7ca6bf','#d2a95f','#bd765f']},hovertemplate:'<b>%{x}</b><br>Índice real %{y:.2f}<extra></extra>'}];
      layout={...plotBase(mobile),showlegend:false,yaxis:{title:'Índice real 2023=100',range:[0,112],gridcolor:'#e5eef4',fixedrange:true},xaxis:{fixedrange:true}};
    } else {
      setDevelopmentMeta('Actividad y empleo registrado desde noviembre de 2023','Índices comparables con base 100 en noviembre de 2023.','coexistencia observada','observed');
      traces=[{type:'bar',x:['EMAE desestacionalizado','Empleo privado registrado'],y:[105.154,96.06],text:['105,15','96,06'],textposition:'outside',cliponaxis:false,marker:{color:['#4d8aaa','#c47768']},hovertemplate:'<b>%{x}</b><br>Índice %{y:.2f}<extra></extra>'}];
      layout={...plotBase(mobile),showlegend:false,yaxis:{title:'Índice nov-2023=100',range:[90,108],gridcolor:'#e5eef4',fixedrange:true},xaxis:{tickangle:mobile?-22:0,fixedrange:true},shapes:[{type:'line',x0:-.5,x1:1.5,y0:100,y1:100,line:{color:'#8ba1af',dash:'dot'}}]};
    }
    Plotly.react(target,traces,layout,plotConfig);
  }

  function renderNarratives() {
    const target=document.getElementById('epicaNarrativeGrid');
    if (!target) return;
    target.innerHTML=narrativeRows.filter(row=>narrativeCategory==='all'||row.category===narrativeCategory).map(row=>`<article class="epica-narrative-card"><small>Frase de origen · ${row.category==='macro'?'macro y dólares':row.category==='households'?'hogares y crédito':'Estado y desarrollo'}</small><p class="epica-narrative-origin">${row.origin}</p><h3>${row.question}</h3><p><b>Lectura actual:</b> ${row.reading}</p><p><b>Límite:</b> ${row.limit}</p><div class="epica-narrative-status"><span class="epica-chip ${row.kind}">${row.status}</span><button type="button" onclick="activateTab('${row.tab}')">Abrir evidencia →</button></div></article>`).join('');
  }

  window.renderEpicaDevelopment=renderDevelopment;
  window.renderEpicaNarratives=renderNarratives;

  document.querySelectorAll('[data-epica-development-view]').forEach(button=>button.addEventListener('click',()=>{
    developmentView=button.dataset.epicaDevelopmentView;
    document.querySelectorAll('[data-epica-development-view]').forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});
    renderDevelopment();
  }));
  document.querySelectorAll('[data-epica-narrative-category]').forEach(button=>button.addEventListener('click',()=>{
    narrativeCategory=button.dataset.epicaNarrativeCategory;
    document.querySelectorAll('[data-epica-narrative-category]').forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});
    renderNarratives();
  }));

  tabs.querySelector('[data-tab="tab-epica-development"]')?.addEventListener('click',()=>window.setTimeout(renderDevelopment,190));
  tabs.querySelector('[data-tab="tab-epica-narratives"]')?.addEventListener('click',()=>window.setTimeout(renderNarratives,190));
  renderNarratives();
})();
