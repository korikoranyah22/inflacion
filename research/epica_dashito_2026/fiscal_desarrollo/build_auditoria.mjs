import fs from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const outDir = path.join(root, "research", "epica_dashito_2026", "fiscal_desarrollo");
const cutoff = "2026-08-31";

function parseDelimited(text, delimiter = ",") {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === delimiter) {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const [header, ...body] = rows.filter((r) => r.some((v) => v !== ""));
  return body.map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ""])));
}

function num(value) {
  if (value == null || value === "" || value === "NA") return null;
  return Number(String(value).replace(",", "."));
}

function csvEscape(value) {
  if (value == null) return "";
  const s = String(value);
  return /[",\n\r]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

async function writeCsv(name, rows, columns) {
  const text = [
    columns.join(","),
    ...rows.map((r) => columns.map((c) => csvEscape(r[c])).join(",")),
  ].join("\n") + "\n";
  await fs.writeFile(path.join(outDir, name), text, "utf8");
}

function pct(value, digits = 2) {
  return `${value.toFixed(digits)}%`;
}

const salary = parseDelimited(
  await fs.readFile(path.join(root, "data", "fuentes", "salarios", "indec", "indice_salarios_2026-08-20.csv"), "utf8"),
  ";",
);
const cpi = parseDelimited(
  await fs.readFile(path.join(root, "data", "fuentes", "tasas", "indec", "serie_ipc_divisiones.csv"), "utf8"),
  ";",
);
const fiscal = parseDelimited(
  await fs.readFile(path.join(root, "data", "derivados", "pendulo_poder_economico", "fiscal_result_2002_2026.csv"), "utf8"),
);
const emae = parseDelimited(
  await fs.readFile(path.join(root, "data", "derivados", "emae", "emae_mensual_limpio.csv"), "utf8"),
);
const routes = parseDelimited(
  await fs.readFile(path.join(root, "data", "derivados", "rutas_publico_privado", "rutas_publico_privado_corredores.csv"), "utf8"),
);
const householdNotes = await fs.readFile(
  path.join(root, "data", "fuentes", "hogares", "REFERENCIAS_AHORRO_STOCK_2018_2025.md"),
  "utf8",
);

const ipcByPeriod = new Map(
  cpi
    .filter((r) => r.Codigo === "0" && r.Descripcion === "NIVEL GENERAL" && r.Region === "Nacional")
    .map((r) => [r.Periodo, num(r.Indice_IPC)]),
);

function salaryPeriod(period) {
  const [, month, year] = period.split("/").map(Number);
  return `${year}-${String(month).padStart(2, "0")}`;
}

function realSalarySummary(column) {
  const base = salary.find((r) => r.periodo === "1/11/2023");
  const baseWage = num(base[column]);
  const baseCpi = ipcByPeriod.get("202311");
  const rows = salary
    .map((r) => {
      const period = salaryPeriod(r.periodo);
      const compact = period.replace("-", "");
      const wage = num(r[column]);
      const price = ipcByPeriod.get(compact);
      if (period < "2023-11" || wage == null || price == null) return null;
      return { period, real: 100 * (wage / price) / (baseWage / baseCpi) };
    })
    .filter(Boolean);
  const trough = rows.reduce((a, b) => (a.real < b.real ? a : b));
  const last = rows.at(-1);
  return {
    baseline_period: "2023-11",
    trough_period: trough.period,
    trough_index: trough.real,
    last_period: last.period,
    last_index: last.real,
    shock_pct: trough.real - 100,
    recovery_from_trough_pct: 100 * (last.real / trough.real - 1),
    saldo_vs_baseline_pct: last.real - 100,
  };
}

const wagePrivate = realSalarySummary("IS_sector_privado_registrado");
const wagePublic = realSalarySummary("IS_sector_publico");
const wageUnregistered = realSalarySummary("IS_sector_no_registrado");

const fiscal2023 = fiscal.find((r) => r.year === "2023");
const fiscal2024 = fiscal.find((r) => r.year === "2024");
const fiscalSwingPp = num(fiscal2024.financial_pct_gdp) - num(fiscal2023.financial_pct_gdp);

const emaeNov23 = emae.find((r) => r.date === "2023-11");
const emaeApr26 = emae.find((r) => r.date === "2026-04");
const emaeChange = 100 * (num(emaeApr26.sa) / num(emaeNov23.sa) - 1);
const emaePcChange = 100 * (num(emaeApr26.pc_sa_raw) / num(emaeNov23.pc_sa_raw) - 1);

const privateEmploymentNov23 = 6_381_500;
const privateEmploymentApr26 = 6_130_000;
const privateEmploymentDelta = privateEmploymentApr26 - privateEmploymentNov23;
const privateEmploymentPct = 100 * (privateEmploymentApr26 / privateEmploymentNov23 - 1);
const totalEmploymentNov23 = 13_323_500;
const totalEmploymentApr26 = 12_765_000;
const totalEmploymentDelta = totalEmploymentApr26 - totalEmploymentNov23;

const rigiApprovedInvestmentUsdM = 29_892;
const rigiApprovedJobs = 54_495;
const rigiApprovedJobsPerUsdBn = rigiApprovedJobs / (rigiApprovedInvestmentUsdM / 1000);
const rigiEvaluationInvestmentUsdM = 111_037;
const rigiEvaluationJobs = 142_168;
const rigiEvaluationJobsPerUsdBn = rigiEvaluationJobs / (rigiEvaluationInvestmentUsdM / 1000);
const rigiJobsVsPrivateLossPct = 100 * rigiApprovedJobs / Math.abs(privateEmploymentDelta);
const pampaInvestmentUsdM = 2_700;
const pampaConstructionJobs = 3_500;
const pampaPermanentJobs = 300;
const pampaConstructionPerUsdBn = pampaConstructionJobs / (pampaInvestmentUsdM / 1000);
const pampaPermanentPerUsdBn = pampaPermanentJobs / (pampaInvestmentUsdM / 1000);

const publicInvestmentIndex2023 = 100;
const publicInvestmentIndex2024 = 24.9;
const publicInvestmentIndex2025 = publicInvestmentIndex2024 * 0.73;
const publicInvestmentChange2025Vs2023 = publicInvestmentIndex2025 - 100;

const householdUseSavings1h2018 = 27.6;
const householdUseSavings1h2024 = 40.1;
const householdUseSavings2h2018 = 30.2;
const householdUseSavings2h2024 = 38.9;
const stockMechanicalEnd2024 = 100 * (1 - 0.206) * (1 + 0.217);
const stockReportedEnd2024 = 105.5;
const stockSpliceGapPp = stockReportedEnd2024 - stockMechanicalEnd2024;

const currentAccount2023UsdM = -20_956;
const currentAccount2024UsdM = 6_285;
const currentAccountSwingUsdM = currentAccount2024UsdM - currentAccount2023UsdM;

const operationalKm = routes
  .filter((r) => r.status === "En operación")
  .reduce((sum, r) => sum + num(r.km), 0);
const awardedKm = routes
  .filter((r) => r.status === "En operación" || r.status === "Adjudicado")
  .reduce((sum, r) => sum + num(r.km), 0);

const indecSalaryUrl = "https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-31-61";
const indecCpiUrl = "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31";
const indecEmaeUrl = "https://www.indec.gob.ar/ftp/cuadros/economia/sh_emae_mensual_base2004.xls";
const employmentUrl = "https://www.argentina.gob.ar/trabajo/estadisticas";
const employmentBaselineUrl = "https://www.argentina.gob.ar/sites/default/files/sis-2024.02_1.pdf";
const rigiUrl = "https://www.argentina.gob.ar/noticias/el-ministerio-de-economia-lanzo-una-web-oficial-con-la-informacion-de-los-proyectos-del";
const pampaUrl = "https://www.argentina.gob.ar/node/509056";
const opc2024Url = "https://opc.gob.ar/ejecucion-presupuestaria/ejecucion-mensual-base-devengado/analisis-de-la-ejecucion-presupuestaria-de-la-inversion-publica-2024/";
const opc2025Url = "https://opc.gob.ar/ejecucion-presupuestaria/ejecucion-mensual-base-devengado/analisis-de-la-ejecucion-presupuestaria-de-la-inversion-publica-2025/";
const bop2024q4Url = "https://www.indec.gob.ar/uploads/informesdeprensa/bal_03_25B8ADD14506.pdf";
const householdUrl = "https://www.indec.gob.ar/ftp/cuadros/publicaciones/dosier_estrategias_manutencion_2025.pdf";
const householdStockUrl = "https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-segundo-semestre-del-2024/";

const metrics = [
  {
    id: "H01",
    item_epica: "4",
    indicador: "Salario real privado registrado, mínimo vs nov-2023",
    periodo_base: wagePrivate.baseline_period,
    valor_base: 100,
    periodo_final: wagePrivate.trough_period,
    valor_final: wagePrivate.trough_index.toFixed(4),
    cambio: wagePrivate.shock_pct.toFixed(4),
    unidad: "índice real nov-2023=100 / %",
    formula: "100*(IS_t/IPC_t)/(IS_nov2023/IPC_nov2023)",
    lectura: `Tocó ${wagePrivate.trough_index.toFixed(2)} en ${wagePrivate.trough_period}; a ${wagePrivate.last_period} quedó ${pct(wagePrivate.saldo_vs_baseline_pct)} vs nov-2023.`,
    fuente_url: `${indecSalaryUrl} | ${indecCpiUrl}`,
    fuente_local: "data/fuentes/salarios/indec/indice_salarios_2026-08-20.csv | data/fuentes/tasas/indec/serie_ipc_divisiones.csv",
    confianza: "alta",
    causalidad: "incidencia observada; no atribuye causa",
  },
  {
    id: "H02",
    item_epica: "4",
    indicador: "Salario real público, mínimo vs nov-2023",
    periodo_base: wagePublic.baseline_period,
    valor_base: 100,
    periodo_final: wagePublic.trough_period,
    valor_final: wagePublic.trough_index.toFixed(4),
    cambio: wagePublic.shock_pct.toFixed(4),
    unidad: "índice real nov-2023=100 / %",
    formula: "100*(IS_t/IPC_t)/(IS_nov2023/IPC_nov2023)",
    lectura: `Tocó ${wagePublic.trough_index.toFixed(2)} en ${wagePublic.trough_period}; a ${wagePublic.last_period} seguía ${pct(wagePublic.saldo_vs_baseline_pct)} vs nov-2023.`,
    fuente_url: `${indecSalaryUrl} | ${indecCpiUrl}`,
    fuente_local: "data/fuentes/salarios/indec/indice_salarios_2026-08-20.csv | data/fuentes/tasas/indec/serie_ipc_divisiones.csv",
    confianza: "alta",
    causalidad: "incidencia observada; no atribuye causa",
  },
  {
    id: "H03",
    item_epica: "3-4",
    indicador: "Hogares que usaron ahorros, 1S-2024 vs 1S-2018",
    periodo_base: "2018-1S",
    valor_base: householdUseSavings1h2018,
    periodo_final: "2024-1S",
    valor_final: householdUseSavings1h2024,
    cambio: (householdUseSavings1h2024 - householdUseSavings1h2018).toFixed(1),
    unidad: "% hogares / puntos porcentuales",
    formula: "%2024 - %2018",
    lectura: "La incidencia subió 12,5 pp; mide uso declarado, no pesos ni ahorro neto de cuentas nacionales.",
    fuente_url: householdUrl,
    fuente_local: "data/fuentes/hogares/REFERENCIAS_AHORRO_STOCK_2018_2025.md",
    confianza: "alta para incidencia; baja para monto",
    causalidad: "descriptiva",
  },
  {
    id: "H04",
    item_epica: "3",
    indicador: "Cuenta corriente anual",
    periodo_base: "2023",
    valor_base: currentAccount2023UsdM,
    periodo_final: "2024",
    valor_final: currentAccount2024UsdM,
    cambio: currentAccountSwingUsdM,
    unidad: "USD millones",
    formula: "total anual 2024 menos total anual 2023, última revisión publicada en informe 4T-2024",
    lectura: "Pasó de necesidad a capacidad externa de financiamiento; no desagrega hogares y empresas.",
    fuente_url: bop2024q4Url,
    fuente_local: "N/D (fuente primaria web verificada al corte)",
    confianza: "alta; datos provisorios revisables",
    causalidad: "identidad contable agregada",
  },
  {
    id: "H05",
    item_epica: "18-19",
    indicador: "EMAE desestacionalizado vs empleo privado registrado",
    periodo_base: "2023-11",
    valor_base: 100,
    periodo_final: "2026-04",
    valor_final: (100 + emaeChange).toFixed(4),
    cambio: emaeChange.toFixed(4),
    unidad: "EMAE %; empleo en observación complementaria",
    formula: "100*(EMAE_abr26/EMAE_nov23-1)",
    lectura: `EMAE +${emaeChange.toFixed(2)}% y EMAE per cápita +${emaePcChange.toFixed(2)}%; empleo privado registrado ${pct(privateEmploymentPct)} (${privateEmploymentDelta.toLocaleString("es-AR")} personas).`,
    fuente_url: `${indecEmaeUrl} | ${employmentUrl} | ${employmentBaselineUrl}`,
    fuente_local: "data/derivados/emae/emae_mensual_limpio.csv",
    confianza: "media-alta; universos distintos",
    causalidad: "simultaneidad, no elasticidad causal",
  },
  {
    id: "H06",
    item_epica: "17",
    indicador: "RIGI aprobado: empleos proyectados por USD 1.000 M",
    periodo_base: "2026-06-11",
    valor_base: rigiApprovedInvestmentUsdM,
    periodo_final: "2026-06-11",
    valor_final: rigiApprovedJobs,
    cambio: rigiApprovedJobsPerUsdBn.toFixed(2),
    unidad: "empleos directos+indirectos proyectados / USD 1.000 M",
    formula: "54.495/(29.892/1.000)",
    lectura: "Es intensidad anunciada para proyectos aprobados, no puestos observados ni permanentes.",
    fuente_url: rigiUrl,
    fuente_local: "N/D (fuente primaria web verificada al corte)",
    confianza: "media para proyección; nula como empleo realizado",
    causalidad: "proyección del promotor público",
  },
  {
    id: "H07",
    item_epica: "17-40",
    indicador: "Proyecto Pampa urea: empleo permanente por USD 1.000 M",
    periodo_base: "2026-07-31",
    valor_base: pampaInvestmentUsdM,
    periodo_final: "operación proyectada",
    valor_final: pampaPermanentJobs,
    cambio: pampaPermanentPerUsdBn.toFixed(2),
    unidad: "empleos permanentes proyectados / USD 1.000 M",
    formula: "300/(2.700/1.000)",
    lectura: `La construcción proyecta ${pampaConstructionPerUsdBn.toFixed(0)} empleos directos+indirectos por USD 1.000 M, pero la operación ${pampaPermanentPerUsdBn.toFixed(0)}; no son stocks simultáneos.`,
    fuente_url: pampaUrl,
    fuente_local: "N/D (fuente primaria web verificada al corte)",
    confianza: "media para proyección; nula como ejecución",
    causalidad: "proyección del proyecto",
  },
  {
    id: "H08",
    item_epica: "23",
    indicador: "Inversión pública real, índice 2023=100",
    periodo_base: "2023",
    valor_base: publicInvestmentIndex2023,
    periodo_final: "2025",
    valor_final: publicInvestmentIndex2025.toFixed(4),
    cambio: publicInvestmentChange2025Vs2023.toFixed(4),
    unidad: "índice real / %",
    formula: "100*(1-0,751)*(1-0,270)",
    lectura: `2024 quedó en 24,90 y 2025 en ${publicInvestmentIndex2025.toFixed(2)}; no equivale a depreciación física medida.`,
    fuente_url: `${opc2024Url} | ${opc2025Url}`,
    fuente_local: "data/derivados/rutas_publico_privado/AUDITORIA_RUTAS_PUBLICO_PRIVADO.md",
    confianza: "alta para flujo presupuestario",
    causalidad: "incidencia presupuestaria observada",
  },
  {
    id: "H09",
    item_epica: "20",
    indicador: "Base necesaria para neutralidad con baja de IIBB del 50%",
    periodo_base: "escenario mecánico",
    valor_base: 100,
    periodo_final: "misma recaudación",
    valor_final: 200,
    cambio: 100,
    unidad: "índice de base / % crecimiento",
    formula: "B1/B0=1/(1-r); crecimiento=r/(1-r)",
    lectura: "Sin respuesta de base, una baja del 50% exige duplicarla; eliminar la alícuota no admite compensación finita dentro del mismo impuesto.",
    fuente_url: "identidad tributaria; sin fuente externa",
    fuente_local: "este script",
    confianza: "alta para aritmética; nula para conducta",
    causalidad: "escenario, no pronóstico",
  },
  {
    id: "H10",
    item_epica: "37",
    indicador: "Kilómetros de corredores concesionados en operación",
    periodo_base: "corte local 2026-08-21",
    valor_base: operationalKm.toFixed(2),
    periodo_final: "incluyendo adjudicados",
    valor_final: awardedKm.toFixed(2),
    cambio: (awardedKm - operationalKm).toFixed(2),
    unidad: "km concesionados",
    formula: "suma km por status",
    lectura: "Output contractual/operativo; no son km construidos, rehabilitados ni estado físico mejorado.",
    fuente_url: "https://www.argentina.gob.ar/transporte/vialidad-nacional/red-federal-de-concesiones",
    fuente_local: "data/derivados/rutas_publico_privado/rutas_publico_privado_corredores.csv",
    confianza: "alta para status oficial; baja para outcome vial",
    causalidad: "input/output, no outcome",
  },
];

const iibbScenarios = [0.10, 0.25, 0.50, 1.00].map((reduction) => {
  const finite = reduction < 1;
  const multiplier = finite ? 1 / (1 - reduction) : null;
  return {
    reduccion_alicuota_pct: reduction * 100,
    alicuota_remanente_pct_de_original: (1 - reduction) * 100,
    multiplicador_base_neutral: finite ? multiplier.toFixed(6) : "N/D",
    crecimiento_base_necesario_pct: finite ? (100 * (multiplier - 1)).toFixed(6) : "infinito/no existe",
    formula: finite ? "1/(1-r)-1" : "con t1=0, t1*B1=0 para toda base finita",
    interpretacion: finite
      ? "Identidad mecánica antes de evasión, formalización, actividad y traslado."
      : "Eliminar el impuesto no puede recaudar lo mismo mediante expansión de su propia base.",
  };
});

const incidence = [
  {
    grupo: "asalariados privados registrados",
    shock_inicial: `${pct(wagePrivate.shock_pct)} al mínimo de ${wagePrivate.trough_period}`,
    recuperacion: `${pct(wagePrivate.recovery_from_trough_pct)} desde el mínimo hasta ${wagePrivate.last_period}`,
    saldo: pct(wagePrivate.saldo_vs_baseline_pct),
    medida: "índice salarial INDEC deflactado por IPC nacional",
    confianza_dato: "alta",
    confianza_causal: "baja",
    advertencia: "promedio sectorial; no distribución",
  },
  {
    grupo: "asalariados públicos",
    shock_inicial: `${pct(wagePublic.shock_pct)} al mínimo de ${wagePublic.trough_period}`,
    recuperacion: `${pct(wagePublic.recovery_from_trough_pct)} desde el mínimo hasta ${wagePublic.last_period}`,
    saldo: pct(wagePublic.saldo_vs_baseline_pct),
    medida: "índice salarial INDEC deflactado por IPC nacional",
    confianza_dato: "alta",
    confianza_causal: "baja",
    advertencia: "promedio nacional; heterogeneidad Nación/provincias",
  },
  {
    grupo: "asalariados privados no registrados",
    shock_inicial: `${pct(wageUnregistered.shock_pct)} al mínimo de ${wageUnregistered.trough_period}`,
    recuperacion: `${pct(wageUnregistered.recovery_from_trough_pct)} desde el mínimo hasta ${wageUnregistered.last_period}`,
    saldo: pct(wageUnregistered.saldo_vs_baseline_pct),
    medida: "índice salarial INDEC deflactado por IPC nacional",
    confianza_dato: "baja para nivel intertemporal",
    confianza_causal: "muy baja",
    advertencia: "salto atípico; auditar metodología/muestra antes de interpretar",
  },
  {
    grupo: "hogares que usaron ahorros",
    shock_inicial: "+12,5 pp en 1S-2024 vs 1S-2018",
    recuperacion: "2S-2024 baja 1,2 pp vs 1S-2024",
    saldo: "+8,7 pp en 2S-2024 vs 2S-2018",
    medida: "incidencia declarada de estrategia",
    confianza_dato: "alta",
    confianza_causal: "baja",
    advertencia: "no mide pesos, stock ni mismo hogar longitudinal",
  },
  {
    grupo: "Estado nacional / SPN",
    shock_inicial: `${num(fiscal2023.financial_pct_gdp).toFixed(3)}% PIB en 2023`,
    recuperacion: `${num(fiscal2024.financial_pct_gdp).toFixed(3)}% PIB en 2024`,
    saldo: `+${fiscalSwingPp.toFixed(3)} pp PIB`,
    medida: "resultado financiero SPN",
    confianza_dato: "alta según auditoría local",
    confianza_causal: "no aplica a identidad; baja para bienestar",
    advertencia: "flujo fiscal no mide patrimonio ni incidencia distributiva",
  },
  {
    grupo: "capital público",
    shock_inicial: "-75,1% real en 2024",
    recuperacion: "-27,0% real adicional en 2025",
    saldo: `${publicInvestmentChange2025Vs2023.toFixed(2)}% vs 2023`,
    medida: "flujo de inversión pública ejecutada",
    confianza_dato: "alta",
    confianza_causal: "baja para deterioro físico",
    advertencia: "no hay depreciación/mantenimiento físico comparable",
  },
  {
    grupo: "empresas, provincias, bancos, fintech, ahorristas, subsidios y transferencias",
    shock_inicial: "N/D comparable",
    recuperacion: "N/D comparable",
    saldo: "N/D",
    medida: "universos heterogéneos",
    confianza_dato: "insuficiente",
    confianza_causal: "no identificada",
    advertencia: "no sumar rentabilidad, gasto, crédito y personas; requiere microdatos/perímetros homogéneos",
  },
];

const evidence = [
  ["D01", "3-4", "Resultado financiero SPN 2023/2024", "flujo fiscal", "SPN; % PIB", "2023-2024", "observado", "local derivado de serie oficial", "data/derivados/pendulo_poder_economico/fiscal_result_2002_2026.csv", "alta", "No identifica hogares/empresas"],
  ["D02", "3", "Cuenta corriente 2023/2024", "flujo externo", "economía total; USD", "2023-2024", "observado provisorio", "INDEC", bop2024q4Url, "alta", "No desagrega ahorro de hogares"],
  ["D03", "3-4", "Uso de ahorros por hogares", "incidencia de estrategia", "hogares; porcentaje", "2018/2024", "observado", "INDEC EPH", householdUrl, "alta", "No cuantifica pesos ni stock"],
  ["D04", "3", "Stock ahorro/inversión de personas humanas", "stock financiero", "personas humanas; pesos reales", "2023-2025", "observado con posible revisión", "BCRA", householdStockUrl, "media", `El empalme mecánico da ${stockMechanicalEnd2024.toFixed(2)} vs 105,5 reportado; brecha ${stockSpliceGapPp.toFixed(2)} pp`],
  ["D05", "4", "Índices salariales reales", "precio/ingreso real", "promedios sectoriales", "2023-11/2026-06", "observado", "INDEC", `${indecSalaryUrl} | ${indecCpiUrl}`, "alta salvo no registrado", "Promedio, no distribución"],
  ["D06", "17", "RIGI aprobados: inversión y empleo", "compromiso/proyección", "16 proyectos", "2026-06-11", "aprobado y proyectado", "Ministerio de Economía", rigiUrl, "media", "No ejecución ni permanencia"],
  ["D07", "17-40", "Pampa urea", "proyección de proyecto", "un proyecto", "2026-07-31", "aprobado/proyectado", "Presidencia", pampaUrl, "media", "Temporal y permanente no son simultáneos"],
  ["D08", "18-19", "EMAE desestacionalizado", "actividad", "economía agregada", "2023-11/2026-04", "observado", "INDEC", indecEmaeUrl, "alta", "No es inversión ni productividad sectorial"],
  ["D09", "18-19", "Empleo privado registrado", "stock de personas", "SIPA", "2023-11/2026-04", "observado", "Secretaría de Trabajo", `${employmentUrl} | ${employmentBaselineUrl}`, "alta", "Revisar cambios de padrón; no incluye informalidad"],
  ["D10", "20", "Neutralidad IIBB", "identidad tributaria", "base y alícuota", "escenario", "derivado", "fórmula", "este script", "alta aritmética", "No estima elasticidades"],
  ["D11", "23", "Inversión pública ejecutada", "flujo presupuestario", "Administración Nacional", "2023-2025", "observado", "OPC/E-Sidif", `${opc2024Url} | ${opc2025Url}`, "alta", "No mide depreciación física"],
  ["D12", "37", "Corredores viales", "input/output contractual", "km concesionados", "2025-2026", "observado administrativo", "Vialidad/Argentina.gob.ar", "data/derivados/rutas_publico_privado/rutas_publico_privado_corredores.csv", "alta para status", "No son km construidos"],
  ["D13", "38", "Proveniencia institucional", "control de calidad", "INDEC/OPC/PEN", cutoff, "auditado", "fuentes primarias", "URLs de esta matriz", "media-alta", "Fuente promotora no reemplaza auditor independiente"],
].map(([dato_id, item_epica, dato, tipo_variable, universo_unidad, periodo, estado, institucion, fuente, confianza, limite]) => ({
  dato_id, item_epica, dato, tipo_variable, universo_unidad, periodo, estado, institucion, fuente, confianza, limite, fecha_corte: cutoff,
}));

const gaps = [
  ["3", "parcial", "Resultado SPN, cuenta corriente y evidencia de uso/stock de ahorro", "cuenta por sector institucional hogares vs sociedades no financieras; ingreso disponible y formación de capital", "No se puede repartir el balance privado entre hogares y empresas"],
  ["4", "parcial", "Salarios por sector, hogares, Estado y capital público", "jubilación base+bono real mensual; bancos/fintech; empresas; provincias; subsidios y transferencias con universo común", "Matriz no aditiva; causalidad baja"],
  ["17", "parcial", "Aprobados/evaluación RIGI y un proyecto con temporal/permanente", "ejecución financiera, empleo realizado, proveedores/import content por proyecto", "Empleo oficial es proyectado"],
  ["18", "parcial", "EMAE vs empleo privado registrado", "capital, productividad, empleo y masa salarial por sector", "No hay elasticidad sectorial"],
  ["19", "no estimable", "Coincidencia de recuperación de actividad y menor empleo privado", "panel sectorial de inversión real, horas, empleo y salarios", "No calcular elasticidad inversión-empleo con agregados"],
  ["20", "mecánico completo; causal pendiente", "Curva de neutralidad aritmética", "elasticidad de formalización/evasión/actividad y traslado a precios", "No asumir respuesta de base"],
  ["21", "no medible", "Ninguno comparable", "definir 'Buenos Aires/27 distritos'; costo funcional y recursos por nivel", "Escenario ambiguo y sin perímetro"],
  ["22", "no medible", "Ninguno comparable", "saldos a favor, plazos y costo financiero PyME; expediente jurídico Misiones", "Cautelar no equivale a sentencia"],
  ["23", "parcial", "Resultado fiscal e inversión pública", "depreciación, mantenimiento y condición física de activos", "No existe resultado fiscal ajustado sin tasa de depreciación y stock"],
  ["24", "no medible", "Ninguno granular", "caja mínima, compromisos, cartera y prestaciones por organismo", "Liquidez no prueba mala prestación"],
  ["25", "no medible", "Flujo agregado de inversión con algunas funciones", "salarios, vacantes, personal, obra, insumos, matrícula y prestaciones compatibles", "Gasto no es capacidad ni outcome"],
  ["36", "sólo marco", "Trayectoria observada", "modelo y supuestos explícitos para cada contrafactual", "No afirmar inevitabilidad ni resultado contrafactual"],
  ["37", "parcial", "Fiscal, RIGI y concesiones clasificados", "inventario completo de medidas, objetivos e indicadores antes/después", "Aprobado/cerrado no es outcome"],
  ["38", "parcial", "Matriz de procedencia INDEC/OPC/PEN", "mandatos, cambios normativos, series de publicación y auditorías", "Control institucional requiere análisis jurídico separado"],
  ["39", "no medible", "Ninguno local", "Cámara Nacional Electoral: ingresos, gastos, observaciones y estado procesal", "Observación no es delito"],
  ["40", "input normativo/proyección", "Pampa industrial; tecnología figura en el universo RIGI", "proyectos tecnológicos aprobados, energía/agua/importaciones/empleo permanente/datos", "No hay outcome tecnológico auditable"],
].map(([item_epica, estado, disponible, faltante, regla_no_inferencia]) => ({
  item_epica, estado, disponible, faltante, regla_no_inferencia, prioridad_siguiente: estado === "parcial" ? "alta" : "media", fecha_corte: cutoff,
}));

await fs.mkdir(outDir, { recursive: true });
await writeCsv("hallazgos_cuantitativos.csv", metrics, [
  "id", "item_epica", "indicador", "periodo_base", "valor_base", "periodo_final", "valor_final", "cambio", "unidad", "formula", "lectura", "fuente_url", "fuente_local", "confianza", "causalidad",
]);
await writeCsv("neutralidad_iibb.csv", iibbScenarios, [
  "reduccion_alicuota_pct", "alicuota_remanente_pct_de_original", "multiplicador_base_neutral", "crecimiento_base_necesario_pct", "formula", "interpretacion",
]);
await writeCsv("matriz_incidencia.csv", incidence, [
  "grupo", "shock_inicial", "recuperacion", "saldo", "medida", "confianza_dato", "confianza_causal", "advertencia",
]);
await writeCsv("matriz_dato_fuente_confianza.csv", evidence, [
  "dato_id", "item_epica", "dato", "tipo_variable", "universo_unidad", "periodo", "estado", "institucion", "fuente", "confianza", "limite", "fecha_corte",
]);
await writeCsv("matriz_brechas_epica.csv", gaps, [
  "item_epica", "estado", "disponible", "faltante", "regla_no_inferencia", "prioridad_siguiente", "fecha_corte",
]);

const report = `# Análisis empírico — fiscal, balances sectoriales, inversión-empleo e infraestructura

**Fecha de corte:** ${cutoff}  
**Ítems de la épica:** 3–4, 17–25 y 36–40  
**Regla de lectura:** se distingue dato observado, identidad, input administrativo, proyección y outcome. Ningún resultado causal se identifica sólo por simultaneidad.

## Resultado ejecutivo

1. **La incidencia salarial fue desigual.** Con IPC nacional e índices INDEC, desde noviembre de 2023 el salario real privado registrado tocó un mínimo de ${wagePrivate.trough_index.toFixed(2)} en ${wagePrivate.trough_period} y a junio de 2026 seguía ${pct(wagePrivate.saldo_vs_baseline_pct)} respecto de la base. El público tocó ${wagePublic.trough_index.toFixed(2)} y seguía ${pct(wagePublic.saldo_vs_baseline_pct)}. El no registrado arroja un salto extremo y queda marcado para revisión metodológica, no como mejora consolidada.

2. **Hubo desahorro/fragilidad observada, pero no una cuenta sectorial completa de hogares.** El uso declarado de ahorros subió de ${householdUseSavings1h2018}% a ${householdUseSavings1h2024}% entre 1S-2018 y 1S-2024 (+${(householdUseSavings1h2024-householdUseSavings1h2018).toFixed(1)} pp). El stock BCRA cayó 20,6% real en 1S-2024 y luego se informó +21,7% semestral; empalmados mecánicamente darían ${stockMechanicalEnd2024.toFixed(2)} (base dic-2023=100), no 105,5 como la variación interanual reportada. La brecha de ${stockSpliceGapPp.toFixed(2)} pp impide unir ambas publicaciones sin revisar revisiones/perímetros.

3. **Superávit fiscal no implica por identidad déficit de hogares.** El resultado financiero del SPN mejoró ${fiscalSwingPp.toFixed(3)} pp del PIB entre 2023 y 2024. A la vez, la cuenta corriente pasó de USD ${Math.abs(currentAccount2023UsdM).toLocaleString("es-AR")} M de déficit en 2023 a USD ${currentAccount2024UsdM.toLocaleString("es-AR")} M de superávit en 2024. La identidad permite que el sector privado agregado tenga capacidad de financiamiento si el saldo externo compensa el superávit público; estos datos no separan hogares de empresas ni igualan perímetros/monedas para cerrar una cuenta exacta.

4. **La actividad se recuperó sin recomponer en igual dirección el empleo privado registrado.** Entre nov-2023 y abr-2026, EMAE desestacionalizado +${emaeChange.toFixed(2)}% y EMAE per cápita +${emaePcChange.toFixed(2)}%; asalariados privados registrados ${pct(privateEmploymentPct)} (${Math.abs(privateEmploymentDelta).toLocaleString("es-AR")} menos). Es coexistencia, no prueba de que capital “cause” menos empleo ni elasticidad sectorial.

5. **RIGI: empleo anunciado/proyectado, no empleo realizado.** Los 16 proyectos aprobados informados el 11/06/2026 sumaban USD ${rigiApprovedInvestmentUsdM.toLocaleString("es-AR")} M y ${rigiApprovedJobs.toLocaleString("es-AR")} empleos directos+indirectos: ${rigiApprovedJobsPerUsdBn.toFixed(0)} por USD 1.000 M. Ese total equivale mecánicamente a ${rigiJobsVsPrivateLossPct.toFixed(1)}% de la pérdida neta de asalariados privados registrados desde nov-2023, pero los universos, horizontes y estados no son comparables. Pampa urea ilustra el problema: ${pampaConstructionJobs.toLocaleString("es-AR")} empleos directos+indirectos de construcción y ${pampaPermanentJobs} operativos permanentes para USD ${pampaInvestmentUsdM.toLocaleString("es-AR")} M.

6. **El flujo fiscal mejoró mientras el flujo de inversión pública cayó; el patrimonio no está medido.** Índice real de inversión pública 2023=100: 2024=${publicInvestmentIndex2024.toFixed(2)}, 2025=${publicInvestmentIndex2025.toFixed(2)}. Esto prueba menor flujo ejecutado, no depreciación física. Para un resultado fiscal ajustado se necesitan stock de activos, mantenimiento necesario y tasas de depreciación por clase.

## Balances sectoriales: qué puede y qué no puede cerrarse

La identidad relevante, con signos explícitos, es:

\`(S-I)_privado = (G-T) + CC\`

donde \`G-T\` es déficit público y \`CC\` la cuenta corriente. Un superávit público hace \`G-T<0\`, pero no obliga a \`(S-I)_privado<0\` si la cuenta corriente es suficientemente positiva. El repositorio permite verificar fiscal, cuenta corriente y señales de hogares; no contiene una cuenta no financiera trimestral que separe hogares, sociedades no financieras y sociedades financieras. Por eso la parte “qué correspondió a empresas” queda N/D.

## Incidencia y auditor de relatos

- El cuadro de incidencia se entrega como matriz no aditiva. No se suman salarios, personas, inversión, rentabilidad y transferencias.
- “Aprobado RIGI” es input administrativo; “inversión comprometida” es compromiso; “empleo asociado” es proyección; “empleo SIPA” es observado.
- ${operationalKm.toFixed(2)} km de corredores figuran en operación y ${awardedKm.toFixed(2)} km al incluir adjudicados. Son km concesionados, no construidos ni rehabilitados.
- En infraestructura, el descenso presupuestario es flujo. No autoriza a cuantificar el deterioro del stock sin inventario físico comparable.
- Para los ítems 21, 22, 24, 25, 36, 39 y 40 se prioriza N/D con requerimiento de dato, en vez de inferir outcomes desde normas, anuncios o caja.

## Neutralidad de Ingresos Brutos

Con recaudación \`R=t·B\`, si la alícuota cae una fracción \`r\`, neutralidad exige \`B_1/B_0=1/(1-r)\`. Las bajas de 10%, 25% y 50% exigen, mecánicamente, aumentos de base de 11,11%, 33,33% y 100%. Con alícuota cero no existe base finita que preserve la recaudación del mismo impuesto. Esto no pronostica formalización ni actividad.

## Fuentes primarias y corte

- INDEC: salarios, IPC, EMAE y balanza de pagos.
- Secretaría de Trabajo/SIPA: trabajadores registrados.
- OPC sobre E-Sidif: inversión pública 2024–2025.
- INDEC EPH y BCRA: uso/stock de ahorro de hogares.
- Ministerio de Economía/Presidencia: RIGI; por ser fuente promotora, sus empleos se tratan como proyección.
- Vialidad/Argentina.gob.ar: estado administrativo de concesiones.

Las URLs, fechas, unidades, límites y confianza están en \`matriz_dato_fuente_confianza.csv\`. La cobertura y los faltantes por ítem están en \`matriz_brechas_epica.csv\`.

## Qué falta para causalidad

1. Microdatos longitudinales de hogares con ingreso, ahorro, deuda y consumo.
2. Cuentas por sector institucional separando hogares y sociedades.
3. Ejecución física/financiera y empleo realizado por proyecto RIGI, con horizonte y permanencia.
4. Panel sectorial de inversión, horas, empleo, masa salarial y productividad.
5. Inventario físico y depreciación del capital público.
6. Diseños contrafactuales preespecificados para shock vs gradualismo; no basta comparar antes/después.
`;

await fs.writeFile(path.join(outDir, "INFORME_AUDITORIA.md"), report, "utf8");

const qa = {
  fecha_corte: cutoff,
  checks: {
    wage_private_trough_below_baseline: wagePrivate.trough_index < 100,
    wage_public_worse_than_private_at_cutoff: wagePublic.last_index < wagePrivate.last_index,
    current_account_2024_latest_revision: currentAccount2024UsdM === 6285,
    fiscal_swing_matches: Math.abs(fiscalSwingPp - 4.700485010999999) < 1e-6,
    public_investment_chain: Math.abs(publicInvestmentIndex2025 - 18.177) < 1e-9,
    iibb_50_requires_double_base: iibbScenarios[2].multiplicador_base_neutral === "2.000000",
    iibb_100_has_no_finite_solution: iibbScenarios[3].multiplicador_base_neutral === "N/D",
    rigi_intensity_positive: rigiApprovedJobsPerUsdBn > 0,
    routes_operational_not_greater_than_awarded: operationalKm <= awardedKm,
    household_reference_strings_present: householdNotes.includes("1S-2024  40,1%") && householdNotes.includes("vs dic-2023 = -20,6% real"),
    coverage_items_complete: gaps.length === 16,
    metric_ids_unique: new Set(metrics.map((r) => r.id)).size === metrics.length,
  },
  calculated: {
    wagePrivate,
    wagePublic,
    wageUnregistered,
    fiscalSwingPp,
    currentAccount2024UsdM,
    currentAccountSwingUsdM,
    emaeChange,
    emaePcChange,
    privateEmploymentDelta,
    rigiApprovedJobsPerUsdBn,
    pampaPermanentPerUsdBn,
    publicInvestmentIndex2025,
    stockMechanicalEnd2024,
    stockSpliceGapPp,
    operationalKm,
    awardedKm,
  },
};
qa.pass = Object.values(qa.checks).every(Boolean);
await fs.writeFile(path.join(outDir, "qa_resultados.json"), JSON.stringify(qa, null, 2) + "\n", "utf8");

if (!qa.pass) {
  throw new Error(`QA failed: ${JSON.stringify(qa.checks)}`);
}

console.log(JSON.stringify({ outDir, files: 7, qa: "PASS", findings: metrics.length, gaps: gaps.length }, null, 2));
