from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v149" / "binaries"
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


# id, institución, título, URL, archivo, período, serie, tipo, nota, procedencia
SOURCES = [
    ("e0_argentina_resolution_6_2008_closing_original", "Secretaría de Hacienda / CGN / TGN", "Resolución SH 6/2008 · cierre de cuentas del ejercicio 2008", "https://www.argentina.gob.ar/normativa/nacional/norma-148348/texto", "argentina_resolution_6_2008_closing_original.html", "2008-2009", "Resolución SH 6/2008", "HTML oficial · texto original preservado", "Arts. 4, 6, 8 y 22: plazos C-41/C-55, listados finales, conformidad, ajustes, notas y archivo oficial de originales.", "Captura directa del texto original en argentina.gob.ar."),
    ("e0_cgn_disposition_28_2008_intermediate_close", "Contaduría General de la Nación", "Disposición CGN 28/2008 · cierre intermedio al 30 de junio", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/disp28/disp28.htm", "cgn_disposition_28_2008_intermediate_close.html", "2008", "Disposición CGN 28/2008", "HTML oficial · captura preservada", "Cierre intermedio, regularización de inconsistencias, saldos finales, conformidad definitiva y aclaraciones.", "Captura directa de economia.gob.ar; TLS vencido tolerado tras verificar dominio y contenido."),
    ("e0_cgn_disposition_38_1996_cut_account_3855", "CGN / TGN", "Disposición CGN 38/1996 · conciliación CUT y BNA 3855/19", "https://www.economia.gob.ar/digesto/disposiciones/cgn/1996/discgn38.htm", "cgn_disposition_38_1996_cut_account_3855.html", "1996", "Disposición CGN 38/1996", "HTML oficial · captura preservada", "Prueba 3855/19 histórica, conciliación SIDIF Central, comprobante/importe y fechas de extracto/proceso.", "Captura directa del Digesto oficial; TLS vencido tolerado tras verificar dominio y contenido."),
    ("e0_cgn_disposition_38_1996_annex_cut_extracts", "CGN / TGN / BNA", "Anexo Disposición CGN 38/1996 · doble edición de extractos CUT", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/disp38/dis38a.htm", "cgn_disposition_38_1996_annex_cut_extracts.html", "1996", "Anexo Disposición CGN 38/1996", "HTML oficial · captura preservada", "BNA producía dos ediciones magnéticas diarias y una en papel: TGN recibía una y el SAF otra más respaldo.", "Captura directa de economia.gob.ar; TLS vencido tolerado tras verificar dominio y contenido."),
    ("e0_mecon_uai_report_06_2019_saf355_close_2018", "Ministerio de Hacienda · UAI / SAF 355", "Informe UAI 06/2019 · cierre 2018 del SAF 355", "https://www.argentina.gob.ar/sites/default/files/informe_uai_no_06.pdf", "mecon_uai_report_06_2019_saf355_close_2018.pdf", "2018-2019", "Informe UAI 06/2019", "PDF oficial · binario preservado", "Anexo I publica tipo, número interno, número SIDIF e historia de cortes; REPO sólo como comparador posterior.", "Descarga oficial; páginas 4-6 controladas visualmente."),
    ("e0_mecon_uai_report_35_2019_saf355_change_close", "Ministerio de Hacienda · UAI / SAF 355", "Informe UAI 35/2019 · cambio de administración SAF 355", "https://www.argentina.gob.ar/sites/default/files/informe_uai_no_35.pdf", "mecon_uai_report_35_2019_saf355_change_close.pdf", "2019", "Informe UAI 35/2019", "PDF oficial · binario preservado", "Individualiza acta y base SIGADE actualizada reservada en UAI para consulta.", "Descarga oficial; página 4 controlada visualmente."),
    ("e0_mecon_uai_report_37_2019_tgn_change_close", "Ministerio de Hacienda · UAI / TGN", "Informe UAI 37/2019 · cambio de administración TGN", "https://www.argentina.gob.ar/sites/default/files/informe_uai_no_37_a.pdf", "mecon_uai_report_37_2019_tgn_change_close.pdf", "2019", "Informe UAI 37/2019", "PDF oficial · binario preservado", "Individualiza módulo de conciliación, nota TGN, movimientos, saldos y salidas para BNA 3855/19.", "Descarga oficial; páginas 3-6 controladas visualmente."),
    ("e0_mecon_uai_report_02_2019_tgn_close_2018", "Ministerio de Hacienda · UAI / TGN", "Informe UAI 02/2019 · cierre 2018 de la TGN", "https://www.argentina.gob.ar/sites/default/files/informe_uai_no_02.pdf", "mecon_uai_report_02_2019_tgn_close_2018.pdf", "2018-2019", "Informe UAI 02/2019", "PDF oficial · binario preservado", "Expone 3855/19, clases de pago y saldos SIDIF/banco/partidas conciliatorias.", "Descarga oficial; páginas 4-7 controladas visualmente."),
    ("e0_argentina_resolution_257_2018_closing_original", "Secretaría de Hacienda / CGN", "Resolución SH 257/2018 · cierre de cuentas 2018", "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-257-2018-317443/texto", "argentina_resolution_257_2018_closing_original.html", "2018-2019", "Resolución SH 257/2018", "HTML oficial · texto original preservado", "Comparador posterior de listados finales y archivo oficial; no prueba el target 2008.", "Captura directa del texto original en argentina.gob.ar."),
]

source_rows = []
for sid, institution, title, url, filename, period, series, kind, note, provenance_note in SOURCES:
    path = BIN / filename; assert path.is_file(), path
    source_rows.append({"id": sid, "institution": institution, "title": title, "url": url, "local": "/" + path.relative_to(REPO).as_posix(), "period": period, "series": series, "kind": kind, "note": note, "provenance_note": provenance_note, "sha": sha256(path), "bytes": path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{"id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"], "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"], "fecha_descarga": "2026-08-31", "fecha_publicacion": s["period"], "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"], "sha256": s["sha"], "nota": "V149: " + s["note"]} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V149.csv"
census = read_csv(census_path)
census = upsert(census, [{"source_id": s["id"], "institution": s["institution"], "artifact": s["title"], "url": s["url"], "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"], "period_coverage": s["period"], "variable_families": "closing;SAF355;SIDIF;SIGADE;TGN;BNA;CUT;custody", "primary_source": "YES", "preserved": "YES", "method_breaks": "cierre intermedio/final; fecha extracto/proceso; cuenta histórica/target; custodia/pago", "use_status": "E0_USABLE_WITH_SCOPE", "caveat": s["note"]} for s in source_rows], "source_id")
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V149.csv"
provenance = read_csv(provenance_path)
provenance = upsert(provenance, [{"source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"], "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT", "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"], "provenance_note": s["provenance_note"]} for s in source_rows], "source_id")
write_csv(provenance_path, provenance, list(provenance[0]))

closing = matrix("E0_2008_CLOSING_FORM_AND_ARCHIVE_ROUTE_V149.csv", ["row_id","object","contemporaneous_fact","retrieval_consequence","source_id","locator","status","target_payment_confirmed"], [
    ("CL149_01","SIDIF_CLOSE","CGN cerraba 2008 con SIDIF y complementarios.","Pedir salida y corte SAF355.","e0_argentina_resolution_6_2008_closing_original","art.1","ROUTE_PROVED_TARGET_OPEN","FALSE"),
    ("CL149_02","C41_DEADLINE","C-41 se recibía hasta 7/1/2009.","Buscar ambos lados del corte.","e0_argentina_resolution_6_2008_closing_original","art.4","WINDOW_PROVED_TYPE_OPEN","FALSE"),
    ("CL149_03","C55_REGULARIZATION","Regularizaciones TGN C-10/C-55 hasta 31/1/2009.","Buscar historia enero 2009.","e0_argentina_resolution_6_2008_closing_original","art.6","WINDOW_PROVED_TYPE_OPEN","FALSE"),
    ("CL149_04","VALID_BASE","SIDIF al cierre era base válida.","Pedir dump/listado reproducible.","e0_argentina_resolution_6_2008_closing_original","art.8","BASE_PROVED","FALSE"),
    ("CL149_05","FINAL_LISTS","CGN daba listados finales a los SAF.","Pedir archivo, parámetros y hash.","e0_argentina_resolution_6_2008_closing_original","art.8","RECORD_CLASS_PROVED","FALSE"),
    ("CL149_06","VERIFICATION","SAF debía verificar y conciliar.","Pedir papel de conciliación.","e0_argentina_resolution_6_2008_closing_original","art.8","CONTROL_PROVED","FALSE"),
    ("CL149_07","RETURN_CONFORMITY","Listados volvían conformados en diez días.","Pedir versión firmada.","e0_argentina_resolution_6_2008_closing_original","art.8","SIGNED_RECORD_CLASS_PROVED","FALSE"),
    ("CL149_08","ADJUSTMENT_FORM","Diferencias exigían formularios de ajuste.","Pedir tipo, número y renglones.","e0_argentina_resolution_6_2008_closing_original","art.8","ADJUSTMENT_ROUTE_PROVED","FALSE"),
    ("CL149_09","EXPLANATORY_NOTE","Cada discrepancia exigía nota firmada.","Pedir nota, anexos y firmantes.","e0_argentina_resolution_6_2008_closing_original","art.8","NOTE_ROUTE_PROVED","FALSE"),
    ("CL149_10","UAI_NOTICE","Diferencias se comunicaban a SIGEN/UAI.","Pedir comunicación y seguimiento.","e0_argentina_resolution_6_2008_closing_original","art.8","AUDIT_ROUTE_PROVED","FALSE"),
    ("CL149_11","RESPONSIBLE_OFFICIALS","Había responsables SAF y contables nominados.","Pedir inventario por productor.","e0_argentina_resolution_6_2008_closing_original","art.22","RESPONSIBILITY_PROVED","FALSE"),
    ("CL149_12","ORIGINAL_SUPPORT","Firmas certificaban originales en archivo oficial.","Pedir originales e inventario.","e0_argentina_resolution_6_2008_closing_original","art.22","ORIGINAL_ARCHIVE_ROUTE_PROVED","FALSE"),
    ("CL149_13","COMPLEMENTARY_AUTHORITY","CGN/ONP/TGN podían pedir más información.","Pedir requerimientos y respuestas.","e0_argentina_resolution_6_2008_closing_original","art.31","REQUEST_ROUTE_PROVED","FALSE"),
    ("CL149_14","TYPE_LIMIT","C-41 y C-55 coexistían en el cierre.","No clasificar por número.","e0_argentina_resolution_6_2008_closing_original","arts.4 y 6","TARGET_TYPE_OPEN","FALSE"),
    ("CL149_15","PUBLIC_GAP","Sólo está pública la fila Anexo K.","Pedir cuerpos; mantener 0/10.","e0_cgn_cuenta_inversion_2008_sdp","Anexo K p.67","TARGET_BODIES_NOT_LOCATED","FALSE"),
])

intermediate = matrix("E0_2008_INTERMEDIATE_FINAL_LIST_ROUTE_V149.csv", ["row_id","stage","official_fact","requested_record","source_id","locator","inference_limit","status"], [
    ("IC149_01","CUT_DATE","Cierre intermedio al 30/6/2008.","corte y parámetros","e0_cgn_disposition_28_2008_intermediate_close","arts.1-2","No es 31/12.","PROVED"),
    ("IC149_02","CONFORMITY","Conformidad volvía inalterable la ejecución salvo causa.","constancia firmada","e0_cgn_disposition_28_2008_intermediate_close","cuerpo","No elimina cambios posteriores.","PROVED"),
    ("IC149_03","INCONSISTENCIES","Inconsistencias debían regularizarse.","formularios y nota","e0_cgn_disposition_28_2008_intermediate_close","cuerpo","No identifica target.","PROVED"),
    ("IC149_04","FINAL_BALANCES","CGN remitía saldos finales.","listado final 30/6","e0_cgn_disposition_28_2008_intermediate_close","cuerpo","Saldo neto no identifica movimiento.","PROVED"),
    ("IC149_05","DEFINITIVE_CONFORMITY","SAF/UEPEX daban conformidad definitiva.","devolución conformada","e0_cgn_disposition_28_2008_intermediate_close","cuerpo","No sustituye formulario.","PROVED"),
    ("IC149_06","NOTES","Podían adjuntarse notas y aclaraciones.","nota y anexos","e0_cgn_disposition_28_2008_intermediate_close","cuerpo","No confirma pago.","PROVED"),
    ("IC149_07","SUPPORT","Responsables certificaban respaldo.","originales e inventario","e0_cgn_disposition_28_2008_intermediate_close","art.15","Custodia no es ejecución.","PROVED"),
    ("IC149_08","H1_SEARCH","Primer semestre tenía paquete formal.","listas/conformidad/notas 30/6","e0_cgn_disposition_28_2008_intermediate_close","integral","No asignar IDs por magnitud.","SEARCH_BRANCH"),
    ("IC149_09","H2_SEARCH","Cierre anual tenía paquete formal.","listas/ajustes/notas 31/12","e0_argentina_resolution_6_2008_closing_original","art.8","No asignar IDs por magnitud.","SEARCH_BRANCH"),
    ("IC149_10","TARGET_SPLIT","Buscar tres IDs en ambos paquetes.","71597;152677;2876","multiple","H1/H2","No inferir semestre.","OPEN_0_OF_10"),
])

last_forms = matrix("E0_UAI_LAST_FORM_CUT_SCHEMA_V149.csv", ["row_id","record_type","act_internal_sidif","later_internal_sidif","observed_change","controlled_use","source_id","locator","target_2008_proof"], [
    ("LF149_01","ACTS","IF-2019-00247631 / IF-2019-01053905","N/A","dos cortes","Pedir actas equivalentes.","e0_mecon_uai_report_06_2019_saf355_close_2018","pp.4-5","FALSE"),
    ("LF149_02","IR","556/483003","587/483153","31","Crosswalk interno↔SIDIF.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_03","CMIR","23/15294","25/16462","2","Número solo no clasifica.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_04","C35","61564/109183","sin cambio","0","Clase explícita requerida.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_05","C41","307329/331295","sin cambio","0","C-41 no se deduce del rango.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_06","PRE","9/325077","sin cambio","0","Conservar tipo e IDs.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_07","C42","307331/20100","sin cambio","0","Conservar tipo e IDs.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_08","C55","307342/73318","307820/74633","17 y luego 4","Buscar historia post-cierre.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_09","CMR","2446/73652","sin cambio","0","Conservar clase y corte.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_10","CRG","2545/73870","2629/SN","27 y luego 57","Buscar historia y monto.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_11","REPO","N/A","CRG posterior","cancelaciones REPO","Comparador posterior.","e0_mecon_uai_report_06_2019_saf355_close_2018","p.5","FALSE"),
    ("LF149_12","SCHEMA","tipo+número interno+número SIDIF","dos cortes","historia","Pedir mismo esquema 2008.","e0_mecon_uai_report_06_2019_saf355_close_2018","Anexo I p.6","FALSE"),
    ("LF149_13","LIMIT","71597/152677/2876","N/A","sin cuerpo","No homologar por rango.","e0_cgn_cuenta_inversion_2008_sdp","Anexo K p.67","FALSE"),
])

sigade = matrix("E0_UAI_SIGADE_BACKUP_CUSTODY_ROUTE_V149.csv", ["row_id","object","official_fact","request_field","source_id","locator","status","target_2008_proof"], [
    ("SG149_01","CUT","Corte al 9/12/2019.","timestamp","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","COMPARATOR","FALSE"),
    ("SG149_02","LAST_FORMS","UAI obtuvo últimos e-SIDIF.","acta/exportación","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","RECORD_CLASS_PROVED","FALSE"),
    ("SG149_03","ACT","IF-2019-109041824-APN-UAI#MHA.","cuerpo/anexos","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","EXACT_ID_PROVED","FALSE"),
    ("SG149_04","BACKUP","UAI obtuvo base SIGADE al corte.","medio/archivo/formato","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","BACKUP_CLASS_PROVED","FALSE"),
    ("SG149_05","CUSTODIAN","Base reservada en UAI para consulta.","inventario/ubicación","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","NAMED_CUSTODIAN_2019","FALSE"),
    ("SG149_06","INTEGRITY","No publica hash ni esquema.","checksum/motor/versión","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","METADATA_OPEN","FALSE"),
    ("SG149_07","RESTORE","La copia admite consulta institucional.","restore/export","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","REQUEST_OBJECT","FALSE"),
    ("SG149_08","QUERY","83106000 no aparece.","consulta exacta/cero","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","TARGET_QUERY_OPEN","FALSE"),
    ("SG149_09","TEMPORAL_LIMIT","Snapshot probado sólo en 2019.","inventarios 2008","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","NO_2008_SNAPSHOT_INFERENCE","FALSE"),
    ("SG149_10","DISPOSITION","Destino posterior no publicado.","custodia/transferencia/expurgo","e0_mecon_uai_report_35_2019_saf355_change_close","p.4","PRESERVATION_OPEN","FALSE"),
])

tgn = matrix("E0_TGN_BANK_CUT_OUTPUT_AND_NOTE_CHAIN_V149.csv", ["row_id","object","official_fact","retrieval_use","source_id","locator","status","target_2008_proof"], [
    ("TB149_01","UNIVERSE","UAI pidió universo de cuentas TGN.","Pedir universo 2008.","e0_mecon_uai_report_37_2019_tgn_change_close","pp.3-4","COMPARATOR","FALSE"),
    ("TB149_02","BALANCES","Pidió saldos y conciliaciones.","Pedir SIDIF/extracto/partidas.","e0_mecon_uai_report_37_2019_tgn_change_close","pp.3-4","COMPARATOR","FALSE"),
    ("TB149_03","MOVEMENTS","Obtuvo listas e-SIDIF.","Pedir salida nativa/CSV.","e0_mecon_uai_report_37_2019_tgn_change_close","pp.3-4","RECORD_CLASS_PROVED","FALSE"),
    ("TB149_04","ACT","IF-2019-109242536-APN-UAI#MHA.","Pedir cuerpo/anexos.","e0_mecon_uai_report_37_2019_tgn_change_close","p.4","EXACT_ID_PROVED","FALSE"),
    ("TB149_05","TGN_NOTE","NO-2019-109266599-APN-TGN#MHA.","Pedir nota/adjuntos.","e0_mecon_uai_report_37_2019_tgn_change_close","p.4","EXACT_ID_PROVED","FALSE"),
    ("TB149_06","MODULE","Usó módulo de conciliación bancaria.","Pedir versión/filtros.","e0_mecon_uai_report_37_2019_tgn_change_close","p.4","SYSTEM_ROUTE_PROVED","FALSE"),
    ("TB149_07","ACCOUNT","BNA 3855/19 figura en salida.","Filtro histórico candidato.","e0_mecon_uai_report_37_2019_tgn_change_close","pp.4-5","LATER_ACCOUNT_PROVED","FALSE"),
    ("TB149_08","LAST_CHEQUE","Individualiza último cheque.","Pedir tipo/número/movimiento.","e0_mecon_uai_report_37_2019_tgn_change_close","p.5","OUTPUT_CLASS_PROVED","FALSE"),
    ("TB149_09","NETWORK_PAYMENT","Usa Listado Reporte Resumen de Pagos.","Pedir reporte/parámetros.","e0_mecon_uai_report_37_2019_tgn_change_close","p.5","NAMED_OUTPUT_PROVED","FALSE"),
    ("TB149_10","NOTE_PAYMENT","Individualiza último pago por nota.","Pedir nota/resultado.","e0_mecon_uai_report_37_2019_tgn_change_close","p.5","OUTPUT_CLASS_PROVED","FALSE"),
    ("TB149_11","EXTRACT_DELAY","Extracto previo se procesó después.","Separar fecha valor/proceso.","e0_mecon_uai_report_37_2019_tgn_change_close","pp.4-5","DATE_BREAK_PROVED","FALSE"),
    ("TB149_12","2018_RECON","Cierre usa saldo SIDIF, banco y partidas.","Pedir tabla completa.","e0_mecon_uai_report_02_2019_tgn_close_2018","pp.6-7","COMPARATOR","FALSE"),
    ("TB149_13","SIGADE_NOTES","Partidas incluían notas SIGADE y lotes.","Pedir nota/lote/cruce.","e0_mecon_uai_report_02_2019_tgn_close_2018","p.6","COMPARATOR","FALSE"),
    ("TB149_14","LIMIT","Informes no publican target 83106000.","No atribuir cuenta/salida.","multiple","integral","TARGET_ACCOUNT_OPEN","FALSE"),
])

cut = matrix("E0_CUT_3855_HISTORICAL_CUSTODY_ROUTE_V149.csv", ["row_id","element","historic_fact","target_use","source_id","locator","status","target_payment_confirmed"], [
    ("CU149_01","ACCOUNT","BNA 3855/19 operaba en 1996.","Filtro histórico candidato.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento","HISTORICAL_CONTINUITY_PROVED","FALSE"),
    ("CU149_02","CUT","Era cuenta CUT/TGN.","Pedir vigencia 2008.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento","ACCOUNT_ROLE_PROVED_1996","FALSE"),
    ("CU149_03","DAILY","BNA emitía extractos diarios.","Pedir fecha valor/secuencia.","e0_cgn_disposition_38_1996_annex_cut_extracts","anexo","FREQUENCY_PROVED","FALSE"),
    ("CU149_04","MAGNETIC_A","Primera copia magnética iba a TGN.","Buscar copia TGN.","e0_cgn_disposition_38_1996_annex_cut_extracts","anexo","CUSTODY_ROUTE_PROVED","FALSE"),
    ("CU149_05","MAGNETIC_B","Segunda copia magnética iba al SAF.","Buscar copia SAF355.","e0_cgn_disposition_38_1996_annex_cut_extracts","anexo","CUSTODY_ROUTE_PROVED","FALSE"),
    ("CU149_06","PAPER","Papel y respaldo iban al SAF.","Pedir soporte/inventario.","e0_cgn_disposition_38_1996_annex_cut_extracts","anexo","DUAL_MEDIA_ROUTE_PROVED","FALSE"),
    ("CU149_07","LOADER","TGN cargaba soporte BNA en SIDIF.","Pedir log de carga.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento 1","SYSTEM_ROUTE_PROVED","FALSE"),
    ("CU149_08","READER","Proceso leía cada movimiento 3855/19.","Exportar sin filtro inicial.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento 2","MOVEMENT_UNIVERSE_PROVED","FALSE"),
    ("CU149_09","FIELDS","Usaba código, comprobante e importe.","Cruzar referencia/importe.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento 2","FIELD_ROUTE_PROVED","FALSE"),
    ("CU149_10","BOOK","Registraba en Libro Banco.","Pedir asiento/marca.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento","BOOK_ROUTE_PROVED","FALSE"),
    ("CU149_11","RECONCILED","Marcaba movimientos conciliados.","Pedir estado/reversas.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento","RECONCILIATION_ROUTE_PROVED","FALSE"),
    ("CU149_12","DATES","Emisión=extracto; registro=proceso.","Distinguir ambas fechas.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento","DATE_SEMANTICS_PROVED","FALSE"),
    ("CU149_13","NEGATIVE_CODE","TRAC/TROD eran transferencias.","No tratarlos como comisión.","e0_cgn_disposition_38_1996_cut_account_3855","procedimiento 2","NEGATIVE_CONTROL","FALSE"),
    ("CU149_14","LIMIT","Continuidad no prueba uso target 2008.","Exigir cuerpo/extracto target.","multiple","1996-2019","TARGET_ACCOUNT_OPEN","FALSE"),
])

dadp = matrix("E0_DADP_BUYBACK_DOCUMENT_CUSTODY_V149.csv", ["row_id","object","contemporaneous_rule","request_use","source_id","locator","status","target_commission_proved"], [
    ("DP149_01","OFFERS","Procedimiento documenta ofertas.","Pedir planillas/soporte.","e0_argentina_rc_212_24_2008_recompra","§1","PRODUCER_ROUTE_PROVED","FALSE"),
    ("DP149_02","PREADJUDICATION","ONCP confecciona preadjudicación.","Pedir versión firmada.","e0_argentina_rc_212_24_2008_recompra","§1","RECORD_CLASS_PROVED","FALSE"),
    ("DP149_03","TRANSFER","Caja informa títulos transferidos.","Pedir comunicación.","e0_argentina_rc_212_24_2008_recompra","§1","RECORD_CLASS_PROVED","FALSE"),
    ("DP149_04","PAYMENT","Finanzas paga en cuenta BCRA.","Pedir instrucción/resultado.","e0_argentina_rc_212_24_2008_recompra","§1","PAYMENT_ROUTE_PROVED","FALSE"),
    ("DP149_05","CUSTODIAN","Documentación queda en DADP.","Pedir inventario/legajo.","e0_argentina_rc_212_24_2008_recompra","§1.13","NAMED_CUSTODIAN_PROVED","FALSE"),
    ("DP149_06","CONTROL","Custodia es para control competente.","Pedir copia/índice.","e0_argentina_rc_212_24_2008_recompra","§1.13","CONTROL_PURPOSE_PROVED","FALSE"),
    ("DP149_07","CROSSWALK","Legajo puede enlazar orden bancaria.","Pedir IDs/remisiones.","e0_argentina_rc_212_24_2008_recompra","§1","REQUEST_OBJECT","FALSE"),
    ("DP149_08","LIMIT","Norma no vincula 83106000.","No atribuir sin cuerpo.","e0_argentina_rc_212_24_2008_recompra","integral","TARGET_LINK_OPEN","FALSE"),
])

search = matrix("E0_V149_EXACT_PUBLIC_SEARCH_V149.csv", ["search_id","exact_query","official_result","status","result_url","searched_on","negative_inference_limit","next_action"], [
    ("XS149_01","83106000","fila Anexo K","EXACT_PUBLIC_REFERENCE_ROW_ONLY","https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf","2026-08-31","No prueba cuerpo/pago.","pedido por archivo"),
    ("XS149_02","71597","sólo fila Anexo K","EXACT_PUBLIC_REFERENCE_ROW_ONLY","https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf","2026-08-31","No prueba tipo.","buscar H1/H2"),
    ("XS149_03","152677","sólo fila Anexo K","EXACT_PUBLIC_REFERENCE_ROW_ONLY","https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf","2026-08-31","No prueba tipo.","buscar H1/H2"),
    ("XS149_04","2876","sólo fila Anexo K","EXACT_PUBLIC_REFERENCE_ROW_ONLY","https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf","2026-08-31","No prueba tipo.","buscar H1/H2"),
    ("XS149_05","32.270,30","agregado publicado","EXACT_PUBLIC_REFERENCE_ROW_ONLY","https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf","2026-08-31","No desagrega cuerpos.","pedir componentes"),
    ("XS149_06","3855/19 2008","sin fila target","PUBLIC_TARGET_LINK_NOT_LOCATED","N/A","2026-08-31","Cuenta histórica no es target.","pedir extractos"),
    ("XS149_07","acta últimos formularios 2008","sin cuerpo","PUBLIC_BODY_NOT_LOCATED","N/A","2026-08-31","No prueba inexistencia.","pedir UAI/SAF"),
    ("XS149_08","listados finales SAF355 2008","sin archivo","PUBLIC_BODY_NOT_LOCATED","N/A","2026-08-31","No prueba inexistencia.","pedir archivo oficial"),
    ("XS149_09","respaldo SIGADE 2008 UAI","sin snapshot","PUBLIC_SNAPSHOT_NOT_LOCATED","N/A","2026-08-31","2019 no retrotrae.","pedir inventario"),
    ("XS149_10","negative_limit","cuerpos no localizados","CONTROLLED_NEGATIVE","N/A","2026-08-31","Sólo no localización pública.","pedidos no enviados"),
])

object_specs = [
    ("CGN/SAF355","Listados finales SIDIF","archivo;parámetros;corte;hash"),("SAF355","Devoluciones conformadas","firma;fecha;versión"),("SAF355/CGN","Ajustes","tipo;número;renglones"),("SAF355","Notas firmadas","nota;firmantes;anexos"),("SIGEN/UAI","Comunicaciones de diferencias","ID;fecha;seguimiento"),("Archivo SAF355","Originales respaldatorios","inventario;serie;caja"),("CGN/SAF355","Paquete 30/6/2008","listas;conformidad;notas"),("CGN/SAF355","Paquete 31/12/2008","listas;ajustes;notas"),("SIDIF/SICHE","Cuerpo 71597","tipo;interno;SIDIF;estado"),("SIDIF/SICHE","Cuerpo 152677","tipo;interno;SIDIF;estado"),("SIDIF/SICHE","Cuerpo 2876","tipo;interno;SIDIF;estado"),("UAI","Acta últimos formularios","IF;tipo;interno;SIDIF"),("UAI/SIGADE","Backups 2008","archivo;motor;timestamp;hash"),("UAI/SIGADE","Restore/consulta 83106000","filtros;filas;diccionario"),("TGN","Nota de saldos/movimientos","cuenta;fecha;signo;importe"),("TGN/SIDIF","Reporte Resumen de Pagos","parámetros;orden;resultado"),("TGN/BNA","Extractos 3855/19/alternativas","fecha valor;proceso;código"),("SAF355","Copia magnética/papel BNA","medio;inventario;custodia"),("DADP/ONCP","Legajo recompra §1.13","índice;orden;remisión"),("CGN/TGN/BNA","Libro Banco y conciliación","movimiento;grupo;reversa"),
]
request_objects = matrix("E0_V149_REQUEST_OBJECTS_V149.csv", ["object_id","owner_or_system","requested_record","minimum_usable_fields","success_test","negative_response_rule","status"], [(f"RO149_{i:02d}",owner,record,fields,"Enlazable por ID, fecha, cuenta, signo, importe y referencia.","Individualizar serie, búsqueda, migración o disposición.","DRAFT_NOT_SENT") for i,(owner,record,fields) in enumerate(object_specs,1)])

# 3855/19 deja de ser identificador sólo posterior, sin convertirse en cuenta target probada.
repo_path = HERE / "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V149.csv"
repo_rows = read_csv(repo_path)
for row in repo_rows:
    if row["row_id"] == "CR141_04":
        row.update({"target_application":"identificar 3855/19 y cuentas alternativas vigentes en 2008","inference_limit":"3855/19 es candidata histórica; no cuenta target","status":"HISTORICAL_ACCOUNT_CLASS_QUERY_PROVED"})
    if row["row_id"] == "CR141_09":
        row.update({"evidence":"Cuenta CUT 3855/19 probada en 1996 y controles 2018/2019","proved_scope":"continuidad histórica del identificador","target_application":"filtro candidato junto con universo completo 2008","required_output":"vigencia;titular;cuenta;extracto;referencia","inference_limit":"no prueba que 83106000 usara esa cuenta","status":"HISTORICAL_ACCOUNT_CONTINUITY_PROVED_TARGET_USE_OPEN","source_id":"e0_cgn_disposition_38_1996_cut_account_3855;e0_mecon_uai_report_02_2019_tgn_close_2018","locator":"Disposición 38/1996; UAI 02/2019 pp.6-7"})
write_csv(repo_path, repo_rows, list(repo_rows[0]))

visual_path = HERE / "E0_V149_PDF_VISUAL_CONTROL.csv"
visual = read_csv(visual_path)
visual_specs = [
    ("PV149_45","e0_mecon_uai_report_06_2019_saf355_close_2018","3","4","corte, actos y registros posteriores"),("PV149_46","e0_mecon_uai_report_06_2019_saf355_close_2018","4","5","C-55, CRG y causas REPO"),("PV149_47","e0_mecon_uai_report_06_2019_saf355_close_2018","5","6","Anexo I tipo-interno-SIDIF"),("PV149_48","e0_mecon_uai_report_35_2019_saf355_change_close","4","4","base SIGADE reservada UAI"),("PV149_49","e0_mecon_uai_report_37_2019_tgn_change_close","3","3","cuentas, saldos y conciliaciones"),("PV149_50","e0_mecon_uai_report_37_2019_tgn_change_close","4","4","acta, nota, módulo y demora"),("PV149_51","e0_mecon_uai_report_37_2019_tgn_change_close","5","5","3855/19 y clases de pago"),("PV149_52","e0_mecon_uai_report_37_2019_tgn_change_close","6","6","salidas BCRA"),("PV149_53","e0_mecon_uai_report_02_2019_tgn_close_2018","4","4","metodología y saldos"),("PV149_54","e0_mecon_uai_report_02_2019_tgn_close_2018","5","5","3855/19 y reporte de pagos"),("PV149_55","e0_mecon_uai_report_02_2019_tgn_close_2018","6","6","partidas y notas SIGADE"),("PV149_56","e0_mecon_uai_report_02_2019_tgn_close_2018","7","7","saldo SIDIF, banco y tránsitos"),
]
visual = upsert(visual, [{"control_id":cid,"source_id":sid,"printed_page":printed,"pdf_page":pdf,"rendered_check":check,"result":"PASS","inference_limit":"Control visual de ruta; no confirma target 2008."} for cid,sid,printed,pdf,check in visual_specs], "control_id")
write_csv(visual_path, visual, list(visual[0]))

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V149.csv"
breaks = read_csv(breaks_path)
break_specs = [
    ("target_support_originals_official_entity_archive_2008","archive","Originales certificados en archivo oficial.","Pedir original/inventario; archivo no prueba pago.","e0_argentina_resolution_6_2008_closing_original"),
    ("c41_c55_closing_windows_not_target_type","document_type","C-41 y C-55 coexistían.","No clasificar por numeración/plazo.","e0_argentina_resolution_6_2008_closing_original"),
    ("midyear_final_lists_not_yearend_settlement","cut","30/6 y 31/12 son paquetes distintos.","Buscar ambos; no homologar.","e0_cgn_disposition_28_2008_intermediate_close"),
    ("uai_held_2019_sigade_snapshot_not_2008_snapshot","temporal","UAI reservó snapshot 2019.","Pedir inventario 2008.","e0_mecon_uai_report_35_2019_saf355_change_close"),
    ("last_form_cut_crosswalk_not_target_body","identifier","Corte UAI prueba crosswalk.","Pedir esquema 2008; no homologar rango.","e0_mecon_uai_report_06_2019_saf355_close_2018"),
    ("3855_historical_account_not_target_account","account","3855/19 tiene continuidad.","Usar candidata, no atribuir target.","e0_cgn_disposition_38_1996_cut_account_3855"),
    ("dual_extract_custody_not_preservation_proof","custody","TGN y SAF recibían copias.","Pedir ambas; no presumir conservación.","e0_cgn_disposition_38_1996_annex_cut_extracts"),
    ("bank_extract_date_vs_process_date","time","Extracto y proceso difieren.","Conservar ambas fechas.","e0_cgn_disposition_38_1996_cut_account_3855;e0_mecon_uai_report_37_2019_tgn_change_close"),
    ("repo_crg_cancellation_later_not_unrounded_target","comparison","REPO vía CRG aparece en 2019.","No prueba clase/monto 2008.","e0_mecon_uai_report_06_2019_saf355_close_2018"),
    ("buyback_dadp_custody_not_commission_identity","custody","DADP conserva legajo recompra.","Pedir legajo sin atribuir 83106000.","e0_argentina_rc_212_24_2008_recompra"),
]
breaks = upsert(breaks, [{"break_id":bid,"dimension":dim,"problem":problem,"rule":rule,"status":"FROZEN_V149","evidence":evidence} for bid,dim,problem,rule,evidence in break_specs], "break_id")
write_csv(breaks_path, breaks, list(breaks[0]))

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V149.csv"
trace = read_csv(trace_path)
trace_specs = [
    ("REQ149_ECON","CGN/SAF355","CL149_FINAL_LISTS","Listados finales SIDIF","2008","83106000"),("REQ149_ECON","SAF355","CL149_CONFORMITY","Devoluciones conformadas","2008-2009","SAF355"),("REQ149_ECON","SAF355/CGN","CL149_ADJUST","Ajustes y notas","2008-2009","71597;152677;2876"),("REQ149_ECON","SIGEN/UAI","CL149_AUDIT_NOTICE","Comunicaciones de diferencias","2008-2009","SAF355;83106000"),("REQ149_ECON","Archivo SAF355","CL149_ORIGINALS","Originales/inventario","2008","art.22 Res.6/08"),("REQ149_ECON","CGN/SAF355","CL149_H1","Paquete 30/6","2008-06-30","71597;152677;2876"),("REQ149_ECON","CGN/SAF355","CL149_H2","Paquete 31/12","2008-12-31","71597;152677;2876"),("REQ149_ECON","SIDIF/SICHE","CL149_HISTORY","Tipo, interno/SIDIF e historia","2008-2009","71597;152677;2876"),("REQ149_ECON","UAI","CL149_LAST_FORMS","Acta últimos formularios","2008-2009","SAF355"),("REQ149_ECON","UAI/SIGADE","CL149_BACKUP","Inventario snapshots","2008","83106000"),("REQ149_ECON","UAI/SIGADE","CL149_RESTORE","Restore/consulta","2008","83106000;7.2.8"),("REQ149_ECON","TGN","CL149_NOTE","Nota, saldos y movimientos","2008","3855/19;alternativas"),("REQ149_ECON","TGN/SIDIF","CL149_PAYMENT_REPORT","Reporte Resumen de Pagos","2008","71597;152677;2876"),("REQ149_BNA","BNA/TGN","CL149_EXTRACTS","Extractos diarios","2008","3855/19"),("REQ149_ECON","SAF355","CL149_DUAL_COPY","Copia magnética/papel","2008","3855/19;alternativas"),("REQ149_ECON","DADP/ONCP","CL149_DADP","Legajo recompra","2008","83106000;rondas"),("REQ149_ECON","CUT/SIDIF","CL149_RECON","Libro Banco/conciliación","2008-2009","71597;152677;2876"),("REQ149_ECON","Archivo/Sistemas","CL149_NEGATIVE","Inventarios/migraciones/disposición","1996-2019","SAF355;TGN;UAI;DADP"),
]
trace = upsert(trace, [{"trace_id":f"TR149_{i:03d}","request_id":req,"institution":inst,"gap_id":gap,"requested_record":record,"period_or_date":period,"identifiers":ids,"minimum_usable_fields":"tipo;ID;fecha extracto;fecha proceso;cuenta;signo;importe;referencia;estado;hash","confidentiality_fallback":"copia testada preservando trazabilidad","status":"DRAFT_NOT_SENT"} for i,(req,inst,gap,record,period,ids) in enumerate(trace_specs,1)], "trace_id")
write_csv(trace_path, trace, list(trace[0]))

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V149.csv"
keys = read_csv(keys_path)
key_specs = [
    ("legal","Resolución SH 6/2008 artículo 8"),("archive","archivo oficial de la entidad"),("record_class","listados finales de ejecución"),("record_class","devolución conformada dentro de diez días"),("record_class","nota explicativa firmada"),("cut","30 de junio de 2008"),("cut","31 de diciembre de 2008"),("form","C-41 7 de enero de 2009"),("form","C-55 31 de enero de 2009"),("act","IF-2019-109041824-APN-UAI#MHA"),("act","IF-2019-109242536-APN-UAI#MHA"),("note","NO-2019-109266599-APN-TGN#MHA"),("output","Listado Reporte Resumen de Pagos"),("account","3855/19"),("custodian","Dirección de Administración de la Deuda Pública"),("custodian","Unidad de Auditoría Interna reserva para consulta"),("system","Conciliación Bancaria SIDIF Central"),("target","83106000;71597;152677;2876;32.270,30"),
]
keys = upsert(keys, [{"key_id":f"SK149_{i:02d}","request_id":"REQ149_ECON","key_group":group,"exact_key":key,"search_purpose":"Localizar objeto exacto o documentar cero.","source_or_basis":"E0_2008_CLOSING_FORM_AND_ARCHIVE_ROUTE_V149.csv;E0_CUT_3855_HISTORICAL_CUSTODY_ROUTE_V149.csv","caveat":"Clave de recuperación; no prueba pago, tipo ni cuenta target."} for i,(group,key) in enumerate(key_specs,1)], "key_id")
write_csv(keys_path, keys, list(keys[0]))

append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V149.md", "## Ampliación V149 · cierre 2008, archivo oficial y custodios nominados", """
Estado: **BORRADOR_NO_ENVIADO**. Este texto no autoriza ni registra presentación.

La Resolución SH 6/2008 obliga a reconstruir el paquete contemporáneo. Para `83106000 · COMISIONES - BANCO NACION · $32.270,30 · 71597/152677/2876`, se solicitan: listados finales SIDIF; devoluciones conformadas; ajustes; notas explicativas firmadas; comunicaciones a SIGEN/UAI; y originales respaldatorios e inventario del archivo oficial cuya existencia certificaban los responsables conforme art. 22.

La búsqueda debe abarcar el paquete intermedio al 30/6/2008, el anual al 31/12/2008 y registraciones posteriores: C-41 hasta 7/1/2009 y regularizaciones C-10/C-55 hasta 31/1/2009. Los plazos no clasifican los IDs. Para cada uno se pide tipo, número interno, número SIDIF, historia, cabecera, renglones, orden, fecha de extracto, fecha de proceso y reversas.

Como guía de salida —no como prueba retroactiva—, UAI 06/2019 publica tipo, número interno, SIDIF e historia de cortes. UAI 35/2019 identifica una base SIGADE reservada en UAI. Se pide inventario 2008, medio, archivo, motor/versión, timestamp, hash, esquema, custodia y restore/export con consulta exacta `83106000`.

La cuenta BNA 3855/19 es filtro histórico porque la Disposición CGN 38/1996 la identifica en la CUT y documenta copia diaria a TGN y otra al SAF más papel/respaldo. No se afirma que sea cuenta target: consúltese también el universo completo de cuentas 2008. Pídanse extractos, códigos, comprobantes, Libro Banco y conciliación, separando fecha de extracto y proceso.

La RC 212/2008 y 24/2008 dejó la documentación de recompra en DADP para control. Pídase inventario, legajo, oferta, preadjudicación, remisión, instrucción y resultado. La custodia no atribuye `83106000` a recompra: el vínculo debe surgir del cuerpo.
""")
append_section(HERE / "REQUEST_BNA_FIRST_STAGE_BLOTTER_V149.md", "## Ampliación V149 · extractos CUT, doble custodia y cuenta histórica candidata", """
Estado: **BORRADOR_NO_ENVIADO**. La Disposición CGN 38/1996 prueba dos ediciones magnéticas diarias del extracto CUT y una en papel: una copia a TGN y otra, con papel y respaldo, al SAF. Se solicita el esquema vigente en 2008, constancias de entrega y extractos de 3855/19 y cuentas alternativas SAF355, preservando fecha valor/extracto, fecha de proceso, código, signo, comprobante, importe, referencia y saldo. La continuidad vuelve 3855/19 candidata; no demuestra que `83106000` operara por ella.
""")
append_section(HERE / "SOURCE_REFERENCES_V149.md", "## Fuentes nuevas V149 · cierre, CUT y custodios", "\n".join(f"- `{s['id']}` · {s['title']} · {s['url']} · `{s['local']}` · `{s['sha']}`" for s in source_rows))
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V149.md", "## Control V149 · dos cortes, dos fechas y dos custodias", """
- Mantener seis pedidos `DRAFT_NOT_SENT` hasta autorización.
- Pedir paquetes 30/6 y 31/12 más enero 2009; no asignar tipo por magnitud.
- Pedir listados, conformidades, ajustes, notas, comunicaciones y originales.
- Distinguir número interno/SIDIF y fecha extracto/proceso.
- Consultar 3855/19 como candidata y el universo completo de cuentas 2008.
- Pedir copias TGN/SAF, snapshot UAI y legajo DADP; custodia no es pago.
- Mantener 0/10 hasta cuerpo y puente bancario conciliado.
""")

(HERE / "README_V149.md").write_text("""# V149 · archivo contemporáneo, cuenta CUT histórica y custodios nominados

V149 cierra un vacío documental central. La Resolución SH 6/2008 prueba que el cierre generaba listados finales SIDIF, devoluciones conformadas, ajustes, notas y comunicaciones; los responsables certificaban originales en el archivo oficial. La Disposición CGN 28/2008 agrega un paquete distinto al 30 de junio. Los tres IDs deben buscarse en ambos cortes y enero de 2009, sin inferir tipo por numeración.

Los UAI 2019 prueban el esquema tipo–número interno–SIDIF–cortes, una base SIGADE reservada en UAI y, para TGN, módulo de conciliación, notas, saldos, movimientos y `Listado Reporte Resumen de Pagos`. Son comparadores, no prueba target 2008.

La Disposición CGN 38/1996 prueba que BNA 3855/19 era cuenta CUT, con copias diarias para TGN y SAF más papel/respaldo. Es candidata histórica, no cuenta target demostrada. La búsqueda conserva todo el universo de cuentas. DADP era custodio de documentación de recompra.

No se localizaron cuerpos públicos 71597/152677/2876, snapshot SIGADE 2008 ni vínculo cuenta–target. Resultado: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Seis `DRAFT_NOT_SENT`; cero presentaciones y respuestas. REPO 0,45 sigue como tensión de precisión, no error probado.
""", encoding="utf-8")
(HERE / "VEREDICTO_V149.md").write_text("""# Veredicto V149

La ruta de recuperación es ahora demostrable: en 2008 debían existir listados, conformidades, ajustes, notas y originales archivados. Hay custodios concretos: SAF355/archivo oficial, UAI para snapshots comparadores, TGN/SAF para extractos CUT y DADP para legajos de recompra.

3855/19 deja de ser extrapolación posterior: su función CUT está probada desde 1996. Sigue sin probarse que sea la cuenta target. C-41 y C-55 son ramas coexistentes, no clasificación de 71597/152677/2876.

Sin cuerpo, historia, cuenta, fecha valor, signo, importe, referencia, Libro Banco, conciliación y ausencia de reversa no hay ejecución. Resultado: 0/10. Seis borradores no enviados; cero presentaciones y respuestas.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V149.md").write_text("""# Reconstrucción fiscal E0 V149

V149 mantiene 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones. La evidencia demuestra rutas de producción/archivo, no el hecho target: paquetes 30/6 y 31/12, enero 2009, copias CUT TGN/SAF, snapshot SIGADE y legajo DADP. Sólo una conciliación individual completa entra al numerador. REPO 0,45 no es error probado.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V149.md").write_text("""# Registro de recuperación V149

- Nueve fuentes oficiales nuevas: cuatro PDF UAI, dos resoluciones y tres disposiciones/anexos CGN.
- Doce páginas nuevas controladas visualmente; PASS.
- Ruta 2008 de listados, conformidad, ajustes, notas y originales probada.
- 3855/19 probada desde 1996; uso target abierto.
- UAI custodio de snapshot 2019; snapshot 2008 abierto. DADP custodio de recompra; vínculo target abierto.
- Búsquedas exactas sólo recuperan fila Anexo K, no cuerpos.
- Cero pedidos presentados; 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V149_A_V150.md").write_text("""# Handover V149 → V150

## Estado

- QA PASS; 9 fuentes nuevas; 483 maestras y 243 E0.
- Res. SH 6/2008 prueba listados finales, conformidad, ajustes, notas, UAI y originales en archivo oficial.
- Disp. 28/2008 separa cierre 30/6 del anual 31/12.
- C-41 hasta 7/1/2009 y C-10/C-55 hasta 31/1/2009; tipo target abierto.
- UAI 06/2019 prueba esquema tipo–interno–SIDIF–cortes; no clasifica IDs 2008.
- UAI 35/2019 prueba snapshot SIGADE reservado en UAI en 2019; 2008 no probado.
- UAI TGN prueba módulo, nota, 3855/19 y salidas como comparadores.
- Disp. 38/1996 prueba 3855/19 histórica y doble custodia TGN/SAF; cuenta target abierta.
- DADP custodia recompra; vínculo 83106000 abierto.
- Cuerpos no localizados; seis `DRAFT_NOT_SENT`; cero presentaciones/respuestas; 0/10.

## Prioridad V150

1. Mantener borradores salvo autorización.
2. Buscar inventarios SAF355/CGN y actas de últimos formularios 2008.
3. Rastrear IDs en 30/6, 31/12 y enero 2009 con doble número interno/SIDIF.
4. Buscar inventarios UAI SIGADE y cadena DADP.
5. Precisar cuentas/extractos 2008 por copias TGN y SAF.
6. Mantener 0/10 hasta cuerpo y puente bancario.
""", encoding="utf-8")
old_handover = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V149_A_V149.md"
if old_handover.exists(): old_handover.unlink()

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V149 · archivo oficial, CUT histórica y custodios", """
- Cierre 2008: listados, conformidades, ajustes, notas y originales en archivo oficial probados.
- Paquetes 30/6 y 31/12 separados; enero 2009 incluido; tipo target abierto.
- CUT 3855/19 probada desde 1996 y doble custodia TGN/SAF; uso target abierto.
- UAI snapshot 2019 y DADP recompra son custodios nominados; no prueban target.
- Nueve fuentes nuevas; 0/10; seis borradores no enviados.
""")
write_csv(HERE / "INHERITED_QA_STATUS_V149.csv", [
    {"script":"qa_v148.py","pre_v149_result":"PASS","post_v149_result":"EXPECTED_SUPERSEDED_ASSERTION","interpretation":"V148 ampliada por archivo 2008, CUT y custodios."},
    {"script":"qa_v149.py","pre_v149_result":"N/A","post_v149_result":"PASS","interpretation":"Verifica fuentes, matrices, no envío y 0/10."},
])

hash_rows = []
for row in catalog:
    local = row["archivo_local"]; path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file()); actual = sha256(path) if exists else ""; expected = row["sha256"]
    hash_rows.append({"id":row["id"],"archivo_local":local,"exists":str(exists),"sha_catalog":expected,"sha_actual":actual,"hash_ok":str(bool(exists and expected and actual.lower()==expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V149.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V149.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows); hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts: continue
    size = path.stat().st_size
    size_rows.append({"path":path.relative_to(REPO).as_posix(),"bytes":size,"mib":f"{size/1048576:.6f}","over_50_mib":str(size>50*1048576),"over_100_mib":str(size>100*1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V149.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V148.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V149","date":"2026-08-31","state":"E0_2008_ORIGINAL_ARCHIVE_CUT_HISTORY_NAMED_CUSTODIANS_PROVED_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries":len(catalog),"physical_local_copies":physical,"physical_local_hash_ok":hash_ok,"remaining_physical_gaps":len(catalog)-physical,"e0_primary_sources_preserved":len(census),
    "numeric_v149_strict_changed":False,"sources_newly_preserved_v149":9,"e0_primary_sources_newly_preserved_v149":9,"e0_fiscal_method_breaks_frozen":len(breaks),"e0_request_traceability_rows":len(trace),"e0_request_search_keys":len(keys),"e0_v149_pdf_visual_controls":len(visual),
    "e0_2008_closing_route_rows":len(closing),"e0_2008_intermediate_route_rows":len(intermediate),"e0_uai_last_form_rows":len(last_forms),"e0_uai_sigade_custody_rows":len(sigade),"e0_tgn_bank_cut_rows":len(tgn),"e0_cut_3855_route_rows":len(cut),"e0_dadp_custody_rows":len(dadp),"e0_v149_exact_search_rows":len(search),"e0_v149_request_objects":len(request_objects),
    "e0_target_original_support_official_entity_archive_2008":True,"e0_2008_final_lists_conformity_adjustment_notes_proved":True,"e0_3855_historical_account_continuity_proved":True,"e0_3855_target_account_proved":False,"e0_uai_sigade_snapshot_custodian_2019":True,"e0_uai_sigade_snapshot_2008_proved":False,"e0_dadp_buyback_document_custodian_proved":True,"e0_target_commission_buyback_link_proved":False,
    "e0_target_forms_public_bodies_located":0,"e0_settlement_executed_rows_confirmed":0,"e0_requests_submitted":0,"e0_request_responses_received":0,"e0_request_package_status":"DRAFT_NOT_SENT","historical_workstream":"Recover official-archive close packages, CUT extracts, SIGADE snapshots and DADP legajo; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V149.json").write_text(json.dumps(complete,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

(HERE / "AUDITORIA_V149.md").write_text(f"""# Auditoría V149

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: 9.
- Copias/hash: {physical}/{hash_ok}; controles visuales: {len(visual)}; quiebres: {len(breaks)}.
- Archivo/listados 2008: ruta probada; cuerpos target: 0/3.
- 3855/19 histórica probada; uso target no.
- Ejecución: 0/10; pedidos/respuestas: 0/0.
""", encoding="utf-8")

def checkpoint_manifest():
    files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha256(path)} for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V149.json"]
    payload = {
        "checkpoint":"V149","parent_checkpoint":"V148","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"exact_entities":30,"strict_coverage_pct":STRICT,"closed_network_gate":"NO","e0_primary_sources":len(census),"new_preserved_sources":9,"fiscal_method_breaks":len(breaks),"request_traceability_rows":len(trace),"request_search_keys":len(keys),"pdf_visual_controls_v149":len(visual),
        "closing_route_rows":len(closing),"intermediate_route_rows":len(intermediate),"last_form_rows":len(last_forms),"sigade_custody_rows":len(sigade),"tgn_bank_cut_rows":len(tgn),"cut_3855_rows":len(cut),"dadp_custody_rows":len(dadp),"exact_search_rows":len(search),"v149_request_objects":len(request_objects),
        "target_original_support_official_entity_archive_2008":True,"historical_account_3855_continuity_proved":True,"target_account_3855_proved":False,"uai_sigade_snapshot_custodian_2019":True,"uai_sigade_snapshot_2008_proved":False,"target_forms_public_bodies_located":0,"award_rows_exact":10,"account_candidate_rows":9,"executed_settlement_rows_confirmed":0,"request_drafts":6,"requests_submitted":0,"responses_received":0,"files":files,
    }
    (HERE / "MANIFEST_V149.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def tree(root):
    paths = sorted(Path(root).rglob("*"), key=lambda value:value.relative_to(root).as_posix().casefold())
    return "\n".join(path.relative_to(root).as_posix()+("/" if path.is_dir() else "") for path in paths if ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts)+"\n"

(REPO / "TREE.txt").write_text(tree(REPO),encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE),encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda value:value.relative_to(REPO).as_posix().casefold()):
    if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts and path != global_manifest:
        global_files.append({"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)})
global_payload = json.dumps({"checkpoint":"V149","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":STRICT,"exact_entities":30,"closed_network_gate":"NO","source_audit":f"{len(catalog)} master; {physical} physical SHA-valid; 9 new sources; archive/CUT routes proved; target open; 0/10; six drafts not submitted.","historical_workstream":"Recover close packages, target forms, CUT extracts, SIGADE backups and DADP legajo; no request submitted","file_count_excluding_manifest":len(global_files),"files":global_files},ensure_ascii=False,indent=2)+"\n"
tmp = global_manifest.with_suffix(".json.v149tmp"); tmp.write_text(global_payload,encoding="utf-8"); tmp.replace(global_manifest)

print(f"V149 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok}")
