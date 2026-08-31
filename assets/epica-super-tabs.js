(() => {
  'use strict';

  if (document.getElementById('epica-super-tabs-v1')) return;

  const style = document.createElement('style');
  style.id = 'epica-super-tabs-v1';
  style.textContent = `
.epica-shell{--epica-accent:#a0527b;--epica-accent-soft:#fff0f6;--epica-ink:#573f63;--epica-muted:#78687d;display:grid;gap:14px}
.epica-shell.dollars{--epica-accent:#26766f;--epica-accent-soft:#ecfbf7;--epica-ink:#315d5b;--epica-muted:#617a79}
.epica-shell.caputo{--epica-accent:#67559a;--epica-accent-soft:#f3f0ff;--epica-ink:#4f426f;--epica-muted:#706887}
.epica-hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.65fr);gap:16px;align-items:stretch;padding:18px 20px;border:1px solid color-mix(in srgb,var(--epica-accent) 28%,#e7dce9);border-radius:22px;background:linear-gradient(135deg,#fff 0%,var(--epica-accent-soft) 100%);box-shadow:0 12px 32px rgba(81,53,91,.07)}
.epica-eyebrow{display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border:1px solid color-mix(in srgb,var(--epica-accent) 30%,#fff);border-radius:999px;background:#fff;color:var(--epica-accent);font-size:10px;font-weight:950;letter-spacing:.05em;text-transform:uppercase}
.epica-hero h2{margin:9px 0 6px;color:var(--epica-ink);font-size:clamp(24px,3.6vw,40px);line-height:1.04;letter-spacing:-.025em}
.epica-hero p{max-width:800px;margin:0;color:var(--epica-muted);font-size:12px;line-height:1.55}
.epica-status-card{display:grid;align-content:center;gap:9px;padding:14px;border:1px solid rgba(255,255,255,.9);border-radius:17px;background:rgba(255,255,255,.78)}
.epica-status-card strong{color:var(--epica-ink);font-size:16px;line-height:1.25}.epica-status-card small{color:var(--epica-muted);font-size:10px;line-height:1.45}
.epica-status-row{display:flex;flex-wrap:wrap;gap:6px}.epica-chip{display:inline-flex;align-items:center;min-height:25px;padding:5px 8px;border:1px solid #dfd3e3;border-radius:999px;background:#fff;color:#755f7a;font-size:9px;font-weight:900}.epica-chip.observed{border-color:#b8ddcd;color:#28735a;background:#f4fff9}.epica-chip.proxy{border-color:#e6c985;color:#88631d;background:#fff9e8}.epica-chip.open{border-color:#e3b8c9;color:#9c4666;background:#fff5f8}
.epica-toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:7px;padding:10px 12px;border:1px solid #e4d9e7;border-radius:16px;background:#fff}.epica-toolbar>span{margin-right:auto;color:var(--epica-muted);font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:.04em}
.epica-toggle{min-height:34px;padding:7px 11px;border:1px solid #ddd0e2;border-radius:999px;background:#fff;color:#735e78;font:inherit;font-size:10px;font-weight:900;cursor:pointer}.epica-toggle.active{border-color:var(--epica-accent);background:var(--epica-accent-soft);color:var(--epica-accent);box-shadow:inset 0 0 0 1px var(--epica-accent)}
.epica-kpis{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px}.epica-kpi{position:relative;min-height:112px;padding:13px;border:1px solid #e4d9e7;border-radius:17px;background:#fff;overflow:hidden}.epica-kpi:after{content:"";position:absolute;inset:auto -28px -34px auto;width:90px;height:90px;border-radius:50%;background:var(--epica-accent-soft)}.epica-kpi small{position:relative;z-index:1;display:block;min-height:26px;color:var(--epica-muted);font-size:9px;font-weight:900;line-height:1.35;text-transform:uppercase}.epica-kpi b{position:relative;z-index:1;display:block;margin:6px 0 3px;color:var(--epica-ink);font-size:clamp(23px,3vw,34px);line-height:1}.epica-kpi span{position:relative;z-index:1;color:#8b7b8f;font-size:8px;font-weight:800}
.epica-grid{display:grid;grid-template-columns:minmax(0,1.28fr) minmax(290px,.72fr);gap:12px}.epica-grid.equal{grid-template-columns:repeat(2,minmax(0,1fr))}.epica-panel{min-width:0;padding:15px;border:1px solid #e4d9e7;border-radius:19px;background:#fff;box-shadow:0 8px 22px rgba(80,54,92,.045)}.epica-panel-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:8px}.epica-panel-head h3{margin:0;color:var(--epica-ink);font-size:15px}.epica-panel-head p{max-width:560px;margin:4px 0 0;color:var(--epica-muted);font-size:9px;line-height:1.45}.epica-panel-head .epica-chip{flex:0 0 auto}
.epica-chart{width:100%;height:360px}.epica-chart.tall{height:390px}
.epica-answer-grid{display:grid;gap:8px}.epica-answer{padding:11px 12px;border:1px solid #e8e0ea;border-radius:14px;background:#fcfafc}.epica-answer b{display:block;margin-bottom:4px;color:var(--epica-ink);font-size:10px}.epica-answer p{margin:0;color:var(--epica-muted);font-size:9px;line-height:1.5}.epica-answer.good{border-left:4px solid #70b999}.epica-answer.caution{border-left:4px solid #ddb967}.epica-answer.open{border-left:4px solid #d889a7}
.epica-strata-read{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:7px}.epica-strata-read div{padding:9px;border-radius:12px;background:#faf7fb;color:#77637b;font-size:8px;line-height:1.4}.epica-strata-read b{display:block;color:var(--epica-ink);font-size:10px}
.epica-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:7px}.epica-flow div{position:relative;padding:11px;border:1px solid #e2dfe4;border-radius:14px;background:#fbfcfc}.epica-flow div:not(:last-child):after{content:"→";position:absolute;right:-8px;top:50%;z-index:2;transform:translateY(-50%);color:#9a8c9e;font-weight:950}.epica-flow small{display:block;color:#7a707e;font-size:8px;font-weight:900;text-transform:uppercase}.epica-flow b{display:block;margin-top:5px;color:#4e6464;font-size:16px}.epica-flow .negative b{color:#a75070}.epica-flow .result{border-color:#b8ddcd;background:#f4fff9}.epica-flow .result b{color:#28735a}
.epica-bridge{display:flex;flex-wrap:wrap;gap:7px}.epica-bridge button,.epica-bridge a{display:inline-flex;align-items:center;min-height:34px;padding:7px 10px;border:1px solid #ddd1e1;border-radius:999px;background:#fff;color:#6e5875;font:inherit;font-size:9px;font-weight:900;text-decoration:none;cursor:pointer}.epica-bridge button:hover,.epica-bridge a:hover{border-color:var(--epica-accent);color:var(--epica-accent);background:var(--epica-accent-soft)}
.epica-formula{padding:11px 12px;border:1px dashed color-mix(in srgb,var(--epica-accent) 35%,#ded5e1);border-radius:14px;background:var(--epica-accent-soft);color:var(--epica-ink);font-size:10px;line-height:1.55}.epica-formula code{background:rgba(255,255,255,.75);color:inherit}
.epica-quote-audit{padding:15px 17px;border:1px solid #ddd5ec;border-radius:18px;background:linear-gradient(135deg,#fff 0%,#f7f4ff 100%)}.epica-quote-audit small{display:block;color:#7b6e95;font-size:9px;font-weight:950;text-transform:uppercase;letter-spacing:.05em}.epica-quote-audit blockquote{margin:8px 0 5px;color:#4f426f;font-size:clamp(16px,2.4vw,23px);font-weight:850;line-height:1.28;letter-spacing:-.015em}.epica-quote-audit p{margin:0;color:#81788f;font-size:9px;line-height:1.5}
.epica-amount-control{display:grid;grid-template-columns:minmax(170px,1fr) auto;align-items:center;gap:12px;margin:8px 0 2px;padding:11px 12px;border:1px solid #e2dcec;border-radius:14px;background:#fbfaff}.epica-amount-control label{display:grid;gap:6px;color:#716680;font-size:9px;font-weight:900}.epica-amount-control input{width:100%;accent-color:var(--epica-accent)}.epica-amount-control output{min-width:118px;color:var(--epica-ink);font-size:19px;font-weight:950;text-align:right}
.epica-rate-stack{display:grid;gap:7px}.epica-rate-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:10px 11px;border:1px solid #e7e1ed;border-radius:13px;background:#fdfcfe}.epica-rate-row b{display:block;color:var(--epica-ink);font-size:10px}.epica-rate-row small{display:block;margin-top:3px;color:var(--epica-muted);font-size:8px;line-height:1.4}.epica-rate-row strong{color:var(--epica-accent);font-size:15px;white-space:nowrap}
.epica-path-note{margin:9px 0 0;color:var(--epica-muted);font-size:9px;line-height:1.5}.epica-verdict{padding:16px 17px;border:1px solid #cfc4e6;border-left:5px solid var(--epica-accent);border-radius:16px;background:#faf8ff;color:var(--epica-ink);font-size:11px;line-height:1.6}.epica-verdict b{font-size:13px}
@media(max-width:980px){.epica-hero,.epica-grid,.epica-grid.equal{grid-template-columns:1fr}.epica-kpis{grid-template-columns:repeat(3,minmax(0,1fr))}.epica-status-card{grid-template-columns:minmax(0,1fr) auto;align-items:center}.epica-chart{height:390px}}
@media(max-width:720px){.epica-hero{padding:15px;border-radius:18px}.epica-status-card{grid-template-columns:1fr}.epica-toolbar{align-items:flex-start}.epica-toolbar>span{width:100%}.epica-toggle{flex:1 1 auto;min-width:86px}.epica-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.epica-kpi:last-child{grid-column:1/-1}.epica-panel{padding:12px}.epica-panel-head{display:block}.epica-panel-head .epica-chip{margin-top:6px}.epica-chart,.epica-chart.tall{height:430px}.epica-strata-read{grid-template-columns:1fr}.epica-flow{grid-template-columns:1fr}.epica-flow div:not(:last-child):after{content:"↓";right:50%;top:auto;bottom:-12px;transform:translateX(50%)}.epica-bridge button,.epica-bridge a{width:100%;justify-content:center}.epica-amount-control{grid-template-columns:1fr}.epica-amount-control output{text-align:left}}
`;
  document.head.appendChild(style);

  const tabs = document.getElementById('dash-main-tabs');
  const storyButton = tabs?.querySelector('[data-tab="tab-story"]');
  if (!tabs || !storyButton) return;

  storyButton.insertAdjacentHTML('afterend', `
    <button class="tab-btn" type="button" data-tab="tab-epica-households">Hogares · supervivencia</button>
    <button class="tab-btn" type="button" data-tab="tab-epica-dollars">Dólares · qué hay realmente</button>
    <button class="tab-btn" type="button" data-tab="tab-epica-caputo-colchon">Dólares del colchón · incentivos</button>
  `);

  const storyPanel = document.getElementById('tab-story');
  storyPanel.insertAdjacentHTML('beforebegin', `
  <section id="tab-epica-households" class="tab-panel">
    <div class="epica-shell households">
      <header class="epica-hero">
        <div><span class="epica-eyebrow">♡ Super-tab A · bolsillo real</span><h2>¿Quién llega sin comerse el futuro?</h2><p>La EPH permite separar sin doble conteo ahorro, préstamos, cuotas/fiado, venta de pertenencias y combinaciones. El resultado describe estrategias declaradas por hogares urbanos; no convierte un proxy en “llegar a fin de mes”.</p></div>
        <aside class="epica-status-card"><div><strong>Microdato reproducido y auditado</strong><small>78.994 registros de hogar · ponderador PONDIH · réplica del dosier INDEC dentro de 0,15 puntos.</small></div><div class="epica-status-row"><span class="epica-chip observed">observado</span><span class="epica-chip proxy">proxy visible</span><span class="epica-chip open">panel longitudinal pendiente</span></div></aside>
      </header>
      <div class="epica-toolbar" role="group" aria-label="Período de estrategias del hogar"><span>Período EPH</span><button class="epica-toggle" type="button" data-epica-household-period="2025-S1" aria-pressed="false">2025 · 1er semestre</button><button class="epica-toggle" type="button" data-epica-household-period="2025-S2" aria-pressed="false">2025 · 2º semestre</button><button class="epica-toggle active" type="button" data-epica-household-period="2026-Q1" aria-pressed="true">2026 · 1er trimestre</button></div>
      <div class="epica-kpis" aria-live="polite"><article class="epica-kpi"><small>Usó al menos una estrategia</small><b id="epicaHouseholdAny">71,8%</b><span>V13–V17 · observado</span></article><article class="epica-kpi"><small>No declaró estrategias V13–V17</small><b id="epicaHouseholdNone">28,2%</b><span>no equivale a suficiencia</span></article><article class="epica-kpi"><small>Sólo recursos corrientes</small><b id="epicaHouseholdCurrent">24,5%</b><span>proxy estricto</span></article><article class="epica-kpi"><small>Combinó 2+ canales</small><b id="epicaHouseholdMixed">36,6%</b><span>perfil excluyente</span></article><article class="epica-kpi"><small>Cuotas o fiado</small><b id="epicaHouseholdInstallments">50,7%</b><span>respuesta superpuesta</span></article></div>
      <div class="epica-grid">
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Perfiles mutuamente excluyentes</h3><p>Cada hogar aparece una sola vez. La suma cierra en 100% para el período seleccionado.</p></div><span class="epica-chip observed">microdato EPH</span></div><div id="epicaHouseholdProfileChart" class="epica-chart tall" role="img" aria-label="Distribución de estrategias de manutención mutuamente excluyentes"></div></section>
        <aside class="epica-panel"><div class="epica-panel-head"><div><h3>Alcance de la lectura</h3><p>Cuatro referencias para no sobreinterpretar el gráfico.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Qué muestran los datos</b><p>La proporción que recurrió a por lo menos una estrategia extraordinaria y la combinación exacta de canales declarados.</p></div><div class="epica-answer caution"><b>Qué no muestran</b><p>Un presupuesto completo, atrasos, monto de ahorro consumido, destino del préstamo ni suficiencia del ingreso.</p></div><div class="epica-answer good"><b>Lectura compatible</b><p>La salida de la pobreza puede coexistir con fragilidad: “no pobre” no implica ahorro positivo ni ausencia de deuda.</p></div><div class="epica-answer open"><b>Dato faltante para causalidad</b><p>Panel que siga al mismo hogar y enlace ingresos, patrimonio, crédito y mora a 3, 6 y 12 meses.</p></div></div></aside>
      </div>
      <div class="epica-grid equal">
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>La estrategia cambia con el estrato</h3><p>2026-Q1 · bajo = deciles 1–4 más hogares sin ingreso monetario; medio = 5–8; alto = 9–10.</p></div><span class="epica-chip observed">corte distributivo</span></div><div id="epicaHouseholdStrataChart" class="epica-chart" role="img" aria-label="Matriz de estrategias por estrato de ingreso"></div><div class="epica-strata-read"><div><b>Bajo</b>Más préstamos y venta de pertenencias.</div><div><b>Medio</b>Mayor peso de cuotas/fiado que el estrato bajo.</div><div><b>Alto</b>Más cuotas/fiado; no debe leerse automáticamente como estrés.</div></div></section>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Del indicador a las preguntas siguientes</h3><p>Este super-tab conecta módulos existentes sin duplicarlos.</p></div></div><div class="epica-formula"><b>Proxy corriente</b><br><code>fuente monetaria corriente ≥ 1</code> + ninguna fuente en especie + ninguna estrategia V13–V17. Es la aproximación observable más estricta; no es una prueba de holgura financiera.</div><div class="epica-bridge" style="margin-top:10px"><button type="button" onclick="activateTab('tab-poverty')">Pobreza absoluta →</button><button type="button" onclick="activateTab('tab-structure')">Vulnerabilidad →</button><button type="button" onclick="activateTab('tab-morosidad')">Mora bancaria →</button><button type="button" onclick="activateTab('tab-credit-mora')">Del shock a la mora →</button><button type="button" onclick="activateTab('tab-family')">Canasta familiar →</button></div></section>
      </div>
      <section class="sources-box"><h3>Fuentes, fórmula y descarga</h3><div class="source-links"><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_exclusive_profiles.csv">⬇ CSV · perfiles excluyentes</a><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_strategy_summary.csv">⬇ CSV · estrategias y estratos</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/ftp/cuadros/publicaciones/dosier_estrategias_manutencion_2025.pdf">📄 INDEC · dosier de manutención</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos">🗃️ INDEC · bases EPH</a></div><div class="sources-note"><b>Fecha de corte:</b> 31/08/2026. <b>Universo:</b> hogares de aglomerados urbanos relevados por EPH. <b>Fórmula:</b> clasificación booleana de V13–V17 con ponderación PONDIH; “préstamos” colapsa V14 y V15. Los originales y sus SHA-256 están preservados en el manifiesto de la investigación.</div></section>
    </div>
  </section>

  <section id="tab-epica-dollars" class="tab-panel">
    <div class="epica-shell dollars">
      <header class="epica-hero"><div><span class="epica-eyebrow">◇ Super-tab B · restricción externa</span><h2>¿Cuántos dólares hay realmente?</h2><p>Separamos stock bruto, composición, flujos predeterminados y deuda. El residual de estrés ayuda a leer liquidez, pero no se etiqueta como reservas netas ni como dólares libres.</p></div><aside class="epica-status-card"><div><strong>Fechas y perímetros visibles</strong><small>Reservas SDDS: 31/07/2026 · deuda: 31/03/2026 · balanza de pagos: 2026-Q1.</small></div><div class="epica-status-row"><span class="epica-chip observed">oficial observado</span><span class="epica-chip proxy">estrés estático</span><span class="epica-chip open">netas/propias N/D</span></div></aside></header>
      <div class="epica-kpis"><article class="epica-kpi"><small>Activos de reserva oficiales</small><b>USD 47.599 M</b><span>31/07/2026 · bruto</span></article><article class="epica-kpi"><small>Flujos predeterminados a 1 año</small><b>−USD 41.779 M</b><span>autoridad monetaria</span></article><article class="epica-kpi"><small>Residual de estrés a 1 año</small><b>USD 5.820 M</b><span>no es “reservas netas”</span></article><article class="epica-kpi"><small>Servicios de deuda 2027–31</small><b>USD 243.188 M</b><span>Administración Central</span></article><article class="epica-kpi"><small>Cuenta corriente 2026-Q1</small><b>−USD 1.651 M</b><span>último dato INDEC</span></article></div>
      <div class="epica-toolbar" role="group" aria-label="Vista principal de dólares"><span>Explorar el frente externo</span><button class="epica-toggle active" type="button" data-epica-dollar-view="liquidity" aria-pressed="true">Puente de liquidez</button><button class="epica-toggle" type="button" data-epica-dollar-view="composition" aria-pressed="false">Composición</button><button class="epica-toggle" type="button" data-epica-dollar-view="debt" aria-pressed="false">Deuda 2027–31</button></div>
      <div class="epica-grid"><section class="epica-panel"><div class="epica-panel-head"><div><h3 id="epicaDollarChartTitle">Stock bruto y residual por horizonte</h3><p id="epicaDollarChartSubtitle">Estrés estático: no supone nuevas entradas, rollover ni valuación.</p></div><span id="epicaDollarChartBadge" class="epica-chip proxy">escenario mecánico</span></div><div id="epicaDollarMainChart" class="epica-chart tall" role="img" aria-label="Puente de liquidez, composición de reservas y vencimientos de deuda"></div></section><aside class="epica-panel"><div class="epica-panel-head"><div><h3>Gate metodológico</h3><p>La etiqueta cambia la interpretación.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Medida oficial</b><p>Activos de reserva, composición y flujos predeterminados provienen de la planilla SDDS del BCRA.</p></div><div class="epica-answer caution"><b>Estimación identificada</b><p>El residual resta los flujos programados al stock y congela entradas, rollover y valuación.</p></div><div class="epica-answer open"><b>No disponible</b><p>Una cifra sincronizada de reservas netas, líquidas y propias. La porción en yuanes del swap no está separada con el detalle necesario.</p></div><div class="epica-answer good"><b>Definición BCRA</b><p>Líquidas = brutas menos oro, DEG y parte en yuanes del swap con China.</p></div></div></aside></div>
      <section class="epica-panel"><div class="epica-panel-head"><div><h3>Por qué superávit de bienes no significa superávit externo completo</h3><p>Balanza de pagos · 2026-Q1 · USD millones.</p></div><span class="epica-chip observed">identidad contable</span></div><div class="epica-flow"><div><small>Bienes</small><b>+6.339</b></div><div class="negative"><small>Servicios</small><b>−4.028</b></div><div class="negative"><small>Ingreso primario</small><b>−4.676</b></div><div><small>Ingreso secundario</small><b>+714</b></div><div class="result"><small>Cuenta corriente</small><b>−1.651</b></div></div></section>
      <div class="epica-grid equal"><section class="epica-panel"><div class="epica-panel-head"><div><h3>Qué ya puede afirmarse</h3><p>Conclusiones que pasan el gate.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Brutas ≠ libres</b><p>La composición y el calendario de flujos impiden tratar el stock como caja disponible sin condiciones.</p></div><div class="epica-answer good"><b>Comprar ≠ acumular uno a uno</b><p>Pagos, depósitos, financiamiento, intervención y valuación también mueven el stock.</p></div><div class="epica-answer caution"><b>Muro cuantificado, perímetro acotado</b><p>USD 243.188 M para 2027–2031 es Administración Central, no sector público consolidado.</p></div></div></section><section class="epica-panel"><div class="epica-panel-head"><div><h3>Seguir la evidencia</h3><p>Abrí los módulos detallados o descargá los puentes auditados.</p></div></div><div class="epica-bridge"><button type="button" onclick="activateTab('tab-bcra')">BCRA detallado →</button><button type="button" onclick="activateTab('tab-trade')">Balanza comercial →</button><button type="button" onclick="activateTab('tab-debt-public')">Deuda pública →</button><button type="button" onclick="activateTab('tab-program')">Escenarios →</button><button type="button" onclick="activateTab('tab-bigmac')">Tipo de cambio real →</button></div></section></div>
      <section class="sources-box"><h3>Fuentes, perímetros y descarga</h3><div class="source-links"><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/bcra_reserve_liquidity_bridge.csv">⬇ CSV · puente de liquidez</a><a class="download-link" download href="research/epica_dashito_2026/deep_dive_2026-08-31/derived/debt_service_2026_2031.csv">⬇ CSV · vencimientos</a><a class="source-link" target="_blank" rel="noopener" href="https://www.bcra.gob.ar/normas-especiales-para-la-divulgacion-de-datos-fmi/">🏦 BCRA · planilla SDDS</a><a class="source-link" target="_blank" rel="noopener" href="https://www.argentina.gob.ar/economia/finanzas/datos-trimestrales-de-la-deuda">📊 Finanzas · deuda trimestral</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-35-45">🌎 INDEC · cuentas internacionales</a></div><div class="sources-note"><b>Fecha de corte de investigación:</b> 31/08/2026. <b>Deuda:</b> perfil contractual estático de la Administración Central al 31/03/2026. <b>Liquidez:</b> la resta de flujos es una sensibilidad; no se presenta como medida oficial. Originales y SHA-256 disponibles en el manifiesto.</div></section>
    </div>
  </section>

  <section id="tab-epica-caputo-colchon" class="tab-panel">
    <div class="epica-shell caputo">
      <header class="epica-hero">
        <div><span class="epica-eyebrow">◎ Super-tab C · mapa de incentivos</span><h2>Los dólares del colchón: ¿qué decisiones intervienen?</h2><p>La pregunta reúne tres dimensiones distintas: quién dispone de ahorro invertible, qué atributos ofrece cada canal y qué objetivos declara la política. El tab las separa para comparar evidencia, mecanismos y límites.</p></div>
        <aside class="epica-status-card"><div><strong>Origen de la pregunta</strong><small>La intuición inicial de Miyu queda registrada en el storytelling. Aquí usamos una formulación más amplia basada en el argumento oficial: depósitos → crédito empresario → actividad y empleo.</small></div><div class="epica-status-row"><span class="epica-chip observed">argumento oficial localizado</span><span class="epica-chip proxy">paráfrasis de trabajo</span><span class="epica-chip open">alcance delimitado</span></div></aside>
      </header>
      <section class="epica-quote-audit"><small>Punto de partida del storytelling</small><blockquote>“Con estas nuevas medidas, los argentinos van a sacar los dólares del colchón para invertir”.</blockquote><p>Se conserva como paráfrasis de trabajo para explicar el origen de las preguntas; no se presenta como cita textual verificada de Luis Caputo.</p></section>
      <div class="epica-kpis"><article class="epica-kpi"><small>Ingreso del 20% superior</small><b>50,1%</b><span>INDEC · no mide riqueza</span></article><article class="epica-kpi"><small>Ingreso del 40% inferior</small><b>14,5%</b><span>INDEC · ingreso corriente</span></article><article class="epica-kpi"><small>Depósitos privados USD</small><b>USD 40.300 M</b><span>agosto 2026 · oficial</span></article><article class="epica-kpi"><small>Capacidad de crédito ya libre</small><b>USD 5.800 M</b><span>contrapunto oficial</span></article><article class="epica-kpi"><small>Brecha de tasa observada</small><b>2,09 p.p.</b><span>T-Bill 52s vs PF USD 60+</span></article></div>

      <div class="epica-grid">
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Quiénes tienen margen para invertir?</h3><p>Participación de cada decil en el ingreso corriente individual · 2026-T1.</p></div><span class="epica-chip observed">INDEC</span></div><div id="epicaCaputoIncomeChart" class="epica-chart tall" role="img" aria-label="Participación del ingreso corriente por decil"></div></section>
        <aside class="epica-panel"><div class="epica-panel-head"><div><h3>Qué aporta y qué no resuelve</h3><p>Capacidad probable, no inventario de billetes.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Distribución observada</b><p>El 20% superior reúne 50,1% del ingreso; el decil 10 solo, 33,5%. La capacidad de ahorro no está repartida de forma homogénea.</p></div><div class="epica-answer caution"><b>Alcance del indicador</b><p>La EPH no pregunta cuántos dólares posee cada hogar. Informa ingresos, no identifica al tenedor de efectivo o activos.</p></div><div class="epica-answer caution"><b>Contexto de los hogares</b><p>71,8% declaró al menos una estrategia extraordinaria de sostenimiento en 2026-T1; eso tampoco equivale automáticamente a falta de ahorro.</p></div><div class="epica-answer open"><b>Información todavía abierta</b><p>La PII agrupa hogares, empresas e instituciones sin fines de lucro. No permite aislar el efectivo familiar.</p></div></div></aside>
      </div>

      <div class="epica-grid equal">
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Qué rendimiento de referencia ofrece cada alternativa?</h3><p>Ganancia bruta anual ilustrativa; bases de tasa distintas, antes de comisiones e impuestos.</p></div><span class="epica-chip proxy">simulador simple</span></div><div class="epica-amount-control"><label for="epicaCaputoAmount">Monto a comparar · USD<input id="epicaCaputoAmount" type="range" min="1000" max="100000" step="1000" value="10000"></label><output id="epicaCaputoAmountOutput" for="epicaCaputoAmount">USD 10.000</output></div><div id="epicaCaputoReturnChart" class="epica-chart" role="img" aria-label="Ganancia bruta anual estimada por canal"></div></section>
        <aside class="epica-panel"><div class="epica-panel-head"><div><h3>Banco local y cuenta comitente</h3><p>La comitente es el canal; el riesgo depende del activo comprado.</p></div></div><div class="epica-rate-stack"><div class="epica-rate-row"><div><b>Efectivo físico · 0%</b><small>Liquidez fuera del sistema; robo/pérdida y cero renta.</small></div><strong id="epicaCaputoGainCash">USD 0</strong></div><div class="epica-rate-row"><div><b>Caja de ahorro USD · 0,22% TNA</b><small>Operatoria local y garantía limitada; muy baja remuneración.</small></div><strong id="epicaCaputoGainSavings">+USD 22</strong></div><div class="epica-rate-row"><div><b>Plazo fijo USD 60+ · 2,05% TNA</b><small>Mayor tasa bancaria; dinero inmovilizado.</small></div><strong id="epicaCaputoGainFixed">+USD 205</strong></div><div class="epica-rate-row"><div><b>T-Bill EE.UU. 52 semanas · 4,14%</b><small>Bajo riesgo crediticio; suma comisiones, impuestos, custodia y riesgo de precio si se vende antes.</small></div><strong id="epicaCaputoGainTreasury">+USD 414</strong></div></div><div class="epica-formula" style="margin-top:10px"><b>Comparación de referencia:</b> en estas fechas, la alternativa externa muestra mayor rendimiento bruto, mientras el banco ofrece otros atributos: comodidad, pagos locales, garantía aplicable, simplicidad operativa y liquidez. La conveniencia depende del perfil y de los costos reales.</div></aside>
      </div>

      <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Cómo cambia la transmisión según el canal?</h3><p>Elegí un destino y observá decisiones, intermediarios y efectos posibles.</p></div><span class="epica-chip proxy">mecanismo, no pronóstico</span></div><div class="epica-toolbar" role="group" aria-label="Canal de uso de los dólares"><span>Escenario de transmisión</span><button class="epica-toggle active" type="button" data-epica-caputo-channel="bank" aria-pressed="true">Depósito bancario</button><button class="epica-toggle" type="button" data-epica-caputo-channel="broker" aria-pressed="false">Comitente + activo externo</button><button class="epica-toggle" type="button" data-epica-caputo-channel="spend" aria-pressed="false">Consumo o inversión directa</button></div><div id="epicaCaputoPath" class="epica-flow" style="margin-top:10px"><div><small>Dueño</small><b>Ahorro USD</b></div><div><small>Intermediario</small><b>Banco local</b></div><div><small>Decisión ajena</small><b>Crédito empresa</b></div><div><small>Mecánica</small><b>Liquida USD</b></div><div class="result"><small>Resultado buscado</small><b>Actividad y empleo</b></div></div><p id="epicaCaputoPathNote" class="epica-path-note">El beneficio macro es posible, no automático: hacen falta banco dispuesto, empresa elegible, demanda solvente y un uso que efectivamente aumente producción o empleo.</p></section>

      <div class="epica-grid equal">
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Qué objetivos y mecanismos presenta la política?</h3><p>Declaraciones oficiales e interpretaciones diferenciadas.</p></div></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Objetivo declarado · formalización</b><p>Las comunicaciones oficiales buscan que ahorros informales entren al sistema y asocian esa formalización con mayor actividad e ingresos fiscales.</p></div><div class="epica-answer good"><b>Mecanismo declarado · crédito y empleo</b><p>Caputo presenta al depósito como fondeo para préstamos a empresas, rentabilidad, inversión y empleo.</p></div><div class="epica-answer caution"><b>Interpretación posible · crecer sin nuevo estímulo</b><p>Movilizar ahorro existente ofrece un canal de expansión que no requiere aumentar gasto público ni emisión. Es una lectura del mecanismo, no un objetivo textual.</p></div><div class="epica-answer caution"><b>Efecto posible · mercado de cambios</b><p>Los préstamos en USD deben liquidarse en el mercado de cambios: si se otorgan, pueden sumar oferta de divisas. No garantiza acumulación de reservas uno a uno.</p></div></div></section>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Qué preguntas permanecen abiertas?</h3><p>Datos que matizan la lectura y objetivos no identificados en las fuentes.</p></div></div><div class="epica-answer-grid"><div class="epica-answer caution"><b>Capacidad crediticia disponible</b><p>La presentación estimó unos USD 5.800 millones adicionales de crédito posibles con los depósitos existentes. La falta de fondeo no aparece como único límite inmediato.</p></div><div class="epica-answer open"><b>Estabilidad bancaria</b><p>Las fuentes revisadas no la identifican como objetivo principal. Harían falta otros documentos para evaluar ese posible propósito.</p></div><div class="epica-answer open"><b>Financiamiento del Tesoro</b><p>La regulación limita la tenencia de deuda pública en relación con los préstamos en dólares; no surge como objetivo central de estas medidas.</p></div><div class="epica-answer open"><b>Motivaciones personales</b><p>Quedan fuera del alcance empírico. El análisis se concentra en objetivos declarados, incentivos, restricciones y beneficiarios.</p></div></div></section>
      </div>

      <section class="epica-panel"><div class="epica-panel-head"><div><h3>Síntesis de la exploración</h3><p>Cómo se relacionan capacidad de ahorro, decisión privada y objetivo de política.</p></div><span class="epica-chip observed">alcance y límites</span></div><div class="epica-verdict"><b>La pregunta admite respuestas distintas según el actor y el canal.</b> El ingreso disponible está concentrado, pero los datos no identifican qué hogares poseen dólares. El banco local ofrece utilidad transaccional, simplicidad y cobertura limitada; una cuenta comitente permite acceder a otros activos con diferentes rendimientos, costos y riesgos. Para la política económica, el depósito local agrega un posible canal de formalización, crédito y oferta de divisas. La capacidad crediticia ya disponible sugiere que el fondeo es una pieza del mecanismo, no necesariamente la única restricción. No es recomendación financiera individual.</div><div class="epica-bridge" style="margin-top:10px"><button type="button" onclick="activateTab('tab-epica-households')">Quién tiene margen →</button><button type="button" onclick="activateTab('tab-epica-dollars')">Restricción externa →</button><button type="button" onclick="activateTab('tab-bcra')">Sistema bancario →</button><button type="button" onclick="activateTab('tab-debt-public')">Deuda pública →</button></div></section>

      <section class="sources-box"><h3>Fuentes, respaldo y descarga</h3><div class="source-links"><a class="download-link" download href="research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/income_distribution_2026_q1.csv">⬇ CSV · distribución del ingreso</a><a class="download-link" download href="research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/channel_comparison.csv">⬇ CSV · banco y comitente</a><a class="download-link" download href="research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/policy_questions_matrix.csv">⬇ CSV · preguntas y evidencia</a><a class="download-link" download href="research/epica_dashito_2026/caputo_colchon_2026-08-31/source_manifest.csv">⬇ Manifiesto SHA-256</a><a class="source-link" target="_blank" rel="noopener" href="https://www.argentina.gob.ar/node/510406">🏛️ Economía · crédito en USD</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/uploads/informesdeprensa/ingresos1trim26536C8EDD3E.pdf">📊 INDEC · distribución del ingreso</a><a class="source-link" target="_blank" rel="noopener" href="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202608&amp;type=daily_treasury_bill_rates">🇺🇸 US Treasury · T-Bills</a><a class="source-link" target="_blank" rel="noopener" href="https://www.sedesa.com.ar/wp-content/uploads/2026/03/A8407.pdf">🛡️ Garantía de depósitos</a></div><div class="sources-note"><b>Corte:</b> 31/08/2026. <b>Tasas:</b> BCRA al 27/08 y US Treasury al 28/08. <b>Garantía:</b> hasta ARS 50 millones por persona/entidad desde 01/04/2026; moneda extranjera convertida al tipo de referencia aplicable. La hipótesis de origen figura en el storytelling; este tab organiza preguntas y mecanismos. Originales completos, registro de URL y SHA-256 preservados en el repo.</div></section>
    </div>
  </section>
  `);

  const householdData = {
    '2025-S1': { any:70.690, none:29.310, current:25.811, mixed:36.246, installments:50.874, profiles:[29.310,8.768,3.500,21.169,1.007,36.246] },
    '2025-S2': { any:70.533, none:29.467, current:25.386, mixed:36.750, installments:51.563, profiles:[29.467,7.546,3.964,21.155,1.119,36.750] },
    '2026-Q1': { any:71.778, none:28.222, current:24.534, mixed:36.599, installments:50.660, profiles:[28.222,9.190,3.542,21.510,0.937,36.599] }
  };
  const householdProfileLabels = ['Ninguna V13–V17','Sólo ahorro','Sólo préstamos','Sólo cuotas/fiado','Sólo venta','Combinación 2+'];
  let householdPeriod = '2026-Q1';
  let dollarView = 'liquidity';
  let caputoChannel = 'bank';
  const pct = value => `${value.toLocaleString('es-AR',{minimumFractionDigits:1,maximumFractionDigits:1})}%`;
  const usd = value => `USD ${Math.round(value).toLocaleString('es-AR')}`;
  const plotConfig = { responsive:true, displaylogo:false, displayModeBar:false };

  function plotBase(mobile) {
    return {paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'#fff',font:{family:'Inter,system-ui,sans-serif',size:mobile?9:10,color:'#65516d'},margin:{l:mobile?48:60,r:18,t:24,b:mobile?92:68},hoverlabel:{bgcolor:'#fff',bordercolor:'#d9cde0',font:{color:'#5d4867'}}};
  }

  function renderHouseholdProfiles() {
    const target = document.getElementById('epicaHouseholdProfileChart');
    if (!target || !window.Plotly) return;
    const row = householdData[householdPeriod];
    const mobile = window.innerWidth <= 720;
    ['Any','None','Current','Mixed','Installments'].forEach(key => {
      const map = {Any:'any',None:'none',Current:'current',Mixed:'mixed',Installments:'installments'};
      const element = document.getElementById(`epicaHousehold${key}`);
      if (element) element.textContent = pct(row[map[key]]);
    });
    const layout = {...plotBase(mobile),showlegend:false,bargap:.27,yaxis:{title:'% de hogares',range:[0,44],gridcolor:'#eee7f0',ticksuffix:'%',fixedrange:true},xaxis:{tickangle:mobile?-35:-15,fixedrange:true,automargin:true}};
    Plotly.react(target,[{type:'bar',x:householdProfileLabels,y:row.profiles,text:row.profiles.map(pct),textposition:'outside',cliponaxis:false,marker:{color:['#b7a8bd','#e5a8bd','#d3b0df','#d9bd71','#d88e84','#9c5e83'],line:{color:'#fff',width:1}},hovertemplate:'<b>%{x}</b><br>%{y:.3f}% de hogares<extra></extra>'}],layout,plotConfig);
  }

  function renderHouseholdStrata() {
    const target = document.getElementById('epicaHouseholdStrataChart');
    if (!target || !window.Plotly) return;
    const mobile = window.innerWidth <= 720;
    const x = ['Ahorros','Cuotas/fiado','Préstamos','Venta','Alguna V13–17','Proxy corriente'];
    const z = [[39.847,39.752,32.941,14.979,69.745,23.926],[39.093,54.037,24.316,9.011,71.507,25.849],[36.858,66.040,16.747,5.199,76.442,23.141]];
    const layout = {...plotBase(mobile),margin:{l:mobile?58:70,r:15,t:18,b:mobile?100:72},xaxis:{tickangle:mobile?-38:-20,fixedrange:true},yaxis:{fixedrange:true,autorange:'reversed'},coloraxis:{cmin:0,cmax:80,colorscale:[[0,'#fff8fb'],[.35,'#efd3df'],[.7,'#c382a2'],[1,'#744b78']],colorbar:{title:'%',thickness:10,len:.8}}};
    Plotly.react(target,[{type:'heatmap',x,y:['Bajo','Medio','Alto'],z,coloraxis:'coloraxis',text:z.map(row=>row.map(pct)),texttemplate:'%{text}',hovertemplate:'<b>%{y}</b><br>%{x}: %{z:.3f}%<extra></extra>'}],layout,plotConfig);
  }

  function setDollarMeta(title, subtitle, badge, kind) {
    const titleEl = document.getElementById('epicaDollarChartTitle');
    const subtitleEl = document.getElementById('epicaDollarChartSubtitle');
    const badgeEl = document.getElementById('epicaDollarChartBadge');
    if (titleEl) titleEl.textContent = title;
    if (subtitleEl) subtitleEl.textContent = subtitle;
    if (badgeEl) { badgeEl.textContent = badge; badgeEl.className = `epica-chip ${kind}`; }
  }

  function renderDollarChart() {
    const target = document.getElementById('epicaDollarMainChart');
    if (!target || !window.Plotly) return;
    const mobile = window.innerWidth <= 720;
    let traces;
    let layout;
    if (dollarView === 'composition') {
      setDollarMeta('Composición de los activos de reserva','Planilla SDDS · 31/07/2026 · USD millones.','medida oficial','observed');
      traces = [{type:'pie',labels:['Moneda extranjera','Oro','DEG','Otros activos'],values:[38433.62,8046.37,908.14,211.06],hole:.58,sort:false,textinfo:'label+percent',textposition:mobile?'inside':'outside',marker:{colors:['#4b9a8f','#d9b65c','#8e77b8','#cf91a8'],line:{color:'#fff',width:2}},hovertemplate:'<b>%{label}</b><br>USD %{value:,.2f} M<br>%{percent}<extra></extra>'}];
      layout = {...plotBase(mobile),margin:{l:20,r:20,t:18,b:20},showlegend:mobile,legend:{orientation:'h',y:-.08},annotations:[{text:'USD 47.599 M<br><span style="font-size:9px">total oficial</span>',x:.5,y:.5,showarrow:false,font:{size:16,color:'#315d5b'}}]};
    } else if (dollarView === 'debt') {
      setDollarMeta('Muro de servicios 2027–2031','Administración Central · perfil estático al 31/03/2026.','perímetro acotado','proxy');
      const years=[2027,2028,2029,2030,2031],capital=[72570.254,40028.613,26234.018,22527.077,38448.478],interest=[10141.386,9761.577,8982.286,7901.508,6592.491];
      traces=[{type:'bar',name:'Capital',x:years,y:capital,marker:{color:'#4f8f88'},hovertemplate:'<b>%{x}</b><br>Capital USD %{y:,.0f} M<extra></extra>'},{type:'bar',name:'Intereses',x:years,y:interest,marker:{color:'#d5ad59'},hovertemplate:'<b>%{x}</b><br>Intereses USD %{y:,.0f} M<extra></extra>'}];
      layout={...plotBase(mobile),barmode:'stack',legend:{orientation:'h',y:1.12},yaxis:{title:'USD millones',gridcolor:'#e8efed',fixedrange:true},xaxis:{dtick:1,fixedrange:true},hovermode:'x unified'};
    } else {
      setDollarMeta('Stock bruto y residual por horizonte','Estrés estático: no supone nuevas entradas, rollover ni valuación.','escenario mecánico','proxy');
      const labels=['Activos oficiales','Después de ≤1 mes','Después de ≤3 meses','Después de ≤1 año'],values=[47599.19,10471.37,10227.88,5819.75];
      traces=[{type:'bar',x:labels,y:values,text:values.map(v=>`USD ${Math.round(v).toLocaleString('es-AR')} M`),textposition:'outside',cliponaxis:false,marker:{color:['#4b9a8f','#d8bd70','#cfa967','#c78478'],line:{color:'#fff',width:1}},hovertemplate:'<b>%{x}</b><br>USD %{y:,.2f} M<extra></extra>'}];
      layout={...plotBase(mobile),showlegend:false,yaxis:{title:'USD millones',range:[0,53000],gridcolor:'#e8efed',fixedrange:true},xaxis:{tickangle:mobile?-30:-12,fixedrange:true,automargin:true},annotations:[{xref:'paper',yref:'paper',x:.99,y:.98,xanchor:'right',text:'Flujos acumulados a 1 año: −USD 41.779 M',showarrow:false,font:{size:9,color:'#8b6a40'},bgcolor:'#fff8e7',bordercolor:'#e3c97e',borderpad:5}]};
    }
    Plotly.react(target,traces,layout,plotConfig);
  }

  function renderCaputoIncome() {
    const target = document.getElementById('epicaCaputoIncomeChart');
    if (!target || !window.Plotly) return;
    const mobile = window.innerWidth <= 720;
    const shares = [1.8,3.2,4.2,5.3,6.3,7.6,9.3,12.1,16.6,33.5];
    const labels = shares.map((_,index) => `D${index + 1}`);
    const layout = {...plotBase(mobile),showlegend:false,bargap:.22,yaxis:{title:'% del ingreso corriente',range:[0,39],gridcolor:'#eeeaf4',ticksuffix:'%',fixedrange:true},xaxis:{title:'Decil de ingreso individual',fixedrange:true},annotations:[{x:'D10',y:36.5,text:'El decil 10 concentra 33,5%',showarrow:false,font:{size:9,color:'#67559a'},bgcolor:'#f6f3ff',bordercolor:'#d7ceed',borderpad:4}]};
    Plotly.react(target,[{type:'bar',x:labels,y:shares,text:shares.map(pct),textposition:'outside',cliponaxis:false,marker:{color:shares.map((_,index)=>index>=8?'#67559a':'#c8bee1'),line:{color:'#fff',width:1}},hovertemplate:'<b>Decil %{x}</b><br>%{y:.1f}% del ingreso<extra></extra>'}],layout,plotConfig);
  }

  function renderCaputoReturns() {
    const target = document.getElementById('epicaCaputoReturnChart');
    const input = document.getElementById('epicaCaputoAmount');
    if (!target || !input || !window.Plotly) return;
    const mobile = window.innerWidth <= 720;
    const amount = Number(input.value);
    const rates = [0,0.22,2.05,4.14];
    const gains = rates.map(rate => amount * rate / 100);
    const output = document.getElementById('epicaCaputoAmountOutput');
    if (output) output.textContent = usd(amount);
    [['Cash',0],['Savings',1],['Fixed',2],['Treasury',3]].forEach(([key,index]) => {
      const element = document.getElementById(`epicaCaputoGain${key}`);
      if (element) element.textContent = `${Number(index) === 0 ? '' : '+'}${usd(gains[Number(index)])}`;
    });
    const labels = ['Efectivo','Caja ahorro USD','PF USD 60+','T-Bill EE.UU. 52s'];
    const layout = {...plotBase(mobile),showlegend:false,margin:{l:mobile?52:64,r:18,t:28,b:mobile?105:78},yaxis:{title:'Ganancia bruta estimada · USD',range:[0,Math.max(50,Math.max(...gains)*1.22)],gridcolor:'#eeeaf4',fixedrange:true},xaxis:{tickangle:mobile?-32:-16,fixedrange:true,automargin:true}};
    Plotly.react(target,[{type:'bar',x:labels,y:gains,text:gains.map(value=>value===0?'USD 0':`+${usd(value)}`),textposition:'outside',cliponaxis:false,marker:{color:['#c7bfce','#b9aecf','#9383bb','#67559a'],line:{color:'#fff',width:1}},customdata:rates,hovertemplate:'<b>%{x}</b><br>Tasa de referencia: %{customdata:.2f}%<br>Ganancia bruta: USD %{y:,.2f}<extra></extra>'}],layout,plotConfig);
  }

  function renderCaputoPath() {
    const target = document.getElementById('epicaCaputoPath');
    const note = document.getElementById('epicaCaputoPathNote');
    if (!target || !note) return;
    const paths = {
      bank: {
        steps:[['Dueño','Ahorro USD'],['Intermediario','Banco local'],['Decisión ajena','Crédito empresa'],['Mecánica','Liquida USD'],['Resultado buscado','Actividad y empleo']],
        note:'El beneficio macro es posible, no automático: hacen falta banco dispuesto, empresa elegible, demanda solvente y un uso que efectivamente aumente producción o empleo.'
      },
      broker: {
        steps:[['Dueño','Ahorro USD'],['Intermediario','Cuenta comitente'],['Decisión propia','Compra T-Bill'],['Beneficio privado','Renta y liquidez'],['Efecto local directo','Sin fondeo bancario']],
        note:'El ahorrista elige el activo y captura su renta, descontados costos e impuestos. Ese dinero no amplía directamente la capacidad de crédito de un banco argentino.'
      },
      spend: {
        steps:[['Dueño','Ahorro USD'],['Uso','Vende o paga'],['Destino','Consumo / proyecto'],['Transmisión','Demanda y empleo'],['Resultado posible','Actividad e impuestos']],
        note:'También puede movilizar actividad sin depósito previo. El resultado depende de cuánto sea producción local, importación, ahorro de terceros o inversión efectiva.'
      }
    };
    const selected = paths[caputoChannel];
    target.innerHTML = selected.steps.map(([label,value],index)=>`<div class="${index===selected.steps.length-1?'result':''}"><small>${label}</small><b>${value}</b></div>`).join('');
    note.textContent = selected.note;
  }

  window.renderEpicaHouseholds = () => { renderHouseholdProfiles(); renderHouseholdStrata(); };
  window.renderEpicaDollars = renderDollarChart;
  window.renderEpicaCaputo = () => { renderCaputoIncome(); renderCaputoReturns(); renderCaputoPath(); };

  document.querySelectorAll('[data-epica-household-period]').forEach(button => button.addEventListener('click', () => {
    householdPeriod = button.dataset.epicaHouseholdPeriod;
    document.querySelectorAll('[data-epica-household-period]').forEach(item => { const active=item===button; item.classList.toggle('active',active); item.setAttribute('aria-pressed',String(active)); });
    renderHouseholdProfiles();
  }));
  document.querySelectorAll('[data-epica-dollar-view]').forEach(button => button.addEventListener('click', () => {
    dollarView = button.dataset.epicaDollarView;
    document.querySelectorAll('[data-epica-dollar-view]').forEach(item => { const active=item===button; item.classList.toggle('active',active); item.setAttribute('aria-pressed',String(active)); });
    renderDollarChart();
  }));
  document.getElementById('epicaCaputoAmount')?.addEventListener('input', renderCaputoReturns);
  document.querySelectorAll('[data-epica-caputo-channel]').forEach(button => button.addEventListener('click', () => {
    caputoChannel = button.dataset.epicaCaputoChannel;
    document.querySelectorAll('[data-epica-caputo-channel]').forEach(item => { const active=item===button; item.classList.toggle('active',active); item.setAttribute('aria-pressed',String(active)); });
    renderCaputoPath();
  }));

  tabs.querySelector('[data-tab="tab-epica-households"]')?.addEventListener('click', () => window.setTimeout(window.renderEpicaHouseholds, 190));
  tabs.querySelector('[data-tab="tab-epica-dollars"]')?.addEventListener('click', () => window.setTimeout(window.renderEpicaDollars, 190));
  tabs.querySelector('[data-tab="tab-epica-caputo-colchon"]')?.addEventListener('click', () => window.setTimeout(window.renderEpicaCaputo, 190));
  window.addEventListener('resize', () => {
    if (document.getElementById('tab-epica-households')?.classList.contains('active')) window.renderEpicaHouseholds();
    if (document.getElementById('tab-epica-dollars')?.classList.contains('active')) window.renderEpicaDollars();
    if (document.getElementById('tab-epica-caputo-colchon')?.classList.contains('active')) window.renderEpicaCaputo();
  });
})();
