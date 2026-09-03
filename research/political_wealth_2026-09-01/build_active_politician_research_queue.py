from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
ROSTER_PATH = DERIVED / "active_politicians_roster_2026-09-01.csv"
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"

QUEUE_PATH = DERIVED / "active_politician_research_queue_2026-09-01.csv"
IDENTITY_PATH = DERIVED / "active_politician_oa_identity_review_2026-09-01.csv"
SERIES_PATH = DERIVED / "active_politician_oa_candidate_series_2017_2024.csv"
SUMMARY_PATH = DERIVED / "active_politician_research_summary_2026-09-01.json"

FREEZE_DATE = "2026-09-02"
FREEZE_REASON = (
    "Expansión pausada para priorizar profundidad analítica en las trayectorias ya publicadas. "
    "El freeze no equivale a descarte, incumplimiento ni patrimonio cero."
)

TYPE_PRIORITY = {"Inicial": 1, "Baja": 2, "Anual": 3}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.upper().replace("Ñ", "N")
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    return " ".join(value.split())


def clean(value: str) -> str:
    return " ".join((value or "").replace('""', "").split()).strip('" ')


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def selection_key(row: dict[str, str]) -> tuple[int, int, int]:
    return (
        TYPE_PRIORITY.get(row.get("tipo_declaracion_jurada_descripcion", ""), 0),
        int(row.get("rectificativa") or 0),
        int(row.get("dj_id") or 0),
    )


def institution_match(level: str, organismo: str, cargo: str) -> bool:
    text = normalize(f"{organismo} {cargo}")
    if level == "Diputados nacionales":
        return "DIPUTAD" in text or "CAMARA DE DIPUTADOS" in text
    if level == "Senado nacional":
        return "SENAD" in text or "SENADO DE LA NACION" in text
    if level == "Conducción superior PEN":
        return any(token in text for token in ("PRESIDENCIA", "MINISTERIO", "JEFATURA DE GABINETE"))
    return False


def masked_person_key(cuit: str) -> str:
    if not cuit:
        return ""
    return hashlib.sha256(cuit.encode("utf-8")).hexdigest()[:16]


with ROSTER_PATH.open(encoding="utf-8", newline="") as handle:
    roster = list(csv.DictReader(handle))
assert len(roster) == 789

homonym_resolutions: list[dict[str, str]] = []
homonym_resolution_iteration_by_id: dict[str, int] = {}
for resolution_path in sorted(DERIVED.glob("active_politician_homonymy_resolutions_iteration_*_2026-09-01.csv")):
    match = re.search(r"iteration_(\d+)_", resolution_path.name)
    assert match
    iteration_number = int(match.group(1))
    with resolution_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        assert row["persona_id"] not in homonym_resolution_iteration_by_id
        homonym_resolution_iteration_by_id[row["persona_id"]] = iteration_number
    homonym_resolutions.extend(rows)
assert len(homonym_resolutions) in {0, 7, 12, 13, 14}
homonym_resolution_by_id = {row["persona_id"]: row for row in homonym_resolutions}
assert len(homonym_resolution_by_id) == len(homonym_resolutions)

homonym_exclusion_by_id: dict[str, dict[str, str]] = {}
homonym_exclusion_iteration_by_id: dict[str, int] = {}
for exclusion_path in sorted(DERIVED.glob("active_politician_homonymy_exclusions_iteration_*_2026-09-01.csv")):
    match = re.search(r"iteration_(\d+)_", exclusion_path.name)
    assert match
    iteration_number = int(match.group(1))
    with exclusion_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            homonym_exclusion_by_id[row["persona_id"]] = row
            homonym_exclusion_iteration_by_id[row["persona_id"]] = iteration_number
homonym_exclusions = list(homonym_exclusion_by_id.values())
assert len(homonym_exclusions) in {0, 5, 6, 7}
full_homonym_exclusion_by_id = {
    row["persona_id"]: row
    for row in homonym_exclusions
    if row["alcance_descarte"].startswith("total_")
}
assert len(full_homonym_exclusion_by_id) in {0, 3, 6, 7}

candidate_names = {
    clean(row["oa_historial_nombres"])
    for row in roster
    if row["oa_historial_2017_2024_estado"] == "nombre_compatible_unico_en_oa"
}
candidate_names.update(row["oa_nombre_resuelto"] for row in homonym_resolutions)
assert len(candidate_names) > 300

oa_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
with zipfile.ZipFile(ZIP_PATH) as archive:
    for year in range(2017, 2025):
        member = f"declaraciones-juradas-{year}-consolidado-al-20251222.csv"
        with archive.open(member) as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for row in csv.DictReader(text):
                    name = clean(row.get("funcionario_apellido_nombre", ""))
                    if name in candidate_names:
                        oa_rows[name].append({key: clean(value) for key, value in row.items()})

assert candidate_names == set(oa_rows), "No se recuperaron todos los candidatos nominales del ZIP OA"

identity_by_person: dict[str, dict[str, object]] = {}
selected_by_person_year: dict[tuple[str, int], dict[str, str]] = {}

for person in roster:
    if person["oa_historial_2017_2024_estado"] != "nombre_compatible_unico_en_oa":
        continue
    official_name = clean(person["oa_historial_nombres"])
    raw = oa_rows[official_name]
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in raw:
        grouped[int(row["anio"])].append(row)
    selected = {year: max(rows, key=selection_key) for year, rows in grouped.items()}
    for year, row in selected.items():
        selected_by_person_year[(person["persona_id"], year)] = row

    cuits = sorted({row["cuit"] for row in raw if row.get("cuit")})
    evidence_years = sorted(
        year
        for year, row in selected.items()
        if institution_match(person["nivel_cargo"], row.get("organismo", ""), row.get("cargo", ""))
    )
    latest_year = max(selected)
    latest = selected[latest_year]
    current_filing = person["estado_ddjj_cargo_actual"].startswith("presentacion_")
    exact_name = normalize(person["persona"]) == normalize(official_name)

    if person["serie_tab_id"]:
        status = "serie_curada"
        next_action = "Mantener auditoría persona-año y sumar el ejercicio 2025 cuando exista fuente primaria."
    elif evidence_years and current_filing and len(cuits) == 1:
        status = "preclasificacion_fuerte_misma_institucion"
        next_action = "Cotejar manualmente nombre, CUIT reservado, distrito y cargo; luego promover la serie al tab."
    elif person["nivel_cargo"] in {"Gobernaciones", "Legislaturas provinciales"}:
        status = "historial_oa_posible_cargo_nacional_previo"
        next_action = "No atribuir al cargo provincial actual: localizar primero el régimen y la DDJJ provincial."
    elif len(cuits) == 1 and exact_name:
        status = "preclasificacion_nombre_y_cuit_unicos"
        next_action = "Revisar organismo y cargo por año antes de publicar como identidad confirmada."
    else:
        status = "revision_manual_identidad"
        next_action = "Resolver variaciones de nombre o identificador antes de usar importes."

    identity_by_person[person["persona_id"]] = {
        "persona_id": person["persona_id"],
        "persona": person["persona"],
        "nivel_cargo": person["nivel_cargo"],
        "cargo_actual": person["cargo"],
        "jurisdiccion": person["jurisdiccion"],
        "oa_nombre": official_name,
        "nombre_normalizado_exacto": "sí" if exact_name else "no",
        "oa_personas_por_cuit": len(cuits),
        "oa_person_key": masked_person_key(cuits[0]) if len(cuits) == 1 else "",
        "oa_anios_seleccionados": "|".join(map(str, sorted(selected))),
        "evidencia_misma_institucion_anios": "|".join(map(str, evidence_years)),
        "presentacion_cargo_actual_localizada": "sí" if current_filing else "no",
        "ultimo_anio_oa": latest_year,
        "ultimo_organismo_oa": latest.get("organismo", ""),
        "ultimo_cargo_oa": latest.get("cargo", ""),
        "estado_revision_identidad": status,
        "siguiente_accion": next_action,
    }

roster_by_id = {row["persona_id"]: row for row in roster}
for person_id, resolution in homonym_resolution_by_id.items():
    person = roster_by_id[person_id]
    official_name = clean(resolution["oa_nombre_resuelto"])
    resolved_rows = [
        row
        for row in oa_rows[official_name]
        if masked_person_key(row.get("cuit", "")) == resolution["oa_person_key"]
    ]
    assert resolved_rows, f"La resolución de {person_id} no recuperó filas OA"
    resolved_cuits = {row["cuit"] for row in resolved_rows if row.get("cuit")}
    assert len(resolved_cuits) == 1

    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in resolved_rows:
        grouped[int(row["anio"])].append(row)
    selected = {year: max(rows, key=selection_key) for year, rows in grouped.items()}
    for year, row in selected.items():
        selected_by_person_year[(person_id, year)] = row

    evidence_years = sorted(
        year
        for year, row in selected.items()
        if institution_match(person["nivel_cargo"], row.get("organismo", ""), row.get("cargo", ""))
    )
    latest_year = max(selected)
    latest = selected[latest_year]
    current_filing = person["estado_ddjj_cargo_actual"].startswith("presentacion_")
    identity_by_person[person_id] = {
        "persona_id": person_id,
        "persona": person["persona"],
        "nivel_cargo": person["nivel_cargo"],
        "cargo_actual": person["cargo"],
        "jurisdiccion": person["jurisdiccion"],
        "oa_nombre": official_name,
        "nombre_normalizado_exacto": "sí" if normalize(person["persona"]) == normalize(official_name) else "no",
        "oa_personas_por_cuit": 1,
        "oa_person_key": resolution["oa_person_key"],
        "oa_anios_seleccionados": "|".join(map(str, sorted(selected))),
        "evidencia_misma_institucion_anios": "|".join(map(str, evidence_years)),
        "presentacion_cargo_actual_localizada": "sí" if current_filing else "no",
        "ultimo_anio_oa": latest_year,
        "ultimo_organismo_oa": latest.get("organismo", ""),
        "ultimo_cargo_oa": latest.get("cargo", ""),
        "estado_revision_identidad": "preclasificacion_homonimia_resuelta_fuente_oficial",
        "siguiente_accion": "Auditar la resolución documental y publicar la serie separada del resto de homónimos.",
    }

strong_candidates = sorted(
    (
        row for row in identity_by_person.values()
        if row["estado_revision_identidad"] == "preclasificacion_fuerte_misma_institucion"
    ),
    key=lambda row: (row["nivel_cargo"], normalize(str(row["persona"]))),
)
iteration_one = {row["persona_id"] for row in strong_candidates[:30]}

confirmed_by_iteration: dict[int, set[str]] = {}
strong_candidate_ids = {row["persona_id"] for row in strong_candidates}
governor_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Gobernaciones"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
caba_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Legislaturas provinciales"
    and row["jurisdiccion"] == "Ciudad Autónoma de Buenos Aires"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
pba_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Legislaturas provinciales"
    and row["jurisdiccion"] == "Buenos Aires"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
santa_fe_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Legislaturas provinciales"
    and row["jurisdiccion"] == "Santa Fe"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
rio_negro_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Legislaturas provinciales"
    and row["jurisdiccion"] == "Río Negro"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
cordoba_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Legislaturas provinciales"
    and row["jurisdiccion"] == "Córdoba"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
misiones_history_candidate_ids = {
    row["persona_id"]
    for row in identity_by_person.values()
    if row["nivel_cargo"] == "Legislaturas provinciales"
    and row["jurisdiccion"] == "Misiones"
    and row["estado_revision_identidad"] == "historial_oa_posible_cargo_nacional_previo"
}
with (
    DERIVED / "active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv"
).open(encoding="utf-8-sig", newline="") as handle:
    pen_unique_identity_candidate_ids = {
        row["persona_id"] for row in csv.DictReader(handle)
    }
assert len(pen_unique_identity_candidate_ids) == 8
assert all(
    identity_by_person[person_id]["nivel_cargo"] == "Conducción superior PEN"
    and identity_by_person[person_id]["oa_personas_por_cuit"] == 1
    and identity_by_person[person_id]["oa_anios_seleccionados"]
    for person_id in pen_unique_identity_candidate_ids
)
with (
    DERIVED / "active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv"
).open(encoding="utf-8-sig", newline="") as handle:
    cross_institution_candidate_ids = {
        row["persona_id"] for row in csv.DictReader(handle)
    }
assert len(cross_institution_candidate_ids) == 4
assert all(
    identity_by_person[person_id]["nivel_cargo"] in {"Diputados nacionales", "Senado nacional"}
    and identity_by_person[person_id]["oa_personas_por_cuit"] == 1
    and identity_by_person[person_id]["presentacion_cargo_actual_localizada"] == "sí"
    for person_id in cross_institution_candidate_ids
)
identity_candidate_ids = set(identity_by_person)
homonym_resolution_ids = set(homonym_resolution_by_id)
for audit_path in sorted(DERIVED.glob("active_politician_identity_audit_iteration_*_2026-09-01.csv")):
    match = re.search(r"iteration_(\d+)_", audit_path.name)
    assert match
    iteration_number = int(match.group(1))
    with audit_path.open(encoding="utf-8-sig", newline="") as handle:
        confirmed = {
            row["persona_id"]
            for row in csv.DictReader(handle)
            if row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial"
            and row["publicable_en_tab"] == "sí"
        }
    assert confirmed <= identity_candidate_ids
    if iteration_number <= 5:
        assert confirmed <= strong_candidate_ids
    elif iteration_number == 6:
        assert confirmed <= governor_history_candidate_ids
    elif iteration_number == 7:
        assert confirmed <= caba_history_candidate_ids
    elif iteration_number == 8:
        assert confirmed <= pba_history_candidate_ids
    elif iteration_number == 9:
        assert confirmed <= santa_fe_history_candidate_ids
    elif iteration_number == 10:
        assert confirmed <= rio_negro_history_candidate_ids
    elif iteration_number == 11:
        assert confirmed <= cordoba_history_candidate_ids
    elif iteration_number == 12:
        assert confirmed <= misiones_history_candidate_ids
    elif iteration_number in {13, 14, 15, 17}:
        allowed = {
            person_id
            for person_id, resolution_iteration in homonym_resolution_iteration_by_id.items()
            if resolution_iteration == iteration_number
        }
        assert confirmed <= allowed
    elif iteration_number == 18:
        assert confirmed <= pen_unique_identity_candidate_ids
    elif iteration_number == 19:
        assert confirmed <= cross_institution_candidate_ids
    else:
        raise AssertionError(f"La cola todavía no define el universo admisible de la iteración {iteration_number}")
    if iteration_number == 1:
        assert confirmed <= iteration_one
    confirmed_by_iteration[iteration_number] = confirmed

confirmed_all = set().union(*confirmed_by_iteration.values()) if confirmed_by_iteration else set()
confirmed_iteration_by_id = {
    person_id: iteration_number
    for iteration_number, person_ids in confirmed_by_iteration.items()
    for person_id in person_ids
}
assert len(confirmed_iteration_by_id) == sum(len(value) for value in confirmed_by_iteration.values())
for person_id in confirmed_all:
    identity_by_person[person_id]["estado_revision_identidad"] = "identidad_confirmada_cruce_oficial"
    identity_by_person[person_id]["siguiente_accion"] = (
        "Serie normalizada y contrafactuales incorporados; actualizar con el consolidado 2025 cuando se publique."
    )

queue_rows: list[dict[str, object]] = []
for person in roster:
    identity = identity_by_person.get(person["persona_id"])
    oa_state = person["oa_historial_2017_2024_estado"]
    if person["serie_tab_id"]:
        search_status = "serie_curada"
        iteration = 0
        next_action = "Actualizar y profundizar la serie existente."
    elif identity and person["persona_id"] not in full_homonym_exclusion_by_id:
        search_status = str(identity["estado_revision_identidad"])
        if person["persona_id"] in iteration_one:
            iteration = 1
        elif person["persona_id"] in confirmed_iteration_by_id:
            iteration = confirmed_iteration_by_id[person["persona_id"]]
        elif search_status == "preclasificacion_fuerte_misma_institucion":
            iteration = 2
        elif person["nivel_cargo"] in {"Diputados nacionales", "Senado nacional", "Conducción superior PEN"}:
            iteration = 3
        else:
            iteration = 4
        next_action = str(identity["siguiente_accion"])
    elif person["persona_id"] in full_homonym_exclusion_by_id:
        exclusion = full_homonym_exclusion_by_id[person["persona_id"]]
        search_status = "sin_registro_oa_2017_2024_identidad_desambiguada"
        iteration = homonym_exclusion_iteration_by_id[person["persona_id"]]
        next_action = (
            "La identidad oficial descarta todas las claves OA nominales recuperadas; buscar la DDJJ del régimen "
            "actual sin atribuir cifras de homónimos. " + exclusion["nota_evidencia"]
        )
    elif oa_state == "coincidencia_multiple_revisar_homonimia":
        search_status = "homonimia_oa_por_resolver"
        iteration = 5
        next_action = "Distinguir homónimos mediante CUIT, organismo, distrito y cargo."
    else:
        search_status = "sin_registro_oa_2017_2024"
        iteration = 6 if person["nivel_cargo"] in {"Gobernaciones", "Legislaturas provinciales"} else 5
        next_action = "Buscar fuente del régimen actual y documentar publicado, reservado o no localizado."
    publishable = search_status in {"serie_curada", "identidad_confirmada_cruce_oficial"}
    queue_rows.append(
        {
            "persona_id": person["persona_id"],
            "persona": person["persona"],
            "nivel_cargo": person["nivel_cargo"],
            "cargo": person["cargo"],
            "jurisdiccion": person["jurisdiccion"],
            "partido_o_alianza": person["partido_o_alianza"],
            "estado_ddjj_cargo_actual": person["estado_ddjj_cargo_actual"],
            "fuente_ddjj_actual_url": person["fuente_ddjj_actual_url"],
            "oa_historial_estado": oa_state,
            "oa_historial_nombres": person["oa_historial_nombres"],
            "oa_anios": person["oa_anios_2017_2024"],
            "estado_busqueda_patrimonial": search_status,
            "estado_investigacion": "cerrado_publicable" if publishable else "freezado",
            "fecha_estado_investigacion": FREEZE_DATE,
            "motivo_estado_investigacion": (
                "Trayectoria publicada con controles reproducibles."
                if publishable
                else FREEZE_REASON
            ),
            "iteracion_sugerida": iteration,
            "siguiente_accion": next_action,
        }
    )

series_rows: list[dict[str, object]] = []
for person in roster:
    identity = identity_by_person.get(person["persona_id"])
    if not identity:
        continue
    for year in range(2017, 2025):
        row = selected_by_person_year.get((person["persona_id"], year))
        if not row:
            continue
        total = row["total_bienes_inicio"] if row["tipo_declaracion_jurada_descripcion"] == "Inicial" else row["total_bienes_final"]
        debt = row["deudas_inicio"] if row["tipo_declaracion_jurada_descripcion"] == "Inicial" else row["total_deudas_final"]
        series_rows.append(
            {
                "persona_id": person["persona_id"],
                "persona": person["persona"],
                "nivel_cargo_actual": person["nivel_cargo"],
                "jurisdiccion_actual": person["jurisdiccion"],
                "oa_nombre": identity["oa_nombre"],
                "oa_person_key": identity["oa_person_key"],
                "estado_revision_identidad": identity["estado_revision_identidad"],
                "anio": year,
                "tipo_ddjj": row["tipo_declaracion_jurada_descripcion"],
                "rectificativa": row["rectificativa"],
                "dj_id": row["dj_id"],
                "organismo_oa": row["organismo"],
                "cargo_oa": row["cargo"],
                "total_bienes_ars": total,
                "deudas_ars": debt,
                "diferencia_valuacion_ars": row["diferencia_valuacion"],
                "ingresos_neto_gastos_ars": row["ingresos_neto_gastos"],
                "fuente_url": "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales",
                "publicable_en_tab": (
                    "sí · identidad confirmada"
                    if identity["estado_revision_identidad"] in {"serie_curada", "identidad_confirmada_cruce_oficial"}
                    else "no · identidad pendiente"
                ),
            }
        )

queue_fields = [
    "persona_id", "persona", "nivel_cargo", "cargo", "jurisdiccion", "partido_o_alianza",
    "estado_ddjj_cargo_actual", "fuente_ddjj_actual_url", "oa_historial_estado",
    "oa_historial_nombres", "oa_anios", "estado_busqueda_patrimonial",
    "estado_investigacion", "fecha_estado_investigacion", "motivo_estado_investigacion",
    "iteracion_sugerida", "siguiente_accion",
]
identity_fields = [
    "persona_id", "persona", "nivel_cargo", "cargo_actual", "jurisdiccion", "oa_nombre",
    "nombre_normalizado_exacto", "oa_personas_por_cuit", "oa_person_key",
    "oa_anios_seleccionados", "evidencia_misma_institucion_anios",
    "presentacion_cargo_actual_localizada", "ultimo_anio_oa", "ultimo_organismo_oa",
    "ultimo_cargo_oa", "estado_revision_identidad", "siguiente_accion",
]
series_fields = [
    "persona_id", "persona", "nivel_cargo_actual", "jurisdiccion_actual", "oa_nombre",
    "oa_person_key", "estado_revision_identidad", "anio", "tipo_ddjj", "rectificativa",
    "dj_id", "organismo_oa", "cargo_oa", "total_bienes_ars", "deudas_ars",
    "diferencia_valuacion_ars", "ingresos_neto_gastos_ars", "fuente_url", "publicable_en_tab",
]

write_csv(QUEUE_PATH, queue_rows, queue_fields)
write_csv(IDENTITY_PATH, list(identity_by_person.values()), identity_fields)
write_csv(SERIES_PATH, series_rows, series_fields)

status_counts: dict[str, int] = defaultdict(int)
for row in queue_rows:
    status_counts[str(row["estado_busqueda_patrimonial"])] += 1
iteration_counts: dict[str, int] = defaultdict(int)
for row in queue_rows:
    iteration_counts[str(row["iteracion_sugerida"])] += 1
frozen_rows = [row for row in queue_rows if row["estado_investigacion"] == "freezado"]
publishable_rows = [row for row in queue_rows if row["estado_investigacion"] == "cerrado_publicable"]
frozen_status_counts: dict[str, int] = defaultdict(int)
for row in frozen_rows:
    frozen_status_counts[str(row["estado_busqueda_patrimonial"])] += 1

summary = {
    "corte": "2026-09-01",
    "universo_cargos": len(roster),
    "personas_con_candidato_oa_unico": len(identity_by_person),
    "filas_persona_anio_oa_preseleccionadas": len(series_rows),
    "preclasificaciones_fuertes_misma_institucion": len(strong_candidates),
    "homonimias_resueltas_preclasificadas": len(homonym_resolution_ids),
    "homonimias_auditadas_con_descartes": len(homonym_exclusions),
    "homonimias_descartadas_sin_registro_oa_compatible": len(full_homonym_exclusion_by_id),
    "homonimias_depuradas_parcialmente": len(homonym_exclusions) - len(full_homonym_exclusion_by_id),
    "primera_iteracion_revision_manual": len(iteration_one),
    "primera_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(1, set())),
    "segunda_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(2, set())),
    "tercera_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(3, set())),
    "cuarta_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(4, set())),
    "quinta_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(5, set())),
    "sexta_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(6, set())),
    "septima_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(7, set())),
    "octava_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(8, set())),
    "novena_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(9, set())),
    "decima_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(10, set())),
    "undecima_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(11, set())),
    "duodecima_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(12, set())),
    "decimotercera_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(13, set())),
    "decimocuarta_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(14, set())),
    "decimoquinta_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(15, set())),
    "decimoctava_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(18, set())),
    "decimonovena_iteracion_identidades_confirmadas": len(confirmed_by_iteration.get(19, set())),
    "iteraciones_completadas": len(confirmed_by_iteration),
    "ultima_iteracion_auditoria": max(
        set(confirmed_by_iteration) | set(homonym_exclusion_iteration_by_id.values()),
        default=0,
    ),
    "identidades_confirmadas_por_iteracion": {
        str(key): len(value) for key, value in sorted(confirmed_by_iteration.items())
    },
    "identidades_confirmadas_total": len(confirmed_all),
    "trayectorias_auditadas_dashboard": 8 + len(confirmed_all),
    "trayectorias_auditadas_activas": 5 + len(confirmed_all),
    "series_ya_curadas": sum(bool(row["serie_tab_id"]) for row in roster),
    "expansion_universo_estado": "freezada",
    "expansion_universo_fecha": FREEZE_DATE,
    "motivo_freeze": FREEZE_REASON,
    "cargos_freezados": len(frozen_rows),
    "cargos_publicables": len(publishable_rows),
    "pendientes_preservados_por_estado": dict(sorted(frozen_status_counts.items())),
    "por_estado_busqueda": dict(sorted(status_counts.items())),
    "por_iteracion_sugerida": dict(sorted(iteration_counts.items(), key=lambda item: int(item[0]))),
    "advertencia": "Una coincidencia nominal y una preclasificación automática no confirman identidad. Los importes candidatos no se publican en el tab hasta cotejar identificador, organismo y cargo.",
    "disponibilidad_2025": "El portal oficial informa que la planta completa del ejercicio 2025 estará disponible entre septiembre y octubre de 2026.",
}
SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert len(queue_rows) == 789
expected_identity_ids = {
    row["persona_id"]
    for row in roster
    if row["oa_historial_2017_2024_estado"] == "nombre_compatible_unico_en_oa"
} | homonym_resolution_ids
assert set(identity_by_person) == expected_identity_ids
assert sum(status_counts.values()) == 789
assert len(frozen_rows) == 491
assert len(publishable_rows) == 298
assert len(iteration_one) == min(30, len(strong_candidates))
print(
    f"OK: cola patrimonial · {len(queue_rows)} cargos · {len(identity_by_person)} candidatos OA · "
    f"{len(series_rows)} filas persona-año · {len(strong_candidates)} preclasificaciones fuertes"
)
