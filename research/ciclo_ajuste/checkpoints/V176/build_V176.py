from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V175"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v176"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v176"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


FILES = {
    "sisio2014": HIST / "sss_sisio_followup_2014.pdf",
    "sisio2015": HIST / "sss_sisio_followup_2015.pdf",
    "sisio2016": HIST / "sss_sisio_followup_2016.pdf",
    "sisio2017": HIST / "sss_sisio_regularized_2017.pdf",
}
EXPECTED = {
    FILES["sisio2014"]: (15361262, "2b6eca65df8020e0913c7155cd1d4741cb3607fdbf55bb96b57ef73948b3653e"),
    FILES["sisio2015"]: (15217531, "d9fffbf9778249130eb35dad341841c97f4b706ae57b3e6405d9b7e87fbc7ef0"),
    FILES["sisio2016"]: (21137430, "4a797ec62a538f3df050dfdab856634eeb1cf8f0d8540b62ac8b746b023a8655"),
    FILES["sisio2017"]: (1878615, "cec0e2007197669cb92bd58199d05f5fca0e56e56b070e28221f487184cd2e8e"),
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


def clone_parent():
    skip = {
        "MANIFEST_V175.json", "README_V175.md", "VEREDICTO_V175.md", "AUDITORIA_V175.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V175_A_V176.md", "V175_SOURCE_BUNDLE.csv",
        "V175_PUBLIC_SEARCH_LOG.csv", "V175_PDF_VISUAL_CONTROL.csv",
        "V175_PDF_VISUAL_AND_TEXT_CONTROL.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V175", "V176")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V175", "V176"), encoding="utf-8")


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest

source_specs = [
    (
        "e0_sss_sisio_followup_2014_account2008_observation_v176",
        "Informe de Auditoría UAI SSS 02/2014 · exportación SISIO de observaciones en trámite",
        "https://www.argentina.gob.ar/sites/default/files/informe_02-14_-_resolucion_15_2006_-_sgn.pdf",
        FILES["sisio2014"], "2014", "Informe UAI SSS 02/2014 · PDF 6 y 17",
        "Prueba una observación Cuenta de Inversión 2008 identificada por organismo, informe 04/2009, observación 5 y sector, en trámite al 31/12/2013. También prueba una fila UEPEX de 2013 con estado, motivo, hallazgo y recomendación.",
    ),
    (
        "e0_sss_sisio_followup_2015_account2008_observation_v176",
        "Informe de Auditoría UAI SSS 02/2015 · persistencia SISIO de observaciones",
        "https://www.argentina.gob.ar/sites/default/files/informe_02-15_-_resolucion_152006_-_sgn.pdf",
        FILES["sisio2015"], "2015", "Informe UAI SSS 02/2015 · PDF 6 y 16",
        "Prueba que la misma clave compuesta Cuenta 2008/Informe 04/2009/Obs.5 seguía en trámite al 29/12/2014 y que la observación UEPEX 2012 persistía al 03/06/2014.",
    ),
    (
        "e0_sss_sisio_followup_2016_account2008_and_uepex_disposition_v176",
        "Informe de Auditoría UAI SSS 02/2016 · seguimiento SISIO y casos no regularizables",
        "https://www.argentina.gob.ar/sites/default/files/informe_02-16_-_resolucion_15-2006_-_sgn_0.pdf",
        FILES["sisio2016"], "2016", "Informe UAI SSS 02/2016 · PDF 10 y 44",
        "Prueba la Cuenta 2008/Obs.5 aún en trámite al 18/02/2016 y una observación UEPEX con importes, motivo y comentario de no regularizabilidad por cierre del proyecto y cuenta bancaria.",
    ),
    (
        "e0_sss_sisio_regularized_2017_account2008_observation_v176",
        "Listado UAI SSS 2017 · observaciones regularizadas durante 2016",
        "https://www.argentina.gob.ar/sites/default/files/informe_no_02-17_resolucion_15-2006_sgn_anexo_iii_de_la_resolucion_73-10_sgn.pdf",
        FILES["sisio2017"], "2017-02-14", "Anexo III Res. 73/10 SGN · PDF 1",
        "Prueba que la Cuenta 2008/Informe 04/2009/Obs.5 pasó al listado de observaciones regularizadas por cumplimiento de recomendación el 30/12/2016.",
    ),
]

sources = []
for source_id, title, url, path, publication, code, note in source_specs:
    sources.append({
        "id":source_id, "tema":"ciclo_ajuste_e0_fiscal", "institucion":"Superintendencia de Servicios de Salud · Unidad de Auditoría Interna / SIGEN",
        "titulo":title, "url_original":url, "archivo_local":"/" + path.relative_to(REPO).as_posix(),
        "fecha_descarga":"2026-09-01", "fecha_publicacion":publication, "codigo_serie":code,
        "periodo_utilizado":"2008-2016", "tipo":"PDF oficial preservado · exportación SISIO controlada visualmente",
        "sha256":EXPECTED[path][1], "nota":note,
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]:row for row in catalog}
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 627

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({
        "id":row["id"], "archivo_local":row["archivo_local"], "exists":str(path.is_file()),
        "sha_catalog":row["sha256"].lower(), "sha_actual":actual,
        "hash_ok":str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V176.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V176.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V176.csv", missing, list(audit[0]))
assert not missing

write_csv(HERE / "E0_SISIO_COMPOSITE_KEY_LONGITUDINAL_EXAMPLE_V176.csv", [
    {"row_id":"LH176_01","entity":"UAI-SUPERINTENDENCIA DE SERVICIOS DE SALUD","report":"04","report_date":"20/04/2009","observation":"5","title":"Cuenta de Inversión 2008","sector":"Gerencia de Administración","snapshot_date":"31/12/2013","status":"En Trámite","motive":"Elaboración de Norma y/o Procedimiento","event":"hallazgo activo","source":"Informe UAI 02/2014 PDF 6"},
    {"row_id":"LH176_02","entity":"UAI-SUPERINTENDENCIA DE SERVICIOS DE SALUD","report":"04","report_date":"20/04/2009","observation":"5","title":"Cuenta de Inversión 2008","sector":"Gerencia de Administración","snapshot_date":"29/12/2014","status":"En Trámite","motive":"Elaboración de Norma y/o Procedimiento","event":"misma clave compuesta persistente","source":"Informe UAI 02/2015 PDF 6"},
    {"row_id":"LH176_03","entity":"UAI-SUPERINTENDENCIA DE SERVICIOS DE SALUD","report":"04","report_date":"20/04/2009","observation":"5","title":"Cuenta de Inversión 2008","sector":"Gerencia de Administración","snapshot_date":"18/02/2016","status":"En Trámite","motive":"No Aplica","event":"misma observación; motivo modificado","source":"Informe UAI 02/2016 PDF 10"},
    {"row_id":"LH176_04","entity":"UAI-SUPERINTENDENCIA DE SERVICIOS DE SALUD","report":"04","report_date":"20/04/2009","observation":"5","title":"Cuenta de Inversión 2008","sector":"Gerencia de Administración","snapshot_date":"30/12/2016","status":"Regularizada","motive":"Cumplimiento Recomendación","event":"incorporada al listado anual de regularizadas","source":"Listado 2017 PDF 1"},
])

write_csv(HERE / "E0_SISIO_UEPEX_STATUS_SEMANTICS_V176.csv", [
    {"row_id":"US176_01","composite_key":"SSS|Informe 05|24/05/2013|Obs.6|Cuenta 2012","snapshot":"03/06/2014","status_or_motive":"En Trámite · Elaboración de Norma/Procedimiento","finding":"PNUD ARG 10/022 FORSALUD; inconsistencias Disponibilidades-Otros entre cierre 2011 e inicio 2012","disposition":"pendiente de verificar y regularizar","classification":"OPEN_CORRECTION"},
    {"row_id":"US176_02","composite_key":"SSS|Informe 05|24/05/2013|Obs.6|Cuenta 2012","snapshot":"03/06/2014 en informe 2015","status_or_motive":"En Trámite · Elaboración de Norma/Procedimiento","finding":"misma inconsistencia UEPEX y cuadros 13.3/Fuentes y Usos/Patrimonio Neto","disposition":"persistente","classification":"OPEN_CORRECTION"},
    {"row_id":"US176_03","composite_key":"SSS|Informe 05|24/05/2013|Obs.6|Cuenta 2012","snapshot":"19/02/2016","status_or_motive":"Seguimiento no asociado a Informe","finding":"misma inconsistencia UEPEX","disposition":"comentario: no regularizable porque proyecto terminó en 2013 y la cuenta bancaria cerró el 22/07/2013","classification":"NONREGULARIZABLE_NOT_CORRECTED"},
    {"row_id":"US176_04","composite_key":"SSS|Informe 07|28/06/2013|Obs.2|ARG/10/022","snapshot":"19/02/2016","status_or_motive":"Seguimiento no asociado a Informe","finding":"diferencias de saldos iniciales/finales atribuidas a tipos de cambio PNUD","disposition":"no regularizable por cierre de proyecto/cuenta; conserva importes y explicación","classification":"QUANTIFIED_DISCONTINUITY_WITH_EXPLANATION"},
    {"row_id":"US176_05","composite_key":"regla metodológica","snapshot":"V176","status_or_motive":"estado y motivo son dimensiones separadas","finding":"regularizada, en trámite, no regularizable y seguimiento no asociado no son equivalentes","disposition":"pedir historial completo y comentario, no sólo último estado","classification":"REQUEST_AND_ANALYSIS_RULE"},
])

amount_rows = [
    ("AM176_01", "31/12/2011→01/01/2012", "5124915.77", "5185413.97", "-60498.20"),
    ("AM176_02", "31/12/2012→01/01/2013", "2468589.94", "2429294.25", "39295.69"),
    ("AM176_03", "31/03/2013→13/05/2013", "2272507.35", "2262970.52", "9536.83"),
]
amounts = []
for row_id, bridge, final_value, next_initial, reported_difference in amount_rows:
    calculated = Decimal(final_value) - Decimal(next_initial)
    assert calculated == Decimal(reported_difference)
    amounts.append({
        "row_id":row_id, "bridge":bridge, "prior_final_ars":final_value, "next_initial_ars":next_initial,
        "calculated_final_minus_initial_ars":str(calculated), "reported_difference_ars":reported_difference,
        "reported_explanation":"tipo de cambio informado por PNUD días después del cierre", "status_2016":"no regularizable por cierre del proyecto y cuenta",
        "analytic_limit":"ejemplo 2011-2013; no corresponde al target 2008 ni prueba apropiación",
    })
write_csv(HERE / "E0_SISIO_UEPEX_AMOUNT_DISCONTINUITY_EXAMPLE_V176.csv", amounts)

write_csv(HERE / "E0_SISIO_OUTCOME_CLASSIFICATION_RULES_V176.csv", [
    {"rule_id":"OC176_01","observed_label":"En Trámite","allowed_conclusion":"observación seguía abierta en la fecha del snapshot","forbidden_conclusion":"hubo corrección o incumplimiento definitivo"},
    {"rule_id":"OC176_02","observed_label":"Regularizada · Cumplimiento Recomendación","allowed_conclusion":"la UAI/SISIO la incluyó como regularizada por ese motivo y fecha","forbidden_conclusion":"importe recuperado o causalidad de Nota 3672 sin documento de acción"},
    {"rule_id":"OC176_03","observed_label":"No regularizable / proyecto o cuenta cerrados","allowed_conclusion":"el seguimiento no podía continuar bajo ese objeto según comentario","forbidden_conclusion":"la inconsistencia fue corregida"},
    {"rule_id":"OC176_04","observed_label":"Seguimiento no asociado a Informe","allowed_conclusion":"modo/motivo de seguimiento de la fila","forbidden_conclusion":"ausencia de informe origen; la clave compuesta aún lo identifica"},
    {"rule_id":"OC176_05","observed_label":"fila ausente en una lista anual","allowed_conclusion":"no estaba en esa exportación/filtro","forbidden_conclusion":"regularización, eliminación o inexistencia sin historial"},
    {"rule_id":"OC176_06","observed_label":"diferencia de saldos cuantificada","allowed_conclusion":"discontinuidad contable a explicar y conciliar","forbidden_conclusion":"daño, desvío o beneficio sin causa, documentación y contraparte"},
])

write_csv(HERE / "E0_NOTE_3672_SISIO_TARGET_EXPORT_SCHEMA_V176.csv", [
    {"field_group":"composite_identity","required_fields":"organismo/entidad; UAI; informe número; informe fecha; observación número; título; sector","why":"Obs.5 no es globalmente única; la unión exige clave compuesta","closure":"todos los hallazgos cargados por 3672 identificados sin colisiones"},
    {"field_group":"directive_origin","required_fields":"Nota 0120/09; Nota 3672/09; fecha de alta; usuario; área; documento adjunto","why":"separar fila SISIO de la orden que dispuso cargarla","closure":"referencia documental uno-a-uno"},
    {"field_group":"substance","required_fields":"calificación/impacto; texto íntegro del hallazgo; recomendación; comentario; acción encarada","why":"el estado solo no explica contenido ni respuesta","closure":"texto y acciones completos"},
    {"field_group":"history","required_fields":"cada fecha; estado; motivo; usuario/área; comentario; documento soporte","why":"la misma fila cambió de motivo y luego de estado","closure":"historial no sobrescrito"},
    {"field_group":"financial_join","required_fields":"SAF; UEPEX/proyecto; préstamo; cuadro; cuenta bancaria; moneda; importe; período; documento SIDIF","why":"permitir cuantificación y reconciliación","closure":"join con ledger CGN antes/después"},
    {"field_group":"disposition","required_fields":"regularizada/no regularizable/otra; razón; fecha; acto/documento; cierre proyecto/cuenta","why":"no confundir cierre administrativo con corrección","closure":"clasificación mutuamente excluyente y fundada"},
])

# Update the signatory conclusion using the already-preserved official Cuenta 2009 text.
write_csv(HERE / "E0_NOTE_3672_SIGNATORY_AUTHORITY_WINDOW_V176.csv", [
    {"row_id":"SG176_01","officeholder":"rol firmante","official_event":"Cuenta 2009 dice literalmente que la Nota 3672/09 fue suscripta por el Señor Síndico General de la Nación","boundary":"2009; fecha exacta abierta","target_implication":"cargo del firmante probado","status":"SIGNATORY_ROLE_PROVED_PERSON_OPEN"},
    {"row_id":"SG176_02","officeholder":"Carlos Pacios","official_event":"renuncia aceptada por Decreto 1795/2009","boundary":"hasta relevo 19-20/11/2009","target_implication":"candidato personal si la nota precede el relevo","status":"DO_NOT_ATTRIBUTE_WITHOUT_EXACT_DATE_OR_BODY"},
    {"row_id":"SG176_03","officeholder":"Daniel Reposo","official_event":"designación por Decreto 1796/2009","boundary":"desde 20/11/2009","target_implication":"candidato personal si la nota es posterior","status":"DO_NOT_ATTRIBUTE_WITHOUT_EXACT_DATE_OR_BODY"},
    {"row_id":"SG176_04","officeholder":"persona firmante de Nota 3672/09-GSEyP","official_event":"ABIERTO","boundary":"fecha exacta abierta","target_implication":"el cargo no resuelve la persona en el relevo","status":"PERSONAL_SIGNATORY_NOT_PROVED"},
])

write_csv(HERE / "E0_NOTE_3672_ATTRIBUTION_PROOF_REQUIREMENTS_V176.csv", [
    {"requirement_id":"PR176_01","dataset":"SISIO","minimum_fields":"clave compuesta entidad+UAI+informe+número/fecha+observación+título+sector; hallazgo; recomendación; acciones; historial estado/motivo/comentario","join_keys":"3672/09; 0120/09; UEPEX; cierre 2008; organismo; informe","closure_test":"cada observación instruida identificada y trazada sin colisiones"},
    {"requirement_id":"PR176_02","dataset":"CGN / DAIF","minimum_fields":"cuadro antes/después; inconsistencia; importe; moneda; formulario SIDIF; certificante; fecha; respuesta","join_keys":"proyecto/organismo; cuadro; formulario; ejercicio; observación","closure_test":"corrección específica cuantificada y documentalmente vinculada"},
    {"requirement_id":"PR176_03","dataset":"Mesa SIGEN / CIDD / SPD / archivo","minimum_fields":"número; fecha; firmante persona/cargo; destinatario; asunto; adjuntos; expediente; acceso; caja; remito; acuse","join_keys":"3672/09-GSEyP","closure_test":"identidad, emisión, entrega, custodia y contenido primario cerrados"},
    {"requirement_id":"PR176_04","dataset":"Mesa CGN / expediente receptor","minimum_fields":"entrada; fecha; remitente; número nota; expediente; pases; anexos; respuesta; archivo","join_keys":"3672/09; asunto; 0120/09","closure_test":"salida SIGEN unida uno-a-uno con ingreso y expediente CGN"},
    {"requirement_id":"PR176_05","dataset":"clasificación de resultado","minimum_fields":"estado, motivo, comentario, acción, fecha y documento de cierre","join_keys":"clave compuesta SISIO","closure_test":"separar regularizada, abierta y no regularizable; no tratar cierre de proyecto como corrección"},
    {"requirement_id":"PR176_06","dataset":"atribución causal","minimum_fields":"secuencia temporal; orden concreta; destinatario; acción posterior; fuentes alternativas; resultado medible","join_keys":"observación e identificadores documentales comunes","closure_test":"no confundir persistencia/cierre administrativo con efecto causado por 3672"},
])

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V176.csv")
new_keys = [
    {"key_id":"SK176_40","request_id":"REQ155_SIGEN","key_group":"sisio_composite_key","exact_key":"entidad+UAI+informe número/fecha+observación+título+sector para cada alta derivada de 3672/09","search_purpose":"evitar colisiones de observaciones numeradas localmente","source_or_basis":"exportaciones SISIO SSS 2014-2017","caveat":"número de observación aislado no identifica fila"},
    {"key_id":"SK176_41","request_id":"REQ155_SIGEN","key_group":"full_status_history","exact_key":"historial no sobrescrito de estado, motivo, comentario, acción, fecha, usuario y soporte","search_purpose":"distinguir en trámite, regularizada y no regularizable","source_or_basis":"trayectorias públicas V176","caveat":"último estado solo no cierra"},
    {"key_id":"SK176_42","request_id":"REQ155_SIGEN","key_group":"all_dispositions","exact_key":"incluir filas regularizadas, pendientes, no regularizables, no compartidas y seguimiento no asociado","search_purpose":"evitar sesgo por filtro de exportación","source_or_basis":"SISIO4 Anexos_RESULT","caveat":"ausencia en un listado anual no prueba eliminación"},
    {"key_id":"SK176_43","request_id":"REQ133_ECON","key_group":"financial_join","exact_key":"SAF, UEPEX, préstamo, cuadro, cuenta, moneda, importes, período, SIDIF y documento correctivo","search_purpose":"unir observación con diferencia y corrección","source_or_basis":"ejemplo UEPEX cuantificado V176","caveat":"diferencia no equivale a daño"},
    {"key_id":"SK176_44","request_id":"REQ155_SIGEN","key_group":"signatory_person","exact_key":"fecha exacta y persona firmante de Nota 3672/09; cargo Síndico General ya probado","search_purpose":"resolver relevo Pacios/Reposo","source_or_basis":"Cuenta 2009 + Decretos 1795/1796","caveat":"no interpolar persona"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V176.csv", list({row["key_id"]:row for row in keys + new_keys}.values()))

objects = read_csv(HERE / "E0_V176_REQUEST_OBJECTS.csv")
new_objects = [
    {"row_id":"RO176_40","object_id":"SIGEN_3672_SISIO_COMPOSITE_HISTORY_EXPORT","custodian":"SIGEN · SISIO/UAI/gerencia competente","exact_record":"todas las observaciones dadas de alta o instruidas por Nota 3672/09, con clave compuesta e historial","period":"2009-último estado","minimum_fields":"entidad; UAI; informe número/fecha; observación; título; sector; hallazgo; recomendación; estado; motivo; comentario; acción; fechas; soportes","closure_rule":"exportación de todos los estados/filtros, no sólo vigentes o regularizados","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO176_41","object_id":"SIGEN_3672_SISIO_ORIGIN_DOCUMENT_CROSSWALK","custodian":"SIGEN · SISIO/Archivo/GSEyP","exact_record":"crosswalk alta SISIO ↔ Nota 3672/09 ↔ 0120/09 ↔ informe/adjunto origen","period":"2009-2010","minimum_fields":"IDs; fechas; usuario; área; documentos; rutas; adjuntos; checksum o folio","closure_rule":"unión uno-a-uno por cada fila o negativo técnico fundado","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO176_42","object_id":"SIGEN_3672_SISIO_ALL_DISPOSITIONS","custodian":"SIGEN · SISIO/UAI","exact_record":"disposición final o actual de cada hallazgo derivado de 3672","period":"2009-último estado","minimum_fields":"regularizada; en trámite; no regularizable; no compartida; motivo; comentario; fecha; acción; documento de cierre","closure_rule":"universo exhaustivo y categorías mutuamente excluyentes","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO176_43","object_id":"CGN_3672_OBSERVATION_FINANCIAL_JOIN","custodian":"CGN · DAIF/SIDIF/Archivo","exact_record":"join por observación con SAF/UEPEX/préstamo/cuadro/cuenta/importe y corrección","period":"cierre 2008 a seguimiento","minimum_fields":"clave SISIO; SAF; proyecto; préstamo; cuenta; moneda; antes; después; diferencia; explicación; documento SIDIF; certificante","closure_rule":"ledger conciliable; diferencias explicadas y resultado clasificado","status":"DRAFT_NOT_SENT"},
]
objects = list({row["row_id"]:row for row in objects + new_objects}.values())
write_csv(HERE / "E0_V176_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V176_REQUEST_OBJECTS_V176.csv", objects)

addendum = """

## Adenda V176 · clave compuesta, historial y disposición SISIO

Cuatro exportaciones oficiales SISIO de la UAI de la Superintendencia de Servicios de Salud muestran cómo debe identificarse y auditarse una observación real. La fila `SSS + Informe 04 de 20/04/2009 + Observación 5 + Cuenta de Inversión 2008 + Gerencia de Administración` permaneció En Trámite en snapshots de 2013, 2014 y febrero de 2016 y fue incluida como Regularizada por Cumplimiento de Recomendación el 30/12/2016. Esto prueba que el número de observación aislado no es una clave global y que el historial no debe sobrescribirse.

Otra fila específicamente UEPEX prueba una cautela adicional: una inconsistencia de saldos pasó de En Trámite a un comentario de no regularizabilidad porque el proyecto y su cuenta bancaria habían cerrado. El mismo paquete conserva diferencias monetarias y una explicación por tipos de cambio PNUD. Por ello, `no regularizable`, `regularizada`, `en trámite` y `seguimiento no asociado a informe` deben entregarse y analizarse como categorías distintas. El cierre de un proyecto o cuenta no prueba corrección, y una diferencia contable no prueba daño.

Para la Nota 3672/09 se solicita un export completo de todos los filtros y estados, con clave compuesta entidad/UAI/informe/fecha/observación/título/sector, hallazgo, recomendación, acciones, estado, motivo, comentario, fechas y documentos. Cada fila debe vincularse a 3672/09, 0120/09, expediente CGN y ledger financiero. La Cuenta 2009 ya prueba que la nota fue suscripta por el Síndico General; la identidad personal sigue abierta hasta recuperar fecha o cuerpo. Solicitudes 0; objetos `DRAFT_NOT_SENT`; SAF355 0/5; ejecución bancaria 0/10.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V176.md", "REQUEST_SUBMISSION_CHECKLIST_V176.md", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V176.md"):
    path = HERE / name
    body = path.read_text(encoding="utf-8-sig")
    if "Adenda V176 · clave compuesta" not in body:
        path.write_text(body + addendum, encoding="utf-8")

strict = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V176.csv")
strict[0]["coverage_set"] = "V176 strict 34-entity set; unchanged from V175"
strict[0]["v161_change"] = "V176: no banking promotion; unchanged from V175."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V176.csv", strict)

public_log = [
    {"log_id":"PUB176_01","surface":"web exact search","query_or_target":"Nota 112/10 DAIF","result":"sin cuerpo autónomo; sólo referencia Cuenta 2010","classification":"REFERENCED_BODY_NOT_LOCATED","limit_or_next_step":"pedido CGN por nota/anexos/expediente"},
    {"log_id":"PUB176_02","surface":"web exact search","query_or_target":"Nota DAIF 93/11","result":"sin cuerpo autónomo; sólo referencia Cuenta 2011","classification":"REFERENCED_BODY_NOT_LOCATED","limit_or_next_step":"pedido CGN"},
    {"log_id":"PUB176_03","surface":"web exact search","query_or_target":"Nota DAIF 145/12","result":"sin cuerpo autónomo; sólo referencia Cuenta 2012","classification":"REFERENCED_BODY_NOT_LOCATED","limit_or_next_step":"pedido CGN"},
    {"log_id":"PUB176_04","surface":"Argentina.gob.ar · Informe UAI SSS 02/2014","query_or_target":"Cuenta 2008 Obs.5 + UEPEX Obs.6","result":"filas SISIO, estados y campos localizados","classification":"OFFICIAL_SISIO_EXPORT","limit_or_next_step":"comparador; no prueba vínculo 3672"},
    {"log_id":"PUB176_05","surface":"Argentina.gob.ar · Informe UAI SSS 02/2015","query_or_target":"persistencia de mismas claves","result":"En Trámite confirmado","classification":"OFFICIAL_LONGITUDINAL_SNAPSHOT","limit_or_next_step":"comparador"},
    {"log_id":"PUB176_06","surface":"Argentina.gob.ar · Informe UAI SSS 02/2016","query_or_target":"Cuenta 2008 + UEPEX no regularizable","result":"historial, importes y comentarios localizados","classification":"OFFICIAL_STATUS_AND_AMOUNT_EVIDENCE","limit_or_next_step":"no extrapolar a target"},
    {"log_id":"PUB176_07","surface":"Argentina.gob.ar · listado regularizadas 2017","query_or_target":"Cuenta 2008 Obs.5","result":"Regularizada 30/12/2016 por cumplimiento","classification":"OFFICIAL_FINAL_DISPOSITION","limit_or_next_step":"pedir igual salida para target"},
    {"log_id":"PUB176_08","surface":"Cuenta 2009 oficial ya preservada","query_or_target":"frase de firma Nota 3672","result":"suscripta por el Señor Síndico General","classification":"SIGNATORY_ROLE_PROVED_PERSON_OPEN","limit_or_next_step":"fecha/cuerpo para Pacios o Reposo"},
    {"log_id":"PUB176_09","surface":"Common Crawl","query_or_target":"decisión de reintento","result":"sin consultas V176; control V174 falló 2/2","classification":"DEFERRED_UNTIL_VALID_CONTROL","limit_or_next_step":"40 pendientes"},
]
write_csv(HERE / "V176_PUBLIC_SEARCH_LOG.csv", public_log)

write_csv(HERE / "V176_PDF_VISUAL_CONTROL.csv", [
    {"control_id":"PDF176_01","source_id":sources[0]["id"],"pdf_pages":"6","target":"Cuenta 2008 Obs.5; clave/estado/fecha/hallazgo/recomendación","result":"PASS_LEGIBLE_COMPLETE","limit":"comparador SSS"},
    {"control_id":"PDF176_02","source_id":sources[0]["id"],"pdf_pages":"17","target":"UEPEX Obs.6 en trámite","result":"PASS_LEGIBLE_COMPLETE","limit":"ejercicio 2012"},
    {"control_id":"PDF176_03","source_id":sources[1]["id"],"pdf_pages":"6","target":"persistencia Cuenta 2008 Obs.5","result":"PASS_LEGIBLE_COMPLETE","limit":"comparador SSS"},
    {"control_id":"PDF176_04","source_id":sources[1]["id"],"pdf_pages":"16","target":"persistencia UEPEX Obs.6","result":"PASS_LEGIBLE_COMPLETE","limit":"ejercicio 2012"},
    {"control_id":"PDF176_05","source_id":sources[2]["id"],"pdf_pages":"10","target":"Cuenta 2008 Obs.5 en trámite 18/02/2016","result":"PASS_LEGIBLE_COMPLETE","limit":"no vínculo 3672"},
    {"control_id":"PDF176_06","source_id":sources[2]["id"],"pdf_pages":"44","target":"UEPEX importes, comentario y no regularizabilidad","result":"PASS_LEGIBLE_COMPLETE","limit":"ejemplo posterior"},
    {"control_id":"PDF176_07","source_id":sources[3]["id"],"pdf_pages":"1","target":"Cuenta 2008 Obs.5 regularizada 30/12/2016","result":"PASS_LEGIBLE_COMPLETE","limit":"motivo UAI; sin importe"},
])

bundle = []
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    bundle.append({"role":"V176_OFFICIAL_SISIO_EXPORT","path":source["archivo_local"],"url":source["url_original"],"bytes":str(path.stat().st_size),"sha256":source["sha256"],"analytic_use":source["nota"]})
write_csv(HERE / "V176_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync = []
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    sync.append({"role":"V176_PUBLIC_SOURCE","relative_path":source["archivo_local"],"source_url":source["url_original"],"size_bytes":str(path.stat().st_size),"sha256":source["sha256"],"format_verification":"PDF_VISUAL_PASS_TLS_VALID"})
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V176.csv", sync)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V176.csv", public_log)
(SYNC / "SOURCE_SYNC_REPORT_V176.md").write_text("# Sincronización V176\n\n- Catálogo 627/627; hash válido; brecha 0.\n- Cuatro exportaciones oficiales SISIO/UAI SSS nuevas.\n- Siete páginas PDF controladas visualmente.\n- Quedaron preservadas una trayectoria 2009→2016 y una fila UEPEX con importes/no regularizabilidad.\n- Common Crawl no se reintentó; cuarenta consultas pendientes.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v176.py").write_text("""from pathlib import Path
import csv,hashlib
root=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V176.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==4
for r in rows:
 p=root/r['relative_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(r['size_bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('SOURCE SYNC V176 PASS · 4/4')
""", encoding="utf-8")

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V176.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    census.append({"source_id":source["id"],"institution":source["institucion"],"artifact":source["titulo"],"url":source["url_original"],"local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"period_coverage":source["periodo_utilizado"],"variable_families":"SISIO;Cuenta2008;UEPEX;status_history;amounts;disposition","primary_source":"YES","preserved":"YES","method_breaks":"official comparator rows; target 3672 crosswalk absent","use_status":"E0_USABLE_LONGITUDINAL_SISIO_COMPARATOR","caveat":source["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V176.csv", list({row["source_id"]:row for row in census}.values()))

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V176.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    prov.append({"source_id":source["id"],"original_url":source["url_original"],"retrieval_url":source["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_TLS_VALID","local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"provenance_note":source["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V176.csv", list({row["source_id"]:row for row in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V176.md").open("a", encoding="utf-8") as f:
    f.write("\n## V176 · exportaciones SISIO longitudinales y UEPEX\n")
    for source in sources:
        f.write(f"\n- `{source['id']}` · {source['titulo']} · {source['url_original']} · `{source['archivo_local']}` · `{source['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V176.md").open("a", encoding="utf-8") as f:
    f.write("\n## V176\n\n- Cuerpos 112/10, 93/11 y 145/12 no localizados fuera de sus referencias en Cuentas.\n- Cuatro exportaciones oficiales SISIO SSS preservadas.\n- Cuenta 2008/Informe 04/2009/Obs.5 trazada En Trámite 2013-2016 → Regularizada 30/12/2016.\n- Fila UEPEX trazada En Trámite → no regularizable por cierre de proyecto/cuenta; importes preservados.\n- Cargo firmante de 3672 probado; persona abierta.\n")

recovery = f"""# Recuperación archivística · V176

Las exportaciones SISIO oficiales muestran que una observación se identifica por clave compuesta y conserva estado, motivo, comentario, fechas, hallazgo y recomendación. Una fila Cuenta 2008 de 2009 persistió hasta regularizarse en 2016; otra fila UEPEX pasó de En Trámite a no regularizable por cierre de proyecto/cuenta. Esto vuelve insuficiente pedir sólo IDs o último estado. Para 3672 deben recuperarse todas las filas y filtros, historial no sobrescrito, vínculo documental y ledger financiero. El cargo firmante Síndico General está probado; la persona, cuerpo, fecha, expediente y remito siguen abiertos. Archivo 627/627; panel 34 y {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V176.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V176.md", "E0_FISCAL_RECONSTRUCTION_V176.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V176.md").write_text(f"# Revisión acumulada V176\n\nPanel 34 y {COVERAGE}% congelado. La forma real del historial SISIO y la distinción regularizada/no regularizable quedaron probadas; target 3672 sigue sin filas, cuerpo o atribución monetaria. Solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "README_V176.md").write_text(f"""# Checkpoint V176

- Archivo 627/627; cuatro exportaciones oficiales SISIO nuevas; hashes válidos.
- La clave SISIO real es compuesta: organismo/UAI + informe número/fecha + observación + título + sector.
- Cuenta de Inversión 2008, Informe 04/2009, Obs.5 SSS: En Trámite en 2013, 2014 y febrero 2016; Regularizada por cumplimiento el 30/12/2016.
- Fila UEPEX 2012: En Trámite en 2014; en 2016, no regularizable por cierre del proyecto y su cuenta bancaria. Cierre administrativo no equivale a corrección.
- Ejemplo cuantificado: tres discontinuidades de saldos explicadas por tipos de cambio PNUD; son conciliaciones, no daño probado.
- La Cuenta 2009 prueba que 3672/09 fue suscripta por el Síndico General; la persona sigue abierta por el relevo Pacios/Reposo.
- Los cuerpos 112/10, 93/11 y 145/12 no aparecieron públicamente fuera de las Cuentas.
- Common Crawl: sin nuevo intento; cuarenta consultas pendientes.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V176.md").write_text("# Veredicto V176\n\nAvance probatorio sobre la evidencia que debe existir. Cuatro exportaciones oficiales demuestran que SISIO conserva claves compuestas, hallazgos, recomendaciones, estados, motivos, comentarios y fechas durante años, y que regularizada y no regularizable son desenlaces distintos. Esto hace más exigible y verificable la exportación target, pero no prueba que la observación SSS o la fila UEPEX comparadora provengan de Nota 3672. Para atribución específica siguen faltando filas 3672, crosswalk 0120/09, expediente CGN y ledger antes/después. Sin promoción bancaria ni solicitud enviada.\n", encoding="utf-8")
(HERE / "AUDITORIA_V176.md").write_text(f"# Auditoría V176\n\n- 627/627 fuentes; huecos 0; nuevas 4 oficiales.\n- PDF visual: siete páginas PASS.\n- Trayectoria Cuenta 2008: 4 snapshots; UEPEX: 3 snapshots/disposición; diferencias monetarias: 3 con aritmética exacta.\n- Matrices nuevas: longitudinal 4, semántica 5, importes 3, reglas 6, export schema 6.\n- Common Crawl: 0 consultas V176; 40 pendientes.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V176_A_V177.md").write_text("""# Handover V176 → V177

## Cerrado
- Archivo 627/627; cuatro exportaciones oficiales SISIO nuevas.
- Clave compuesta e historial longitudinal real probados.
- Cuenta 2008/Informe 04/2009/Obs.5: En Trámite 2013-2016 → Regularizada 30/12/2016.
- UEPEX comparador: En Trámite → no regularizable por cierre de proyecto/cuenta.
- Diferencias UEPEX con importes y explicación por tipo de cambio preservadas.
- Cargo firmante de 3672 = Síndico General; persona abierta.

## Prioridad V177
1. Buscar exportaciones SISIO/UAI de organismos y proyectos enumerados en Cuenta 2009, usando nombres de proyecto y claves compuestas.
2. Recuperar cuerpo/fecha/persona firmante/CIDD/SPD/caja/remito/acuse de 3672.
3. Obtener expediente receptor CGN y crosswalk 0120/09→3672→fila SISIO.
4. Recuperar cuerpos/anexos/respuestas 112/10, 93/11 y 145/12.
5. Clasificar cada target como corregido, abierto o no regularizable; no sumar cierres administrativos como correcciones.
6. Construir ledger antes/después sólo con SAF/proyecto/cuadro/cuenta/moneda/documento.
7. Reintentar Common Crawl sólo tras control válido; mantener borradores DRAFT_NOT_SENT y solicitudes 0.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V175.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V176", "date":"2026-09-01", "master_catalog_entries":627, "physical_local_copies":627, "physical_local_hash_ok":627, "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_SISIO_LONGITUDINAL_SCHEMA_PROVED_TARGET_ROWS_OPEN", "analytical_promotion":"NONE_V176_SISIO_COMPARATORS_ONLY", "exact_entities":34,
    "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS, "strict_coverage_increment_v175_pp":"0",
    "requests_submitted":0, "responses_received":0, "saf355_certifications_located":0, "executed_historical_bank_rows_confirmed":0,
    "note_3672_09_body_located":False, "note_3672_recipient_file_located":False, "note_3672_signatory_role_located":True, "note_3672_signatory_role":"Síndico General de la Nación", "note_3672_personal_signatory_located":False,
    "sisio_composite_key_schema_empirically_proved":True, "sisio_longitudinal_status_history_empirically_proved":True,
    "sisio_account_2008_observation_regularization_trajectory_located":True, "sisio_uepex_nonregularizable_comparator_located":True,
    "note_3672_target_sisio_rows_located":False, "note_3672_specific_causal_attribution_proved":False, "note_3672_specific_monetary_attribution_proved":False,
    "daif_112_10_body_located":False, "daif_93_11_body_located":False, "daif_145_12_body_located":False,
    "commoncrawl_exact_prefix_queries_v176":0, "commoncrawl_valid_no_capture_v176":0, "commoncrawl_service_errors_v176":0, "commoncrawl_capture_rows_v176":0,
    "commoncrawl_pending_retry_queries":40, "commoncrawl_pending_retry_collections":20, "new_v176_sources":4,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V176.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V176","note":"official SISIO/UAI PDF export; visually verified"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V176","note":"incremental four-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V176","note":"SISIO longitudinal checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V176.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V176.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V176.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V176.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V176","note":"627-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V176 · historial SISIO comprobado" not in body:
    body += "\n\n## V176 · historial SISIO comprobado\n\nCuatro exportaciones oficiales prueban la clave compuesta y trayectoria de observaciones: una Cuenta 2008 de 2009 quedó En Trámite hasta 2016 y luego Regularizada; una fila UEPEX terminó no regularizable por cierre de proyecto/cuenta. Son comparadores, no filas 3672. Cargo firmante probado; persona y causalidad abiertas. Archivo 627/627; panel 34; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V176; 627/627 fuentes.\n- Clave compuesta e historial SISIO real probados con cuatro exportaciones oficiales.\n- Cuenta 2008: En Trámite 2013-2016 → Regularizada; UEPEX: cierre no regularizable.\n- Cargo firmante 3672 probado; persona/filas/cuerpo abiertos.\n- Common Crawl no reintentado; 40 pendientes.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "qa_v176.py").write_text("""from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==627
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V176.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==627 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V176.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V176' and co['master_catalog_entries']==627
assert co['sisio_composite_key_schema_empirically_proved'] and co['sisio_longitudinal_status_history_empirically_proved'] and co['note_3672_signatory_role_located']
assert not co['note_3672_target_sisio_rows_located'] and not co['note_3672_personal_signatory_located'] and not co['note_3672_specific_monetary_attribution_proved']
assert co['commoncrawl_exact_prefix_queries_v176']==0 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_SISIO_COMPOSITE_KEY_LONGITUDINAL_EXAMPLE_V176.csv'))==4
assert [x['status'] for x in rows('E0_SISIO_COMPOSITE_KEY_LONGITUDINAL_EXAMPLE_V176.csv')]==['En Trámite','En Trámite','En Trámite','Regularizada']
assert len(rows('E0_SISIO_UEPEX_STATUS_SEMANTICS_V176.csv'))==5
assert len(rows('E0_SISIO_OUTCOME_CLASSIFICATION_RULES_V176.csv'))==6
assert len(rows('E0_NOTE_3672_SISIO_TARGET_EXPORT_SCHEMA_V176.csv'))==6
for x in rows('E0_SISIO_UEPEX_AMOUNT_DISCONTINUITY_EXAMPLE_V176.csv'):
 assert Decimal(x['prior_final_ars'])-Decimal(x['next_initial_ars'])==Decimal(x['reported_difference_ars'])
assert len(rows('V176_PDF_VISUAL_CONTROL.csv'))==7 and all(x['result'].startswith('PASS') for x in rows('V176_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V176.csv'); assert {'SK176_40','SK176_41','SK176_42','SK176_43','SK176_44'}<={x['key_id'] for x in keys}
obj=rows('E0_V176_REQUEST_OBJECTS.csv'); assert {'RO176_40','RO176_41','RO176_42','RO176_43'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V176_REQUEST_OBJECTS_V176.csv')
for n in ('REQUEST_AGN_2018_REPLY_V176.md','REQUEST_BCRA_CRYL_SETTLEMENT_V176.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V176.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V176.md','REQUEST_CNV_CUSTODY_RECORDS_V176.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V176.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V176.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V176_SOURCE_BUNDLE.csv'))==4
m=json.loads((H/'MANIFEST_V176.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V176' and m['parent_checkpoint']=='V175' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V176 QA PASS · 627/627 · new=4 · SISIO-HISTORY=PROVED · TARGET-ROWS=OPEN · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x:x.name.casefold()) if p.is_file() and p.name != "MANIFEST_V176.json"]
manifest = {
    "checkpoint":"V176", "parent_checkpoint":"V175", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities":34, "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS,
    "new_promotions":[], "source_archive":"627/627; four official SISIO/UAI exports added",
    "historical_finding":"composite SISIO key and longitudinal outcomes proved; target rows and causal attribution open",
    "note_3672_signatory_role":"Síndico General de la Nación", "note_3672_personal_signatory":"NOT_PROVED", "note_3672_target_sisio_rows":"NOT_LOCATED",
    "commoncrawl_queries_v176":0, "commoncrawl_pending":40, "closed_network_gate":"NO", "saf355_certifications":"0/5",
    "executed_historical_bank_rows":"0/10", "requests_submitted":0, "files":manifest_files,
}
(HERE / "MANIFEST_V176.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V176","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"627 master; 627 physical SHA-valid","historical_workstream":"SISIO history proved; target rows/person/causality open; CC pending 40; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V176tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V176 BUILD PASS · catalog=627/627 · new=4 · SISIO-history=PROVED · target-rows=OPEN · panel=34 · requests=0")
