(() => {
  'use strict';

  const scriptUrl = document.currentScript?.src || 'assets/fortune-income-tab.js';
  const dataUrl = new URL('fortune-income-data.json', scriptUrl).href;

  class FortuneIncomeDashboard extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.data = null;
      this.catalogId = 'annual2026';
      this.aggregation = 'mean';
      this.selectedId = '';
      this.mode = 'households';
      this.zoomHouseholds = false;
      this.search = '';
      this.boundResize = () => this.drawDonut();
    }

    connectedCallback() {
      if (this.dataset.ready) return;
      this.dataset.ready = 'loading';
      this.renderShell();
      this.load();
    }

    disconnectedCallback() {
      window.removeEventListener('resize', this.boundResize);
    }

    async load() {
      try {
        const response = await fetch(dataUrl, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        this.data = await response.json();
        this.catalogId = this.data.defaults?.catalog || 'annual2026';
        this.selectedId = this.catalog.rows[0]?.id || '';
        this.renderApp();
        this.bind();
        this.reset();
        this.dataset.ready = 'true';
        window.addEventListener('resize', this.boundResize);
      } catch (error) {
        this.shadowRoot.getElementById('fiMount').innerHTML = `
          <section class="fi-error" role="alert">
            <strong>No se pudieron cargar los datos del tab.</strong>
            <span>${this.escape(error.message)}. Probá recargar la página.</span>
          </section>`;
        this.dataset.ready = 'error';
      }
    }

    get catalog() {
      return this.data.catalogs[this.catalogId];
    }

    $(id) {
      return this.shadowRoot.getElementById(id);
    }

    escape(value) {
      return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      })[char]);
    }

    renderShell() {
      this.shadowRoot.innerHTML = `
        <style>${this.styles()}</style>
        <div id="fiMount" class="fi-loading" aria-live="polite">
          <span class="fi-loader" aria-hidden="true"></span>
          <strong>Armando la comparación…</strong>
        </div>`;
    }

    renderApp() {
      const catalogOptions = Object.entries(this.data.catalogs)
        .map(([id, item]) => `<option value="${id}">${this.escape(item.label)}</option>`)
        .join('');
      const rateOptions = this.data.rates
        .map(item => `<option value="${item.id}">${this.escape(item.label)} · ${this.dec(item.annual_percent)}%</option>`)
        .join('');
      const salaryOptions = this.data.salary_references
        .map(item => `<option value="${item.id}">${this.escape(item.label)}</option>`)
        .join('');

      this.shadowRoot.getElementById('fiMount').outerHTML = `
        <div id="fiMount" class="fi-app">
          <section class="fi-shield" aria-label="Advertencia metodológica">
            <span>Ingresos y grandes fortunas · comparación de magnitudes</span>
            <strong>El patrimonio es un stock. Para compararlo con un ingreso mensual, primero lo convertimos en una renta financiera hipotética.</strong>
            <div class="fi-badges">
              <b>Forbes · estimaciones</b><b>SIPA / RIPTE · salarios</b><b>Escenario editable</b>
            </div>
          </section>

          <header class="fi-hero">
            <div>
              <p class="fi-eyebrow">Renta del capital · ingreso de hogares</p>
              <h1>La torta de los ingresos.<br><span>También por encima de la clase alta.</span></h1>
              <p class="fi-lead">Cinco ingresos familiares de referencia y una capa adicional: la renta mensual que podría producir una gran fortuna bajo supuestos explícitos.</p>
            </div>
            <aside class="fi-hero-note">
              <small>La pregunta</small>
              <strong>¿Qué escala de ingreso puede generar el capital sin gastar el capital?</strong>
              <p>La fortuna completa nunca entra a la torta. Sólo entra el flujo mensual simulado.</p>
            </aside>
          </header>

          <div class="fi-notice">
            <strong>No es una distribución del ingreso argentino ni una torta de población.</strong>
            Compara una referencia monetaria por categoría. Los universos, unidades y fechas son distintos.
          </div>

          <section class="fi-section fi-pyramid-section" id="fiPyramidSection">
            <div class="fi-section-head">
              <div>
                <p class="fi-eyebrow">Lectura de apertura · dos pirámides, dos unidades</p>
                <h2>La sociedad por hogares. El capital por patrimonio.</h2>
                <p>La primera reconstruye la placa original de Consultora W. La segunda invierte la forma y ordena las fortunas del catálogo elegido.</p>
              </div>
            </div>
            <div class="fi-pyramid-grid">
              <article class="fi-card fi-pyramid-card">
                <div class="fi-pyramid-title">
                  <div><small>PIRÁMIDE SOCIAL ORIGINAL</small><h3>Cómo se reparten los hogares</h3></div>
                  <b>% DE HOGARES</b>
                </div>
                <svg id="fiSocialPyramid" viewBox="0 0 760 455" role="img" aria-label="Pirámide social por porcentaje de hogares"></svg>
                <p id="fiSocialPyramidFoot" class="fi-pyramid-foot"></p>
              </article>
              <article class="fi-card fi-pyramid-card fi-pyramid-capital-card">
                <div class="fi-pyramid-title">
                  <div><small>PIRÁMIDE INVERTIDA DEL CAPITAL</small><h3>Quién concentra más patrimonio</h3></div>
                  <b>USD DE STOCK</b>
                </div>
                <svg id="fiCapitalPyramid" viewBox="0 0 760 455" role="img" aria-label="Pirámide invertida por patrimonio en dólares"></svg>
                <p id="fiCapitalPyramidFoot" class="fi-pyramid-foot"></p>
              </article>
            </div>
            <div class="fi-unit-note">
              <strong>No se superponen.</strong> La pirámide social usa participación de hogares e ingresos mensuales en ARS; la invertida compara stocks patrimoniales estimados en USD. La conversión a renta recién aparece en la torta monetaria.
            </div>
          </section>

          <section class="fi-card fi-controls" id="fiScenario">
            <div class="fi-section-head">
              <div><p class="fi-eyebrow">01 · Del capital al ingreso</p><h2>Elegí los supuestos</h2></div>
              <button type="button" id="fiReset">Restablecer</button>
            </div>
            <div class="fi-control-grid">
              <label>Catálogo patrimonial
                <select id="fiCatalog">${catalogOptions}</select>
                <small id="fiCatalogMeta"></small>
              </label>
              <label>Capital representativo
                <select id="fiAggregation">
                  <option value="mean">Promedio del catálogo</option>
                  <option value="median">Mediana del catálogo</option>
                  <option value="selected">Caso seleccionado</option>
                  <option value="sum">Suma del catálogo</option>
                </select>
                <small>La suma no equivale a la riqueza nacional.</small>
              </label>
              <label>Caso seleccionado
                <select id="fiCase"></select>
                <small>También podés elegirlo en el mapa.</small>
              </label>
              <label>Referencia de rendimiento
                <select id="fiRatePreset">${rateOptions}</select>
                <small id="fiRateMeta"></small>
              </label>
              <label>Rendimiento anual en USD (%)
                <input id="fiRate" type="number" min="0" max="20" step="0.01">
                <small>Prorrateo lineal r / 12; no promete cobro mensual.</small>
              </label>
              <label>Conversión ARS por USD
                <input id="fiFx" type="number" min="1" max="100000" step="1">
                <small id="fiFxMeta"></small>
              </label>
              <label>Parte invertible (%)
                <input id="fiFraction" type="number" min="0" max="100" step="1">
                <small>No se conoce la fracción líquida real.</small>
              </label>
              <label>Referencia salarial
                <select id="fiSalary">${salaryOptions}</select>
                <small id="fiSalaryMeta"></small>
              </label>
            </div>
            <details class="fi-extra">
              <summary>Ajustar liquidación, costos e impuestos</summary>
              <div class="fi-control-grid fi-control-grid-small">
                <label>Desagio al convertir activos (%)
                  <input id="fiHaircut" type="number" min="0" max="100" step="1">
                </label>
                <label>Costos anuales sobre capital (%)
                  <input id="fiFee" type="number" min="0" max="20" step="0.05">
                </label>
                <label>Impuesto efectivo sobre renta (%)
                  <input id="fiTax" type="number" min="0" max="100" step="1">
                </label>
              </div>
            </details>
            <div id="fiInputError" class="fi-input-error" role="alert" hidden></div>
            <div class="fi-param-foot">
              <span id="fiParamSummary"></span>
              <div><button type="button" id="fiDownloadCsv">Cálculo CSV ↓</button><button type="button" id="fiDownloadJson">Datos JSON ↓</button></div>
            </div>
          </section>

          <section class="fi-kpis" aria-live="polite">
            <article><small>CAPITAL DE REFERENCIA</small><strong id="fiCapitalKpi">—</strong><span id="fiCapitalDetail"></span></article>
            <article class="fi-kpi-purple"><small>RENTA MENSUAL SIMULADA</small><strong id="fiMonthlyKpi">—</strong><span id="fiMonthlyDetail"></span></article>
            <article><small>EQUIVALENCIA SALARIAL</small><strong id="fiSalaryKpi">—</strong><span id="fiSalaryDetail"></span></article>
            <article class="fi-kpi-mint"><small>VS. HOGAR DE CLASE ALTA</small><strong id="fiHighKpi">—</strong><span>Ingreso medio familiar de referencia: $14 millones.</span></article>
          </section>

          <section class="fi-section" id="fiPieSection">
            <div class="fi-section-head fi-section-head-wrap">
              <div>
                <p class="fi-eyebrow">02 · El área representa dinero mensual</p>
                <h2>Torta monetaria</h2>
                <p id="fiPieDescription">Una referencia por categoría; sin ponderar por cantidad de hogares.</p>
              </div>
              <div class="fi-switches" role="group" aria-label="Contenido de la torta">
                <button type="button" id="fiModeHouseholds" class="active" aria-pressed="true">Hogares + fortuna</button>
                <button type="button" id="fiModeSalary" aria-pressed="false">Salario + fortuna</button>
                <button type="button" id="fiZoomHouseholds" aria-pressed="false">Ampliar hogares</button>
              </div>
            </div>
            <div class="fi-card fi-chart-card">
              <div class="fi-pie-grid">
                <div class="fi-donut-wrap">
                  <svg id="fiDonut" viewBox="0 0 460 420" role="img" aria-label="Comparación de ingresos mensuales"></svg>
                  <p id="fiPieTotal"></p>
                </div>
                <div id="fiLegend" class="fi-legend"></div>
              </div>
              <p id="fiPieFoot" class="fi-chart-foot"></p>
            </div>
            <div class="fi-chart-bottom">
              <article class="fi-card fi-pad">
                <div class="fi-mini-title"><span>Cinco hogares · detalle ampliado</span><b>OTRA ESCALA</b></div>
                <div id="fiHouseholdBars" class="fi-household-bars"></div>
              </article>
              <article class="fi-card fi-insight">
                <small>La distancia entre referencias</small>
                <strong id="fiInsightRatio">—</strong>
                <p id="fiInsightText"></p>
              </article>
            </div>
          </section>

          <section class="fi-section">
            <div class="fi-section-head">
              <div>
                <p class="fi-eyebrow">03 · Patrimonio por patrimonio</p>
                <h2>Mapa de las grandes fortunas</h2>
                <p>Cada barra muestra la renta mensual hipotética con los mismos supuestos. Elegí un caso para abrir su cuenta.</p>
              </div>
            </div>
            <div class="fi-map-layout">
              <div class="fi-card fi-pad"><div id="fiWealthMap" class="fi-wealth-map"></div></div>
              <aside id="fiSelectedDetail" class="fi-card fi-detail"></aside>
            </div>
          </section>

          <section class="fi-section">
            <div class="fi-section-head fi-section-head-wrap">
              <div>
                <p class="fi-eyebrow">04 · Cuenta abierta</p>
                <h2>Capital, renta y equivalencias</h2>
                <p id="fiTableIntro"></p>
              </div>
              <label class="fi-search">Buscar
                <input id="fiSearch" type="search" placeholder="Nombre o grupo familiar…">
              </label>
            </div>
            <div class="fi-card fi-pad">
              <div class="fi-table-wrap">
                <table>
                  <thead><tr><th>Patrimonio reportado</th><th>Capital USD</th><th>Capital aplicado</th><th>Renta mensual ARS</th><th>Equiv. salarios</th><th>Fuente</th></tr></thead>
                  <tbody id="fiWealthRows"></tbody>
                </table>
              </div>
              <p id="fiTableNote" class="fi-note"></p>
            </div>
          </section>

          <section class="fi-section">
            <div class="fi-section-head">
              <div>
                <p class="fi-eyebrow">05 · El ingreso del trabajo</p>
                <h2>Comparación con salarios registrados</h2>
                <p>Son remuneraciones de puestos o personas, no ingresos familiares. Se muestran separados para no sumarlos dos veces.</p>
              </div>
            </div>
            <div id="fiSalaryCards" class="fi-salary-grid"></div>
            <div class="fi-card fi-capital-needed">
              <div><small>CAPITAL NECESARIO PARA GENERAR EL SALARIO ELEGIDO</small><strong id="fiCapitalNeeded">—</strong></div>
              <p id="fiCapitalNeededNote"></p>
            </div>
          </section>

          <section class="fi-section">
            <div class="fi-section-head">
              <div>
                <p class="fi-eyebrow">06 · Qué cambia si movemos un supuesto</p>
                <h2>Sensibilidad de la renta mensual</h2>
                <p>La tasa y la fracción invertible son supuestos. Esta matriz deja visible cuánto depende el resultado de cada uno.</p>
              </div>
            </div>
            <div class="fi-card fi-pad fi-table-wrap"><table id="fiSensitivity"></table></div>
          </section>

          <section class="fi-section">
            <div class="fi-section-head">
              <div>
                <p class="fi-eyebrow">07 · Sin mezclar stock con flujo</p>
                <h2>Cómo leer esta comparación</h2>
              </div>
            </div>
            <div class="fi-method-grid">
              <article class="fi-card fi-pad"><h3>La fórmula</h3><pre>Capital aplicado = patrimonio × fracción × (1 − desagio)
Renta anual = (capital × tasa − costos) − impuestos
Renta mensual ARS = renta anual ÷ 12 × ARS/USD</pre><p>La tasa es anualizada y se prorratea linealmente. No es una promesa de retorno ni una recomendación de inversión.</p></article>
              <article class="fi-card fi-pad"><h3>Qué significa “grandes fortunas”</h3><p id="fiScopeText"></p><p>Forbes estima patrimonios; no publica una auditoría fiscal. Algunas unidades son personas y otras grupos familiares.</p></article>
              <article class="fi-card fi-pad"><h3>Qué dice la torta</h3><p>Compara órdenes de magnitud mensuales bajo una cuenta reproducible. Permite ver cuánto ingreso puede producir un stock patrimonial sin consumirlo.</p><p><strong>No dice</strong> qué porción del ingreso nacional recibe cada clase.</p></article>
              <article class="fi-card fi-pad"><h3>Fechas, riesgo y límites</h3><p>Hogares, salarios, cotización y patrimonios tienen fechas y universos distintos. La referencia Treasury reduce el riesgo crediticio del ejercicio, pero no elimina riesgo de tasa, reinversión, mercado, liquidez, impuestos ni conversión.</p></article>
            </div>
          </section>

          <section class="fi-section">
            <div class="fi-section-head">
              <div>
                <p class="fi-eyebrow">08 · Abrí las fuentes y rehacé la cuenta</p>
                <h2>Fuentes y trazabilidad</h2>
                <p>Las fuentes respaldan los insumos. Las rentas y proporciones son cálculos de este tab.</p>
              </div>
            </div>
            <div id="fiSources" class="fi-sources"></div>
          </section>

          <footer class="fi-footer">
            <strong>Lectura responsable:</strong> ejercicio de magnitudes, no medición del ingreso observado de estas personas ni recomendación financiera. Datos compilados el ${this.escape(this.data.compiled_on)}.
          </footer>
        </div>`;
    }

    bind() {
      this.$('fiCatalog').addEventListener('change', event => {
        this.catalogId = event.target.value;
        this.selectedId = this.catalog.rows[0]?.id || '';
        this.populateCases();
        this.update();
      });
      this.$('fiAggregation').addEventListener('change', event => {
        this.aggregation = event.target.value;
        this.update();
      });
      this.$('fiCase').addEventListener('change', event => {
        this.selectedId = event.target.value;
        this.update();
      });
      this.$('fiRatePreset').addEventListener('change', event => {
        const rate = this.data.rates.find(item => item.id === event.target.value);
        if (rate) this.$('fiRate').value = rate.annual_percent;
        this.update();
      });
      ['fiRate', 'fiFx', 'fiFraction', 'fiHaircut', 'fiFee', 'fiTax', 'fiSalary']
        .forEach(id => this.$(id).addEventListener('input', () => this.update()));
      this.$('fiReset').addEventListener('click', () => this.reset());
      this.$('fiModeHouseholds').addEventListener('click', () => {
        this.mode = 'households';
        this.zoomHouseholds = false;
        this.update();
      });
      this.$('fiModeSalary').addEventListener('click', () => {
        this.mode = 'salary';
        this.zoomHouseholds = false;
        this.update();
      });
      this.$('fiZoomHouseholds').addEventListener('click', () => {
        this.mode = 'households';
        this.zoomHouseholds = !this.zoomHouseholds;
        this.update();
      });
      this.$('fiSearch').addEventListener('input', event => {
        this.search = event.target.value.trim().toLocaleLowerCase('es');
        this.renderTable(this.readParams());
      });
      this.$('fiDownloadCsv').addEventListener('click', () => this.downloadCsv());
      this.$('fiDownloadJson').addEventListener('click', () => this.downloadJson());
    }

    reset() {
      const defaults = this.data.defaults || {};
      this.catalogId = defaults.catalog || 'annual2026';
      this.aggregation = defaults.aggregation || 'mean';
      this.mode = defaults.pieMode === 'salary' ? 'salary' : 'households';
      this.zoomHouseholds = false;
      this.search = '';
      this.$('fiCatalog').value = this.catalogId;
      this.selectedId = this.catalog.rows[0]?.id || '';
      this.populateCases();
      this.$('fiAggregation').value = this.aggregation;
      this.$('fiRatePreset').value = defaults.rateId || 'ust3m';
      this.$('fiRate').value = defaults.rate ?? 3.91;
      this.$('fiFx').value = defaults.fx ?? this.data.fx.ars_per_usd;
      this.$('fiFraction').value = defaults.fraction ?? 100;
      this.$('fiHaircut').value = defaults.haircut ?? 0;
      this.$('fiFee').value = defaults.fee ?? 0;
      this.$('fiTax').value = defaults.tax ?? 0;
      this.$('fiSalary').value = defaults.salaryId || 'sipa_mean';
      this.$('fiSearch').value = '';
      this.update();
    }

    populateCases() {
      this.$('fiCase').innerHTML = this.catalog.rows
        .map(row => `<option value="${row.id}">${this.escape(row.name)} · ${this.shortUsd(row.wealth_usd)}</option>`)
        .join('');
      this.$('fiCase').value = this.selectedId;
    }

    readParams() {
      const values = {};
      const limits = {
        fiRate: [0, 20], fiFx: [1, 100000], fiFraction: [0, 100],
        fiHaircut: [0, 100], fiFee: [0, 20], fiTax: [0, 100]
      };
      for (const [id, [min, max]] of Object.entries(limits)) {
        const raw = this.$(id).value;
        const value = Number(raw);
        if (raw === '' || !Number.isFinite(value) || value < min || value > max) {
          throw new Error(`Revisá el valor de ${this.$(id).closest('label')?.childNodes[0]?.textContent.trim() || id}: debe estar entre ${min} y ${max}.`);
        }
        values[id] = value;
      }
      values.salary = this.data.salary_references.find(item => item.id === this.$('fiSalary').value)
        || this.data.salary_references[0];
      return {
        rate: values.fiRate, fx: values.fiFx, fraction: values.fiFraction,
        haircut: values.fiHaircut, fee: values.fiFee, tax: values.fiTax,
        salary: values.salary
      };
    }

    calculate(wealth, params) {
      const capital = wealth * params.fraction / 100 * (1 - params.haircut / 100);
      const gross = capital * params.rate / 100;
      const costs = capital * params.fee / 100;
      const beforeTax = gross - costs;
      const taxes = Math.max(beforeTax, 0) * params.tax / 100;
      const annual = beforeTax - taxes;
      return {
        wealth, capital, gross, costs, taxes, annual,
        monthlyUsd: annual / 12,
        monthlyArs: annual / 12 * params.fx
      };
    }

    representative() {
      const rows = this.catalog.rows;
      const wealth = rows.map(row => Number(row.wealth_usd)).sort((a, b) => a - b);
      if (this.aggregation === 'selected') {
        const row = rows.find(item => item.id === this.selectedId) || rows[0];
        return { wealth: row.wealth_usd, label: row.name };
      }
      if (this.aggregation === 'sum') {
        return { wealth: wealth.reduce((sum, value) => sum + value, 0), label: `Suma de ${rows.length} unidades` };
      }
      if (this.aggregation === 'median') {
        const middle = Math.floor(wealth.length / 2);
        const value = wealth.length % 2 ? wealth[middle] : (wealth[middle - 1] + wealth[middle]) / 2;
        return { wealth: value, label: `Mediana de ${rows.length} unidades` };
      }
      return {
        wealth: wealth.reduce((sum, value) => sum + value, 0) / wealth.length,
        label: `Promedio de ${rows.length} unidades`
      };
    }

    update() {
      let params;
      try {
        params = this.readParams();
        this.$('fiInputError').hidden = true;
      } catch (error) {
        this.$('fiInputError').textContent = `${error.message} Se conserva el último escenario válido.`;
        this.$('fiInputError').hidden = false;
        return;
      }
      const representative = this.representative();
      const result = this.calculate(representative.wealth, params);
      this.current = { params, representative, result };
      this.renderMeta(params, representative, result);
      this.renderKpis(params, representative, result);
      this.renderPyramids();
      this.drawDonut();
      this.renderHouseholds();
      this.renderMap(params);
      this.renderDetail(params);
      this.renderTable(params);
      this.renderSalaries(params);
      this.renderSensitivity(params, representative);
      this.renderSources();
      this.renderModeButtons();
    }

    renderMeta(params, representative, result) {
      const catalog = this.catalog;
      this.$('fiCatalogMeta').textContent = `${catalog.period}. ${catalog.scope}`;
      const rateMatch = this.data.rates.find(item => Math.abs(item.annual_percent - params.rate) < 1e-9);
      this.$('fiRateMeta').textContent = rateMatch
        ? rateMatch.id.startsWith('scenario')
          ? `${rateMatch.label}. Supuesto, no cotización.`
          : `${this.data.rate_metadata.date} · ${rateMatch.label}.`
        : 'Tasa personalizada: supuesto del escenario.';
      this.$('fiFxMeta').textContent = params.fx === Number(this.data.fx.ars_per_usd)
        ? `${this.data.fx.label} · ${this.data.fx.date}, ${this.data.fx.time_local}.`
        : 'Conversión personalizada: supuesto del escenario.';
      this.$('fiSalaryMeta').textContent = `${params.salary.period}. ${params.salary.basis}`;
      this.$('fiParamSummary').textContent =
        `${this.dec(params.rate)}% anual · ${this.dec(params.fraction, 0)}% invertible · ${this.dec(params.haircut, 0)}% desagio · ${this.dec(params.fee)}% costos · ${this.dec(params.tax, 0)}% impuesto · ${this.money(params.fx)} por USD`;
      this.$('fiScopeText').textContent = `${catalog.scope} ${catalog.comparability}`;
      this.$('fiTableIntro').textContent = `${catalog.label}. ${catalog.comparability}`;
      this.$('fiCapitalDetail').textContent = `${representative.label}. Aplicado: ${this.shortUsd(result.capital)}.`;
    }

    renderKpis(params, representative, result) {
      const high = this.data.income_groups.find(item => item.id === 'high') || this.data.income_groups[0];
      this.$('fiCapitalKpi').textContent = this.shortUsd(result.wealth);
      this.$('fiMonthlyKpi').textContent = this.shortMoney(result.monthlyArs);
      this.$('fiMonthlyDetail').textContent = `${this.shortUsd(result.monthlyUsd)} por mes antes de convertir a pesos.`;
      this.$('fiSalaryKpi').textContent = `${this.dec(result.monthlyArs / params.salary.value_ars, 1)} salarios`;
      this.$('fiSalaryDetail').textContent = `${params.salary.label} · ${this.money(params.salary.value_ars)}.`;
      this.$('fiHighKpi').textContent = `${this.dec(result.monthlyArs / high.monthly_ars, 1)} hogares`;
    }

    renderPyramids() {
      this.renderSocialPyramid();
      this.renderCapitalPyramid();
    }

    renderSocialPyramid() {
      const svg = this.$('fiSocialPyramid');
      if (!svg) return;
      const colors = ['#268447', '#eaa42d', '#f1cf38', '#e76f79', '#d9232e'];
      const boundaries = [30, 62, 100, 142, 184, 224];
      const center = 300;
      const startY = 67;
      const step = 62;
      const height = 50;
      const layers = this.data.income_groups.map((item, index) => {
        const y = startY + index * step;
        const top = boundaries[index];
        const bottom = boundaries[index + 1];
        const share = Number(item.household_share_percent || 0);
        const floor = Number(item.floor_ars);
        const floorLabel = Number.isFinite(floor) && floor > 0 ? this.shortMoney(floor) : 'Sin piso informado';
        const title = `${item.label}: ${this.dec(share, 0)}% de hogares; ingreso promedio ${this.money(item.monthly_ars)} por mes`;
        return `
          <g><title>${this.escape(title)}</title>
            <polygon points="${center - top},${y} ${center + top},${y} ${center + bottom},${y + height} ${center - bottom},${y + height}" fill="${colors[index]}" stroke="#fff" stroke-width="3"></polygon>
            <text x="${center}" y="${y + 32}" text-anchor="middle" fill="${index === 2 ? '#4d3157' : '#fff'}" font-size="20" font-weight="900">${this.dec(share, 0)}%</text>
            <text x="18" y="${y + 22}" fill="#765f7e" font-size="13" font-weight="800">${this.escape(floorLabel)}</text>
            <text x="548" y="${y + 19}" fill="#4d3157" font-size="14" font-weight="900">${this.escape(item.label)}</text>
            <text x="548" y="${y + 39}" fill="#765f7e" font-size="13">${this.escape(item.code)} · ${this.shortMoney(item.monthly_ars)} / mes</text>
          </g>`;
      }).join('');
      svg.innerHTML = `
        <text x="18" y="28" fill="#8b5076" font-size="11" font-weight="900" letter-spacing="1">PISO DEL NIVEL</text>
        <text x="300" y="28" text-anchor="middle" fill="#8b5076" font-size="11" font-weight="900" letter-spacing="1">% DE HOGARES</text>
        <text x="548" y="28" fill="#8b5076" font-size="11" font-weight="900" letter-spacing="1">INGRESO PROMEDIO</text>
        ${layers}`;
      const pyramid = this.data.household_pyramid || {};
      this.$('fiSocialPyramidFoot').innerHTML = `<strong>${this.escape(pyramid.period || '2.º trimestre 2026')}.</strong> Ingreso promedio del hogar total país: ${this.shortMoney(pyramid.average_household_ars || 3500000)}. En D2/E la placa informa 22% de hogares y 30% de la población.`;
    }

    renderCapitalPyramid() {
      const svg = this.$('fiCapitalPyramid');
      if (!svg) return;
      const sorted = [...this.catalog.rows].sort((a, b) => b.wealth_usd - a.wealth_usd);
      const selected = sorted.find(row => row.id === this.selectedId);
      const visible = sorted.slice(0, 6);
      if (selected && !visible.some(row => row.id === selected.id)) visible[5] = selected;
      visible.sort((a, b) => b.wealth_usd - a.wealth_usd);
      const max = Math.max(...visible.map(row => row.wealth_usd), 1);
      const center = 300;
      const startY = 66;
      const step = 57;
      const height = 47;
      const colors = ['#694094', '#7850a5', '#8761b5', '#9673c2', '#a788cf', '#baa0db'];
      const halfWidths = visible.map(row => 66 + 188 * (row.wealth_usd / max));
      const layers = visible.map((row, index) => {
        const y = startY + index * step;
        const top = halfWidths[index];
        const bottom = index < visible.length - 1 ? halfWidths[index + 1] : Math.max(48, top * .72);
        const selectedClass = row.id === this.selectedId;
        const shortName = row.name.length > 31 ? `${row.name.slice(0, 28)}…` : row.name;
        return `
          <g><title>${this.escape(row.name)}: ${this.shortUsd(row.wealth_usd)}</title>
            <polygon points="${center - top},${y} ${center + top},${y} ${center + bottom},${y + height} ${center - bottom},${y + height}" fill="${colors[index]}" stroke="${selectedClass ? '#4d3157' : '#fff'}" stroke-width="${selectedClass ? 5 : 3}"></polygon>
            <text x="${center}" y="${y + 21}" text-anchor="middle" fill="#fff" font-size="13" font-weight="900">${this.escape(shortName)}</text>
            <text x="${center}" y="${y + 39}" text-anchor="middle" fill="#fff" font-size="12">${this.shortUsd(row.wealth_usd)}</text>
            <text x="578" y="${y + 29}" fill="#765f7e" font-size="12">${index + 1}. ${this.escape(shortName)}</text>
          </g>`;
      }).join('');
      svg.innerHTML = `
        <text x="300" y="28" text-anchor="middle" fill="#8b5076" font-size="11" font-weight="900" letter-spacing="1">ANCHO PROPORCIONAL AL PATRIMONIO</text>
        <text x="578" y="28" fill="#8b5076" font-size="11" font-weight="900" letter-spacing="1">ORDEN DEL CATÁLOGO</text>
        ${layers}`;
      const includesExtra = selected && sorted.indexOf(selected) >= 6;
      this.$('fiCapitalPyramidFoot').innerHTML = `<strong>${this.escape(this.catalog.label)}.</strong> ${includesExtra ? 'Cinco patrimonios mayores más el caso seleccionado.' : `Se muestran los ${visible.length} patrimonios mayores.`} El ancho representa stock estimado, no ingreso ni cantidad de personas.`;
    }

    chartData() {
      const { params, result } = this.current;
      const fortune = {
        id: 'fortune', label: 'Grandes fortunas', value: result.monthlyArs,
        color: '#8b5cf6', note: 'Renta mensual hipotética'
      };
      if (this.mode === 'salary') {
        return [
          fortune,
          { id: 'salary', label: params.salary.label, value: params.salary.value_ars, color: '#2f8f79', note: params.salary.period }
        ];
      }
      const palette = ['#d79a33', '#32a795', '#5c9fda', '#d97593', '#a788b4'];
      const households = this.data.income_groups.map((item, index) => ({
        id: item.id, label: item.label, value: item.monthly_ars,
        color: palette[index], note: `${item.code} · promedio neto por hogar`
      }));
      return this.zoomHouseholds ? households : [fortune, ...households];
    }

    drawDonut() {
      if (!this.current || !this.$('fiDonut')) return;
      const data = this.chartData();
      const svg = this.$('fiDonut');
      const sum = data.reduce((total, item) => total + Math.max(0, item.value), 0);
      if (!(sum > 0)) {
        svg.innerHTML = '<text x="230" y="210" text-anchor="middle" fill="#705a78">No hay un flujo positivo para dibujar.</text>';
        return;
      }
      const arc = (cx, cy, outer, inner, start, end) => {
        const point = (radius, angle) => [cx + radius * Math.sin(angle), cy - radius * Math.cos(angle)];
        const p1 = point(outer, start), p2 = point(outer, end);
        const p3 = point(inner, end), p4 = point(inner, start);
        const large = end - start > Math.PI ? 1 : 0;
        return `M${p1} A${outer},${outer} 0 ${large} 1 ${p2} L${p3} A${inner},${inner} 0 ${large} 0 ${p4} Z`;
      };
      let position = 0;
      const tau = Math.PI * 2;
      const paths = data.map(item => {
        if (item.value <= 0) return '';
        const start = position;
        let end = position + item.value / sum * tau;
        if (end - start >= tau - 1e-10) end = start + tau - 1e-9;
        position = end;
        return `<path d="${arc(230, 197, 160, 105, start, end)}" fill="${item.color}" tabindex="0" aria-label="${this.escape(item.label)}: ${this.money(item.value)} por mes, ${this.dec(item.value / sum * 100, 3)}%"><title>${this.escape(item.label)} · ${this.money(item.value)} / mes</title></path>`;
      }).join('');
      const fortune = data.find(item => item.id === 'fortune');
      const centerTop = this.zoomHouseholds ? 'DETALLE HOGARES' : (fortune ? 'RENTA DEL CAPITAL' : 'REFERENCIAS');
      const centerValue = fortune && !this.zoomHouseholds
        ? `${this.dec(fortune.value / sum * 100, fortune.value / sum > .999 ? 4 : 1)}%`
        : this.shortMoney(Math.max(...data.map(item => item.value)));
      svg.innerHTML = `${paths}
        <text x="230" y="174" text-anchor="middle" fill="#79637f" font-size="11" font-weight="800" letter-spacing="1.1">${centerTop}</text>
        <text x="230" y="207" text-anchor="middle" fill="#4d3157" font-size="27" font-weight="900">${centerValue}</text>
        <text x="230" y="229" text-anchor="middle" fill="#79637f" font-size="11">${this.zoomHouseholds ? 'mayor referencia mensual' : 'de las referencias dibujadas'}</text>`;
      this.$('fiPieTotal').textContent = `Suma de referencias dibujadas: ${this.shortMoney(sum)} por mes`;
      this.$('fiLegend').innerHTML = data.map(item => `
        <div class="fi-legend-row">
          <i style="background:${item.color}"></i>
          <div><strong>${this.escape(item.label)}</strong><small>${this.escape(item.note)}</small></div>
          <div class="fi-legend-value"><strong>${this.shortMoney(item.value)}</strong><small>${this.dec(item.value / sum * 100, item.value / sum < .001 ? 4 : 1)}%</small></div>
        </div>`).join('');
      this.$('fiPieFoot').innerHTML = this.zoomHouseholds
        ? '<strong>Zoom metodológico:</strong> la renta patrimonial quedó fuera sólo para que las diferencias entre hogares sean legibles.'
        : '<strong>Lectura:</strong> cada porción es un monto mensual de referencia. El porcentaje pertenece únicamente a esta suma construida.';
    }

    renderModeButtons() {
      const households = this.mode === 'households' && !this.zoomHouseholds;
      const salary = this.mode === 'salary';
      this.$('fiModeHouseholds').classList.toggle('active', households);
      this.$('fiModeHouseholds').setAttribute('aria-pressed', String(households));
      this.$('fiModeSalary').classList.toggle('active', salary);
      this.$('fiModeSalary').setAttribute('aria-pressed', String(salary));
      this.$('fiZoomHouseholds').classList.toggle('active', this.zoomHouseholds);
      this.$('fiZoomHouseholds').setAttribute('aria-pressed', String(this.zoomHouseholds));
      this.$('fiPieDescription').textContent = salary
        ? 'Una remuneración individual frente a la renta hipotética del capital.'
        : this.zoomHouseholds
          ? 'Sólo referencias familiares, en una escala ampliada.'
          : 'Una referencia por hogar y una renta patrimonial; sin ponderar por población.';
    }

    renderHouseholds() {
      const max = Math.max(...this.data.income_groups.map(item => item.monthly_ars));
      this.$('fiHouseholdBars').innerHTML = this.data.income_groups.map((item, index) => {
        const colors = ['#d79a33', '#32a795', '#5c9fda', '#d97593', '#a788b4'];
        return `<div class="fi-household-row"><span>${this.escape(item.label)}</span><div><i style="width:${item.monthly_ars / max * 100}%;background:${colors[index]}"></i></div><strong>${this.shortMoney(item.monthly_ars)}</strong></div>`;
      }).join('');
      const high = this.data.income_groups.find(item => item.id === 'high') || this.data.income_groups[0];
      const poor = this.data.income_groups.find(item => item.id === 'lowpoor') || this.data.income_groups.at(-1);
      const ratio = high.monthly_ars / poor.monthly_ars;
      this.$('fiInsightRatio').textContent = `${this.dec(ratio, 1)} veces`;
      this.$('fiInsightText').textContent = `El ingreso familiar medio de clase alta equivale a ${this.dec(ratio, 1)} referencias de un hogar de clase baja en pobreza. La renta patrimonial está en otra escala.`;
    }

    renderMap(params) {
      const rows = this.catalog.rows
        .map(row => ({ ...row, calc: this.calculate(row.wealth_usd, params) }))
        .sort((a, b) => b.wealth_usd - a.wealth_usd);
      const max = Math.max(...rows.map(row => Math.max(0, row.calc.monthlyArs)), 1);
      const visible = rows.slice(0, this.catalogId === 'annual2026' ? 6 : 15);
      this.$('fiWealthMap').innerHTML = visible.map(row => `
        <button type="button" class="${row.id === this.selectedId ? 'selected' : ''}" data-fi-select="${row.id}" aria-pressed="${row.id === this.selectedId}">
          <span><strong>${this.escape(row.name)}</strong><small>${this.shortUsd(row.wealth_usd)}</small></span>
          <i><b style="width:${Math.max(1.5, row.calc.monthlyArs / max * 100)}%"></b></i>
          <em>${this.shortMoney(row.calc.monthlyArs)} / mes</em>
        </button>`).join('') + (rows.length > visible.length ? `<p>Se muestran los 15 mayores. La tabla conserva las ${rows.length} unidades.</p>` : '');
      this.shadowRoot.querySelectorAll('[data-fi-select]').forEach(button => button.addEventListener('click', () => {
        this.selectedId = button.dataset.fiSelect;
        this.$('fiCase').value = this.selectedId;
        this.update();
      }));
    }

    renderDetail(params) {
      const row = this.catalog.rows.find(item => item.id === this.selectedId) || this.catalog.rows[0];
      const result = this.calculate(row.wealth_usd, params);
      this.$('fiSelectedDetail').innerHTML = `
        <small>CASO SELECCIONADO</small>
        <h3>${this.escape(row.name)}</h3>
        <dl>
          <div><dt>Patrimonio estimado</dt><dd>${this.shortUsd(result.wealth)}</dd></div>
          <div><dt>Capital aplicado</dt><dd>${this.shortUsd(result.capital)}</dd></div>
          <div><dt>Interés bruto anual</dt><dd>${this.shortUsd(result.gross)}</dd></div>
          <div class="fi-detail-main"><dt>Renta mensual simulada</dt><dd>${this.shortMoney(result.monthlyArs)}</dd></div>
          <div><dt>Equiv. salario elegido</dt><dd>${this.dec(result.monthlyArs / params.salary.value_ars, 1)}</dd></div>
        </dl>
        <p>${this.escape(row.unit)}</p>
        <a href="${this.escape(row.source_url)}" target="_blank" rel="noopener noreferrer">Ver estimación original ↗</a>`;
    }

    renderTable(params) {
      let rows = this.catalog.rows;
      if (this.search) rows = rows.filter(row => `${row.name} ${row.unit}`.toLocaleLowerCase('es').includes(this.search));
      this.$('fiWealthRows').innerHTML = rows.map(row => {
        const result = this.calculate(row.wealth_usd, params);
        return `<tr>
          <td><strong>${this.escape(row.name)}</strong><small>${this.escape(row.unit)}</small></td>
          <td class="fi-num">${this.shortUsd(result.wealth)}</td>
          <td class="fi-num">${this.shortUsd(result.capital)}</td>
          <td class="fi-num">${this.shortMoney(result.monthlyArs)}</td>
          <td class="fi-num">${this.dec(result.monthlyArs / params.salary.value_ars, 1)}</td>
          <td><a href="${this.escape(row.source_url)}" target="_blank" rel="noopener noreferrer">[${this.escape(row.source_id)}] ↗</a></td>
        </tr>`;
      }).join('');
      this.$('fiTableNote').textContent = `${rows.length} de ${this.catalog.rows.length} unidades visibles. El buscador no modifica promedios, medianas ni sumas.`;
    }

    renderSalaries(params) {
      this.$('fiSalaryCards').innerHTML = this.data.salary_references.map(item => `
        <article class="fi-card ${item.id === params.salary.id ? 'selected' : ''}">
          <small>${this.escape(item.period)}</small>
          <h3>${this.escape(item.label)}</h3>
          <strong>${this.money(item.value_ars)}</strong>
          <p>${this.escape(item.basis)}</p>
          <a href="${this.escape(item.source_url)}" target="_blank" rel="noopener noreferrer">Fuente ↗</a>
        </article>`).join('');
      const effective = params.fraction / 100 * (1 - params.haircut / 100)
        * Math.max(params.rate - params.fee, 0) / 100 * (1 - params.tax / 100);
      const needed = effective > 0 ? params.salary.value_ars * 12 / (params.fx * effective) : Infinity;
      this.$('fiCapitalNeeded').textContent = Number.isFinite(needed) ? this.shortUsd(needed) : 'No calculable';
      this.$('fiCapitalNeededNote').textContent = Number.isFinite(needed)
        ? `Con el mismo rendimiento, conversión, fracción, desagio, costos e impuesto del escenario.`
        : 'La tasa neta del escenario no es positiva.';
    }

    renderSensitivity(params, representative) {
      const rates = [2, 3.91, 5];
      const fractions = [10, 25, 100];
      const header = `<thead><tr><th>Parte invertible</th>${rates.map(rate => `<th>${this.dec(rate)}% anual</th>`).join('')}</tr></thead>`;
      const body = fractions.map(fraction => {
        const cells = rates.map(rate => {
          const result = this.calculate(representative.wealth, { ...params, rate, fraction });
          return `<td>${this.shortMoney(result.monthlyArs)}<small>${this.dec(result.monthlyArs / params.salary.value_ars, 1)} salarios</small></td>`;
        }).join('');
        return `<tr><th>${fraction}%</th>${cells}</tr>`;
      }).join('');
      this.$('fiSensitivity').innerHTML = `${header}<tbody>${body}</tbody>`;
    }

    renderSources() {
      if (this.sourcesRendered) return;
      this.$('fiSources').innerHTML = this.data.sources.map(source => `
        <article class="fi-card" id="fi-source-${this.escape(source.id)}">
          <small>[${this.escape(source.id)}] · ${this.escape(source.date || '')}</small>
          <h3>${this.escape(source.label)}</h3>
          <p>${this.escape(source.values || source.type || '')}</p>
          ${source.caveat ? `<p class="fi-source-caveat">${this.escape(source.caveat)}</p>` : ''}
          <a href="${this.escape(source.url)}" target="_blank" rel="noopener noreferrer">Abrir fuente ↗</a>
        </article>`).join('');
      this.sourcesRendered = true;
    }

    downloadCsv() {
      const params = this.readParams();
      const rows = [['catalogo', 'nombre', 'patrimonio_usd', 'capital_aplicado_usd', 'renta_anual_neta_usd', 'renta_mensual_ars', 'equivalencia_salarios', 'fuente']];
      this.catalog.rows.forEach(row => {
        const result = this.calculate(row.wealth_usd, params);
        rows.push([
          this.catalogId, row.name, row.wealth_usd, result.capital, result.annual,
          result.monthlyArs, result.monthlyArs / params.salary.value_ars, row.source_url
        ]);
      });
      const csv = rows.map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n');
      this.downloadBlob(`grandes_fortunas_ingresos_${this.catalogId}.csv`, '\ufeff' + csv, 'text/csv;charset=utf-8');
    }

    downloadJson() {
      this.downloadBlob('ingresos_y_grandes_fortunas_datos.json', JSON.stringify(this.data, null, 2), 'application/json');
    }

    downloadBlob(filename, content, type) {
      const url = URL.createObjectURL(new Blob([content], { type }));
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 500);
    }

    dec(value, digits = 2) {
      return new Intl.NumberFormat('es-AR', { maximumFractionDigits: digits }).format(Number(value));
    }

    money(value) {
      return '$' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(Number(value));
    }

    shortMoney(value) {
      return this.short(value, '$');
    }

    shortUsd(value) {
      return this.short(value, 'USD ');
    }

    short(value, prefix) {
      const number = Number(value);
      const absolute = Math.abs(number);
      const sign = number < 0 ? '−' : '';
      if (!Number.isFinite(number)) return '—';
      if (absolute >= 1e12) return `${sign}${prefix}${this.dec(absolute / 1e12)} billones`;
      if (absolute >= 1e9) return `${sign}${prefix}${this.dec(absolute / 1e9)} mil M`;
      if (absolute >= 1e6) return `${sign}${prefix}${this.dec(absolute / 1e6)} M`;
      if (absolute >= 1e3) return `${sign}${prefix}${this.dec(absolute / 1e3)} mil`;
      return `${sign}${prefix}${this.dec(absolute)}`;
    }

    styles() {
      return `
        :host{display:block;--fi-ink:#4d3157;--fi-muted:#765f7e;--fi-line:#e6d7eb;--fi-panel:#fff;--fi-soft:#fbf7fd;--fi-purple:#8052aa;--fi-pink:#c85f86;--fi-mint:#2f8f79;--fi-shadow:0 12px 30px rgba(99,66,119,.075);color:var(--fi-ink);font:14px/1.52 Inter,ui-rounded,"Segoe UI",sans-serif}
        *{box-sizing:border-box}h1,h2,h3,p{margin:0}button,input,select,summary{font:inherit;color:inherit}button,input,select{border:1px solid var(--fi-line);border-radius:11px;background:#fff}button{padding:9px 13px;font-weight:800;cursor:pointer}button:hover{border-color:#b993cc;background:#fcf8fe}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid rgba(128,82,170,.25);outline-offset:2px}a{color:#7a3e91;text-underline-offset:3px}.fi-app{display:block}.fi-loading,.fi-error{min-height:280px;display:grid;place-content:center;gap:12px;text-align:center;border:1px solid var(--fi-line);border-radius:24px;background:var(--fi-soft)}.fi-loader{width:28px;height:28px;margin:auto;border:3px solid #eadff0;border-top-color:var(--fi-purple);border-radius:50%;animation:fiSpin .8s linear infinite}@keyframes fiSpin{to{transform:rotate(360deg)}}.fi-error span{color:var(--fi-muted)}
        .fi-shield{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:15px 18px;border:1px solid #dfcae8;border-radius:20px;background:#f8effc;box-shadow:var(--fi-shadow)}.fi-shield>span{font-size:11px;font-weight:900;letter-spacing:.045em;text-transform:uppercase;color:#765080}.fi-shield>strong{flex:1 1 480px;font-size:13px}.fi-badges{display:flex;gap:6px;flex-wrap:wrap}.fi-badges b{padding:5px 8px;border:1px solid #ddcce6;border-radius:8px;background:#fff;font-size:10px;letter-spacing:.02em}
        .fi-hero{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.75fr);gap:28px;align-items:end;padding:42px 12px 30px}.fi-eyebrow{margin-bottom:7px;color:#8b5076;font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.fi-hero h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(34px,5vw,60px);line-height:.98;letter-spacing:-2px}.fi-hero h1 span{color:var(--fi-pink)}.fi-lead{max-width:760px;margin-top:20px;color:#695270;font-size:16px}.fi-hero-note{padding:22px;border-left:4px solid var(--fi-purple);border-radius:8px 18px 18px 8px;background:#f5ecfa}.fi-hero-note small,.fi-insight small,.fi-detail>small,.fi-capital-needed small{display:block;color:#86688f;font-size:10px;font-weight:900;letter-spacing:.07em}.fi-hero-note>strong{display:block;margin:7px 0 10px;font:700 21px/1.18 Georgia,serif}.fi-hero-note p{color:var(--fi-muted);font-size:12px}.fi-notice{padding:14px 17px;border:1px solid #ecd8df;border-left:4px solid var(--fi-pink);border-radius:14px;background:#fff8fa;color:#6e5361}
        .fi-section{margin-top:38px}.fi-card{border:1px solid var(--fi-line);border-radius:20px;background:var(--fi-panel);box-shadow:var(--fi-shadow)}.fi-pad{padding:20px}.fi-controls{margin-top:20px;padding:22px}.fi-section-head{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:17px}.fi-section-head h2{font:800 25px/1.1 Georgia,serif}.fi-section-head p:not(.fi-eyebrow){margin-top:6px;color:var(--fi-muted)}.fi-section-head-wrap{flex-wrap:wrap}.fi-control-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px}.fi-control-grid label,.fi-search{display:flex;flex-direction:column;gap:6px;font-size:12px;font-weight:850}.fi-control-grid small{min-height:33px;color:var(--fi-muted);font-size:10px;font-weight:500;line-height:1.35}.fi-control-grid input,.fi-control-grid select,.fi-search input{width:100%;min-height:42px;padding:9px 10px}.fi-extra{margin-top:14px;border-top:1px solid var(--fi-line);padding-top:13px}.fi-extra summary{cursor:pointer;font-weight:850}.fi-control-grid-small{margin-top:14px;grid-template-columns:repeat(3,minmax(0,1fr))}.fi-param-foot{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:15px;padding-top:12px;border-top:1px solid var(--fi-line);color:var(--fi-muted);font-size:11px}.fi-param-foot>div{display:flex;gap:7px}.fi-input-error{margin-top:12px;padding:10px;border-radius:9px;background:#fff0f2;color:#9d2349;font-weight:750}
        .fi-pyramid-section{margin-top:30px}.fi-pyramid-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.fi-pyramid-card{padding:19px;overflow:hidden}.fi-pyramid-title{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}.fi-pyramid-title small{display:block;color:#8b5076;font-size:9px;font-weight:900;letter-spacing:.08em}.fi-pyramid-title h3{margin-top:4px;font:800 20px/1.1 Georgia,serif}.fi-pyramid-title>b{flex:none;padding:5px 7px;border:1px solid #dfcde7;border-radius:7px;background:#faf5fc;color:#765080;font-size:9px;letter-spacing:.04em}.fi-pyramid-card svg{display:block;width:100%;height:auto;margin:10px auto 0}.fi-pyramid-foot{min-height:48px;margin-top:4px;padding-top:11px;border-top:1px solid #eee5f1;color:var(--fi-muted);font-size:10px}.fi-unit-note{margin-top:13px;padding:13px 15px;border:1px solid #e1d3e7;border-left:4px solid var(--fi-purple);border-radius:12px;background:#f9f4fb;color:var(--fi-muted);font-size:11px}.fi-unit-note strong{color:var(--fi-ink)}
        .fi-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:14px}.fi-kpis article{min-height:145px;padding:18px;border:1px solid var(--fi-line);border-top:4px solid var(--fi-pink);border-radius:18px;background:#fff;box-shadow:var(--fi-shadow)}.fi-kpis article.fi-kpi-purple{border-top-color:var(--fi-purple)}.fi-kpis article.fi-kpi-mint{border-top-color:var(--fi-mint)}.fi-kpis small{display:block;color:#836b8a;font-size:10px;font-weight:900;letter-spacing:.055em}.fi-kpis strong{display:block;margin:10px 0 5px;font:850 clamp(21px,2.5vw,31px)/1.05 Georgia,serif}.fi-kpis span{color:var(--fi-muted);font-size:11px}
        .fi-switches{display:flex;gap:7px;flex-wrap:wrap}.fi-switches button.active{border-color:var(--fi-purple);background:var(--fi-purple);color:#fff}.fi-chart-card{padding:20px}.fi-pie-grid{display:grid;grid-template-columns:minmax(300px,.9fr) minmax(320px,1.1fr);gap:24px;align-items:center}.fi-donut-wrap{max-width:520px;margin:auto;text-align:center}.fi-donut-wrap svg{display:block;width:100%;height:auto;max-height:430px}.fi-donut-wrap p{color:var(--fi-muted);font-size:11px}.fi-legend{display:grid;gap:2px}.fi-legend-row{display:grid;grid-template-columns:11px minmax(0,1fr) auto;gap:11px;align-items:center;padding:12px 4px;border-bottom:1px solid #eee5f1}.fi-legend-row i{width:11px;height:36px;border-radius:5px}.fi-legend-row div>strong,.fi-legend-row div>small{display:block}.fi-legend-row small{color:var(--fi-muted);font-size:10px}.fi-legend-value{text-align:right}.fi-legend-value>strong{font-size:16px}.fi-chart-foot{margin-top:15px;padding:12px;border-radius:11px;background:#f7f1fa;color:var(--fi-muted);font-size:11px}.fi-chart-bottom{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(240px,.65fr);gap:13px;margin-top:13px}.fi-mini-title{display:flex;justify-content:space-between;gap:12px;font-weight:850}.fi-mini-title b{font-size:9px;color:#8c6b95}.fi-household-bars{display:grid;gap:11px;margin-top:17px}.fi-household-row{display:grid;grid-template-columns:110px minmax(80px,1fr) 82px;gap:10px;align-items:center;font-size:11px}.fi-household-row>div{height:9px;border-radius:5px;background:#f0e8f3;overflow:hidden}.fi-household-row i{display:block;height:100%;border-radius:5px}.fi-household-row strong{text-align:right}.fi-insight{display:flex;flex-direction:column;justify-content:center;padding:24px;background:#f7effb}.fi-insight>strong{display:block;margin:8px 0;font:850 36px Georgia,serif;color:var(--fi-purple)}.fi-insight p{color:var(--fi-muted)}
        .fi-map-layout{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(260px,.55fr);gap:13px}.fi-wealth-map{display:grid;gap:5px}.fi-wealth-map button{display:grid;grid-template-columns:minmax(170px,.8fr) minmax(100px,1fr) 125px;gap:12px;align-items:center;width:100%;padding:10px;border-color:transparent;text-align:left}.fi-wealth-map button.selected{border-color:#9f73b7;background:#f8f1fb}.fi-wealth-map span strong,.fi-wealth-map span small{display:block}.fi-wealth-map span small{color:var(--fi-muted);font-size:10px}.fi-wealth-map i{height:9px;border-radius:5px;background:#eee5f2;overflow:hidden}.fi-wealth-map i b{display:block;height:100%;border-radius:5px;background:var(--fi-purple)}.fi-wealth-map em{font-style:normal;font-weight:850;text-align:right}.fi-wealth-map>p{margin-top:8px;color:var(--fi-muted);font-size:11px}.fi-detail{padding:22px;background:#f7f0fa}.fi-detail h3{margin:7px 0 15px;font:800 24px/1.08 Georgia,serif}.fi-detail dl{margin:0}.fi-detail dl>div{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid #e7d9eb}.fi-detail dt{color:var(--fi-muted);font-size:11px}.fi-detail dd{margin:0;font-weight:850;text-align:right}.fi-detail .fi-detail-main dd{color:var(--fi-purple);font-size:17px}.fi-detail p{margin:15px 0 8px;color:var(--fi-muted);font-size:11px}
        .fi-search{width:min(300px,100%)}.fi-table-wrap{max-width:100%;overflow:auto}.fi-table-wrap table{width:100%;border-collapse:collapse;min-width:780px}.fi-table-wrap th,.fi-table-wrap td{padding:11px 9px;border-bottom:1px solid #eee6f0;text-align:left;vertical-align:top;font-size:11px}.fi-table-wrap thead th{position:sticky;top:0;background:#f7f1fa;color:#705878;font-size:9px;letter-spacing:.04em;text-transform:uppercase}.fi-table-wrap td small{display:block;max-width:250px;margin-top:3px;color:var(--fi-muted);font-size:9px}.fi-table-wrap .fi-num{text-align:right;font-variant-numeric:tabular-nums}.fi-note{margin-top:10px;color:var(--fi-muted);font-size:10px}.fi-salary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.fi-salary-grid article{padding:18px}.fi-salary-grid article.selected{border-color:#9a6caf;background:#faf5fc}.fi-salary-grid small{color:var(--fi-muted);font-size:10px}.fi-salary-grid h3{margin:5px 0 10px}.fi-salary-grid strong{display:block;font:800 24px Georgia,serif}.fi-salary-grid p{margin:9px 0;color:var(--fi-muted);font-size:10px}.fi-capital-needed{display:grid;grid-template-columns:minmax(230px,.7fr) minmax(0,1.3fr);gap:22px;align-items:center;margin-top:12px;padding:20px}.fi-capital-needed strong{display:block;margin-top:7px;font:850 28px Georgia,serif;color:var(--fi-purple)}.fi-capital-needed p{color:var(--fi-muted)}
        #fiSensitivity th,#fiSensitivity td{text-align:center}#fiSensitivity tbody th{background:#faf7fb}#fiSensitivity td{font-weight:850;font-size:14px}#fiSensitivity td small{max-width:none}.fi-method-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.fi-method-grid h3{margin-bottom:10px}.fi-method-grid p{margin-top:9px;color:var(--fi-muted)}.fi-method-grid pre{max-width:100%;overflow:auto;margin:0;padding:13px;border-radius:12px;background:#f7f1fa;color:#5b3b64;font:11px/1.6 ui-monospace,Consolas,monospace;white-space:pre-wrap}.fi-sources{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.fi-sources article{padding:17px}.fi-sources small{color:#8a6b92;font-size:9px}.fi-sources h3{margin:5px 0 9px;font-size:14px}.fi-sources p{color:var(--fi-muted);font-size:10px}.fi-sources .fi-source-caveat{margin-top:7px;padding-left:8px;border-left:3px solid #dd9bb2}.fi-sources a{display:inline-block;margin-top:10px;font-size:11px;font-weight:850}.fi-footer{margin-top:28px;padding:16px;border-top:1px solid var(--fi-line);color:var(--fi-muted);font-size:11px}
        @media(max-width:1000px){.fi-control-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.fi-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.fi-pyramid-grid,.fi-pie-grid,.fi-map-layout{grid-template-columns:1fr}.fi-detail{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}.fi-detail>small,.fi-detail h3,.fi-detail p,.fi-detail a{grid-column:1/-1}.fi-sources{grid-template-columns:repeat(2,minmax(0,1fr))}}
        @media(max-width:650px){:host{font-size:13px}.fi-shield{padding:13px}.fi-hero{display:block;padding:28px 4px 20px}.fi-hero h1{font-size:37px;letter-spacing:-1.1px}.fi-hero-note{margin-top:20px}.fi-controls{padding:16px}.fi-control-grid,.fi-control-grid-small,.fi-salary-grid,.fi-method-grid,.fi-sources{grid-template-columns:1fr}.fi-control-grid small{min-height:0;margin-bottom:4px}.fi-param-foot{align-items:flex-start;flex-direction:column}.fi-param-foot>div{width:100%;flex-wrap:wrap}.fi-kpis{gap:8px}.fi-kpis article{min-height:130px;padding:14px}.fi-kpis strong{font-size:22px}.fi-section{margin-top:30px}.fi-section-head{display:block}.fi-pyramid-card{padding:12px 8px}.fi-pyramid-title{padding:0 5px}.fi-pyramid-title h3{font-size:17px}.fi-pyramid-card svg{min-width:610px;transform-origin:left top}.fi-pyramid-card{overflow-x:auto}.fi-switches{margin-top:12px}.fi-chart-card{padding:12px 8px}.fi-pie-grid{gap:8px}.fi-chart-bottom{grid-template-columns:1fr}.fi-household-row{grid-template-columns:92px minmax(65px,1fr) 69px;gap:7px}.fi-wealth-map button{grid-template-columns:minmax(135px,.8fr) minmax(60px,1fr);gap:8px}.fi-wealth-map button em{grid-column:2;text-align:right;font-size:10px}.fi-detail{display:block}.fi-capital-needed{grid-template-columns:1fr}.fi-donut-wrap svg{max-height:360px}.fi-section-head h2{font-size:22px}}
      `;
    }
  }

  if (!customElements.get('fortune-income-dashboard')) {
    customElements.define('fortune-income-dashboard', FortuneIncomeDashboard);
  }
})();
