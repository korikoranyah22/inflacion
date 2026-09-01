from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv, hashlib, json, os

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V172"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v173"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v173"
HIST = HIST_ROOT / "binaries"
QUERY = HIST_ROOT / "query_logs"
METHODS = HIST_ROOT / "methods"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}

RES_TEXT = HIST / "infoleg_sigen_resolution_41_2007_text.html"
BO_PDF = HIST / "hcdn_bo_31194_2007_07_12_first_section.pdf"
ORG22 = HIST / "sigen_organization_2022_mesa_gde_digital_notes_archive.pdf"
WEB_SEARCH = HIST / "sigen_archiveweb_public_reports_search.html"
WEB_145 = HIST / "sigen_archiveweb_pre2009_record_id145.html"
RES_SUMMARY = HIST / "infoleg_sigen_resolution_41_2007_summary.html"
RES_INDEX = HIST / "infoleg_resolution_7_2003_modifiers_index.html"
CC = QUERY / "commoncrawl_health_control_2014_49.csv"
SCANNER = METHODS / "commoncrawl_exact_prefix_scanner_v173.ps1"
EXPECTED = {
    RES_TEXT: (37714, "9ae2e5eb12df63e37daaa1456d3fe2131ea58bde7a4914195f80ead38b7412e9"),
    BO_PDF: (3695610, "9e69a91e91810bf3613f853d080e62a73d3c0d0c891e9245bde8a284c9930e97"),
    ORG22: (790216, "74d3836f28e8ee6c2784d974e7532d495f833235fa8cddae960004be5bbb7f99"),
    WEB_SEARCH: (26458, "e9495bda9d5e8c1ab406bc940b22aaea213f613f38c9431ced1af0d64b2b59a9"),
    WEB_145: (11691, "e183dca60a0a963faad65154561e5be8dd58fb3c605d74a925dfa538b5fdc700"),
    RES_SUMMARY: (33245, "eda11fae3436f51576557efa52cb1970ece8f2576a1985cc7893909065f99010"),
    RES_INDEX: (31494, "74135f5681188e6aa50460acdfE874394edc831c9aeb2e187770ad50e0a615b8".lower()),
    CC: (794, "2a9b600379927c12b485169e6541c34194421effea0d83a4ebe13f604d8912f9"),
    SCANNER: (6014, "e4fede8e068fecb83702b5d11e5b515b92a1f8d8f4b4e7b03270ae151838457a"),
}

def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def write_csv(path, rows, fields=None):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def iter_files(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted((x for x in dns if x not in EXCLUDED), key=str.casefold)
        for fn in sorted(fns, key=str.casefold): yield Path(dp) / fn

def tree(root):
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted((x for x in dns if x not in EXCLUDED), key=str.casefold); base = Path(dp)
        out += [(base/x).relative_to(root).as_posix()+"/" for x in dns]
        out += [(base/x).relative_to(root).as_posix() for x in sorted(fns, key=str.casefold)]
    return "\n".join(out)+"\n"

def clone_parent():
    skip = {
        "MANIFEST_V172.json", "README_V172.md", "VEREDICTO_V172.md", "AUDITORIA_V172.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V172_A_V173.md", "V172_SOURCE_BUNDLE.csv",
        "V172_PUBLIC_SEARCH_LOG.csv", "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V172.md",
        "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V172.md", "E0_FISCAL_RECONSTRUCTION_V172.md",
        "CNV_ATTACHMENT_ANALYTIC_REVIEW_V172.md",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p:p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_","qa_")): continue
        dst = HERE / src.name.replace("V172","V173")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V172","V173"), encoding="utf-8")

HERE.mkdir(parents=True, exist_ok=True); clone_parent()
for path, (size, digest) in EXPECTED.items(): assert path.is_file() and path.stat().st_size == size and sha(path) == digest

sources = [
    {"id":"e0_sigen_resolution_41_2007_cidd_spd_full_text_v173","tema":"ciclo_ajuste_e0_fiscal","institucion":"Sindicatura General de la Nación / Infoleg","titulo":"Resolución SIGEN 41/2007 · procedimiento Archivo Digital, CIDD y SPD","url_original":"https://www.argentina.gob.ar/normativa/nacional/norma-130039/texto","archivo_local":"/"+RES_TEXT.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31","fecha_publicacion":"2007-07-12","codigo_serie":"Resolución SIGEN 41/2007 · BO 31.194 p.34","periodo_utilizado":"2007-2009","tipo":"HTML oficial completo preservado · TLS válido","sha256":EXPECTED[RES_TEXT][1],"nota":"V173: recupera el cuerpo y anexo. Identifica sistema Archivo Digital, código NOT, CIDD, SPD, control de integridad y vínculo a caja física. No contiene el registro concreto de Nota 3672/09."},
    {"id":"e0_hcdn_bo_31194_sigen_resolution_41_2007_annexes_v173","tema":"ciclo_ajuste_e0_fiscal","institucion":"Honorable Cámara de Diputados / Boletín Oficial","titulo":"Boletín Oficial 31.194 · Resolución SIGEN 41/2007 y anexos gráficos","url_original":"https://www4.hcdn.gob.ar/BO/boletin07/2007-07/BO12-07-2007leg.pdf","archivo_local":"/"+BO_PDF.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31","fecha_publicacion":"2007-07-12","codigo_serie":"BO 31.194 · Primera Sección · páginas 34-35","periodo_utilizado":"2007-2009","tipo":"PDF oficial histórico preservado · control visual páginas PDF 34-35","sha256":EXPECTED[BO_PDF][1],"nota":"V173: conserva CIDD y formulario SPD legibles. Campos: tipo NOT, número oficio/expediente, fecha, anexos, referencia, palabras clave, acceso y caja; SPD agrega archivo, tratamiento, folios y conformidades. No prueba carga del target."},
    {"id":"e0_sigen_resolution_223_2022_annex2_gde_digital_notes_archive_v173","tema":"ciclo_ajuste_e0_fiscal","institucion":"Sindicatura General de la Nación","titulo":"Resolución SIGEN 223/2022 · Anexo II, Mesa GDE y archivo digital de Notas","url_original":"https://www.argentina.gob.ar/sites/default/files/2018/11/if-2022-42340125-apn-snisigen.pdf","archivo_local":"/"+ORG22.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31","fecha_publicacion":"2022-05-04","codigo_serie":"Resolución SIGEN 223/2022 · IF-2022-42340125-APN-SNI#SIGEN","periodo_utilizado":"2022; extremo de migración posterior","tipo":"PDF oficial preservado · control visual PDF p.7","sha256":EXPECTED[ORG22][1],"nota":"V173: Mesa mantiene entradas/egresos mediante GDE y administra archivo digital de Notas SIGEN. Justifica pedir crosswalk legado→GDE/Archivo Digital; no retroproyecta un ID GDE a 2009."},
    {"id":"e0_sigen_archiveweb_public_reports_search_schema_v173","tema":"ciclo_ajuste_e0_fiscal","institucion":"Sindicatura General de la Nación","titulo":"ArchivoWeb SIGEN · buscador público limitado a informes","url_original":"https://www.sigen.gob.ar/archivoweb/Buscador.aspx","archivo_local":"/"+WEB_SEARCH.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31","fecha_publicacion":"","codigo_serie":"ArchivoWeb/Buscador.aspx","periodo_utilizado":"1993-2026; interfaz vigente al 2026-08-31","tipo":"HTML oficial dinámico preservado · TLS válido","sha256":EXPECTED[WEB_SEARCH][1],"nota":"V173: interfaz filtra año, 12 tipos de informe, palabras clave y organismo; no expone tipo NOT/Nota. Un cero aquí no es negativo válido para Nota 3672/09."},
    {"id":"e0_sigen_archiveweb_pre2009_record_id145_v173","tema":"ciclo_ajuste_e0_fiscal","institucion":"Sindicatura General de la Nación","titulo":"ArchivoWeb SIGEN · registro IdDocumento 145 de año 2006","url_original":"https://www.sigen.gob.ar/ArchivoWeb/ArchivosAdjuntos_Ver.aspx?IdDocumento=145","archivo_local":"/"+WEB_145.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-31","fecha_publicacion":"2006","codigo_serie":"ArchivoWeb IdDocumento=145","periodo_utilizado":"2006; comparador pre-target","tipo":"HTML oficial preservado · TLS válido","sha256":EXPECTED[WEB_145][1],"nota":"V173: prueba que la superficie actual contiene IDs y metadatos de informes previos a 2009. No demuestra que publique el universo interno ni Notas SIGEN."},
]

catalog = read_csv(CATALOG); fields = list(catalog[0]); byid = {r["id"]:r for r in catalog}
for r in sources: byid[r["id"]] = r
catalog = list(byid.values()); write_csv(CATALOG,catalog,fields); assert len(catalog)==607
audit=[]
for r in catalog:
    p=REPO/r["archivo_local"].lstrip("/"); actual=sha(p) if p.is_file() else ""
    audit.append({"id":r["id"],"archivo_local":r["archivo_local"],"exists":str(p.is_file()),"sha_catalog":r["sha256"].lower(),"sha_actual":actual,"hash_ok":str(p.is_file() and bool(r["sha256"]) and actual==r["sha256"].lower())})
write_csv(AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V173.csv",audit); write_csv(AUDIT/"SOURCE_BACKUP_CENSUS_V173.csv",audit)
missing=[r for r in audit if r["hash_ok"]!="True"]; write_csv(AUDIT/"SOURCE_PRESERVATION_MISSING_V173.csv",missing,list(audit[0])); assert not missing

cc = read_csv(CC); assert len(cc)==2 and all(r["classification"]=="SERVICE_ERROR" for r in cc)
cc_exec=[]
for r in cc:
    x=dict(r); x["run_scope"]="HEALTH_CONTROL_2014_49"; x["evidentiary_effect"]="NONE_SERVICE_ERROR_DO_NOT_RUN_PENDING40"; cc_exec.append(x)
write_csv(HERE/"E0_COMMONCRAWL_HEALTH_CONTROL_V173.csv",cc_exec)
write_csv(HERE/"E0_COMMONCRAWL_QUERY_COMPLETENESS_V173.csv",[
    {"batch":"HEALTH_CONTROL_2014_49","collections_targeted":"1","queries":"2","valid_no_capture":"0","service_errors":"2","captures":"0","pending_queries":"40","decision":"STOP_PENDING_BATCH_CONTROL_FAILED"},
    {"batch":"PENDING_RETRY","collections_targeted":"20","queries":"0","valid_no_capture":"0","service_errors":"0","captures":"0","pending_queries":"40","decision":"NOT_EXECUTED_AFTER_FAILED_CONTROL"},
])

cidd_rows = [
    ("CIDD173_01","Tipo de documento","NOT = nota SIGEN","buscar tipo NOT, no Informe","EXACT_CODE"),
    ("CIDD173_02","Número de documento","campo aplicable a resoluciones/circulares/notas","3672 y variantes 03672/2009","EXACT_FIELD"),
    ("CIDD173_03","Fecha","dd.mm.aaaa","acotar salida/comunicación 2009","EXACT_FORMAT"),
    ("CIDD173_04","Número de expediente u oficio","clave única alfanumérica; método idéntico al sistema Mesa de Entradas","correlacionar salida, trámite previo y receptor","CROSS_SYSTEM_KEY"),
    ("CIDD173_05","Cantidad de páginas","documento principal","detectar cuerpo incompleto","INTEGRITY_FIELD"),
    ("CIDD173_06","Cantidad de archivos anexos","documentos complementarios","recuperar adjuntos","INTEGRITY_FIELD"),
    ("CIDD173_07","Referencia o extracto","resumen conceptual","0120/09 DAIF, Cuenta/Cierre 2008, UEPEX","SEARCH_FIELD"),
    ("CIDD173_08","Emisor","responsable documental","GSEyP/firmante","SEARCH_FIELD"),
    ("CIDD173_09","Palabras clave","temas y frases","deuda, comisiones, Cuenta 2008","SEARCH_FIELD"),
    ("CIDD173_10","Área temática","tabla del sistema de Mesa","recuperar código/valor histórico","CROSS_SYSTEM_FIELD"),
    ("CIDD173_11","Nivel de acceso","público, reservado o confidencial","distinguir no publicación de inexistencia","ACCESS_FIELD"),
    ("CIDD173_12","Número de caja","ubicación en Archivo General","rastrear original físico","PHYSICAL_LINK"),
]
write_csv(HERE/"E0_SIGEN_CIDD_FIELD_DICTIONARY_V173.csv",[{"row_id":a,"descriptor":b,"official_definition":c,"target_use":d,"status":e,"source_id":sources[1]["id"]} for a,b,c,d,e in cidd_rows])

spd_rows = [
    ("SPD173_01","Nombre del Archivo (CIDD)","denominación electrónica"),("SPD173_02","Expte Nº","vínculo de actuación"),
    ("SPD173_03","Tratamiento particular","doble faz; no escanear; difícil lectura/manchas; otros; cantidad/folios"),
    ("SPD173_04","Aclaraciones/observaciones","incidencias"),("SPD173_05","Documento/páginas","principal y anexos 1-3"),
    ("SPD173_06","Visualización","público; reservado; confidencial"),("SPD173_07","Publicación web","sí/no"),
    ("SPD173_08","Conformidades","Sector Solicitante; Secretaría General; recepción CGSI; Sector conforme; firmas/fechas"),
    ("SPD173_09","Resultados digitalización","completado por Mesa de Ayuda"),
]
write_csv(HERE/"E0_SIGEN_SPD_FORM_SCHEMA_V173.csv",[{"row_id":a,"field_or_block":b,"official_content":c,"request_use":"Pedir formulario SPD, valor, firmante, fecha y relación con Nota 3672/09.","limit":"Formulario prueba esquema, no existencia de formulario target.","source_id":sources[1]["id"]} for a,b,c in spd_rows])

lifecycle = [
    {"step":"1","actor":"Sector Solicitante / Secretaría General para notas","action":"asigna descriptores CIDD en sistema","record":"registro Archivo Digital","target_test":"tipo NOT + número + fecha + referencia"},
    {"step":"2","actor":"Sector Solicitante","action":"remite ejemplar foliado y SPD a Mesa de Ayuda","record":"SPD + original","target_test":"folios, anexos, expediente/oficio"},
    {"step":"3","actor":"Mesa de Ayuda CGSI","action":"verifica integridad/CIDD y corrige deficiencias","record":"recepción/incidencia","target_test":"acuse, observaciones y correcciones"},
    {"step":"4","actor":"Mesa de Ayuda CGSI","action":"escanea, nombra archivo y controla calidad","record":"archivo electrónico","target_test":"nombre CIDD, fecha, operador, archivo/hash"},
    {"step":"5","actor":"Mesa de Ayuda CGSI","action":"actualiza Archivo Digital, publica si corresponde y completa resultado SPD","record":"ID/estado/acceso/resultado","target_test":"IdDocumento, acceso y publicación"},
    {"step":"6","actor":"Sector Solicitante","action":"confronta original y copia; presta conformidad","record":"SPD firmado","target_test":"firma/fecha/conformidad"},
    {"step":"7","actor":"Archivo General","action":"guarda original y registra ubicación física","record":"número de caja","target_test":"fondo/serie/caja/folios"},
]
write_csv(HERE/"E0_SIGEN_DIGITALIZATION_LIFECYCLE_V173.csv",lifecycle)

write_csv(HERE/"E0_SIGEN_ARCHIVEWEB_UNIVERSE_AUDIT_V173.csv",[
    {"test_id":"AW173_01","surface":"ArchivoWeb Buscador","observed":"años 1993-2026; 12 subtipos; palabra clave; organismo","classification":"PUBLIC_REPORTS_INTERFACE","effect":"apta para informes, no para tipo NOT","limit":"cero no cierra Nota 3672/09"},
    {"test_id":"AW173_02","surface":"selector tipo","observed":"Auditoría, Control, Entrega/Recepción, Especiales, evaluaciones, fondos, Red Federal, juicios, resultados, situaciones","classification":"NOTES_NOT_EXPOSED","effect":"exclusión de universo testable","limit":"no prueba ausencia en backend Archivo Digital"},
    {"test_id":"AW173_03","surface":"IdDocumento=145","observed":"registro de informe año 2006 con organismo, extracto, año y tipo","classification":"PRE_TARGET_METADATA_CONTINUITY","effect":"prueba IDs públicos anteriores a 2009","limit":"registro de informe, no Nota"},
    {"test_id":"AW173_04","surface":"búsqueda web exacta","observed":"NOT+3672/GSEyP sin resultado","classification":"PUBLIC_SEARCH_NEGATIVE_SCOPED","effect":"ninguno sobre backend/archivo físico","limit":"acceso/selección/indexación desconocidos"},
])

write_csv(HERE/"E0_SIGEN_LEGACY_TO_GDE_DIGITAL_NOTES_CROSSWALK_V173.csv",[
    {"period":"2007","system_or_area":"sistema de Mesa + Archivo Digital","documented_function":"clave Mesa; CIDD/SPD; archivo electrónico y caja física","target_request":"exportación legado y diccionario","status":"EXACT_CAPABILITY","limit":"no body target"},
    {"period":"2009","system_or_area":"Secretaría General/Mesa/Archivo","documented_function":"Notas se indexan bajo código NOT luego de comunicarse si se digitalizan","target_request":"registro 3672/09, SPD, archivo y caja","status":"TARGET_TESTABLE","limit":"carga/digitalización no confirmadas"},
    {"period":"2022","system_or_area":"Mesa de Entradas y Gestión Documental","documented_function":"GDE registra ingresos/egresos; área administra archivo digital de Notas","target_request":"crosswalk/migración legado→GDE y Archivo Digital","status":"LATER_ROUTE","limit":"no retroproyectar ID GDE"},
])

write_csv(HERE/"V173_PDF_VISUAL_CONTROL.csv",[
    {"control_id":"PDF173_01","source_id":sources[1]["id"],"pdf_pages":"34-35","printed_pages":"34-35","target":"Resolución 41/07, CIDD y SPD","result":"PASS_LEGIBLE_COMPLETE","limit":"esquema no registro target"},
    {"control_id":"PDF173_02","source_id":sources[2]["id"],"pdf_pages":"7","printed_pages":"7 of 67","target":"Mesa GDE y archivo digital de Notas","result":"PASS_LEGIBLE_COMPLETE","limit":"ruta 2022 no ID 2009"},
])

keys=read_csv(HERE/"E0_REQUEST_SEARCH_KEY_MATRIX_V173.csv")
keys += [
    {"key_id":"SK173_20","request_id":"REQ155_SIGEN","key_group":"cidd_document_type","exact_key":"Tipo NOT; número 3672; fecha 2009; GSEyP","search_purpose":"localizar registro Archivo Digital","source_or_basis":"Resolución SIGEN 41/2007 CIDD","caveat":"probar variantes y no exigir publicación"},
    {"key_id":"SK173_21","request_id":"REQ155_SIGEN","key_group":"cidd_office_key","exact_key":"número de expediente u oficio alfanumérico · método Mesa de Entradas","search_purpose":"correlacionar salida, 0120/09 y receptor","source_or_basis":"CIDD","caveat":"valor concreto abierto"},
    {"key_id":"SK173_22","request_id":"REQ155_SIGEN","key_group":"spd_form","exact_key":"SPD · Nombre Archivo CIDD · Expte · folios · anexos · acceso · conformidades","search_purpose":"recuperar solicitud/resultados de digitalización","source_or_basis":"SPD oficial","caveat":"puede no haberse digitalizado"},
    {"key_id":"SK173_23","request_id":"REQ155_SIGEN","key_group":"physical_box","exact_key":"NOT 3672/09 · número de caja · Archivo General","search_purpose":"localizar original físico","source_or_basis":"Res.41/07 I.9.8/CIDD","caveat":"pedir fondo, serie y transferencia"},
    {"key_id":"SK173_24","request_id":"REQ155_SIGEN","key_group":"access_level","exact_key":"público | reservado | confidencial","search_purpose":"explicar no publicación","source_or_basis":"CIDD/SPD","caveat":"acceso restringido no equivale a inexistencia"},
    {"key_id":"SK173_25","request_id":"REQ155_SIGEN","key_group":"migration_crosswalk","exact_key":"Archivo Digital 2007/2009 ↔ GDE 2022 ↔ archivo digital Notas SIGEN","search_purpose":"recuperar tabla de equivalencias/migración","source_or_basis":"Res.41/07 + Res.223/2022 Anexo II","caveat":"no exigir ID GDE originario"},
]
write_csv(HERE/"E0_REQUEST_SEARCH_KEY_MATRIX_V173.csv",keys)

objects=read_csv(HERE/"E0_V173_REQUEST_OBJECTS.csv")
objects += [
    {"row_id":"RO173_20","object_id":"SIGEN_ARCHIVO_DIGITAL_NOT_3672","custodian":"SIGEN · Secretaría General/Mesa/Archivo Digital","exact_record":"registro tipo NOT número 3672/09","period":"2009","minimum_fields":"IdDocumento; tipo; número; fecha; expediente/oficio; referencia; emisor; palabras clave; área; acceso; páginas; anexos; nombre archivo; estado","closure_rule":"Exportación+archivo o negativo por campo, variante, tabla, período y backend.","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO173_21","object_id":"SIGEN_SPD_3672","custodian":"SIGEN · Mesa de Ayuda CGSI/Secretaría General","exact_record":"formulario SPD y resultados de digitalización de Nota 3672/09","period":"2009","minimum_fields":"archivo CIDD; expte; tratamiento; folios; anexos; acceso; web; incidencias; resultados; firmas; fechas","closure_rule":"Formulario completo o certificación de no digitalización/búsqueda.","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO173_22","object_id":"SIGEN_PHYSICAL_BOX_3672","custodian":"SIGEN · Archivo General","exact_record":"original físico y ubicación de Nota 3672/09","period":"2009 en adelante","minimum_fields":"fondo; serie; caja; carpeta; folios; transferencia; préstamo; baja; disposición","closure_rule":"Copia/ubicación o acto de transferencia/baja con inventario.","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO173_23","object_id":"SIGEN_LEGACY_GDE_NOTES_CROSSWALK","custodian":"SIGEN · Mesa/Gestión Documental/TI","exact_record":"migración de Archivo Digital y Mesa legado a GDE/archivo digital de Notas","period":"2007-2022","minimum_fields":"sistema origen/destino; tabla/campo; ID; fecha; lote; integridad; excepciones; acceso; disposición","closure_rule":"Crosswalk y logs o negativa técnica fundada.","status":"DRAFT_NOT_SENT"},
]
write_csv(HERE/"E0_V173_REQUEST_OBJECTS.csv",objects); write_csv(HERE/"E0_V173_REQUEST_OBJECTS_V173.csv",objects)

breaks=read_csv(HERE/"E0_FISCAL_METHOD_BREAKS_V173.csv")
breaks += [
    {"break_id":"archive_digital_schema_not_target_record_v173","dimension":"document_route","problem":"Res.41/07 prueba esquema y deberes, no la carga de 3672/09.","rule":"Pedir registro, SPD, archivo y caja; mantener cuerpo abierto.","status":"FROZEN_V173","evidence":"Res. SIGEN 41/2007"},
    {"break_id":"archiveweb_reports_not_notes_v173","dimension":"public_surface","problem":"ArchivoWeb público sólo expone subtipos de informe.","rule":"No usar cero de interfaz como negativo de tipo NOT.","status":"FROZEN_V173","evidence":"Buscador.aspx selectors"},
    {"break_id":"access_level_not_nonexistence_v173","dimension":"publication","problem":"CIDD/SPD admiten público, reservado y confidencial.","rule":"Separar existencia, digitalización, acceso y publicación.","status":"FROZEN_V173","evidence":"CIDD/SPD"},
    {"break_id":"later_gde_route_not_original_id_v173","dimension":"migration","problem":"GDE 2022 no implica ID GDE originario en 2009.","rule":"Pedir crosswalk legado→GDE sin retroproyección.","status":"FROZEN_V173","evidence":"Res.223/2022 Anexo II"},
    {"break_id":"failed_health_control_stops_pending40_v173","dimension":"archive_query","problem":"Control Common Crawl falló 2/2.","rule":"No ejecutar 40 pendientes ni convertir error en ausencia.","status":"FROZEN_V173","evidence":"V173 health control"},
]
write_csv(HERE/"E0_FISCAL_METHOD_BREAKS_V173.csv",breaks)

producer=read_csv(HERE/"E0_RECORD_PRODUCER_SYSTEM_MAP_V173.csv")
producer += [
    {"map_id":"PS173_01","institution":"SIGEN","producer_or_custodian":"Secretaría General/Mesa de Ayuda/Archivo General","system_or_record":"Archivo Digital + CIDD + SPD","record_class":"Nota SIGEN digitalizable","exact_fields_or_trace":"NOT; número; fecha; oficio; referencia; acceso; anexos; archivo; conformidades; caja","target_use":"Nota 3672/09","source_id":sources[0]["id"],"source_locator":"I.9 + anexos","applicability":"EXACT_2007_PROCEDURE","caveat":"digitalización target no confirmada"},
    {"map_id":"PS173_02","institution":"SIGEN","producer_or_custodian":"Mesa de Entradas y Gestión Documental","system_or_record":"GDE + archivo digital de Notas","record_class":"entrada/egreso y Nota SIGEN","exact_fields_or_trace":"ID GDE; registro; relación con archivo digital; migración","target_use":"crosswalk 2009→2022","source_id":sources[2]["id"],"source_locator":"Anexo II PDF p.7","applicability":"LATER_MIGRATION_ENDPOINT","caveat":"no ID originario 2009"},
]
write_csv(HERE/"E0_RECORD_PRODUCER_SYSTEM_MAP_V173.csv",producer)

temporal=read_csv(HERE/"E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V173.csv")
temporal += [{"institution":"SIGEN","target_period":"2007-2022","contemporaneous_route":"Mesa + Archivo Digital CIDD/SPD + original físico/caja","later_route_or_migration":"GDE + archivo digital de Notas SIGEN","required_search_scope":"NOT; número; fecha; oficio; referencia; acceso; SPD; archivo; caja; crosswalk GDE","temporal_caveat":"ArchivoWeb público sólo consulta informes; GDE posterior no es ID originario","official_basis":"Res.41/2007 + Res.223/2022 Anexo II"}]
write_csv(HERE/"E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V173.csv",temporal)

addendum="""

## Adenda V173 · código NOT, CIDD, SPD y Archivo Digital

La Resolución SIGEN Nº 41/2007 y sus anexos fueron recuperados completos. Para Notas SIGEN, el Catálogo de Indexación (CIDD) usa el código `NOT` y registra número, fecha, número de expediente u oficio —con una clave alfanumérica y el mismo método del sistema de Mesa de Entradas—, páginas, anexos, referencia/extracto, emisor, palabras clave, área temática, nivel de acceso y número de caja. Secretaría General era responsable de cargar/revisar índices y la digitalización de notas se promovía luego de comunicar el documento.

Se solicita el registro `NOT` de la Nota 3672/09, su IdDocumento o equivalente, el formulario Solicitud Publicación/Digitalización (SPD), nombre de archivo CIDD, expediente, folios, anexos, incidencias, resultados, firmas, fechas, nivel de acceso y publicación. Asimismo, el original físico debe buscarse por fondo, serie y número de caja. La estructura SIGEN 2022 demuestra que Mesa registra ingresos/egresos en GDE y administra el archivo digital de Notas SIGEN: pídase el crosswalk legado→GDE/Archivo Digital sin inventar un ID GDE originario.

El ArchivoWeb público expone únicamente subtipos de informes; no ofrece `NOT`. Un cero allí no cierra la nota. Common Crawl no se reabrió porque el control V173 falló 2/2; cuarenta consultas siguen pendientes y los errores no son ausencia. Estado DRAFT_NOT_SENT; solicitudes 0; SAF355 0/5; ejecución 0/10.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V173.md","REQUEST_SUBMISSION_CHECKLIST_V173.md","E0_INSTITUTIONAL_REQUEST_PACKAGE_V173.md"):
    p=HERE/name; body=p.read_text(encoding="utf-8-sig")
    if "Adenda V173 · código NOT" not in body: p.write_text(body+addendum,encoding="utf-8")

strict=read_csv(HERE/"STRICT_Q4_FOUR_LEG_COVERAGE_V173.csv"); strict[0]["coverage_set"]="V173 strict 34-entity set; unchanged from V172"; strict[0]["v161_change"]="V173: no banking promotion; unchanged from V172."; write_csv(HERE/"STRICT_Q4_FOUR_LEG_COVERAGE_V173.csv",strict)

public_log=[
    {"log_id":"PUB173_01","surface":"Infoleg/BO","query_or_target":"Resolución SIGEN 41/2007","result":"cuerpo+CIDD+SPD localizados","classification":"PRIMARY_BODY_AND_ANNEXES_LOCATED","limit_or_next_step":"buscar registro target"},
    {"log_id":"PUB173_02","surface":"ArchivoWeb","query_or_target":"universo/filtros","result":"sólo informes; NOT no expuesto","classification":"PUBLIC_UNIVERSE_LIMIT_LOCATED","limit_or_next_step":"backend/archivo institucional"},
    {"log_id":"PUB173_03","surface":"web exacta","query_or_target":"NOT 3672 GSEyP","result":"sin resultado","classification":"PUBLIC_SEARCH_NEGATIVE_SCOPED","limit_or_next_step":"no implica ausencia"},
    {"log_id":"PUB173_04","surface":"Common Crawl","query_or_target":"control CC-MAIN-2014-49 dos hosts","result":"2 service errors","classification":"SERVICE_ERROR","limit_or_next_step":"40 pendientes no ejecutadas"},
]
write_csv(HERE/"V173_PUBLIC_SEARCH_LOG.csv",public_log)

recovery=f"""# Recuperación archivística · V173

Se recuperó el cuerpo completo de la Resolución SIGEN 41/2007 y sus anexos CIDD/SPD. La nota target pasa a ser consultable por tipo `NOT`, número, fecha, clave oficio/expediente, referencia, acceso, anexos, archivo y caja física. La Resolución 223/2022 prueba el extremo posterior GDE + archivo digital de Notas, habilitando un pedido de crosswalk. ArchivoWeb es una interfaz pública de informes y no puede producir un negativo válido de una Nota. Common Crawl: control 0/2 evaluable, dos errores; 40 consultas pendientes no ejecutadas. Cuerpo/asiento 3672, SPD/archivo/caja, IDs receptor/SISIO y Plan 2009 siguen abiertos. Archivo 607/607; panel 34 y {COVERAGE}%; solicitudes 0, SAF355 0/5, ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V173.md","E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V173.md","E0_FISCAL_RECONSTRUCTION_V173.md"): (HERE/name).write_text(recovery,encoding="utf-8")
(HERE/"CNV_ATTACHMENT_ANALYTIC_REVIEW_V173.md").write_text(f"# Revisión acumulada V173\n\nPanel 34 y {COVERAGE}% congelado. CIDD/SPD y continuidad GDE hacen testable la Nota 3672/09 sin probar aún cuerpo ni ejecución. ArchivoWeb no cubre Notas. Solicitudes 0; SAF355 0/5; ejecución 0/10.\n",encoding="utf-8")

bundle_specs=[
    ("RES41_TEXT",RES_TEXT,sources[0]["url_original"],"normative body and machine-readable annex"),("BO31194_PDF",BO_PDF,sources[1]["url_original"],"visual CIDD/SPD"),
    ("RES223_ANNEX2",ORG22,sources[2]["url_original"],"GDE and digital Notes archive"),("ARCHIVEWEB_SEARCH",WEB_SEARCH,sources[3]["url_original"],"public report-only universe"),
    ("ARCHIVEWEB_ID145",WEB_145,sources[4]["url_original"],"pre-2009 public record comparator"),("RES41_SUMMARY",RES_SUMMARY,"official supporting page","metadata mirror"),
    ("RES7_MODIFIERS",RES_INDEX,"official supporting page","exact act locator"),("CC_CONTROL",CC,"generated log","2 service errors"),("SCANNER",SCANNER,"generated method","reproducible control"),
]
bundle=[{"role":role,"path":"/"+p.relative_to(REPO).as_posix(),"url":url,"bytes":str(p.stat().st_size),"sha256":sha(p),"analytic_use":use} for role,p,url,use in bundle_specs]; write_csv(HERE/"V173_SOURCE_BUNDLE.csv",bundle)

SYNC.mkdir(parents=True,exist_ok=True)
sync=[]
for s in sources:
    p=REPO/s["archivo_local"].lstrip("/"); sync.append({"role":"V173_PUBLIC_SOURCE","relative_path":s["archivo_local"],"source_url":s["url_original"],"size_bytes":str(p.stat().st_size),"sha256":s["sha256"],"format_verification":"PDF_VISUAL_PASS_TLS_VALID" if p.suffix.lower()==".pdf" else "HTML_CONTENT_PASS_TLS_VALID"})
write_csv(SYNC/"SOURCE_SYNC_FILE_MANIFEST_V173.csv",sync); write_csv(SYNC/"SOURCE_SYNC_PUBLIC_ENDPOINTS_V173.csv",public_log)
(SYNC/"SOURCE_SYNC_REPORT_V173.md").write_text("# Sincronización V173\n\n- Catálogo 607/607, hash válido, brecha 0.\n- +5 fuentes oficiales: Res.41/07 texto y BO, Res.223/22 Anexo II, ArchivoWeb buscador y registro pre-2009.\n- CIDD/SPD y dos PDF controlados visualmente.\n- Common Crawl control falló; lote 40 no ejecutado.\n",encoding="utf-8")
(SYNC/"qa_source_sync_v173.py").write_text("""from pathlib import Path
import csv,hashlib
root=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V173.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==5
for r in rows:
 p=root/r['relative_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(r['size_bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('SOURCE SYNC V173 PASS · 5/5')
""",encoding="utf-8")

census=read_csv(HERE/"E0_LOCAL_PRIMARY_SOURCE_CENSUS_V173.csv")
for s in sources:
    p=REPO/s["archivo_local"].lstrip("/"); census.append({"source_id":s["id"],"institution":s["institucion"],"artifact":s["titulo"],"url":s["url_original"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"period_coverage":s["periodo_utilizado"],"variable_families":"Nota3672;SIGEN;ArchivoDigital;CIDD;SPD;GDE;ArchiveWeb","primary_source":"YES","preserved":"YES","method_breaks":"schema/route not target body","use_status":"E0_USABLE_RECORD_ROUTE","caveat":s["nota"]})
write_csv(HERE/"E0_LOCAL_PRIMARY_SOURCE_CENSUS_V173.csv",census)
prov=read_csv(HERE/"ARCHIVAL_PROVENANCE_V173.csv")
for s in sources:
    p=REPO/s["archivo_local"].lstrip("/"); prov.append({"source_id":s["id"],"original_url":s["url_original"],"retrieval_url":s["url_original"],"capture_timestamp":"2026-08-31","cdx_digest":"N/A_OFFICIAL_DIRECT_TLS_VALID","local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"provenance_note":s["nota"]})
write_csv(HERE/"ARCHIVAL_PROVENANCE_V173.csv",prov)
with (HERE/"SOURCE_REFERENCES_V173.md").open("a",encoding="utf-8") as f:
    f.write("\n## V173 · CIDD/SPD y continuidad Archivo Digital\n")
    for s in sources: f.write(f"\n- `{s['id']}` · {s['titulo']} · {s['url_original']} · `{s['archivo_local']}` · `{s['sha256']}`\n")
with (HERE/"RETRIEVAL_LOG_V173.md").open("a",encoding="utf-8") as f: f.write("\n## V173\n\n- Res.41/07 y anexos recuperados.\n- ArchivoWeb delimitado como informes.\n- GDE/archivo Notas 2022 localizado.\n- CC control 2 errores; 40 pendientes no ejecutadas.\n")

(HERE/"README_V173.md").write_text(f"""# Checkpoint V173

- Archivo 607/607; +5 fuentes oficiales; hashes válidos.
- Resolución SIGEN 41/2007: cuerpo, CIDD y SPD recuperados completos.
- Nota SIGEN: código `NOT`; campos número, fecha, oficio/expediente, referencia, emisor, acceso, anexos, archivo y caja.
- Ruta: Secretaría General → Mesa de Ayuda → Archivo Digital → conformidad → Archivo General/caja.
- 2022: Mesa registra ingresos/egresos en GDE y administra archivo digital de Notas; crosswalk 2009→GDE pedido, no supuesto.
- ArchivoWeb público sólo filtra informes; no produce negativo válido de Notas.
- Common Crawl: control 2/2 errores; cuarenta pendientes no ejecutadas.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
""",encoding="utf-8")
(HERE/"VEREDICTO_V173.md").write_text("# Veredicto V173\n\nAvance documental mayor. La Resolución 41/2007 transforma la Nota 3672/09 en una búsqueda por esquema oficial exacto, pero no recupera aún su registro ni cuerpo. ArchivoWeb no cubre Notas y GDE es un extremo posterior. Common Crawl permanece técnico. Sin promoción bancaria ni solicitud enviada.\n",encoding="utf-8")
(HERE/"AUDITORIA_V173.md").write_text(f"# Auditoría V173\n\n- 607/607 fuentes; huecos 0; nuevas 5.\n- PDF visual: BO páginas 34-35 PASS; SIGEN 2022 página 7 PASS.\n- CIDD 12 campos; SPD 9 bloques; lifecycle 7 pasos.\n- CC: 2 errores de control; lote 40 no ejecutado.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n",encoding="utf-8")
(HERE/"HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V173_A_V174.md").write_text("""# Handover V173 → V174

## Cerrado
- Archivo 607/607; Res.41/07+CIDD+SPD completos.
- Código NOT, clave oficio/expediente, acceso y caja identificados.
- ArchivoWeb delimitado como informes; GDE/archivo de Notas 2022 localizado.
- Common Crawl frenado tras control 2/2 errores.

## Prioridad V174
1. Buscar/exportar registro `NOT` 3672/09 por backend Archivo Digital y Secretaría General.
2. Recuperar SPD, archivo electrónico, nivel de acceso y número de caja/original.
3. Pedir crosswalk Mesa/Archivo Digital legado→GDE y Archivo Digital de Notas.
4. Correlacionar oficio/expediente con salida SIGEN, entrada CGN, 0120/09 y SISIO.
5. Reintentar CC sólo tras control válido; 40 consultas siguen pendientes.
6. Mantener seis DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
""",encoding="utf-8")

complete=json.loads((AUDIT/"CURRENT_SOURCE_COMPLETENESS_V172.json").read_text(encoding="utf-8-sig")); complete.update({
    "checkpoint":"V173","date":"2026-08-31","master_catalog_entries":607,"physical_local_copies":607,"physical_local_hash_ok":607,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_RES41_CIDD_SPD_LOCATED_NOTE_TARGET_RECORD_OPEN","analytical_promotion":"NONE_V173_ARCHIVAL_SCHEMA_ONLY","exact_entities":34,
    "strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,"strict_coverage_increment_v172_pp":"0",
    "requests_submitted":0,"responses_received":0,"saf355_certifications_located":0,"executed_historical_bank_rows_confirmed":0,
    "note_3672_09_body_located":False,"note_3672_archive_digital_record_located":False,"note_3672_spd_located":False,"note_3672_physical_box_located":False,
    "sigen_resolution_41_2007_body_located":True,"sigen_resolution_41_2007_annexes_located":True,"sigen_cidd_not_code_located":True,"sigen_spd_schema_located":True,
    "sigen_archiveweb_exposes_notes":False,"sigen_gde_digital_notes_later_route_located":True,"sigen_legacy_gde_crosswalk_located":False,
    "commoncrawl_exact_prefix_queries_completed":152,"commoncrawl_exact_prefix_queries_v173":2,"commoncrawl_valid_no_capture_v173":0,"commoncrawl_service_errors_v173":2,
    "commoncrawl_exact_prefix_service_errors":42,"commoncrawl_capture_rows_v173":0,"commoncrawl_pending_retry_queries":40,"commoncrawl_pending_retry_collections":20,
    "new_v173_sources":5,
}); (AUDIT/"CURRENT_SOURCE_COMPLETENESS_V173.json").write_text(json.dumps(complete,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

orig=read_csv(ORIGINS); bypath={r["path"]:r for r in orig}
for p in iter_files(HIST_ROOT): bypath[p.relative_to(CYCLE).as_posix()]={"path":p.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V173" if p.parent==HIST else "generated/preserved V173","note":"official SIGEN/Infoleg/HCDN source or controlled archive diagnostic"}
for p in iter_files(SYNC): bypath[p.relative_to(CYCLE).as_posix()]={"path":p.relative_to(CYCLE).as_posix(),"origin":"generated/updated V173","note":"incremental source synchronization"}
for p in HERE.iterdir():
    if p.is_file(): bypath[p.relative_to(CYCLE).as_posix()]={"path":p.relative_to(CYCLE).as_posix(),"origin":"generated/updated V173","note":"CIDD/SPD checkpoint"}
for p in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V173.csv",AUDIT/"SOURCE_BACKUP_CENSUS_V173.csv",AUDIT/"SOURCE_PRESERVATION_MISSING_V173.csv",AUDIT/"CURRENT_SOURCE_COMPLETENESS_V173.json"): bypath[p.relative_to(CYCLE).as_posix()]={"path":p.relative_to(CYCLE).as_posix(),"origin":"generated/updated V173","note":"607-source completeness"}
write_csv(ORIGINS,list(bypath.values()),["path","origin","note"])

t=CYCLE/"TRANSPARENCY_README.md"; body=t.read_text(encoding="utf-8-sig")
if "## V173 · CIDD, SPD y Notas SIGEN" not in body: body += "\n\n## V173 · CIDD, SPD y Notas SIGEN\n\nLa Resolución 41/2007 y anexos identifican código NOT, CIDD, SPD, acceso y caja física. ArchivoWeb público sólo cubre informes; la ruta GDE/archivo digital de Notas está documentada en 2022 sin retroproyección. Common Crawl quedó detenido tras control fallido. Archivo 607/607; panel 34; solicitudes 0.\n"; t.write_text(body,encoding="utf-8")
(REPO/"BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"# Backup de actualización · 2026-08-31\n\n- V173; 607/607 fuentes.\n- Res.41/07+CIDD+SPD completos; target 3672 aún abierto.\n- ArchivoWeb informes-only; GDE/Notas 2022 localizado.\n- CC control falló; 40 pendientes no ejecutadas.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n",encoding="utf-8")

(HERE/"qa_v173.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==607
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V173.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==607 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V173.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V173' and co['master_catalog_entries']==607
assert co['sigen_resolution_41_2007_body_located'] and co['sigen_resolution_41_2007_annexes_located'] and co['sigen_cidd_not_code_located'] and not co['note_3672_archive_digital_record_located']
assert co['commoncrawl_service_errors_v173']==2 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_SIGEN_CIDD_FIELD_DICTIONARY_V173.csv'))==12 and len(rows('E0_SIGEN_SPD_FORM_SCHEMA_V173.csv'))==9 and len(rows('E0_SIGEN_DIGITALIZATION_LIFECYCLE_V173.csv'))==7
assert len(rows('E0_SIGEN_ARCHIVEWEB_UNIVERSE_AUDIT_V173.csv'))==4 and len(rows('E0_SIGEN_LEGACY_TO_GDE_DIGITAL_NOTES_CROSSWALK_V173.csv'))==3
assert len(rows('V173_PDF_VISUAL_CONTROL.csv'))==2 and all(x['result'].startswith('PASS') for x in rows('V173_PDF_VISUAL_CONTROL.csv'))
cc=rows('E0_COMMONCRAWL_HEALTH_CONTROL_V173.csv'); assert len(cc)==2 and all(x['classification']=='SERVICE_ERROR' for x in cc)
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V173.csv'); assert {'SK173_20','SK173_21','SK173_22','SK173_23','SK173_24','SK173_25'}<={x['key_id'] for x in keys}
obj=rows('E0_V173_REQUEST_OBJECTS.csv'); assert {'RO173_20','RO173_21','RO173_22','RO173_23'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V173_REQUEST_OBJECTS_V173.csv')
for n in ('REQUEST_AGN_2018_REPLY_V173.md','REQUEST_BCRA_CRYL_SETTLEMENT_V173.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V173.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V173.md','REQUEST_CNV_CUSTODY_RECORDS_V173.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V173.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V173.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V173_SOURCE_BUNDLE.csv'))==9
m=json.loads((H/'MANIFEST_V173.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V173' and m['parent_checkpoint']=='V172' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V173 QA PASS · 607/607 · new=5 · RES41+CIDD+SPD=LOCATED · CC=2-errors/40-pending · panel=34 · requests=0 · SAF355=0/5 · execution=0/10')
""",encoding="utf-8")

(REPO/"TREE.txt").write_text(tree(REPO),encoding="utf-8"); (CYCLE/"TREE.txt").write_text(tree(CYCLE),encoding="utf-8")
files=[{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(),key=lambda x:x.name.casefold()) if p.is_file() and p.name!="MANIFEST_V173.json"]
manifest={"checkpoint":"V173","parent_checkpoint":"V172","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,"new_promotions":[],"source_archive":"607/607; five sources added","historical_finding":"Res41 body+CIDD+SPD located; code NOT and physical box link; GDE later route; ArchiveWeb reports-only","note_3672_09_body":"NOT_LOCATED","note_3672_archive_digital_record":"NOT_LOCATED","commoncrawl_queries_v173":2,"commoncrawl_service_errors_v173":2,"commoncrawl_pending":40,"closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files}
(HERE/"MANIFEST_V173.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
gm=CYCLE/"MANIFEST_SHA256.json"; gf=[{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p!=gm]
payload={"checkpoint":"V173","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"607 master; 607 physical SHA-valid","historical_workstream":"Res41 CIDD/SPD located; target record/body and execution open; CC pending 40; six drafts not sent","file_count_excluding_manifest":len(gf),"files":gf}
tmp=gm.with_suffix(".json.V173tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(gm)
print("V173 BUILD PASS · catalog=607/607 · new=5 · RES41+CIDD+SPD=LOCATED · cc=2 errors/40 pending · panel=34 · requests=0")
