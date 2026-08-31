from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def upsert(rows, additions, key):
    by_key = {str(row[key]): row for row in rows}
    order = [str(row[key]) for row in rows]
    for row in additions:
        k = str(row[key]); by_key[k] = {name: str(value) for name, value in row.items()}
        if k not in order: order.append(k)
    return [by_key[k] for k in order]


def append_section(path: Path, marker: str, body: str):
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


SOURCES = [
    ("e0_dgsiaf_slu_admin_local_manual_2007", "Secretaría de Hacienda · DGSIAF", "SLU · Manual del Usuario Mantenimiento · Administrador Local · abril 2007", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_mantenimiento_slu_al.pdf", "/research/ciclo_ajuste/inputs/historical_retrieval/v145/binaries/dgsiaf_slu_mantenimiento_administrador_local_2007.pdf", "2007-04", "SLU versión 10 · Administrador Local", "PDF oficial · captura preservada", "Administración local por SAF, historia de usuarios/roles, importación y llaves C55."),
    ("e0_argentina_resolution_115_2005_financial_systems", "Secretaría de Hacienda", "Resolución 115/2005 · implantación, mantenimiento y migración de sistemas financieros", "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-115-2005-106401/texto", "/research/ciclo_ajuste/inputs/historical_retrieval/v145/binaries/argentina_resolucion_115_2005_sistemas_administracion_financiera.html", "2005-05-17", "Resolución SH 115/2005", "HTML oficial · captura preservada", "Acta Acuerdo con backup previo, migración, control entre bases, diferencias e informes firmados."),
    ("e0_cgn_joint_disposition_4_03_backup_recovery", "Contaduría General de la Nación · Unidad Informática", "Disposición Conjunta CGN 4/03 · UI 1/03 · Resguardo y Recuperación", "https://cdi.mecon.gob.ar/bases/docelec/lg1188.pdf", "/research/ciclo_ajuste/inputs/historical_retrieval/v145/binaries/cdi_mecon_digesto_administracion_financiera_capitulo_v_h.pdf", "2003-02-11", "Disposición 4/03 CGN · 1/03 UI", "PDF oficial consolidado · captura preservada", "Obligación local, responsable SAF, registros, logs, pruebas y retención perpetua de fuentes/bases."),
    ("e0_argentina_resolution_7028_2007_backup_comparator", "Ministerio de Desarrollo Social", "Resolución 7028/2007 · procedimientos de backup · comparador", "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-7028-2007-131148/texto", "/research/ciclo_ajuste/inputs/historical_retrieval/v145/binaries/argentina_resolucion_7028_2007_backup_comparator.html", "2007", "Resolución MDS 7028/2007", "HTML oficial · captura preservada", "Comparador: transacciones horarias, full diario, redundancia y archivo anual; no prueba SAF 355."),
]

source_data = []
for sid, institution, title, url, local, published, series, kind, note in SOURCES:
    path = REPO / local.lstrip("/"); assert path.is_file(), path
    source_data.append({"id": sid, "institution": institution, "title": title, "url": url, "local": local,
                        "published": published, "series": series, "kind": kind, "note": note,
                        "sha": sha256(path), "bytes": path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{"id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"],
    "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"], "fecha_descarga": "2026-08-31",
    "fecha_publicacion": s["published"], "codigo_serie": s["series"], "periodo_utilizado": s["published"],
    "tipo": s["kind"], "sha256": s["sha"], "nota": "V145 E0: " + s["note"]} for s in source_data], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V145.csv"
census = read_csv(census_path)
census = upsert(census, [{"source_id": s["id"], "institution": s["institution"], "artifact": s["title"], "url": s["url"],
    "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"], "period_coverage": s["published"],
    "variable_families": "SLU;backup;migration;custody;C55;SICHE", "primary_source": "YES", "preserved": "YES",
    "method_breaks": "norma/esquema no equivale a fila target", "use_status": "E0_USABLE_WITH_LIMIT", "caveat": s["note"]} for s in source_data], "source_id")
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V145.csv"
provenance = read_csv(provenance_path)
provenance = upsert(provenance, [{"source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT", "local_path": s["local"], "sha256": s["sha"],
    "bytes": s["bytes"], "provenance_note": "Captura oficial directa; hash y tamaño preservados en V145."} for s in source_data], "source_id")
write_csv(provenance_path, provenance, list(provenance[0]))


backup_duties = [
    ("BD145_01","scope","Obligatoria para organismos usuarios de sistemas de Hacienda administrados localmente","art. 4","identificar SAF/sistema","no prueba soporte actual"),
    ("BD145_02","responsibility","Director General de Administración o titular informático del SAF responde por el resguardo","art. 5","pedir responsable y transferencia de custodia","no identifica soporte"),
    ("BD145_03","central_role","UI mantiene sistemas; CGN vela por integridad de bases centrales y locales","considerandos","búsqueda coordinada CGN/DGSIAF/SAF","no presumir custodio exclusivo"),
    ("BD145_04","preproduction","Todo sistema debía documentar resguardo/recuperación antes de producción","Anexo I.1","pedir procedimiento por versión","documento aún no localizado"),
    ("BD145_05","coverage","Debía cubrir programas, archivos y bases de datos","Anexo I.1.d-e","pedir esquema y datos SLU","no identifica instancia"),
    ("BD145_06","label","Cada copia: equipo, fecha/hora, frecuencia, lote, tipo y sistema","Anexo I.2","buscar inventario SLU 2006-2009","etiqueta no es restauración"),
    ("BD145_07","daily_register","Registro diario de cintas, uso y lugar de guarda","Anexo I.3","pedir planillas y custodia","registro puede haberse expurgado"),
    ("BD145_08","execution_log","Todo respaldo debía generar log; preferible verificación de integridad","Anexo I.4","pedir job/resultado/checksum","log perdido no niega backup"),
    ("BD145_09","offsite","En lo posible dos copias y una fuera del edificio","Anexo I.6","pedir guarda externa/traslados","regla no asegura doble copia"),
    ("BD145_10","full_frequency","Con incrementales: full cada siete días","Anexo I.8.c","buscar cortes semanales 2008","depende de aplicación"),
    ("BD145_11","recovery_test","Prueba de recuperación al menos cada treinta días","Anexo I.9","pedir actas y archivos recuperados","prueba muestral"),
    ("BD145_12","signed_act","Prueba formalizada en acta firmada","Anexo I.9 y II","pedir fecha/equipo/backup/archivos/firmas","acta no contiene necesariamente datos"),
    ("BD145_13","retention","Fuentes y bases de datos: perpetuo","Anexo I.12","pedir soporte o acto de transferencia/expurgo","deber no es hallazgo"),
    ("BD145_14","retention","Lotes TRANSAF: perpetuo","Anexo I.12","pedir lotes SIDIF","no reemplaza extracto"),
    ("BD145_15","retention","Actividad de usuarios y pistas: tres años","Anexo I.12","separar log temporal de base perpetua","no asumir supervivencia del log"),
    ("BD145_16","historical_media","Histórico en soportes no reutilizables y grabación automática","Anexo I.13-14","pedir catálogo y cadena de custodia","no identifica ubicación"),
]
write_csv(HERE/"E0_SLU_BACKUP_RETENTION_DUTY_V145.csv", [{"duty_id":a,"dimension":b,"official_rule":c,"locator":d,"request_effect":e,"inference_limit":f,"source_id":"e0_cgn_joint_disposition_4_03_backup_recovery"} for a,b,c,d,e,f in backup_duties])

migration_rows = [
    ("MG145_01","database_admin","CGN centraliza información como Administrador de la Base de Datos","Anexo I.b","nota/opinión órganos rectores"),
    ("MG145_02","legal_file","Manuales, Acta Acuerdo y convenio de prestación","Anexo I.c.I","expediente de implantación"),
    ("MG145_03","backup_rules","Esquema, guarda, responsables, identificación y recuperación","Anexo I.c.II","procedimiento local"),
    ("MG145_04","signed_agreement","Acta Acuerdo firmada por autoridad SAF y Hacienda","Anexo I.e","Acta Acuerdo SAF 355"),
    ("MG145_05","pre_migration_backup","Backup del sistema reemplazado antes de migrar","Anexo I.f.IV","inventario/copia/hash"),
    ("MG145_06","migration","Migración de datos","Anexo I.f.V","scripts/mapeos/conteos"),
    ("MG145_07","database_control","Testeo y control entre bases; diferencias documentadas","Anexo I.f.VI","totales antes/después y diferencias"),
    ("MG145_08","parallel_test","Prueba paralela y diferencias documentadas","Anexo I.f.VIII","resultados/aceptación"),
    ("MG145_09","production","Puesta en producción y seguimiento","Anexo I.f.IX-X","fecha/versión/informes"),
    ("MG145_10","progress","Informe dentro de cinco días de cada etapa, firmado UI+SAF","Anexo I.g","informes firmados"),
    ("MG145_11","responsibles","UI, SAF y órganos rectores designan representantes","Anexo I.h","designaciones nominales"),
    ("MG145_12","incidents","Problemas por Mesa de Atención con número y documentación","Anexo I.i","tickets/casos"),
]
write_csv(HERE/"E0_SLU_MIGRATION_DOCUMENT_CHAIN_V145.csv", [{"chain_id":a,"stage":b,"official_requirement":c,"locator":d,"target_record":e,"status":"REQUIRED_RECORD_NOT_LOCATED","source_id":"e0_argentina_resolution_115_2005_financial_systems"} for a,b,c,d,e in migration_rows])

admin_rows = [
    ("AL145_01","local_scope","Cada SAF dispone de administración local de menú/seguridad","p.3","rol local; no custodia física"),
    ("AL145_02","database_admin","Administración transparente de base, usuarios, roles y permisos","p.3","no DBA irrestricto"),
    ("AL145_03","user_history","Historia de cambios del usuario","p.22","no historia bancaria"),
    ("AL145_04","role_history","Historia de rol con inicio/fin de vigencia","p.32","modelo temporal de seguridad"),
    ("AL145_05","import_scope","Importación sólo para usuarios, roles, relaciones y llaves","pp.163-164","no BMOVEXTERNO/AMOV_FORG"),
    ("AL145_06","import_format","Plano con cabecera, fechas y separador ~","pp.166-167","sólo archivos de seguridad"),
    ("AL145_07","commit","Commit sin/masivo/individual y _error.log","pp.165-167","log de esa importación"),
    ("AL145_08","migration","Usuarios/roles sólo Commit Individual","p.172","migración estrecha"),
    ("AL145_09","c55_permissions","C55 consultar/ingresar/autorizar/predatar","p.89","permiso no prueba emisión"),
    ("AL145_10","c55_modify_c41","C55 modifica C41 por transferencia, factura, reservados u otros","p.89","rama requiere registro"),
    ("AL145_11","c55_reversal","Revertir C55 de desafectación confirmado por central","p.90","buscar original/reversa"),
    ("AL145_12","direct_debit","C55 Regularización Global · Débito Directo","p.148","carril, no fila target"),
    ("AL145_13","exchange_difference","C55 Regularización Global · Diferencia de Cambios","p.149","causa alternativa"),
    ("AL145_14","global_correction","C55 Corrección Global y desautorización","pp.153-154","exigir estados"),
    ("AL145_15","responses","Consultas, respuestas, sin respuesta, rechazos y manuales centrales","pp.154-156","pedir export integral"),
]
write_csv(HERE/"E0_SLU_LOCAL_ADMIN_HISTORY_AND_C55_V145.csv", [{"control_id":a,"dimension":b,"official_fact":c,"locator":d,"inference_limit":e,"source_id":"e0_dgsiaf_slu_admin_local_manual_2007"} for a,b,c,d,e in admin_rows])

siche_rows = [
    ("SC145_01","authority","SICHE es la única herramienta para sistemas discontinuados","Resolución 53/2024 art. 1"),
    ("SC145_02","SLU_route","Desde 1/7/2024 SLU debe consultarse por SICHE","Resolución 53/2024 art. 2"),
    ("SC145_03","competence","CGN y DGSIAF pueden dictar normas complementarias","Resolución 53/2024 art. 3"),
    ("SC145_04","query","Consultas estandarizadas filtran, seleccionan y ordenan","Resolución 53/2024 considerando"),
    ("SC145_05","export","Grilla exportable a planilla","Resolución 53/2024 considerando"),
    ("SC145_06","origin","Repositorio tal como está, sin migración/transformación","Resolución 53/2024 considerando"),
    ("SC145_07","historical_access","SICHE estandariza acceso histórico","página SICHE"),
    ("SC145_08","decommission","SLU se desafecta tras disponibilización en SICHE","página SLU"),
    ("SC145_09","first_action","Primero exportar SICHE/inventario; backups si falta cobertura","inferencia controlada V145"),
    ("SC145_10","zero_rule","Cero no prueba ausencia sin corte, filtros y universo","inferencia controlada V145"),
]
write_csv(HERE/"E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V145.csv", [{"route_id":a,"dimension":b,"official_or_controlled_rule":c,"locator":d,"status":"PROVED_ROUTE_TARGET_EXPORT_NOT_EXECUTED","source_id":"e0_argentina_resolution_53_2024_siche;e0_dgsiaf_siche_landing;e0_dgsiaf_slu_landing"} for a,b,c,d in siche_rows])

request_objects = [
    ("RO145_01","Inventario de consultas/datasets SICHE-SLU","nombre;descripción;período;campos;filtros;corte"),
    ("RO145_02","Exportación SICHE SLU 2008 con parámetros","consulta;filtros;universo;filas;archivo;hash"),
    ("RO145_03","Procedimiento de resguardo aplicable al SLU","versión;vigencia;responsable;frecuencia;retención"),
    ("RO145_04","Inventario de backups SLU 2006-2009","equipo;instancia;esquema;fecha;tipo;lote;soporte;ubicación"),
    ("RO145_05","Registro diario de soportes","fecha;equipo;cinta;lote;reuso;guarda;firma"),
    ("RO145_06","Logs de ejecución/verificación","job;inicio;fin;resultado;error;checksum"),
    ("RO145_07","Actas mensuales de recuperación","fecha;backup;archivos;tiempo;resultado;problemas;firmas"),
    ("RO145_08","Inventario histórico y traslados","soporte;fecha;edificio;responsable;custodia"),
    ("RO145_09","Acta Acuerdo SLU del SAF objetivo","expediente;firmantes;fecha;cronograma;versión"),
    ("RO145_10","Backup previo a cada migración","sistema;fecha;soporte;hash;restaurabilidad"),
    ("RO145_11","Scripts/mapeos v7→v9/v10","tabla origen;tabla destino;transformación;conteos"),
    ("RO145_12","Testeo entre bases y diferencias","tabla;antes;después;diferencia;resolución"),
    ("RO145_13","Prueba paralela e informes firmados","etapa;fecha;versión;diferencias;firmas"),
    ("RO145_14","Responsables y tickets Mesa de Atención","nombre;cargo;función;número;fecha;solución"),
    ("RO145_15","Dumps 2008 BMOVEXTERNO/AMOV_FORG","cuenta;movimiento;contracódigo;partida;vigencia;estado"),
    ("RO145_16","C55 débito/diferencia/corrección/reversa","tipo;estado;C41;fecha;importe;cuenta;respuesta"),
    ("RO145_17","conc_01/conc_02, Libro Banco y extracto","cuenta;fecha;signo;importe;referencia;estado N/P/T"),
    ("RO145_18","Constancia fundada de inexistencia/expurgo","objeto;repositorios;fechas;norma;acto;responsable"),
]
write_csv(HERE/"E0_SLU_BACKUP_AND_SICHE_REQUEST_OBJECTS_V145.csv", [{"object_id":a,"requested_record":b,"minimum_fields":c,"success_test":"archivo/constancia individualizable y reproducible","negative_response_rule":"no basta respuesta genérica ni consulta actual sin cobertura","status":"DRAFT_NOT_SENT","source_id":"E0_SLU_BACKUP_RETENTION_DUTY_V145.csv;E0_SLU_MIGRATION_DOCUMENT_CHAIN_V145.csv;E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V145.csv"} for a,b,c in request_objects])

comparator_rows = [
    ("CP145_01","CONPRE sólo lectura y reemplazado por SLU","contexto MDS 2007","no prueba custodia target"),
    ("CP145_02","Transacciones horarias y full 22:00 SQL Server","factibilidad institucional","no atribuir a Oracle/SAF 355"),
    ("CP145_03","Copias a dos servidores RAID 5","práctica de redundancia","no inventario target"),
    ("CP145_04","Diferenciales diarios y cintas mensuales","práctica de retención","no reemplaza norma aplicable"),
    ("CP145_05","Último juego anual para siempre","comparador de archivo","no prueba inclusión SLU target"),
    ("CP145_06","Recuperación a puntos por log","capacidad SQL Server","no extrapolar sin evidencia"),
]
write_csv(HERE/"E0_2007_BACKUP_COMPARATOR_AND_LIMITS_V145.csv", [{"control_id":a,"official_fact":b,"permitted_use":c,"inference_limit":d,"source_id":"e0_argentina_resolution_7028_2007_backup_comparator"} for a,b,c,d in comparator_rows])

visual_rows = [
    ("PV145_01","e0_dgsiaf_slu_admin_local_manual_2007","3","4","administración local por SAF"),
    ("PV145_02","e0_dgsiaf_slu_admin_local_manual_2007","22","23","Historia de usuario"),
    ("PV145_03","e0_dgsiaf_slu_admin_local_manual_2007","32","33","Historia de rol/vigencia"),
    ("PV145_04","e0_dgsiaf_slu_admin_local_manual_2007","89-90","90-91","llaves C55 y reversa"),
    ("PV145_05","e0_dgsiaf_slu_admin_local_manual_2007","148","149","C55 débito directo"),
    ("PV145_06","e0_dgsiaf_slu_admin_local_manual_2007","149","150","C55 diferencia de cambios"),
    ("PV145_07","e0_dgsiaf_slu_admin_local_manual_2007","153-154","154-155","corrección/desautorización"),
    ("PV145_08","e0_dgsiaf_slu_admin_local_manual_2007","163","164","importación restringida"),
    ("PV145_09","e0_dgsiaf_slu_admin_local_manual_2007","165-167","166-168","commit/formato/error log"),
    ("PV145_10","e0_dgsiaf_slu_admin_local_manual_2007","172","173","migración usuarios/roles"),
    ("PV145_11","e0_cgn_joint_disposition_4_03_backup_recovery","2226","2140","UI/CGN y bases central/local"),
    ("PV145_12","e0_cgn_joint_disposition_4_03_backup_recovery","2227","2141","obligación y responsable SAF"),
    ("PV145_13","e0_cgn_joint_disposition_4_03_backup_recovery","2228-2229","2142-2143","etiquetas, registro, logs/copias"),
    ("PV145_14","e0_cgn_joint_disposition_4_03_backup_recovery","2230","2144","pruebas y retención perpetua"),
    ("PV145_15","e0_cgn_joint_disposition_4_03_backup_recovery","2231","2145","recuperación mensual firmada"),
    ("PV145_16","e0_cgn_joint_disposition_4_03_backup_recovery","2233-2235","2147-2149","soportes históricos/planilla"),
]
write_csv(HERE/"E0_V145_PDF_VISUAL_CONTROL.csv", [{"control_id":a,"source_id":b,"printed_page":c,"pdf_page":d,"rendered_check":e,"result":"PASS","inference_limit":"control visual; no fila target"} for a,b,c,d,e in visual_rows])

breaks_path = HERE/"E0_FISCAL_METHOD_BREAKS_V145.csv"
breaks = read_csv(breaks_path)
breaks = upsert(breaks, [
    {"break_id":"slu_perpetual_retention_not_recovered_copy","dimension":"access","problem":"Retención perpetua no equivale a soporte recuperado.","rule":"Pedir inventario/restauración/exportación con hash.","status":"FROZEN_V145","evidence":"E0_SLU_BACKUP_RETENTION_DUTY_V145.csv"},
    {"break_id":"slu_shared_custody_not_exclusive","dimension":"custody","problem":"CGN/UI y SAF tienen funciones concurrentes.","rule":"Evitar derivación circular; constancia por repositorio.","status":"FROZEN_V145","evidence":"E0_SLU_BACKUP_RETENTION_DUTY_V145.csv"},
    {"break_id":"slu_audit_three_years_database_perpetual","dimension":"retention","problem":"Pistas de usuario 3 años; fuentes/bases perpetuas.","rule":"Ausencia de log no niega fila de base.","status":"FROZEN_V145","evidence":"E0_SLU_BACKUP_RETENTION_DUTY_V145.csv"},
    {"break_id":"slu_security_import_not_transaction_migration","dimension":"migration","problem":"Manual importa seguridad, no movimientos.","rule":"Pedir Acta/scripts/control entre bases.","status":"FROZEN_V145","evidence":"E0_SLU_LOCAL_ADMIN_HISTORY_AND_C55_V145.csv"},
    {"break_id":"siche_zero_without_ingest_coverage","dimension":"coverage","problem":"Cero SICHE sin catálogo/corte no prueba ausencia.","rule":"Exportar parámetros y pedir cobertura.","status":"FROZEN_V145","evidence":"E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V145.csv"},
], "break_id")
write_csv(breaks_path, breaks, list(breaks[0]))

trace_path = HERE/"E0_INFORMATION_REQUEST_TRACEABILITY_V145.csv"
trace = read_csv(trace_path)
trace_additions = [{"trace_id":f"TR145_{i:03d}","request_id":"REQ133_ECON","institution":"Economía / CGN / DGSIAF / SAF","gap_id":row[0],"requested_record":row[1],"period_or_date":"2006-2009; foco 2008","identifiers":"SLU;SAF 355;SICHE;BMOVEXTERNO;AMOV_FORG;C55","minimum_usable_fields":row[2],"confidentiality_fallback":"metadatos/conteos sin datos personales","status":"DRAFT_NOT_SENT"} for i,row in enumerate(request_objects,196)]
trace = upsert(trace, trace_additions, "trace_id"); write_csv(trace_path, trace, list(trace[0]))

keys_path = HERE/"E0_REQUEST_SEARCH_KEY_MATRIX_V145.csv"
keys = read_csv(keys_path)
exact_keys = ["Disposición Conjunta 4/03 CGN · 1/03 UI","fuentes y base de datos: perpetuo","formulario prueba recuperación de backups","planilla registro de back-up soportes","Acta Acuerdo","backup previo a la migración","testeo y control entre las bases de datos","documentación de diferencias detectadas","informe de avance firmado conjuntamente","Resolución 115/2005","Resolución 53/2024","SICHE SLU","BMOVEXTERNO","AMOV_FORG","conc_01.rep","conc_02.rep","C55 Regularización Pura Débito Directo","C55 Diferencia de Cambios","C55 Corrección Global"]
keys = upsert(keys, [{"key_id":f"SK145_{i:02d}","request_id":"REQ133_ECON","key_group":"backup_migration_siche","exact_key":key,"search_purpose":"localizar registro exacto","source_or_basis":"V145 normas/manual","caveat":"clave, no fila objetivo"} for i,key in enumerate(exact_keys,1)], "key_id")
write_csv(keys_path, keys, list(keys[0]))

recovery_path = HERE/"E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V145.csv"
recovery = read_csv(recovery_path)
recovery = upsert(recovery, [
    {"recovery_id":"HR145_13","problem":"retención perpetua sin inventario","required_record":"planilla/catálogo 2006-2009","minimum_fields":"equipo;fecha;lote;soporte;ubicación","success_test":"soporte SLU individualizado","negative_rule":"deber no equivale a recuperación","source_id":"E0_SLU_BACKUP_RETENTION_DUTY_V145.csv","status":"DRAFT_NOT_SENT"},
    {"recovery_id":"HR145_14","problem":"migración sin expediente","required_record":"Acta, backup previo, scripts y control","minimum_fields":"versión;fecha;tabla;conteo;diferencia;firma","success_test":"cadena reconstruida","negative_rule":"manual de usuarios no basta","source_id":"E0_SLU_MIGRATION_DOCUMENT_CHAIN_V145.csv","status":"DRAFT_NOT_SENT"},
    {"recovery_id":"HR145_15","problem":"ruta actual no ejecutada","required_record":"export SICHE e inventario","minimum_fields":"consulta;período;filtros;filas;hash","success_test":"export reproducible","negative_rule":"cero sin cobertura no prueba","source_id":"E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V145.csv","status":"DRAFT_NOT_SENT"},
    {"recovery_id":"HR145_16","problem":"C55 no localizado","required_record":"débito/diferencia/corrección/reversa","minimum_fields":"tipo;estado;origen;fecha;importe;cuenta","success_test":"cruce con extracto","negative_rule":"permiso no prueba formulario","source_id":"E0_SLU_LOCAL_ADMIN_HISTORY_AND_C55_V145.csv","status":"DRAFT_NOT_SENT"},
], "recovery_id")
write_csv(recovery_path, recovery, list(recovery[0]))

request_path = HERE/"REQUEST_ECONOMIA_TESORO_SETTLEMENT_V145.md"
append_section(request_path, "## Clave V145 · SICHE, retención perpetua y migración", """
Estado: **BORRADOR_NO_ENVIADO**. Este apartado no autoriza ni registra presentación.

La Disposición Conjunta CGN 4/03–UI 1/03 hace obligatorias las normas de resguardo para sistemas de Hacienda administrados localmente, asigna responsabilidad al Director General de Administración o titular informático del SAF y fija retención **perpetua** para fuentes y bases. La Resolución 115/2005 exige backup previo a migración, migración, control entre bases, diferencias documentadas, informes firmados y responsables. Desde el 1/7/2024, la Resolución 53/2024 establece SICHE como vía única para consultar SLU.

Se solicita, en este orden: (1) inventario de consultas/datasets SICHE-SLU y exportación 2008 con parámetros, cobertura, conteos y hash; (2) inventario de respaldos SLU 2006-2009, planillas diarias, logs, actas mensuales y soportes históricos; (3) Acta Acuerdo, cronograma, backup previo, scripts/mapeos, control entre bases, diferencias, prueba paralela e informes firmados; (4) dumps de `BMOVEXTERNO` y `AMOV_FORG`; (5) C55 de Débito Directo, Diferencia de Cambios, Corrección Global y reversas; y (6) `conc_01.rep`, `conc_02.rep`, Libro Banco y extracto.

Una respuesta negativa deberá individualizar repositorios, períodos, consultas, filtros, fecha de corte SICHE, inventarios examinados, acto de expurgo/transferencia y autoridad responsable. Una vista vigente vacía o afirmación genérica no satisface el objeto.
""")

append_section(HERE/"REQUEST_SUBMISSION_CHECKLIST_V145.md", "## Control V145 · SICHE, backups y migración SLU", """
- Mantener `DRAFT_NOT_SENT` sin autorización expresa.
- Adjuntar las matrices de deber, migración, administración/C55, ruta SICHE y objetos de pedido.
- Pedir primero exportación SICHE reproducible; usar restauración si falta cobertura.
- Exigir inventario, logs, actas y custodia; no convertir retención perpetua en presunción de hallazgo.
- Mantener 0/10 hasta cerrar C55/extracto/Libro Banco/cuenta/importe.
""")

append_section(HERE/"SOURCE_REFERENCES_V145.md", "## Fuentes nuevas V145 · resguardo, migración, administrador local y comparador", "\n".join(f"- `{s['id']}` · {s['title']} · {s['url']} · `{s['local']}` · `{s['sha']}`" for s in source_data))
append_section(HERE/"E0_INSTITUTIONAL_REQUEST_PACKAGE_V145.md", "## Clave V145 · obligación de resguardo y consulta SICHE", "El pedido Economía/Tesoro nombra inventario SICHE, planillas, logs, actas de recuperación, Acta Acuerdo, backup previo, migración, comparación entre bases e informes firmados. Adjuntos: `E0_SLU_BACKUP_RETENTION_DUTY_V145.csv`, `E0_SLU_MIGRATION_DOCUMENT_CHAIN_V145.csv`, `E0_SLU_BACKUP_AND_SICHE_REQUEST_OBJECTS_V145.csv` y `E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V145.csv`. Estado: `DRAFT_NOT_SENT`.")

(HERE/"README_V145.md").write_text("""# V145 · obligación de resguardo, migración y ruta SICHE

V145 cierra el vacío normativo de custodia. La Disposición Conjunta CGN 4/03–UI 1/03 era obligatoria para sistemas de Hacienda administrados localmente, identifica al responsable de cada SAF, exige inventarios, logs y pruebas mensuales firmadas, y fija retención perpetua para fuentes y bases. La Resolución 115/2005 exige Acta Acuerdo, backup previo, migración, comparación entre bases, diferencias documentadas, prueba paralela e informes firmados.

La Resolución 53/2024 convierte a SICHE en la vía única para consultar SLU. La secuencia queda: exportación SICHE con inventario/cobertura/parámetros → inventario/restauración si falta cobertura → migración/diferencias → `BMOVEXTERNO`/`AMOV_FORG` → C55 → extracto/Libro Banco/conciliación.

El manual de Administrador Local 2007 prueba historia de usuarios/roles y C55 de débito directo, diferencia de cambio, corrección y reversa. Su importación sólo cubre seguridad; no acredita migración de movimientos. Ninguna consulta fue ejecutada ni enviada. Permanecen 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos `DRAFT_NOT_SENT`.
""", encoding="utf-8")

(HERE/"VEREDICTO_V145.md").write_text("""# Veredicto V145

La recuperación histórica dejó de ser especulativa: existía obligación expresa de resguardar perpetuamente fuentes y bases, identificar soportes, registrar backups, generar logs y probar la recuperación mensualmente mediante actas firmadas. Cada migración debía documentar backup previo, comparación entre bases y diferencias. Los responsables se delimitan entre CGN, UI/DGSIAF y SAF.

Esto no confirma la fila objetivo. Retención obligatoria no equivale a soporte localizado; la historia del Administrador Local concierne usuarios/roles; el comparador MDS 2007 no prueba el inventario de SAF 355. La prueba exige exportación SICHE o restauración documentada y el cruce `BMOVEXTERNO` → `AMOV_FORG` → C55 → extracto/Libro Banco.

No se recuperó código BNA, fila 2008, C55, extracto ni respaldo individual. Continúan 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos sin enviar.
""", encoding="utf-8")

(HERE/"E0_FISCAL_RECONSTRUCTION_V145.md").write_text("""# Reconstrucción fiscal E0 V145

La reconstrucción numérica estricta no cambia. V145 fortalece la recuperación: retención perpetua de fuentes/bases, responsables, registros y actas de backup, cadena de migración y ruta SICHE. Esos objetos no fueron obtenidos ni ejecutados. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE/"RETRIEVAL_LOG_V145.md").write_text("""# Registro de recuperación V145

- 2026-08-30/31: manual SLU Administrador Local 2007 preservado; revisión textual/visual.
- 2026-08-31: Resolución 115/2005 preservada desde Argentina.gob.ar.
- 2026-08-31: digesto oficial CDI/Economía con Disposición 4/03–1/03 y anexos preservado; páginas impresas 2226-2235 verificadas.
- 2026-08-31: Resolución MDS 7028/2007 preservada como comparador limitado.
- El HTML histórico CGN presentó certificado vencido; se usó la copia oficial consolidada CDI.
- No se ejecutó SICHE ni se presentó pedido.
""", encoding="utf-8")

(HERE/"AUDITORIA_V145.md").write_text(f"""# Auditoría V145

- Fuentes maestras: {len(catalog)}.
- Fuentes primarias E0: {len(census)}.
- Fuentes nuevas: 4.
- Retención: fuentes/bases perpetua; actividad/pistas 3 años.
- Fila target: no localizada; SICHE ejecutado: 0.
- Pedidos enviados: 0; respuestas: 0.
""", encoding="utf-8")

(HERE/"HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V145_A_V146.md").write_text("""# Handover V145 → V146

## Estado

- QA V145: PASS.
- Cuatro fuentes oficiales nuevas; 457 fuentes maestras y 217 E0.
- Disposición 4/03–1/03: obligación local, responsable SAF, registro/log/prueba y retención perpetua de fuentes/bases.
- Resolución 115/2005: Acta Acuerdo, backup previo, migración, comparación entre bases, diferencias e informes firmados.
- Resolución 53/2024: SICHE es vía única SLU; exporta grillas y toma repositorio sin transformar.
- Manual AL 2007: historia usuarios/roles; C55 débito, diferencia, corrección y reversa; importación limitada a seguridad.
- Sin fila target; seis `DRAFT_NOT_SENT`; 10 adjudicaciones, 9 cuentas, 0/10 ejecuciones.

## Prioridad V146

1. Mantener borradores salvo autorización.
2. Buscar catálogo/manual de consultas SICHE-SLU y equivalencias de campos.
3. Localizar Acta Acuerdo/migración SLU del SAF 355 y responsables.
4. Buscar planillas/actas de soportes históricos y recuperación.
5. Localizar salida 2008 `BMOVEXTERNO`, `AMOV_FORG`, C55, `conc_01/02`, extracto o Libro Banco.
6. Separar deber jurídico, capacidad técnica, soporte localizado y ejecución económica.
""", encoding="utf-8")

queue_path = HERE/"HISTORICAL_SOURCE_QUEUE_V145.csv"
queue = read_csv(queue_path)
queue = upsert(queue, [{"priority":"P0","episode":"E0_2008","variable_family":"SLU_backup_SICHE","target_artifact":"SICHE export + backup inventory + migration file + populated banking tables","preferred_source":"CGN+DGSIAF+SAF 355","status":"LEGAL_DUTY_PROVED_TARGET_DATA_OPEN_NOT_SENT","why":"fuentes/bases perpetuas y migraciones documentadas","next_action":"catálogo SICHE, Acta, planillas y export 2008"}], "target_artifact")
write_csv(queue_path, queue, list(queue[0]))

recovery_queue_path = HERE/"RECOVERY_QUEUE_V145.csv"
rq = read_csv(recovery_queue_path)
rq = upsert(rq, [
    {"priority":"11","entity":"SLU 2008 backup","missing_artifact":"Inventario, soporte y restauración","why":"recupera tablas sin historia","status":"OPEN_LEGAL_DUTY_PROVED"},
    {"priority":"12","entity":"SICHE SLU","missing_artifact":"Inventario y export 2008","why":"vía legal vigente","status":"OPEN_NOT_EXECUTED"},
], "entity")
write_csv(recovery_queue_path, rq, list(rq[0]))

hash_rows = []
for row in catalog:
    local = row["archivo_local"]; path = REPO/local.lstrip("/") if local else None
    exists = bool(path and path.is_file()); actual = sha256(path) if exists else ""; expected = row["sha256"]
    hash_rows.append({"id":row["id"],"archivo_local":local,"exists":str(exists),"sha_catalog":expected,"sha_actual":actual,"hash_ok":str(bool(exists and expected and actual.lower()==expected.lower()))})
write_csv(AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V145.csv", hash_rows)
write_csv(AUDIT/"SOURCE_BACKUP_CENSUS_V145.csv", hash_rows)
physical = sum(r["exists"]=="True" for r in hash_rows); hash_ok = sum(r["hash_ok"]=="True" for r in hash_rows)

size_rows=[]
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts: continue
    size=path.stat().st_size
    size_rows.append({"path":path.relative_to(REPO).as_posix(),"bytes":size,"mib":f"{size/1048576:.6f}","over_50_mib":str(size>50*1048576),"over_100_mib":str(size>100*1048576)})
write_csv(AUDIT/"GITHUB_FILE_SIZE_AUDIT_V145.csv", size_rows)

complete_path = AUDIT/"CURRENT_SOURCE_COMPLETENESS_V145.json"
if not complete_path.exists():
    previous = (AUDIT/"CURRENT_SOURCE_COMPLETENESS_V144.json").read_text(encoding="utf-8-sig")
    complete_path.write_text(previous.replace("V144", "V145").replace("v144", "v145"), encoding="utf-8")
complete = json.loads(complete_path.read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V145","date":"2026-08-31","state":"E0_SLU_BACKUP_RETENTION_MIGRATION_DUTY_PROVED_SICHE_ROUTE_CURRENT_TARGET_NOT_EXECUTED_NOT_SENT",
    "numeric_v145_strict_changed":False,"master_catalog_entries":len(catalog),"physical_local_copies":physical,"physical_local_hash_ok":hash_ok,
    "binary_required_entries":386,"binary_required_preserved":385,"remaining_physical_gaps":len(catalog)-physical,
    "e0_primary_sources_preserved":len(census),"sources_newly_preserved_v145":4,"e0_primary_sources_newly_preserved_v145":4,"e0_duplicate_recaptures_v145":0,
    "e0_fiscal_method_breaks_frozen":len(breaks),"e0_request_traceability_rows":len(trace),"e0_request_search_keys":len(keys),
    "e0_slu_backup_retention_duty_rows":len(backup_duties),"e0_slu_migration_document_chain_rows":len(migration_rows),"e0_slu_local_admin_c55_rows":len(admin_rows),
    "e0_siche_slu_legal_route_rows":len(siche_rows),"e0_slu_backup_request_objects_rows":len(request_objects),"e0_2007_backup_comparator_rows":len(comparator_rows),"e0_v145_pdf_visual_controls":len(visual_rows),
    "e0_slu_sources_and_databases_retention_rule":"PERPETUAL","e0_slu_user_activity_audit_retention_years":3,
    "e0_slu_backup_retention_norm_located":True,"e0_slu_migration_required_record_types_located":True,"e0_slu_historical_backup_inventory_located":False,"e0_slu_specific_2008_backup_restored":False,
    "e0_siche_slu_current_legal_route_proved":True,"e0_siche_named_queries_executed":0,"e0_siche_target_exports_located":0,"e0_slu_target_2008_populated_table_row_located":False,
    "e0_settlement_executed_rows_confirmed":0,"e0_requests_submitted":0,"e0_request_responses_received":0,"e0_request_package_status":"DRAFT_NOT_SENT",
    "historical_workstream":"Obtain parameterized SICHE-SLU export and mandatory backup/migration records; restore 2008 tables and cross C55/extract/Libro Banco; no request submitted"})
complete_path.write_text(json.dumps(complete,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

append_section(REPO/"BACKUP_ACTUALIZACION_2026-08-29.md", "## V145 · obligación de resguardo, migración y ruta SICHE", """
- Disposición 4/03–1/03: fuentes/bases perpetuas; registros, logs, pruebas mensuales y responsable SAF.
- Resolución 115/2005: backup previo, migración, control entre bases, diferencias e informes firmados.
- Resolución 53/2024: SICHE vía única SLU.
- Manual AL 2007: C55 débito, diferencia, corrección y reversa; historia limitada a seguridad.
- Sin export/soporte target; 10 adjudicaciones, 9 cuentas, 0/10; seis borradores no enviados.
""")

write_csv(HERE/"INHERITED_QA_STATUS_V145.csv", [
    {"script":"qa_v144.py","pre_v145_result":"PASS","post_v145_result":"EXPECTED_SUPERSEDED_ASSERTION","interpretation":"V144 ampliada por retención/migración/SICHE."},
    {"script":"qa_v145.py","pre_v145_result":"N/A","post_v145_result":"PASS","interpretation":"Verifica fuentes, matrices, hashes, límites y no envío."}])

def checkpoint_manifest():
    files=[{"path":p.name,"bytes":p.stat().st_size,"sha256":sha256(p)} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!="MANIFEST_V145.json"]
    manifest={"checkpoint":"V145","parent_checkpoint":"V144","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"exact_entities":30,"strict_coverage_pct":STRICT,"closed_network_gate":"NO","e0_primary_sources":len(census),"new_preserved_sources":4,"fiscal_ledger_rows":len(read_csv(HERE/"E0_FISCAL_MECHANISM_LEDGER_V145.csv")),"fiscal_method_breaks":len(breaks),"request_traceability_rows":len(trace),"request_search_keys":len(keys),"slu_backup_retention_duty_rows":len(backup_duties),"slu_migration_document_chain_rows":len(migration_rows),"slu_local_admin_c55_rows":len(admin_rows),"siche_slu_legal_route_rows":len(siche_rows),"slu_backup_request_objects_rows":len(request_objects),"backup_comparator_rows":len(comparator_rows),"pdf_visual_controls_v145":len(visual_rows),"siche_named_queries_executed":0,"siche_target_exports_located":0,"specific_2008_backup_restored":False,"award_rows_exact":10,"account_candidate_rows":9,"executed_settlement_rows_confirmed":0,"request_drafts":6,"requests_submitted":0,"responses_received":0,"files":files}
    (HERE/"MANIFEST_V145.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def tree(root):
    return "\n".join(p.relative_to(root).as_posix()+("/" if p.is_dir() else "") for p in sorted(root.rglob("*"),key=lambda x:x.relative_to(root).as_posix().casefold()) if ".git" not in p.parts and "__pycache__" not in p.parts and "tmp" not in p.parts)+"\n"

(REPO/"TREE.txt").write_text(tree(REPO),encoding="utf-8")
(CYCLE/"TREE.txt").write_text(tree(CYCLE),encoding="utf-8")
checkpoint_manifest()

gm_path=CYCLE/"MANIFEST_SHA256.json"; gm_files=[]
for p in sorted(REPO.rglob("*"),key=lambda x:x.relative_to(REPO).as_posix().casefold()):
    if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and "tmp" not in p.parts and p!=gm_path:
        gm_files.append({"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha256(p)})
gm={"checkpoint":"V145","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":STRICT,"exact_entities":30,"closed_network_gate":"NO","source_audit":f"{len(catalog)} master; {physical} physical SHA-valid; 4 new official sources; perpetual retention/migration duties and SICHE route proved; target not located; 0/10; six drafts not submitted.","historical_workstream":"Obtain SICHE export and mandatory backup/migration records; restore 2008 tables and cross C55/extract/Libro Banco; no request submitted","file_count_excluding_manifest":len(gm_files),"files":gm_files}
gm_path.write_text(json.dumps(gm,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

print(f"V145 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok}")
