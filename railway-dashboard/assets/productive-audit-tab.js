(() => {
  'use strict';

  const scriptUrl = document.currentScript?.src || 'assets/productive-audit-tab.js';
  const dataUrl = new URL('productive-audit-data.json', scriptUrl).href;

  const STATUS = {
    partial: { label: 'Dato cierto · alcance recortado', short: 'Recorte', color: '#d7872f' },
    mismatch: { label: 'La cifra responde otra pregunta', short: 'Indicador cambiado', color: '#b94d7e' },
    unsupported: { label: 'Los datos no prueban la conclusión', short: 'Salto lógico', color: '#7461b8' }
  };

  const TESTS = [
    ['phenomenon', 'Mismo fenómeno'],
    ['period', 'Mismo período'],
    ['unit', 'Unidad comparable'],
    ['inference', 'Conclusión demostrada']
  ];

  class ProductiveAuditDashboard extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.data = null;
      this.filter = 'all';
      this.resizeObserver = null;
      this.boundTabOpen = () => requestAnimationFrame(() => this.renderCharts(true));
    }

    connectedCallback() {
      if (this.dataset.ready) return;
      this.dataset.ready = 'loading';
      this.renderShell();
      this.load();
    }

    disconnectedCallback() {
      this.resizeObserver?.disconnect();
      document.querySelector('[data-tab="tab-productive-audit"]')?.removeEventListener('click', this.boundTabOpen);
    }

    async load() {
      try {
        const response = await fetch(dataUrl, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        this.data = await response.json();
        this.renderApp();
        this.bind();
        this.renderClaims();
        this.renderSources();
        this.dataset.ready = 'true';
        document.querySelector('[data-tab="tab-productive-audit"]')?.addEventListener('click', this.boundTabOpen);
        this.resizeObserver = new ResizeObserver(entries => {
          if (entries.some(entry => entry.contentRect.width > 300)) this.renderCharts();
        });
        this.resizeObserver.observe(this);
        requestAnimationFrame(() => this.renderCharts());
      } catch (error) {
        this.shadowRoot.getElementById('paMount').innerHTML = `
          <section class="pa-error" role="alert">
            <strong>No se pudo cargar el chequeo productivo.</strong>
            <span>${this.escape(error.message)}. Probá recargar la página.</span>
          </section>`;
        this.dataset.ready = 'error';
      }
    }

    $(id) {
      return this.shadowRoot.getElementById(id);
    }

    escape(value) {
      return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      })[char]);
    }

    dec(value, digits = 1) {
      return new Intl.NumberFormat('es-AR', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits
      }).format(Number(value));
    }

    signed(value, digits = 1) {
      const number = Number(value);
      return `${number > 0 ? '+' : ''}${this.dec(number, digits)}%`;
    }

    money(value) {
      return `USD ${this.dec(Number(value) / 1000, 2)} mil M`;
    }

    renderShell() {
      this.shadowRoot.innerHTML = `
        <style>${this.styles()}</style>
        <div id="paMount" class="pa-loading" aria-live="polite">
          <span class="pa-loader" aria-hidden="true"></span>
          <strong>Cruzando series oficiales…</strong>
        </div>`;
    }

    renderApp() {
      const industry = this.data.activity.industry.latest;
      const construction = this.data.activity.construction.latest;
      const tourism = this.data.tourism.latest;
      const moi = this.data.trade.moi_decomposition;
      const oil = this.data.oil;
      const regional = this.data.regional_exports;

      this.shadowRoot.getElementById('paMount').outerHTML = `
        <main id="paMount" class="pa-app">
          <section class="pa-shield">
            <span>Chequeo de afirmaciones · corte 10/09/2026</span>
            <strong>No auditamos identidades ni intenciones. Auditamos si el dato citado alcanza para sostener la conclusión.</strong>
            <div><b>INDEC</b><b>Secretaría de Energía</b><b>Secretaría de Agricultura</b></div>
          </section>

          <header class="pa-hero">
            <div>
              <p class="pa-eyebrow">Un dato aislado puede ser verdadero y la historia, falsa</p>
              <h1>¿Dato cierto?<br><span>¿Conclusión cierta?</span></h1>
              <p class="pa-lead">Seis afirmaciones del comunicado oficial, sometidas a cuatro controles mínimos: fenómeno, período, unidad e inferencia.</p>
            </div>
            <aside class="pa-score">
              <small>RESULTADO DEL CONTROL</small>
              <strong><span>0</span> / 6</strong>
              <p>conclusiones atraviesan los cuatro controles. Esto no valida automáticamente la afirmación contraria.</p>
            </aside>
          </header>

          <section class="pa-rules" aria-label="Reglas de auditoría">
            ${TESTS.map(([key, label], index) => `
              <article><span>0${index + 1}</span><div><strong>${label}</strong><p>${{
                phenomenon: 'Producción no es exportación; turismo receptivo no es todo el turismo.',
                period: 'Un semestre, un mes y un año completo no se intercambian.',
                unit: 'Valor, precio, cantidad, nivel y variación cuentan cosas distintas.',
                inference: 'Un dato compatible con una historia no demuestra su causa.'
              }[key]}</p></div></article>`).join('')}
          </section>

          <section class="pa-section" id="paMatrixSection">
            <div class="pa-section-head">
              <div><p class="pa-eyebrow">01 · El mapa del problema</p><h2>Qué falla en cada afirmación</h2><p>Una cruz no dice que el número sea inventado: señala dónde deja de responder la pregunta original.</p></div>
              <button type="button" class="pa-download" id="paClaimsCsv">Matriz CSV ↓</button>
            </div>
            <div id="paMatrix" class="pa-matrix" role="table" aria-label="Matriz de control de afirmaciones"></div>
          </section>

          <section class="pa-section">
            <div class="pa-section-head">
              <div><p class="pa-eyebrow">02 · Actividad real</p><h2>La serie que corresponde a la pregunta</h2><p>Índices desestacionalizados de producción. Cada panel conserva su propia escala: no se comparan niveles entre IPI e ISAC.</p></div>
              <button type="button" class="pa-download" id="paActivityCsv">Series CSV ↓</button>
            </div>
            <div class="pa-chart-grid">
              <article class="pa-card pa-chart-card">
                <div class="pa-card-head"><div><small>INDUSTRIA · IPI</small><h3>${this.signed(industry.yoy_pct)} interanual</h3></div><b>${this.signed(industry.mom_pct)} mensual</b></div>
                <div id="paIndustryChart" class="pa-chart" aria-label="Serie del IPI manufacturero desestacionalizado"></div>
                <p><strong>Acumulado enero-julio: ${this.signed(industry.cumulative_yoy_pct)}.</strong> Julio queda en el percentil ${this.dec(industry.percentile_in_available_series, 1)} de la serie disponible desde 2016: muy bajo, aunque no es el mínimo.</p>
              </article>
              <article class="pa-card pa-chart-card">
                <div class="pa-card-head"><div><small>CONSTRUCCIÓN · ISAC</small><h3>${this.signed(construction.yoy_pct)} interanual</h3></div><b>${this.signed(construction.mom_pct)} mensual</b></div>
                <div id="paConstructionChart" class="pa-chart" aria-label="Serie del ISAC desestacionalizado"></div>
                <p><strong>Acumulado enero-julio: ${this.signed(construction.cumulative_yoy_pct)}.</strong> El +2,8% citado correspondía sólo a enero-junio; al sumar julio quedó en +1,7%.</p>
              </article>
            </div>
            <div class="pa-bridge">
              <strong>La palabra “histórica” necesita una regla.</strong>
              <p>¿Récord de caída mensual, interanual, acumulada o nivel frente a un año base? Las series muestran deterioro y niveles en el decil inferior, pero no autorizan un superlativo sin definir el benchmark.</p>
            </div>
          </section>

          <section class="pa-section pa-split">
            <article class="pa-card pa-pad">
              <div class="pa-card-head"><div><small>EXPORTACIONES MOI</small><h3>${this.signed(moi.value_yoy_pct)} en valor</h3></div><b>enero-julio</b></div>
              <div id="paMoiChart" class="pa-chart pa-chart-short" aria-label="Descomposición de la variación de exportaciones MOI"></div>
              <p><strong>${this.signed(moi.price_yoy_pct)} precios · ${this.signed(moi.quantity_yoy_pct)} cantidades.</strong> El valor exportado creció, pero no equivale a producción fabril ni a volumen físico.</p>
            </article>
            <article class="pa-card pa-pad pa-equation">
              <p class="pa-eyebrow">La identidad mínima</p>
              <div><i>Valor</i><span>≈</span><i>Precio</i><span>×</span><i>Cantidad</i></div>
              <strong>(1 + 0,1698) × (1 + 0,0684) − 1 ≈ 24,98%</strong>
              <p>Por eso “USD exportados +25%” no se puede leer como “industria +25%”. El propio cuadro de INDEC permite separar ambos efectos.</p>
            </article>
          </section>

          <section class="pa-section">
            <div class="pa-section-head"><div><p class="pa-eyebrow">03 · El denominador que desaparece</p><h2>Turismo: entraron más, pero eso no es “todo el turismo”</h2></div><button type="button" class="pa-jump" data-jump="tab-tourism">Abrir tab Turismo ↗</button></div>
            <article class="pa-card pa-tour-card">
              <div class="pa-tour-kpis">
                <div><small>ENTRARON</small><strong>${this.dec(tourism.inbound_tourists_thousands, 1)} mil</strong><span>${this.signed(tourism.inbound_yoy_pct)} interanual</span></div>
                <div><small>SALIERON</small><strong>${this.dec(tourism.outbound_tourists_thousands, 1)} mil</strong><span>${this.signed(tourism.outbound_yoy_pct)} interanual</span></div>
                <div class="negative"><small>SALDO DE TURISTAS</small><strong>${this.dec(tourism.tourist_balance_thousands, 1)} mil</strong><span>julio de 2026</span></div>
              </div>
              <div id="paTourismChart" class="pa-chart pa-chart-wide" aria-label="Turistas receptivos, emisivos y saldo"></div>
              <p class="pa-foot"><strong>Y todavía falta una dimensión:</strong> estas series son cruces internacionales. No miden ocupación, gasto ni viajes dentro del país; por lo tanto no refutan por sí solas una afirmación sobre turismo interno.</p>
            </article>
          </section>

          <section class="pa-section pa-split">
            <article class="pa-card pa-pad">
              <div class="pa-card-head"><div><small>37 COMPLEJOS REGIONALES</small><h3>USD ${this.dec(regional.value_usd_millions, 0)} M</h3></div><b>${this.signed(regional.value_yoy_pct)}</b></div>
              <div class="pa-region-grid">
                <div><strong>${this.dec(regional.volume_tonnes / 1e6, 2)} M t</strong><span>${this.signed(regional.volume_yoy_pct)} volumen</span></div>
                <div><strong>USD ${this.dec(regional.average_price_usd_per_tonne, 1)} / t</strong><span>${this.signed(regional.average_price_yoy_pct)} precio medio</span></div>
              </div>
              <p>El récord exportador es verificable y combina más volumen con mejor precio. Su universo es una canasta definida de 37 complejos: no es una medición integral de empleo, actividad o rentabilidad regional.</p>
            </article>
            <article class="pa-card pa-pad">
              <div class="pa-card-head"><div><small>PETRÓLEO · JULIO</small><h3>${this.dec(oil.barrels_per_day / 1000, 1)} mil barriles/día</h3></div><b>${this.signed(oil.yoy_pct)}</b></div>
              <div class="pa-oil-meter"><span style="width:${Math.min(100, oil.vaca_muerta_barrels_per_day / oil.barrels_per_day * 100)}%"></span></div>
              <p><strong>Vaca Muerta aportó ${this.dec(oil.vaca_muerta_barrels_per_day / 1000, 1)} mil barriles/día.</strong> El récord productivo es un dato sólido. Convertirlo en “independencia energética” requiere, además, demanda, estacionalidad, refinación, transporte e importaciones por producto.</p>
            </article>
          </section>

          <section class="pa-section">
            <div class="pa-section-head"><div><p class="pa-eyebrow">04 · Dos saldos oficiales, dos universos</p><h2>El superávit energético depende de qué se incluya</h2><p>Ambas cuentas son correctas. No deben mezclarse ni usarse como sinónimo automático de autoabastecimiento.</p></div><button type="button" class="pa-jump" data-jump="tab-trade">Abrir Balanza comercial ↗</button></div>
            <article class="pa-card pa-energy-card">
              <div id="paEnergyChart" class="pa-chart pa-chart-wide" aria-label="Dos definiciones oficiales del saldo comercial energético"></div>
              <div class="pa-energy-notes"><p><strong>USD 6.853 M</strong><span>Grandes rubros: exportaciones CyE menos importaciones CyL.</span></p><p><strong>USD 5.806 M</strong><span>Capítulo 27 de la NCM: universo aduanero más estrecho.</span></p></div>
              <div class="pa-warning"><strong>2013 anual ≠ enero-julio de 2026.</strong> La comparación del comunicado cambia de período y luego atribuye causalidad. Para medir evolución corresponde enfrentar meses equivalentes y controlar precios, cantidades y contexto.</div>
            </article>
          </section>

          <section class="pa-section" id="paClaimsSection">
            <div class="pa-section-head pa-wrap"><div><p class="pa-eyebrow">05 · Afirmación por afirmación</p><h2>El expediente corto</h2></div><div class="pa-filters" role="group" aria-label="Filtrar resultados"><button class="active" data-filter="all" aria-pressed="true">Todas</button><button data-filter="partial" aria-pressed="false">Recortes</button><button data-filter="mismatch" aria-pressed="false">Cambios de indicador</button><button data-filter="unsupported" aria-pressed="false">Saltos lógicos</button></div></div>
            <div id="paClaims" class="pa-claims"></div>
          </section>

          <section class="pa-section pa-method">
            <div><p class="pa-eyebrow">Cómo leer este chequeo</p><h2>No alcanza con encontrar un número verdadero.</h2><p>Una refutación válida debe usar el indicador que mide la afirmación, el mismo período, una unidad comparable y una inferencia que no exceda la evidencia. Si una etapa falla, la conclusión queda abierta.</p></div>
            <div class="pa-flow" aria-label="Secuencia de validación"><span>Dato</span><i>→</i><span>Universo</span><i>→</i><span>Comparación</span><i>→</i><span>Conclusión</span></div>
          </section>

          <section class="pa-section">
            <div class="pa-section-head"><div><p class="pa-eyebrow">Fuentes y trazabilidad</p><h2>Todo sale de planillas o publicaciones oficiales</h2><p>Los hashes identifican exactamente los archivos usados para construir este corte.</p></div></div>
            <div id="paSources" class="pa-sources"></div>
          </section>
        </main>`;
    }

    bind() {
      this.shadowRoot.querySelectorAll('[data-filter]').forEach(button => {
        button.addEventListener('click', () => {
          this.filter = button.dataset.filter;
          this.shadowRoot.querySelectorAll('[data-filter]').forEach(item => {
            const active = item === button;
            item.classList.toggle('active', active);
            item.setAttribute('aria-pressed', String(active));
          });
          this.renderClaims();
        });
      });
      this.shadowRoot.querySelectorAll('[data-jump]').forEach(button => {
        button.addEventListener('click', () => {
          document.querySelector(`[data-tab="${button.dataset.jump}"]`)?.click();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        });
      });
      this.$('paClaimsCsv')?.addEventListener('click', () => this.downloadClaimsCsv());
      this.$('paActivityCsv')?.addEventListener('click', () => this.downloadActivityCsv());
    }

    renderMatrix() {
      const head = `<div class="pa-matrix-row pa-matrix-head" role="row"><span role="columnheader">Afirmación</span>${TESTS.map(([, label]) => `<span role="columnheader">${label}</span>`).join('')}<span role="columnheader">Diagnóstico</span></div>`;
      const rows = this.data.claims.map(claim => `<div class="pa-matrix-row" role="row"><strong role="cell">${this.escape(claim.topic)}</strong>${TESTS.map(([key]) => `<span role="cell" class="pa-test ${claim.tests[key] ? 'pass' : 'fail'}" title="${claim.tests[key] ? 'Supera' : 'No supera'} este control">${claim.tests[key] ? '✓' : '×'}</span>`).join('')}<span role="cell" class="pa-pill ${claim.status}">${this.escape(claim.verdict)}</span></div>`).join('');
      this.$('paMatrix').innerHTML = head + rows;
    }

    renderClaims() {
      this.renderMatrix();
      const claims = this.data.claims.filter(claim => this.filter === 'all' || claim.status === this.filter);
      this.$('paClaims').innerHTML = claims.map((claim, index) => {
        const status = STATUS[claim.status];
        return `<article class="pa-claim" style="--status:${status.color}">
          <div class="pa-claim-number">${String(index + 1).padStart(2, '0')}</div>
          <div class="pa-claim-body"><div class="pa-claim-top"><span>${this.escape(claim.topic)}</span><b>${this.escape(status.label)}</b></div><h3>“${this.escape(claim.claim)}”</h3><p>${this.escape(claim.finding)}</p><div class="pa-claim-tests">${TESTS.map(([key, label]) => `<span class="${claim.tests[key] ? 'pass' : 'fail'}">${claim.tests[key] ? '✓' : '×'} ${label}</span>`).join('')}</div></div>
        </article>`;
      }).join('') || '<p class="pa-empty">No hay afirmaciones en este filtro.</p>';
    }

    renderSources() {
      this.$('paSources').innerHTML = this.data.sources.map(source => `<article>
        <small>${this.escape(source.institution)}</small>
        <strong>${this.escape(source.title)}</strong>
        <div><a href="${this.escape(source.url)}" target="_blank" rel="noopener">Ver publicación ↗</a>${source.data_url ? `<a href="${this.escape(source.data_url)}" target="_blank" rel="noopener">Descargar datos ↓</a>` : ''}</div>
        ${source.sha256 ? `<code title="SHA-256 del archivo usado">sha256 · ${source.sha256.slice(0, 12)}…</code>` : ''}
      </article>`).join('');
    }

    renderCharts(force = false) {
      if (!this.data || !window.Plotly || this.getBoundingClientRect().width < 300) return;
      if (this.dataset.charts === 'true' && !force) {
        ['paIndustryChart', 'paConstructionChart', 'paMoiChart', 'paTourismChart', 'paEnergyChart'].forEach(id => {
          const node = this.$(id);
          if (node) window.Plotly.Plots.resize(node);
        });
        return;
      }
      this.plotActivity('paIndustryChart', this.data.activity.industry.series, '#b64a7a', 'IPI');
      this.plotActivity('paConstructionChart', this.data.activity.construction.series, '#6b58b3', 'ISAC');
      this.plotMoi();
      this.plotTourism();
      this.plotEnergy();
      this.dataset.charts = 'true';
    }

    baseLayout(extra = {}) {
      return {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter, ui-sans-serif, system-ui, sans-serif', color: '#5b4266', size: 12 },
        margin: { l: 48, r: 18, t: 18, b: 42 },
        hoverlabel: { bgcolor: '#fffafb', bordercolor: '#d9c7df', font: { color: '#3d2748' } },
        ...extra
      };
    }

    plotConfig() {
      return { responsive: true, displayModeBar: false, staticPlot: false, scrollZoom: false };
    }

    plotActivity(id, rows, color, label) {
      window.Plotly.react(this.$(id), [
        {
          x: rows.map(row => row.date),
          y: rows.map(row => row.seasonally_adjusted),
          type: 'scatter', mode: 'lines', name: `${label} desestacionalizado`,
          line: { color, width: 2.5 }, fill: 'tozeroy', fillcolor: `${color}18`,
          hovertemplate: '%{x}<br><b>%{y:.1f}</b><extra></extra>'
        },
        {
          x: rows.map(row => row.date),
          y: rows.map(row => row.trend_cycle),
          type: 'scatter', mode: 'lines', name: 'Tendencia-ciclo',
          line: { color: '#42a48d', width: 2, dash: 'dot' },
          hovertemplate: '%{x}<br>Tendencia <b>%{y:.1f}</b><extra></extra>'
        }
      ], this.baseLayout({
        height: 320,
        showlegend: true,
        legend: { orientation: 'h', y: 1.12, x: 0, font: { size: 11 } },
        xaxis: { gridcolor: '#eee4f0', tickformat: '%Y', dtick: 'M24', fixedrange: true },
        yaxis: { title: 'Base 2004=100', gridcolor: '#eee4f0', zeroline: false, fixedrange: true },
        shapes: [{ type: 'line', x0: '2023-12', x1: '2023-12', y0: 0, y1: 1, yref: 'paper', line: { color: '#9376a2', dash: 'dash', width: 1 } }],
        annotations: [{ x: '2023-12', y: 1, yref: 'paper', text: 'dic-23', showarrow: false, yshift: 11, font: { size: 10, color: '#755681' } }]
      }), this.plotConfig());
    }

    plotMoi() {
      const moi = this.data.trade.moi_decomposition;
      window.Plotly.react(this.$('paMoiChart'), [{
        type: 'waterfall', orientation: 'v',
        x: ['Precio', 'Cantidad', 'Interacción', 'Valor'],
        y: [moi.price_yoy_pct, moi.quantity_yoy_pct, moi.value_yoy_pct - moi.price_yoy_pct - moi.quantity_yoy_pct, moi.value_yoy_pct],
        measure: ['relative', 'relative', 'relative', 'total'],
        text: [this.signed(moi.price_yoy_pct), this.signed(moi.quantity_yoy_pct), this.signed(moi.value_yoy_pct - moi.price_yoy_pct - moi.quantity_yoy_pct), this.signed(moi.value_yoy_pct)],
        textposition: 'outside', connector: { line: { color: '#cbb9d0' } },
        increasing: { marker: { color: '#3ca58b' } }, totals: { marker: { color: '#7954ba' } },
        hovertemplate: '%{x}: <b>%{y:.1f} pp</b><extra></extra>'
      }], this.baseLayout({
        height: 285, margin: { l: 42, r: 12, t: 28, b: 40 }, showlegend: false,
        xaxis: { fixedrange: true }, yaxis: { title: '% interanual', gridcolor: '#eee4f0', zerolinecolor: '#bca9c2', fixedrange: true }
      }), this.plotConfig());
    }

    plotTourism() {
      const rows = this.data.tourism.series.filter(row => row.date >= '2024-01');
      window.Plotly.react(this.$('paTourismChart'), [
        {
          x: rows.map(row => row.date), y: rows.map(row => row.inbound_tourists_thousands),
          type: 'scatter', mode: 'lines', name: 'Turistas que entraron',
          line: { color: '#2d9b7f', width: 2.5 }, hovertemplate: '%{x}<br>Entraron <b>%{y:.1f} mil</b><extra></extra>'
        },
        {
          x: rows.map(row => row.date), y: rows.map(row => row.outbound_tourists_thousands),
          type: 'scatter', mode: 'lines', name: 'Turistas que salieron',
          line: { color: '#c8507c', width: 2.5 }, hovertemplate: '%{x}<br>Salieron <b>%{y:.1f} mil</b><extra></extra>'
        },
        {
          x: rows.map(row => row.date), y: rows.map(row => row.tourist_balance_thousands),
          type: 'bar', name: 'Saldo', marker: { color: rows.map(row => row.tourist_balance_thousands >= 0 ? '#82cbb9' : '#e6a0b8') },
          opacity: 0.5, hovertemplate: '%{x}<br>Saldo <b>%{y:.1f} mil</b><extra></extra>'
        }
      ], this.baseLayout({
        height: 360, barmode: 'overlay',
        legend: { orientation: 'h', y: 1.12, x: 0, font: { size: 11 } },
        xaxis: { gridcolor: '#eee4f0', tickformat: '%b %Y', dtick: 'M6', fixedrange: true },
        yaxis: { title: 'Miles de turistas', gridcolor: '#eee4f0', zerolinecolor: '#997aa5', fixedrange: true }
      }), this.plotConfig());
    }

    plotEnergy() {
      const energy = this.data.trade.energy;
      const definitions = [energy.broad_classification, energy.chapter_27];
      window.Plotly.react(this.$('paEnergyChart'), [
        { x: definitions.map(item => item.label), y: definitions.map(item => item.exports_usd_millions), type: 'bar', name: 'Exportaciones', marker: { color: '#3fa58d' }, texttemplate: 'USD %{y:,.0f} M', textposition: 'outside', hovertemplate: '%{x}<br>Exportaciones <b>USD %{y:,.0f} M</b><extra></extra>' },
        { x: definitions.map(item => item.label), y: definitions.map(item => -item.imports_usd_millions), type: 'bar', name: 'Importaciones', marker: { color: '#c8507c' }, texttemplate: 'USD %{customdata:,.0f} M', customdata: definitions.map(item => item.imports_usd_millions), textposition: 'outside', hovertemplate: '%{x}<br>Importaciones <b>USD %{customdata:,.0f} M</b><extra></extra>' }
      ], this.baseLayout({
        height: 370, barmode: 'relative', margin: { l: 60, r: 25, t: 45, b: 85 },
        legend: { orientation: 'h', y: 1.14, x: 0 },
        xaxis: { tickfont: { size: 11 }, fixedrange: true },
        yaxis: { title: 'Millones de USD', gridcolor: '#eee4f0', zerolinecolor: '#997aa5', fixedrange: true },
        annotations: definitions.map((item, index) => ({ x: item.label, y: item.balance_usd_millions, text: `<b>Saldo USD ${this.dec(item.balance_usd_millions, 0)} M</b>`, showarrow: false, yshift: 18, xshift: index ? 45 : 35, font: { color: '#654275', size: 11 } }))
      }), this.plotConfig());
    }

    csvCell(value) {
      const text = String(value ?? '');
      return /[;"\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
    }

    download(filename, content) {
      const blob = new Blob(['\ufeff' + content], { type: 'text/csv;charset=utf-8' });
      const anchor = document.createElement('a');
      anchor.href = URL.createObjectURL(blob);
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(anchor.href), 800);
    }

    downloadClaimsCsv() {
      const header = ['tema', 'afirmacion', 'diagnostico', ...TESTS.map(([, label]) => label), 'hallazgo'];
      const rows = this.data.claims.map(claim => [claim.topic, claim.claim, claim.verdict, ...TESTS.map(([key]) => claim.tests[key] ? 'sí' : 'no'), claim.finding]);
      this.download('chequeo_productivo_afirmaciones_2026-09-10.csv', [header, ...rows].map(row => row.map(value => this.csvCell(value)).join(';')).join('\n'));
    }

    downloadActivityCsv() {
      const header = ['indicador', 'fecha', 'indice_original', 'var_interanual_pct', 'var_acumulada_pct', 'indice_desestacionalizado', 'var_mensual_pct', 'tendencia_ciclo'];
      const rows = [];
      for (const [key, label] of [['industry', 'IPI manufacturero'], ['construction', 'ISAC']]) {
        this.data.activity[key].series.forEach(row => rows.push([label, row.date, row.original, row.yoy_pct, row.cumulative_yoy_pct, row.seasonally_adjusted, row.mom_pct, row.trend_cycle]));
      }
      this.download('ipi_isac_series_oficiales_2026-07.csv', [header, ...rows].map(row => row.map(value => this.csvCell(value)).join(';')).join('\n'));
    }

    styles() {
      return `
        :host{display:block;color:#4b3157;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;--ink:#4b3157;--muted:#735f7c;--line:#e7d9e9;--paper:rgba(255,255,255,.92);--rose:#b94d7e;--violet:#7055b4;--mint:#329b82;--amber:#d7872f}
        *{box-sizing:border-box}button,a{font:inherit}.pa-app{display:grid;gap:22px}.pa-loading,.pa-error{min-height:280px;display:flex;align-items:center;justify-content:center;gap:12px;border:1px solid var(--line);border-radius:24px;background:var(--paper)}.pa-error{flex-direction:column;color:#9d315b}.pa-loader{width:24px;height:24px;border:3px solid #eadfeb;border-top-color:var(--rose);border-radius:50%;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
        .pa-shield{padding:15px 18px;border:1px solid #dcc7e1;border-radius:18px;background:linear-gradient(100deg,#fff4f8,#f7f2ff);display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;font-size:13px}.pa-shield>span{font-weight:900;letter-spacing:.05em;text-transform:uppercase;color:var(--rose)}.pa-shield>strong{font-weight:650}.pa-shield>div{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}.pa-shield b{padding:5px 8px;border-radius:999px;background:#fff;border:1px solid #e9dce9;font-size:11px}
        .pa-hero{min-height:400px;padding:42px;border:1px solid #d9c6df;border-radius:28px;background:radial-gradient(circle at 85% 18%,rgba(120,82,183,.18),transparent 29%),radial-gradient(circle at 12% 88%,rgba(55,163,136,.14),transparent 35%),linear-gradient(135deg,#fff8fb,#f7f1ff);display:grid;grid-template-columns:minmax(0,1.5fr) minmax(270px,.65fr);align-items:center;gap:35px;overflow:hidden;position:relative}.pa-hero:after{content:"?";position:absolute;right:26%;bottom:-130px;font:900 420px/1 Georgia,serif;color:rgba(112,85,180,.045);pointer-events:none}.pa-eyebrow{margin:0 0 8px;color:#97506f;text-transform:uppercase;letter-spacing:.085em;font-weight:900;font-size:12px}.pa-hero h1,.pa-section h2,.pa-card h3,.pa-method h2{font-family:Georgia,"Times New Roman",serif;color:#43274f}.pa-hero h1{margin:0;font-size:clamp(42px,6vw,78px);line-height:.98;letter-spacing:-.035em;position:relative;z-index:1}.pa-hero h1 span{color:var(--rose)}.pa-lead{max-width:760px;font-size:19px;line-height:1.55;color:#6b5275;margin:22px 0 0}.pa-score{position:relative;z-index:1;padding:28px;border-radius:22px;background:rgba(255,255,255,.86);border:1px solid #dac7df;box-shadow:0 18px 45px rgba(80,43,91,.12)}.pa-score small{font-size:11px;letter-spacing:.09em;font-weight:900;color:#8b637f}.pa-score strong{display:block;margin:8px 0;font:700 48px/1 Georgia,serif}.pa-score strong span{font-size:86px;color:var(--rose)}.pa-score p{margin:10px 0 0;line-height:1.5;color:var(--muted)}
        .pa-rules{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.pa-rules article{padding:18px;border:1px solid var(--line);border-radius:18px;background:var(--paper);display:flex;gap:12px}.pa-rules article>span{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;background:#f4eaf4;color:#8e4670;font-weight:900}.pa-rules strong{display:block;font-size:14px;color:var(--ink)}.pa-rules p{margin:5px 0 0;font-size:12px;line-height:1.45;color:var(--muted)}
        .pa-section{display:grid;gap:15px}.pa-section-head{display:flex;align-items:end;justify-content:space-between;gap:20px}.pa-section-head h2,.pa-method h2{margin:0;font-size:clamp(28px,4vw,44px);line-height:1.08}.pa-section-head p:not(.pa-eyebrow){margin:8px 0 0;color:var(--muted);line-height:1.5;max-width:780px}.pa-download,.pa-jump{border:1px solid #ceb9d5;border-radius:999px;background:#fff;color:#6a4378;padding:10px 14px;font-weight:850;cursor:pointer;white-space:nowrap}.pa-download:hover,.pa-jump:hover{background:#f6edf8}
        .pa-matrix{border:1px solid var(--line);border-radius:20px;overflow:hidden;background:var(--paper)}.pa-matrix-row{display:grid;grid-template-columns:minmax(150px,1.4fr) repeat(4,minmax(76px,.55fr)) minmax(130px,1fr);align-items:center;min-height:62px;border-top:1px solid var(--line)}.pa-matrix-row:first-child{border-top:0}.pa-matrix-row>*{padding:11px 12px}.pa-matrix-head{min-height:50px;background:#f8f2f8;font-size:10px;text-transform:uppercase;letter-spacing:.05em;font-weight:900}.pa-test{text-align:center;font-size:23px;font-weight:900}.pa-test.pass{color:var(--mint)}.pa-test.fail{color:var(--rose)}.pa-pill{justify-self:start;padding:6px 9px!important;border-radius:999px;font-size:11px;font-weight:900;background:#f7eff4}.pa-pill.partial{color:#a4661e;background:#fff5e8}.pa-pill.mismatch{color:#a03c6b;background:#fff0f6}.pa-pill.unsupported{color:#654ca7;background:#f4f0ff}
        .pa-chart-grid,.pa-split{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.pa-card{border:1px solid var(--line);border-radius:22px;background:var(--paper);box-shadow:0 12px 26px rgba(76,43,84,.055);overflow:hidden}.pa-chart-card{padding:20px}.pa-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.pa-card-head small{font-weight:900;letter-spacing:.08em;color:#95607e}.pa-card-head h3{font-size:27px;margin:4px 0 0}.pa-card-head>b{padding:7px 10px;border-radius:999px;background:#f5ecf7;color:#744681;font-size:12px}.pa-chart{width:100%;min-height:300px}.pa-chart-short{min-height:260px}.pa-chart-wide{min-height:340px}.pa-chart-card>p,.pa-card.pa-pad>p,.pa-foot{margin:3px 4px 0;line-height:1.55;color:var(--muted);font-size:13px}.pa-chart-card>p strong,.pa-card.pa-pad>p strong{color:var(--ink)}.pa-bridge{padding:16px 18px;border-left:4px solid var(--amber);border-radius:12px;background:#fff6e9;display:grid;grid-template-columns:auto 1fr;gap:15px;align-items:center}.pa-bridge strong{color:#855317}.pa-bridge p{margin:0;color:#765d64;line-height:1.5;font-size:13px}.pa-pad{padding:22px}.pa-equation{display:flex;flex-direction:column;justify-content:center;background:linear-gradient(135deg,#4a2d58,#7351a0);color:#fff;padding:30px}.pa-equation .pa-eyebrow,.pa-equation p{color:#eadfec!important}.pa-equation>div{display:flex;align-items:center;justify-content:center;gap:13px;margin:22px 0}.pa-equation i{font:700 26px Georgia,serif;font-style:normal}.pa-equation>strong{font-size:18px;text-align:center}.pa-equation>p:last-child{margin-top:20px!important}
        .pa-tour-card{padding:20px}.pa-tour-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.pa-tour-kpis>div{padding:17px;border-radius:16px;background:#f2faf7;border:1px solid #d9eee8}.pa-tour-kpis .negative{background:#fff2f6;border-color:#f0d5df}.pa-tour-kpis small{display:block;font-size:10px;font-weight:900;letter-spacing:.08em;color:#7b657d}.pa-tour-kpis strong{display:block;margin:5px 0;font:700 24px Georgia,serif;color:var(--ink)}.pa-tour-kpis span{font-size:12px;color:var(--muted)}.pa-foot{padding:0 4px 5px}.pa-region-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:24px 0}.pa-region-grid>div{padding:15px;border:1px solid #e8dae9;border-radius:15px;background:#faf6fb}.pa-region-grid strong,.pa-region-grid span{display:block}.pa-region-grid strong{font-size:21px;color:var(--ink)}.pa-region-grid span{margin-top:4px;font-size:12px;color:var(--muted)}.pa-oil-meter{height:32px;margin:32px 0 21px;border-radius:999px;background:#eadfed;overflow:hidden}.pa-oil-meter span{display:block;height:100%;background:linear-gradient(90deg,#7350b3,#c15480);border-radius:inherit}.pa-energy-card{padding:22px}.pa-energy-notes{display:grid;grid-template-columns:1fr 1fr;gap:12px}.pa-energy-notes p{margin:0;padding:15px;border-radius:14px;background:#faf6fb}.pa-energy-notes strong,.pa-energy-notes span{display:block}.pa-energy-notes strong{font:700 22px Georgia,serif;color:var(--ink)}.pa-energy-notes span{font-size:12px;line-height:1.45;color:var(--muted);margin-top:4px}.pa-warning{margin-top:14px;padding:15px 17px;border-radius:14px;background:#fff3e5;color:#795a3b;font-size:13px;line-height:1.5}
        .pa-wrap{align-items:center}.pa-filters{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}.pa-filters button{border:1px solid #d7c5dc;background:#fff;color:#6d5175;border-radius:999px;padding:8px 11px;cursor:pointer;font-size:12px;font-weight:800}.pa-filters button.active{background:#563465;color:#fff;border-color:#563465}.pa-claims{display:grid;gap:11px}.pa-claim{display:grid;grid-template-columns:62px 1fr;border:1px solid var(--line);border-left:5px solid var(--status);border-radius:18px;background:var(--paper);overflow:hidden}.pa-claim-number{display:grid;place-items:center;background:#faf6fa;font:700 20px Georgia,serif;color:#9c829f}.pa-claim-body{padding:18px}.pa-claim-top{display:flex;align-items:center;justify-content:space-between;gap:10px}.pa-claim-top>span{font-weight:950;text-transform:uppercase;letter-spacing:.07em;font-size:11px;color:var(--status)}.pa-claim-top>b{font-size:11px;color:var(--muted)}.pa-claim h3{margin:9px 0 7px;font-size:20px}.pa-claim p{margin:0;color:var(--muted);line-height:1.55}.pa-claim-tests{display:flex;gap:7px;flex-wrap:wrap;margin-top:13px}.pa-claim-tests span{padding:5px 8px;border-radius:8px;font-size:11px;font-weight:800}.pa-claim-tests .pass{background:#ecf8f4;color:#277b67}.pa-claim-tests .fail{background:#fff0f5;color:#a6416d}.pa-empty{padding:25px;text-align:center;color:var(--muted)}
        .pa-method{padding:30px;border-radius:24px;background:linear-gradient(135deg,#f9f1fa,#effaf6);border:1px solid #dccde0;grid-template-columns:1.1fr 1fr;align-items:center}.pa-method>div>p:not(.pa-eyebrow){color:var(--muted);line-height:1.6}.pa-flow{display:flex;align-items:center;justify-content:center;gap:9px;flex-wrap:wrap}.pa-flow span{padding:12px 14px;border-radius:12px;background:#fff;border:1px solid #ddcfe1;font-weight:900}.pa-flow i{font-style:normal;color:#9d809f}.pa-sources{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.pa-sources article{padding:16px;border:1px solid var(--line);border-radius:16px;background:var(--paper);display:flex;flex-direction:column;gap:7px}.pa-sources small{font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;color:#9a5575}.pa-sources strong{font-size:13px;line-height:1.4}.pa-sources article>div{display:flex;gap:10px;flex-wrap:wrap}.pa-sources a{color:#6b4a9c;text-decoration:none;font-size:11px;font-weight:850}.pa-sources a:hover{text-decoration:underline}.pa-sources code{font-size:9px;color:#8b788e;overflow-wrap:anywhere}
        :host-context(.dark) .pa-card,:host-context(.dark) .pa-matrix,:host-context(.dark) .pa-rules article,:host-context(.dark) .pa-sources article,:host-context(.dark-mode) .pa-card,:host-context(.dark-mode) .pa-matrix,:host-context(.dark-mode) .pa-rules article,:host-context(.dark-mode) .pa-sources article{background:rgba(39,29,45,.94)}:host-context(.dark),:host-context(.dark-mode){--ink:#f6eafa;--muted:#cbb8d0;--line:#503d57;color:#eaddeb}:host-context(.dark) .pa-hero,:host-context(.dark-mode) .pa-hero{background:radial-gradient(circle at 85% 18%,rgba(132,90,196,.25),transparent 29%),linear-gradient(135deg,#2b202f,#211a28)}:host-context(.dark) .pa-shield,:host-context(.dark) .pa-method,:host-context(.dark-mode) .pa-shield,:host-context(.dark-mode) .pa-method{background:linear-gradient(135deg,#302234,#252836)}:host-context(.dark) .pa-score,:host-context(.dark-mode) .pa-score{background:rgba(36,26,42,.9)}:host-context(.dark) .pa-matrix-head,:host-context(.dark) .pa-claim-number,:host-context(.dark) .pa-region-grid>div,:host-context(.dark) .pa-energy-notes p,:host-context(.dark-mode) .pa-matrix-head,:host-context(.dark-mode) .pa-claim-number,:host-context(.dark-mode) .pa-region-grid>div,:host-context(.dark-mode) .pa-energy-notes p{background:#302635}:host-context(.dark) .pa-download,:host-context(.dark) .pa-jump,:host-context(.dark) .pa-filters button,:host-context(.dark-mode) .pa-download,:host-context(.dark-mode) .pa-jump,:host-context(.dark-mode) .pa-filters button{background:#2c2131;color:#eee0f1}:host-context(.dark) .pa-equation,:host-context(.dark-mode) .pa-equation{background:linear-gradient(135deg,#36203f,#543d79)}
        @media(max-width:900px){.pa-shield{grid-template-columns:1fr}.pa-shield>div{justify-content:flex-start}.pa-hero{grid-template-columns:1fr;padding:30px}.pa-score{max-width:480px}.pa-rules{grid-template-columns:1fr 1fr}.pa-matrix{overflow-x:auto}.pa-matrix-row{min-width:780px}.pa-chart-grid,.pa-split,.pa-method{grid-template-columns:1fr}.pa-sources{grid-template-columns:1fr 1fr}}
        @media(max-width:600px){.pa-app{gap:18px}.pa-hero{padding:24px;min-height:0}.pa-hero h1{font-size:44px}.pa-lead{font-size:16px}.pa-score strong span{font-size:66px}.pa-rules{grid-template-columns:1fr}.pa-section-head{align-items:flex-start;flex-direction:column}.pa-chart-card,.pa-pad,.pa-tour-card,.pa-energy-card{padding:15px}.pa-tour-kpis,.pa-region-grid,.pa-energy-notes{grid-template-columns:1fr}.pa-chart{min-height:285px}.pa-claim{grid-template-columns:42px 1fr}.pa-claim-body{padding:14px}.pa-claim-top{align-items:flex-start;flex-direction:column}.pa-claim h3{font-size:18px}.pa-sources{grid-template-columns:1fr}.pa-bridge{grid-template-columns:1fr}.pa-filters{justify-content:flex-start}.pa-flow{justify-content:flex-start}}
        @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}.pa-loader{animation:none}}
      `;
    }
  }

  if (!customElements.get('productive-audit-dashboard')) {
    customElements.define('productive-audit-dashboard', ProductiveAuditDashboard);
  }
})();
