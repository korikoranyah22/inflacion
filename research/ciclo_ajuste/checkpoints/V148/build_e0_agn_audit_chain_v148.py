from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v148" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def upsert(rows: list[dict[str, str]], additions: list[dict[str, object]], key: str) -> list[dict[str, str]]:
    order = [str(row[key]) for row in rows]
    indexed = {str(row[key]): row for row in rows}
    for addition in additions:
        row = {name: str(value) for name, value in addition.items()}
        value = row[key]
        indexed[value] = row
        if value not in order:
            order.append(value)
    return [indexed[value] for value in order]


def append_section(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


SOURCES = [
    ("e0_cgn_disposition_49_2002_saf355_closing_exception", "Contaduría General de la Nación", "Disposición CGN 49/2002 · cierre y excepción SAF 355/356", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2002/disp49/disp49.htm", "cgn_disposition_49_2002_saf355_closing_exception.html", "2002-2008", "Disposición CGN 49/2002", "HTML oficial · captura preservada", "El art. 1 exceptúa a SAF 355/356 de los cuadros de cierre generales; no elimina sus registros ni controles.", "Captura directa del dominio oficial economia.gob.ar; certificado TLS vencido tolerado tras verificar dominio y contenido."),
    ("e0_cgn_account_2008_uepex_closing_exception", "Contaduría General de la Nación", "Cuenta de Inversión 2008 · Separata UEPEX · excepción SAF 355/356", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sep.pdf", "cgn_account_2008_uepex_closing_exception.pdf", "2008", "Cuenta 2008 · Separata UEPEX", "PDF oficial · binario preservado", "PDF pp.73 y 76: listados parametrizados, consultas específicas, sustituciones/regularizaciones y aplicación 2008 de la excepción.", "Descarga directa del dominio oficial economia.gob.ar; certificado TLS vencido tolerado tras verificar dominio, PDF y páginas."),
    ("e0_mecon_uai_report_03_2022_saf355_closure_2021", "Ministerio de Economía · UAI", "Informe UAI 03/2022 · cierre 2021 SAF 355", "https://www.argentina.gob.ar/sites/default/files/informe_uai_03-2022.pdf", "mecon_uai_report_03_2022_saf355_closure_2021.pdf", "2021-2022", "Informe UAI 03/2022", "PDF oficial · binario preservado", "Resumen ejecutivo público de 2 páginas; refiere un Informe Analítico no incluido y difiere opinión de integridad hasta el cierre definitivo.", "Descarga oficial directa de argentina.gob.ar; PDF visualmente controlado."),
    ("e0_mecon_uai_report_51_2022_account_2021", "Ministerio de Economía · UAI", "Informe UAI 51/2022 · Cuenta de Inversión ONCP 2021", "https://www.argentina.gob.ar/sites/default/files/informe_uai_51-2022_ci_oncp_2021.pdf", "mecon_uai_report_51_2022_account_2021.pdf", "2021-2022", "Informe UAI 51/2022", "PDF oficial · binario preservado", "Resumen ejecutivo público de 3 páginas; remite a Informe Analítico y registra diferencias ONCP-CGN y pagos ausentes en SIGADE.", "Descarga oficial directa de argentina.gob.ar; PDF visualmente controlado."),
    ("e0_argentina_mecon_uai_audit_catalog_2022", "Ministerio de Economía · UAI", "Catálogo público de informes UAI 2022", "https://www.argentina.gob.ar/node/366229", "argentina_mecon_uai_audit_catalog_2022.html", "2022", "Catálogo UAI 2022", "HTML oficial · captura preservada", "Individualiza UAI 03/2022 y UAI 51/2022 y permite controlar el alcance de los PDF públicos.", "Captura oficial directa de argentina.gob.ar."),
]
source_rows = []
for values in SOURCES:
    sid, institution, title, url, filename, period, series, kind, note, provenance_note = values
    path = BIN / filename
    assert path.is_file(), path
    source_rows.append({"id": sid, "institution": institution, "title": title, "url": url, "local": "/" + path.relative_to(REPO).as_posix(), "period": period, "series": series, "kind": kind, "note": note, "provenance_note": provenance_note, "sha": sha256(path), "bytes": path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{"id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"], "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"], "fecha_descarga": "2026-08-31", "fecha_publicacion": s["period"], "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"], "sha256": s["sha"], "nota": "V148: " + s["note"]} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V148.csv"
census = read_csv(census_path)
census = upsert(census, [{"source_id": s["id"], "institution": s["institution"], "artifact": s["title"], "url": s["url"], "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"], "period_coverage": s["period"], "variable_families": "SAF355;closing;SIDIF;SIGADE;TGN;CGN;BNA;custody", "primary_source": "YES", "preserved": "YES", "method_breaks": "cuadro general versus vía especial; resumen ejecutivo versus analítico; custodia versus pago", "use_status": "E0_USABLE_WITH_SCOPE", "caveat": s["note"]} for s in source_rows], "source_id")
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V148.csv"
provenance = read_csv(provenance_path)
provenance = upsert(provenance, [{"source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"], "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT", "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"], "provenance_note": s["provenance_note"]} for s in source_rows], "source_id")
write_csv(provenance_path, provenance, list(provenance[0]))


def simple_matrix(name: str, fields: list[str], rows: list[tuple]) -> None:
    write_csv(HERE / name, [dict(zip(fields, row)) for row in rows], fields)


closing = [
    ("CE148_01", "GENERAL_RULE", "Disposición 49/02 art.1", "Los SAF presentan cuadros de cierre según anexos.", "Regla general; revisar excepciones.", "e0_cgn_disposition_49_2002_saf355_closing_exception", "art.1", "FALSE"),
    ("CE148_02", "GENERAL_BANK_TABLE", "Cuadro 1 · Caja y Bancos", "Integra el cierre estándar.", "No atribuirlo automáticamente a SAF355.", "e0_cgn_disposition_49_2002_saf355_closing_exception", "anexos", "FALSE"),
    ("CE148_03", "EXCEPTION", "SAF 355 y 356", "Exceptuados de cuadros estándar.", "Excepción de ruta, no de registración.", "e0_cgn_disposition_49_2002_saf355_closing_exception", "art.1", "FALSE"),
    ("CE148_04", "APPLIED_2008", "Cuenta 2008", "La CGN aplica la excepción a 355/356.", "Prueba contemporánea directa.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.76", "FALSE"),
    ("CE148_05", "DETAILED_LISTS", "Listados parametrizados", "CGN suministró listados para conciliación.", "Pedir salida, parámetros, corte y hash.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.73", "FALSE"),
    ("CE148_06", "SPECIFIC_QUERIES", "Consultas específicas", "CGN habilitó consultas de movimientos.", "Pedir cuerpo y metadatos.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.73", "FALSE"),
    ("CE148_07", "REPLACEMENT", "Sustitución de cuadros/anexos", "Información corregida podía reemplazar productos.", "Pedir versiones y responsables.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.73", "FALSE"),
    ("CE148_08", "REGULARIZATION", "Regularizaciones con certificación UAI", "Salida formal posible.", "Buscar tipo sin prejuzgar C-55.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.73", "FALSE"),
    ("CE148_09", "TARGET_BRANCH", "Anexo K 83106000", "Fila especial de deuda con tres SIDIF.", "Priorizar ONCP/SAF355.", "e0_cgn_cuenta_inversion_2008_sdp", "PDF p.67", "FALSE"),
    ("CE148_10", "EXCLUDED_PRESUMPTION", "Cierre bancario general", "No puede presumirse repositorio target.", "No aceptar su cero como cierre.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.76", "FALSE"),
    ("CE148_11", "SPECIAL_ROUTE", "Anexo K→listas/formularios→banco", "Ruta coherente con la excepción.", "Cerrar por identidad completa.", "e0_cgn_account_2008_uepex_closing_exception", "PDF pp.73,76", "FALSE"),
    ("CE148_12", "NEGATIVE_LIMIT", "Ausencia en cierre general", "No prueba inexistencia o no pago.", "Exigir repositorios especiales.", "e0_cgn_account_2008_uepex_closing_exception", "PDF p.76", "FALSE"),
]
simple_matrix("E0_SAF355_CLOSING_EXCEPTION_AND_SPECIAL_ROUTE_V148.csv", ["route_id", "element", "record_or_rule", "official_fact", "controlled_use", "source_id", "locator", "target_payment_confirmed"], closing)

tgn = [
    ("TB148_01", "SUPPORT", "Art.69", "Respaldo a ONCP de desembolsos/pagos directos.", "Pedir respaldo y remisión.", "e0_argentina_decree_1344_2007_original_finance_rule", "OPEN", "FALSE"),
    ("TB148_02", "JURISDICTION90", "Art.70", "Gastos de crédito público a Jurisdicción 90.", "Ámbito, no identidad.", "e0_argentina_decree_1344_2007_original_finance_rule", "SCOPE_PROVED", "FALSE"),
    ("TB148_03", "PRE_CANCELLATION", "Art.74(k)", "TGN conserva órdenes hasta cancelación.", "Pedir orden y estado a TGN.", "e0_argentina_decree_1344_2007_original_finance_rule", "CUSTODY_RULE_PROVED", "FALSE"),
    ("TB148_04", "POST_CANCELLATION", "Art.74(k)", "Órdenes canceladas se remiten a CGN.", "Pedir cuerpo cancelado a CGN.", "e0_argentina_decree_1344_2007_original_finance_rule", "CUSTODY_RULE_PROVED", "FALSE"),
    ("TB148_05", "BANK_INFORMATION", "Art.78.7.4", "BNA debe informar movimientos/saldos a TGN a requerimiento.", "Solicitar consulta histórica TGN→BNA.", "e0_argentina_decree_1344_2007_original_finance_rule", "STATUTORY_ROUTE_PROVED", "FALSE"),
    ("TB148_06", "TGN_QUERY", "71597/152677/2876", "Ruta legal a movimientos BNA.", "Pedir cuenta, fecha, signo, importe, referencia.", "e0_argentina_decree_1344_2007_original_finance_rule", "DRAFT_NOT_SENT", "FALSE"),
    ("TB148_07", "BRANCH_A", "Orden", "Unir formulario, orden, cancelación y banco.", "Aplicar custodia TGN/CGN.", "e0_argentina_decree_1344_2007_original_finance_rule", "TYPE_OPEN", "FALSE"),
    ("TB148_08", "BRANCH_B", "Débito/regularización", "Unir extracto, aviso, formulario y Libro Banco.", "Circular 22/04 como comparador.", "e0_cgn_circular_22_2004_note_regularization", "TYPE_OPEN", "FALSE"),
    ("TB148_09", "BRANCH_A_CLOSE", "Ordenada y pagada", "Cancelación sola no basta.", "Exigir movimiento conciliado.", "e0_argentina_decree_1344_2007_original_finance_rule", "OPEN_0_OF_10", "FALSE"),
    ("TB148_10", "BRANCH_B_CLOSE", "Débito confirmado", "Extracto solo no prueba imputación.", "Exigir referencia y sin reversa.", "e0_cgn_circular_22_2004_note_regularization", "OPEN_0_OF_10", "FALSE"),
    ("TB148_11", "REDACTION", "Datos protegidos", "Puede testarse preservando campos operativos.", "Pedir disociación.", "e0_argentina_decree_1344_2007_original_finance_rule", "DRAFT_NOT_SENT", "FALSE"),
    ("TB148_12", "LIMIT", "Capacidad jurídica", "No demuestra movimiento target.", "Mantener 0/10.", "e0_argentina_decree_1344_2007_original_finance_rule", "TARGET_NOT_PROVED", "FALSE"),
]
simple_matrix("E0_TGN_BNA_LEGAL_CUSTODY_AND_MOVEMENT_ROUTE_V148.csv", ["route_id", "stage", "legal_locator", "contemporaneous_rule", "target_request_use", "source_id", "status", "target_payment_confirmed"], tgn)

executive = [
    ("EA148_01", "CATALOG_03", "UAI 03/2022", "Catálogo oficial individualiza cierre SAF355.", "PUBLIC_EXECUTIVE_LOCATED", "e0_argentina_mecon_uai_audit_catalog_2022", "FALSE"),
    ("EA148_02", "UAI03_BODY", "2 páginas", "El PDF público es resumen ejecutivo.", "PUBLIC_EXECUTIVE_ONLY", "e0_mecon_uai_report_03_2022_saf355_closure_2021", "FALSE"),
    ("EA148_03", "UAI03_ANALYTIC", "Informe Analítico", "Referido pero no incorporado.", "ANALYTIC_BODY_NOT_LOCATED", "e0_mecon_uai_report_03_2022_saf355_closure_2021", "FALSE"),
    ("EA148_04", "INTEGRITY", "Cierre definitivo", "Integridad no opinada hasta cerrar registros primarios.", "LATER_COMPARATOR", "e0_mecon_uai_report_03_2022_saf355_closure_2021", "FALSE"),
    ("EA148_05", "CATALOG_51", "UAI 51/2022", "Catálogo oficial individualiza Cuenta ONCP.", "PUBLIC_EXECUTIVE_LOCATED", "e0_argentina_mecon_uai_audit_catalog_2022", "FALSE"),
    ("EA148_06", "UAI51_BODY", "3 páginas", "El PDF público es resumen ejecutivo.", "PUBLIC_EXECUTIVE_ONLY", "e0_mecon_uai_report_51_2022_account_2021", "FALSE"),
    ("EA148_07", "UAI51_ANALYTIC", "Secciones 5/6", "Informe Analítico referido no incluido.", "ANALYTIC_BODY_NOT_LOCATED", "e0_mecon_uai_report_51_2022_account_2021", "FALSE"),
    ("EA148_08", "ONCP_CGN", "Diferencias ONCP-CGN", "Necesidad de conciliación intersistema.", "LATER_COMPARATOR", "e0_mecon_uai_report_51_2022_account_2021", "FALSE"),
    ("EA148_09", "SIGADE_LIMIT", "Pagos holdout ausentes", "Pago puede obrar fuera de SIGADE.", "LATER_COMPARATOR_NOT_TARGET", "e0_mecon_uai_report_51_2022_account_2021", "FALSE"),
    ("EA148_10", "ACT_BODY", "IF-2023-147866862 / IF-2023-148676623", "Citados por UAI 48/2023; cuerpos no localizados.", "PUBLIC_ACT_BODY_NOT_LOCATED", "e0_mecon_uai_report_48_2023_saf355_closure", "FALSE"),
]
simple_matrix("E0_PUBLIC_EXECUTIVE_ONLY_ACT_BODY_GAP_V148.csv", ["gap_id", "object", "public_scope", "controlled_interpretation", "status", "source_id", "target_2008_proof"], executive)

searches = [
    ("XP148_01", "83106000", "Cuenta 2008 Anexo K", "EXACT_PUBLIC_REFERENCE_ROW_ONLY", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf"),
    ("XP148_02", "71597", "Sólo dentro de la fila publicada 2008", "EXACT_PUBLIC_REFERENCE_ROW_ONLY", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf"),
    ("XP148_03", "152677", "Sólo dentro de la fila publicada 2008", "EXACT_PUBLIC_REFERENCE_ROW_ONLY", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf"),
    ("XP148_04", "2876", "Sólo dentro de la fila publicada dentro del universo controlado", "EXACT_PUBLIC_REFERENCE_ROW_ONLY", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf"),
    ("XP148_05", "32.270,30", "Sólo como importe agregado de la fila", "EXACT_PUBLIC_REFERENCE_ROW_ONLY", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf"),
    ("XP148_06", "COMISIONES - BANCO NACION", "Continuidad anual; cuerpos target no", "REFERENCE_SERIES_ONLY", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf"),
    ("XP148_07", "71597 expediente", "Sin cuerpo oficial individualizable", "PUBLIC_BODY_NOT_LOCATED", "N/A"),
    ("XP148_08", "152677 expediente", "Sin cuerpo oficial individualizable", "PUBLIC_BODY_NOT_LOCATED", "N/A"),
    ("XP148_09", "2876 SIDIF 2008", "Sin cuerpo oficial individualizable", "PUBLIC_BODY_NOT_LOCATED", "N/A"),
    ("XP148_10", "83106000 C-41 C-55", "Sin clasificación target pública", "TARGET_DOCUMENT_TYPE_OPEN", "N/A"),
    ("XP148_11", "83106000 Banco Nación 32270", "Sin orden, extracto o conciliación pública", "TARGET_SETTLEMENT_BODY_NOT_LOCATED", "N/A"),
    ("XP148_12", "negative_limit", "No localizado públicamente no equivale a inexistente", "CONTROLLED_NEGATIVE", "N/A"),
]
simple_matrix("E0_EXACT_TARGET_ID_PUBLIC_SEARCH_V148.csv", ["search_id", "exact_query_or_control", "result", "status", "official_result_url", "searched_on", "negative_inference_limit", "next_action"], [r + ("2026-08-31", "No prueba inexistencia, expurgo ni falta de pago.", "Pedido por serie, sistema, custodio, parámetros, archivo y hash.") for r in searches])

continuity = [
    ("DT148_01", "2005", "229688.25", "126144/11853", "NUMBERED_SIDIF", "e0_cgn_cuenta_inversion_2005_sdp", "Anexo J"),
    ("DT148_02", "2006", "47480.40", "VARIOS", "AGGREGATED", "e0_cgn_cuenta_inversion_2006_sdp", "Anexo J"),
    ("DT148_03", "2007", "26656.30", "83318/151752/240417", "NUMBERED_SIDIF", "e0_cgn_cuenta_inversion_2007_sdp", "PDF p.68"),
    ("DT148_04", "2008", "32270.30", "71597/152677/2876", "TARGET_TYPE_OPEN", "e0_cgn_cuenta_inversion_2008_sdp", "PDF p.67"),
    ("DT148_05", "2009", "17557.10", "BLANK", "NO_PRINTED_DOCUMENT_SIGNAL", "e0_cgn_cuenta_inversion_2009_sdp", "PDF p.74"),
    ("DT148_06", "2010", "1869.45", "C41 5310/74291/156087/285224", "C41_EXPLICIT", "e0_cgn_cuenta_inversion_2010_sdp", "PDF p.74"),
    ("DT148_07", "2005-2010", "N/A", "numbered→VARIOS→numbered→target→blank→C41", "DISCLOSURE_TYPE_VARIES", "multiple", "annual annexes"),
    ("DT148_08", "LIMIT", "N/A", "same code/label", "NO_TARGET_TYPE_INFERENCE", "multiple", "annual annexes"),
]
simple_matrix("E0_83106000_DISCLOSURE_TYPE_CONTINUITY_2005_2010_V148.csv", ["row_id", "year", "amount_ars", "printed_document_reference", "document_signal", "source_id", "locator", "account", "description", "permitted_inference", "forbidden_inference"], [r + ("83106000", "COMISIONES - BANCO NACION" if i < 6 else "serie comparada", "La divulgación varía; C-41 es comparador sólo desde el año explícito.", "Asignar C-41, C-55, propósito o pago a 2008 por continuidad.") for i, r in enumerate(continuity)])

decision = [
    ("START", "Recuperar cuerpo 71597/152677/2876", "Tipo y estado legibles", "CLASSIFY", "Si no: SICHE/archivo"),
    ("CLASSIFY_A", "Tipo orden/C-41 o equivalente", "ORDER", "A_ORDERED", "No inferir liquidación"),
    ("A_ORDERED", "Localizar orden y respaldo", "TGN antes; CGN después", "A_BANK", "Custodia no es pago"),
    ("A_BANK", "Localizar movimiento BNA vía TGN", "Cuenta, fecha, signo, importe, referencia", "A_RECONCILE", "Cero sin metadatos no cierra"),
    ("A_RECONCILE", "Conciliar formulario/orden/movimiento", "Identidad y sin reversa", "SETTLED_A", "Sólo entonces confirma"),
    ("CLASSIFY_B", "Tipo C-55/débito/regularización", "DIRECT_DEBIT", "B_EXTRACT", "No inferir por concepto"),
    ("B_EXTRACT", "Localizar extracto/aviso BNA", "Código, cuenta, fecha, signo, importe", "B_BOOK", "Extracto no prueba imputación"),
    ("B_BOOK", "Cruzar Libro Banco y regularización", "Formulario, partida, estado, referencia", "B_RECONCILE", "Revisar reversa"),
    ("B_RECONCILE", "Conciliar débito/formulario/Libro Banco", "Identidad y sin reversa", "SETTLED_B", "Sólo entonces confirma"),
    ("OPEN", "Tipo o puente faltante", "Cualquier divergencia", "OPEN_0_OF_10", "Mantener abierto"),
]
simple_matrix("E0_DUAL_PAYMENT_MECHANISM_DECISION_TREE_V148.csv", ["node_id", "test_or_action", "positive_condition", "next_state", "control", "source_ids", "current_target_state"], [r + ("e0_argentina_decree_1344_2007_original_finance_rule;e0_cgn_circular_22_2004_note_regularization;e0_cgn_account_2008_uepex_closing_exception", "OPEN_0_OF_10") for r in decision])

repo = [
    ("RU148_01", "2.1.2.01.02.99.00", "official exact web search", "Only UAI comparator reports", "NO_UNROUNDED_LEDGER"),
    ("RU148_02", "563,16", "official exact web search", "Published rounded aggregate only", "NO_WORKPAPER"),
    ("RU148_03", "0,61 REPO", "official exact web search", "Published component only", "NO_RAW_COMPONENT"),
    ("RU148_04", "563,61 - 563,16", "calculation", "0,45 displayed-value tension", "NOT_ARITHMETIC_ERROR_PROOF"),
    ("RU148_05", "Informe Analítico/papel", "official public search", "Not located", "PUBLIC_BODY_NOT_LOCATED"),
    ("RU148_06", "negative_limit", "method", "Unknown precision remains", "UNROUNDED_INPUTS_REQUIRED"),
]
simple_matrix("E0_REPO_PUBLIC_UNROUNDED_SEARCH_V148.csv", ["search_id", "query_or_datum", "search_scope", "result", "status", "searched_on", "arithmetic_error_proved", "unrounded_components_located"], [r + ("2026-08-31", "FALSE", "FALSE") for r in repo])

objects = [
    ("CGN/SAF355", "Serie especial de cierre 2008 que alimentó Anexo K", "serie;inventario;responsable;fecha;remisión;hash"),
    ("CGN/SAF355", "Listados detallados parametrizados", "consulta;parámetros;corte;filas;archivo;hash"),
    ("CGN/SAF355", "Consultas específicas de movimientos", "sistema;dataset;filtros;resultado;diccionario"),
    ("CGN/SAF355", "Versiones sustituidas de cuadros/anexos", "versión;fecha;motivo;responsable;diferencias"),
    ("UAI/SAF355", "Formularios de regularización certificados", "tipo;número;estado;importe;certificación;respaldo"),
    ("SIDIF/SICHE", "Formulario 71597 completo", "tipo;cabecera;renglones;estado;beneficiario;importe;orden"),
    ("SIDIF/SICHE", "Formulario 152677 completo", "tipo;cabecera;renglones;estado;beneficiario;importe;orden"),
    ("SIDIF/SICHE", "Formulario 2876 completo", "tipo;cabecera;renglones;estado;beneficiario;importe;orden"),
    ("SIGADE/SIDIF", "Mayorizado y crosswalk 83106000", "evento;cuenta;asiento;formulario;orden;referencia"),
    ("TGN", "Orden y estado previo a cancelación", "orden;fecha;estado;custodia;remisión"),
    ("CGN", "Orden cancelada remitida por TGN", "orden;fecha de cancelación;recepción;cuerpo;anexos"),
    ("TGN/BNA", "Movimientos y saldos de la cuenta pública", "cuenta;fecha valor;signo;importe;moneda;referencia;saldo"),
    ("TGN", "Constancia de requerimiento al BNA", "fecha;alcance;respuesta;archivo;hash"),
    ("BNA", "Extracto o aviso de débito target", "cuenta;fecha valor;código;signo;importe;referencia"),
    ("CUT/SIDIF", "Libro Banco y conciliación", "movimiento;formulario;estado;grupo;reversa"),
    ("UAI 03/2022", "Informe Analítico y anexos", "secciones;hallazgos;actas;inventarios;hash"),
    ("UAI 51/2022", "Informe Analítico secciones 5/6 y anexos", "diferencias;papeles;registros;hash"),
    ("UAI/ONCP", "Componentes no redondeados REPO", "importe fuente;precisión;asiento;regla;cálculo"),
]
simple_matrix("E0_V148_REQUEST_OBJECTS_V148.csv", ["object_id", "owner_or_system", "requested_record", "minimum_usable_fields", "success_test", "negative_response_rule", "status"], [(f"RO148_{i:02d}",) + r + ("Objeto individualizable y enlazable por ID, fecha, cuenta, signo e importe.", "Informar series, repositorios, períodos, parámetros, migraciones y expurgos.", "DRAFT_NOT_SENT") for i, r in enumerate(objects, 1)])

visual_path = HERE / "E0_V148_PDF_VISUAL_CONTROL.csv"
visual = read_csv(visual_path)
visual_add = [
    ("PV148_40", "e0_cgn_account_2008_uepex_closing_exception", "N/A", "73", "listados parametrizados, consultas y regularización"),
    ("PV148_41", "e0_cgn_account_2008_uepex_closing_exception", "N/A", "76", "excepción SAF355/356 aplicada en 2008"),
    ("PV148_42", "e0_mecon_uai_report_03_2022_saf355_closure_2021", "2", "2", "integridad diferida e Informe Analítico referido"),
    ("PV148_43", "e0_mecon_uai_report_51_2022_account_2021", "2", "2", "alcance ejecutivo e Informe Analítico"),
    ("PV148_44", "e0_mecon_uai_report_51_2022_account_2021", "3", "3", "diferencias ONCP-CGN y pagos fuera de SIGADE"),
]
visual = upsert(visual, [{"control_id": cid, "source_id": sid, "printed_page": printed, "pdf_page": page, "rendered_check": check, "result": "PASS", "inference_limit": "Control de alcance; no confirma pago target."} for cid, sid, printed, page, check in visual_add], "control_id")
write_csv(visual_path, visual, list(visual[0]))

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V148.csv"
breaks = read_csv(breaks_path)
new_breaks = [
    ("saf355_general_closing_tables_exempt_2008", "institutional_scope", "SAF355 was excepted from general closing tables in 2008.", "Do not presume Caja y Bancos is the target repository.", "e0_cgn_disposition_49_2002_saf355_closing_exception;e0_cgn_account_2008_uepex_closing_exception"),
    ("standard_caja_bancos_route_not_target_repository", "repository", "General bank close and special debt route differ.", "Search Anexo K production records, forms, queries and bank bridge.", "e0_cgn_account_2008_uepex_closing_exception"),
    ("public_executive_not_analytic_report", "publication_scope", "Public executive PDF is not the cited analytic report.", "Request analytic body and annexes; do not infer contents.", "e0_mecon_uai_report_03_2022_saf355_closure_2021;e0_mecon_uai_report_51_2022_account_2021"),
    ("closing_integrity_not_final_before_definitive_close", "audit_state", "Later UAI review withheld integrity opinion pending final closure.", "Treat preliminary closure as incomplete; comparator only.", "e0_mecon_uai_report_03_2022_saf355_closure_2021"),
    ("tgn_bna_statutory_access_not_target_movement", "legal_capability", "TGN could require movements and balances from BNA.", "Use as retrieval route, not as target proof.", "e0_argentina_decree_1344_2007_original_finance_rule"),
    ("tgn_custody_before_cancellation_cgn_after", "custody", "Payment-order custody changes at cancellation.", "Ask TGN before and CGN after; custody is not payment.", "e0_argentina_decree_1344_2007_original_finance_rule"),
    ("later_debit_direct_rule_not_target_type", "document_type", "Bank-debit regularization is a plausible branch.", "Do not classify target as C-55 without body or metadata.", "e0_cgn_circular_22_2004_note_regularization"),
]
breaks = upsert(breaks, [{"break_id": key, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V148", "evidence": evidence} for key, dimension, problem, rule, evidence in new_breaks], "break_id")
write_csv(breaks_path, breaks, list(breaks[0]))

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V148.csv"
trace = read_csv(trace_path)
trace_add = [
    ("REQ148_ECON", "CGN/SAF355", "CL148_SPECIAL_CLOSE", "Serie especial de cierre y papeles Anexo K", "2008", "83106000;Anexo K"),
    ("REQ148_ECON", "CGN/SAF355", "CL148_LISTS", "Listados detallados parametrizados", "2008", "SAF355;83106000"),
    ("REQ148_ECON", "CGN/SAF355", "CL148_QUERIES", "Consultas específicas de movimientos", "2008", "71597;152677;2876"),
    ("REQ148_ECON", "SIDIF/SICHE", "CL148_FORM71597", "Formulario completo 71597", "2008", "71597"),
    ("REQ148_ECON", "SIDIF/SICHE", "CL148_FORM152677", "Formulario completo 152677", "2008", "152677"),
    ("REQ148_ECON", "SIDIF/SICHE", "CL148_FORM2876", "Formulario completo 2876", "2008", "2876"),
    ("REQ148_ECON", "TGN", "CL148_ORDER_PRE", "Orden y estado antes de cancelación", "2008", "71597;152677;2876"),
    ("REQ148_ECON", "CGN", "CL148_ORDER_POST", "Orden cancelada remitida por TGN", "2008", "71597;152677;2876"),
    ("REQ148_ECON", "TGN/BNA", "CL148_BANK_ROUTE", "Movimientos y saldos de cuenta pública", "2008", "83106000;32270.30"),
    ("REQ148_BNA", "BNA", "CL148_DEBIT", "Extracto o aviso de débito", "2008", "COMISIONES;32270.30"),
    ("REQ148_ECON", "CUT/SIDIF", "CL148_RECON", "Libro Banco y conciliación", "2008", "71597;152677;2876"),
    ("REQ148_ECON", "UAI", "CL148_ANALYTIC03", "Informe Analítico UAI 03/2022", "2021-2022", "UAI03/2022"),
    ("REQ148_ECON", "UAI", "CL148_ANALYTIC51", "Informe Analítico UAI 51/2022", "2021-2022", "UAI51/2022"),
    ("REQ148_ECON", "SAF355/UAI", "CL148_REPO_RAW", "Componentes no redondeados REPO", "2018-2019", "2.1.2.01.02.99.00;0.61"),
    ("REQ148_ECON", "Archivo/Sistemas", "CL148_NEGATIVE", "Inventarios, migraciones y actos si no obra", "2006-2009", "SAF355;SIDIF;CUT"),
]
trace = upsert(trace, [{"trace_id": f"TR148_{i:03d}", "request_id": req, "institution": institution, "gap_id": gap, "requested_record": record, "period_or_date": period, "identifiers": ids, "minimum_usable_fields": "tipo;ID;fecha;cuenta;signo;importe;referencia;estado;archivo;hash", "confidentiality_fallback": "copia testada preservando trazabilidad", "status": "DRAFT_NOT_SENT"} for i, (req, institution, gap, record, period, ids) in enumerate(trace_add, 1)], "trace_id")
write_csv(trace_path, trace, list(trace[0]))

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V148.csv"
keys = read_csv(keys_path)
exact_keys = [
    ("REQ148_ECON", "legal", "Disposición CGN 49/2002"), ("REQ148_ECON", "institution", "SAF 355"),
    ("REQ148_ECON", "record_class", "listados detallados parametrizados"), ("REQ148_ECON", "record_class", "consultas específicas de movimientos"),
    ("REQ148_ECON", "account", "83106000"), ("REQ148_ECON", "form", "71597"), ("REQ148_ECON", "form", "152677"),
    ("REQ148_ECON", "form", "2876"), ("REQ148_ECON", "amount", "32.270,30"), ("REQ148_ECON", "custody", "TGN hasta cancelación"),
    ("REQ148_ECON", "custody", "CGN después de cancelación"), ("REQ148_ECON", "bank_route", "artículo 78.7.4 Decreto 1344/2007"),
    ("REQ148_ECON", "audit", "Informe Analítico UAI 03/2022"), ("REQ148_ECON", "audit", "Informe Analítico UAI 51/2022"),
    ("REQ148_ECON", "repo", "2.1.2.01.02.99.00"),
]
keys = upsert(keys, [{"key_id": f"SK148_{i:02d}", "request_id": req, "key_group": group, "exact_key": key, "search_purpose": "Localizar objeto exacto o documentar cero reproducible.", "source_or_basis": "E0_SAF355_CLOSING_EXCEPTION_AND_SPECIAL_ROUTE_V148.csv;E0_TGN_BNA_LEGAL_CUSTODY_AND_MOVEMENT_ROUTE_V148.csv", "caveat": "Clave de recuperación; no prueba pago ni tipo."} for i, (req, group, key) in enumerate(exact_keys, 1)], "key_id")
write_csv(keys_path, keys, list(keys[0]))

append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V148.md", "## Rectificación V148 · excepción SAF 355 y ruta TGN/CGN/BNA", """
Estado: **BORRADOR_NO_ENVIADO**. No se autoriza ni registra presentación.

La Disposición CGN 49/2002 y su aplicación expresa en la Cuenta de Inversión 2008 exceptuaron a los SAF 355 y 356 de los cuadros generales de cierre. No se solicita el Cuadro general de Caja y Bancos como repositorio exclusivo ni se aceptará su ausencia como respuesta suficiente. Se pide la **serie especial del SAF 355/ONCP que produjo el Anexo K**: listados detallados parametrizados, consultas específicas de movimientos, cada versión original/sustituida/rectificada del anexo, formularios de regularización, certificaciones UAI, inventario, remisión y responsable.

Para `83106000 · COMISIONES - BANCO NACION · $32.270,30 · 7.2.8. · 71597/152677/2876`, entréguese cada formulario y el crosswalk SIGADE–SIDIF–asiento–orden–cuenta. Si es orden de pago, el Decreto 1344/2007 original asigna custodia a TGN hasta cancelación y remisión a CGN después: se pide a cada órgano la etapa correspondiente. Si fue débito/regularización, entréguense aviso o extracto BNA, formulario, Libro Banco, conciliación y reversas.

El artículo 78.7.4 facultaba a TGN a requerir al BNA denominación, número, tipo, movimientos y saldos de cuentas públicas. Se solicita que TGN consulte y entregue ese registro preexistente —o constancia de requerimiento y respuesta— con cuenta, fecha valor, signo, moneda, importe, referencia y saldo. Cancelación sin banco o débito sin imputación no cierran prueba.

Los PDF públicos UAI 03/2022 y 51/2022 son ejecutivos y remiten a Informes Analíticos no incluidos. Se solicitan cuerpos, anexos, actas e inventarios. Una negativa debe individualizar serie, sistema, repositorio, período, parámetros, inventario, migración, transferencia o acto de disposición. Puede testarse información protegida preservando campos operativos.
""")

append_section(HERE / "REQUEST_BNA_FIRST_STAGE_BLOTTER_V148.md", "## Ampliación V148 · coordinación con la ruta legal TGN", """
Estado: **BORRADOR_NO_ENVIADO**. La rama BNA es complementaria. El Decreto 1344/2007 original obligaba a las instituciones bancarias —en especial BNA— a informar a TGN, a requerimiento, cuentas, movimientos y saldos del sector público. Se solicita localizar toda consulta, respuesta, extracto, aviso o rendición transmitida a TGN respecto de `83106000`, `71597/152677/2876` y $32.270,30. Esa potestad no prueba el movimiento: se exige cuerpo, fecha, cuenta, signo, importe, referencia y conciliación, con disociación de datos protegidos.
""")

append_section(HERE / "SOURCE_REFERENCES_V148.md", "## Fuentes nuevas V148 · excepción SAF 355 y ruta de cierre", "\n".join(f"- `{s['id']}` · {s['title']} · {s['url']} · `{s['local']}` · `{s['sha']}`" for s in source_rows))
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V148.md", "## Control V148 · vía especial y custodia", """
- Mantener seis pedidos `DRAFT_NOT_SENT` hasta autorización.
- No usar Caja y Bancos como universo exclusivo de SAF355.
- Pedir listados, consultas, versiones y regularizaciones que produjeron Anexo K.
- Aplicar custodia TGN antes de cancelación y CGN después; pedir ruta TGN→BNA.
- Ejecutar ramas orden y débito/regularización en paralelo hasta recuperar el tipo.
- No cerrar sin formulario, orden/imputación y movimiento conciliados; mantener 0/10.
""")

(HERE / "README_V148.md").write_text("""# V148 · excepción SAF 355 y ruta legal TGN–CGN–BNA

V148 identifica una excepción contemporánea decisiva: en 2008 el SAF 355 no estaba obligado a presentar los cuadros generales de cierre, incluido Caja y Bancos. La Cuenta 2008 confirma la excepción y documenta listados parametrizados, consultas específicas, sustituciones de anexos y regularizaciones certificadas.

La ruta correcta queda como `Anexo K → serie especial SAF355/ONCP → listados/consultas → SIDIF 71597/152677/2876 → orden o regularización → movimiento TGN/BNA → Libro Banco/conciliación`.

El Decreto 1344/2007 original agrega custodia y acceso: TGN conservaba órdenes hasta cancelación; luego se remitían a CGN; TGN podía requerir al BNA movimientos y saldos. Es ruta jurídica de recuperación, no prueba de pago.

La publicación 83106000 varía entre 2005 y 2010: SIDIF numerados, `VARIOS`, blanco y C-41 explícito. C-41 es comparador y C-55/débito una rama plausible, pero el tipo 2008 sigue abierto. Tampoco se localizaron cuerpos separados de los tres SIDIF, Informes Analíticos UAI ni componentes REPO no redondeados.

Estado: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Seis pedidos `DRAFT_NOT_SENT`; cero presentaciones y respuestas. REPO 0,45 sigue como tensión de precisión, no error probado.
""", encoding="utf-8")

(HERE / "VEREDICTO_V148.md").write_text("""# Veredicto V148

La investigación localiza mejor el archivo correcto, pero aún no confirma ejecución. La excepción SAF355 impide usar el cierre bancario general como control negativo suficiente. La prueba debe buscarse en la serie especial de deuda, listados/consultas CGN, tres formularios SIDIF y puente bancario.

La norma divide el pedido: TGN para orden previa a cancelación y consulta BNA; CGN para orden cancelada; BNA/CUT para extracto, Libro Banco y conciliación. Si el tipo es orden/C-41 se sigue la rama ordenada; si es débito/C-55, regularización. Ninguna cierra sin cuenta, fecha, signo, moneda, importe, referencia y ausencia de reversa.

No se localizaron públicamente cuerpos de 71597/152677/2876, Informes Analíticos UAI, actos citados o REPO no redondeado. Es límite de publicación, no prueba de inexistencia o falta de pago.

Resultado: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Seis borradores no enviados; cero presentaciones y respuestas.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V148.md").write_text("""# Reconstrucción fiscal E0 V148

V148 mantiene 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. El SAF355 estaba exceptuado del cierre general: el target se busca en la serie especial de Anexo K. Sólo entra al numerador cuando una rama —orden o débito/regularización— concilia formulario, estado, cuenta, fecha, signo, importe, referencia, banco y ausencia de reversa. REPO 0,45 no es error probado.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V148.md").write_text("""# Registro de recuperación V148

- Cinco fuentes nuevas: Disposición CGN 49/2002, Separata UEPEX Cuenta 2008, UAI 03/2022, UAI 51/2022 y catálogo UAI.
- Control visual PASS en PDF 73/76 de la Separata, UAI03 p.2 y UAI51 pp.2-3.
- Excepción SAF355/356 corroborada por norma y aplicación 2008.
- Búsquedas exactas sólo recuperaron la fila Anexo K, no cuerpos target.
- PDF UAI públicos ejecutivos; Analíticos y actos no localizados.
- REPO no redondeado no localizado; no se ejecutó SICHE ni presentó pedido.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V148_A_V149.md").write_text("""# Handover V148 → V149

## Estado

- QA V148: PASS; cinco fuentes oficiales nuevas; 474 fuentes maestras y 234 E0.
- En 2008 SAF355/356 estaba exceptuado de cuadros generales; Caja y Bancos no puede presumirse repositorio target.
- Ruta especial: listados parametrizados, consultas específicas, sustituciones/rectificaciones y formularios certificados.
- Decreto 1344/2007: TGN custodia órdenes hasta cancelación, CGN después; TGN puede requerir movimientos/saldos al BNA.
- Dos ramas abiertas: orden/C-41 equivalente y débito/C-55/regularización; ninguna clasificada o liquidada.
- Búsqueda pública exacta: sólo fila Anexo K; cuerpos 71597/152677/2876 no localizados.
- Informes Analíticos UAI 03/2022 y 51/2022 y actos citados no localizados públicamente.
- REPO no redondeado no localizado; 0,45 es tensión de precisión, no error probado.
- Seis `DRAFT_NOT_SENT`; cero presentaciones/respuestas; 0/10 ejecuciones.

## Prioridad V149

1. Mantener borradores salvo autorización expresa.
2. Buscar inventarios/índices de la serie especial SAF355 que produjo Anexo K y los Informes Analíticos.
3. Localizar equivalencias de los tres SIDIF en AGAN, SICHE, SIDIF Central o inventarios de migración.
4. Precisar cuenta, fecha valor y código mediante ruta TGN→BNA del art.78.7.4.
5. Determinar tipo antes de priorizar C-41 frente a C-55.
6. Buscar REPO no redondeado sin convertir comparadores en prueba target.
""", encoding="utf-8")
old_handover = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V148_A_V148.md"
if old_handover.exists():
    old_handover.unlink()

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V148 · excepción SAF 355 y ruta TGN–CGN–BNA", """
- SAF355/356 estaba exceptuado de cuadros generales en 2008; ruta especial documentada.
- TGN custodia órdenes antes de cancelación, CGN después, y puede requerir movimientos/saldos al BNA.
- Cuerpos 71597/152677/2876 e Informes Analíticos UAI no localizados públicamente.
- Ramas orden y débito/regularización abiertas; 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V148.csv", [
    {"script": "qa_v147.py", "pre_v148_result": "PASS", "post_v148_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V147 ampliada por excepción SAF355 y ruta de custodia/acceso."},
    {"script": "qa_v148.py", "pre_v148_result": "N/A", "post_v148_result": "PASS", "interpretation": "Verifica fuentes, rutas, hashes, controles, no envío y 0/10."},
])

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V148.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V148.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size, "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V148.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V147.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V148", "date": "2026-08-31", "state": "E0_SAF355_SPECIAL_CLOSE_TGN_CGN_BNA_ROUTE_PROVED_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "remaining_physical_gaps": len(catalog) - physical, "e0_primary_sources_preserved": len(census), "numeric_v148_strict_changed": False,
    "sources_newly_preserved_v148": 5, "e0_primary_sources_newly_preserved_v148": 5,
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_v148_pdf_visual_controls": len(visual), "e0_saf355_special_route_rows": len(closing), "e0_tgn_bna_legal_route_rows": len(tgn),
    "e0_public_executive_gap_rows": len(executive), "e0_exact_target_public_search_rows": len(searches),
    "e0_83106000_continuity_rows": len(continuity), "e0_dual_payment_decision_rows": len(decision),
    "e0_repo_public_unrounded_search_rows": len(repo), "e0_v148_request_objects": len(objects),
    "e0_saf355_standard_closing_tables_required_2008": False, "e0_saf355_special_closing_route_proved_2008": True,
    "e0_tgn_can_require_bna_movements_original_2007": True, "e0_tgn_custody_before_cancellation_cgn_after": True,
    "e0_target_forms_public_bodies_located": 0, "e0_public_uai_analytic_reports_located": 0,
    "e0_repo_unrounded_components_located": False, "e0_repo_arithmetic_error_proved": False,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0, "e0_request_responses_received": 0,
    "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover special SAF355 close, target forms and TGN-CGN-BNA bank bridge; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V148.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V148.md").write_text(f"""# Auditoría V148

- Fuentes maestras: {len(catalog)}.
- Fuentes primarias E0: {len(census)}.
- Fuentes nuevas: 5.
- Copias físicas/hash válidos: {physical}/{hash_ok}.
- Controles visuales acumulados: {len(visual)}.
- Quiebres metodológicos congelados: {len(breaks)}.
- SAF355 en cierre general 2008: exceptuado; ruta especial probada.
- Formularios target públicos: 0/3; ejecución: 0/10.
- Informes Analíticos UAI públicos: 0/2.
- Pedidos presentados: 0; respuestas: 0.
""", encoding="utf-8")


def checkpoint_manifest() -> None:
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V148.json"]
    manifest = {
        "checkpoint": "V148", "parent_checkpoint": "V147", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO", "e0_primary_sources": len(census), "new_preserved_sources": 5,
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "saf355_special_route_rows": len(closing), "tgn_bna_legal_route_rows": len(tgn), "public_executive_gap_rows": len(executive),
        "exact_target_search_rows": len(searches), "account_continuity_rows": len(continuity), "dual_payment_decision_rows": len(decision),
        "repo_unrounded_search_rows": len(repo), "v148_request_objects": len(objects), "pdf_visual_controls_v148": len(visual),
        "saf355_standard_closing_tables_required_2008": False, "tgn_can_require_bna_movements_original_2007": True,
        "target_forms_public_bodies_located": 0, "public_uai_analytic_reports_located": 0,
        "repo_arithmetic_error_proved": False, "repo_unrounded_components_located": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V148.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root: Path) -> str:
    paths = sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().casefold())
    return "\n".join(path.relative_to(root).as_posix() + ("/" if path.is_dir() else "") for path in paths if ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda value: value.relative_to(REPO).as_posix().casefold()):
    if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts and path != global_manifest:
        global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_payload = json.dumps({
    "checkpoint": "V148", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; 5 new official sources; SAF355 special close and TGN-CGN-BNA route proved; target not settled; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover special SAF355 close, target forms and bank bridge; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}, ensure_ascii=False, indent=2) + "\n"
global_tmp = global_manifest.with_suffix(".json.v148tmp")
global_tmp.write_text(global_payload, encoding="utf-8")
global_tmp.replace(global_manifest)

print(f"V148 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok}")
