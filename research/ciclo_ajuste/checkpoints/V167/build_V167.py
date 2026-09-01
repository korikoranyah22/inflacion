from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from html import unescape
import csv
import gzip
import hashlib
import json
import os
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
V166 = CYCLE / "checkpoints" / "V166"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v167"
HIST = CYCLE / "inputs" / "historical_retrieval" / "v167" / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
GENERIC_CAPTURE = HIST / "sigen_planannual_generic_20081006.arc.gz"
PLAN2008_CAPTURE = HIST / "sigen_planannual_2008_20080705.arc.gz"
GENERIC_SHA = "aa4b44de448d93e9fb0e79533439c2ed1df7b6a11896fa20fef6483672219a21"
PLAN2008_SHA = "6506ba4ecb9b28d463d45bc62108ba06225704234c2f27da43eba3cbbe6fe444"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
SYSTEM_ASSETS = "96697695.5"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path):
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def clone_parent():
    excluded = {
        "build_V166.py", "qa_v166.py", "MANIFEST_V166.json", "README_V166.md",
        "VEREDICTO_V166.md", "AUDITORIA_V166.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V166_A_V167.md",
        "CURRENT_STATE_V166.csv", "FOUR_LEG_PASS_PANEL_V166.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V166.csv",
        "V166_SOURCE_BUNDLE.csv", "V166_PUBLIC_SEARCH_LOG.csv", "V166_PDF_VISUAL_CONTROL.csv",
        "CNV_ATTACHMENT_ANALYTIC_REVIEW_V166.md", "E0_FISCAL_RECONSTRUCTION_V166.md",
        "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V166.csv",
    }
    for source in sorted(V166.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in excluded:
            continue
        target = HERE / source.name.replace("V166", "V167")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V166", "V167"), encoding="utf-8")


def arc_text(path: Path):
    with gzip.open(path, "rb") as handle:
        return handle.read().decode("cp1252", errors="replace")


def hrefs(text: str):
    return sorted({unescape(match) for match in re.findall(r"(?i)href\s*=\s*[\"']([^\"']+)", text)})


def tree(root: Path):
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base / name).relative_to(root).as_posix() + "/" for name in dirnames)
        lines.extend((base / name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines) + "\n"


clone_parent()

# 1. Validate and catalogue the two recovered archival records.
assert GENERIC_CAPTURE.is_file() and GENERIC_CAPTURE.stat().st_size == 4619 and sha256(GENERIC_CAPTURE) == GENERIC_SHA
assert PLAN2008_CAPTURE.is_file() and PLAN2008_CAPTURE.stat().st_size == 4978 and sha256(PLAN2008_CAPTURE) == PLAN2008_SHA

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
new_sources = [
    {
        "id":"sigen_planannual_generic_cc_20081006_v167","tema":"ciclo_ajuste_historico",
        "institucion":"SIGEN · captura archivística Common Crawl",
        "titulo":"Página oficial histórica plananual.asp · captura 2008-10-06 · contenido Plan SIGEN 2007",
        "url_original":"http://www.sigen.gov.ar/plananual.asp",
        "archivo_local":"/" + GENERIC_CAPTURE.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31",
        "fecha_publicacion":"2008-10-06","codigo_serie":"CC-MAIN-2008-2009",
        "periodo_utilizado":"2007-2009","tipo":"ARC.GZ · payload oficial preservado por archivo web",
        "sha256":GENERIC_SHA,
        "nota":"V167: captura Common Crawl timestamp 20081006152047; ARC crawl-001/2008/10/14/22/1224046153641_22.arc.gz, offset 39320466, length 4619. Prueba que la ruta genérica seguía sirviendo Plan 2007; no prueba Plan 2009.",
    },
    {
        "id":"sigen_planannual_2008_cc_20080705_v167","tema":"ciclo_ajuste_historico",
        "institucion":"SIGEN · captura archivística Common Crawl",
        "titulo":"Página oficial histórica plananual2008.asp · convención de archivos Plan SIGEN 2008",
        "url_original":"http://www.sigen.gov.ar/plananual2008.asp",
        "archivo_local":"/" + PLAN2008_CAPTURE.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31",
        "fecha_publicacion":"2008-07-05","codigo_serie":"CC-MAIN-2008-2009",
        "periodo_utilizado":"2008-2010","tipo":"ARC.GZ · payload oficial preservado por archivo web",
        "sha256":PLAN2008_SHA,
        "nota":"V167: captura Common Crawl timestamp 20080705175930; ARC crawl-001/2008/07/22/0/1216748283503_0.arc.gz, offset 96667438, length 4978. Revela carpeta documentacion/plananualpdfs, espacios en Plan SIGEN 2008.pdf y anexos Anexo D - Cuadro 5..15.pdf.",
    },
]
catalog_by_id = {row["id"]: row for row in catalog}
for row in new_sources:
    catalog_by_id[row["id"]] = row
catalog = list(catalog_by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 587 and len(catalog_by_id) == 587

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    exists = local.is_file()
    actual = sha256(local) if exists else ""
    audit_rows.append({
        "id":row["id"],"archivo_local":row["archivo_local"],"exists":str(exists),
        "sha_catalog":row["sha256"].lower(),"sha_actual":actual,
        "hash_ok":str(exists and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V167.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V167.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V167.csv", missing, list(audit_rows[0]))
assert not missing

# 2. Parse the archived official pages and freeze the actual route grammar.
generic = arc_text(GENERIC_CAPTURE)
specific = arc_text(PLAN2008_CAPTURE)
generic_links = hrefs(generic)
specific_links = hrefs(specific)
assert "Plan Sigen 2007" in generic
assert "documentos_pdf/Plan_SIGEN_2007.pdf" in generic_links
assert len([link for link in generic_links if "documentos_pdf/plannual2007/cuadro" in link]) == 11
assert "Plan Sigen 2008" in specific
assert "documentacion/plananualpdfs/Plan SIGEN 2008.pdf" in specific_links
annex_2008 = [link for link in specific_links if link.startswith("documentacion/plananualpdfs/Anexo D - Cuadro")]
assert len(annex_2008) == 11
assert {int(re.search(r"Cuadro (\d+)", link).group(1)) for link in annex_2008} == set(range(5, 16))

grammar = [
    {"control_id":"RG167_01","capture_or_period":"2008-10-06","page":"plananual.asp","document_route":"documentos_pdf/Plan_SIGEN_2007.pdf","annex_route":"documentos_pdf/plannual2007/cuadro5..15.pdf","result":"GENERIC_PAGE_STALE_STILL_PLAN_2007","probative_use":"No equiparar URL genérica con año publicado","limit":"No corresponde al Plan 2009"},
    {"control_id":"RG167_02","capture_or_period":"2008-07-05","page":"plananual2008.asp","document_route":"documentacion/plananualpdfs/Plan SIGEN 2008.pdf","annex_route":"documentacion/plananualpdfs/Anexo D - Cuadro 5..15.pdf","result":"SPECIFIC_PAGE_AND_NEW_NAMING_GRAMMAR_CONFIRMED","probative_use":"Fija carpeta histórica y uso de espacios","limit":"No determina los nombres usados en 2009"},
    {"control_id":"RG167_03","capture_or_period":"2010-09","page":"plananual2010.asp referido por Infoleg","document_route":"documentacion/plananualpdfs/Plan SIGEN 2010.pdf","annex_route":"Plan SIGEN 2010 - Anexo D Cuadro 4..14.pdf; Anexo E","result":"COMMON_CRAWL_2010_CONTROL_CAPTURED","probative_use":"Confirma continuidad de carpeta y evolución de nombres","limit":"Sólo comparador cercano al período objetivo"},
    {"control_id":"RG167_04","capture_or_period":"hipótesis 2009","page":"plananual2009.asp","document_route":"documentacion/plananualpdfs/Plan SIGEN 2009.pdf","annex_route":"UNKNOWN_BETWEEN_2008_AND_2010_PATTERNS","result":"HIGH_PRECISION_CANDIDATE_NOT_CAPTURED","probative_use":"Localizador archivístico y clave para pedido de acceso","limit":"La inferencia no sustituye evidencia documental"},
]
write_csv(HERE / "E0_SIGEN_HISTORICAL_ROUTE_GRAMMAR_V167.csv", grammar)
write_csv(HERE / "E0_SIGEN_ARCHIVED_PAGE_LINKS_V167.csv", [
    {"capture":"plananual.asp@20081006152047","href":link,"classification":"OFFICIAL_PAGE_LINK"} for link in generic_links
] + [
    {"capture":"plananual2008.asp@20080705175930","href":link,"classification":"OFFICIAL_PAGE_LINK"} for link in specific_links
])

# 3. Record public-index outcomes with scope-correct negatives.
search = [
    {"search_id":"PS167_01","surface":"web search","query_or_url":"site:argentina.gob.ar/sites/default/files Plan SIGEN 2009","result":"Memoria SIGEN 2008 only; approval date 2008-12-15","classification":"REFERENCE_ONLY","next_step":"seek complete plan and approval act"},
    {"search_id":"PS167_02","surface":"Common Crawl CC-MAIN-2008-2009","query_or_url":"www.sigen.gov.ar/plananual.asp","result":"capture 20081006152047 recovered; content is Plan 2007","classification":"CAPTURE_RECOVERED_STALE_GENERIC","next_step":"do not map generic URL to 2009"},
    {"search_id":"PS167_03","surface":"Common Crawl CC-MAIN-2008-2009","query_or_url":"www.sigen.gov.ar/plananual2008.asp","result":"capture 20080705175930 recovered; exact 2008 route grammar","classification":"CAPTURE_RECOVERED_ROUTE_GRAMMAR","next_step":"use directory and spacing as candidate family"},
    {"search_id":"PS167_04","surface":"Common Crawl CC-MAIN-2009-2010","query_or_url":".../documentacion/plananualpdfs/Plan%20SIGEN%202009.pdf","result":"No Captures found","classification":"INDEX_NEGATIVE_SCOPED","next_step":"archive custody request; not nonexistence"},
    {"search_id":"PS167_05","surface":"Common Crawl CC-MAIN-2009-2010","query_or_url":"www.sigen.gov.ar/plananual2009.asp","result":"No Captures found","classification":"INDEX_NEGATIVE_SCOPED","next_step":"archive custody request; test registry and backups"},
    {"search_id":"PS167_06","surface":"Common Crawl CC-MAIN-2012","query_or_url":"2009 page, PDF and inferred annex directory","result":"No Captures found for all three candidates","classification":"LATE_INDEX_NEGATIVE_SCOPED","next_step":"do not overstate public exhaustion"},
    {"search_id":"PS167_07","surface":"Common Crawl CC-MAIN-2009-2010","query_or_url":".../documentacion/plananualpdfs/Plan%20SIGEN%202010.pdf and directory prefix","result":"main PDF plus 11 Annex-D tables, Annex E and planred2010 captured","classification":"NAMING_CONTROL_CONFIRMED","next_step":"preserve as comparator only"},
    {"search_id":"PS167_08","surface":"live SIGEN domain","query_or_url":"https://www.sigen.gob.ar/documentacion/plananualpdfs/Plan%20SIGEN%202009.pdf","result":"HTTP 404 on 2026-08-31","classification":"LIVE_ROUTE_NEGATIVE","next_step":"historical archive, not current web"},
    {"search_id":"PS167_09","surface":"Internet Archive CDX","query_or_url":"plananual2009 candidates","result":"service inaccessible from both semantic open and direct query","classification":"SERVICE_UNAVAILABLE_NOT_NEGATIVE","next_step":"retry later or request institutional copy"},
]
write_csv(HERE / "V167_PUBLIC_SEARCH_LOG.csv", search)
write_csv(HERE / "E0_PLAN_2009_ARCHIVE_CANDIDATE_MATRIX_V167.csv", search)

old_gate = read_csv(V166 / "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V166.csv")
old_gate.extend([
    {"row_id":"DG167_11","question":"¿Se reconstruyó la gramática real de rutas 2007-2010?","public_result":"Sí, con dos capturas oficiales archivadas y control 2010","proved_fact":"La URL genérica estaba rezagada; desde 2008 rige documentacion/plananualpdfs y nombres con espacios","remaining_gap":"Nombre y cuerpo exactos del Plan 2009","required_record":"Plan 2009, índice o registro web/archivo","status":"ARCHIVAL_LOCATOR_CLOSED"},
    {"row_id":"DG167_12","question":"¿Common Crawl conserva el Plan 2009 en la ruta correcta?","public_result":"No en índices 2009-2010 ni 2012 consultados","proved_fact":"Negativo limitado a esas colecciones y candidatos","remaining_gap":"Otros respaldos, inventarios o custodia institucional","required_record":"Copia en archivo SIGEN, acto aprobatorio e índice de custodia","status":"SCOPED_INDEX_NEGATIVE"},
    {"row_id":"DG167_13","question":"¿La captura de Plan 2008 prueba contenido 2009?","public_result":"No","proved_fact":"Sólo fija convención y transición de rutas","remaining_gap":"Cuerpo y anexos del año target","required_record":"Plan SIGEN 2009 completo","status":"METHOD_GUARDRAIL"},
])
write_csv(HERE / "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V167.csv", old_gate)

bridge = [
    {"layer":"UAI","known_target_value":"UAI Ministerio de Economía y Finanzas Públicas","evidence":"Plan 2010 Anexo H, crosswalk cercano al período objetivo","exact_link_to_2009_target":"NO","missing_identifier":"encabezado y versión UAI del Plan 2009","status":"NEAR_TARGET_ONLY"},
    {"layer":"entidad","known_target_value":"MEyFP; ONCCA; MAGyP; MIyT; YCRT bajo una UAI en 2010","evidence":"Plan 2010 Anexo H y competencia transitoria del Decreto 1366/2009","exact_link_to_2009_target":"PARCIAL","missing_identifier":"crosswalk 2009 fila a fila con vigencia efectiva","status":"LEGAL_AND_PLAN_BRIDGE"},
    {"layer":"proyecto","known_target_value":"Cuenta de Inversión como programa horizontal en 2008 y 2010","evidence":"Plan SIGEN 2008 y Plan SIGEN 2010","exact_link_to_2009_target":"NO","missing_identifier":"id, título, horas y área responsable del proyecto 2009","status":"ANNUAL_CONTINUITY_NOT_IDENTITY"},
    {"layer":"producto","known_target_value":"Informe global Cuenta de Inversión 2008 emitido en 2009","evidence":"referencia en Memoria SIGEN 2009","exact_link_to_2009_target":"PARCIAL","missing_identifier":"id de producto, número de informe y UAI contribuyentes","status":"PRODUCT_REFERENCED_BODY_ABSENT"},
    {"layer":"supervision_planeamiento","known_target_value":"aproximadamente 120/160 informes de supervisión alrededor del período","evidence":"agregados de Cuenta 2009 y Memoria 2009","exact_link_to_2009_target":"NO","missing_identifier":"número, fecha y versión del plan en el informe UAI Economía","status":"DENOMINATOR_OPEN"},
    {"layer":"informe_sustantivo","known_target_value":"objeto global de control Cuenta de Inversión 2008","evidence":"inventario Libro Blanco SIGEN y memoria anual","exact_link_to_2009_target":"PARCIAL","missing_identifier":"cuerpo, anexos, contribuyentes, distribución y papeles de trabajo","status":"REPORT_BODY_OPEN"},
    {"layer":"nota_3672","known_target_value":"Nota SIGEN 3672/09 GSEyP ordena seguimiento SISIO","evidence":"referencia contemporánea en Cuenta CGN 2009 UEPEX","exact_link_to_2009_target":"SOLO_REFERENCIA","missing_identifier":"fecha completa, cuerpo firmado, destinatarios, adjuntos y registro de salida","status":"NOTE_BODY_OPEN"},
    {"layer":"observacion_SISIO","known_target_value":"los hallazgos debían incorporarse a SISIO para seguimiento UAI","evidence":"referencia contemporánea a Nota 3672/09 y esquema Resolución 15/2006","exact_link_to_2009_target":"NO","missing_identifier":"id, organismo, observación, estado, historial y documentos vinculados","status":"SYSTEM_ENTRY_OPEN"},
    {"layer":"ejecucion_bancaria","known_target_value":"ninguna capa de planeamiento prueba pago o reversa","evidence":"registro de quiebres metodológicos","exact_link_to_2009_target":"NO","missing_identifier":"10 filas objetivo de ejecución y respaldo bancario","status":"BANK_GATE_0_OF_10"},
]
write_csv(HERE / "E0_UAI_ENTITY_PROJECT_PRODUCT_REPORT_CROSSWALK_V167.csv", bridge)

method_breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V167.csv")
method_breaks.extend([
    {"break_id":"archived_route_grammar_not_target_document","dimension":"document","problem":"La gramática de rutas 2007-2010 acota búsquedas pero no prueba que el Plan 2009 haya usado un nombre particular.","rule":"Conservar candidatos como localizadores y exigir cuerpo, índice y acto.","status":"FROZEN_V167","evidence":"Common Crawl official SIGEN page captures"},
    {"break_id":"stale_generic_page_not_target_year","dimension":"time","problem":"plananual.asp servía Plan 2007 todavía en octubre de 2008.","rule":"No inferir año por URL genérica; verificar contenido y timestamp.","status":"FROZEN_V167","evidence":"SIGEN plananual.asp capture 20081006152047"},
    {"break_id":"common_crawl_no_capture_not_nonexistence","dimension":"archive","problem":"Ausencia en índices Common Crawl 2009-2010 y 2012 no prueba inexistencia ni falta de emisión.","rule":"Registrar colección, consulta y alcance; mantener ruta institucional.","status":"FROZEN_V167","evidence":"Common Crawl scoped index queries"},
])
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V167.csv", method_breaks)

# 4. Preserve unchanged analytic state and freeze the historical result.
write_csv(HERE / "CURRENT_STATE_V167.csv", read_csv(V166 / "CURRENT_STATE_V166.csv"))
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V167.csv", read_csv(V166 / "FOUR_LEG_PASS_PANEL_V166.csv"))
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V167.csv", read_csv(V166 / "STRICT_Q4_FOUR_LEG_COVERAGE_V166.csv"))

recovery_note = """# Recuperación archivística Plan SIGEN 2009 · V167

V167 corrige el localizador, no declara recuperado el Plan 2009. Dos registros Common Crawl preservan páginas oficiales SIGEN: `plananual.asp` al 6-10-2008 aún publicaba el Plan 2007, mientras `plananual2008.asp` al 5-7-2008 enlazaba `documentacion/plananualpdfs/Plan SIGEN 2008.pdf` y once anexos `Anexo D - Cuadro 5..15.pdf`. El índice 2009-2010 conserva en la misma carpeta el Plan 2010 y sus anexos, con una convención nuevamente modificada.

La ruta candidata de mayor precisión pasa a ser `documentacion/plananualpdfs/Plan SIGEN 2009.pdf`, pero no tiene captura en las colecciones Common Crawl 2009-2010 ni 2012 consultadas y hoy devuelve 404 en el dominio `.gob.ar`. La consulta a Internet Archive no estuvo disponible. Todo negativo queda limitado a superficie, colección, fecha y cadena exacta; no se interpreta como inexistencia.

El pedido institucional puede ahora identificar: Plan SIGEN 2009 completo; acto del 15-12-2008; índice y metadatos del antiguo directorio `documentacion/plananualpdfs`; subplan UAI Economía; comunicación de aprobación; versiones SISPE/SISIO; informe de Supervisión del Planeamiento; proyecto, producto e informe Cuenta de Inversión 2008; Nota 3672/09 GSEyP, registro de salida y entradas SISIO vinculadas.

La cadena UAI-entidad-proyecto-producto-informe sigue abierta. Banco, documentos de ejecución y reversas permanecen 0/10. No se enviaron solicitudes.
"""
(HERE / "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V167.md").write_text(recovery_note, encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V167.md").write_text(recovery_note, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V167.md").write_text(f"""# Revisión analítica acumulada V167

El panel bancario permanece congelado en 34 entidades exactas y {COVERAGE}% de activos; V167 no agrega promociones. El avance es archivístico: dos páginas oficiales SIGEN recuperadas corrigen la familia de rutas del Plan 2009 y separan URL, año publicado y cuerpo documental. El Plan 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-producto-informe continúan abiertos; seis pedidos permanecen DRAFT_NOT_SENT y la ejecución histórica sigue 0/10.
""", encoding="utf-8")

# 5. Source bundle and synchronization controls.
bundle_specs = [
    ("SIGEN_GENERIC_PLAN_PAGE_ARCHIVE", GENERIC_CAPTURE, "http://www.sigen.gov.ar/plananual.asp"),
    ("SIGEN_PLAN_2008_PAGE_ARCHIVE", PLAN2008_CAPTURE, "http://www.sigen.gov.ar/plananual2008.asp"),
    ("SIGEN_MEMORY_2008_PLAN2009_APPROVAL", CYCLE / "inputs/historical_retrieval/v157/binaries/sigen_memoria_2008_plan_2009_approval.pdf", "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2008.pdf"),
    ("SIGEN_PLAN_2008_TARGET_CONTROL", CYCLE / "inputs/historical_retrieval/v157/binaries/infoleg_plan_sigen_2008_target_control_program.html", "https://www.infoleg.gob.ar/"),
    ("SIGEN_PLAN_2010_PART1", CYCLE / "inputs/historical_retrieval/v157/binaries/infoleg_plan_sigen_2010_part_1.html", "https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno22-2-2010-1.htm"),
    ("SIGEN_PLAN_2010_PART2", CYCLE / "inputs/historical_retrieval/v157/binaries/infoleg_plan_sigen_2010_part_2_sisio_cutoff.html", "https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno1-3-2010-1.htm"),
    ("SIGEN_PLAN_2010_ANNEX_G", CYCLE / "inputs/historical_retrieval/v160/binaries/infoleg_plan_sigen_2010_annex_g_supervision_area_acronyms_image16.jpg", "OFFICIAL_INFOLEG_CAPTURE"),
    ("SIGEN_PLAN_2010_ANNEX_H", CYCLE / "inputs/historical_retrieval/v160/binaries/infoleg_plan_sigen_2010_annex_h_multi_entity_uai_image19.jpg", "OFFICIAL_INFOLEG_CAPTURE"),
    ("CGN_ACCOUNT_2009_NOTE_3672_CHAIN", CYCLE / "inputs/historical_retrieval/v155/binaries/cgn_cuenta_2009_uepex_note_sisio_chain.pdf", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sep.pdf"),
]
bundle = []
for role, path, url in bundle_specs:
    assert path.is_file()
    bundle.append({"role":role,"path":"/" + path.relative_to(REPO).as_posix(),"url":url,"bytes":str(path.stat().st_size),"sha256":sha256(path),"analytic_use":"Plan SIGEN 2009 / Note 3672 / UAI crosswalk V167"})
write_csv(HERE / "V167_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{
    "role":"ARCHIVED_OFFICIAL_SIGEN_PAGE","relative_path":"/" + path.relative_to(REPO).as_posix(),
    "source_url":url,"size_bytes":str(path.stat().st_size),"sha256":sha256(path),
    "format_verification":"GZIP_MAGIC_ARC_RECORD_DECOMPRESSED_AND_CONTENT_ASSERTED",
} for path, url in ((GENERIC_CAPTURE, new_sources[0]["url_original"]), (PLAN2008_CAPTURE, new_sources[1]["url_original"]))]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V167.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V167.csv", search)
(SYNC / "SOURCE_SYNC_REPORT_V167.md").write_text("""# Sincronización incremental de fuentes · V167

- Catálogo maestro: 587/587 copias locales y SHA-256 válido; brecha 0.
- Nuevas fuentes: dos registros ARC.GZ con páginas oficiales históricas SIGEN preservadas por Common Crawl.
- Se verificó descompresión, timestamp, URL, título y enlaces internos decisivos.
- El Plan SIGEN 2009 no fue recuperado; se corrigió su localizador y se congelaron negativos con alcance.
""", encoding="utf-8")

# 6. Checkpoint summaries.
(HERE / "README_V167.md").write_text(f"""# Checkpoint V167

- Archivo fuente: 587/587 copias locales con hash válido; +2 capturas archivísticas SIGEN.
- Hallazgo: `plananual.asp` estaba rezagada en Plan 2007; `plananual2008.asp` revela la carpeta y gramática correctas desde 2008.
- Candidato Plan 2009: `documentacion/plananualpdfs/Plan SIGEN 2009.pdf`; sin captura en Common Crawl 2009-2010/2012 y 404 actual.
- Plan 2009 y Nota 3672/09: cuerpos aún no recuperados; crosswalk UAI-entidad-proyecto-producto-informe abierto.
- Panel bancario sin cambio: 34 entidades; activos {NUMERATOR}/{SYSTEM_ASSETS}; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V167.md").write_text("""# Veredicto V167

Avance archivístico real, sin cierre probatorio del target. Las capturas recuperadas descartan la URL genérica como identidad anual y revelan la familia correcta de archivos, permitiendo formular un localizador y un pedido institucional mucho más precisos. La ausencia del candidato 2009 en dos colecciones Common Crawl y el 404 actual son negativos acotados, no prueba de inexistencia. Plan, acto, Nota 3672/09, entrada SISIO y crosswalk fila a fila continúan abiertos. No cambia el panel bancario ni la ejecución 0/10.
""", encoding="utf-8")
(HERE / "AUDITORIA_V167.md").write_text(f"""# Auditoría V167

- Catálogo/copia/hash: 587/587; huecos 0; fuentes nuevas 2.
- ARC: 2/2 con gzip válido, metadatos y contenido decisivo verificados.
- Gramática: transición 2007/2008 y control 2010 congelados; candidato 2009 explícito.
- Negativos: Common Crawl 2009-2010 y 2012 acotados; vivo 404; Internet Archive no disponible, no negativo.
- Crosswalk: 9 capas separadas; ninguna se convierte en banco o ejecución.
- Panel: 34 entidades, {COVERAGE}%; promociones 0; solicitudes 0.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V167_A_V168.md").write_text("""# Handover V167 → V168

## Cerrado en V167

- Dos capturas oficiales SIGEN archivadas y catalogadas; gramática de rutas 2007-2010 reconstruida.
- Localizador Plan 2009 corregido; negativos públicos congelados con alcance.
- Archivo 587/587; panel 34 sin cambio.

## Prioridad V168

1. Reintentar Internet Archive para la ruta exacta y enumerar inventarios/respaldos SIGEN, sin tratar fallas del servicio como negativos.
2. Buscar acto aprobatorio 15-12-2008, índice del directorio histórico y comunicación UAI Economía.
3. Buscar cuerpo y registro de salida Nota 3672/09, más ids SISIO vinculados.
4. Mantener seis borradores DRAFT_NOT_SENT, SAF355 0/5 y ejecución bancaria 0/10 hasta evidencia o autorización.
""", encoding="utf-8")

refs = HERE / "SOURCE_REFERENCES_V167.md"
with refs.open("a", encoding="utf-8") as handle:
    for row in new_sources:
        handle.write(f"\n- `{row['id']}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V166.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V167","date":"2026-08-31","master_catalog_entries":587,
    "physical_local_copies":587,"physical_local_hash_ok":587,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_SIGEN_PLAN_ROUTE_GRAMMAR_RECOVERED_TARGET_BODIES_OPEN",
    "analytical_promotion":"NONE_V167_ARCHIVAL_LOCATOR_ONLY","exact_entities":34,
    "strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":SYSTEM_ASSETS,
    "strict_coverage_pct":COVERAGE,"strict_coverage_increment_v166_pp":"0",
    "request_drafts_status":"DRAFT_NOT_SENT","requests_submitted":0,"responses_received":0,
    "saf355_certifications_located":0,"executed_historical_bank_rows_confirmed":0,
    "discovered_official_binary_recovery_queue":0,"plan_sigen_2009_body_located":False,
    "note_3672_09_body_located":False,"new_archival_captures":2,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V167.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 7. Provenance, transparency, trees and manifests.
archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V167.csv")
archival.extend([
    {
        "source_id":new_sources[0]["id"],"original_url":new_sources[0]["url_original"],
        "retrieval_url":"https://data.commoncrawl.org/crawl-001/2008/10/14/22/1224046153641_22.arc.gz",
        "capture_timestamp":"20081006152047","cdx_digest":"DVGOTYMYBIVN73RE2KQYMH3L6TXGOK33",
        "local_path":new_sources[0]["archivo_local"],"sha256":new_sources[0]["sha256"],"bytes":str(GENERIC_CAPTURE.stat().st_size),
        "provenance_note":"Common Crawl ARC byte range offset 39320466 length 4619; official SIGEN payload; route-grammar evidence only.",
    },
    {
        "source_id":new_sources[1]["id"],"original_url":new_sources[1]["url_original"],
        "retrieval_url":"https://data.commoncrawl.org/crawl-001/2008/07/22/0/1216748283503_0.arc.gz",
        "capture_timestamp":"20080705175930","cdx_digest":"MNSAM5KY7KSS3FFR2KU5WOV6SPBPJDMZ",
        "local_path":new_sources[1]["archivo_local"],"sha256":new_sources[1]["sha256"],"bytes":str(PLAN2008_CAPTURE.stat().st_size),
        "provenance_note":"Common Crawl ARC byte range offset 96667438 length 4978; official SIGEN payload; route-grammar evidence only.",
    },
])
write_csv(HERE / "ARCHIVAL_PROVENANCE_V167.csv", archival)

origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(HIST.parent):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"downloaded/preserved V167","note":"Common Crawl ARC record carrying official historical SIGEN page"}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V167","note":"incremental archival-source synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path":rel,"origin":"generated/updated V167","note":"SIGEN Plan 2009 archival-route checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V167.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V167.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V167.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V167.json"):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V167","note":"587-source physical/hash completeness control"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
text = transparency.read_text(encoding="utf-8-sig")
if "## V167 · Ruta histórica Plan SIGEN 2009" not in text:
    text += """

## V167 · Ruta histórica Plan SIGEN 2009

Dos registros Common Crawl preservan páginas oficiales SIGEN y prueban que la URL genérica estaba rezagada en Plan 2007, mientras la página 2008 ya usaba `documentacion/plananualpdfs` y nombres con espacios. El control 2010 confirma la carpeta pero también otra evolución de nombres. El candidato 2009 correcto no fue capturado en las colecciones consultadas y hoy devuelve 404: negativos acotados, no inexistencia. Plan 2009, Nota 3672/09 y crosswalk continúan abiertos. Archivo 587/587; panel 34 sin cambio.
"""
    transparency.write_text(text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V167.
- Fuentes: 587/587 local y SHA-válido; +2 capturas SIGEN históricas.
- Plan SIGEN 2009: localizador corregido, cuerpo aún abierto; Nota 3672/09 abierta.
- Panel: 34 entidades; {COVERAGE}% de activos; promociones V167: 0.
- Solicitudes: 0 enviadas; seis borradores DRAFT_NOT_SENT.
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V167.json"]
manifest = {
    "checkpoint":"V167","parent_checkpoint":"V166","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":SYSTEM_ASSETS,
    "new_promotions":[],"historical_finding":"Two official SIGEN page captures recover the 2007-2010 route grammar; Plan 2009 candidate corrected but body remains absent",
    "source_archive":"587/587 catalogued physical SHA-valid; two Common Crawl ARC records added; binary queue 0",
    "plan_sigen_2009_body":"NOT_LOCATED","note_3672_09_body":"NOT_LOCATED","crosswalk_gate":"OPEN",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files,
}
(HERE / "MANIFEST_V167.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)} for path in iter_files(REPO) if path != global_manifest]
global_payload = {
    "checkpoint":"V167","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO",
    "source_audit":"587 master; 587 physical SHA-valid; two historical SIGEN ARC captures added",
    "historical_workstream":"Plan SIGEN 2009 route grammar recovered; Plan body, Note 3672/09, SISIO ids and execution remain open; six drafts not sent",
    "file_count_excluding_manifest":len(global_files),"files":global_files,
}
tmp = global_manifest.with_suffix(".json.V167tmp")
tmp.write_text(json.dumps(global_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print("V167 BUILD PASS · catalog=587/587 · archival_captures=2 · exact=34 · coverage_unchanged · requests=0")
