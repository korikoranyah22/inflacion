(() => {
  'use strict';

  if (document.getElementById('political-wealth-v2')) return;

  const scriptUrl = document.currentScript?.src;
  const publicBaseUrl = scriptUrl ? new URL('../',scriptUrl) : new URL('./',document.baseURI);
  const DATA_URL = new URL('research/political_wealth_2026-09-01/derived/dashboard_data_2017_2025.json',publicBaseUrl).href;
  const ROSTER_URL = new URL('research/political_wealth_2026-09-01/derived/active_politicians_coverage_2026-09-01.json',publicBaseUrl).href;
  const RESEARCH_URL = new URL('research/political_wealth_2026-09-01/derived/active_politician_research_summary_2026-09-01.json',publicBaseUrl).href;
  const KARINA_AUDIT_URL = new URL('research/political_wealth_2026-09-01/derived/karina_milei_revaluation_audit_2023_2025.json',publicBaseUrl).href;
  const JAVIER_AUDIT_URL = new URL('research/political_wealth_2026-09-01/derived/javier_milei_revaluation_audit_2023_2025.json',publicBaseUrl).href;

  async function fetchJson(url,label){
    let lastError;
    for(const delay of [0,180,650]){
      if(delay) await new Promise(resolve=>window.setTimeout(resolve,delay));
      try{
        const response = await fetch(url,{cache:'no-store',credentials:'same-origin'});
        if(!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      }catch(error){
        lastError = error;
      }
    }
    throw new Error(`${label}: ${lastError?.message||'falló la carga'}`);
  }
  const style = document.createElement('style');
  style.id = 'political-wealth-v2';
  style.textContent = `
.epica-shell.wealth{--epica-accent:#7d536d;--epica-accent-soft:#fbf0f6;--epica-ink:#593f51;--epica-muted:#786673}
.pw-controls{display:flex;min-width:0;max-width:100%;flex-wrap:wrap;gap:7px}.pw-person-button{min-height:34px;padding:7px 11px;border:1px solid #dfd0da;border-radius:999px;background:#fff;color:#725d6b;font:inherit;font-size:10px;font-weight:900;cursor:pointer}.pw-person-button.active{border-color:var(--epica-accent);background:var(--epica-accent-soft);color:var(--epica-accent);box-shadow:inset 0 0 0 1px var(--epica-accent)}
.pw-kpi-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px}.pw-kpi{min-width:0;padding:13px;border:1px solid #e5dbe1;border-radius:17px;background:#fff}.pw-kpi small{display:block;min-height:26px;color:#8a7482;font-size:8px;font-weight:950;text-transform:uppercase;letter-spacing:.035em}.pw-kpi b{display:block;margin:6px 0 3px;color:#5c4353;font-size:clamp(18px,2.15vw,28px);line-height:1}.pw-kpi span{display:block;color:#897985;font-size:8px;font-weight:800;line-height:1.4}.pw-kpi.review{border-left:4px solid #cf708b}.pw-kpi.expected{border-left:4px solid #6eb092}.pw-kpi.partial{border-left:4px solid #d7a24d}.pw-kpi.frozen{border-left:4px solid #8292a5}
.pw-callout{padding:13px 14px;border:1px solid #ead7e1;border-left:5px solid var(--epica-accent);border-radius:15px;background:#fff9fc;color:#66505f;font-size:10px;line-height:1.6}.pw-callout strong{color:#523747}
.pw-table-wrap{min-width:0;max-width:100%;overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-gutter:stable;scrollbar-width:thin;-webkit-overflow-scrolling:touch;touch-action:pan-x pan-y;border:1px solid #eadfe5;border-radius:15px}.pw-table-wrap::-webkit-scrollbar{height:9px;width:9px}.pw-table-wrap::-webkit-scrollbar-thumb{border:2px solid transparent;border-radius:999px;background:#cdbcc6;background-clip:padding-box}.pw-table{width:100%;border-collapse:collapse;min-width:760px;background:#fff}.pw-table th,.pw-table td{padding:10px 11px;border-bottom:1px solid #eee5ea;text-align:left;font-size:9px;line-height:1.4}.pw-table th{background:#faf6f8;color:#715767;font-size:8px;text-transform:uppercase;letter-spacing:.035em}.pw-table td{color:#756470}.pw-table td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.pw-table tr:last-child td{border-bottom:0}
.pw-status{display:inline-flex;align-items:center;padding:4px 7px;border-radius:999px;font-size:8px;font-weight:950;white-space:nowrap}.pw-status.expected{background:#effaf5;color:#277056}.pw-status.review{background:#fff1f5;color:#a54768}.pw-status.partial{background:#fff8e8;color:#88631d}.pw-status.missing{background:#f2f1f2;color:#746f72}.pw-status.frozen{background:#edf2f7;color:#53657a}
.pw-quality-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.pw-quality-grid div{padding:11px;border:1px solid #e5dce1;border-radius:14px;background:#fff}.pw-quality-grid b{display:block;color:#5d4353;font-size:10px}.pw-quality-grid span{display:block;margin-top:4px;color:#816f79;font-size:8px;line-height:1.45}
.pw-benchmark-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.pw-benchmark-card{padding:13px;border:1px solid #e5dce1;border-radius:15px;background:#fff}.pw-benchmark-card small{display:block;color:#927989;font-size:8px;font-weight:950;text-transform:uppercase}.pw-benchmark-card b{display:block;margin:5px 0;color:#5e4354;font-size:18px}.pw-benchmark-card p{margin:0;color:#826f7a;font-size:8px;line-height:1.5}.pw-benchmark-card.low{border-top:4px solid #6eb092}.pw-benchmark-card.medium{border-top:4px solid #d2aa58}.pw-benchmark-card.high{border-top:4px solid #a35e7b}
.pw-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}.pw-flow div{position:relative;padding:12px;border:1px solid #e6dce2;border-radius:14px;background:#fff}.pw-flow div:not(:last-child):after{content:'→';position:absolute;right:-8px;top:50%;z-index:2;transform:translateY(-50%);color:#a48d9a;font-weight:950}.pw-flow small{display:block;color:#927989;font-size:8px;font-weight:950;text-transform:uppercase}.pw-flow b{display:block;margin:5px 0;color:#5e4354;font-size:11px}.pw-flow p{margin:0;color:#826f7a;font-size:8px;line-height:1.4}
.pw-data-note{margin-top:8px;color:#8b7884;font-size:8px;line-height:1.45}.pw-surface[hidden]{display:none!important}.pw-chart-empty{display:grid;place-items:center;min-height:230px;padding:25px;text-align:center;color:#826f7a;font-size:10px;line-height:1.6}.pw-loading{padding:28px;text-align:center;color:#7d6875;font-size:11px}
.pw-roster-tools{display:grid;grid-template-columns:minmax(220px,2fr) repeat(2,minmax(150px,1fr));gap:8px;margin:10px 0}.pw-roster-tools label{display:grid;gap:4px;color:#806c78;font-size:8px;font-weight:950;text-transform:uppercase;letter-spacing:.03em}.pw-roster-tools input,.pw-roster-tools select{width:100%;min-height:38px;padding:8px 10px;border:1px solid #dfd2da;border-radius:11px;background:#fff;color:#614c59;font:inherit;font-size:10px}.pw-roster-tools input:focus,.pw-roster-tools select:focus{outline:2px solid #dec4d3;outline-offset:1px}.pw-roster-wrap{max-height:540px;overflow:auto}.pw-roster-wrap .pw-table{min-width:1120px}.pw-roster-wrap .pw-table th{position:sticky;top:0;z-index:2}.pw-open-series{min-height:28px;padding:5px 8px;border:1px solid #cfaec2;border-radius:9px;background:#fff7fb;color:#7d536d;font:inherit;font-size:8px;font-weight:950;cursor:pointer}.pw-scope-line{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin-top:8px;color:#806d79;font-size:9px}.pw-scope-line b{color:#5d4353}
.pw-case-audit{border:1px solid #d9c5d1;background:linear-gradient(145deg,#fff 0%,#fff7fb 100%)}.pw-case-lead{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.65fr);gap:10px;margin:10px 0}.pw-case-verdict{padding:15px;border-radius:16px;background:#593f51;color:#fff;font-size:10px;line-height:1.6}.pw-case-verdict strong{display:block;margin-bottom:5px;color:#fff;font-size:13px}.pw-case-verdict span{color:#f5e9f0}.pw-case-source{padding:14px;border:1px solid #eadbe3;border-radius:16px;background:#fff;color:#765f6d;font-size:9px;line-height:1.55}.pw-case-source b{display:block;margin-bottom:4px;color:#5d4353;font-size:10px}.pw-case-audit .pw-table{min-width:900px}
@media(max-width:980px){.pw-kpi-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.pw-flow{grid-template-columns:repeat(2,minmax(0,1fr))}.pw-flow div:nth-child(2):after,.pw-flow div:nth-child(4):after{display:none}.pw-quality-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:720px){.pw-kpi-grid,.pw-quality-grid,.pw-flow,.pw-benchmark-grid,.pw-roster-tools,.pw-case-lead{grid-template-columns:1fr}.pw-flow div:not(:last-child):after{content:'↓';right:50%;top:auto;bottom:-12px;transform:translateX(50%)}.pw-flow div:nth-child(2):after,.pw-flow div:nth-child(4):after{display:block}.pw-controls{flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;overscroll-behavior-inline:contain;scroll-snap-type:x proximity;scrollbar-width:thin;scrollbar-gutter:stable;-webkit-overflow-scrolling:touch;touch-action:pan-x pan-y;padding-bottom:4px}.pw-person-button{flex:0 0 auto;min-width:max-content;min-height:42px;scroll-snap-align:start}.pw-roster-wrap{max-height:min(65svh,540px)}.pw-open-series{min-height:38px}}
`;
  document.head.appendChild(style);

  const tabs = document.getElementById('dash-main-tabs');
  const castaButton = tabs?.querySelector('[data-tab="tab-casta"]');
  const castaPanel = document.getElementById('tab-casta');
  if (!tabs || !castaButton || !castaPanel) return;

  castaButton.insertAdjacentHTML('beforebegin', '<button class="tab-btn" type="button" data-tab="tab-political-wealth">Patrimonio político · DDJJ</button>');
  castaPanel.insertAdjacentHTML('beforebegin', `
  <section id="tab-political-wealth" class="tab-panel">
    <div class="epica-shell wealth">
      <header class="epica-hero">
        <div><span class="epica-eyebrow">◈ Poder económico · DJPI bajo lupa</span><h2>Patrimonio político: la película desde 2017</h2><p>Bienes declarados, inflación, dólar y composición bajo la misma regla. Los huecos quedan visibles y las explicaciones contables no se confunden con conclusiones penales.</p></div>
        <aside class="epica-status-card"><div><strong><span id="pwUniverseHeroCount">—</span> cargos activos registrados</strong><small><span id="pwDeepHeroCount">—</span> trayectorias tienen identidad y serie auditadas. La expansión restante está freezada para profundizar la calidad de lectura sin borrar la cola ni convertir N/D en cero.</small></div><div class="epica-status-row"><span class="epica-chip observed">padrón oficial</span><span class="epica-chip proxy">OA 2017–2024</span><span class="epica-chip open">profundidad primero</span></div></aside>
      </header>

      <div class="epica-toolbar" role="group" aria-label="Vista de patrimonio político"><span>Explorar</span><button class="epica-toggle active" type="button" data-pw-view="coverage" aria-pressed="true">Todos los cargos (789)</button><button id="pwPersonViewButton" class="epica-toggle" type="button" data-pw-view="person" aria-pressed="false">Trayectorias auditadas</button><button class="epica-toggle" type="button" data-pw-view="method" aria-pressed="false">Método y límites</button></div>

      <div id="pwLoading" class="pw-loading">Cargando serie auditada 2017–2025…</div>

      <div class="pw-surface" data-pw-surface="person" hidden>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Elegí una trayectoria auditada</h3><p id="pwDeepScopeCopy">Los casos con identidad confirmada tienen importes persona-año normalizados; no representan el universo completo. Las demás personas están en “Todos los cargos” con su estado de búsqueda, sin inventar una serie.</p></div><span id="pwPersonScopeBadge" class="epica-chip observed">cargando</span></div><div id="pwPersonControls" class="pw-controls" role="group" aria-label="Funcionario o funcionaria con trayectoria auditada"></div></section>

        <div class="pw-kpi-grid" aria-live="polite">
          <article class="pw-kpi"><small id="pwStartLabel">Primer dato</small><b id="pwStartValue">—</b><span id="pwStartNote">—</span></article>
          <article id="pwEndKpi" class="pw-kpi"><small id="pwEndLabel">Último dato</small><b id="pwEndValue">—</b><span id="pwEndNote">—</span></article>
          <article class="pw-kpi"><small>Cambio nominal</small><b id="pwNominalChange">—</b><span id="pwNominalNote">—</span></article>
          <article class="pw-kpi expected"><small>Cambio real IPC</small><b id="pwRealChange">—</b><span id="pwRealNote">CAGR — · pesos de 2025</span></article>
          <article class="pw-kpi partial"><small>Cambio en USD A3500</small><b id="pwUsdChange">—</b><span id="pwUsdNote">CAGR — · equivalencia de cierre</span></article>
        </div>

        <div class="epica-grid">
          <section class="epica-panel"><div class="epica-panel-head"><div><h3 id="pwTrendTitle">Bienes declarados: tres lentes</h3><p id="pwTrendSubtitle">Índice base=100 en el primer año disponible.</p></div><span class="epica-chip proxy">2017–2025</span></div><div id="politicalWealthTrendChart" class="epica-chart tall" role="img" aria-label="Evolución nominal, real y equivalente al dólar A3500"></div></section>
          <aside class="epica-panel"><div class="epica-panel-head"><div><h3>Qué permite decir</h3><p>Período, moneda y fuente antes que un porcentaje aislado.</p></div></div><div id="pwPersonReading" class="epica-answer-grid"></div><div id="pwPersonCallout" class="pw-callout" style="margin-top:9px"></div></aside>
        </div>

        <section id="pwCaseAudit" class="epica-panel pw-case-audit" hidden><div class="epica-panel-head"><div><h3 id="pwCaseTitle">Lectura profunda</h3><p id="pwCaseQuestion">¿Qué explica el salto declarado y qué documentación permite comprobarlo?</p></div><span id="pwCaseChip" class="epica-chip open">análisis documental · no conclusión penal</span></div><div class="pw-case-lead"><div class="pw-case-verdict"><strong>Respuesta corta</strong><span id="pwCaseVerdict">La composición contable ubica el aumento, pero no reemplaza la trazabilidad documental.</span></div><div class="pw-case-source"><b>Capas de evidencia</b><span id="pwCaseSource">Se distinguen datos oficiales, copias respaldadas y cifras provisionales.</span></div></div><div class="pw-kpi-grid"><article class="pw-kpi review"><small id="pwCaseGrossLabel">Aumento bienes</small><b id="pwCaseGrossChange">—</b><span>stock bruto, no rendimiento de cartera</span></article><article class="pw-kpi expected"><small>Valuación / aumento</small><b id="pwCaseRevaluationShare">—</b><span>puede superar 100% si otros bienes bajan</span></article><article class="pw-kpi review"><small>Inmueble vs. IPC</small><b id="pwCasePropertyVsIpc">—</b><span>variación del último período</span></article><article class="pw-kpi partial"><small>Brecha vs. IPC simple</small><b id="pwCaseIpcGap">—</b><span>requiere base fiscal y cálculo</span></article><article class="pw-kpi frozen"><small>IPC simple explica</small><b id="pwCaseIpcShare">—</b><span>del salto del inmueble</span></article></div><div class="pw-table-wrap" style="margin-top:10px"><table class="pw-table"><thead><tr><th>Período</th><th>Fuente</th><th>Δ bienes</th><th>Diferencia valuación</th><th>% del aumento</th><th>Δ inmueble</th><th>IPC</th><th>Lectura</th></tr></thead><tbody id="pwCaseBridgeBody"></tbody></table></div><div id="pwCaseReading" class="epica-answer-grid" style="margin-top:10px"></div><div id="pwCaseSourceAlert" class="pw-callout" style="margin-top:10px"></div></section>

        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Qué habría pasado si el capital inicial se invertía?</h3><p id="pwBenchmarkSubtitle">Retornos totales en USD sobre la misma ventana de la persona.</p></div><span class="epica-chip proxy">contrafactual, no explicación</span></div><div id="pwBenchmarkCards" class="pw-benchmark-grid"></div><div class="epica-grid equal" style="margin-top:10px"><div id="politicalWealthBenchmarkChart" class="epica-chart" role="img" aria-label="CAGR del patrimonio en dólares frente a tres benchmarks de inversión"></div><div><div id="pwBenchmarkReading" class="epica-answer-grid"></div><div id="pwBenchmarkCallout" class="pw-callout" style="margin-top:9px"></div></div></div></section>

        <div class="epica-grid equal">
          <section class="epica-panel"><div class="epica-panel-head"><div><h3 id="pwCompositionTitle">Composición del último año detallado</h3><p>Bienes de cierre agrupados con una regla reproducible.</p></div><span id="pwCompositionBadge" class="epica-chip observed">2022–2024</span></div><div id="politicalWealthCompositionChart" class="epica-chart" role="img" aria-label="Composición de los bienes declarados"></div><p class="pw-data-note">Las categorías analíticas suman el total de bienes informado en la DJPI seleccionada.</p></section>
          <section class="epica-panel"><div class="epica-panel-head"><div><h3>Conciliación anual exploratoria</h3><p id="pwReconciliationSubtitle">Última DJPI anual o de baja con campos disponibles.</p></div><span class="epica-chip proxy">no es una pericia</span></div><div id="pwReconciliation" class="epica-answer-grid"></div><div class="pw-callout" style="margin-top:9px"><strong>El residual no implica irregularidad.</strong> Mide lo que esta identidad simple no reconcilia con los campos publicados; puede reflejar perímetros, valuaciones, signos o datos de origen.</div></section>
        </div>
      </div>

      <div class="pw-surface" data-pw-surface="coverage">
        <div class="pw-kpi-grid"><article class="pw-kpi"><small>Cargos activos · capas 1–2</small><b id="pwActiveCount">—</b><span>Nación + gobernaciones + tanda subnacional</span></article><article class="pw-kpi expected"><small>Presentación de Cámara</small><b id="pwCurrentFilingCount">—</b><span>localizada nominalmente en listados 2025/2026</span></article><article class="pw-kpi"><small>Cruce nominal OA único</small><b id="pwOaUniqueCount">—</b><span>candidato de historial · 2017–2024</span></article><article class="pw-kpi partial"><small>Trayectoria auditada</small><b id="pwCuratedActiveCount">—</b><span>personas activas ya integradas al análisis</span></article><article class="pw-kpi review"><small>Bancas prov. nominales</small><b id="pwProvincialIndexed">—</b><span>sobre 1.199 al sumar las 24 fichas DNE</span></article></div>
        <div id="pwResearchQueueStatus" class="pw-callout" style="margin:10px 0"></div>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Quiénes están en actividad?</h3><p>Un padrón buscable separa cargo vigente, presentación del régimen actual y coincidencia histórica en OA.</p></div><span class="epica-chip observed">corte 02/09/2026</span></div><div id="pwRosterScope" class="pw-callout"></div><div class="pw-roster-tools"><label>Buscar persona, cargo o distrito<input id="pwRosterSearch" type="search" placeholder="Ej.: Caputo, Córdoba, Senado…"></label><label>Bloque institucional<select id="pwRosterLevel"><option value="all">Todos</option><option value="Diputados nacionales">Diputados nacionales</option><option value="Senado nacional">Senado nacional</option><option value="Conducción superior PEN">Conducción superior PEN</option><option value="Gobernaciones">Gobernaciones</option><option value="Legislaturas provinciales">Legislaturas provinciales</option></select></label><label>Estado de datos<select id="pwRosterStatus"><option value="all">Todos</option><option value="filing">Presentación localizada</option><option value="pending">Ruta o verificación pendiente</option><option value="oa">Coincidencia OA única</option><option value="series">Trayectoria auditada</option><option value="frozen">Investigación freezada</option></select></label></div><div class="pw-scope-line"><b id="pwRosterVisibleCount">—</b><span>N/D significa no localizado en las fuentes respaldadas; no equivale a incumplimiento ni patrimonio cero.</span></div><div class="pw-table-wrap pw-roster-wrap"><table class="pw-table"><thead><tr><th>Persona</th><th>Cargo activo</th><th>Jurisdicción</th><th>Partido / bloque</th><th>DDJJ del cargo actual</th><th>Cruce OA 2017–2024</th><th>Trayectoria</th></tr></thead><tbody id="pwActiveRosterBody"></tbody></table></div></section>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Mapa de avance subnacional</h3><p>Las 24 fichas DNE cuantifican el universo; la columna nominal muestra qué nóminas oficiales ya están incorporadas.</p></div><span class="epica-chip proxy">24 jurisdicciones</span></div><div class="pw-table-wrap"><table class="pw-table"><thead><tr><th>Jurisdicción</th><th>Sistema</th><th>Bancas DNE</th><th>Nómina incorporada</th><th>Intendencias DNE</th><th>Estado</th></tr></thead><tbody id="pwProvincialCoverageBody"></tbody></table></div><p class="pw-data-note">La introducción del informe declara 1.201 bancas; las 24 fichas detalladas suman 1.199. CABA no tiene intendencias en este relevamiento.</p></section>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Trayectorias ya auditadas</h3><p>Este subgrupo sí tiene importes, deflactores y controles persona-año. Los faltantes no se interpolan.</p></div><span id="pwDeepCoverageBadge" class="epica-chip proxy">casos auditados</span></div><div class="pw-table-wrap"><table class="pw-table"><thead><tr><th>Persona</th><th>Ventana observada</th><th>Años oficiales</th><th>Huecos 2017–2024</th><th>2025</th><th>Δ real*</th></tr></thead><tbody id="pwCoverageBody"></tbody></table></div><p class="pw-data-note">* Entre el primer y el último valor comparable de cada persona; para Máximo, Javier y Karina el extremo 2025 es provisional.</p></section>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>¿Se puede comparar por partido?</h3><p>La estructura queda preparada, pero la estadística todavía no supera el gate metodológico.</p></div><span class="epica-chip open">sin ranking</span></div><div class="epica-answer-grid"><div class="epica-answer good"><b>Unidad correcta</b><p>Primero se calculan cambios por persona con igual tipo de declaración y ventana comparable; después se resume la distribución.</p></div><div class="epica-answer caution"><b>Afiliación temporal</b><p>Partido, bloque y coalición deben registrarse para la fecha de cada DJPI. La etiqueta actual no se proyecta hacia atrás.</p></div><div class="epica-answer caution"><b>Cohorte homogénea</b><p id="pwPartyCohortNote">Las trayectorias tienen huecos y ventanas distintas; todavía no permiten atribuir diferencias a una agrupación.</p></div><div class="epica-answer open"><b>Qué falta</b><p>Más personas por espacio, misma ventana, mismo perímetro y consolidado 2025 antes de calcular medianas.</p></div></div></section>
      </div>

      <div class="pw-surface" data-pw-surface="method" hidden>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Qué significa “cubrir a quienes están en actividad”</h3><p>La cobertura se publica por capas para no confundir un cargo identificado con una trayectoria patrimonial verificada.</p></div><span class="epica-chip proxy">789 cargos · capas 1–2</span></div><div class="pw-quality-grid"><div><b>Cargo vigente</b><span>Nómina oficial al 01/09/2026: Nación, gobernaciones y 423 bancas de Buenos Aires, CABA, Córdoba, Misiones, Río Negro y Santa Fe.</span></div><div><b>Presentación localizada</b><span>Indica aparición nominal en el listado de la Cámara; una ruta provincial publicada todavía puede estar pendiente de cruce.</span></div><div><b>Cruce OA candidato</b><span>La coincidencia nominal única abre una auditoría; identidad y trayectoria requieren cotejar CUIT, organismo y cargo.</span></div><div><b>Expansión freezada</b><span>491 casos conservan evidencia, estado y próxima acción, pero no se amplían mientras se prioriza profundidad analítica.</span></div><div><b>Discrepancia DNE</b><span>La introducción informa 1.201 bancas provinciales; la suma de las 24 fichas da 1.199. Se preservan ambos valores.</span></div></div></section>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Cómo se construyó la serie</h3><p>Fuente cruda respaldada, selección determinística y comparadores oficiales.</p></div><span class="epica-chip observed">reproducible</span></div><div class="pw-flow"><div><small>Fuente</small><b>ZIP Justicia 2012–2024</b><p>Se usan sólo declaraciones de 2017 a 2024.</p></div><div><small>Persona-año</small><b>Anual &gt; Baja &gt; Inicial</b><p>Luego mayor rectificativa y dj_id.</p></div><div><small>Total</small><b>Bienes de cierre</b><p>En una Inicial se toma el valor de inicio.</p></div><div><small>Comparadores</small><b>IPC + A3500</b><p>INDEC y BCRA al cierre de cada año.</p></div><div><small>Huecos</small><b>N/D visible</b><p>Sin interpolación ni equivalencia con cero.</p></div></div></section>
        <div class="epica-grid equal"><section class="epica-panel"><div class="epica-panel-head"><div><h3>Base 2017: qué dice y qué no</h3><p>La fecha es relevante, pero no reemplaza toda la regla de valuación.</p></div></div><div class="pw-callout"><strong>La referencia al 31/12/2017 funciona como piso fiscal transitorio para inmuebles dentro del art. 22 de la Ley 23.966.</strong> No significa que todos los bienes de todas las DJPI sean simplemente “valor 2017 × IPC”.</div><div class="pw-quality-grid" style="margin-top:9px"><div><b>Bienes totales</b><span>Incluyen categorías con reglas distintas.</span></div><div><b>Valor fiscal</b><span>Puede diferir del valor de mercado.</span></div><div><b>Ruta de carga</b><span>La DJPI puede migrar datos fiscales o admitir carga manual.</span></div></div></section><section class="epica-panel"><div class="epica-panel-head"><div><h3>Conciliación neutral</h3><p>Una pregunta abierta, no una hipótesis penal.</p></div></div><div class="epica-formula"><code>Residual = Δ patrimonio neto − (valuación + ingresos + herencias + deducciones sin erogación − gastos)</code></div><div class="pw-callout" style="margin-top:10px"><strong>Un residual alto abre una revisión documental.</strong> No identifica por sí solo ingresos omitidos, delito o corrupción; primero hay que verificar signos, perímetros y campos de origen.</div></section></div>
        <section class="epica-panel"><div class="epica-panel-head"><div><h3>Controles de calidad aplicados</h3><p>Lo que sostiene y limita la comparación.</p></div></div><div class="pw-quality-grid"><div><b id="pwQualityPositions">— posiciones</b><span>Una fila por persona y año, incluidos N/D.</span></div><div><b id="pwQualityReconciliations">— conciliaciones</b><span>Anuales o de baja; una fila malformada queda marcada.</span></div><div><b id="pwQualityComposition">— agregados</b><span>Composición 2022–2024 que reconcilia con cada total disponible.</span></div><div><b id="pwQualityBenchmarks">— contrafactuales</b><span>Tres estrategias cuando la ventana tiene al menos dos años.</span></div><div><b>2025 separado</b><span>Tres valores publicados, sin mezclar con el consolidado.</span></div><div><b>Deuda controlada</b><span>Bienes brutos y patrimonio neto no se intercambian; si resumen y detalle no concilian, el residual se suspende.</span></div><div><b>Valuación ≠ absolución</b><span>Explica una partida contable sólo cuando sus insumos son trazables; no prueba licitud ni corrupción.</span></div><div><b>FX como lente</b><span>A3500 es equivalencia contable, no precio de cada activo.</span></div><div><b>Retorno total</b><span>Cupones y distribuciones reinvertidos cuando corresponde.</span></div><div><b>Sin apalancamiento</b><span>El escenario no supone deuda ni aportes posteriores.</span></div></div></section>
      </div>

      <section class="sources-box"><h3>Fuentes, respaldo y descargas</h3><div class="source-links"><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politicians_roster_2026-09-01.csv">⬇ CSV · padrón activo</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politicians_coverage_2026-09-01.json">⬇ JSON · cobertura activa</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/provincial_coverage_matrix_2026-09-01.csv">⬇ CSV · avance provincial</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/person_series_2017_2025.csv">⬇ CSV · serie 2017–2025</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/cohort_coverage_2017_2025.csv">⬇ CSV · cobertura profunda</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/macro_deflators_2017_2025.csv">⬇ CSV · IPC y A3500</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/benchmark_annual_returns_2017_2025.csv">⬇ CSV · retornos benchmark</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/person_investment_benchmarks_2017_2025.csv">⬇ CSV · contrafactuales</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/asset_composition_2022_2024.csv">⬇ CSV · composición</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/annual_reconciliation_2017_2024.csv">⬇ CSV · conciliación</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/asset_persistence_audit.csv">⬇ CSV · persistencia de activos</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/viral_claim_audit.csv">⬇ CSV · auditoría de afirmaciones</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/dashboard_data_2017_2025.json">⬇ JSON · datos del tab</a><a class="download-link" download href="research/political_wealth_2026-09-01/source_registry.csv">⬇ CSV · registro de fuentes</a><a class="download-link" download href="research/political_wealth_2026-09-01/source_manifest.csv">⬇ CSV · SHA-256</a><a class="source-link" target="_blank" rel="noopener" href="https://www.hcdn.gob.ar/diputados/">🏛️ Diputados · nómina vigente</a><a class="source-link" target="_blank" rel="noopener" href="https://www.senado.gob.ar/senadores/listados/listaSenadoRes">🏛️ Senado · nómina vigente</a><a class="source-link" target="_blank" rel="noopener" href="https://cfi.org.ar/quienes_somos">🗺️ CFI · gobernaciones</a><a class="source-link" target="_blank" rel="noopener" href="https://www.argentina.gob.ar/interior/observatorioelectoral/informes-electorales/relevamientos-electorales-2026">🧭 DNE · poder provincial</a><a class="source-link" target="_blank" rel="noopener" href="https://www.hcdiputados-ba.gov.ar/index.php?page=diputados&amp;search=seccionBloques">🏛️ PBA · Diputados vigentes</a><a class="source-link" target="_blank" rel="noopener" href="https://senado-ba.gov.ar/Senadores.aspx">🏛️ PBA · Senado vigente</a><a class="source-link" target="_blank" rel="noopener" href="https://www.legislatura.gob.ar/seccion/composicion-actual.html">🏛️ CABA · composición actual</a><a class="source-link" target="_blank" rel="noopener" href="https://www.legislatura.gob.ar/seccion/listado-diputados-djpi.html">📄 CABA · DJPI</a><a class="source-link" target="_blank" rel="noopener" href="https://legislaturacba.gob.ar/composicion-de-la-camara/">🏛️ Córdoba · composición</a><a class="source-link" target="_blank" rel="noopener" href="https://legislaturacba.gob.ar/declaraciones-juradas/">📄 Córdoba · DDJJ</a><a class="source-link" target="_blank" rel="noopener" href="https://diputadossantafe.gov.ar/web/camara/diputados">🏛️ Santa Fe · Diputados</a><a class="source-link" target="_blank" rel="noopener" href="https://www.senadosantafe.gob.ar/">🏛️ Santa Fe · Senado</a><a class="source-link" target="_blank" rel="noopener" href="https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales">🗃️ Justicia · dataset oficial</a><a class="source-link" target="_blank" rel="noopener" href="https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31">📈 INDEC · IPC</a><a class="source-link" target="_blank" rel="noopener" href="https://www.bcra.gob.ar/apis-banco-central/">💱 BCRA · API A3500</a><a class="source-link" target="_blank" rel="noopener" href="https://fred.stlouisfed.org/series/GS3M">🛡️ Fed/FRED · Treasury 3 meses</a><a class="source-link" target="_blank" rel="noopener" href="https://personal1.vanguard.com/pub/Pdf/p502.pdf">⚖️ Vanguard · Balanced 60/40</a><a class="source-link" target="_blank" rel="noopener" href="https://www.msci.com/documents/10199/a71b65b5-d0ea-4b5c-a709-24b1213bc3c5">🌐 MSCI · ACWI net USD</a></div><div class="sources-note"><b>Corte:</b> 01/09/2026. <b>Padrón:</b> 789 cargos: 366 de Nación/gobernaciones y 423 bancas provinciales nominalizadas. Las copias crudas oficiales y el PDF DNE quedan en el repo de investigación y se excluyen del bundle liviano de Railway. <b>Alcance:</b> una coincidencia de nombre en OA es candidata, no identidad confirmada; las rutas provinciales de DDJJ no equivalen a una presentación individual. <b>2025:</b> Máximo Kirchner y Karina Milei permanecen provisionales hasta respaldar sus PDF individuales OA.</div></section>
    </div>
  </section>`);

  let payload = null;
  let rosterPayload = null;
  let researchSummary = null;
  let researchQueueById = new Map();
  let selectedPerson = 'maximo';
  const plotConfig = {displayModeBar:false,responsive:true,scrollZoom:false,doubleClick:false};
  const byId = id => document.getElementById(id);
  const num = value => value === '' || value == null ? null : Number(value);
  const pct = value => {
    const number = num(value);
    if (number == null) return 'N/D';
    return `${number > 0 ? '+' : ''}${number.toLocaleString('es-AR',{minimumFractionDigits:1,maximumFractionDigits:1})}%`;
  };
  const money = value => {
    const number = num(value);
    if (number == null) return 'N/D';
    const millions = number / 1e6;
    return `$ ${millions.toLocaleString('es-AR',{minimumFractionDigits:millions < 100 ? 1 : 0,maximumFractionDigits:1})} M`;
  };
  const sourceLabel = state => state === 'oficial_consolidado_oa' ? 'oficial consolidado' : state === 'publicado_pdf_oa_pendiente' ? 'provisional · PDF OA pendiente' : 'N/D';
  const esc = value => String(value ?? '').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const searchText = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();

  function personRows(id){ return payload.series.filter(row => row.persona_id === id); }
  function coverageRow(id){ return payload.coverage.find(row => row.persona_id === id); }

  function renderPerson(){
    if (!payload) return;
    const rows = personRows(selectedPerson);
    const observed = rows.filter(row => num(row.total_bienes_ars) != null);
    const first = observed[0];
    const last = observed[observed.length - 1];
    const coverage = coverageRow(selectedPerson);
    const person = payload.people.find(item => item.persona_id === selectedPerson);
    const historicFederal = person?.alcance_serie === 'historial_federal_previo_no_ddjj_provincial_actual';
    const historicPublic = person?.alcance_serie === 'historial_publico_oa_previo_no_equivale_ddjj_mandato_actual';
    const historicScopeLabel = historicFederal ? 'historial federal previo' : historicPublic ? 'historial OA previo' : '';
    const historicScopeWarning = historicFederal
      ? 'estos valores corresponden a un cargo público nacional previo; no representan una DDJJ del mandato provincial actual ni permiten inferir el patrimonio presente.'
      : historicPublic
        ? 'estos valores forman un historial público OA previo al corte; pueden incluir la Legislatura CABA o cargos nacionales anteriores y no equivalen por sí solos a la DDJJ del mandato actual.'
        : '';
    const metricFirst = observed.find(row => Number(row.anio) === Number(coverage.anio_base_metricas)) || first;
    const provisional = last.estado_fuente === 'publicado_pdf_oa_pendiente';

    byId('pwPersonScopeBadge').textContent = `${coverage.anios_oficiales_2017_2024}/8 años oficiales${historicScopeLabel ? ` · ${historicScopeLabel}` : ''}`;
    byId('pwStartLabel').textContent = `Base comparable · ${metricFirst.anio}`;
    byId('pwStartValue').textContent = money(metricFirst.total_bienes_ars);
    byId('pwStartNote').textContent = sourceLabel(metricFirst.estado_fuente);
    byId('pwEndLabel').textContent = `Último dato · ${last.anio}`;
    byId('pwEndValue').textContent = money(last.total_bienes_ars);
    byId('pwEndNote').textContent = sourceLabel(last.estado_fuente);
    byId('pwEndKpi').className = `pw-kpi ${provisional ? 'review' : 'expected'}`;
    byId('pwNominalChange').textContent = pct(coverage.cambio_nominal_primero_ultimo_pct);
    byId('pwNominalNote').textContent = `${metricFirst.anio}→${last.anio}`;
    byId('pwRealChange').textContent = pct(coverage.cambio_real_primero_ultimo_pct);
    byId('pwUsdChange').textContent = pct(coverage.cambio_usd_primero_ultimo_pct);
    byId('pwRealNote').textContent = `CAGR ${pct(coverage.cagr_real_anual_pct)} anual · pesos de 2025`;
    byId('pwUsdNote').textContent = `CAGR ${pct(coverage.cagr_usd_anual_pct)} anual · A3500`;
    byId('pwTrendTitle').textContent = `${person.persona}: bienes declarados bajo tres lentes`;
    byId('pwTrendSubtitle').textContent = `Base ${metricFirst.anio}=100 · huecos sin interpolar${provisional ? ' · 2025 provisional' : ''}${historicScopeLabel ? ' · no equivale a DDJJ actual' : ''}.`;
    const missing = coverage.anios_faltantes_2017_2024 === 'ninguno' ? 'Ninguno entre 2017 y 2024.' : coverage.anios_faltantes_2017_2024.replaceAll('|', ', ');
    byId('pwPersonReading').innerHTML = `
      <div class="epica-answer good"><b>Ventana observada</b><p>${first.anio}→${last.anio}; métricas comparables desde ${metricFirst.anio}; ${coverage.anios_oficiales_2017_2024} registros oficiales en 2017–2024.</p></div>
      <div class="epica-answer caution"><b>Huecos oficiales</b><p>${missing}</p></div>
      <div class="epica-answer ${provisional ? 'open' : 'good'}"><b>Último estado</b><p>${sourceLabel(last.estado_fuente)}.</p></div>`;
    byId('pwPersonCallout').innerHTML = `${historicScopeWarning ? `<strong>Alcance:</strong> ${historicScopeWarning}<br><br>` : ''}<strong>Lectura neutral:</strong> el cambio nominal fue ${pct(coverage.cambio_nominal_primero_ultimo_pct)}, pero pasa a ${pct(coverage.cambio_real_primero_ultimo_pct)} al descontar IPC y a ${pct(coverage.cambio_usd_primero_ultimo_pct)} como equivalente A3500. Son lentes contables; ninguno prueba por sí solo el origen del cambio.`;

    if (window.Plotly) {
      const x = rows.map(row => String(row.anio));
      const traces = [
        {name:'Nominal',field:'indice_nominal_base',color:'#a35e7b'},
        {name:'Real IPC',field:'indice_real_base',color:'#4f9980'},
        {name:'USD A3500',field:'indice_usd_base',color:'#c29336'}
      ].map(spec => ({type:'scatter',mode:'lines+markers',name:spec.name,x,y:rows.map(row=>num(row[spec.field])),connectgaps:false,line:{color:spec.color,width:3},marker:{size:7},hovertemplate:`<b>%{x}</b><br>${spec.name} %{y:.1f}<extra></extra>`}));
      const provisionalRows = rows.filter(row => row.estado_fuente === 'publicado_pdf_oa_pendiente');
      if (provisionalRows.length) traces.push({type:'scatter',mode:'markers',name:'2025 provisional',x:provisionalRows.map(row=>String(row.anio)),y:provisionalRows.map(row=>num(row.indice_nominal_base)),marker:{size:13,symbol:'diamond-open',color:'#a54768',line:{width:2}},hovertemplate:'<b>%{x}</b><br>valor publicado · PDF OA pendiente<extra></extra>'});
      const mobile = window.innerWidth <= 720;
      Plotly.react('politicalWealthTrendChart',traces,{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'#fff',font:{family:'Inter,system-ui,sans-serif',size:mobile?9:10,color:'#715e69'},margin:{l:mobile?48:60,r:18,t:45,b:48},legend:{orientation:'h',y:1.17},yaxis:{title:'Índice base=100',rangemode:'tozero',gridcolor:'#eee5ea',fixedrange:true},xaxis:{fixedrange:true,type:'category',categoryorder:'array',categoryarray:rows.map(row=>String(row.anio))},hovermode:'x unified'},plotConfig);
    }
    renderBenchmarks();
    renderComposition();
    renderReconciliation();
    renderCaseAudit();
  }

  function renderBenchmarks(){
    const rows = payload.benchmark_comparisons.filter(row => row.persona_id === selectedPerson);
    if (!rows.length) {
      byId('pwBenchmarkSubtitle').textContent = 'Se necesitan al menos dos años con patrimonio positivo para calcular un CAGR comparable.';
      byId('pwBenchmarkCards').innerHTML = '<div class="pw-chart-empty" style="grid-column:1/-1;min-height:120px">Un solo año observado: el contrafactual queda N/D hasta sumar otro ejercicio.</div>';
      byId('pwBenchmarkReading').innerHTML = '<div class="epica-answer open"><b>Ventana insuficiente</b><p>No se anualiza un cambio de un único punto.</p></div>';
      byId('pwBenchmarkCallout').innerHTML = '<strong>N/D no es cero.</strong> El benchmark se habilitará cuando exista un segundo año comparable.';
      if (window.Plotly) Plotly.purge('politicalWealthBenchmarkChart');
      byId('politicalWealthBenchmarkChart').innerHTML = '<div class="pw-chart-empty">Sin ventana temporal comparable.</div>';
      return;
    }
    const riskMeta = {
      poco:{label:'Poco riesgo',kind:'low',description:'T-bills 3 meses · rollover proxy'},
      medio:{label:'Riesgo medio',kind:'medium',description:'Vanguard Balanced Index · 60/40'},
      mucho:{label:'Mucho riesgo',kind:'high',description:'MSCI ACWI · acciones globales'}
    };
    const observedUsd = num(rows[0].patrimonio_cagr_usd_a3500_pct);
    const observedReal = num(rows[0].patrimonio_cagr_real_pct);
    byId('pwBenchmarkSubtitle').textContent = `${rows[0].anio_inicio}→${rows[0].anio_fin} · retorno total USD · CAGR patrimonio USD A3500 ${pct(observedUsd)}.`;
    byId('pwBenchmarkCards').innerHTML = rows.map(row=>{const meta=riskMeta[row.riesgo];return `<article class="pw-benchmark-card ${meta.kind}"><small>${meta.label}</small><b>${pct(row.benchmark_cagr_usd_pct)} anual</b><p>${meta.description}<br>Acumulado: ${pct(row.benchmark_retorno_acumulado_usd_pct)} · brecha patrimonio−benchmark: ${pct(row.brecha_cagr_vs_patrimonio_usd_pp)} pp/año.</p></article>`;}).join('');
    byId('pwBenchmarkReading').innerHTML = `<div class="epica-answer good"><b>Patrimonio real IPC</b><p>CAGR ${pct(observedReal)} anual.</p></div><div class="epica-answer caution"><b>Patrimonio en USD</b><p>CAGR ${pct(observedUsd)} anual al A3500.</p></div><div class="epica-answer open"><b>Capital contrafactual</b><p>${money(rows[0].capital_final_contrafactual_ars_a3500)} a ${money(rows[2].capital_final_contrafactual_ars_a3500)}, según riesgo.</p></div>`;
    const caseWarning = selectedPerson === 'karina'
      ? '<br><br><strong>En este caso no debe leerse como rendimiento.</strong> El extremo 2025 es provisional y el salto está dominado por una diferencia de valuación del inmueble, no por una cartera que haya ganado esa tasa.'
      : selectedPerson === 'javier'
        ? '<br><br><strong>En este caso no debe leerse como rendimiento.</strong> El extremo 2025 es provisional y el puente profundo separa valuación, ingresos, gastos y variación real; superar un benchmark no prueba que una cartera haya ganado esa tasa.'
        : '';
    byId('pwBenchmarkCallout').innerHTML = `<strong>No describe la cartera real.</strong> Supone que todo el patrimonio inicial se convirtió al A3500, se invirtió sin aportes ni retiros, reinvirtió cupones/dividendos y volvió a pesos al cierre. Es antes de impuestos, sin apalancamiento y sin costos de acceso desde Argentina.${caseWarning}`;
    if (!window.Plotly) return;
    const labels = ['Patrimonio DDJJ',...rows.map(row=>riskMeta[row.riesgo].label)];
    const values = [observedUsd,...rows.map(row=>num(row.benchmark_cagr_usd_pct))];
    const colors = ['#715e69','#6eb092','#d2aa58','#a35e7b'];
    Plotly.react('politicalWealthBenchmarkChart',[{type:'bar',orientation:'h',y:labels,x:values,marker:{color:colors},text:values.map(value=>pct(value)),textposition:'auto',hovertemplate:'<b>%{y}</b><br>CAGR %{x:.2f}%<extra></extra>'}],{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'#fff',font:{family:'Inter,system-ui,sans-serif',size:9,color:'#715e69'},margin:{l:105,r:18,t:18,b:45},xaxis:{title:'CAGR anual en USD (%)',zeroline:true,zerolinecolor:'#bbaeb6',gridcolor:'#eee5ea',fixedrange:true},yaxis:{fixedrange:true,autorange:'reversed'},showlegend:false},plotConfig);
  }

  function renderComposition(){
    const target = byId('politicalWealthCompositionChart');
    const rows = payload.composition.filter(row => row.persona_id === selectedPerson);
    if (!rows.length) {
      if (window.Plotly) Plotly.purge(target);
      target.innerHTML = '<div class="pw-chart-empty">No hay detalle abierto de bienes para esta trayectoria en 2022–2024. El total histórico se conserva, pero no se inventa su composición.</div>';
      byId('pwCompositionBadge').textContent = 'detalle N/D';
      return;
    }
    const year = Math.max(...rows.map(row => Number(row.anio)));
    const current = rows.filter(row => Number(row.anio) === year);
    byId('pwCompositionBadge').textContent = String(year);
    byId('pwCompositionTitle').textContent = `Composición ${year}`;
    if (!window.Plotly) return;
    Plotly.react(target,[{type:'pie',hole:.56,labels:current.map(row=>row.categoria),values:current.map(row=>num(row.importe_ars)),textinfo:'percent',hovertemplate:'<b>%{label}</b><br>$ %{value:,.0f}<br>%{percent}<extra></extra>',marker:{colors:['#7d536d','#4f9980','#d2aa58','#9c7eb4','#6d92ad','#cc7b79','#97a278']}}],{paper_bgcolor:'rgba(0,0,0,0)',font:{family:'Inter,system-ui,sans-serif',size:9,color:'#715e69'},margin:{l:10,r:10,t:16,b:30},legend:{orientation:'h',y:-.08}},plotConfig);
  }

  function renderCaseAudit(){
    const section = byId('pwCaseAudit');
    const audit = payload?.case_audits?.[selectedPerson];
    const visible = Boolean(audit);
    section.hidden = !visible;
    if (!visible) return;
    const latest = audit.periodos.find(row=>row.periodo === '2024-2025') || audit.periodos[audit.periodos.length-1];
    const reading = audit.lectura_epistemica;
    const shortList = values => values.map(value=>`• ${esc(value)}`).join('<br>');
    const endYear = String(latest.periodo).split('-').at(-1);
    byId('pwCaseTitle').textContent = `Lectura profunda · ${audit.metadata.persona}`;
    byId('pwCaseQuestion').textContent = audit.metadata.pregunta;
    byId('pwCaseChip').textContent = audit.metadata.etiqueta || 'anomalía documental · no conclusión penal';
    byId('pwCaseSource').textContent = audit.metadata.alcance;
    byId('pwCaseVerdict').textContent = reading.conclusion;
    byId('pwCaseGrossLabel').textContent = `Aumento bienes · ${endYear}`;
    byId('pwCaseGrossChange').textContent = pct(latest.aumento_bienes_pct);
    byId('pwCaseRevaluationShare').textContent = pct(latest.valuacion_sobre_aumento_bienes_pct);
    byId('pwCasePropertyVsIpc').textContent = `${pct(latest.aumento_inmueble_pct)} / ${pct(latest.ipc_periodo_pct)}`;
    byId('pwCaseIpcGap').textContent = money(latest.brecha_inmueble_vs_ipc_simple_ars);
    byId('pwCaseIpcShare').textContent = pct(latest.aumento_inmueble_explicado_por_ipc_simple_pct);
    byId('pwCaseBridgeBody').innerHTML = audit.periodos.map(row=>{
      const primary = row.estado_fuente === 'oficial_consolidado_oa';
      const interpretation = row.lectura || (row.periodo === '2023-2024'
        ? 'El inmueble acompaña el IPC; la valuación explica sólo una parte del aumento bruto.'
        : 'La valuación supera el aumento bruto y el IPC anual sólo explica una fracción del salto del inmueble.');
      return `<tr><td><b>${esc(row.periodo)}</b></td><td><span class="pw-status ${primary?'expected':'review'}">${primary?'oficial':'provisional'}</span></td><td class="num">${money(row.aumento_bienes_ars)}</td><td class="num">${money(row.diferencia_valuacion_total_ars)}</td><td class="num">${pct(row.valuacion_sobre_aumento_bienes_pct)}</td><td class="num">${pct(row.aumento_inmueble_pct)}</td><td class="num">${pct(row.ipc_periodo_pct)}</td><td>${esc(interpretation)}</td></tr>`;
    }).join('');
    byId('pwCaseReading').innerHTML = `
      <div class="epica-answer good"><b>Qué sí está documentado</b><p>${shortList(reading.documentado)}</p></div>
      <div class="epica-answer caution"><b>Qué podría explicarlo</b><p>${shortList(reading.compatible_pero_no_probado)}</p></div>
      <div class="epica-answer open"><b>Qué todavía no está probado</b><p>${shortList(reading.no_documentado)}</p></div>
      <div class="epica-answer caution"><b>Qué cerraría la pregunta</b><p>${shortList(reading.evidencia_para_cerrar)}</p></div>`;
    const fallbackAlert = selectedPerson === 'karina'
      ? 'El consolidado tiene una inconsistencia independiente en deudas: en 2023 el total resumen ($10,91 M) es diez veces la suma de sus cinco filas de detalle ($1,09 M), y el cierre 2024 tampoco coincide con la apertura 2025 publicada. El dato crudo se preserva, pero el residual automático queda suspendido.'
      : 'El dato crudo se preserva, pero no se interpreta como una pericia ni se atribuye a la persona.';
    byId('pwCaseSourceAlert').innerHTML = `<strong>Control de calidad de fuente.</strong> ${esc(audit.alerta_fuente || fallbackAlert)}`;
  }

  function renderReconciliation(){
    const rows = payload.reconciliation.filter(row => row.persona_id === selectedPerson);
    const target = byId('pwReconciliation');
    const override = payload?.case_audits?.[selectedPerson]?.reconciliation_override;
    if (override) {
      byId('pwReconciliationSubtitle').textContent = `${override.periodo} · puente corregido contra el formulario individual`;
      target.innerHTML = `<div class="epica-answer good"><b>Δ patrimonio neto</b><p>${money(override.delta_patrimonio_neto_ars)}</p></div><div class="epica-answer caution"><b>Componentes disponibles</b><p>${money(override.componentes_disponibles_ars)}</p></div><div class="epica-answer good"><b>Residual ajustado</b><p>${money(override.residual_ajustado_ars)}</p></div><div class="epica-answer open"><b>Lectura</b><p>${esc(override.lectura)}</p></div>`;
      return;
    }
    if (selectedPerson === 'karina' && payload?.case_audits?.karina) {
      byId('pwReconciliationSubtitle').textContent = 'Control suspendido: los campos de deuda del consolidado no concilian entre resumen, detalle y apertura siguiente.';
      target.innerHTML = '<div class="epica-answer caution"><b>No calculable de forma robusta</b><p>Se conserva el dato crudo, pero no se presenta un residual automático hasta resolver la inconsistencia de origen.</p></div><div class="epica-answer good"><b>Puente alternativo</b><p>La auditoría profunda separa bienes brutos, valuación, inmueble e IPC sin usar ese total de deuda defectuoso.</p></div>';
      return;
    }
    if (!rows.length) {
      byId('pwReconciliationSubtitle').textContent = 'Sin DJPI anual o de baja calculable en la ventana.';
      target.innerHTML = '<div class="epica-answer open"><b>N/D</b><p>No se fuerza una identidad con datos insuficientes.</p></div>';
      return;
    }
    const row = rows[rows.length - 1];
    byId('pwReconciliationSubtitle').textContent = `${row.anio} · ${row.tipo_ddjj} · dj_id ${row.dj_id}`;
    if (row.estado_calculo !== 'calculable') {
      target.innerHTML = '<div class="epica-answer open"><b>Dato de origen malformado</b><p>La fila se conserva y queda fuera del cálculo; no se corrige por inferencia.</p></div>';
      return;
    }
    target.innerHTML = `<div class="epica-answer good"><b>Δ patrimonio neto</b><p>${money(row.delta_patrimonio_neto_ars)}</p></div><div class="epica-answer caution"><b>Componentes disponibles</b><p>${money(row.suma_componentes_ars)}</p></div><div class="epica-answer open"><b>Residual</b><p>${money(row.residual_ars)}</p></div>`;
  }

  function renderCoverage(){
    if (!payload || !rosterPayload) return;
    const summary = rosterPayload.summary;
    byId('pwActiveCount').textContent = Number(summary.cargos_activos).toLocaleString('es-AR');
    byId('pwCurrentFilingCount').textContent = Number(summary.presentaciones_camara_localizadas).toLocaleString('es-AR');
    byId('pwOaUniqueCount').textContent = Number(summary.personas_con_nombre_compatible_unico_oa_2017_2024).toLocaleString('es-AR');
    byId('pwCuratedActiveCount').textContent = Number(researchSummary?.trayectorias_auditadas_activas ?? summary.personas_con_serie_curada_tab).toLocaleString('es-AR');
    byId('pwProvincialIndexed').textContent = `${Number(summary.legisladores_provinciales_nominales).toLocaleString('es-AR')} / ${Number(summary.bancas_provinciales_suma_fichas_dne).toLocaleString('es-AR')}`;
    byId('pwUniverseHeroCount').textContent = Number(summary.cargos_activos).toLocaleString('es-AR');
    byId('pwRosterScope').innerHTML = `<strong>${esc(rosterPayload.scope.title)}.</strong> ${esc(rosterPayload.scope.included)}<br><b>Todavía fuera:</b> ${esc(rosterPayload.scope.not_yet_included)} ${esc(rosterPayload.scope.next_layer_reference)}`;
    byId('pwCoverageBody').innerHTML = payload.coverage.map(row => {
      const gaps = row.anios_faltantes_2017_2024 === 'ninguno' ? 'ninguno' : row.anios_faltantes_2017_2024.replaceAll('|', ', ');
      const state2025 = row.dato_2025 === 'provisional_publicado' ? '<span class="pw-status review">provisional</span>' : '<span class="pw-status missing">N/D</span>';
      return `<tr><td><b>${row.persona}</b></td><td>${row.primer_anio_con_dato}–${row.ultimo_anio_con_dato}</td><td class="num">${row.anios_oficiales_2017_2024}/8</td><td>${gaps}</td><td>${state2025}</td><td class="num">${pct(row.cambio_real_primero_ultimo_pct)}</td></tr>`;
    }).join('');
    byId('pwProvincialCoverageBody').innerHTML = (rosterPayload.provincial_coverage || []).map(row => {
      const indexed = Number(row.legisladores_nominales_incorporados);
      const total = Number(row.bancas_total_ficha_dne);
      const complete = indexed === total;
      const status = complete
        ? '<span class="pw-status expected">nómina incorporada</span>'
        : '<span class="pw-status review">pendiente nominal</span>';
      const municipalities = Number(row.intendencias_ficha_dne) || '—';
      return `<tr><td><b>${esc(row.jurisdiccion_corta)}</b></td><td>${esc(row.tipo_legislatura)}</td><td class="num">${total.toLocaleString('es-AR')}</td><td class="num">${indexed.toLocaleString('es-AR')} / ${total.toLocaleString('es-AR')}</td><td class="num">${typeof municipalities === 'number' ? municipalities.toLocaleString('es-AR') : municipalities}</td><td>${status}</td></tr>`;
    }).join('');
    renderActiveRoster();
  }

  function currentStatus(row){
    const state = row.estado_ddjj_cargo_actual;
    if (state.startsWith('presentacion_')) return ['expected','presentación localizada'];
    if (state.startsWith('sin_presentacion_')) return ['missing','sin localizar en el listado'];
    if (state === 'listado_ddjj_2025_publicado_sin_cruce_nominal') return ['partial','listado 2025 · cruce pendiente'];
    if (state === 'ruta_provincial_localizada_sin_cruce_nominal') return ['partial','ruta oficial · cruce pendiente'];
    if (state === 'ruta_provincial_por_relevar') return ['review','ruta provincial pendiente'];
    return ['partial','verificación 2025/2026 pendiente'];
  }

  function oaStatus(row){
    const state = row.oa_historial_2017_2024_estado;
    if (state === 'nombre_compatible_unico_en_oa') return ['expected',`${row.oa_cantidad_anios_2017_2024} año${Number(row.oa_cantidad_anios_2017_2024)===1?'':'s'} · candidato único`];
    if (state === 'coincidencia_multiple_revisar_homonimia') return ['review','homonimia por revisar'];
    return ['missing','sin nombre compatible'];
  }

  function researchStatus(row){
    const item = researchQueueById.get(row.persona_id);
    if (!item) return ['missing','estado pendiente',''];
    if (item.estado_investigacion === 'freezado') return ['frozen','freezado',item.motivo_estado_investigacion||'Expansión pausada; la evidencia reunida se conserva.'];
    const labels = {
      serie_curada:['expected','serie curada'],
      identidad_confirmada_cruce_oficial:['expected','identidad + serie auditadas'],
      preclasificacion_fuerte_misma_institucion:['partial','evidencia institucional'],
      preclasificacion_nombre_y_cuit_unicos:['partial','identidad a cotejar'],
      historial_oa_posible_cargo_nacional_previo:['review','posible antecedente nacional'],
      revision_manual_identidad:['review','identidad a revisar'],
      homonimia_oa_por_resolver:['review','homonimia'],
      sin_registro_oa_2017_2024:['missing','buscar otra fuente'],
      sin_registro_oa_2017_2024_identidad_desambiguada:['missing','OA descartada · buscar régimen actual']
    };
    const [kind,label] = labels[item.estado_busqueda_patrimonial] || ['missing','estado pendiente'];
    return [kind,label,item.siguiente_accion||''];
  }

  function renderActiveRoster(){
    if (!rosterPayload) return;
    const query = searchText(byId('pwRosterSearch')?.value);
    const level = byId('pwRosterLevel')?.value || 'all';
    const status = byId('pwRosterStatus')?.value || 'all';
    const rows = rosterPayload.rows.filter(row => {
      const haystack = searchText([row.persona,row.cargo,row.jurisdiccion,row.partido_o_alianza].join(' '));
      if (query && !haystack.includes(query)) return false;
      if (level !== 'all' && row.nivel_cargo !== level) return false;
      if (status === 'filing' && !row.estado_ddjj_cargo_actual.startsWith('presentacion_')) return false;
      if (status === 'pending' && row.estado_ddjj_cargo_actual.startsWith('presentacion_')) return false;
      if (status === 'oa' && row.oa_historial_2017_2024_estado !== 'nombre_compatible_unico_en_oa') return false;
      if (status === 'series' && !payload.people.some(person=>person.persona_id===row.persona_id || person.persona_id===row.serie_tab_id)) return false;
      if (status === 'frozen' && researchQueueById.get(row.persona_id)?.estado_investigacion !== 'freezado') return false;
      return true;
    });
    byId('pwRosterVisibleCount').textContent = `Mostrando ${rows.length.toLocaleString('es-AR')} de ${rosterPayload.rows.length.toLocaleString('es-AR')} cargos`;
    byId('pwActiveRosterBody').innerHTML = rows.map(row => {
      const [currentKind,currentLabel] = currentStatus(row);
      const [oaKind,oaLabel] = oaStatus(row);
      const [researchKind,researchLabel,researchDetail] = researchStatus(row);
      const deepSeriesId = row.serie_tab_id || (payload.people.some(person=>person.persona_id===row.persona_id) ? row.persona_id : '');
      const frozen = researchQueueById.get(row.persona_id)?.estado_investigacion === 'freezado';
      const action = deepSeriesId ? `<button class="pw-open-series" type="button" data-pw-open-series="${esc(deepSeriesId)}">Abrir análisis</button>` : frozen ? '<span class="pw-status frozen">freezado</span>' : '<span class="pw-status missing">en cola</span>';
      const detail = row.detalle_ddjj_cargo_actual ? ` title="${esc(row.detalle_ddjj_cargo_actual)}"` : '';
      const researchTitle = researchDetail ? ` title="${esc(researchDetail)}"` : '';
      return `<tr><td><b>${esc(row.persona)}</b></td><td>${esc(row.cargo)}</td><td>${esc(row.jurisdiccion)}</td><td>${esc(row.partido_o_alianza)}</td><td><span class="pw-status ${currentKind}"${detail}>${currentLabel}</span></td><td><span class="pw-status ${oaKind}">${oaLabel}</span></td><td><span class="pw-status ${researchKind}"${researchTitle}>${researchLabel}</span></td><td>${action}</td></tr>`;
    }).join('') || '<tr><td colspan="8">No hay coincidencias con estos filtros.</td></tr>';
  }

  function openSeries(id){
    if (!payload.people.some(person=>person.persona_id===id)) return;
    selectedPerson = id;
    document.querySelectorAll('[data-pw-person]').forEach(item=>{const active=item.dataset.pwPerson===id;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});
    setView('person');
    renderPerson();
    document.getElementById('tab-political-wealth')?.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function setView(view){
    document.querySelectorAll('[data-pw-surface]').forEach(surface => {surface.hidden = surface.dataset.pwSurface !== view;});
    document.querySelectorAll('[data-pw-view]').forEach(button => {const active=button.dataset.pwView===view;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));});
    if (view === 'person') window.setTimeout(renderPerson,40);
    if (view === 'coverage') renderCoverage();
  }

  function initialize(data, roster, research, queue=[], caseAudits=[]){
    for (const audit of caseAudits || []) {
      const id = audit?.metadata?.persona_id;
      if (id) data.case_audits = {...(data.case_audits||{}),[id]:audit};
    }
    payload = data;
    rosterPayload = roster;
    researchSummary = research;
    researchQueueById = new Map(queue.map(item=>[item.persona_id,item]));
    const rosterHeader = document.querySelector('#pwActiveRosterBody')?.closest('table')?.querySelector('thead tr');
    if (rosterHeader && rosterHeader.children.length === 7) rosterHeader.children[6].insertAdjacentHTML('beforebegin','<th>Investigación</th>');
    const sourceLinks = document.querySelector('#tab-political-wealth .source-links');
    if (sourceLinks && !sourceLinks.querySelector('[href*="karina_milei_revaluation_bridge_2024_2025.csv"]')) {
      sourceLinks.insertAdjacentHTML('afterbegin','<a class="download-link" download href="research/political_wealth_2026-09-01/derived/karina_milei_revaluation_bridge_2024_2025.csv">⬇ CSV · puente de revaluación · Karina</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/karina_milei_source_consistency_audit_2023_2025.csv">⬇ CSV · consistencia de fuente · Karina</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/karina_milei_revaluation_audit_2023_2025.json">⬇ JSON · lectura profunda · Karina</a>');
    }
    if (sourceLinks && !sourceLinks.querySelector('[href*="javier_milei_patrimonial_bridge_2023_2025.csv"]')) {
      sourceLinks.insertAdjacentHTML('afterbegin','<a class="download-link" download href="research/political_wealth_2026-09-01/derived/javier_milei_patrimonial_bridge_2023_2025.csv">⬇ CSV · puente patrimonial · Javier</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/javier_milei_revaluation_components_2025.csv">⬇ CSV · componentes de valuación · Javier</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/javier_milei_source_consistency_audit_2023_2025.csv">⬇ CSV · consistencia de fuente · Javier</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/javier_milei_revaluation_audit_2023_2025.json">⬇ JSON · lectura profunda · Javier</a>');
    }
    if (sourceLinks && !sourceLinks.querySelector('[href*="active_politician_research_queue_2026-09-01.csv"]')) {
      const verifiedBatchFiles = [
        {batch:1,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_1_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_1_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_1_2017_2024.csv'},
        {batch:2,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_2_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_2_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_2_2017_2024.csv'},
        {batch:3,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_3_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_3_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_3_2017_2024.csv'},
        {batch:4,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_4_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_4_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_4_2017_2024.csv'},
        {batch:5,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_5_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_5_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_5_2017_2024.csv'},
        {batch:6,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_6_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_6_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_6_2017_2024.csv'},
        {batch:7,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_7_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_7_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_7_2017_2024.csv'},
        {batch:8,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_8_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_8_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_8_2017_2024.csv'},
        {batch:9,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_9_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_9_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_9_2017_2024.csv'},
        {batch:10,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_10_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_10_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_10_2017_2024.csv'},
        {batch:11,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_11_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_11_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_11_2017_2024.csv'},
        {batch:12,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_12_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_12_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_12_2017_2024.csv'},
        {batch:13,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_13_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_13_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_13_2017_2024.csv'},
        {batch:14,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_14_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_14_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_14_2017_2024.csv'},
        {batch:15,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_15_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_15_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_15_2017_2024.csv'},
        {batch:17,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_17_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_17_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_17_2017_2024.csv'},
        {batch:18,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_18_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_18_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_18_2017_2024.csv'},
        {batch:19,audit:'research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_19_2026-09-01.csv',series:'research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_19_2017_2024.csv',benchmarks:'research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_19_2017_2024.csv'}
      ];
      const confirmedBatches = researchSummary?.identidades_confirmadas_por_iteracion || {};
      const batchDownloads = verifiedBatchFiles.filter(item=>Number(confirmedBatches[item.batch] || 0)>0).map(item=>`<a class="download-link" download href="${item.audit}">⬇ CSV · auditoría de identidad · tanda ${item.batch}</a><a class="download-link" download href="${item.series}">⬇ CSV · series verificadas · tanda ${item.batch}</a><a class="download-link" download href="${item.benchmarks}">⬇ CSV · contrafactuales · tanda ${item.batch}</a>`).join('');
      sourceLinks.insertAdjacentHTML('afterbegin',`${batchDownloads}<a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_candidate_audit_2026-09-01.csv">⬇ CSV · candidatos de homonimia</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_13_2026-09-01.csv">⬇ CSV · homonimias · tanda 13</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_14_2026-09-01.csv">⬇ CSV · homonimias · tanda 14</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_15_2026-09-01.csv">⬇ CSV · homonimia resuelta · tanda 15</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_exclusions_iteration_15_2026-09-01.csv">⬇ CSV · homónimos descartados · tanda 15</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_exclusions_iteration_16_2026-09-01.csv">⬇ CSV · cotejos reservados · tanda 16</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_exclusions_iteration_17_2026-09-01.csv">⬇ CSV · identidades cerradas · tanda 17</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_research_queue_2026-09-01.csv">⬇ CSV · cola de los 789</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_oa_identity_review_2026-09-01.csv">⬇ CSV · revisión de identidad OA</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_oa_candidate_series_2017_2024.csv">⬇ CSV · series OA candidatas</a><a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_research_summary_2026-09-01.json">⬇ JSON · avance de investigación</a>`);
      sourceLinks.insertAdjacentHTML('afterbegin','<a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_17_2026-09-01.csv">⬇ CSV · homonimia resuelta · tanda 17</a>');
      sourceLinks.insertAdjacentHTML('afterbegin','<a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv">⬇ CSV · autoridades PEN · tanda 18</a>');
      sourceLinks.insertAdjacentHTML('afterbegin','<a class="download-link" download href="research/political_wealth_2026-09-01/derived/active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv">⬇ CSV · puentes institucionales · tanda 19</a>');
    }
    if (sourceLinks && !sourceLinks.querySelector('[href="https://web.legisrn.gov.ar/institucional/legisladores"]')) {
      sourceLinks.insertAdjacentHTML('beforeend','<a class="source-link" target="_blank" rel="noopener" href="https://web.legisrn.gov.ar/institucional/legisladores">🏛️ Río Negro · Legisladores</a>');
    }
    if (sourceLinks && !sourceLinks.querySelector('[href="https://www.diputadosmisiones.gov.ar/nuevo/diputados"]')) {
      sourceLinks.insertAdjacentHTML('beforeend','<a class="source-link" target="_blank" rel="noopener" href="https://www.diputadosmisiones.gov.ar/nuevo/diputados">🏛️ Misiones · Representantes</a>');
    }
    if (sourceLinks && !sourceLinks.querySelector('[href="https://www.electoral.gob.ar/nuevo/paginas/pdf/BEP%204-2023.pdf"]')) {
      sourceLinks.insertAdjacentHTML('beforeend','<a class="source-link" target="_blank" rel="noopener" href="https://www.electoral.gob.ar/nuevo/paginas/pdf/BEP%204-2023.pdf">🗳️ Río Negro · acta de proclamación 2023</a>');
    }
    if (sourceLinks && !sourceLinks.querySelector('[href="https://www3.hcdn.gob.ar/archivos/transparencia/Opciones2025.pdf"]')) {
      sourceLinks.insertAdjacentHTML('beforeend','<a class="source-link" target="_blank" rel="noopener" href="https://www3.hcdn.gob.ar/archivos/transparencia/Opciones2025.pdf">🏛️ Diputados · nombres completos 2025</a>');
    }
    const sourcesNote = document.querySelector('#tab-political-wealth .sources-note');
    if (sourcesNote) sourcesNote.innerHTML = '<b>Corte analítico:</b> 02/09/2026. <b>Padrón:</b> 789 cargos; 298 trayectorias activas publicables y 491 casos freezados sin perder su estado ni sus fuentes. Las copias oficiales y periodísticas usadas en los casos profundos de Karina y Javier están respaldadas en el repo; las pesadas se excluyen del bundle liviano de Railway. <b>2025:</b> los tres valores publicados —Máximo, Javier y Karina— se conservan provisionales hasta respaldar sus PDF OA; ninguna anomalía aritmética se presenta como conclusión penal.';
    if (researchSummary) byId('pwResearchQueueStatus').innerHTML = `<strong>Expansión freezada al ${esc(researchSummary.expansion_universo_fecha || '02/09/2026')}: ${Number(researchSummary.cargos_freezados || 0).toLocaleString('es-AR')} cargos pendientes quedan preservados y ${Number(researchSummary.cargos_publicables || researchSummary.trayectorias_auditadas_activas).toLocaleString('es-AR')} tienen trayectoria publicable.</strong> El freeze cambia la prioridad hacia análisis más profundos; no borra fuentes, no cierra preguntas y no convierte una ausencia en incumplimiento o patrimonio cero. Las ${researchSummary.identidades_confirmadas_total.toLocaleString('es-AR')} identidades verificadas y sus ${researchSummary.filas_persona_anio_oa_preseleccionadas.toLocaleString('es-AR')} filas persona-año permanecen reproducibles.`;
    const deepCount = payload.people.length;
    byId('pwPersonViewButton').textContent = `Trayectorias auditadas (${deepCount.toLocaleString('es-AR')})`;
    byId('pwDeepHeroCount').textContent = deepCount.toLocaleString('es-AR');
    byId('pwDeepCoverageBadge').textContent = `${deepCount.toLocaleString('es-AR')} casos auditados`;
    byId('pwDeepScopeCopy').textContent = `Estas ${deepCount.toLocaleString('es-AR')} trayectorias tienen identidad auditada e importes persona-año normalizados. Los ${Number(researchSummary?.cargos_freezados || 0).toLocaleString('es-AR')} cargos restantes preservan su estado en “Todos los cargos”; el freeze no inventa una serie ni convierte N/D en cero.`;
    byId('pwPartyCohortNote').textContent = `${deepCount.toLocaleString('es-AR')} trayectorias con huecos, entradas y afiliaciones temporales distintas todavía no permiten atribuir diferencias a una agrupación.`;
    byId('pwQualityPositions').textContent = `${payload.series.length.toLocaleString('es-AR')} posiciones`;
    byId('pwQualityReconciliations').textContent = `${payload.reconciliation.length.toLocaleString('es-AR')} conciliaciones`;
    byId('pwQualityComposition').textContent = `${payload.composition.length.toLocaleString('es-AR')} agregados`;
    byId('pwQualityBenchmarks').textContent = `${payload.benchmark_comparisons.length.toLocaleString('es-AR')} contrafactuales`;
    byId('pwLoading').hidden = true;
    setView('coverage');
    byId('pwPersonControls').innerHTML = payload.people.map((person,index)=>`<button class="pw-person-button ${index===0?'active':''}" type="button" data-pw-person="${person.persona_id}" aria-pressed="${index===0?'true':'false'}">${person.persona}${payload?.case_audits?.[person.persona_id]?' · caso profundo':''}</button>`).join('');
    document.querySelectorAll('[data-pw-person]').forEach(button=>button.addEventListener('click',()=>{selectedPerson=button.dataset.pwPerson;document.querySelectorAll('[data-pw-person]').forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});renderPerson();}));
    byId('pwRosterSearch')?.addEventListener('input',renderActiveRoster);
    byId('pwRosterLevel')?.addEventListener('change',renderActiveRoster);
    byId('pwRosterStatus')?.addEventListener('change',renderActiveRoster);
    byId('pwActiveRosterBody')?.addEventListener('click',event=>{
      const button = event.target.closest('[data-pw-open-series]');
      if (button) openSeries(button.dataset.pwOpenSeries);
    });
    renderCoverage();
    renderPerson();
  }

  document.querySelectorAll('[data-pw-view]').forEach(button=>button.addEventListener('click',()=>setView(button.dataset.pwView)));
  tabs.querySelector('[data-tab="tab-political-wealth"]')?.addEventListener('click',()=>window.setTimeout(renderPerson,180));
  window.renderPoliticalWealth = ()=>{
    if(payload&&!document.querySelector('[data-pw-surface="person"]')?.hidden) renderPerson();
  };

  const bootstrap = window.__POLITICAL_WEALTH_BOOTSTRAP__;
  const hasBootstrap = Boolean(bootstrap?.data&&bootstrap?.roster);
  const wealthPanel = document.getElementById('tab-political-wealth');
  if(wealthPanel) wealthPanel.dataset.pwDataSource = hasBootstrap?'bootstrap':'fetch';
  const loadPromise = hasBootstrap
    ? Promise.resolve([bootstrap.data,bootstrap.roster,bootstrap.research||null,bootstrap.queue||[]])
    : Promise.all([
        fetchJson(DATA_URL,'serie patrimonial'),
        fetchJson(ROSTER_URL,'padrón activo'),
        fetchJson(RESEARCH_URL,'avance de investigación'),
        Promise.resolve([]),
        Promise.all([fetchJson(KARINA_AUDIT_URL,'auditoría Karina'),fetchJson(JAVIER_AUDIT_URL,'auditoría Javier')])
      ]);
  loadPromise.then(([data,roster,research,queue,caseAudits])=>initialize(data,roster,research,queue,caseAudits)).catch(error=>{byId('pwLoading').innerHTML=`No se pudo cargar el universo patrimonial (${error.message}). Los CSV siguen disponibles en la sección de fuentes.`;});
})();
