import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..", "..");
const outputCsv = path.join(here, "matriz_evidencia.csv");
const bundledNodeModules = process.env.CODEX_WORKSPACE_NODE_MODULES
  ?? "C:\\Users\\miyur\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const nodeModulesJunction = path.join(here, "node_modules");
let createdJunction = false;
try {
  await fs.lstat(nodeModulesJunction);
} catch {
  await fs.symlink(bundledNodeModules, nodeModulesJunction, "junction");
  createdJunction = true;
}
const { Workbook } = await import("@oai/artifact-tool");

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
  const headers = rows.shift().map((x, i) => (i === 0 ? x.replace(/^\uFEFF/, "") : x));
  return rows.filter((r) => r.some((x) => x !== "")).map((r) =>
    Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""]))
  );
}

async function readCsv(rel, delimiter = ",", encoding = "utf8") {
  const bytes = await fs.readFile(path.join(root, rel));
  const text = new TextDecoder(encoding).decode(bytes);
  return parseDelimited(text, delimiter);
}

function num(value) {
  if (typeof value === "number") return value;
  return Number(String(value).replace(/\./g, "").replace(",", "."));
}

function approx(actual, expected, tolerance = 1e-6, label = "valor") {
  if (!Number.isFinite(actual) || Math.abs(actual - expected) > tolerance) {
    throw new Error(`${label}: esperado ${expected}, obtenido ${actual}`);
  }
}

function pctChange(a, b) {
  return (b / a - 1) * 100;
}

function csvEscape(value) {
  if (value === null || value === undefined) return "";
  const s = String(value);
  return /[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

const moraHogares = await readCsv("Mora/05_ANALISIS_Y_CALCULOS/datos/morosidad_hogares.csv");
const moraPnfc = await readCsv("Mora/05_ANALISIS_Y_CALCULOS/datos/morosidad_pnfc.csv");
const inclusion = await readCsv("Mora/05_ANALISIS_Y_CALCULOS/datos/bcra_inclusion_prestamos_personales_2023_2025.csv");
const sistema = await readCsv("Mora/05_ANALISIS_Y_CALCULOS/datos/bcra_sistema_financiero_2023_2026.csv");
const bancosResumen = await readCsv("Mora/05_ANALISIS_Y_CALCULOS/datos/bcra_panel_bancos_resumen_2023_2026.csv");
const ipc = await readCsv("data/fuentes/tasas/indec/serie_ipc_divisiones.csv", ";", "windows-1252");

const bankNov23 = moraHogares.find((r) => r.date === "2023-11-01");
const bankMay26 = moraHogares.find((r) => r.date === "2026-05-01");
const pnfcNov23 = moraPnfc.find((r) => r.date === "2023-11-01");
const pnfcFeb26 = moraPnfc.find((r) => r.date === "2026-02-01");
const covJul24 = inclusion.find((r) => r.periodo === "2024-07");
const covDec25 = inclusion.find((r) => r.periodo === "2025-12");
const sysDec23 = sistema.find((r) => r.corte_publicacion === "2023-12");
const sysDec25 = sistema.find((r) => r.corte_publicacion === "2025-12");
const sysMay26 = sistema.find((r) => r.corte_publicacion === "2026-05");
const panelMay26 = bancosResumen.find((r) => r.corte_publicacion === "2026-05");

const mean = (xs) => xs.reduce((a, b) => a + b, 0) / xs.length;
const mora1h24 = mean(moraHogares
  .filter((r) => r.date >= "2024-01-01" && r.date <= "2024-06-01")
  .map((r) => Number(r.households_personal_cards_pct)));
const mora2h25 = mean(moraHogares
  .filter((r) => r.date >= "2025-07-01" && r.date <= "2025-12-01")
  .map((r) => Number(r.households_personal_cards_pct)));

function ipcIndex(code, period) {
  const r = ipc.find((x) => x.Region === "Nacional" && x.Codigo === code && x.Periodo === period);
  if (!r) throw new Error(`IPC faltante: ${code} ${period}`);
  return num(r.Indice_IPC);
}

const ipcChanges = Object.fromEntries([
  ["general", "0"],
  ["alimentos", "01"],
  ["vivienda_servicios", "04"],
  ["salud", "06"],
  ["transporte", "07"],
  ["educacion", "10"],
  ["nucleo", "Núcleo"],
  ["regulados", "Regulados"],
].map(([name, code]) => [name, pctChange(ipcIndex(code, "202312"), ipcIndex(code, "202607"))]));

// Controles de anclaje contra las cifras publicadas en los artefactos locales.
approx(Number(bankNov23.households_pct), 2.6950246175325243, 1e-9, "mora hogares nov-2023");
approx(Number(bankMay26.households_pct), 12.795302382570279, 1e-9, "mora hogares may-2026");
approx(Number(pnfcFeb26.pnfc_total_pct), 26.9, 1e-9, "mora PNFC feb-2026");
approx(num(covDec25.cobertura_personales_pct_poblacion_adulta), 32.19603, 1e-6, "cobertura personales dic-2025");
approx(mora1h24, 2.602134850505409, 1e-9, "mora P+T 1S-2024");
approx(mora2h25, 8.540749991346834, 1e-9, "mora P+T 2S-2025");
approx(ipcChanges.general, 241.79837994661034, 1e-6, "IPC general dic-2023/jul-2026");

const S = {
  eph: {
    org: "INDEC",
    title: "Estrategias de manutención. ¿Cómo organizan su economía los hogares argentinos?",
    url: "https://www.indec.gob.ar/ftp/cuadros/publicaciones/dosier_estrategias_manutencion_2025.pdf",
    local: "data/fuentes/hogares/indec/indec_estrategias_manutencion_2025.pdf",
  },
  poverty: {
    org: "INDEC",
    title: "Incidencia de la pobreza y la indigencia en 31 aglomerados urbanos",
    url: "https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-46-152",
    local: "data/fuentes/morosidad/metodologia/AUDITORIA_CAUSAS_MORA_POBREZA_DESEMPLEO.md",
  },
  iif: {
    org: "BCRA",
    title: "Informe de Inclusión Financiera, segundo semestre de 2025",
    url: "https://www.bcra.gob.ar/publicaciones/informe-de-inclusion-financiera-segundo-semestre-de-2025/",
    local: "Mora/03_DATOS_OFICIALES/BCRA/Anexo_Inclusion_Financiera_abril_2026.xlsx",
  },
  banks: {
    org: "BCRA",
    title: "Informe sobre Bancos, mayo de 2026 y series oficiales",
    url: "https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-junio-de-2026/",
    local: "Mora/05_ANALISIS_Y_CALCULOS/datos/morosidad_hogares.csv",
  },
  pnfc: {
    org: "BCRA",
    title: "Informe de Proveedores No Financieros de Crédito, junio de 2026",
    url: "https://www.bcra.gob.ar/publicaciones/informe-de-proveedores-no-financieros-de-credito-junio-de-2026/",
    local: "Mora/05_ANALISIS_Y_CALCULOS/datos/morosidad_pnfc.csv",
  },
  ipc: {
    org: "INDEC",
    title: "Índice de precios al consumidor. Series por divisiones, nacional",
    url: "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31",
    local: "data/fuentes/tasas/indec/serie_ipc_divisiones.csv",
  },
  transfers: {
    org: "Ministerio de Capital Humano",
    title: "AUH y Tarjeta Alimentar: cobertura normativa de la CBA en 2024",
    url: "https://www.argentina.gob.ar/node/450359",
    local: "data/fuentes/manual_recovery_v96_final/capital_humano_auh_alimentar_cba_2024_web_snapshot.pdf",
  },
};

const headers = [
  "evidence_id", "item", "status", "period", "universe", "measure_type", "metric",
  "value_numeric", "value_text", "unit", "comparison", "formula", "classification",
  "confidence", "source_organization", "source_title", "source_url", "local_source", "limitations",
];
const evidence = [];

function add({ id, item, status = "hallazgo", period, universe, measure, metric, value = null,
  valueText = "", unit = "", comparison = "", formula = "", classification,
  confidence, source, limitations }) {
  evidence.push({
    evidence_id: id, item, status, period, universe, measure_type: measure, metric,
    value_numeric: value === null ? "" : Number(value.toFixed(6)), value_text: valueText, unit,
    comparison, formula, classification, confidence,
    source_organization: source.org, source_title: source.title, source_url: source.url,
    local_source: source.local, limitations,
  });
}

add({ id: "H01_AHORRO", item: 1, period: "2025-S1", universe: "Hogares de 31 aglomerados urbanos",
  measure: "incidencia declarada", metric: "Hogares que gastaron ahorros", value: 37.4, unit: "% de hogares",
  comparison: "40,1% en 2024-S1; 38,9% en 2024-S2", formula: "estimación ponderada EPH publicada",
  classification: "observado", confidence: "alta", source: S.eph,
  limitations: "Respuesta multiopción; no mide pesos retirados ni permite identificar por sí sola hogares sin otras estrategias. PDF p.4 y p.13." });
add({ id: "H01_DESCAP", item: 1, period: "2025-S1", universe: "Hogares de 31 aglomerados urbanos",
  measure: "unión publicada", metric: "Usó ahorros o vendió pertenencias", value: 40.8, unit: "% de hogares",
  comparison: "bajo 42,8%; medio 40,6%; alto 37,1%", formula: "unión calculada por INDEC a partir de microdatos EPH",
  classification: "observado", confidence: "alta", source: S.eph,
  limitations: "No sumar con préstamos o cuotas: las estrategias pueden superponerse. PDF p.7 y p.9." });
add({ id: "H01_PRESTAMOS", item: 1, period: "2025-S1", universe: "Hogares de 31 aglomerados urbanos",
  measure: "unión publicada", metric: "Solicitó préstamos a instituciones o familiares/amigos", value: 25.5, unit: "% de hogares",
  comparison: "bajo 30,4%; medio 23,9%; alto 18,6%", formula: "unión calculada por INDEC a partir de microdatos EPH",
  classification: "observado", confidence: "alta", source: S.eph,
  limitations: "No equivale a personas deudoras, saldo de deuda ni mora; no sumar entre fuentes. PDF p.7 y p.8." });
add({ id: "H01_CUOTAS", item: 1, period: "2025-S1", universe: "Hogares de 31 aglomerados urbanos",
  measure: "incidencia declarada", metric: "Compró en cuotas o fiado con tarjeta/libreta", value: 50.9, unit: "% de hogares",
  comparison: "22,0% en 2003-S2", formula: "estimación ponderada EPH publicada",
  classification: "observado", confidence: "alta", source: S.eph,
  limitations: "Financiación de compras no implica necesariamente estrés ni mora; respuesta multiopción. PDF p.4." });
add({ id: "H02_RUNWAY_GAP", item: 2, status: "brecha", period: "corte 2026-08-31", universe: "Hogares tipo",
  measure: "modelo requerido", metric: "Mes de agotamiento del ahorro por hogar", valueText: "No disponible",
  unit: "mes", formula: "ceil(ahorro inicial / déficit corriente mensual)", classification: "no disponible",
  confidence: "alta sobre la brecha", source: S.eph,
  limitations: "Faltan microdatos conjuntos y comparables de ingreso neto, gasto esencial, alquiler, ahorro inicial, servicio de deuda y CFTEA contractual." });

add({ id: "H05_POBREZA", item: 5, period: "2024-S1 a 2025-S2", universe: "Personas de 31 aglomerados urbanos",
  measure: "incidencia de pobreza", metric: "Cambio de pobreza", value: 28.2 - 52.9, unit: "puntos porcentuales",
  comparison: "52,9% a 28,2%", formula: "28,2 - 52,9", classification: "observado",
  confidence: "alta", source: S.poverty,
  limitations: "Personas; no mide patrimonio, deuda ni las mismas unidades que mora. Los valores se trazan en la auditoría causal local a publicaciones INDEC." });
add({ id: "H05_MORA_DIVERGE", item: 5, period: "2024-S1 a 2025-S2", universe: "Saldo bancario de personales + tarjetas de familias",
  measure: "promedio semestral de cartera irregular", metric: "Cambio de mora mientras cayó la pobreza", value: mora2h25 - mora1h24,
  unit: "puntos porcentuales", comparison: `${mora1h24.toFixed(3)}% a ${mora2h25.toFixed(3)}% (${(mora2h25 / mora1h24).toFixed(2)} veces)`,
  formula: "promedio(meses 2025-S2) - promedio(meses 2024-S1)", classification: "observado",
  confidence: "alta descriptiva", source: S.banks,
  limitations: "Divergencia agregada con denominadores distintos; no identifica transición individual ni causalidad." });

add({ id: "C12_COBERTURA_PERSONALES", item: 12, period: "2025-12", universe: "Personas adultas con préstamo personal reportable en CENDEU",
  measure: "cobertura", metric: "Personas con préstamo personal", value: num(covDec25.cobertura_personales_pct_poblacion_adulta), unit: "% de población adulta",
  comparison: `${num(covJul24.cobertura_personales_pct_poblacion_adulta).toFixed(2)}% en 2024-07; +${(num(covDec25.cobertura_personales_pct_poblacion_adulta) - num(covJul24.cobertura_personales_pct_poblacion_adulta)).toFixed(2)} pp dentro del régimen`,
  formula: "personas informadas / población adulta", classification: "observado", confidence: "alta", source: S.iif,
  limitations: "Desde julio de 2024 el umbral reportable es $25.000; junio-julio no es comparable. No equivale a hogares ni a mora." });
add({ id: "C12_MORA_BANCARIA", item: 12, period: "2023-11 a 2026-05", universe: "Saldo financiado a hogares por entidades financieras",
  measure: "cartera irregular / financiaciones", metric: "Mora bancaria de hogares", value: Number(bankMay26.households_pct), unit: "% del saldo",
  comparison: `${Number(bankNov23.households_pct).toFixed(2)}% a ${Number(bankMay26.households_pct).toFixed(2)}%; +${(Number(bankMay26.households_pct) - Number(bankNov23.households_pct)).toFixed(2)} pp`,
  formula: "cartera irregular de familias / financiaciones a familias", classification: "observado", confidence: "alta", source: S.banks,
  limitations: "Saldo, no personas ni nuevos morosos; cambia también por originación, pagos, castigos, ventas y reclasificación." });
add({ id: "C12_MORA_PNFC", item: 12, period: "2023-11 a 2026-02", universe: "Saldo de proveedores no financieros de crédito",
  measure: "cartera >90 días / cartera", metric: "Mora PNFC total", value: Number(pnfcFeb26.pnfc_total_pct), unit: "% del saldo",
  comparison: `${Number(pnfcNov23.pnfc_total_pct).toFixed(1)}% a ${Number(pnfcFeb26.pnfc_total_pct).toFixed(1)}%; +${(Number(pnfcFeb26.pnfc_total_pct) - Number(pnfcNov23.pnfc_total_pct)).toFixed(1)} pp`,
  formula: "saldo PNFC con mora >90 días / saldo PNFC", classification: "observado", confidence: "alta", source: S.pnfc,
  limitations: "Universo y definición no idénticos a bancos; no sumar ambos porcentajes ni convertirlos en personas." });
add({ id: "C13_SUBSISTENCIA_PROXY", item: 13, period: "2025-S1", universe: "Hogares de 31 aglomerados urbanos",
  measure: "estrategia de manutención", metric: "Financiación de compras corrientes en cuotas o fiado", value: 50.9, unit: "% de hogares",
  comparison: "Proxy de uso; no monto", formula: "estimación ponderada EPH publicada", classification: "proxy", confidence: "media", source: S.eph,
  limitations: "La pregunta identifica estrategia para manutención, pero no separa gasto esencial, durable, pago mínimo, refinanciación ni servicio deuda/ingreso." });
add({ id: "C14_INCLUSION_EXPANSION", item: 14, period: "2024-07 a 2025-12", universe: "Personas adultas con préstamo personal reportable en CENDEU",
  measure: "cambio de cobertura", metric: "Expansión de acceso a personales dentro del mismo régimen", value: num(covDec25.cobertura_personales_pct_poblacion_adulta) - num(covJul24.cobertura_personales_pct_poblacion_adulta),
  unit: "puntos porcentuales", comparison: "23,10% a 32,20%", formula: "cobertura dic-2025 - cobertura jul-2024",
  classification: "observado", confidence: "alta", source: S.iif,
  limitations: "No enlaza cada nuevo prestatario con tasa, score y resultado a 3/6/12 meses; no demuestra monetización de exclusión." });

add({ id: "C15_ROA", item: 15, period: "2023-12 a 2025-12", universe: "Sistema financiero agregado AA000",
  measure: "rentabilidad contable", metric: "ROA", value: num(sysDec25.roa_pct), unit: "%",
  comparison: `${num(sysDec23.roa_pct).toFixed(2)}% a ${num(sysDec25.roa_pct).toFixed(2)}%`, formula: "indicador BCRA agregado",
  classification: "observado", confidence: "alta", source: S.banks,
  limitations: "No identifica rentabilidad de préstamos personales ni transferencia hogar→banco." });
add({ id: "C15_IRREGULARIDAD", item: 15, period: "2023-12 a 2026-03 (publicación 2026-05)", universe: "Sistema financiero agregado AA000",
  measure: "calidad de cartera", metric: "Cartera irregular de consumo", value: num(sysMay26.cartera_irregular_consumo_pct), unit: "%",
  comparison: `${num(sysDec23.cartera_irregular_consumo_pct).toFixed(2)}% a ${num(sysMay26.cartera_irregular_consumo_pct).toFixed(2)}%`, formula: "indicador BCRA agregado",
  classification: "observado", confidence: "alta", source: S.banks,
  limitations: "El corte local 2026-05 porta indicadores a marzo de 2026; no confundir con mora de familias a mayo." });
add({ id: "C15_DISTRIBUCION_ENTIDADES", item: 15, period: "publicación 2026-05", universe: "73 entidades financieras informadas",
  measure: "conteo de signo del resultado estimado", metric: "Entidades con resultado estimado positivo", value: Number(panelMay26.resultado_estimado_positivo), unit: "entidades",
  comparison: `${panelMay26.resultado_estimado_negativo} negativas; 0 cero`, formula: "conteo por entidad de resultado integral menos ORI",
  classification: "observado", confidence: "media-alta", source: S.banks,
  limitations: "Sumas por entidad no consolidadas; signo contable total, no desempeño del producto personal." });
add({ id: "C16_FGS_GAP", item: 16, status: "brecha", period: "corte 2026-08-31", universe: "Esquema hipotecario propuesto financiado con FGS",
  measure: "contrato y asignación de riesgo", metric: "Spread neto y portador final del riesgo", valueText: "No disponible", unit: "",
  formula: "tasa al prestatario - costo FGS - costos - pérdida esperada", classification: "no disponible", confidence: "alta sobre la brecha",
  source: S.transfers,
  limitations: "No se localizó contrato verificable con costo de fondeo, spread, costos, riesgo UVA/crediticio y absorción de pérdidas; no corresponde inferirlo desde PRO.CRE.AR." });

add({ id: "S26_EPH_TRANSFER", item: 26, period: "2003-S2 a 2025-S1", universe: "Hogares urbanos que declaran una categoría amplia de transferencias/ayuda",
  measure: "incidencia declarada", metric: "Planes sociales, subsidios y ayuda en dinero", value: 14.6, unit: "% de hogares",
  comparison: "4,5% en 2003-S2", formula: "estimación ponderada EPH publicada", classification: "observado", confidence: "media-alta", source: S.eph,
  limitations: "Mezcla planes, subsidios y ayuda monetaria; no son beneficiarios únicos ni prestaciones. Cobertura geográfica 28 aglomerados en 2003 vs 31 en 2025." });
add({ id: "S26_UNICOS_GAP", item: 26, status: "brecha", period: "corte 2026-08-31", universe: "Personas, prestaciones y hogares receptores",
  measure: "serie apples-to-apples", metric: "Beneficiarios únicos, prestaciones, hogares y gasto real", valueText: "No disponible en una base integrada", unit: "",
  classification: "no disponible", confidence: "alta sobre la brecha", source: S.transfers,
  limitations: "Las fuentes locales no contienen identificadores anonimizados o conciliación entre AUH, Alimentar y otros programas para deduplicar." });
add({ id: "S27_CBA_POLICY", item: 27, period: "2023-12 a 2024", universe: "Hogar tipo cubierto por AUH + Tarjeta Alimentar según comunicación oficial",
  measure: "cobertura normativa de canasta", metric: "AUH + Alimentar / CBA", value: 100, unit: "% de CBA",
  comparison: "54,8% en diciembre de 2023", formula: "beneficio normativo / CBA del hogar tipo", classification: "proxy", confidence: "media", source: S.transfers,
  limitations: "No es tasa de pobreza evitada ni efecto causal; no incorpora take-up, otros ingresos, composición real ni distribución por decil." });
add({ id: "S27_MICROSIM_GAP", item: 27, status: "brecha", period: "corte 2026-08-31", universe: "Personas/hogares EPH",
  measure: "microsimulación contrafactual", metric: "Pobreza sin AUH/sin Alimentar/sin jubilaciones", valueText: "No disponible", unit: "puntos porcentuales",
  formula: "recalcular ingreso familiar por escenario y reponderar contra CBT/CBA", classification: "no disponible", confidence: "alta sobre la brecha", source: S.poverty,
  limitations: "Faltan microdatos EPH y reglas de imputación/compatibilización de transferencias en el repositorio." });

for (const [id, item, metric, key] of [
  ["P28_IPC_GENERAL", 28, "IPC general acumulado", "general"],
  ["P28_VIVIENDA", 28, "Vivienda, agua, electricidad, gas y otros combustibles", "vivienda_servicios"],
  ["P29_ALIMENTOS", 29, "Alimentos y bebidas no alcohólicas", "alimentos"],
  ["P29_NUCLEO", 29, "IPC núcleo acumulado", "nucleo"],
  ["P29_REGULADOS", 29, "IPC regulados acumulado", "regulados"],
]) {
  add({ id, item, period: "2023-12 a 2026-07", universe: "IPC nacional",
    measure: "variación acumulada de índice", metric, value: ipcChanges[key], unit: "%",
    comparison: item === 28 && key === "vivienda_servicios" ? `IPC general ${ipcChanges.general.toFixed(1)}%` : "",
    formula: "(índice jul-2026 / índice dic-2023 - 1) × 100", classification: "observado", confidence: "alta", source: S.ipc,
    limitations: "División o clasificación IPC; no es inflación de un hogar específico sin ponderaciones de su presupuesto." });
}
add({ id: "P28_PERFILES_GAP", item: 28, status: "brecha", period: "corte 2026-08-31", universe: "Perfiles inquilino/propietario/jubilado/familia con niños/etc.",
  measure: "índice Laspeyres por perfil", metric: "Tu inflación", valueText: "Escenario listo; no observado", unit: "%",
  formula: "Σ(peso perfil,rubro × variación índice rubro)", classification: "escenario", confidence: "alta sobre la brecha", source: S.ipc,
  limitations: "Faltan ponderaciones observadas y fechadas por perfil; asignarlas ad hoc produciría escenarios, no medición." });
add({ id: "P29_ESENCIALES_GAP", item: 29, status: "brecha", period: "corte 2026-08-31", universe: "Hogares por decil",
  measure: "índice de esenciales", metric: "Esenciales ponderados por decil", valueText: "No disponible", unit: "%",
  formula: "Σ(peso decil,rubro esencial × variación índice rubro)", classification: "no disponible", confidence: "alta sobre la brecha", source: S.ipc,
  limitations: "La serie por divisiones existe, pero faltan definición estable de esenciales y ponderaciones por decil." });

const csvText = [headers.join(","), ...evidence.map((r) => headers.map((h) => csvEscape(r[h])).join(","))].join("\r\n") + "\r\n";

// La matriz se importa con artifact-tool antes de guardarla para validar forma y legibilidad.
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Evidencia" });
const inspected = await workbook.inspect({
  kind: "table",
  range: `Evidencia!A1:S${evidence.length + 1}`,
  include: "values",
  tableMaxRows: 6,
  tableMaxCols: 19,
  maxChars: 8000,
});
if (!inspected.ndjson.includes("evidence_id") || !inspected.ndjson.includes("H01_AHORRO")) {
  throw new Error("artifact-tool no pudo inspeccionar la matriz generada");
}
const preview = await workbook.render({ sheetName: "Evidencia", range: "A1:H8", scale: 1, format: "png" });
if ((await preview.arrayBuffer()).byteLength < 1000) throw new Error("render CSV vacío o inválido");

await fs.writeFile(outputCsv, csvText, "utf8");
if (createdJunction) await fs.unlink(nodeModulesJunction);
console.log(JSON.stringify({
  status: "PASS",
  output: path.relative(root, outputCsv).replaceAll("\\", "/"),
  evidence_rows: evidence.length,
  observed: evidence.filter((r) => r.classification === "observado").length,
  proxy: evidence.filter((r) => r.classification === "proxy").length,
  scenario: evidence.filter((r) => r.classification === "escenario").length,
  unavailable: evidence.filter((r) => r.classification === "no disponible").length,
  anchors: {
    household_mora_nov2023: Number(bankNov23.households_pct),
    household_mora_may2026: Number(bankMay26.households_pct),
    pnfc_mora_feb2026: Number(pnfcFeb26.pnfc_total_pct),
    personal_loan_coverage_dec2025: num(covDec25.cobertura_personales_pct_poblacion_adulta),
    poverty_mora_semester_gap_pp: mora2h25 - mora1h24,
    ipc_general_dec2023_jul2026_pct: ipcChanges.general,
    ipc_housing_services_dec2023_jul2026_pct: ipcChanges.vivienda_servicios,
  },
}, null, 2));
