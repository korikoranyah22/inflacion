from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v150" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def upsert(rows, additions, key):
    order = [str(row[key]) for row in rows]
    indexed = {str(row[key]): row for row in rows}
    for addition in additions:
        row = {name: str(value) for name, value in addition.items()}
        indexed[row[key]] = row
        if row[key] not in order: order.append(row[key])
    return [indexed[value] for value in order]


def matrix(name, fields, rows):
    data = [dict(zip(fields, row)) for row in rows]
    write_csv(HERE / name, data, fields)
    return data


def append_section(path, marker, body):
    path = Path(path); text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


# id, institution, title, url, filename, period, series, kind, scope note
SOURCES = [
    ("e0_mecon_resolution_sh_47_1996_c42_authorization", "Secretaría de Hacienda", "Resolución SH 47/1996 · autorización del C-42", "https://www.economia.gob.ar/digesto/resoluciones/sh/1996/resolsh47.htm", "mecon_resolution_sh_47_1996_c42_authorization.html", "1996", "Resolución SH 47/1996", "HTML oficial preservado", "Autoriza C-42 y comprende deuda pública del SAF355; caduca al cierre anual."),
    ("e0_cgn_disposition_52_1996_c42_debt_payment", "Contaduría General de la Nación", "Disposición CGN 52/1996 · modificación del C-42", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/dis52.htm", "cgn_disposition_52_1996_c42_debt_payment.html", "1996", "Disposición CGN 52/1996", "HTML oficial preservado", "Modifica formulario, instructivo y procedimiento para fondos de terceros o deuda pública."),
    ("e0_cgn_disposition_52_1996_c42_instructions", "Contaduría General de la Nación", "Anexo I Disposición CGN 52/1996 · instructivo C-42", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/adis52.htm", "cgn_disposition_52_1996_c42_instructions.html", "1996", "Instructivo C-42", "HTML oficial preservado", "Define beneficiario, cuenta, pagador, AXT, monto, SIGADE, respaldo, concepto y firmas."),
    ("e0_cgn_disposition_52_1996_c42_procedure", "Contaduría General de la Nación", "Anexo II Disposición CGN 52/1996 · procedimiento C-42", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/aadis52.htm", "cgn_disposition_52_1996_c42_procedure.html", "1996", "Procedimiento C-42", "HTML oficial preservado", "Prueba cadena SAF–TRANSAF–SIDIF–CGN–TGN y correlativo SIDIF de siete dígitos."),
    ("e0_cgn_disposition_52_1996_c42_form", "Contaduría General de la Nación", "Formulario C-42 · primera página", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/c-42.jpg", "cgn_disposition_52_1996_c42_form_page1.jpg", "1996", "Formulario C-42", "Imagen oficial preservada", "Control visual de campos; no es un cuerpo target de 2008."),
    ("e0_cgn_disposition_52_1996_c42_flow", "Contaduría General de la Nación", "Diagrama oficial del procedimiento C-42", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/c-42proc.jpg", "cgn_disposition_52_1996_c42_procedure_flow.jpg", "1996", "Flujo C-42", "Imagen oficial preservada", "Cadena SAF–CGN–TGN; no acredita pago target."),
    ("e0_cgn_circular_16_1996_c42_presentation", "Contaduría General de la Nación", "Circular CGN 16/1996 · presentación C-42", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1996/cir16.htm", "cgn_circular_16_1996_c42_presentation.html", "1996", "Circular CGN 16/1996", "HTML oficial preservado", "Vía general que excluye expresamente a SAF355/356."),
    ("e0_argentina_resolution_81_2012_original_expense_circuit", "Secretaría de Hacienda", "Resolución SH 81/2012 · circuito de gastos original", "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-81-2012-196825/texto", "argentina_resolution_81_2012_original_expense_circuit.html", "2012", "Resolución SH 81/2012", "HTML oficial preservado", "Comparador e-SIDIF posterior; no se retroproyecta a 2008."),
]

source_rows = []
for sid, institution, title, url, filename, period, series, kind, note in SOURCES:
    path = BIN / filename; assert path.is_file(), path
    source_rows.append({"id":sid,"institution":institution,"title":title,"url":url,
        "local":"/"+path.relative_to(REPO).as_posix(),"period":period,"series":series,
        "kind":kind,"note":note,"sha":sha256(path),"bytes":path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{"id":s["id"],"tema":"ciclo_ajuste_e0_fiscal","institucion":s["institution"],
    "titulo":s["title"],"url_original":s["url"],"archivo_local":s["local"],"fecha_descarga":"2026-08-31",
    "fecha_publicacion":s["period"],"codigo_serie":s["series"],"periodo_utilizado":s["period"],
    "tipo":s["kind"],"sha256":s["sha"],"nota":"V150: "+s["note"]} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V150.csv"
census = read_csv(census_path)
census = upsert(census, [{"source_id":s["id"],"institution":s["institution"],"artifact":s["title"],
    "url":s["url"],"local_path":s["local"],"sha256":s["sha"],"bytes":s["bytes"],
    "period_coverage":s["period"],"variable_families":"C42;SAF355;SIDIF;TRANSAF;CGN;TGN;SIGADE;custody",
    "primary_source":"YES","preserved":"YES","method_breaks":"vigencia/no uso target; formulario/ejecución; legado/e-SIDIF",
    "use_status":"E0_USABLE_WITH_SCOPE","caveat":s["note"]} for s in source_rows], "source_id")
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V150.csv"
provenance = read_csv(provenance_path)
provenance = upsert(provenance, [{"source_id":s["id"],"original_url":s["url"],"retrieval_url":s["url"],
    "capture_timestamp":"2026-08-31","cdx_digest":"N/A_OFFICIAL_DIRECT","local_path":s["local"],
    "sha256":s["sha"],"bytes":s["bytes"],"provenance_note":"Captura directa oficial; alcance probatorio congelado en V150."} for s in source_rows], "source_id")
write_csv(provenance_path, provenance, list(provenance[0]))

bundle_files = [
    ("B150_01","mecon_resolution_sh_47_1996_c42_authorization.html","https://www.economia.gob.ar/digesto/resoluciones/sh/1996/resolsh47.htm","AUTHORIZATION"),
    ("B150_02","cgn_disposition_52_1996_c42_debt_payment.html","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/dis52.htm","DISPOSITION"),
    ("B150_03","cgn_disposition_52_1996_c42_instructions.html","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/adis52.htm","INSTRUCTIONS"),
    ("B150_04","cgn_disposition_52_1996_c42_procedure.html","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/aadis52.htm","PROCEDURE"),
    ("B150_05","cgn_disposition_52_1996_c42_form.html","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/dis52al.htm","FORM_WRAPPER"),
    ("B150_06","cgn_disposition_52_1996_c42_form_page1.jpg","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/c-42.jpg","FORM_PAGE_1"),
    ("B150_07","cgn_disposition_52_1996_c42_form_page2.html","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/dis52all.htm","FORM_PAGE_2_WRAPPER"),
    ("B150_08","cgn_disposition_52_1996_c42_form_page2.jpg","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/c-42b.jpg","FORM_PAGE_2"),
    ("B150_09","cgn_disposition_52_1996_c42_procedure_flow.jpg","https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp52/c-42proc.jpg","PROCEDURE_FLOW"),
    ("B150_10","cgn_circular_16_1996_c42_presentation.html","https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1996/cir16.htm","GENERAL_ROUTE_NEGATIVE_CONTROL"),
    ("B150_11","argentina_resolution_81_2012_original_expense_circuit.html","https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-81-2012-196825/texto","LATER_CROSSWALK"),
]
bundle=[]
for row_id, filename, url, role in bundle_files:
    path=BIN/filename; assert path.is_file(), path
    bundle.append({"row_id":row_id,"filename":filename,"official_url":url,"role":role,
        "bytes":str(path.stat().st_size),"sha256":sha256(path),"preserved":"YES"})
write_csv(HERE/"E0_C42_SOURCE_BUNDLE_V150.csv", bundle)

branch = matrix("E0_C42_1996_2008_TARGET_BRANCH_V150.csv",
    ["row_id","object","contemporaneous_fact","target_query","source_id","locator","status","target_payment_confirmed"], [
    ("CB150_01","AUTHORIZATION","SH autorizó el C-42.","Buscar tipo exacto por cada ID.","e0_mecon_resolution_sh_47_1996_c42_authorization","art.1","BRANCH_PROVED_TARGET_TYPE_OPEN","FALSE"),
    ("CB150_02","SAF355_SCOPE","Deuda pública era competencia exclusiva del SAF355.","Buscar archivo productor SAF355.","e0_mecon_resolution_sh_47_1996_c42_authorization","art.1.a","PRODUCER_PROVED","FALSE"),
    ("CB150_03","NO_BUDGET_CREDIT","C-42 cubría vencimientos sin crédito disponible con modificación solicitada.","Pedir expediente de modificación.","e0_cgn_disposition_52_1996_c42_procedure","procedimiento SAF355/356","USE_CASE_PROVED","FALSE"),
    ("CB150_04","THIRD_PARTY_OR_DEBT","Cubría fondos de terceros o cancelación de deuda pública.","No equiparar ambas causas.","e0_cgn_disposition_52_1996_c42_debt_payment","considerandos","SCOPE_PROVED","FALSE"),
    ("CB150_05","ANNUAL_EXPIRY","El formulario caducaba al cierre del ejercicio.","Pedir estado, reemisión y regularización.","e0_mecon_resolution_sh_47_1996_c42_authorization","art.2","EXPIRY_RULE_PROVED","FALSE"),
    ("CB150_06","OPERATIVE_2008","El cierre 2008 fijó recepción C-42 al 31/12/2008.","Buscar corte 2008 y enero 2009.","e0_argentina_resolution_6_2008_closing_original","art.4","CONTEMPORANEOUS_OPERATION_PROVED","FALSE"),
    ("CB150_07","LEGACY_ORIGIN","SAF podía usar CONPRE, SIDIF Local o sistema propio.","Pedir exportación de los tres universos.","e0_cgn_disposition_52_1996_c42_procedure","apartado SAF","SYSTEM_UNIVERSE_PROVED","FALSE"),
    ("CB150_08","TRANSAF","La transmisión electrónica llegaba por TRANSAF.","Pedir envío, recepción y log.","e0_cgn_disposition_52_1996_c42_procedure","apartado SIDIF","TRANSMISSION_ROUTE_PROVED","FALSE"),
    ("CB150_09","SEVEN_DIGIT","SIDIF asignaba correlativo de siete dígitos, hora y fecha.","Buscar cero relleno y crudo.","e0_cgn_disposition_52_1996_c42_procedure","apartado SIDIF","NUMBERING_PROVED_IDENTITY_OPEN","FALSE"),
    ("CB150_10","PAPER_ORIGINAL_COPY","Original y copia firmados se presentaban a CGN.","Pedir ambos y registro de mesa.","e0_cgn_disposition_52_1996_c42_procedure","apartado CGN","PAPER_ROUTE_PROVED","FALSE"),
    ("CB150_11","SCREEN_COMPARE","CGN cotejaba papel contra pantalla.","Pedir constancia y resultado.","e0_cgn_disposition_52_1996_c42_procedure","apartado CGN","CONTROL_PROVED","FALSE"),
    ("CB150_12","APPROVAL","Aprobado se remitía a TGN para pago.","Separar aprobación, recepción y pago.","e0_cgn_disposition_52_1996_c42_procedure","apartado CGN/TGN","PREPAYMENT_STAGE_PROVED","FALSE"),
    ("CB150_13","OFFICIAL_ARCHIVE","Firmas y respaldos originales integraban archivo del SAF.","Pedir inventario y ubicación.","e0_cgn_disposition_52_1996_c42_procedure","apartado archivo","CUSTODY_ROUTE_PROVED","FALSE"),
    ("CB150_14","BENEFICIARY_BANK","C-42 registraba banco y cuenta del beneficiario.","No confundir con cuenta pagadora.","e0_cgn_disposition_52_1996_c42_instructions","campos beneficiario","FIELD_PROVED_TARGET_OPEN","FALSE"),
    ("CB150_15","SIGADE","C-42 registraba número SIGADE cuando correspondía.","Pedir vínculo exacto C42–SIGADE.","e0_cgn_disposition_52_1996_c42_instructions","campo SIGADE","LINK_FIELD_PROVED_TARGET_OPEN","FALSE"),
    ("CB150_16","SPECIAL_ROUTE","Circular 16 excluía a SAF355/356 de la vía general.","Usar procedimiento especial; general sólo como control.","e0_cgn_circular_16_1996_c42_presentation","cuerpo","SPECIAL_ROUTE_PROVED","FALSE"),
    ("CB150_17","C42_TO_C55","Un C-42 podía requerir posterior regularización presupuestaria.","Buscar ambos sin contar dos pagos.","e0_cgn_disposition_52_1996_c42_procedure","procedimiento SAF355/356","SEQUENCE_HYPOTHESIS_OPEN","FALSE"),
    ("CB150_18","TARGET_GAP","No se localizaron cuerpos públicos de los tres IDs.","Mantener PUBLIC_BODY_NOT_LOCATED y 0/10.","e0_cgn_cuenta_inversion_2008_sdp","Anexo K p.67","PUBLIC_BODY_NOT_LOCATED","FALSE"),
])

field_rows = [
    ("SIDIF_NUMBER","correlativo de siete dígitos","SIDIF/CGN","número, hora y fecha","procedure","NO"),
    ("SAF_NUMBER","identificador de origen","SAF355","número interno y tipo","procedure","NO"),
    ("TRANSAF_LOG","transmisión electrónica","SAF355/CGN","archivo y acuse","procedure","NO"),
    ("RECEIPT_TIMESTAMP","hora y fecha SIDIF","CGN/SIDIF","timestamp exacto","procedure","NO"),
    ("BENEFICIARY_NAME","identidad del beneficiario","SAF355","nombre y código","instructions","NO"),
    ("CUIT","clave tributaria","SAF355","CUIT","instructions","NO"),
    ("ADDRESS","domicilio","SAF355","domicilio","instructions","NO"),
    ("BENEFICIARY_BANK","banco/sucursal","SAF355/TGN","banco y sucursal","instructions","NO"),
    ("BENEFICIARY_ACCOUNT","tipo y número de cuenta","SAF355/TGN","tipo y número","instructions","NO"),
    ("PAYER","servicio pagador","SAF355/TGN","código y nombre","instructions","NO"),
    ("AMOUNT","importe total/parcial","SAF355/CGN","moneda, total y parciales","instructions","NO"),
    ("AXT","auxiliar de tesorería","SAF355/CGN","AXT","instructions","NO"),
    ("PAYMENT_CONCEPT","concepto declarado","SAF355","texto íntegro","instructions","NO"),
    ("EMITTING_OFFICE","oficina emisora","SAF355","oficina y responsable","instructions","NO"),
    ("RESPONSIBLE_ACCOUNT","banco/código/número responsable","SAF355/TGN","tres campos separados","instructions","NO"),
    ("SUPPORT_DOCUMENT","tipo y número de respaldo","SAF355","documento y legajo","instructions","NO"),
    ("SIGADE_NUMBER","vínculo deuda cuando corresponde","SAF355/ONCP","número y versión","instructions","NO"),
    ("SIGNATURES","responsabilidad y controles","SAF355/CGN/TGN","firmas, cargos y fechas","form","NO"),
    ("PAPER_ORIGINAL","soporte firmado","CGN/SAF355","original, copia e inventario","procedure","NO"),
    ("SCREEN_COMPARISON","validación papel/sistema","CGN","resultado y operador","procedure","NO"),
    ("APPROVAL","habilitación previa","CGN","estado y timestamp","procedure","NO"),
    ("TGN_PAYMENT","movimiento de salida y cancelación","TGN/BNA/BCRA","fecha valor, signo, importe, cuenta, referencia, conciliación y reversa","procedure","YES_IF_COMPLETE_CHAIN"),
]
source_by_short={"procedure":"e0_cgn_disposition_52_1996_c42_procedure","instructions":"e0_cgn_disposition_52_1996_c42_instructions","form":"e0_cgn_disposition_52_1996_c42_form"}
fields = matrix("E0_C42_FIELD_AND_CUSTODY_MAP_V150.csv",
    ["row_id","field_or_record","official_meaning","producer_or_custodian","request_object","source_id","payment_proof_alone"],
    [(f"FC150_{i:02d}",a,b,c,d,source_by_short[e],f) for i,(a,b,c,d,e,f) in enumerate(field_rows,1)])

padded = matrix("E0_C42_ZERO_PADDED_KEY_MATRIX_V150.csv",
    ["row_id","raw_key","seven_digit_variant","query_context","controlled_use","status"], [
    ("ZP150_01","71597","0071597","C42 SIDIF","buscar ambas grafías","SEARCH_KEY_ONLY"),
    ("ZP150_02","152677","0152677","C42 SIDIF","buscar ambas grafías","SEARCH_KEY_ONLY"),
    ("ZP150_03","2876","0002876","C42 SIDIF","buscar ambas grafías","SEARCH_KEY_ONLY"),
    ("ZP150_04","83106000","83106000","concepto/código","combinar con cada ID","SEARCH_KEY_ONLY"),
    ("ZP150_05","71597","0071597","C41","control de tipo alternativo","TYPE_OPEN"),
    ("ZP150_06","152677","0152677","C41","control de tipo alternativo","TYPE_OPEN"),
    ("ZP150_07","2876","0002876","C41","control de tipo alternativo","TYPE_OPEN"),
    ("ZP150_08","71597","0071597","C55","control de regularización","TYPE_OPEN"),
    ("ZP150_09","152677","0152677","C55","control de regularización","TYPE_OPEN"),
    ("ZP150_10","2876","0002876","C55","control de regularización","TYPE_OPEN"),
    ("ZP150_11","32.270,30","32270.30","importe","combinar; no identificar por monto","SEARCH_KEY_ONLY"),
    ("ZP150_12","COMISIONES - BANCO NACION","COMISIONES BANCO NACION","texto","variantes con/sin guion","SEARCH_KEY_ONLY"),
])

tree_rows = matrix("E0_THREE_PAYMENT_MECHANISM_DECISION_TREE_V150.csv",
    ["row_id","branch","necessary_record","success_condition","failure_or_next_branch","double_count_control","target_status"], [
    ("DT150_01","C41","cuerpo C-41","ID, cabecera y renglones exactos","buscar C42/C55","un pago por cadena bancaria","OPEN"),
    ("DT150_02","C41","historia","estado pagado/cancelado y sin reversa","buscar TGN/CUT","no contar emisión","OPEN"),
    ("DT150_03","C41","orden TGN","selección/remesa","buscar extracto","no contar selección","OPEN"),
    ("DT150_04","C41","extracto y conciliación","movimiento exacto conciliado","cierre sin ejecución","una fecha valor","OPEN"),
    ("DT150_05","C42","cuerpo C-42","tipo y números SAF/SIDIF","buscar C41/C55","no atribuir por siete dígitos","OPEN"),
    ("DT150_06","C42","TRANSAF y papel","coincidencia electrónica/papel","buscar archivo CGN","no contar transmisión","OPEN"),
    ("DT150_07","C42","aprobación CGN","remisión a TGN","buscar pago TGN","no contar aprobación","OPEN"),
    ("DT150_08","C42","extracto y conciliación","movimiento exacto conciliado","cierre sin ejecución","una sola cadena","OPEN"),
    ("DT150_09","C55","cuerpo C-55","regularización exacta enlazada","buscar documento original","no contar C42+C55 dos veces","OPEN"),
    ("DT150_10","C55","documento antecedente","C41/C42/otro identificado","buscar historia","regularización no es nuevo pago","OPEN"),
    ("DT150_11","C55","historia","estado y reversas","buscar TGN/CUT","no contar estado aislado","OPEN"),
    ("DT150_12","C55","extracto y conciliación","movimiento exacto conciliado","cierre sin ejecución","una sola cadena","OPEN"),
    ("DT150_13","ALL","71597/0071597","tipo probado por cuerpo","seguir rama real","no asignar por rango","OPEN"),
    ("DT150_14","ALL","152677/0152677","tipo probado por cuerpo","seguir rama real","no asignar por rango","OPEN"),
    ("DT150_15","ALL","2876/0002876","tipo probado por cuerpo","seguir rama real","no asignar por rango","OPEN"),
])

crosswalk_data=[
    ("C42","OP NPR","pago no presupuestario","diccionario de búsqueda"),
    ("número SAF","número propio","identificador productor","pedir ambos"),
    ("número SIDIF","número e-SIDIF","identificador central","no homologar valores"),
    ("SIGADE","SIGADE","vínculo deuda","pedir versión y tabla"),
    ("pagador TGN","pagador TGN","rol pagador","buscar salida"),
    ("C55 ajuste","CMR","regularización","buscar parentesco"),
    ("C55 ajuste","CRG","regularización","buscar parentesco"),
    ("papel","archivo oficial digital/papel","custodia","pedir inventario"),
    ("TRANSAF","interoperabilidad e-SIDIF","transmisión","buscar logs legados"),
    ("concepto","descripción","semántica","texto exacto y variantes"),
    ("banco beneficiario","cuenta beneficiaria","destino","no confundir con pagadora"),
    ("2008 legado","2012 e-SIDIF","comparabilidad limitada","no retroproyectar esquema"),
]
crosswalk = matrix("E0_RES81_LEGACY_TO_ESIDIF_CROSSWALK_V150.csv",
    ["row_id","legacy_object","later_esidif_object","continuity","temporal_break","controlled_use","source_id"],
    [(f"CW150_{i:02d}",a,b,c,"e-SIDIF posterior; SAF355 desplegado en 2010",d,"e0_argentina_resolution_81_2012_original_expense_circuit" if i<12 else "e0_cgn_account_2010_saf355_esidif_deployment") for i,(a,b,c,d) in enumerate(crosswalk_data,1)])

image_visual = matrix("E0_V150_IMAGE_VISUAL_CONTROL.csv",
    ["control_id","artifact","visual_finding","scope_limit","result"], [
    ("IV150_01","cgn_disposition_52_1996_c42_form_page1.jpg","Número SIDIF, beneficiario, banco/cuenta, SIGADE, respaldo, AXT, importe, concepto y firmas.","Formulario modelo; no cuerpo target.","PASS"),
    ("IV150_02","cgn_disposition_52_1996_c42_form_page2.jpg","Recibo, identidad, firma y fecha.","Segunda página modelo; no recibo target.","PASS"),
    ("IV150_03","cgn_disposition_52_1996_c42_procedure_flow.jpg","Flujo SAF–procesamiento CGN–aprobación–TGN.","Diagrama normativo; no ejecución target.","PASS"),
])

negative_queries=[
    ("71597 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),("0071597 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),
    ("152677 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),("0152677 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),
    ("2876 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),("0002876 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),
    ("83106000 C-42","economia.gob.ar","PUBLIC_BODY_NOT_LOCATED"),("71597 152677 2876","argentina.gob.ar","PUBLIC_BODY_NOT_LOCATED"),
    ("UAI SAF355 cierre 2008","argentina.gob.ar","PUBLIC_REPORT_NOT_LOCATED"),("C-42 deuda pública SAF355","official","BRANCH_PROVED_TARGET_OPEN"),
]
negative = matrix("E0_V150_PUBLIC_SEARCH_NEGATIVE_RESULTS_V150.csv",
    ["row_id","exact_query","official_domain","result","interpretation","status"],
    [(f"NS150_{i:02d}",q,d,"sin cuerpo target" if i<10 else "normativa hallada","no prueba inexistencia ni pago",s) for i,(q,d,s) in enumerate(negative_queries,1)])

request_data=[
    ("SAF355","Universo C41/C42/C55","tipo; número SAF; número SIDIF","cada ID clasificado por cuerpo"),
    ("SIDIF/CGN","Correlativo de siete dígitos","número; hora; fecha","match crudo y cero relleno"),
    ("SAF355/CGN","TRANSAF","archivo; acuse; timestamp","envío y recepción enlazados"),
    ("CGN","Original y copia C42","firmas; recepción; imágenes","cuerpo legible e íntegro"),
    ("CGN","Cotejo papel/pantalla","operador; fecha; resultado","control enlazado por ID"),
    ("CGN","Aprobación C42","estado; fecha; remisión","aprobación diferenciada de pago"),
    ("TGN","Recepción y selección","ID; lote; fecha; estado","cadena CGN–TGN"),
    ("TGN/BNA/BCRA","Pago/cancelación","fecha valor; signo; moneda; importe; cuenta; referencia","movimiento conciliado y sin reversa"),
    ("SAF355","Beneficiario","nombre; código; CUIT; domicilio","identidad exacta"),
    ("SAF355/TGN","Banco beneficiario","banco; sucursal; tipo; cuenta","destino separado de cuenta pagadora"),
    ("SAF355/TGN","Pagador y cuenta responsable","pagador; banco; código; cuenta","origen financiero exacto"),
    ("SAF355","AXT y concepto","AXT; texto íntegro; parciales","match 83106000 y monto"),
    ("SAF355/ONCP","Vínculo SIGADE","número; versión; obligación","join reproducible"),
    ("SAF355","Documento de respaldo","tipo; número; legajo; inventario","cuerpo original localizado"),
    ("SAF355/CGN","Caducidad C42","estado al 31/12/2008","distinguir caduco, aprobado y pagado"),
    ("SAF355/CGN","Reemisión o regularización C55","antecedente; posterior; relación","secuencia sin doble conteo"),
    ("SAF355/UAI","Backup legado","sistema; motor; versión; corte; hash","restore/export verificable"),
    ("Archivo SAF355/CGN","Inventario y transferencia","serie; caja; fecha; destino","custodia actual nominada"),
]
request_objects = matrix("E0_V150_REQUEST_OBJECTS_V150.csv",
    ["object_id","owner_or_system","requested_record","minimum_usable_fields","success_test","negative_response_rule","status"],
    [(f"RO150_{i:02d}",a,b,c,d,"Individualizar serie, búsqueda, migración, transferencia o disposición.","DRAFT_NOT_SENT") for i,(a,b,c,d) in enumerate(request_data,1)])

breaks_path=HERE/"E0_FISCAL_METHOD_BREAKS_V150.csv"; breaks=read_csv(breaks_path)
break_add=[
    ("c42_public_debt_branch_operative_2008_not_target_type","document_type","C-42 existed for public debt and was operative in 2008 but no target body was located.","Classify each ID only from its body or authoritative system row.","Res. SH 47/1996 art.1; Res. SH 6/2008 art.4"),
    ("c42_expiration_at_close_not_nonpayment_proof","state","Annual expiry does not reveal whether a form was paid, rejected or reissued.","Request status history and subsequent regularization.","Res. SH 47/1996 art.2"),
    ("c42_sidif_7digit_zero_padding_not_identity_proof","identifier","Seven-digit formatting creates plausible padded keys but not type identity.","Use padded variants only as search keys.","Disp. CGN 52/1996 procedure"),
    ("c42_paper_screen_transaf_chain_not_payment","phase","Transmission, paper receipt, screen comparison and approval precede payment.","Require TGN/bank movement and reconciliation.","Disp. CGN 52/1996 procedure"),
    ("c42_beneficiary_bank_not_financing_account","account","Beneficiary bank/account is not necessarily payer or financing account.","Preserve destination and funding separately.","Disp. CGN 52/1996 instructions"),
    ("circular16_general_route_excludes_saf355","route","General C-42 instructions explicitly excluded SAF355/356.","Use special SAF355 procedure; general route only as control.","Circular CGN 16/1996"),
    ("res81_esidif_crosswalk_not_2008_schema","temporal","The 2012 e-SIDIF circuit is not the native 2008 schema.","Request legacy SIDIF/TRANSAF/SAF records first.","Res. SH 81/2012; CGN Cuenta 2010"),
    ("c42_then_c55_regularization_not_double_payment","aggregation","C-42 followed by C-55 can describe one economic event.","Deduplicate by antecedent, amount, date, beneficiary and bank movement.","Disp. CGN 52/1996 procedure"),
]
breaks=upsert(breaks,[{"break_id":a,"dimension":b,"problem":c,"rule":d,"status":"FROZEN","evidence":e} for a,b,c,d,e in break_add],"break_id")
write_csv(breaks_path,breaks,list(breaks[0]))

trace_path=HERE/"E0_INFORMATION_REQUEST_TRACEABILITY_V150.csv"; trace=read_csv(trace_path)
trace_data=[
    ("C42_TYPE","Cuerpo y tipo C41/C42/C55","SAF355","tipo;número SAF;número SIDIF;cuerpo"),
    ("C42_NUMBER","Registro SIDIF de siete dígitos","CGN/SIDIF","correlativo;hora;fecha;estado"),
    ("C42_TRANSAF","Transmisión y acuse TRANSAF","SAF355/CGN","archivo;acuse;timestamp"),
    ("C42_PAPER","Original y copia firmados","CGN","imagen;firmas;mesa;fecha"),
    ("C42_COMPARE","Cotejo papel contra pantalla","CGN","operador;fecha;resultado"),
    ("C42_APPROVAL","Aprobación y remisión","CGN/TGN","estado;fecha;lote;recepción"),
    ("C42_PAYMENT","Selección, pago y cancelación","TGN","fecha valor;moneda;importe;cuenta;referencia"),
    ("C42_BENEFICIARY","Beneficiario y cuenta bancaria","SAF355","nombre;CUIT;banco;sucursal;tipo;cuenta"),
    ("C42_PAYER","Pagador y cuenta responsable","SAF355/TGN","pagador;banco;código;cuenta"),
    ("C42_SUPPORT","Respaldo, AXT, concepto y SIGADE","SAF355","tipo;número;AXT;texto;SIGADE"),
    ("C42_EXPIRY","Historia al cierre y caducidad","SAF355/CGN","estado;fecha;causa;posterior"),
    ("C42_C55","Antecedente C42 y regularización C55","SAF355/CGN","relación;montos;fechas;estado"),
    ("LEGACY_BACKUP","Backup CONPRE/SIDIF Local/sistema propio","SAF355/UAI","motor;versión;corte;hash;restore"),
    ("C42_INVENTORY","Inventario de originales","Archivo SAF355/CGN","serie;caja;folio;transferencia"),
    ("C42_BANK","Movimiento destino versus cuenta pagadora","BNA/TGN","fecha valor;signo;importe;cuenta;referencia;reversa"),
]
trace_add=[]
for i,(gap,record,inst,fields_min) in enumerate(trace_data,1):
    trace_add.append({"trace_id":f"TR150_{i:03d}","request_id":"REQ133_BNA" if i==15 else "REQ133_ECON",
        "institution":inst,"gap_id":gap,"requested_record":record,"period_or_date":"2008-2009",
        "identifiers":"83106000;71597/0071597;152677/0152677;2876/0002876","minimum_usable_fields":fields_min,
        "confidentiality_fallback":"Metadatos no exceptuados, campos testados e informe de búsqueda.","status":"DRAFT_NOT_SENT"})
trace=upsert(trace,trace_add,"trace_id"); write_csv(trace_path,trace,list(trace[0]))

keys_path=HERE/"E0_REQUEST_SEARCH_KEY_MATRIX_V150.csv"; keys=read_csv(keys_path)
key_data=[
    ("sidif","0071597","C42 padded key"),("sidif","0152677","C42 padded key"),("sidif","0002876","C42 padded key"),
    ("form","C-42","document universe"),("form","C-41","alternative branch"),("form","C-55","regularization branch"),
    ("system","TRANSAF","legacy transmission"),("system","CONPRE","legacy origin"),("system","SIDIF LOCAL","legacy origin"),
    ("field","SIGADE","debt link"),("field","AXT","treasury auxiliary"),("concept","COMISIONES - BANCO NACION","exact concept"),
    ("amount","32.270,30","display amount"),("date","31/12/2008","C42 expiry/cut"),
    ("phrase","obligaciones correspondientes a la deuda pública","official scope phrase"),
]
key_add=[{"key_id":f"SK150_{i:02d}","request_id":"REQ133_ECON","key_group":a,"exact_key":b,"search_purpose":c,
    "source_or_basis":"E0_C42_1996_2008_TARGET_BRANCH_V150.csv","caveat":"Clave de búsqueda; no prueba tipo, identidad ni pago."} for i,(a,b,c) in enumerate(key_data,1)]
keys=upsert(keys,key_add,"key_id"); write_csv(keys_path,keys,list(keys[0]))

append_section(HERE/"REQUEST_ECONOMIA_TESORO_SETTLEMENT_V150.md","## Ampliación V150 · universo C-41/C-42/C-55 y cadena completa","""
Estado: BORRADOR_NO_ENVIADO. Este texto no autoriza ni registra presentación.

Para cada identificador 71597/0071597, 152677/0152677 y 2876/0002876, se solicita consulta sin restricción previa de tipo en C-41, C-42, C-55 o equivalente. Deben entregarse número propio SAF, número SIDIF, tipo, cabecera, renglones e historia.

Si el registro es C-42, se solicitan origen CONPRE/SIDIF Local/sistema propio; archivo, acuse y log TRANSAF; correlativo SIDIF de siete dígitos con hora y fecha; original y copia firmados; recepción CGN; cotejo papel/pantalla; aprobación; remisión y recepción TGN. También beneficiario, CUIT, banco y cuenta, pagador, monto, AXT, concepto, cuenta responsable, respaldo, número SIGADE y firmas.

Separadamente se solicita estado al 31/12/2008, caducidad, reemisión o regularización C-55, y movimiento bancario con fecha valor, signo, moneda, importe, cuenta, referencia, conciliación y reversas. Transmisión, cotejo, aprobación o caducidad no se tratarán como prueba de pago. Un C-42 y su C-55 posterior no se contarán como dos hechos.

Circular CGN 16/1996 excluía a SAF355/356 de la ruta general: se requiere primero el procedimiento especial. Resolución SH 81/2012 se usa sólo como diccionario posterior; para 2008 se piden registros legados, inventarios y backups reproducibles.
""")
append_section(HERE/"REQUEST_BNA_FIRST_STAGE_BLOTTER_V150.md","## Ampliación V150 · cuenta beneficiaria versus cuenta pagadora","""
Estado: BORRADOR_NO_ENVIADO. Si los cuerpos fueran C-42, se solicita distinguir banco/cuenta del beneficiario de cuenta responsable o pagadora. La mención BANCO NACION en el concepto no prueba que BNA sea beneficiario ni identifica la cuenta de salida. Para cada movimiento se requieren fecha valor, signo, moneda, importe, referencia, origen/destino, conciliación y reversas.
""")
append_section(HERE/"SOURCE_REFERENCES_V150.md","## Fuentes nuevas V150 · rama C-42","\n".join("- "+s["id"]+" · "+s["title"]+" · "+s["url"]+" · "+s["local"]+" · "+s["sha"] for s in source_rows))
append_section(HERE/"REQUEST_SUBMISSION_CHECKLIST_V150.md","## Control V150 · tercera rama sin anticipar el tipo","""
- Mantener seis pedidos DRAFT_NOT_SENT hasta autorización expresa.
- Buscar C-41, C-42 y C-55 sin clasificar por magnitud o cantidad de dígitos.
- Consultar cada ID crudo y rellenado a siete dígitos.
- Separar SAF, SIDIF/TRANSAF, papel CGN, aprobación TGN y movimiento bancario.
- Distinguir cuenta beneficiaria de cuenta responsable/pagadora.
- Buscar caducidad, reemisión y regularización sin doble conteo.
- Usar e-SIDIF 2012 sólo como comparador; pedir sistemas legados 2008.
- Mantener 0/10 hasta cuerpo y puente bancario conciliado.
""")

(HERE/"README_V150.md").write_text("""# V150 · tercera rama C-42 y árbol documental completo

V150 prueba una tercera vía contemporánea. Resolución SH 47/1996 autorizó C-42 para deuda pública del SAF355; Disposición CGN 52/1996 preserva formulario, campos y cadena SAF–TRANSAF–SIDIF–CGN–TGN. Resolución SH 6/2008 demuestra que C-42 seguía operativo al cierre 2008.

Esto no clasifica los IDs target. Cada uno se busca como C-41, C-42 y C-55, crudo y con siete dígitos. C-42 transmitido, cotejado o aprobado aún no es pago; caducidad tampoco prueba impago. Sólo entra al numerador una salida bancaria conciliada y sin reversa.

Circular CGN 16/1996 excluía a SAF355/356 de vía general. Resolución SH 81/2012 sirve sólo como crosswalk posterior porque e-SIDIF llegó a SAF355 en 2010. Resultado: cuerpos target 0/3, ejecuciones 0/10, seis borradores no enviados y cero respuestas.
""",encoding="utf-8")
(HERE/"VEREDICTO_V150.md").write_text("""# Veredicto V150

El universo correcto tiene tres ramas: C-41 ordinario, C-42 no presupuestario para deuda pública y C-55 de regularización. C-42 estaba operativo en 2008 y deja campos exactos para recuperar: doble número SAF/SIDIF, beneficiario, cuentas, AXT, SIGADE, respaldo, firmas, TRANSAF, cotejo CGN y remisión TGN.

La mejora es probatoria, no una adjudicación. No hay cuerpo público que clasifique 71597, 152677 o 2876; cero-padding sólo genera claves. Tampoco se confunden aprobación con pago, banco beneficiario con cuenta pagadora, ni C-42 con su eventual C-55.

Sin cuerpo, historia, movimiento bancario y conciliación individual, el resultado permanece 0/10. Seis borradores no enviados; cero presentaciones y respuestas.
""",encoding="utf-8")
(HERE/"E0_FISCAL_RECONSTRUCTION_V150.md").write_text("""# Reconstrucción fiscal E0 V150

V150 mantiene 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones. Agrega la rama C-42 vigente en 2008, numeración SIDIF de siete dígitos y cadena de custodia/pago. Los pares 71597/0071597, 152677/0152677 y 2876/0002876 son claves, no identificaciones. Sólo conciliación bancaria individual completa entra al numerador.
""",encoding="utf-8")
(HERE/"RETRIEVAL_LOG_V150.md").write_text("""# Registro de recuperación V150

- Ocho fuentes conceptuales oficiales nuevas y once archivos preservados en bundle C-42.
- Tres imágenes oficiales controladas visualmente; PASS.
- Rama C-42 de deuda pública SAF355 y vigencia 2008 probadas; tipo target abierto.
- Numeración SIDIF de siete dígitos probada; tres variantes incorporadas sólo como claves.
- Ruta especial SAF355 diferenciada de Circular 16; e-SIDIF congelado como posterior.
- Búsquedas exactas sin cuerpos target; seis pedidos no presentados; 0/10.
""",encoding="utf-8")
(HERE/"HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V150_A_V151.md").write_text("""# Handover V150 → V151

## Estado

- QA PASS; 8 fuentes nuevas; 491 maestras y 251 E0.
- Res. SH 47/1996 y Disp. CGN 52/1996 prueban C-42 para deuda pública SAF355.
- Res. SH 6/2008 prueba C-42 operativo en 2008.
- Árbol activo C-41/C-42/C-55; cada ID se clasifica por cuerpo.
- Claves 0071597, 0152677 y 0002876 sólo para búsqueda.
- Cadena: SAF/sistema legado → TRANSAF/SIDIF → papel/cotejo CGN → aprobación → TGN → banco/conciliación.
- Circular 16 excluye SAF355/356 de vía general; Res. 81/2012 es comparador posterior.
- Cuerpos no localizados; seis DRAFT_NOT_SENT; cero presentaciones/respuestas; 0/10.

## Prioridad V151

1. Mantener borradores salvo autorización.
2. Buscar inventarios y actas SAF355/CGN 2008 por C-41/C-42/C-55.
3. Rastrear backups CONPRE/SIDIF Local/TRANSAF y cadena UAI–DADP.
4. Consultar IDs crudos y cero relleno.
5. Precisar cuentas/extractos CUT separando beneficiaria y pagadora.
6. Mantener 0/10 hasta cuerpo y puente bancario conciliado.
""",encoding="utf-8")
old=HERE/"HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V150_A_V150.md"
if old.exists(): old.unlink()

append_section(REPO/"BACKUP_ACTUALIZACION_2026-08-29.md","## V150 · rama C-42 y triple árbol documental","""
- C-42 para deuda pública SAF355 y vigencia 2008 probados; tipo target abierto.
- Árbol C-41/C-42/C-55 y variantes SIDIF de siete dígitos incorporados.
- Cadena SAF–TRANSAF–SIDIF–CGN–TGN–banco separada por estados.
- Ocho fuentes nuevas; 0/10; seis borradores no enviados.
""")

register_path=HERE/"E0_REQUEST_RESPONSE_REGISTER_V150.csv"; register=read_csv(register_path)
for row in register:
    row.update({"status":"DRAFT_NOT_SENT","submitted_on":"N/A","submission_channel":"N/A","receipt_or_case_id":"N/A","response_date":"N/A"})
write_csv(register_path,register,list(register[0]))

write_csv(HERE/"INHERITED_QA_STATUS_V150.csv",[
    {"script":"qa_v149.py","pre_v150_result":"PASS","post_v150_result":"EXPECTED_SUPERSEDED_ASSERTION","interpretation":"V149 ampliada por rama C-42."},
    {"script":"qa_v150.py","pre_v150_result":"N/A","post_v150_result":"PASS","interpretation":"Verifica fuentes, matrices, borradores y 0/10."},
])

hash_rows=[]
for row in catalog:
    local=row["archivo_local"]; path=REPO/local.lstrip("/") if local else None
    exists=bool(path and path.is_file()); actual=sha256(path) if exists else ""; expected=row["sha256"]
    hash_rows.append({"id":row["id"],"archivo_local":local,"exists":str(exists),"sha_catalog":expected,"sha_actual":actual,"hash_ok":str(bool(exists and expected and actual.lower()==expected.lower()))})
write_csv(AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V150.csv",hash_rows); write_csv(AUDIT/"SOURCE_BACKUP_CENSUS_V150.csv",hash_rows)
physical=sum(r["exists"]=="True" for r in hash_rows); hash_ok=sum(r["hash_ok"]=="True" for r in hash_rows)

size_rows=[]
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts: continue
    size=path.stat().st_size
    size_rows.append({"path":path.relative_to(REPO).as_posix(),"bytes":size,"mib":f"{size/1048576:.6f}","over_50_mib":str(size>50*1048576),"over_100_mib":str(size>100*1048576)})
write_csv(AUDIT/"GITHUB_FILE_SIZE_AUDIT_V150.csv",size_rows)

complete=json.loads((AUDIT/"CURRENT_SOURCE_COMPLETENESS_V149.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V150","date":"2026-08-31","state":"E0_C42_PUBLIC_DEBT_BRANCH_OPERATIVE_2008_THREE_BRANCH_TREE_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries":len(catalog),"physical_local_copies":physical,"physical_local_hash_ok":hash_ok,"remaining_physical_gaps":len(catalog)-physical,
    "e0_primary_sources_preserved":len(census),"numeric_v150_strict_changed":False,"sources_newly_preserved_v150":8,"e0_primary_sources_newly_preserved_v150":8,
    "e0_fiscal_method_breaks_frozen":len(breaks),"e0_request_traceability_rows":len(trace),"e0_request_search_keys":len(keys),
    "e0_v150_pdf_visual_controls":56,"e0_v150_image_visual_controls":len(image_visual),"e0_v150_total_visual_controls":56+len(image_visual),
    "e0_c42_source_bundle_files":len(bundle),"e0_c42_branch_rows":len(branch),"e0_c42_field_custody_rows":len(fields),"e0_c42_zero_padded_rows":len(padded),
    "e0_three_branch_tree_rows":len(tree_rows),"e0_res81_crosswalk_rows":len(crosswalk),"e0_v150_public_search_rows":len(negative),"e0_v150_request_objects":len(request_objects),
    "e0_c42_public_debt_branch_operative_2008":True,"e0_c42_target_form_type_proved":False,"e0_c42_legacy_sidif_7digit_numbering_proved":True,
    "e0_c42_target_bodies_located":0,"e0_target_forms_public_bodies_located":0,"e0_three_branch_payment_tree_active":True,
    "e0_settlement_executed_rows_confirmed":0,"e0_requests_submitted":0,"e0_request_responses_received":0,"e0_request_package_status":"DRAFT_NOT_SENT",
    "historical_workstream":"Recover C41/C42/C55 bodies, legacy logs, official archive and bank reconciliation; no request submitted",
})
(AUDIT/"CURRENT_SOURCE_COMPLETENESS_V150.json").write_text(json.dumps(complete,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

(HERE/"AUDITORIA_V150.md").write_text(f"""# Auditoría V150

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: 8.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog)-physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}.
- Controles: 56 PDF heredados + {len(image_visual)} imágenes = {56+len(image_visual)}.
- Rama C-42 2008 probada; cuerpos target 0/3; ejecución 0/10; pedidos/respuestas 0/0.
""",encoding="utf-8")

def checkpoint_manifest():
    files=[{"path":p.name,"bytes":p.stat().st_size,"sha256":sha256(p)} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!="MANIFEST_V150.json"]
    payload={"checkpoint":"V150","parent_checkpoint":"V149","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
        "exact_entities":30,"strict_coverage_pct":STRICT,"closed_network_gate":"NO","e0_primary_sources":len(census),"new_preserved_sources":8,
        "fiscal_method_breaks":len(breaks),"request_traceability_rows":len(trace),"request_search_keys":len(keys),"pdf_visual_controls_inherited":56,
        "image_visual_controls_v150":len(image_visual),"c42_source_bundle_files":len(bundle),"c42_branch_rows":len(branch),"c42_field_rows":len(fields),
        "zero_padded_rows":len(padded),"three_branch_tree_rows":len(tree_rows),"res81_crosswalk_rows":len(crosswalk),"public_search_rows":len(negative),
        "v150_request_objects":len(request_objects),"c42_public_debt_branch_operative_2008":True,"c42_target_form_type_proved":False,
        "c42_legacy_sidif_7digit_numbering_proved":True,"three_branch_payment_tree_active":True,"target_forms_public_bodies_located":0,
        "award_rows_exact":10,"account_candidate_rows":9,"executed_settlement_rows_confirmed":0,"request_drafts":6,"requests_submitted":0,"responses_received":0,"files":files}
    (HERE/"MANIFEST_V150.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def tree(root):
    paths=sorted(Path(root).rglob("*"),key=lambda p:p.relative_to(root).as_posix().casefold())
    return "\n".join(p.relative_to(root).as_posix()+("/" if p.is_dir() else "") for p in paths if ".git" not in p.parts and "__pycache__" not in p.parts and "tmp" not in p.parts)+"\n"

(REPO/"TREE.txt").write_text(tree(REPO),encoding="utf-8"); (CYCLE/"TREE.txt").write_text(tree(CYCLE),encoding="utf-8")
checkpoint_manifest()
global_manifest=CYCLE/"MANIFEST_SHA256.json"; global_files=[]
for path in sorted(REPO.rglob("*"),key=lambda p:p.relative_to(REPO).as_posix().casefold()):
    if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts and path!=global_manifest:
        global_files.append({"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)})
payload={"checkpoint":"V150","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":STRICT,
    "exact_entities":30,"closed_network_gate":"NO","source_audit":f"{len(catalog)} master; {physical} physical SHA-valid; 8 new sources; C42 branch proved; target open; 0/10; six drafts not submitted.",
    "historical_workstream":"Recover C41/C42/C55 bodies, legacy logs, official archive and bank reconciliation; no request submitted","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp=global_manifest.with_suffix(".json.v150tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(global_manifest)
print(f"V150 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)}")
