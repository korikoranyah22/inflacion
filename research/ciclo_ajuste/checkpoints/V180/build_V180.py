from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V179"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v180"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v180"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.440604"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path | str):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def append_note_once(row, sentence: str):
    """Keep catalog-note enrichment idempotent across reproducibility reruns."""
    note = (row.get("nota") or "").strip()
    if sentence not in note:
        row["nota"] = (note + " " + sentence).strip()


def write_csv(path: Path | str, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path | str):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def iter_files(root: Path):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((x for x in dirs if x not in EXCLUDED), key=str.casefold)
        for name in sorted(files, key=str.casefold):
            yield Path(directory) / name


def tree(root: Path):
    out = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((x for x in dirs if x not in EXCLUDED), key=str.casefold)
        base = Path(directory)
        out += [(base / x).relative_to(root).as_posix() + "/" for x in dirs]
        out += [(base / x).relative_to(root).as_posix() for x in sorted(files, key=str.casefold)]
    return "\n".join(out) + "\n"


def clone_parent():
    skip = {
        "MANIFEST_V179.json", "README_V179.md", "VEREDICTO_V179.md", "AUDITORIA_V179.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V179_A_V180.md", "V179_SOURCE_BUNDLE.csv",
        "V179_PUBLIC_SEARCH_LOG.csv", "V179_PDF_VISUAL_CONTROL.csv", "V179_HTML_CONTENT_CONTROL.csv",
        "V179_BO_ENDPOINT_PROVENANCE.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V179", "V180")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V179", "V180"), encoding="utf-8")


EXPECTED = {
    "agn_api_res014_2010.json": (12114, "4e4c0c055679108eae09ec80f21d2d4b8e1917bba3457f355eb48d2f687530a1"),
    "agn_api_res023_2005.json": (11994, "88408f0c302193ca0c3f9927275f719b745276d95baf4523d68b3b25cd13d692"),
    "agn_api_res129_2005_bid1192.json": (306, "47e7348d1fe4ff73f42d34545e806bcf7bfd6a750a10a5ac7bd828a3680a6124"),
    "agn_api_res160_2006.json": (12116, "543ee0175353228890f6118a84d4999e9f053b639a0ef26d69c1025b1a665a5d"),
    "agn_res014_2010_bid1192_ejercicio2008.pdf": (538946, "cc2fafdc076d0fa1cf3788b5231d8f3bc8cffd9f0bb96d116a767b817d24c6d9"),
    "agn_res023_2005_fideicomisos_publicos.pdf": (397340, "dfd7d3ac057f6d4c342b6231f60066d7770d71efff880f25d5b14f1aacf729eb"),
    "agn_res129_2005_current_endpoint_error.html": (253718, "44512fa8043e54b55d98ca0b5fe6a2b70228cffbc138309edfca5e6ee56f4b2a"),
    "agn_res160_2006_bid1192_ejercicio2005.pdf": (413016, "8dcdbf05145e3e98b2b1b55bf94057eeb27b444ceacf1452f4fbe81f26ef3d8d"),
    "bcra_com_a4620_2007_mipymes.pdf": (223821, "8ce2fcf8506ff22467344a733970ad81d3fdf7cb6fecf31842ab3cc4273ba6ba"),
    "bcra_com_b8920_2007_mipymes.pdf": (723826, "0d8427265326b1d878bf0c6a716d9ddd48f8de97663ad9ad1bc141feca6fded8"),
    "bcra_com_b8995_2007_tasas.pdf": (71734, "60156bb571e330815349e771319994203b43a0172c8e274f8596c5b8b91b4fe9"),
    "bcra_com_b9055_2007_tasas.pdf": (71753, "e60a68a9a519643a137724172c2dfd2d27e7c7703d95d50cb0c7581aa24139bb"),
    "bcra_com_b9056_2007_suspension.pdf": (71641, "475c1cd5f3d7f34e1f3e8519af43a48770f84a3b481a4efbce6fa3d9508f4e0b"),
    "bcra_com_b9123_2007_tasas.pdf": (71747, "e0c5a4467dbae389d99e911d708b1deb54fbe7a497e1d3d62cd3b9308b502560"),
    "bcra_texto_ordenado_programa_credito_mipymes.pdf": (321037, "ec4cb243a456610f6b8ce0ea2d178ebba01e6e613598f37bca4e284230c07bb0"),
    "bid_ar0127_evaluacion_intermedia.pdf": (92690, "f5d5244c3b0c14649774eb62aee00f8a15ab899dd9f19852707879375793a873"),
    "bid_ar0127_informe_terminacion_proyecto.pdf": (1037832, "2d95272775dd760eefe091e594be07c72e440cdc5249782628e3ecf72a352e5e"),
    "bid_ar0127_propuesta_prestamo_407194.pdf": (18400, "cf16d52f853f07b69ccc4a622a5d83d6d61724cf82e01cef344c1457217bc37c"),
    "bo_resolucion_347_2004_anexo_modelo_fideicomiso.pdf": (577492, "ea7dd86042808296db63d141a9346757c02a48ace83500517c1f1acc58116764"),
    "bo_resolucion_347_2004_detalle_aviso_7263053.html": (116603, "a157a367492bff8a882c569d5e0934ca0b2557bb5d640eb4b6d6f1bb275002e1"),
    "bo_resolucion_389_2005_anexo_modelo_fideicomiso.pdf": (5948598, "d4bc767e82bbac9ae7fa3d0774610fc4538424b8c1bfee6031144139f78a08d1"),
    "bo_resolucion_389_2005_detalle_aviso_7276817.html": (140607, "5b0341fddf421ea2b078449e15e71c32905ed409ec129b9eca9a92ac7b91c3a4"),
    "infoleg_norma_101253_addendas_fideicomiso.html": (12597, "4d7579121842124c008d31b08920c2b97b4be6d754d824692bb383f67e3a91d6"),
    "wayback_cdx_agn_2005_129info.json": (3, "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"),
}


SPECS = [
    ("e0_bo_res347_2004_full_annex_contract_v180", "Boletín Oficial de la República Argentina", "Resolución 347/2004 · anexo completo del modelo de fideicomiso", "https://www.boletinoficial.gob.ar/detalleAviso/primera/7263053/20040513?busqueda=1&anexos=1", "bo_resolucion_347_2004_anexo_modelo_fideicomiso.pdf", "2004-05-13", "Aviso 7263053 · Anexo 00227867", "2003-2004", "PDF oficial · 87 páginas · texto digital", "Modelo aprobado: contrato y Anexos I-V; fechas y firmas de las partes en blanco. No es contraparte ejecutada."),
    ("e0_bo_res347_2004_notice_endpoint_v180", "Boletín Oficial de la República Argentina", "Detalle oficial del aviso 7263053 y Anexo 00227867", "https://www.boletinoficial.gob.ar/detalleAviso/primera/7263053/20040513?busqueda=1&anexos=1", "bo_resolucion_347_2004_detalle_aviso_7263053.html", "2004-05-13", "Aviso 7263053", "2004", "HTML oficial preservado · procedencia", "Prueba procedencia del anexo, no ejecución."),
    ("e0_bo_res389_2005_full_annex_contract_v180", "Boletín Oficial de la República Argentina", "Resolución 389/2005 · anexo completo del modelo modificado", "https://www.boletinoficial.gob.ar/detalleAviso/primera/7276817/20050711?busqueda=1&anexos=1", "bo_resolucion_389_2005_anexo_modelo_fideicomiso.pdf", "2005-07-11", "Aviso 7276817 · Anexo 00292146", "2004-2005", "PDF oficial escaneado · 89 páginas", "Modelo aprobado: contrato y Anexos I-III publicados; refiere IV-V sin incluirlos. Fecha y firmas de partes en blanco."),
    ("e0_bo_res389_2005_notice_endpoint_v180", "Boletín Oficial de la República Argentina", "Detalle oficial del aviso 7276817 y Anexo 00292146", "https://www.boletinoficial.gob.ar/detalleAviso/primera/7276817/20050711?busqueda=1&anexos=1", "bo_resolucion_389_2005_detalle_aviso_7276817.html", "2005-07-11", "Aviso 7276817", "2005", "HTML oficial preservado · procedencia", "Prueba procedencia del anexo, no ejecución."),
    ("e0_infoleg_res747_2004_guarantee_addenda_v180", "Ministerio de Economía y Producción", "Resolución 747/2004 · addendas y delimitación de garantías IFI", "https://servicios.infoleg.gob.ar/infolegInternet/anexos/100000-104999/101253/norma.htm", "infoleg_norma_101253_addendas_fideicomiso.html", "2004-11-23", "Resolución 747/2004", "2004", "HTML oficial preservado · texto y anexos", "Acredita que el contrato y garantía se celebraron el 26/05/2004; cada IFI garantiza su propia cartera y Macro las obligaciones del fiduciario. El anexo publicado sigue siendo modelo sin firmas."),
    ("e0_agn_res023_2005_fideicomisos_publicos_v180", "Auditoría General de la Nación", "Resolución 23/2005 · relevamiento de fideicomisos públicos", "https://www.agn.gob.ar/sites/default/files/informes/2005_023info_0.pdf", "agn_res023_2005_fideicomisos_publicos.pdf", "2005", "AGN 23/2005 · Act. 688/04", "2004-2005", "PDF oficial · 93 páginas", "Relevamiento, no auditoría de cumplimiento; registra MyPES II, contrato 26/05/2004, plazo, partes y recursos."),
    ("e0_agn_res160_2006_bid1192_fy2005_v180", "Auditoría General de la Nación", "Resolución 160/2006 · auditoría BID 1192 ejercicio 2005", "https://www.agn.gob.ar/sites/default/files/informes/2006_160info_0.pdf", "agn_res160_2006_bid1192_ejercicio2005.pdf", "2006", "AGN 160/2006", "2005-2006", "PDF oficial · 99 páginas", "Acredita por informe de auditoría fechas de instrumentos ejecutados, baja ejecución inicial, operaciones Macro, inactividad Credicoop y brechas de legajos/control. No sustituye contraparte firmada."),
    ("e0_agn_res014_2010_bid1192_fy2008_v180", "Auditoría General de la Nación", "Resolución 14/2010 · auditoría BID 1192 ejercicio 2008", "https://www.agn.gob.ar/sites/default/files/informes/2010_014info_0.pdf", "agn_res014_2010_bid1192_ejercicio2008.pdf", "2010", "AGN 14/2010", "2007-2009", "PDF oficial · 48 páginas", "Cuantifica la facilidad en pesos, tasa máxima, cierre, terminación y liquidación pendiente; dice que Res. 967/2006 no se había perfeccionado al 22/02/2008."),
    ("e0_agn_res129_2005_endpoint_gap_v180", "Auditoría General de la Nación", "Endpoint legado AGN 129/2005 · error de migración preservado", "https://www.agn.gob.ar/sites/default/files/informes/2005_129info.pdf", "agn_res129_2005_current_endpoint_error.html", "2026-09-01", "AGN 129/2005 · endpoint", "2005/consulta 2026", "HTML de respuesta institucional preservado", "Control negativo: el PDF histórico no se recupera por esta ruta; no es evidencia sustantiva."),
    ("e0_agn_res129_2005_api_query_gap_v180", "Auditoría General de la Nación", "Consulta API AGN por resolución 129/2005 · cero registros", "https://webagnapi.agn.gob.ar/api/node/informes?filter%5Bano%5D=2005&filter%5Bresolucion%5D=129&include=informe%2Cresolucion_archivo", "agn_api_res129_2005_bid1192.json", "2026-09-01", "AGN JSON:API · count 0", "2005/consulta 2026", "JSON oficial preservado · control negativo", "La migración pública no devuelve el registro; ausencia de índice no prueba ausencia del informe histórico."),
    ("e0_wayback_agn_res129_2005_cdx_gap_v180", "Internet Archive", "Consulta CDX de AGN 129/2005 · cero capturas", "https://web.archive.org/cdx/search/cdx?url=agn.gov.ar/sites/default/files/informes/2005_129info*&output=json", "wayback_cdx_agn_2005_129info.json", "2026-09-01", "Wayback CDX", "2005/consulta 2026", "JSON preservado · control negativo", "La consulta devolvió []; no prueba inexistencia del documento."),
    ("e0_agn_api_res023_2005_metadata_v180", "Auditoría General de la Nación", "Metadata JSON:API AGN 23/2005", "https://webagnapi.agn.gob.ar/api/node/informes/6e16255b-98d6-4136-8cd0-514fa9f491d7?include=informe%2Cresolucion_archivo", "agn_api_res023_2005.json", "2026-09-01", "AGN JSON:API", "2005", "JSON oficial preservado · procedencia", "Vincula metadata institucional, archivo, tamaño y resolución."),
    ("e0_agn_api_res160_2006_metadata_v180", "Auditoría General de la Nación", "Metadata JSON:API AGN 160/2006", "https://webagnapi.agn.gob.ar/api/node/informes/6661e2fd-a341-4cb0-a884-37ae10093475?include=informe%2Cresolucion_archivo", "agn_api_res160_2006.json", "2026-09-01", "AGN JSON:API", "2006", "JSON oficial preservado · procedencia", "Vincula metadata institucional con el informe auditado."),
    ("e0_agn_api_res014_2010_metadata_v180", "Auditoría General de la Nación", "Metadata JSON:API AGN 14/2010", "https://webagnapi.agn.gob.ar/api/node/informes/8651cfe0-d65b-4cf3-86be-d5e4846352a0?include=informe%2Cresolucion_archivo", "agn_api_res014_2010.json", "2026-09-01", "AGN JSON:API", "2010", "JSON oficial preservado · procedencia", "Vincula metadata institucional con el informe auditado."),
    ("e0_bid_ar0127_pcr_v180", "Banco Interamericano de Desarrollo", "AR0127 · Informe de terminación del proyecto", "https://www.iadb.org/document.cfm?id=EZSHARE-1739351788-35", "bid_ar0127_informe_terminacion_proyecto.pdf", "2014", "AR0127 · PCR", "1999-2014", "PDF oficial · 29 páginas", "Resultados, tasas, alcance, distribución y caveats; contiene inconsistencias internas que se registran y estimaciones que no se tratan como causalidad auditada."),
    ("e0_bid_ar0127_intermediate_evaluation_v180", "Banco Interamericano de Desarrollo", "AR0127 · evaluación intermedia", "https://www.iadb.org/document.cfm?id=EZSHARE-917344851-48", "bid_ar0127_evaluacion_intermedia.pdf", "2005", "AR0127 · evaluación intermedia", "1999-2005", "PDF oficial · 4 páginas", "Control de avance y contexto de ejecución."),
    ("e0_bid_ar0127_loan_proposal_v180", "Banco Interamericano de Desarrollo", "AR0127 · propuesta de préstamo", "https://www.iadb.org/document.cfm?id=EZSHARE-917344851-47", "bid_ar0127_propuesta_prestamo_407194.pdf", "1999", "AR0127 · propuesta", "1999", "PDF oficial · 4 páginas", "Diseño, financiamiento, riesgos y clasificación: no proyecto de equidad social ni de reducción de pobreza según el propio documento."),
    ("e0_bcra_a4620_2007_mipymes_v180", "Banco Central de la República Argentina", "Comunicación A 4620 · facilidad en pesos MiPyME", "https://www.bcra.gob.ar/pdfs/comytexord/a4620.pdf", "bcra_com_a4620_2007_mipymes.pdf", "2007-01-26", "Com. A 4620", "2007", "PDF oficial · 11 páginas", "Define costo de fondeo más administración, banda de spread, responsabilidad total IFI, riesgo crediticio, legajo, control de destino, débito y sanciones."),
    ("e0_bcra_b8920_2007_mipymes_v180", "Banco Central de la República Argentina", "Comunicación B 8920 · reglamentación y primera banda", "https://www.bcra.gob.ar/pdfs/comytexord/b8920.pdf", "bcra_com_b8920_2007_mipymes.pdf", "2007-02-12", "Com. B 8920", "2007", "PDF oficial · 33 páginas", "Tasa de transferencia 2,9%, spread 0-6 pp, TNA máxima 8,9%; garantía IFI mínima 125%; comisiones/seguros afectan CFT."),
    ("e0_bcra_b8995_2007_rates_v180", "Banco Central de la República Argentina", "Comunicación B 8995 · continuidad banda 2,9% + 0-6 pp", "https://www.bcra.gob.ar/pdfs/comytexord/b8995.pdf", "bcra_com_b8995_2007_tasas.pdf", "2007-05-11", "Com. B 8995", "2007", "PDF oficial · 1 página", "Mantiene TNA máxima 8,9% por tres meses."),
    ("e0_bcra_b9055_2007_rates_v180", "Banco Central de la República Argentina", "Comunicación B 9055 · banda 3,9% + 0-5 pp", "https://www.bcra.gob.ar/pdfs/comytexord/b9055.pdf", "bcra_com_b9055_2007_tasas.pdf", "2007-08-10", "Com. B 9055", "2007", "PDF oficial · 1 página", "Eleva transferencia y reduce spread; TNA máxima permanece 8,9%."),
    ("e0_bcra_b9056_2007_suspension_v180", "Banco Central de la República Argentina", "Comunicación B 9056 · suspensión por recursos comprometidos", "https://www.bcra.gob.ar/pdfs/comytexord/b9056.pdf", "bcra_com_b9056_2007_suspension.pdf", "2007-08-13", "Com. B 9056", "2007", "PDF oficial · 1 página", "Suspende nuevos proyectos porque los recursos estaban totalmente comprometidos."),
    ("e0_bcra_b9123_2007_rates_v180", "Banco Central de la República Argentina", "Comunicación B 9123 · continuidad banda 3,9% + 0-5 pp", "https://www.bcra.gob.ar/pdfs/comytexord/b9123.pdf", "bcra_com_b9123_2007_tasas.pdf", "2007-11-12", "Com. B 9123", "2007", "PDF oficial · 1 página", "Mantiene TNA máxima 8,9%; no convierte CFT en TNA."),
    ("e0_bcra_ordered_text_mipymes_comparator_v180", "Banco Central de la República Argentina", "Texto ordenado Programa Global de Crédito a MiPyMEs", "https://www.bcra.gob.ar/pdfs/texord/t-crpyme.pdf", "bcra_texto_ordenado_programa_credito_mipymes.pdf", "2026-09-01", "Texto ordenado BCRA", "1999-2007", "PDF oficial · 64 páginas · comparador", "Comparador normativo de programas relacionados; no se transpone automáticamente a cada tramo del fideicomiso o la facilidad."),
]


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for name, (size, digest) in EXPECTED.items():
    path = HIST / name
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest

sources = []
for sid, inst, title, url, name, publication, code, period, typ, note in SPECS:
    path = HIST / name
    sources.append({
        "id": sid, "tema": "ciclo_ajuste_e0_fiscal", "institucion": inst, "titulo": title,
        "url_original": url, "archivo_local": "/" + path.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": publication,
        "codigo_serie": code, "periodo_utilizado": period, "tipo": typ,
        "sha256": EXPECTED[name][1], "nota": note,
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
if "e0_bo_res967_2006_full_annex_contract_v179" in by_id:
    append_note_once(by_id["e0_bo_res967_2006_full_annex_contract_v179"], "V180 acredita que el modelo Res. 967 no estaba perfeccionado al 22/02/2008; no se lo trata como régimen operativo.")
if "e0_norm_res967_2006_mypesii_trust_v178" in by_id:
    append_note_once(by_id["e0_norm_res967_2006_mypesii_trust_v178"], "AGN 14/2010 informa que el contrato aprobado por Res. 967/2006 no estaba perfeccionado al 22/02/2008.")
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 673

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()), "sha_catalog": row["sha256"].lower(), "sha_actual": actual, "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V180.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V180.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V180.csv", missing, list(audit[0]))
assert not missing


write_csv(HERE / "E0_BID1192_CONTRACT_VERSION_CONTROL_2003_2008_V180.csv", [
    {"row_id":"VC180_01","date":"2003-05-12","instrument":"Decreto 1118/2003","legal_event":"autoriza dos fideicomisos y modelo base","execution_evidence":"norma","operative_status":"BASE_AUTHORIZATION","proof_limit":"modelo no equivale a firma"},
    {"row_id":"VC180_02","date":"2004-05-12/13","instrument":"Resolución 347/2004","legal_event":"aprueba modelo con dos IFI","execution_evidence":"anexo BO 87 páginas sin firmas","operative_status":"APPROVED_MODEL","proof_limit":"fecha y firmas en blanco"},
    {"row_id":"VC180_03","date":"2004-05-26","instrument":"Contrato y Garantía/Indemnidad","legal_event":"celebrados por Estado, SIASA, Macro y Credicoop","execution_evidence":"Res. 747/2004 y AGN 23/2005","operative_status":"EXECUTION_DATE_OFFICIALLY_CORROBORATED","proof_limit":"contraparte firmada no localizada"},
    {"row_id":"VC180_04","date":"2004-11-18/23","instrument":"Resolución 747/2004","legal_event":"aprueba addendas; delimita garantía por IFI","execution_evidence":"texto/anexos Infoleg","operative_status":"APPROVED_ADDENDA","proof_limit":"anexo publicado sin firmas"},
    {"row_id":"VC180_05","date":"2005-03-22","instrument":"Addenda Res. 148/2005","legal_event":"ejecutada por SIASA y las IFI","execution_evidence":"AGN 160/2006","operative_status":"EXECUTION_DATE_OFFICIALLY_CORROBORATED","proof_limit":"contraparte firmada no localizada"},
    {"row_id":"VC180_06","date":"2005-08-19","instrument":"Contrato Res. 389/2005","legal_event":"ejecutado por PEN, SIASA y las IFI","execution_evidence":"AGN 160/2006","operative_status":"EXECUTION_DATE_OFFICIALLY_CORROBORATED","proof_limit":"anexo BO sigue siendo modelo sin firmas"},
    {"row_id":"VC180_07","date":"2006-12-07/11","instrument":"Resolución 967/2006","legal_event":"aprueba nuevo modelo e incorporación autorizada de Nuevo Banco Suquía","execution_evidence":"norma y anexo BO","operative_status":"APPROVED_NOT_PERFECTED_BY_2008_02_22","proof_limit":"AGN 14/2010 niega perfeccionamiento a esa fecha"},
    {"row_id":"VC180_08","date":"2008-09-26","instrument":"Contrato 2005","legal_event":"se configura causal de terminación a tres años","execution_evidence":"AGN 14/2010","operative_status":"TERMINATION_TRIGGER","proof_limit":"liquidación formal y cierre aún pendientes en 2009"},
])

write_csv(HERE / "E0_BID1192_EXECUTED_INSTRUMENT_EVIDENCE_LADDER_V180.csv", [
    {"row_id":"EL180_01","instrument":"Contrato 26/05/2004","approved_model":"YES_87P","official_execution_reference":"YES_RES747_AND_AGN023","signed_counterpart":"NO","evidence_level":"DATE_AND_PARTIES_CORROBORATED_NOT_FULL_COUNTERPART","safe_conclusion":"existió instrumento celebrado; faltan firmas/fojas ejecutadas"},
    {"row_id":"EL180_02","instrument":"Addenda 22/03/2005","approved_model":"YES_RES148","official_execution_reference":"YES_AGN160","signed_counterpart":"NO","evidence_level":"DATE_AND_PARTIES_CORROBORATED_NOT_FULL_COUNTERPART","safe_conclusion":"ejecución referenciada oficialmente"},
    {"row_id":"EL180_03","instrument":"Contrato 19/08/2005","approved_model":"YES_89P","official_execution_reference":"YES_AGN160","signed_counterpart":"NO","evidence_level":"DATE_AND_PARTIES_CORROBORATED_NOT_FULL_COUNTERPART","safe_conclusion":"ejecución y comienzo operativo acreditados indirectamente"},
    {"row_id":"EL180_04","instrument":"Modelo Res. 967/2006","approved_model":"YES_99P","official_execution_reference":"NO; AGN says not perfected","signed_counterpart":"NO","evidence_level":"APPROVED_MODEL_NONOPERATIVE_AS_OF_2008_02_22","safe_conclusion":"no usar para imputar obligaciones efectivas del período"},
])

write_csv(HERE / "E0_BID1192_RES747_GUARANTEE_LIMITATION_MATRIX_V180.csv", [
    {"row_id":"GL180_01","rule":"deuda vencida impaga como condición","obligor":"cada IFI","scope":"cláusula 3.1.5 sólo ante deuda vencida e impaga de la IFI frente al fiduciario","source":"Res. 747/2004","correction":"no es garantía general automática"},
    {"row_id":"GL180_02","rule":"riesgo de crédito propio","obligor":"cada IFI","scope":"hasta el monto de créditos descontados por esa IFI","source":"Res. 747/2004","correction":"no responde por cartera originada por la otra IFI"},
    {"row_id":"GL180_03","rule":"obligaciones específicas del fiduciario","obligor":"Macro-Bansud","scope":"garantía exclusiva de Macro respecto de obligaciones del fiduciario","source":"Res. 747/2004","correction":"no corresponde imputarlas solidariamente a Credicoop"},
    {"row_id":"GL180_04","rule":"activación y pago","obligor":"IFI pertinente","scope":"requiere saldo, mora, aviso, aporte/débito o acción","source":"instrumento + registros de desempeño pendientes","correction":"cláusula no prueba incumplimiento ni daño"},
])

write_csv(HERE / "E0_BID1192_IFI_GUARANTEE_INDEMNITY_MATRIX_V180.csv", [
    {"row_id":"GI180_01","mechanism":"garantía por riesgo de crédito","obligor":"cada IFI","scope":"créditos que esa IFI descontó, con límite a su monto","trigger_or_term":"deuda vencida e impaga según addenda","source":"Res. 747/2004","proof_limit":"falta padrón y mora"},
    {"row_id":"GI180_02","mechanism":"garantía de obligaciones del fiduciario","obligor":"Macro-Bansud exclusivamente","scope":"obligaciones específicas de SIASA/fiduciario","trigger_or_term":"incumplimiento contractual probado","source":"Res. 747/2004","proof_limit":"falta activación"},
    {"row_id":"GI180_03","mechanism":"aporte/débito","obligor":"IFI pertinente","scope":"fondos por obligaciones garantizadas dentro de su alcance","trigger_or_term":"aviso y plazos contractuales","source":"modelos 2004-2005","proof_limit":"faltan avisos y movimientos"},
    {"row_id":"GI180_04","mechanism":"mora e intereses","obligor":"IFI incumplidora","scope":"obligación exigible bajo instrumento ejecutado","trigger_or_term":"vencimiento y falta de pago","source":"anexos de garantía","proof_limit":"sin ledger no se cuantifica"},
    {"row_id":"GI180_05","mechanism":"no transposición Res. 967","obligor":"ninguno por inferencia","scope":"modelo 2006 no perfeccionado al 22/02/2008","trigger_or_term":"requerir contraparte ejecutada posterior","source":"AGN 14/2010","proof_limit":"no usar cláusulas 2006 como hechos"},
])

write_csv(HERE / "E0_BID1192_2006_ROLE_RESPONSIBILITY_MATRIX_V180.csv", [
    {"row_id":"RR180_01","actor":"Estado Nacional / Ministerio","role":"Fiduciante-Beneficiario y fideicomisario en el modelo","proved_duty_or_right":"aportar recursos, controlar e instruir por vías contractuales","source":"Res. 967/2006 y anexo","limit":"modelo aprobado no perfeccionado al 22/02/2008; no prueba obligación operativa"},
    {"row_id":"RR180_02","actor":"SSEPYMEYDR/UCP","role":"Organismo Ejecutor en el modelo","proved_duty_or_right":"evaluación, control, supervisión y sanciones previstas","source":"Res. 967/2006, cláusulas 19-20","limit":"arquitectura prevista; faltan instrumento ejecutado y expedientes"},
    {"row_id":"RR180_03","actor":"SUD Inversiones y Análisis S.A.","role":"Fiduciario en el modelo","proved_duty_or_right":"administración, contabilidad, custodia, cobranza y rendición previstas","source":"Res. 967/2006, cláusulas 10-16","limit":"no acredita que asumiera estas funciones bajo el modelo 2006"},
    {"row_id":"RR180_04","actor":"BCRA","role":"Agente financiero/control en el modelo","proved_duty_or_right":"recepción de información y archivo mensual prevista","source":"Decreto 1118; Res. 967/2006","limit":"no acredita producción efectiva de informes bajo el modelo 2006"},
    {"row_id":"RR180_05","actor":"Banco Credicoop","role":"IFI prevista","proved_duty_or_right":"originación/administración y garantía definidas por el modelo","source":"Res. 967/2006 y anexos","limit":"no atribuir obligación operativa; para el régimen ejecutado aplicar Res. 747 y cartera propia"},
    {"row_id":"RR180_06","actor":"Banco Macro-Bansud","role":"IFI prevista y designante de SUD","proved_duty_or_right":"originación/administración y garantía adicional del fiduciario previstas","source":"Res. 967/2006 y anexos","limit":"no atribuir obligación operativa; activación no probada"},
    {"row_id":"RR180_07","actor":"Nuevo Banco Suquía","role":"IFI cuya incorporación fue autorizada","proved_duty_or_right":"adhesión contemplada por el nuevo modelo","source":"Res. 967/2006","limit":"incorporación ejecutada no localizada; modelo no perfeccionado"},
    {"row_id":"RR180_08","actor":"IFI del modelo 2006","role":"garantes/coobligados previstos","proved_duty_or_right":"Anexo III formula obligaciones, aportes y débitos definidos","source":"Res. 967/2006, Anexo III","limit":"descripción textual del modelo, no hecho jurídico operativo ni garantía activada"},
    {"row_id":"RR180_09","actor":"Subprestatarios MiPyME","role":"deudores finales elegibles previstos","proved_duty_or_right":"elegibilidad, destino, documentación y garantías","source":"Res. 967/2006, Anexo I","limit":"sin operaciones atribuibles al modelo no perfeccionado"},
    {"row_id":"RR180_10","actor":"Auditor externo","role":"control independiente previsto","proved_duty_or_right":"auditorías e informes especiales","source":"Res. 967/2006, cláusula 16 y Anexo IV","limit":"no confundir informes AGN del programa con auditoría contractual del modelo"},
])

write_csv(HERE / "E0_BID1192_2006_VS_2013_ROLE_NONTRANSPOSITION_V180.csv", [
    {"row_id":"NT180R_01","dimension":"instrumento","mypes_2006":"modelo de fideicomiso Res. 967 no perfeccionado al 22/02/2008","fondyf_bna_2013":"convenio de administración BNA-FONDYF","safe_conclusion":"regímenes jurídicos distintos; el primero no se presume operativo"},
    {"row_id":"NT180R_02","dimension":"función bancaria","mypes_2006":"IFI originaría/administraría créditos y aportaría contraparte según modelo","fondyf_bna_2013":"BNA administra fondos y operaciones por cuenta del FONDYF","safe_conclusion":"no homologar funciones"},
    {"row_id":"NT180R_03","dimension":"riesgo crediticio","mypes_2006":"modelo formula garantías IFI; régimen ejecutado previo se limita por Res. 747","fondyf_bna_2013":"modelo dice que BNA no asume riesgo de crédito","safe_conclusion":"no trasladar riesgo ni solidaridad"},
    {"row_id":"NT180R_04","dimension":"garantía/indemnidad","mypes_2006":"Anexo III aprobado, no perfeccionado","fondyf_bna_2013":"sin garantía equivalente localizada","safe_conclusion":"ninguna cláusula 2006 se imputa a BNA ni se toma como hecho"},
    {"row_id":"NT180R_05","dimension":"débito automático","mypes_2006":"autorización prevista sobre cuentas IFI","fondyf_bna_2013":"sin obligación equivalente localizada","safe_conclusion":"exige instrumento ejecutado específico"},
    {"row_id":"NT180R_06","dimension":"remuneración","mypes_2006":"retribución fiduciaria/spread/costos previstos","fondyf_bna_2013":"2% de créditos efectivamente otorgados más gastos taxativos","safe_conclusion":"precios y bases diferentes"},
    {"row_id":"NT180R_07","dimension":"información","mypes_2006":"régimen trimestral/auditoría/archivo BCRA previsto","fondyf_bna_2013":"informes mensuales de operación/cobranza/mora/saldos","safe_conclusion":"pedir archivos por separado"},
    {"row_id":"NT180R_08","dimension":"transición","mypes_2006":"no se perfeccionó; el régimen 2005 terminó","fondyf_bna_2013":"recuperos integrados por Decreto 1273/2012","safe_conclusion":"falta balance/inventario contable de transferencia"},
    {"row_id":"NT180R_09","dimension":"atribución","mypes_2006":"roles sólo aprobados en modelo","fondyf_bna_2013":"obligaciones aprobadas para BNA/Programa","safe_conclusion":"ninguna imputación cruza períodos sin instrumento y ledger"},
])

write_csv(HERE / "E0_BID1192_TRUST_OPERATION_LEDGER_2005_2008_V180.csv", [
    {"row_id":"OL180_01","period":"2005-08-19/2005-12-31","vehicle":"Fideicomiso Res. 389","ifi":"Macro","operations":"10","principal_or_volume":"USD 831,246.65","other_amount":"subprestatarios USD 121,779.34; aporte local IFI USD 3,449,403.82","source":"AGN 160/2006","limit":"corte parcial"},
    {"row_id":"OL180_02","period":"2005","vehicle":"Fideicomiso Res. 389","ifi":"Credicoop","operations":"0","principal_or_volume":"USD 441,150 transferidos y reintegrados 12/01/2006","other_amount":"sin desembolso","source":"AGN 160/2006","limit":"inactividad al cierre"},
    {"row_id":"OL180_03","period":"hasta 2006-12-31","vehicle":"Fideicomiso Res. 389","ifi":"Macro","operations":"35","principal_or_volume":"USD 9,220,439.92","other_amount":"18.44% de capacidad USD 50m","source":"AGN 14/2010","limit":"no prueba calidad final de cartera"},
    {"row_id":"OL180_04","period":"2007","vehicle":"Facilidad en pesos BCRA","ifi":"múltiples IFI","operations":"1121","principal_or_volume":"ARS 535,325,410.46","other_amount":"BID + contraparte","source":"AGN 14/2010","limit":"vehículo distinto del fideicomiso"},
    {"row_id":"OL180_05","period":"2008","vehicle":"recuperos de Facilidad","ifi":"múltiples IFI","operations":"95","principal_or_volume":"ARS 47,563,240.96","other_amount":"operaciones previamente aprobadas","source":"AGN 14/2010","limit":"UCP declaró no tener mayor información sobre 10 operaciones del fideicomiso"},
    {"row_id":"OL180_06","period":"2007-2008","vehicle":"Facilidad total","ifi":"múltiples IFI","operations":"1216 investment loans per BID PCR","principal_or_volume":"ARS 582,888,651.42 AGN facility total","other_amount":"BID PCR also reports 2,598 local working-capital credits","source":"AGN 14/2010 + BID PCR","limit":"diferentes universos/unidades; no sumar sin diccionario"},
])

write_csv(HERE / "E0_BID1192_AGN_FINDINGS_LEDGER_V180.csv", [
    {"row_id":"AF180_01","audit":"AGN 160/2006","finding":"ejecución fiduciaria al cierre 2005 de USD 831,246.65 frente a mínimo USD 8m trimestral","implication":"baja ejecución y posible comisión de compromiso","proof":"documental auditado","limit":"registro financiero no mostraba penalidad; cálculo jurídico pendiente"},
    {"row_id":"AF180_02","audit":"AGN 160/2006","finding":"Credicoop sin operaciones; Macro único participante activo en primera mitad 2006","implication":"concentración operativa inicial","proof":"auditoría","limit":"no extrapolar a toda la vida del programa"},
    {"row_id":"AF180_03","audit":"AGN 160/2006","finding":"legajos/documentación faltante y demora en garantías","implication":"debilidad de control y trazabilidad","proof":"muestra 100% de ejecución crediticia 2005","limit":"no equivale automáticamente a pérdida o fraude"},
    {"row_id":"AF180_04","audit":"AGN 14/2010","finding":"todos los fondos BID ejecutados en 2007; demanda agotó recursos rápidamente","implication":"diseño sin cupos/ventanillas y control insuficiente","proof":"auditoría + comunicaciones BCRA","limit":"éxito de colocación no prueba distribución justa"},
    {"row_id":"AF180_05","audit":"AGN 14/2010","finding":"modelo Res. 967/2006 no perfeccionado al 22/02/2008","implication":"corrige cadena contractual V179","proof":"respuesta/documentación auditada","limit":"estado posterior requiere instrumento"},
    {"row_id":"AF180_06","audit":"AGN 14/2010","finding":"terminación 26/09/2008; liquidación y resolución ministerial pendientes en 2009","implication":"brecha de cierre y custodia","proof":"Exp. S01:0431231/08 y nota UCP 112/09","limit":"no prueba desvío patrimonial"},
])

write_csv(HERE / "E0_BID1192_TERMINATION_LIQUIDATION_TIMELINE_V180.csv", [
    {"row_id":"TL180_01","date":"2007-08-13","event":"BCRA suspende nuevos proyectos","record":"Com. B 9056","state":"FUNDS_FULLY_COMMITTED","open_item":"inventario definitivo de compromisos"},
    {"row_id":"TL180_02","date":"2007-08-31","event":"partes trabajan Carta de Intención de cierre","record":"AGN 14/2010","state":"CLOSURE_NEGOTIATION","open_item":"Carta firmada y anexos"},
    {"row_id":"TL180_03","date":"2008-09-26","event":"causal contractual de terminación","record":"AGN 14/2010","state":"TERMINATION_TRIGGERED","open_item":"resolución y balance de liquidación"},
    {"row_id":"TL180_04","date":"2008","event":"expediente de liquidación","record":"MECON S01:0431231/08","state":"ADMINISTRATIVE_PROCESS","open_item":"expediente completo"},
    {"row_id":"TL180_05","date":"2009-09-14","event":"UCP informa falta de resolución ministerial","record":"Nota UCP 112/09","state":"LIQUIDATION_PENDING","open_item":"acto posterior y rendición final"},
    {"row_id":"TL180_06","date":"2012-08-03","event":"Decreto 1273 crea FONDYF con recuperos","record":"Decreto 1273/2012","state":"LEGAL_SUCCESSION_FRAMEWORK","open_item":"inventario/ledger de activos transferidos"},
    {"row_id":"TL180_07","date":"2013","event":"administración BNA-FONDYF","record":"Res. 206/2012 y 48/2013","state":"NEW_REGIME","open_item":"conciliar saldo inicial con cierre 1192"},
])

write_csv(HERE / "E0_BID1192_FACILIDAD_RATE_AND_VOLUME_MATRIX_V180.csv", [
    {"row_id":"RV180_01","effective_period":"2007-02/2007-05","transfer_tna_pct":"2.9","allowed_spread_pp":"0-6","max_tna_pct":"8.9","volume_or_state":"ventanilla abierta","source":"B 8920","cft_rule":"informado; comisiones/seguros pueden elevarlo"},
    {"row_id":"RV180_02","effective_period":"2007-05/2007-08","transfer_tna_pct":"2.9","allowed_spread_pp":"0-6","max_tna_pct":"8.9","volume_or_state":"continuidad","source":"B 8995","cft_rule":"no confundir TNA con CFT"},
    {"row_id":"RV180_03","effective_period":"desde 2007-08-13","transfer_tna_pct":"3.9","allowed_spread_pp":"0-5","max_tna_pct":"8.9","volume_or_state":"nuevos proyectos suspendidos; fondos comprometidos","source":"B 9055/B 9056","cft_rule":"margen máximo se reduce 1 pp"},
    {"row_id":"RV180_04","effective_period":"desde 2007-11-13","transfer_tna_pct":"3.9","allowed_spread_pp":"0-5","max_tna_pct":"8.9","volume_or_state":"banda mantenida","source":"B 9123","cft_rule":"CFT no topado por igual regla"},
    {"row_id":"RV180_05","effective_period":"2007 total","transfer_tna_pct":"","allowed_spread_pp":"","max_tna_pct":"8.9","volume_or_state":"1121 operaciones; ARS 535,325,410.46","source":"AGN 14/2010","cft_rule":"BID PCR: TNA media 8.7%, CFT medio 10.1%, BNA CFT 7.5%"},
])

write_csv(HERE / "E0_BID1192_BCRA_OBLIGATION_AND_RATE_ARCHITECTURE_V180.csv", [
    {"row_id":"BA180_01","component":"tasa de transferencia","responsible":"BCRA/programa","rule":"costo de fondeo BID + administración","economic_incidence":"Estado absorbe riesgo cambiario tras pesificación","source":"A 4620 + BID PCR","evidence_limit":"no determina por sí sola ganancia bancaria"},
    {"row_id":"BA180_02","component":"spread","responsible":"IFI dentro de banda","rule":"0-6 pp y luego 0-5 pp","economic_incidence":"margen bruto regulado","source":"B 8920/B8995/B9055/B9123","evidence_limit":"no equivale a utilidad neta"},
    {"row_id":"BA180_03","component":"comisiones/seguros","responsible":"IFI","rule":"fijación no idénticamente topada; informar CFT; sin paquete forzoso","economic_incidence":"eleva costo total del deudor","source":"A 4620/B8920/AGN14","evidence_limit":"requiere contrato individual para cuantificar"},
    {"row_id":"BA180_04","component":"riesgo crediticio","responsible":"IFI","rule":"asume todo el riesgo y paga aun si subprestatario incumple","economic_incidence":"justifica parte del spread","source":"A 4620","evidence_limit":"pérdidas efectivas requieren cartera/mora"},
    {"row_id":"BA180_05","component":"garantía al BCRA","responsible":"IFI","rule":"cobertura mínima 125%","economic_incidence":"mitiga exposición del programa","source":"B 8920","evidence_limit":"tipo/valor de garantía por operación pendiente"},
    {"row_id":"BA180_06","component":"legajo/destino","responsible":"IFI","rule":"elegibilidad, solvencia, destino, garantías, archivo y supervisión","economic_incidence":"costo operativo y deber de diligencia","source":"A 4620","evidence_limit":"cumplimiento debe probarse por legajos"},
])

write_csv(HERE / "E0_BID1192_FACILITY_VS_TRUST_NONTRANSPOSITION_V180.csv", [
    {"row_id":"NT180_01","dimension":"vehículo","trust_2005":"patrimonio fiduciario con SIASA y dos IFI","facility_2007":"financiación BCRA a múltiples IFI","why_not_transpose":"partes y flujos distintos"},
    {"row_id":"NT180_02","dimension":"moneda","trust_2005":"estructura original USD","facility_2007":"subpréstamos en pesos","why_not_transpose":"riesgo cambiario desplazado al Estado"},
    {"row_id":"NT180_03","dimension":"tasa","trust_2005":"contrato/reglamento aplicable","facility_2007":"2.9+0-6 y 3.9+0-5; máximo 8.9","why_not_transpose":"banda 2007 no prueba tasa 2005"},
    {"row_id":"NT180_04","dimension":"garantías","trust_2005":"Res. 747 delimita cartera propia y fiduciario","facility_2007":"IFI asume riesgo y garantiza al BCRA mínimo 125%","why_not_transpose":"acreedor y mecanismo diferentes"},
    {"row_id":"NT180_05","dimension":"volumen","trust_2005-06":"35 operaciones Macro por USD 9.22m","facility_2007":"1121 operaciones por ARS 535.33m","why_not_transpose":"universos no sumables sin diccionario"},
])

write_csv(HERE / "E0_BID1192_SUQUIA_ACCESSION_STATUS_V180.csv", [
    {"row_id":"SQ180_01","event":"BCRA autoriza a Macro adquirir Nuevo Banco Suquía","evidence":"Res. BCRA 361 citada por Res. 967","status":"CORPORATE_CONTROL_PROVED","limit":"no prueba adhesión al fideicomiso"},
    {"row_id":"SQ180_02","event":"Macro solicita incorporar Suquía como IFI; partes/BID no objetan","evidence":"considerandos Res. 967","status":"REQUEST_AND_NO_OBJECTION_PROVED","limit":"no equivale a firma"},
    {"row_id":"SQ180_03","event":"art. 2 autoriza incorporación","evidence":"Res. 967","status":"ACCESSION_AUTHORIZED","limit":"ejecución no localizada"},
    {"row_id":"SQ180_04","event":"nuevo modelo Res. 967","evidence":"AGN 14/2010","status":"NOT_PERFECTED_BY_2008_02_22","limit":"no atribuir cartera/garantía efectiva a Suquía"},
])

write_csv(HERE / "E0_BID1192_FULL_MODEL_STRUCTURE_2004_2005_2006_V180.csv", [
    {"row_id":"MS180_01","version":"Res. 347/2004","pages":"87","base_contract":"1-45","annex_i":"46-53","annex_ii":"54-66","annex_iii":"67-85","annex_iv_v":"86-87","signature_state":"blank","visual_control":"87/87"},
    {"row_id":"MS180_02","version":"Res. 389/2005","pages":"89","base_contract":"1-47","annex_i":"48-54","annex_ii":"55-66","annex_iii":"67-89","annex_iv_v":"referenced but absent","signature_state":"blank; ministerial certification is not party signature","visual_control":"89/89"},
    {"row_id":"MS180_03","version":"Res. 967/2006","pages":"99","base_contract":"1-53","annex_i":"54-61","annex_ii":"62-74","annex_iii":"75-97","annex_iv_v":"98-99","signature_state":"blank","visual_control":"99/99 in V179"},
])

write_csv(HERE / "E0_BID1192_VERSION_DIFF_NONRETROACTIVITY_V180.csv", [
    {"row_id":"VD180_01","proposition":"Res. 347 model preceded executed 26/05/2004 contract","status":"SUPPORTED","source":"Res. 747/AGN23","legal_use":"identify baseline architecture","prohibition":"do not call published model signed copy"},
    {"row_id":"VD180_02","proposition":"Res. 389 contract executed 19/08/2005","status":"SUPPORTED_BY_AGN","source":"AGN160","legal_use":"operative version from that date","prohibition":"retain signed-copy gap"},
    {"row_id":"VD180_03","proposition":"Res. 967 obligations governed 2007 facility","status":"REJECTED","source":"AGN14","legal_use":"none absent perfection","prohibition":"no retroactive attribution"},
    {"row_id":"VD180_04","proposition":"FONDYF/BNA inherited identical IFI risk allocation","status":"REJECTED","source":"Decree1273/2012 and 2013 model","legal_use":"trace assets only","prohibition":"new regime says BNA does not assume credit risk"},
])

write_csv(HERE / "E0_BID1192_BID_OUTCOME_AND_EQUITY_CAVEATS_V180.csv", [
    {"row_id":"OC180_01","metric":"credit component","value":"USD 392m direct effects; USD 196m BID + USD 196m local","source":"BID PCR","interpretation":"full disbursement","caveat":"AGN 2008 financial table uses USD 194m + 194m; reconcile definition/cutoff"},
    {"row_id":"OC180_02","metric":"credits","value":"1,216 investment + 2,598 local working-capital = 3,814","source":"BID PCR","interpretation":"broad reach","caveat":"different products; not all equivalent beneficiaries"},
    {"row_id":"OC180_03","metric":"IFI reach","value":"16 IFI in product table; 17 active in results narrative","source":"BID PCR","interpretation":"national intermediation","caveat":"internal inconsistency unresolved"},
    {"row_id":"OC180_04","metric":"rates","value":"TNA weighted 8.7%; CFT 10.1%; BNA CFT 7.5%","source":"BID PCR","interpretation":"preferential fixed financing","caveat":"averages mask dispersion and fees"},
    {"row_id":"OC180_05","metric":"distribution","value":"73.6% loans below USD100k; nearly 60% value to medium firms; 73% count to small firms","source":"BID PCR","interpretation":"small firms numerous, medium firms absorb value","caveat":"equity by count differs from equity by pesos"},
    {"row_id":"OC180_06","metric":"additionality","value":"79% new bank clients or clients without prior investment finance; 15% new pure within group","source":"BID PCR","interpretation":"financial additionality reported","caveat":"self/evaluation measure, not randomized causal estimate"},
    {"row_id":"OC180_07","metric":"impact model","value":"first year +USD65m GDP, +USD16m tax, 1,850 jobs; lifetime +USD249m GDP, +USD62m tax","source":"BID PCR/CEPAL estimate","interpretation":"modeled benefit","caveat":"not audited causal outcome"},
    {"row_id":"OC180_08","metric":"equity classification","value":"not equity social project and not poverty reduction project","source":"BID proposal","interpretation":"development-credit operation","caveat":"do not retrofit poverty mandate absent legal text"},
])

write_csv(HERE / "E0_BID1192_BID_VS_AGN_EVIDENCE_RECONCILIATION_V180.csv", [
    {"row_id":"RC180_01","topic":"disbursement","bid_view":"100% credit component executed","agn_view":"rapid exhaustion in 2007","reconciliation":"consistent on volume","unresolved":"194 vs196m definition"},
    {"row_id":"RC180_02","topic":"effectiveness","bid_view":"rates, maturity, reach and additionality favorable","agn_view":"control weaknesses, legajos and demand imbalance","reconciliation":"outcome and process-control scopes differ","unresolved":"operation-level distribution/quality"},
    {"row_id":"RC180_03","topic":"trust 2005","bid_view":"program recovery after pesification","agn_view":"initially low execution and Macro concentration","reconciliation":"different phases","unresolved":"full loan ledger"},
    {"row_id":"RC180_04","topic":"closure","bid_view":"project termination report favorable","agn_view":"trust liquidation/ministerial act pending in 2009","reconciliation":"project loan closure differs from domestic trust liquidation","unresolved":"final trust accounts"},
])

write_csv(HERE / "E0_BID1192_INTERNAL_SOURCE_CONFLICTS_V180.csv", [
    {"row_id":"IC180_01","source":"BID PCR","conflict":"16 IFI in product table vs 17 active in narrative","safe_treatment":"report both; seek annex/loan database","severity":"MEDIUM"},
    {"row_id":"IC180_02","source":"BID PCR","conflict":"funds exhausted by Aug 2008 in one passage vs suspension/commitment Aug 2007","safe_treatment":"treat 2008 as likely drafting/date issue, not silently correct","severity":"HIGH_DATE"},
    {"row_id":"IC180_03","source":"BID PCR vs AGN14","conflict":"USD196m+196m vs USD194m+194m","safe_treatment":"separate approved/disbursed/direct-effect definitions","severity":"MEDIUM_VALUE"},
    {"row_id":"IC180_04","source":"Res. 967 vs AGN14","conflict":"approved/incorporation authorized vs contract not perfected","safe_treatment":"authorization is not execution","severity":"HIGH_LEGAL"},
    {"row_id":"IC180_05","source":"BID PCR vs AGN160/14","conflict":"favorable aggregate assessment vs documented control gaps","safe_treatment":"different questions; preserve both","severity":"HIGH_INTERPRETIVE"},
])


pdf_controls = [
    ("e0_bo_res347_2004_full_annex_contract_v180","87","contrato + Anexos I-V","PASS_ALL_87_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bo_res389_2005_full_annex_contract_v180","89","contrato + Anexos I-III","PASS_ALL_89_PAGES_VISUALLY_INSPECTED","SCAN"),
    ("e0_agn_res023_2005_fideicomisos_publicos_v180","93","relevamiento completo","PASS_ALL_93_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_agn_res160_2006_bid1192_fy2005_v180","99","auditoría y anexos","PASS_ALL_99_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_agn_res014_2010_bid1192_fy2008_v180","48","auditoría y anexos","PASS_ALL_48_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bid_ar0127_pcr_v180","29","informe de terminación","PASS_ALL_29_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bid_ar0127_intermediate_evaluation_v180","4","evaluación intermedia","PASS_ALL_4_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bid_ar0127_loan_proposal_v180","4","propuesta","PASS_ALL_4_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_a4620_2007_mipymes_v180","11","reglamentación","PASS_ALL_11_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_b8920_2007_mipymes_v180","33","reglamentación/banda","PASS_ALL_33_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_b8995_2007_rates_v180","1","tasa","PASS_ALL_1_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_b9055_2007_rates_v180","1","tasa","PASS_ALL_1_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_b9056_2007_suspension_v180","1","suspensión","PASS_ALL_1_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_b9123_2007_rates_v180","1","tasa","PASS_ALL_1_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
    ("e0_bcra_ordered_text_mipymes_comparator_v180","64","comparador normativo","PASS_ALL_64_PAGES_VISUALLY_INSPECTED","DIGITAL_TEXT"),
]
write_csv(HERE / "V180_PDF_VISUAL_CONTROL.csv", [
    {"control_id":f"PDF180_{i:02d}","source_id":sid,"pdf_pages":pages,"target":target,"method":"contact sheets for all pages plus selected high-resolution pages","result":result,"text_layer":layer,"limit":"visual integrity; substantive limits retained"}
    for i,(sid,pages,target,result,layer) in enumerate(pdf_controls,1)
])

html_checks = [
    ("e0_bo_res347_2004_notice_endpoint_v180","bo_resolucion_347_2004_detalle_aviso_7263053.html","00227867"),
    ("e0_bo_res389_2005_notice_endpoint_v180","bo_resolucion_389_2005_detalle_aviso_7276817.html","00292146"),
    ("e0_infoleg_res747_2004_guarantee_addenda_v180","infoleg_norma_101253_addendas_fideicomiso.html","Fideicomiso"),
    ("e0_agn_res129_2005_endpoint_gap_v180","agn_res129_2005_current_endpoint_error.html","html"),
    ("e0_agn_res129_2005_api_query_gap_v180","agn_api_res129_2005_bid1192.json","\"count\":0"),
    ("e0_wayback_agn_res129_2005_cdx_gap_v180","wayback_cdx_agn_2005_129info.json","[]"),
    ("e0_agn_api_res023_2005_metadata_v180","agn_api_res023_2005.json","\"resolucion\":23"),
    ("e0_agn_api_res160_2006_metadata_v180","agn_api_res160_2006.json","\"resolucion\":160"),
    ("e0_agn_api_res014_2010_metadata_v180","agn_api_res014_2010.json","\"resolucion\":14"),
]
html_rows = []
for i,(sid,name,target) in enumerate(html_checks,1):
    body = (HIST / name).read_text(encoding="utf-8-sig", errors="ignore")
    result = "PASS_EXACT_STRING" if target.lower() in body.lower() else "FAIL"
    assert result == "PASS_EXACT_STRING"
    html_rows.append({"control_id":f"HTML180_{i:02d}","source_id":sid,"target_string":target,"result":result,"limit":"content/provenance control; negative results are not substantive absence proof"})
write_csv(HERE / "V180_HTML_CONTENT_CONTROL.csv", html_rows)

write_csv(HERE / "V180_BO_ENDPOINT_PROVENANCE.csv", [
    {"notice":"7263053","publication":"20040513","annex_id":"00227867","local_pdf":"/"+(HIST/"bo_resolucion_347_2004_anexo_modelo_fideicomiso.pdf").relative_to(REPO).as_posix(),"pages":"87","status":"PRESERVED_AND_VISUALLY_INSPECTED"},
    {"notice":"7276817","publication":"20050711","annex_id":"00292146","local_pdf":"/"+(HIST/"bo_resolucion_389_2005_anexo_modelo_fideicomiso.pdf").relative_to(REPO).as_posix(),"pages":"89","status":"PRESERVED_AND_VISUALLY_INSPECTED"},
])

write_csv(HERE / "V180_SOURCE_BUNDLE.csv", [
    {"source_id":s["id"],"institution":s["institucion"],"title":s["titulo"],"url":s["url_original"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str((REPO/s["archivo_local"].lstrip("/")).stat().st_size),"evidentiary_role":"contract/audit/program/rate/provenance","limit":s["nota"]}
    for s in sources
])

write_csv(HERE / "V180_PUBLIC_SEARCH_LOG.csv", [
    {"query_id":"PS180_01","query":"BO Resolución 347/2004 anexos","result":"Aviso 7263053; Anexo 00227867 preserved","artifact":"87-page PDF + notice HTML","limit":"approved model"},
    {"query_id":"PS180_02","query":"BO Resolución 389/2005 anexos","result":"Aviso 7276817; Anexo 00292146 preserved","artifact":"89-page PDF + notice HTML","limit":"approved model"},
    {"query_id":"PS180_03","query":"Infoleg Resolución 747/2004 fideicomiso garantía","result":"full addenda located","artifact":"official HTML","limit":"published annex unsigned"},
    {"query_id":"PS180_04","query":"AGN BID 1192 ejercicio 2005","result":"Res. 160/2006 located","artifact":"99-page audit","limit":"signed contract still missing"},
    {"query_id":"PS180_05","query":"AGN BID 1192 ejercicio 2008","result":"Res. 14/2010 located","artifact":"48-page audit","limit":"liquidation later state open"},
    {"query_id":"PS180_06","query":"AGN Res. 129/2005 BID1192","result":"legacy endpoint/API/Wayback negative","artifact":"three preserved gap controls","limit":"absence in index is not absence of report"},
    {"query_id":"PS180_07","query":"BID AR0127 project completion report","result":"PCR, intermediate evaluation and proposal located","artifact":"three official PDFs","limit":"internal conflicts retained"},
    {"query_id":"PS180_08","query":"BCRA A4620 B8920 B8995 B9055 B9056 B9123","result":"complete 2007 rule/rate chain located","artifact":"six communications","limit":"facility distinct from trust"},
])

objects = read_csv(HERE / "E0_V180_REQUEST_OBJECTS.csv")
new_objects = [
    ("RO180_60","MYPESII_SIGNED_2004","Ministerio de Economía / Archivo General","Contrato de Fideicomiso y Garantía e Indemnidad ejecutados el 26/05/2004, cinco ejemplares","2004","instrumento íntegro; firmas; personería; anexos; certificaciones","contraparte ejecutada completa o constancia formal de búsqueda"),
    ("RO180_61","MYPESII_SIGNED_ADDENDA_2005","Ministerio de Economía / SIASA","Addenda ejecutada el 22/03/2005 aprobada por Res. 148/2005","2005","firma; fecha; anexos; registración","contraparte ejecutada"),
    ("RO180_62","MYPESII_SIGNED_2005","Ministerio de Economía / SIASA","Contrato ejecutado el 19/08/2005 bajo Res. 389/2005","2005","contrato; anexos I-V; firmas; certificaciones","contraparte ejecutada"),
    ("RO180_63","MYPESII_CLAUSE16_REPORTS","Ministerio/BCRA/SIASA","Rendiciones, cartera, mora, tasas, previsiones, gastos, juicios, auditorías y archivos mensuales","2004-2009","fecha; IFI; crédito; saldo; tasa; mora; garantía; archivo","serie completa o inventario de huecos"),
    ("RO180_64","MYPESII_GUARANTEE_EVENTS","BCRA/SIASA/Macro/Credicoop","Avisos, aportes, débitos y acciones de garantía/indemnidad","2004-2009","obligación; IFI; fecha; saldo; aviso; débito; pago; cierre","ledger completo incluso cero eventos certificado"),
    ("RO180_65","MYPESII_LIQUIDATION_FILE","Ministerio de Economía","Expediente S01:0431231/08 y resolución de liquidación","2008-2013","Carta de cierre; acto; inventario; balance; rendición; remanente","expediente íntegro y acto final"),
    ("RO180_66","MYPESII_FACILITY_LEDGER","BCRA/UCP","Base operación por operación de la Facilidad en pesos 2007-2008","2007-2008","IFI; subprestatario seudonimizado; monto; TNA; CFT; comisión; seguro; plazo; destino; estado","dataset y diccionario"),
    ("RO180_67","MYPESII_FONDYF_HANDOFF","Ministerio/BNA","Inventario y conciliación de recuperos BID 643/867/1192 transferidos a FONDYF","2008-2013","cuenta; saldo; crédito; mora; garantía; fecha de corte; asiento de apertura","puente saldo final 1192 a saldo inicial FONDYF"),
    ("RO180_68","MYPESII_RES967_ACCESSION","Ministerio/Macro/Suquía/SIASA","Instrumento de perfeccionamiento Res. 967 e incorporación de Nuevo Banco Suquía, si existió","2006-2009","firma; fecha; adhesión; anexos; vigencia; baja","documento o certificación de no perfeccionamiento definitivo"),
]
for row_id, object_id, custodian, record, period, fields, closure in new_objects:
    objects.append({"row_id":row_id,"object_id":object_id,"custodian":custodian,"exact_record":record,"period":period,"minimum_fields":fields,"closure_rule":closure,"status":"DRAFT_NOT_SENT"})
objects = list({x["row_id"]:x for x in objects}.values())
write_csv(HERE / "E0_V180_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V180_REQUEST_OBJECTS_V180.csv", objects)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V180.csv")
new_keys = [
    ("SK180_62","REQ180_MYPESII","date","26/05/2004;22/03/2005;19/08/2005","contrapartes ejecutadas","Res747; AGN160","fecha oficial no sustituye documento"),
    ("SK180_63","REQ180_MYPESII","expedient","S01:0264727/2004","addendas/garantías","Res747","pedir cuerpo y anexos"),
    ("SK180_64","REQ180_MYPESII","expedient","S01:0431231/08","liquidación","AGN14","pedir resolución y balance"),
    ("SK180_65","REQ180_MYPESII","note","UCP 112/09 de 14/09/2009","estado de liquidación","AGN14","pedir adjuntos/respuesta"),
    ("SK180_66","REQ180_MYPESII","record_family","Carta de Intención de cierre al 31/08/2007","cierre contractual","AGN14","pedir versión firmada"),
    ("SK180_67","REQ180_MYPESII","record_family","cláusula 16; archivos mensuales de deudores","desempeño y control","modelos 2004-2005","pedir diccionario y serie"),
    ("SK180_68","REQ180_MYPESII","communication","A4620;B8920;B8995;B9055;B9056;B9123","facility ledger/rates","BCRA","norma no sustituye contratos"),
    ("SK180_69","REQ180_MYPESII","account","recuperos 643/867/1192; FONDYF","transición patrimonial","Decreto1273","pedir puente de saldos"),
]
for key_id, request_id, group, exact, purpose, basis, caveat in new_keys:
    keys.append({"key_id":key_id,"request_id":request_id,"key_group":group,"exact_key":exact,"search_purpose":purpose,"source_or_basis":basis,"caveat":caveat})
keys = list({x["key_id"]:x for x in keys}.values())
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V180.csv", keys)

(HERE / "CORRECTION_LOG_V180.md").write_text("""# Correcciones V180

1. **Garantías IFI:** V179 describía con excesiva amplitud la solidaridad Macro-Credicoop del modelo 2006. La Res. 747/2004 delimita el régimen ejecutado: cada IFI garantiza el riesgo de los créditos que ella descontó, hasta ese monto; Macro garantiza en forma exclusiva las obligaciones específicas del fiduciario.
2. **Res. 967/2006:** queda rebajada de posible versión operativa a **modelo aprobado no perfeccionado al 22/02/2008**, según AGN 14/2010. La incorporación de Nuevo Banco Suquía fue autorizada, pero no está probado que se ejecutara.
3. **Prueba de ejecución:** las fechas 26/05/2004, 22/03/2005 y 19/08/2005 ya no quedan como mera hipótesis: están corroboradas por normas/auditoría oficial. Aun así, ninguna referencia sustituye la contraparte firmada.
4. **Vehículos:** el fideicomiso 2005 y la Facilidad en pesos 2007 se separan estrictamente. Sus tasas, IFI, garantías, moneda y universos no se transponen.
5. **Resultado vs control:** el informe BID aporta alcance y resultados agregados; AGN aporta observaciones de ejecución, documentación y cierre. No se descarta ninguno: responden preguntas distintas.
6. **Inconsistencias internas:** se registran 16/17 IFI, agosto 2007/2008 y USD 194/196 millones sin corregirlos silenciosamente.
7. **Daño:** ninguna observación de legajo, demora, concentración o liquidación pendiente se convierte por sí sola en fraude, apropiación, pérdida o daño indemnizable.
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V180.csv")
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    local_census.append({"source_id":s["id"],"institution":s["institucion"],"artifact":s["titulo"],"url":s["url_original"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"period_coverage":s["periodo_utilizado"],"variable_families":"BID1192;trust;facility;rates;guarantees;performance;closure","primary_source":"YES" if "control negativo" not in s["tipo"].lower() else "NO_TECHNICAL_CONTROL","preserved":"YES","method_breaks":"model/executed; trust/facility; aggregate/operation","use_status":"E0_USABLE_WITH_STATED_LIMITS","caveat":s["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V180.csv", list({x["source_id"]:x for x in local_census}.values()))

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V180.csv")
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    prov.append({"source_id":s["id"],"original_url":s["url_original"],"retrieval_url":s["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_DIRECT_OR_RECORDED_NEGATIVE_QUERY","local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"provenance_note":s["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V180.csv", list({x["source_id"]:x for x in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V180.md").open("a", encoding="utf-8") as f:
    f.write("\n## V180 · contratos, auditorías, resultados BID y arquitectura BCRA\n")
    for s in sources:
        f.write(f"\n- `{s['id']}` · {s['titulo']} · {s['url_original']} · `{s['archivo_local']}` · `{s['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V180.md").open("a", encoding="utf-8") as f:
    f.write("""
## V180

- Se preservaron los anexos BO Res. 347/2004 (87 páginas) y Res. 389/2005 (89 páginas), ambos modelos sin firmas de las partes.
- Res. 747/2004 y AGN 23/2005/160/2006 corroboran fecha y partes de instrumentos ejecutados; las contrapartes firmadas siguen pendientes.
- AGN 160/2006 reconstruye la fase fiduciaria inicial y sus brechas; AGN 14/2010 reconstruye la Facilidad en pesos, terminación y liquidación pendiente.
- El BID aporta diseño, terminación, tasas, distribución y estimaciones; se retienen sus conflictos internos y límites de causalidad/equidad.
- A 4620 y B 8920/8995/9055/9056/9123 prueban la fórmula de tasa, el tope TNA 8,9%, deberes IFI, asunción de riesgo y cierre por fondos comprometidos.
- No se enviaron solicitudes; los nueve pedidos nuevos permanecen DRAFT_NOT_SENT.
""")

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{"source_id":s["id"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str((REPO/s["archivo_local"].lstrip("/")).stat().st_size)} for s in sources]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V180.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V180.csv", [{"source_id":s["id"],"url":s["url_original"],"retrieval":"DIRECT_OFFICIAL_OR_PRESERVED_QUERY","status":"PRESERVED"} for s in sources])
(SYNC / "SOURCE_SYNC_REPORT_V180.md").write_text("# Sincronización V180\n\n- Catálogo 673/673; hashes válidos; brecha física 0.\n- 24 artefactos nuevos preservados: 15 PDF y 9 objetos HTML/JSON de contenido/procedencia/gap.\n- Quince PDF inspeccionados visualmente, página por página.\n- Controles negativos AGN 129/2005 no se usan como prueba de inexistencia.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v180.py").write_text("""from pathlib import Path
import csv,hashlib
H=Path(__file__).resolve().parent; R=H.parents[4]
rows=list(csv.DictReader((H/'SOURCE_SYNC_FILE_MANIFEST_V180.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==24
for x in rows:
 p=R/x['local_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(x['bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print('SOURCE SYNC V180 PASS · 24/24')
""", encoding="utf-8")

(HERE / "README_V180.md").write_text(f"""# Checkpoint V180

## Hallazgo principal

V180 cambia el estado probatorio de MyPES II(a): ya no tenemos sólo modelos normativos. La Resolución 747/2004 y las auditorías AGN corroboran que el contrato y la garantía se celebraron el 26/05/2004, que una addenda se ejecutó el 22/03/2005 y que el contrato Res. 389 se ejecutó el 19/08/2005. Las copias con firmas aún no fueron localizadas, de modo que la prueba sube a **ejecución oficialmente corroborada, contraparte íntegra pendiente**.

## Corrección decisiva

- Cada IFI responde por el riesgo de los créditos que ella descontó y sólo hasta ese monto.
- Macro-Bansud responde en forma exclusiva por obligaciones específicas del fiduciario.
- El modelo Res. 967/2006 no estaba perfeccionado al 22/02/2008. Nuevo Banco Suquía fue autorizado, pero su adhesión ejecutada no está probada.
- Por ello se corrige cualquier lectura amplia/solidaria de V179 y se impide usar el modelo 2006 como contrato operativo.

## Reconstrucción económica

- La fase fiduciaria inicial fue lenta y concentrada en Macro: 10 préstamos por USD 831.246,65 al cierre 2005; Credicoop no había operado y reintegró USD 441.150 en enero 2006. Hasta fin de 2006 Macro había colocado 35 operaciones por USD 9,22 millones.
- La Facilidad en pesos 2007 fue otro vehículo. Colocó 1.121 operaciones por ARS 535,33 millones; 95 operaciones previamente aprobadas por ARS 47,56 millones se atendieron en 2008 con recuperos.
- La TNA máxima fue 8,9% durante toda la ventana: primero 2,9% de transferencia + hasta 6 pp, luego 3,9% + hasta 5 pp. Comisiones y seguros podían elevar el CFT; el BID informa promedios de 8,7% TNA y 10,1% CFT.
- La IFI asumía el riesgo crediticio, debía pagar al BCRA aun si el subprestatario no pagaba, verificar elegibilidad/destino/garantías, conservar legajo y soportar inspección. Eso justifica parte del spread, pero no elimina el deber de demostrar costo, riesgo y diligencia operación por operación.

## Resultado y justicia distributiva

El BID reporta 100% del componente de crédito, 1.216 créditos de inversión, 2.598 créditos locales de capital de trabajo, alcance nacional y plazos largos. También informa que casi 60% del valor fue a empresas medianas aunque 73% de la cantidad fue a pequeñas, y clasifica el diseño original como no orientado específicamente a equidad social ni reducción de pobreza. La AGN documenta, a la vez, legajos faltantes, demoras de garantías, concentración inicial, agotamiento acelerado sin cupos adecuados y liquidación pendiente. El resultado agregado favorable no borra los déficits de control; los déficits de control tampoco prueban daño sin ledger, cartera y balance final.

## Cierre y sucesión

La ventanilla se suspendió el 13/08/2007 por recursos totalmente comprometidos. El fideicomiso alcanzó causal de terminación el 26/09/2008 y seguía sin resolución ministerial de liquidación en septiembre de 2009. El Decreto 1273/2012 aporta el puente jurídico hacia FONDYF, pero falta el puente contable: inventario de créditos/recuperos, balance de liquidación y asiento inicial BNA-FONDYF.

## Estado de control

- Archivo: **673/673** fuentes físicas con SHA-256 válido; 24 fuentes nuevas.
- PDF: **15/15 documentos, todas sus páginas inspeccionadas visualmente**.
- Modelos 2004/2005/2006: 87/89/99 páginas; firmas en blanco en las publicaciones.
- Panel bancario histórico: 34 entidades; {NUMERATOR}/{ASSETS}; {COVERAGE}%.
- Solicitudes enviadas: 0. Nueve objetos nuevos permanecen `DRAFT_NOT_SENT`.
- Daño, apropiación, garantía activada y beneficio indebido: no probados.
""", encoding="utf-8")

(HERE / "VEREDICTO_V180.md").write_text("""# Veredicto V180

V180 cierra una brecha jurídica importante y abre otra más precisa. La existencia y fechas de los instrumentos 2004-2005 quedan corroboradas por fuentes oficiales; la distribución de garantías queda limitada por la Res. 747/2004; y el modelo Res. 967/2006 queda descartado como contrato operativo al menos hasta el 22/02/2008. Económicamente se separan el fideicomiso inicial y la Facilidad en pesos: la segunda tuvo una TNA máxima regulada de 8,9%, riesgo crediticio a cargo de las IFI y CFT potencialmente superior por cargos. El programa produjo volumen y alcance, pero también observaciones de control y cierre. La afirmación defendible es que existe una obligación fuerte de rendición, trazabilidad y conciliación distributiva; todavía no existe prueba suficiente para afirmar daño, apropiación o responsabilidad indemnizatoria de una entidad determinada.
""", encoding="utf-8")

(HERE / "AUDITORIA_V180.md").write_text(f"""# Auditoría V180

- 673/673 fuentes físicas; SHA-256 válido; 24 artefactos nuevos.
- 15 PDF inspeccionados visualmente en todas sus páginas: 565 páginas nuevas en total.
- 9 controles HTML/JSON PASS; tres rutas negativas de AGN 129/2005 preservadas sin convertirlas en ausencia sustantiva.
- Matrices nuevas/corregidas: versiones, escalera de ejecución, garantías, operaciones, hallazgos AGN, liquidación, tasas/volúmenes, obligaciones BCRA, no transposición, Suquía, estructura, no retroactividad, resultados/equidad, reconciliación BID-AGN y conflictos internos.
- Contratos 2004/2005: fechas de ejecución corroboradas; copias firmadas no localizadas.
- Res. 967/2006: aprobado, no perfeccionado al 22/02/2008.
- Panel 34; {COVERAGE}%; solicitudes 0; daño no probado.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V180_A_V181.md").write_text("""# Handover V180 → V181

## Cerrado
- Anexos completos Res. 347/2004 y 389/2005 preservados y revisados.
- Fechas de ejecución 26/05/2004, 22/03/2005 y 19/08/2005 corroboradas oficialmente.
- Alcance de garantías corregido por Res. 747/2004.
- Res. 967/2006 clasificada como no perfeccionada al 22/02/2008.
- Fideicomiso 2005 y Facilidad 2007 separados; tasas, volumen, deberes IFI y resultados reconstruidos.
- Terminación/liquidación y transición jurídica FONDYF trazadas.

## Prioridad V181
1. Recuperar las tres contrapartes ejecutadas y el expediente S01:0264727/2004.
2. Recuperar Exp. S01:0431231/08, Carta de Intención, resolución y balance final de liquidación.
3. Obtener ledger operación por operación con TNA, CFT, comisiones, seguros, destino, mora, pérdidas y garantías.
4. Obtener reportes cláusula 16, auditorías externas, archivos mensuales BCRA y eventos de garantía.
5. Conciliar balance final BID1192 con inventario/contabilidad inicial FONDYF-BNA.
6. Reconciliar 16/17 IFI, agosto 2007/2008 y USD 194/196 millones con bases originales.
7. Mantener separados éxito agregado, falla de control, daño y responsabilidad jurídica.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V179.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V180","date":"2026-09-01","master_catalog_entries":673,"physical_local_copies":673,"physical_local_hash_ok":673,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"MYPESII_2004_2005_EXECUTION_DATES_CORROBORATED_RES967_NOT_PERFECTED_FACILITY_AND_CLOSURE_RECONSTRUCTED_SIGNED_COUNTERPARTS_AND_LEDGER_OPEN",
    "analytical_promotion":"CONTRACT_EXECUTION_REFERENCE_AND_RATE_ARCHITECTURE_ONLY_NO_DAMAGE_PROMOTION_V180",
    "mypesii_2004_contract_execution_date_officially_corroborated":True,"mypesii_2005_addenda_execution_date_officially_corroborated":True,"mypesii_2005_contract_execution_date_officially_corroborated":True,
    "mypesii_signed_executed_counterparts_located":False,"mypesii_res967_perfected_by_2008_02_22":False,"mypesii_suquia_executed_accession_located":False,
    "mypesii_res747_ifi_own_portfolio_limit_proved":True,"mypesii_res747_macro_fiduciary_exclusive_guarantee_proved":True,"mypesii_guarantee_execution_proved":False,
    "mypesii_agn_fy2005_audit_located":True,"mypesii_agn_fy2008_audit_located":True,"mypesii_facility_rate_architecture_proved":True,"mypesii_facility_operation_ledger_located":False,
    "mypesii_trust_termination_trigger_proved":True,"mypesii_final_liquidation_balance_located":False,"mypesii_fondyf_legal_transition_located":True,"mypesii_fondyf_accounting_handoff_located":False,
    "bid1192_damage_or_appropriation_proved":False,"requests_submitted":0,"responses_received":0,"saf355_certifications_located":0,"executed_historical_bank_rows_confirmed":0,
    "new_v180_sources":24,"v180_pdf_documents":15,"v180_pdf_pages_visually_inspected":565,"public_web_queries_v180":8,"strict_coverage_increment_v180_pp":"0",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V180.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V180","note":"official BO/Infoleg/AGN/BID/BCRA artifact or explicit negative endpoint control; verified"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V180","note":"24-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V180","note":"BID1192 contracts-audits-facility checkpoint"}
for path in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V180.csv", AUDIT/"SOURCE_BACKUP_CENSUS_V180.csv", AUDIT/"SOURCE_PRESERVATION_MISSING_V180.csv", AUDIT/"CURRENT_SOURCE_COMPLETENESS_V180.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V180","note":"673-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V180 · contratos ejecutados, auditorías y Facilidad en pesos" not in body:
    body += "\n\n## V180 · contratos ejecutados, auditorías y Facilidad en pesos\n\nLas fechas de ejecución 2004-2005 quedan corroboradas por fuentes oficiales, pero las contrapartes firmadas no están preservadas. Res. 747 limita la garantía de cada IFI a su cartera y reserva a Macro la garantía del fiduciario. Res. 967/2006 no estaba perfeccionada al 22/02/2008. La Facilidad 2007 tuvo TNA máxima 8,9%, CFT mayor posible y riesgo crediticio IFI. Éxito agregado, fallas de control, daño y responsabilidad se mantienen como proposiciones separadas. Archivo 673/673; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V180; 673/673 fuentes; 24 nuevas.\n- Contratos 2004-2005: ejecución oficialmente corroborada, copias firmadas pendientes.\n- Res. 747 corrige alcance de garantías; Res. 967 no perfeccionada al 22/02/2008.\n- Facilidad 2007: TNA máxima 8,9%, riesgo IFI, 1.121 operaciones/ARS 535,33m.\n- Liquidación y puente contable FONDYF abiertos; daño no probado.\n- Panel 34, {COVERAGE}%; solicitudes 0.\n", encoding="utf-8")

(HERE / "qa_v180.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==673
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V180.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==673 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V180.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V180' and co['master_catalog_entries']==673
assert co['mypesii_2004_contract_execution_date_officially_corroborated'] and co['mypesii_2005_contract_execution_date_officially_corroborated']
assert not co['mypesii_signed_executed_counterparts_located'] and not co['mypesii_res967_perfected_by_2008_02_22'] and not co['mypesii_suquia_executed_accession_located']
assert co['mypesii_res747_ifi_own_portfolio_limit_proved'] and co['mypesii_res747_macro_fiduciary_exclusive_guarantee_proved'] and not co['mypesii_guarantee_execution_proved']
assert co['mypesii_facility_rate_architecture_proved'] and not co['mypesii_facility_operation_ledger_located'] and not co['mypesii_final_liquidation_balance_located'] and not co['bid1192_damage_or_appropriation_proved']
assert len(rows('V180_SOURCE_BUNDLE.csv'))==24 and len(rows('V180_PDF_VISUAL_CONTROL.csv'))==15 and all(x['result'].startswith('PASS_ALL_') for x in rows('V180_PDF_VISUAL_CONTROL.csv'))
assert len(rows('V180_HTML_CONTENT_CONTROL.csv'))==9 and all(x['result']=='PASS_EXACT_STRING' for x in rows('V180_HTML_CONTENT_CONTROL.csv'))
assert len(rows('E0_BID1192_CONTRACT_VERSION_CONTROL_2003_2008_V180.csv'))==8
assert len(rows('E0_BID1192_EXECUTED_INSTRUMENT_EVIDENCE_LADDER_V180.csv'))==4
assert len(rows('E0_BID1192_RES747_GUARANTEE_LIMITATION_MATRIX_V180.csv'))==4
assert len(rows('E0_BID1192_IFI_GUARANTEE_INDEMNITY_MATRIX_V180.csv'))==5
assert len(rows('E0_BID1192_TRUST_OPERATION_LEDGER_2005_2008_V180.csv'))==6
assert len(rows('E0_BID1192_AGN_FINDINGS_LEDGER_V180.csv'))==6
assert len(rows('E0_BID1192_TERMINATION_LIQUIDATION_TIMELINE_V180.csv'))==7
assert len(rows('E0_BID1192_FACILIDAD_RATE_AND_VOLUME_MATRIX_V180.csv'))==5
assert len(rows('E0_BID1192_BCRA_OBLIGATION_AND_RATE_ARCHITECTURE_V180.csv'))==6
assert len(rows('E0_BID1192_INTERNAL_SOURCE_CONFLICTS_V180.csv'))==5
obj=rows('E0_V180_REQUEST_OBJECTS.csv'); targets={f'RO180_{x}' for x in range(60,69)}; assert targets<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V180_REQUEST_OBJECTS_V180.csv')
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V180.csv'); assert {f'SK180_{x}' for x in range(62,70)}<={x['key_id'] for x in keys}
panel=rows('FOUR_LEG_PASS_PANEL_V180.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V180.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V180' and m['parent_checkpoint']=='V179' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V180 QA PASS · 673/673 · new=24 · PDF=15/15 FULL VISUAL · EXECUTION_DATES=CORROBORATED · RES967=NOT_PERFECTED · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x:x.name.casefold()) if p.is_file() and p.name!="MANIFEST_V180.json"]
manifest = {
    "checkpoint":"V180","parent_checkpoint":"V179","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,
    "new_promotions":[],"source_archive":"673/673; 24 new official/technical artifacts","historical_finding":"2004-2005 execution dates corroborated; guarantee scope corrected; Res967 not perfected; 2007 facility and closure reconstructed; signed counterparts/ledger/liquidation open",
    "mypesii_signed_counterparts":"NOT_LOCATED","mypesii_res967":"NOT_PERFECTED_BY_2008_02_22","ifi_guarantee_scope":"CORRECTED_RES747","facility_max_tna_pct":"8.9",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":manifest_files,
}
(HERE / "MANIFEST_V180.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V180","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"673 master; 673 physical SHA-valid","historical_workstream":"BID1192 execution dates, guarantee scope, facility and closure reconstructed; signed counterparts/ledger/liquidation/damage open; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V180tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V180 BUILD PASS · catalog=673/673 · new=24 · PDF=15 full visual · EXECUTION_DATES=CORROBORATED · RES967=NOT_PERFECTED · panel=34 · requests=0")
