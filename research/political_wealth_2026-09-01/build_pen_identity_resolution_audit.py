from __future__ import annotations

import csv
import hashlib
import html
import io
import re
import unicodedata
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"
IDENTITY_PATH = DERIVED / "active_politician_oa_identity_review_2026-09-01.csv"
OUTPUT_PATH = DERIVED / "active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv"

DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"

CASES = {
    "pen-villarruel-victoria-eugenia": {
        "current_name": "Victoria Eugenia Villarruel",
        "current_role": "Vicepresidenta de la Nación y presidenta del Senado",
        "current_url": "https://www.senado.gob.ar/presidencia",
        "current_local": "sources/active_roster/senado_presidencia_2026-09-01.html",
        "identity_url": "https://www.senado.gob.ar/presidencia",
        "identity_local": "sources/active_roster/senado_presidencia_2026-09-01.html",
        "identifier_required": False,
    },
    "pen-santilli-diego-cesar": {
        "current_name": "Diego César Santilli",
        "current_role": "Jefe de Gabinete de Ministros",
        "current_url": "https://www.argentina.gob.ar/normativa/nacional/norma-427132/texto",
        "current_local": "sources/active_roster/decreto_548_2026_jefe_gabinete.html",
        "identity_url": "https://www.argentina.gob.ar/normativa/nacional/norma-427132/texto",
        "identity_local": "sources/active_roster/decreto_548_2026_jefe_gabinete.html",
        "identifier_required": True,
    },
    "pen-presti-carlos-alberto": {
        "current_name": "Carlos Alberto Presti",
        "current_role": "Ministro de Defensa",
        "current_url": "https://www.argentina.gob.ar/defensa/transparencia/autoridades-personal",
        "current_local": "sources/active_roster/defensa_autoridades_2026-09-01.html",
        "identity_url": "https://www.argentina.gob.ar/defensa/transparencia/autoridades-personal",
        "identity_local": "sources/active_roster/defensa_autoridades_2026-09-01.html",
        "identifier_required": True,
    },
    "pen-mahiques-juan-bautista": {
        "current_name": "Juan Bautista Mahiques",
        "current_role": "Ministro de Justicia",
        "current_url": "https://www.argentina.gob.ar/justicia/transparencia/autoridades-personal",
        "current_local": "sources/active_roster/justicia_autoridades_2026-09-01.html",
        "identity_url": "https://www.argentina.gob.ar/justicia/transparencia/autoridades-personal",
        "identity_local": "sources/active_roster/justicia_autoridades_2026-09-01.html",
        "identifier_required": True,
    },
    "pen-monteoliva-alejandra-susana": {
        "current_name": "Alejandra Susana Monteoliva",
        "current_role": "Ministra de Seguridad Nacional",
        "current_url": "https://www.argentina.gob.ar/seguridad/transparencia/autoridades-personal",
        "current_local": "sources/active_roster/seguridad_autoridades_2026-09-01.html",
        "identity_url": "https://www.argentina.gob.ar/seguridad/transparencia/autoridades-personal",
        "identity_local": "sources/active_roster/seguridad_autoridades_2026-09-01.html",
        "identifier_required": True,
    },
    "pen-lugones-mario-ivan": {
        "current_name": "Mario Iván Lugones",
        "current_role": "Ministro de Salud",
        "current_url": "https://www.argentina.gob.ar/salud/transparencia/autoridades-personal",
        "current_local": "sources/active_roster/salud_autoridades_2026-09-01.html",
        "identity_url": "https://www.argentina.gob.ar/salud/transparencia/autoridades-personal",
        "identity_local": "sources/active_roster/salud_autoridades_2026-09-01.html",
        "identifier_required": True,
    },
    "pen-pettovello-sandra-viviana": {
        "current_name": "Sandra Viviana Pettovello",
        "current_role": "Ministra de Capital Humano",
        "current_url": "https://www.argentina.gob.ar/capital-humano/transparencia-ministerio-de-capital-humano/organigrama-autoridades-y-personal",
        "current_local": "sources/active_roster/capital_humano_autoridades_2026-09-01.html",
        "identity_url": "https://www.argentina.gob.ar/capital-humano/transparencia-ministerio-de-capital-humano/organigrama-autoridades-y-personal",
        "identity_local": "sources/active_roster/capital_humano_autoridades_2026-09-01.html",
        "identifier_required": True,
    },
    "pen-sturzenegger-federico-adolfo": {
        "current_name": "Federico Sturzenegger",
        "current_role": "Ministro de Desregulación y Transformación del Estado",
        "current_url": "https://www.argentina.gob.ar/desregulacion",
        "current_local": "sources/active_roster/desregulacion_autoridad_2026-09-01.html",
        "identity_url": "https://www.argentina.gob.ar/normativa/nacional/norma-401217/texto",
        "identity_local": "sources/identity_crosswalk/decreto_586_2024_sturzenegger.html",
        "identifier_required": True,
    },
}


def clean(value: str) -> str:
    return " ".join((value or "").split())


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", html.unescape(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^A-Za-z0-9]+", " ", value).upper()
    return " ".join(value.split())


def visible_text(raw_html: str) -> str:
    without_scripts = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw_html)
    return normalize(re.sub(r"(?s)<[^>]+>", " ", without_scripts))


def masked_person_key(cuit: str) -> str:
    return hashlib.sha256(cuit.encode("utf-8")).hexdigest()[:16]


def dni_candidates_near_name(source_text: str, full_name: str) -> set[str]:
    normalized_name = normalize(full_name)
    values = set()
    pattern = re.compile(r"D\s*N\s*I(?:\s+N(?:\s*O)?)?\s+(\d{1,2})\s+(\d{3})\s+(\d{3})")
    starts = [match.start() for match in re.finditer(re.escape(normalized_name), source_text)]
    assert starts, f"No aparece el nombre completo en la fuente identificatoria: {full_name}"
    for start in starts:
        window = source_text[max(0, start - 80) : start + len(normalized_name) + 500]
        for match in pattern.finditer(window):
            values.add("".join(match.groups()).lstrip("0"))
    return values


with IDENTITY_PATH.open(encoding="utf-8-sig", newline="") as handle:
    identity_by_id = {row["persona_id"]: row for row in csv.DictReader(handle)}

oa_names = {identity_by_id[person_id]["oa_nombre"] for person_id in CASES}
oa_cuits_by_name: dict[str, set[str]] = {name: set() for name in oa_names}
with zipfile.ZipFile(ZIP_PATH) as archive:
    for year in range(2017, 2025):
        member = f"declaraciones-juradas-{year}-consolidado-al-20251222.csv"
        with archive.open(member) as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text_handle:
                for row in csv.DictReader(text_handle):
                    name = clean(row.get("funcionario_apellido_nombre", ""))
                    if name in oa_cuits_by_name and row.get("cuit"):
                        oa_cuits_by_name[name].add(clean(row["cuit"]))

rows: list[dict[str, str]] = []
for person_id, case in CASES.items():
    identity = identity_by_id[person_id]
    assert identity["nivel_cargo"] == "Conducción superior PEN"
    assert sorted(normalize(identity["persona"]).split()) == sorted(normalize(identity["oa_nombre"]).split())
    assert identity["oa_personas_por_cuit"] == "1"
    assert identity["oa_anios_seleccionados"]

    current_path = ROOT / str(case["current_local"])
    identity_path = ROOT / str(case["identity_local"])
    assert current_path.is_file()
    assert identity_path.is_file()
    current_text = visible_text(current_path.read_text(encoding="utf-8", errors="replace"))
    identity_text = visible_text(identity_path.read_text(encoding="utf-8", errors="replace"))
    assert normalize(str(case["current_name"])) in current_text

    cuits = oa_cuits_by_name[identity["oa_nombre"]]
    assert len(cuits) == 1
    cuit = next(iter(cuits))
    assert masked_person_key(cuit) == identity["oa_person_key"]

    if case["identifier_required"]:
        official_candidates = dni_candidates_near_name(identity_text, identity["persona"])
        oa_document = re.sub(r"\D", "", cuit)[2:-1].lstrip("0")
        assert oa_document in official_candidates, f"El identificador oficial no coincide con OA: {person_id}"
        identifier_match = "sí · cotejo reservado"
        evidence_level = "identificador_oficial_coincidente"
        method = "autoridad_pen_oficial_con_documento_y_clave_oa_coincidente"
        note = (
            f"La fuente oficial identifica a {case['current_name']} en el cargo de {case['current_role']}; "
            "el documento coincide de forma reservada con la única clave fiscal OA y no se publica en derivados."
        )
    else:
        identifier_match = "no · la fuente vigente no lo publica"
        evidence_level = "nombre_completo_cargo_y_trayectoria_oa_unica"
        method = "autoridad_pen_vigente_y_trayectoria_oa_unica"
        note = (
            f"La fuente oficial vigente identifica a {case['current_name']} en el cargo de {case['current_role']}; "
            "el nombre completo exacto, la única clave fiscal OA y la continuidad institucional sostienen el cruce, "
            "sin presentarlo como cotejo documental."
        )

    rows.append(
        {
            "persona_id": person_id,
            "persona": identity["persona"],
            "oa_nombre_resuelto": identity["oa_nombre"],
            "oa_person_key": identity["oa_person_key"],
            "metodo_resolucion": method,
            "nivel_evidencia": evidence_level,
            "identificador_oficial_vs_oa": identifier_match,
            "nombre_fuente_actual": str(case["current_name"]),
            "cargo_actual": str(case["current_role"]),
            "fuente_cargo_actual_url": str(case["current_url"]),
            "respaldo_cargo_actual_local": str(case["current_local"]),
            "fuente_identidad_url": str(case["identity_url"]),
            "respaldo_identidad_local": str(case["identity_local"]),
            "fuente_serie_url": DATASET_URL,
            "nota_evidencia": note,
        }
    )

assert len(rows) == 8
assert sum(row["identificador_oficial_vs_oa"].startswith("sí") for row in rows) == 7
with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print("OK: 8 autoridades PEN auditadas · 7 cotejos reservados de identificador · 1 cruce de nombre, cargo y trayectoria")
