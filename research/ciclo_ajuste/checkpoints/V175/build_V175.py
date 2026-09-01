from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import html
import json
import os
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V174"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v175"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v175"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


FILES = {
    "pacios": HIST / "argentina_decreto_1795_2009_pacios_renuncia.html",
    "reposo": HIST / "argentina_decreto_1796_2009_reposo_designacion.html",
    "decreto759": HIST / "argentina_decreto_759_1966_actualizado.html",
    "res2600": HIST / "argentina_resolucion_2600_2009.html",
    "cgn2010": HIST / "cgn_cuenta_2010_uepex.html",
    "cgn2011": HIST / "cgn_cuenta_2011_uepex.html",
    "cgn2012": HIST / "cgn_cuenta_2012_uepex.html",
    "cgn2013": HIST / "cgn_cuenta_2013_uepex.html",
    "memoria": HIST / "sigen_memoria_2009.pdf",
    "vlex": HIST / "vlex_pjn_tocf4_cfp_2111_2010_to1_2017.html",
}
EXPECTED = {
    FILES["pacios"]: (33171, "cbf76d8de865fce97f2fb26937a4faa2ed7c9020337da0ee9f9d3caa8c9faa60"),
    FILES["reposo"]: (32962, "7e2cae58d83017beece911e8cc59f6a5d9919e9d1313edcefd37e751c7772eec"),
    FILES["decreto759"]: (54292, "3808eede740c2f0986cc3bd76198165179e6791c6b0bc0b099c22fad7a331a10"),
    FILES["res2600"]: (53893, "38b9ca150241ad4e4ea7a7689dd40704f237c95ddd5c8c54c120d4a84b91d266"),
    FILES["cgn2010"]: (115479, "87554e2a514327f06fd41692d35e4841d3f1708de08d637d8d36a08ad43a2e27"),
    FILES["cgn2011"]: (67561, "fe91cb5dddeb344a46db71ec4833679028d6166f70e141a0a23c36288e3b1ff3"),
    FILES["cgn2012"]: (41470, "1c4e300dca6cdf334d978b585b2f6beb85f7cb8b8669853bc32ebbae3539e699"),
    FILES["cgn2013"]: (57243, "066323301806c56d9a971f6f290481c4c230dc1313ced197a777605ae2f1ab6f"),
    FILES["memoria"]: (97057, "c10d014fc500d2fe66387944bd18a4e2c6e4137d39c85859014a07b49230ddcf"),
    FILES["vlex"]: (173290, "bc733cf8af88daae86bce5d1374dd1acfff72d49163633c064b58f1e91f96692"),
}


def read_csv(path: Path | str):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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


def decoded_html(path: Path):
    raw = path.read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            pass
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clone_parent():
    skip = {
        "MANIFEST_V174.json", "README_V174.md", "VEREDICTO_V174.md", "AUDITORIA_V174.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V174_A_V175.md", "V174_SOURCE_BUNDLE.csv",
        "V174_PUBLIC_SEARCH_LOG.csv", "V174_PDF_VISUAL_CONTROL.csv",
        "V174_PDF_VISUAL_AND_TEXT_CONTROL.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V174", "V175")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V174", "V175"), encoding="utf-8")


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest

# Exact text controls on the preserved public material.
texts = {key: decoded_html(path) for key, path in FILES.items() if path.suffix.lower() == ".html"}
for key in ("cgn2010", "cgn2011", "cgn2012", "cgn2013"):
    assert all(token.lower() not in texts[key].lower() for token in ("3672", "0120/09", "SISIO"))
assert "112/10" in texts["cgn2010"] and "93/11" in texts["cgn2011"] and "145/12" in texts["cgn2012"]
assert "Regularizada" in texts["res2600"] and "Sin conocimiento UAI" in texts["res2600"] and "Acciones Encaradas" in texts["res2600"]
assert "4955/2009" in texts["vlex"] and "5353/2009" in texts["vlex"] and "5259/2009" in texts["vlex"]

source_specs = [
    ("e0_argentina_decreto_1795_2009_pacios_renuncia_v175", "Jefatura de Gabinete / Infoleg", "Decreto 1795/2009 · renuncia de Carlos Pacios como Síndico General", "https://www.argentina.gob.ar/normativa/nacional/norma-160448", FILES["pacios"], "2009-11-19", "Decreto 1795/2009", "2009", "HTML oficial completo preservado", "Delimita una autoridad posible hasta el relevo; no identifica al firmante de la Nota 3672 sin su fecha o cuerpo."),
    ("e0_argentina_decreto_1796_2009_reposo_designacion_v175", "Jefatura de Gabinete / Infoleg", "Decreto 1796/2009 · designación de Daniel Reposo como Síndico General", "https://www.argentina.gob.ar/normativa/nacional/norma-160449", FILES["reposo"], "2009-11-20", "Decreto 1796/2009", "2009", "HTML oficial completo preservado", "Delimita una segunda autoridad posible desde el relevo; no permite atribuir firma sin fecha o cuerpo de la Nota 3672."),
    ("e0_argentina_decreto_759_1966_tramite_actualizado_v175", "Poder Ejecutivo Nacional / Infoleg", "Decreto 759/1966 actualizado · numeración, registro, movimiento y archivo de expedientes", "https://www.argentina.gob.ar/normativa/nacional/123084/actualizacion", FILES["decreto759"], "1966-07-06", "Decreto 759/1966 actualizado", "1966-2009", "HTML oficial normativo preservado", "Prueba obligaciones generales de numeración única, recepción, clasificación, registro, distribución, archivo y conservación del movimiento/destino; no prueba por sí solo la fila 3672."),
    ("e0_argentina_resolucion_2600_2009_sisio_workflow_v175", "Ministerio de Planificación Federal / Infoleg", "Resolución 2600/2009 · circuito contemporáneo SIGEN, UAI, expedientes y SISIO", "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-2600-2009-163154/texto", FILES["res2600"], "2009-12-30", "Resolución 2600/2009", "2008-2009", "HTML oficial completo preservado", "Prueba el flujo contemporáneo de informe preliminar/final, expediente receptor, carga en SISIO, estados y acciones encaradas; es comparador procedimental, no el registro objetivo."),
    ("e0_cgn_cuenta_2010_uepex_followup_v175", "Contaduría General de la Nación", "Cuenta de Inversión 2010 · UEPEX, Nota 112/10 DAIF y correcciones", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/sep/uepex.htm", FILES["cgn2010"], "2011", "Cuenta de Inversión 2010 · UEPEX", "2010", "HTML oficial preservado · certificado histórico vencido", "Prueba continuidad de elevación CGN→SIGEN y correcciones por reemplazo de cuadros o regularización SIDIF; no contiene las cadenas 3672, 0120/09 o SISIO."),
    ("e0_cgn_cuenta_2011_uepex_followup_v175", "Contaduría General de la Nación", "Cuenta de Inversión 2011 · UEPEX, Nota DAIF 93/11 y correcciones", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2011/sep/uepex.htm", FILES["cgn2011"], "2012", "Cuenta de Inversión 2011 · UEPEX", "2011", "HTML oficial preservado · certificado histórico vencido", "Prueba continuidad anual del mecanismo correctivo e informe a SIGEN; no contiene las cadenas 3672, 0120/09 o SISIO."),
    ("e0_cgn_cuenta_2012_uepex_followup_v175", "Contaduría General de la Nación", "Cuenta de Inversión 2012 · UEPEX, Nota DAIF 145/12 y subsanaciones", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2012/sep/uepex.htm", FILES["cgn2012"], "2013", "Cuenta de Inversión 2012 · UEPEX", "2012", "HTML oficial preservado · certificado histórico vencido", "Prueba persistencia del control, regularizaciones y un informe específico a SIGEN; no atribuye resultados a Nota 3672."),
    ("e0_cgn_cuenta_2013_uepex_followup_v175", "Contaduría General de la Nación", "Cuenta de Inversión 2013 · UEPEX y subsanaciones", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2013/sep/uepex.htm", FILES["cgn2013"], "2014", "Cuenta de Inversión 2013 · UEPEX", "2013", "HTML oficial preservado · certificado histórico vencido", "Prueba continuidad de sustitución de cuadros, regularización SIDIF y subsanaciones; no contiene las cadenas 3672, 0120/09 o SISIO."),
    ("e0_sigen_memoria_2009_archive_sisio_capability_v175", "Sindicatura General de la Nación", "Memoria SIGEN 2009 · Cuenta de Inversión, SISIO WEB y archivo digital", "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2009.pdf", FILES["memoria"], "2009", "Memoria SIGEN 2009", "2009", "PDF oficial preservado · control visual páginas 6, 7 y 13", "Prueba capacidad contemporánea: instrucciones para certificaciones, mejoras SISIO WEB y construcción/reordenamiento del archivo digital y general; no exhibe la Nota 3672."),
    ("e0_vlex_pjn_tocf4_sigen_remitos_2009_inventory_v175", "Poder Judicial de la Nación · reproducción pública vLex", "Acta TOCF 4 de 2017 · inventario de Notas, remitos y avisos de recibo SIGEN 2009", "https://ar.vlex.com/vid/principal-tribunal-oral-to01-694793069", FILES["vlex"], "2017-09-29", "CFP 2111/2010/TO1", "2009-2017", "HTML de reproducción pública judicial preservado · alojamiento no oficial", "Reproduce un inventario judicial con Nota 734 fechada, Nota 5259, rangos correlativos de remitos y avisos de recibo originales. La procedencia primaria es judicial; el host preservado no es oficial."),
]

sources = []
for source_id, institution, title, url, path, publication, code, period, source_type, note in source_specs:
    sources.append({
        "id": source_id, "tema": "ciclo_ajuste_e0_fiscal", "institucion": institution,
        "titulo": title, "url_original": url, "archivo_local": "/" + path.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": publication, "codigo_serie": code,
        "periodo_utilizado": period, "tipo": source_type, "sha256": EXPECTED[path][1], "nota": note,
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 623

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V175.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V175.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V175.csv", missing, list(audit[0]))
assert not missing

write_csv(HERE / "E0_NOTE_3672_DIRECTIVE_TO_OUTCOME_ATTRIBUTION_GATE_V175.csv", [
    {"gate_id":"AT175_01","link":"Cuenta 2009 / Nota 0120/09 DAIF → SIGEN","evidence":"CGN informa resultados del cierre 2008 y eleva antecedentes","proved":"YES","not_proved":"contenido íntegro y adjuntos de 0120/09","classification":"DIRECT_REFERENCE_PROVED"},
    {"gate_id":"AT175_02","link":"Nota SIGEN 3672/09-GSEyP → áreas / SISIO","evidence":"referencia contemporánea conservada en Cuenta 2009","proved":"YES_REFERENCE_AND_DIRECTIVE","not_proved":"cuerpo, fecha, firmante, destinatario formal y anexos","classification":"DIRECTIVE_REFERENCE_PROVED_BODY_OPEN"},
    {"gate_id":"AT175_03","link":"circuito SIGEN → expediente → SISIO → acciones","evidence":"Resolución 2600/2009, Anexo II","proved":"YES_AS_CONTEMPORARY_WORKFLOW","not_proved":"IDs SISIO concretos de 3672","classification":"PROCEDURE_PROVED_TARGET_ROWS_OPEN"},
    {"gate_id":"AT175_04","link":"correcciones CGN 2009-2013","evidence":"Cuentas UEPEX: cuadros reemplazados, regularización SIDIF, ajustes CGN y subsanaciones","proved":"YES_AGGREGATE_MECHANISM","not_proved":"qué corrección/importe fue causada por 3672","classification":"OUTCOMES_PROVED_ATTRIBUTION_OPEN"},
    {"gate_id":"AT175_05","link":"Nota 3672 → corrección individual / importe","evidence":"requiere join por observación, organismo, cuadro, documento SIDIF, fecha y estado","proved":"NO","not_proved":"cadena uno-a-uno y contrafactual","classification":"CAUSAL_AND_MONETARY_ATTRIBUTION_NOT_PROVED"},
    {"gate_id":"AT175_06","link":"conclusión V175","evidence":"convergencia de circuito, archivo, SISIO y continuidad correctiva","proved":"mecanismo y capacidad institucional","not_proved":"efecto específico imputable a Nota 3672","classification":"DO_NOT_OVERSTATE"},
])

followup_rows = []
annual = [
    ("2010", "112/10 DAIF", "muchas inconsistencias corregidas; reemplazo de cuadros o regularización SIDIF"),
    ("2011", "93/11 DAIF", "mecanismo anual repetido; correcciones y ajustes CGN"),
    ("2012", "145/12", "informe específico a SIGEN; gran parte subsanada"),
    ("2013", "sin número individual recuperado", "gran mayoría subsanada; persiste regularización/ajuste"),
]
for index, (year, annual_note, positive) in enumerate(annual, start=1):
    followup_rows.append({
        "row_id": f"CF175_{index:02d}", "account_year": year, "annual_cgn_to_sigen_note": annual_note,
        "exact_3672_hits": "0", "exact_0120_09_hits": "0", "exact_sisio_hits": "0",
        "positive_evidence": positive, "classification": "PUBLIC_TEXT_NEGATIVE_FOR_EXACT_CHAIN_POSITIVE_FOR_RECURRING_MECHANISM",
        "limit": "ausencia de cadena exacta sólo en esta página pública; no es negativo de archivos, anexos, notas ni SISIO",
    })
write_csv(HERE / "E0_CGN_POST_3672_FOLLOWUP_SEARCH_V175.csv", followup_rows)

write_csv(HERE / "E0_SIGEN_2009_NOTE_NUMBERING_AND_REMIT_EVIDENCE_V175.csv", [
    {"row_id":"NR175_01","record":"Decreto 759/1966 actualizado","date_or_range":"vigente como marco de trámite","evidence":"numeración única del organismo originante; mesa registra, distribuye, archiva y mantiene movimiento/destino","strength":"OFFICIAL_NORMATIVE_DUTY","target_limit":"no prueba serie anual ni fila 3672"},
    {"row_id":"NR175_02","record":"Nota SIGEN 734/2009-GA + remito 014580","date_or_range":"10/03/2009","evidence":"copia fechada, entrega de original y remito reproducidos en inventario judicial","strength":"DATED_NOTE_AND_ORIGINAL_DELIVERY_REPRODUCTION","target_limit":"host vLex no oficial; otro número/área"},
    {"row_id":"NR175_03","record":"Nota SIGEN 3183/2009","date_or_range":"recibida 11/09/2009","evidence":"comparador contemporáneo ya preservado","strength":"DATED_RECIPIENT_COMPARATOR","target_limit":"otra materia"},
    {"row_id":"NR175_04","record":"Nota SIGEN 3672/2009-GSEyP","date_or_range":"ABIERTO","evidence":"referencia existente; fecha/cuerpo/remito pendientes","strength":"TARGET_REFERENCE_ONLY","target_limit":"no interpolar"},
    {"row_id":"NR175_05","record":"Remitos originales 4955/2009-NyT a 5353/2009-GSIS","date_or_range":"15-29/12/2009","evidence":"inventario los describe como numeración correlativa y conserva avisos de recibo originales","strength":"CORRELATIVE_RANGE_AND_RECEIPT_PRESERVATION_REPRODUCTION","target_limit":"no incluye rango 3672 ni prueba una única serie global"},
    {"row_id":"NR175_06","record":"Notas SIGEN 5016/2009 a 5373/2009","date_or_range":"15-29/12/2009","evidence":"biblioratos rojos inventariados judicialmente","strength":"LATE_YEAR_NOTE_RANGE_REPRODUCTION","target_limit":"no lista individualmente fila 3672"},
    {"row_id":"NR175_07","record":"Nota SIGEN 5259/2009","date_or_range":"28/12/2009","evidence":"nota, informe, remitos y recepción al Ministerio de Economía reproducidos en acta","strength":"EXACT_LATE_YEAR_COMPARATOR","target_limit":"otra nota"},
    {"row_id":"NR175_08","record":"conclusión de serie","date_or_range":"2009","evidence":"muestras fechadas + rango declarado correlativo + originales de remito/acuse","strength":"ANNUAL_CORRELATIVE_PRACTICE_SUPPORTED","target_limit":"regla formal y fila 3672 siguen abiertas"},
])

write_csv(HERE / "E0_SIGEN_2009_ARCHIVE_AND_SISIO_CAPABILITY_V175.csv", [
    {"row_id":"AC175_01","source":"Memoria SIGEN 2009","page":"PDF 6","capability":"instrucciones de trabajo para certificaciones UAI de Cuenta de Inversión e Informe Cuenta 2008","evidentiary_effect":"capacidad y actividad contemporánea probadas","target_gap":"no enumera Nota 3672"},
    {"row_id":"AC175_02","source":"Memoria SIGEN 2009","page":"PDF 7","capability":"mejoras a SISIO WEB para supervisión y seguimiento de planificación UAI; hallazgos y acciones","evidentiary_effect":"SISIO operativo y usado para seguimiento","target_gap":"faltan exportación e IDs de observaciones"},
    {"row_id":"AC175_03","source":"Memoria SIGEN 2009","page":"PDF 13","capability":"continuidad del archivo digital de Mesa de Entradas e inicio de reordenamiento, revisión, clasificación y registro del Archivo General","evidentiary_effect":"capacidad de custodia contemporánea probada","target_gap":"falta ubicación digital/física individual"},
    {"row_id":"AC175_04","source":"Resolución 2600/2009","page":"Anexo II","capability":"SIGEN carga observaciones y estados en SISIO; UAI/áreas registran acciones y seguimiento","evidentiary_effect":"campos y transiciones reclamables definidos","target_gap":"no contiene las filas del caso CGN"},
])

write_csv(HERE / "E0_NOTE_3672_SIGNATORY_AUTHORITY_WINDOW_V175.csv", [
    {"row_id":"SG175_01","officeholder":"Carlos Pacios","official_event":"renuncia aceptada por Decreto 1795/2009","boundary":"19-20/11/2009","target_implication":"candidato institucional si 3672 precede el relevo","status":"DO_NOT_ATTRIBUTE_WITHOUT_NOTE_DATE_OR_BODY"},
    {"row_id":"SG175_02","officeholder":"Daniel Reposo","official_event":"designación por Decreto 1796/2009","boundary":"desde 20/11/2009","target_implication":"candidato institucional si 3672 es posterior al relevo","status":"DO_NOT_ATTRIBUTE_WITHOUT_NOTE_DATE_OR_BODY"},
    {"row_id":"SG175_03","officeholder":"firmante de Nota 3672/09-GSEyP","official_event":"ABIERTO","boundary":"fecha exacta abierta","target_implication":"dos candidatos institucionales; puede además firmar autoridad delegada del área","status":"SIGNATORY_NOT_PROVED"},
])

write_csv(HERE / "E0_NOTE_3672_ATTRIBUTION_PROOF_REQUIREMENTS_V175.csv", [
    {"requirement_id":"PR175_01","dataset":"SISIO","minimum_fields":"ID observación; informe/auditoría origen; organismo; UAI; hallazgo; estado; historial de estados con fecha; acciones encaradas; documento soporte; cierre","join_keys":"3672/09; 0120/09; UEPEX; cierre 2008; organismo; informe","closure_test":"cada observación cargada por la instrucción identificada y trazada hasta su resultado"},
    {"requirement_id":"PR175_02","dataset":"CGN / DAIF","minimum_fields":"cuadro antes/después; inconsistencia; importe; moneda; formulario SIDIF; número de documento; certificante; fecha; respuesta","join_keys":"proyecto/organismo; cuadro; formulario; ejercicio; observación","closure_test":"corrección específica cuantificada y documentalmente vinculada"},
    {"requirement_id":"PR175_03","dataset":"Mesa SIGEN / CIDD / SPD / archivo","minimum_fields":"número; fecha; firmante; destinatario; asunto; adjuntos; expediente; registro digital; acceso; caja; remito; acuse","join_keys":"3672/09-GSEyP","closure_test":"identidad, emisión, entrega, custodia y contenido primario cerrados"},
    {"requirement_id":"PR175_04","dataset":"Mesa CGN / expediente receptor","minimum_fields":"entrada; fecha; remitente; número de nota; expediente/actuación; pases; anexos; respuesta; archivo","join_keys":"3672/09; asunto; 0120/09","closure_test":"salida SIGEN unida uno-a-uno con ingreso y expediente CGN"},
    {"requirement_id":"PR175_05","dataset":"atribución causal","minimum_fields":"secuencia temporal; orden concreta; destinatario; acción posterior; ausencia de orden alternativa; resultado medible","join_keys":"observación e identificadores documentales comunes","closure_test":"no confundir simultaneidad o mecanismo general con efecto causado por 3672"},
])

# Replace the narrower V174 envelope with the expanded, still cautious evidence ladder.
serial = read_csv(HERE / "E0_SIGEN_2009_NOTE_NUMBERING_AND_REMIT_EVIDENCE_V175.csv")
write_csv(HERE / "E0_SIGEN_2009_NOTE_SERIAL_DATE_ENVELOPE_V175.csv", [
    {"row_id":row["row_id"], "note":row["record"], "area":"según registro", "date_or_envelope":row["date_or_range"],
     "recipient_record":row["evidence"], "evidence_level":row["strength"], "target_use":"regla/ventana/remito", "limit":row["target_limit"]}
    for row in serial
])

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V175.csv")
new_keys = [
    {"key_id":"SK175_30","request_id":"REQ155_SIGEN","key_group":"sisio_history","exact_key":"observaciones dadas de alta por Nota 3672/09-GSEyP; historial completo de estados y acciones","search_purpose":"cerrar vínculo instrucción→observación→resultado","source_or_basis":"Cuenta 2009 + Res.2600/2009","caveat":"entregar IDs y marcas temporales; agregado no basta"},
    {"key_id":"SK175_31","request_id":"REQ155_SIGEN","key_group":"remit_receipt","exact_key":"remito, hoja de ruta y aviso de recibo de Nota 3672/09; libro/bibliorato 2009","search_purpose":"probar fecha, entrega y destinatario","source_or_basis":"inventario judicial contemporáneo de rangos y originales","caveat":"host vLex es reproducción; pedir original SIGEN"},
    {"key_id":"SK175_32","request_id":"REQ133_ECON","key_group":"annual_cgn_sigen_followup","exact_key":"Notas DAIF 112/10, 93/11 y 145/12, anexos y respuestas SIGEN","search_purpose":"trazar continuidad del ciclo correctivo 2009-2012","source_or_basis":"Cuentas UEPEX 2010-2012","caveat":"continuidad no equivale a causalidad de 3672"},
    {"key_id":"SK175_33","request_id":"REQ133_ECON","key_group":"correction_ledger","exact_key":"ledger antes/después de cuadros reemplazados, regularizaciones SIDIF y ajustes CGN 2008-2013","search_purpose":"cuantificar correcciones por organismo, documento e importe","source_or_basis":"Cuentas UEPEX 2009-2013","caveat":"exigir claves de unión y autoridad certificante"},
    {"key_id":"SK175_34","request_id":"REQ155_SIGEN/REQ133_ECON","key_group":"signatory_and_custody","exact_key":"fecha, firmante, delegación, destinatario, CIDD, SPD, caja, remito, acuse, expediente receptor","search_purpose":"cerrar identidad y custodia de 3672/09","source_or_basis":"Decretos 1795/1796 + Memoria 2009 + Decreto 759","caveat":"no atribuir firma por interpolación serial"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V175.csv", list({r["key_id"]: r for r in keys + new_keys}.values()))

objects = read_csv(HERE / "E0_V175_REQUEST_OBJECTS.csv")
new_objects = [
    {"row_id":"RO175_30","object_id":"SIGEN_3672_SISIO_OBSERVATION_HISTORY","custodian":"SIGEN · SISIO/UAI/gerencia competente","exact_record":"exportación de observaciones cargadas o instruidas por Nota 3672/09-GSEyP","period":"2009-actualidad/último estado","minimum_fields":"ID; informe origen; organismo; hallazgo; estado; historial fechado; acciones; soportes; cierre","closure_rule":"exportación íntegra con identificadores o negativo fundado por tablas/campos","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO175_31","object_id":"SIGEN_3672_REMIT_ROUTE_RECEIPT","custodian":"SIGEN · Secretaría General/Mesa/Archivo","exact_record":"hoja de ruta, remito y aviso de recibo de Nota 3672/09","period":"2009","minimum_fields":"número; fecha; área; firmante; destinatario; dirección; remito; acuse; contenedor; folio","closure_rule":"copia del original o certificación de búsqueda por serie y contenedor","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO175_32","object_id":"CGN_ANNUAL_DAIF_SIGEN_NOTES_2010_2012","custodian":"CGN · DAIF/Mesa/Archivo","exact_record":"Notas 112/10, 93/11, 145/12, anexos, respuestas y expedientes","period":"2010-2012","minimum_fields":"nota; fecha; asunto; adjuntos; observaciones; correcciones; respuesta; expediente; archivo","closure_rule":"cuerpos y anexos completos o negativo fundado individual","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO175_33","object_id":"CGN_UEPEX_CORRECTION_BEFORE_AFTER_LEDGER","custodian":"CGN · DAIF/SIDIF/Archivo","exact_record":"detalle de reemplazos, regularizaciones y ajustes derivados del control UEPEX","period":"cierre 2008 a Cuenta 2013","minimum_fields":"organismo; cuadro; inconsistencia; importe; antes; después; SIDIF; certificante; fecha; vínculo observación","closure_rule":"ledger auditable y conciliable con Cuentas; agregado narrativo no cierra","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO175_34","object_id":"SIGEN_3672_SIGNATORY_DELEGATION_AND_CUSTODY","custodian":"SIGEN · Secretaría General/GSEyP/Archivo","exact_record":"metadatos de firma, delegación, CIDD, SPD y archivo de Nota 3672/09","period":"2009","minimum_fields":"fecha/hora; firmante; cargo; delegación; destinatario; asunto; adjuntos; CIDD; SPD; caja; remito","closure_rule":"registro primario y cuerpo o certificación técnica/archivística trazable","status":"DRAFT_NOT_SENT"},
]
objects = list({r["row_id"]: r for r in objects + new_objects}.values())
write_csv(HERE / "E0_V175_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V175_REQUEST_OBJECTS_V175.csv", objects)

addendum = """

## Adenda V175 · historial SISIO, remito y cuantificación antes/después

La prueba pública ya permite afirmar cuatro extremos distintos: (1) la Nota 3672/09 fue referida como instrucción de seguimiento; (2) en 2009 SIGEN operaba SISIO y un circuito documentado de estados y acciones; (3) SIGEN mantenía archivo digital de Mesa de Entradas y reordenaba su Archivo General; y (4) las Cuentas UEPEX 2010-2013 describen sustitución de cuadros, regularizaciones SIDIF, ajustes y subsanaciones. También existe una reproducción pública de un inventario judicial que describe numeración correlativa de remitos de diciembre de 2009 y avisos de recibo originales.

La convergencia prueba el mecanismo y la capacidad institucional, pero todavía no autoriza atribuir una corrección o un importe concreto a la Nota 3672. Para cerrar ese salto se solicitan: exportación SISIO con IDs e historial de estados; hoja de ruta, remito y acuse de 3672; cuerpos y anexos de las Notas DAIF 112/10, 93/11 y 145/12; y un ledger por organismo/cuadro/documento SIDIF con valores antes/después, fecha y certificante. Debe existir una unión uno-a-uno entre 0120/09, 3672/09, observación SISIO, expediente CGN y corrección cuantificada.

Los Decretos 1795 y 1796 delimitan un relevo de autoridad en noviembre de 2009, pero no identifican al firmante de 3672: sin fecha/cuerpo o delegación no debe asignarse. Las búsquedas exactas en las páginas públicas 2010-2013 no encontraron `3672`, `0120/09` ni `SISIO`; ese cero está limitado a esas páginas y no es un negativo de archivos o sistemas. Solicitudes 0; todos los objetos siguen `DRAFT_NOT_SENT`; SAF355 0/5; ejecución bancaria 0/10.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V175.md", "REQUEST_SUBMISSION_CHECKLIST_V175.md", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V175.md"):
    path = HERE / name
    body = path.read_text(encoding="utf-8-sig")
    if "Adenda V175 · historial SISIO" not in body:
        path.write_text(body + addendum, encoding="utf-8")

strict = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V175.csv")
strict[0]["coverage_set"] = "V175 strict 34-entity set; unchanged from V174"
strict[0]["v161_change"] = "V175: no banking promotion; unchanged from V174."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V175.csv", strict)

public_log = [
    {"log_id":"PUB175_01","surface":"CGN Cuenta 2010 UEPEX","query_or_target":"Nota 112/10 DAIF; 3672; 0120/09; SISIO","result":"mecanismo correctivo y nota anual presentes; exactos 0/0/0","classification":"RECURRING_MECHANISM_POSITIVE_TARGET_CHAIN_ABSENT_FROM_PAGE","limit_or_next_step":"pedir cuerpo/anexos y expediente"},
    {"log_id":"PUB175_02","surface":"CGN Cuenta 2011 UEPEX","query_or_target":"Nota 93/11; 3672; 0120/09; SISIO","result":"mecanismo correctivo presente; exactos 0/0/0","classification":"RECURRING_MECHANISM_POSITIVE_TARGET_CHAIN_ABSENT_FROM_PAGE","limit_or_next_step":"pedir cuerpo/anexos"},
    {"log_id":"PUB175_03","surface":"CGN Cuenta 2012 UEPEX","query_or_target":"Nota 145/12; subsanaciones; exactos","result":"seguimiento positivo; exactos 0/0/0","classification":"FOLLOWUP_POSITIVE_TARGET_CHAIN_ABSENT_FROM_PAGE","limit_or_next_step":"pedir informe y respuestas"},
    {"log_id":"PUB175_04","surface":"CGN Cuenta 2013 UEPEX","query_or_target":"subsanaciones; exactos","result":"continuidad positiva; exactos 0/0/0","classification":"FOLLOWUP_POSITIVE_TARGET_CHAIN_ABSENT_FROM_PAGE","limit_or_next_step":"no convertir ausencia de texto en ausencia archivística"},
    {"log_id":"PUB175_05","surface":"Argentina.gob.ar · Decreto 759/1966 actualizado","query_or_target":"numeración, Mesa de Entradas, movimiento/destino y archivo","result":"deberes normativos localizados","classification":"OFFICIAL_RECORD_DUTY_PROVED","limit_or_next_step":"aplicar a registro objetivo"},
    {"log_id":"PUB175_06","surface":"Argentina.gob.ar · Resolución 2600/2009","query_or_target":"circuito SIGEN, expediente, SISIO, estados y acciones","result":"flujo contemporáneo exacto localizado","classification":"CONTEMPORARY_WORKFLOW_PROVED","limit_or_next_step":"obtener filas target"},
    {"log_id":"PUB175_07","surface":"Memoria SIGEN 2009","query_or_target":"Cuenta, SISIO WEB, archivo digital/general","result":"capacidades localizadas en PDF 6, 7 y 13","classification":"CONTEMPORARY_CAPABILITY_PROVED","limit_or_next_step":"buscar asiento/caja individual"},
    {"log_id":"PUB175_08","surface":"Infoleg · Decretos 1795/1796","query_or_target":"relevo Síndico General noviembre 2009","result":"dos ventanas institucionales delimitadas","classification":"AUTHORITY_BOUNDARY_PROVED_SIGNATORY_OPEN","limit_or_next_step":"no atribuir sin fecha/cuerpo"},
    {"log_id":"PUB175_09","surface":"vLex · reproducción acta TOCF4","query_or_target":"Notas/remitos/avisos SIGEN 2009","result":"rango correlativo y originales descriptos","classification":"PUBLIC_JUDICIAL_REPRODUCTION_CORRELATIVE_PRACTICE","limit_or_next_step":"pedir original SIGEN; host no oficial"},
    {"log_id":"PUB175_10","surface":"Common Crawl","query_or_target":"decisión de reintento","result":"sin consultas V175 por control V174 2/2 SERVICE_ERROR","classification":"DEFERRED_UNTIL_VALID_CONTROL","limit_or_next_step":"40 consultas pendientes; no inferir ausencia"},
]
write_csv(HERE / "V175_PUBLIC_SEARCH_LOG.csv", public_log)

write_csv(HERE / "V175_PDF_VISUAL_CONTROL.csv", [
    {"control_id":"PDF175_01","source_id":"e0_sigen_memoria_2009_archive_sisio_capability_v175","pdf_pages":"6","target":"Cuenta de Inversión 2008; instrucciones/certificaciones","result":"PASS_LEGIBLE_COMPLETE","limit":"capacidad general; no Nota 3672"},
    {"control_id":"PDF175_02","source_id":"e0_sigen_memoria_2009_archive_sisio_capability_v175","pdf_pages":"7","target":"mejoras SISIO WEB; supervisión y seguimiento","result":"PASS_LEGIBLE_COMPLETE","limit":"sin filas target"},
    {"control_id":"PDF175_03","source_id":"e0_sigen_memoria_2009_archive_sisio_capability_v175","pdf_pages":"13","target":"archivo digital de Mesa; reordenamiento/registro Archivo General","result":"PASS_LEGIBLE_COMPLETE","limit":"sin ubicación individual"},
])

bundle = []
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    bundle.append({"role":"V175_SOURCE","path":source["archivo_local"],"url":source["url_original"],"bytes":str(path.stat().st_size),"sha256":source["sha256"],"analytic_use":source["nota"]})
write_csv(HERE / "V175_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync = []
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    if path == FILES["memoria"]:
        verification = "PDF_VISUAL_PASS_TLS_VALID"
    elif path.name.startswith("cgn_cuenta_"):
        verification = "HTML_CONTENT_PASS_CERT_EXPIRED_OR_INVALID_AT_RETRIEVAL"
    elif path == FILES["vlex"]:
        verification = "HTML_CONTENT_PASS_PUBLIC_JUDICIAL_REPRODUCTION_NONOFFICIAL_HOST"
    else:
        verification = "HTML_CONTENT_PASS_TLS_VALID"
    sync.append({"role":"V175_PUBLIC_SOURCE","relative_path":source["archivo_local"],"source_url":source["url_original"],"size_bytes":str(path.stat().st_size),"sha256":source["sha256"],"format_verification":verification})
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V175.csv", sync)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V175.csv", public_log)
(SYNC / "SOURCE_SYNC_REPORT_V175.md").write_text("# Sincronización V175\n\n- Catálogo 623/623; hash válido; brecha 0.\n- Diez fuentes nuevas: nueve oficiales y una reproducción pública de un acta judicial.\n- Memoria SIGEN 2009 controlada visualmente en páginas PDF 6, 7 y 13.\n- Las cuatro páginas históricas CGN se preservaron pese al certificado vencido/inválido del host.\n- Common Crawl no se reintentó: el control V174 había fallado 2/2; cuarenta consultas siguen pendientes.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v175.py").write_text("""from pathlib import Path
import csv,hashlib
root=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V175.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==10
for r in rows:
 p=root/r['relative_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(r['size_bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('SOURCE SYNC V175 PASS · 10/10')
""", encoding="utf-8")

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V175.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    is_primary = "NO_REPRODUCTION" if path == FILES["vlex"] else "YES"
    census.append({"source_id":source["id"],"institution":source["institucion"],"artifact":source["titulo"],"url":source["url_original"],"local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"period_coverage":source["periodo_utilizado"],"variable_families":"Nota3672;SIGEN;SISIO;CGN;archive;corrections","primary_source":is_primary,"preserved":"YES","method_breaks":"target-specific attribution remains open","use_status":"E0_USABLE_METHOD_OR_ARCHIVE_EVIDENCE","caveat":source["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V175.csv", list({r["source_id"]: r for r in census}.values()))

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V175.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    if path.name.startswith("cgn_cuenta_"):
        provenance = "DIRECT_OFFICIAL_HISTORICAL_HOST_CERTIFICATE_INVALID_OR_EXPIRED"
    elif path == FILES["vlex"]:
        provenance = "PUBLIC_JUDICIAL_REPRODUCTION_NONOFFICIAL_HOST"
    else:
        provenance = "N/A_OFFICIAL_DIRECT_TLS_VALID"
    prov.append({"source_id":source["id"],"original_url":source["url_original"],"retrieval_url":source["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":provenance,"local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"provenance_note":source["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V175.csv", list({r["source_id"]: r for r in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V175.md").open("a", encoding="utf-8") as f:
    f.write("\n## V175 · circuito correctivo, SISIO, archivo y remitos\n")
    for source in sources:
        f.write(f"\n- `{source['id']}` · {source['titulo']} · {source['url_original']} · `{source['archivo_local']}` · `{source['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V175.md").open("a", encoding="utf-8") as f:
    f.write("\n## V175\n\n- Cuentas CGN 2010-2013 preservadas: continuidad del mecanismo correctivo; exactos 3672/0120/09/SISIO ausentes sólo de esas páginas.\n- Resolución 2600/2009 preservada: flujo SIGEN-expediente-SISIO-acciones y estados.\n- Memoria SIGEN 2009 preservada y controlada visualmente: Cuenta, SISIO WEB y archivo.\n- Acta judicial reproducida por vLex preservada con rangos correlativos de remitos/notas y avisos originales; host no oficial.\n- Common Crawl no reintentado por control inválido previo.\n")

recovery = f"""# Recuperación archivística · V175

La evidencia contemporánea prueba que SIGEN tenía capacidad operativa y archivística para registrar, seguir y conservar el circuito: Memoria 2009 (Cuenta, SISIO WEB y archivo digital/general), Resolución 2600/2009 (expedientes, estados SISIO y acciones) y un inventario judicial público (numeración correlativa, remitos y avisos originales). Las Cuentas CGN 2010-2013 prueban continuidad de correcciones y reportes, pero no enlazan públicamente una corrección individual con Nota 3672. Se requieren cuerpo/CIDD/SPD/caja/remito/acuse, expediente receptor, exportación SISIO e historial, y ledger CGN antes/después. No atribuir firmante ni efecto monetario por interpolación. Archivo 623/623; panel 34 y {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V175.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V175.md", "E0_FISCAL_RECONSTRUCTION_V175.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V175.md").write_text(f"# Revisión acumulada V175\n\nPanel 34 y {COVERAGE}% congelado. Se probó el circuito correctivo/archivístico contemporáneo y se definió el test de atribución; Nota 3672 y su efecto específico siguen abiertos. Solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "README_V175.md").write_text(f"""# Checkpoint V175

- Archivo 623/623; diez fuentes nuevas: nueve oficiales y una reproducción pública de un acta judicial; hashes válidos.
- Quedó probado el circuito contemporáneo Nota/informe → expediente → SISIO → estados/acciones, no sus filas objetivo.
- Memoria SIGEN 2009 prueba que SISIO WEB estaba activo y que Mesa mantenía archivo digital mientras se reordenaba y registraba el Archivo General.
- La práctica anual/correlativa y la conservación de remitos/avisos originales están respaldadas por comparadores e inventario judicial público; la regla formal completa y la fila 3672 siguen abiertas.
- Las Cuentas CGN 2010-2013 prueban continuidad del mecanismo correctivo; no enlazan públicamente una corrección o importe individual con 3672/09.
- Test causal: unir 0120/09 → 3672/09 → ID SISIO → expediente CGN → documento SIDIF/cuadro antes-después.
- El relevo Pacios/Reposo delimita candidatos institucionales, pero no identifica al firmante.
- Common Crawl: sin nuevo intento; control V174 falló 2/2 y cuarenta consultas siguen pendientes.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V175.md").write_text("# Veredicto V175\n\nAvance probatorio sustantivo, sin promoción bancaria. El mecanismo institucional de observación, seguimiento SISIO, corrección CGN y custodia documental está probado para el período. La atribución causal y monetaria específica a Nota SIGEN 3672/09 no está probada: faltan cuerpo y metadatos, remito/acuse, expediente receptor, IDs e historial SISIO y ledger antes/después. La formulación defendible es mecanismo y capacidad probados; resultado individual atribuible, abierto.\n", encoding="utf-8")
(HERE / "AUDITORIA_V175.md").write_text(f"# Auditoría V175\n\n- 623/623 fuentes; huecos 0; nuevas 10 (9 oficiales + 1 reproducción pública judicial).\n- PDF visual Memoria SIGEN 2009: páginas 6, 7 y 13 PASS.\n- Cuatro Cuentas CGN 2010-2013: exactos 3672/0120/09/SISIO = 0 por página; mecanismo recurrente positivo.\n- Matrices nuevas: atribución 6, seguimiento 4, numeración/remitos 8, capacidad 4, firmante 3, requisitos 5.\n- Common Crawl: 0 consultas V175; 40 pendientes.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V175_A_V176.md").write_text("""# Handover V175 → V176

## Cerrado
- Archivo 623/623; diez fuentes nuevas con hash válido.
- Flujo contemporáneo SIGEN→expediente→SISIO→acciones/estados probado.
- Capacidad SISIO WEB y archivo digital/general SIGEN en 2009 probada.
- Continuidad de correcciones CGN 2010-2013 probada.
- Práctica correlativa y preservación de remitos/avisos respaldada por comparadores e inventario judicial público.
- Separación explícita entre mecanismo probado y atribución individual abierta.

## Prioridad V176
1. Recuperar cuerpo, fecha, firmante, CIDD, SPD, caja, hoja de ruta, remito y acuse de 3672/09-GSEyP.
2. Obtener expediente/actuación receptor CGN y unir salida/ingreso por número, asunto y 0120/09.
3. Pedir exportación SISIO: IDs, informe origen, organismo, estado histórico, acciones, documentos y cierre.
4. Recuperar Notas DAIF 112/10, 93/11 y 145/12 con anexos/respuestas.
5. Construir ledger CGN por organismo/cuadro/documento SIDIF/importe antes-después; atribuir sólo con join completo.
6. Reintentar Common Crawl únicamente tras control válido; mantener 40 pendientes.
7. Mantener todos los borradores DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V174.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V175", "date":"2026-09-01", "master_catalog_entries":623, "physical_local_copies":623, "physical_local_hash_ok":623, "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_CORRECTIVE_WORKFLOW_PROVED_TARGET_ATTRIBUTION_OPEN", "analytical_promotion":"NONE_V175_METHOD_AND_ARCHIVE_EVIDENCE_ONLY", "exact_entities":34,
    "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS, "strict_coverage_increment_v174_pp":"0",
    "requests_submitted":0, "responses_received":0, "saf355_certifications_located":0, "executed_historical_bank_rows_confirmed":0,
    "note_3672_09_body_located":False, "note_3672_archive_digital_record_located":False, "note_3672_spd_located":False, "note_3672_physical_box_located":False,
    "note_3672_recipient_file_located":False, "note_3672_signatory_located":False, "sigen_2009_note_numbering_rule_located":False,
    "sigen_2009_archive_digital_and_reordering_capability_proved":True, "sisio_contemporary_status_workflow_proved":True,
    "cgn_correction_mechanism_2009_2013_proved":True, "note_3672_specific_causal_attribution_proved":False, "note_3672_specific_monetary_attribution_proved":False,
    "public_judicial_reproduction_note_remit_correlative_practice_located":True, "vlex_host_is_official":False,
    "cgn_followup_pages_exact_3672_hits":0, "cgn_followup_pages_exact_0120_09_hits":0, "cgn_followup_pages_exact_sisio_hits":0,
    "commoncrawl_exact_prefix_queries_v175":0, "commoncrawl_valid_no_capture_v175":0, "commoncrawl_service_errors_v175":0, "commoncrawl_capture_rows_v175":0,
    "commoncrawl_pending_retry_queries":40, "commoncrawl_pending_retry_collections":20, "new_v175_sources":10,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V175.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]: row for row in origins}
for path in iter_files(HIST_ROOT):
    note = "official source preserved V175"
    if path == FILES["vlex"]:
        note = "public judicial reproduction preserved V175; nonofficial host"
    elif path.name.startswith("cgn_cuenta_"):
        note = "official historical page preserved V175; invalid/expired certificate disclosed"
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V175","note":note}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V175","note":"incremental 10-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V175","note":"attribution-gate checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V175.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V175.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V175.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V175.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V175","note":"623-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V175 · circuito probado, atribución abierta" not in body:
    body += "\n\n## V175 · circuito probado, atribución abierta\n\nFuentes contemporáneas prueban el flujo expediente/SISIO/acciones, la capacidad archivística SIGEN 2009 y la continuidad correctiva CGN 2009-2013. No prueban aún qué corrección o importe individual fue causado por Nota 3672/09. La reproducción vLex de un acta judicial se identifica como host no oficial. Archivo 623/623; panel 34; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V175; 623/623 fuentes.\n- Circuito SIGEN/SISIO/CGN y capacidad archivística 2009 probados; atribución individual a 3672 abierta.\n- Diez fuentes nuevas: nueve oficiales y una reproducción pública judicial no oficial.\n- Common Crawl no reintentado; 40 pendientes.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "qa_v175.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==623
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V175.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==623 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V175.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V175' and co['master_catalog_entries']==623
assert co['sigen_2009_archive_digital_and_reordering_capability_proved'] and co['sisio_contemporary_status_workflow_proved'] and co['cgn_correction_mechanism_2009_2013_proved']
assert not co['note_3672_specific_causal_attribution_proved'] and not co['note_3672_specific_monetary_attribution_proved'] and not co['note_3672_signatory_located']
assert co['commoncrawl_exact_prefix_queries_v175']==0 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_NOTE_3672_DIRECTIVE_TO_OUTCOME_ATTRIBUTION_GATE_V175.csv'))==6
assert len(rows('E0_CGN_POST_3672_FOLLOWUP_SEARCH_V175.csv'))==4 and all(x['exact_3672_hits']==x['exact_0120_09_hits']==x['exact_sisio_hits']=='0' for x in rows('E0_CGN_POST_3672_FOLLOWUP_SEARCH_V175.csv'))
assert len(rows('E0_SIGEN_2009_NOTE_NUMBERING_AND_REMIT_EVIDENCE_V175.csv'))==8
assert len(rows('E0_SIGEN_2009_ARCHIVE_AND_SISIO_CAPABILITY_V175.csv'))==4
assert len(rows('E0_NOTE_3672_SIGNATORY_AUTHORITY_WINDOW_V175.csv'))==3
assert len(rows('E0_NOTE_3672_ATTRIBUTION_PROOF_REQUIREMENTS_V175.csv'))==5
assert len(rows('V175_PDF_VISUAL_CONTROL.csv'))==3 and all(x['result'].startswith('PASS') for x in rows('V175_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V175.csv'); assert {'SK175_30','SK175_31','SK175_32','SK175_33','SK175_34'}<={x['key_id'] for x in keys}
obj=rows('E0_V175_REQUEST_OBJECTS.csv'); assert {'RO175_30','RO175_31','RO175_32','RO175_33','RO175_34'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V175_REQUEST_OBJECTS_V175.csv')
for n in ('REQUEST_AGN_2018_REPLY_V175.md','REQUEST_BCRA_CRYL_SETTLEMENT_V175.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V175.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V175.md','REQUEST_CNV_CUSTODY_RECORDS_V175.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V175.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V175.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V175_SOURCE_BUNDLE.csv'))==10
m=json.loads((H/'MANIFEST_V175.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V175' and m['parent_checkpoint']=='V174' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V175 QA PASS · 623/623 · new=10 · WORKFLOW=PROVED · ATTRIBUTION=OPEN · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x: x.name.casefold()) if p.is_file() and p.name != "MANIFEST_V175.json"]
manifest = {
    "checkpoint":"V175", "parent_checkpoint":"V174", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities":34, "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS,
    "new_promotions":[], "source_archive":"623/623; ten sources added (nine official, one public judicial reproduction)",
    "historical_finding":"corrective/archival/SISIO workflow proved; target-specific causal and monetary attribution open",
    "note_3672_09_body":"NOT_LOCATED", "note_3672_recipient_file":"NOT_LOCATED", "note_3672_signatory":"NOT_PROVED",
    "commoncrawl_queries_v175":0, "commoncrawl_pending":40, "closed_network_gate":"NO", "saf355_certifications":"0/5",
    "executed_historical_bank_rows":"0/10", "requests_submitted":0, "files":manifest_files,
}
(HERE / "MANIFEST_V175.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V175","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"623 master; 623 physical SHA-valid","historical_workstream":"workflow proved; target attribution open; CC pending 40; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V175tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V175 BUILD PASS · catalog=623/623 · new=10 · workflow=PROVED · attribution=OPEN · panel=34 · requests=0")
