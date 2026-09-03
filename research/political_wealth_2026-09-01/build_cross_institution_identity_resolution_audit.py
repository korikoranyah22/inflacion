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
CANDIDATE_SERIES_PATH = DERIVED / "active_politician_oa_candidate_series_2017_2024.csv"
OUTPUT_PATH = DERIVED / "active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv"

DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"

CASES = {
    "sen-bullrich-patricia": {
        "identity_url": "https://www.argentina.gob.ar/normativa/nacional/decreto-6-2023-394974/texto",
        "identity_local": "sources/identity_crosswalk/decreto_6_2023_patricia_bullrich.html",
        "historical_role_tokens": ("MINISTERIO DE SEGURIDAD", "MINISTRA DE SEGURIDAD"),
        "bridge_label": "Ministerio de Seguridad",
    },
    "sen-soria-martin-ignacio": {
        "identity_url": "https://www.argentina.gob.ar/normativa/nacional/decreto-225-2021-348277/texto",
        "identity_local": "sources/identity_crosswalk/decreto_225_2021_martin_soria.html",
        "historical_role_tokens": ("MINISTERIO DE JUSTICIA", "MINISTRO DE JUSTICIA"),
        "bridge_label": "Ministerio de Justicia y Derechos Humanos",
    },
    "dip-serquis-adriana-cristina": {
        "identity_url": "https://www.argentina.gob.ar/normativa/nacional/decreto-380-2024-398809/texto",
        "identity_local": "sources/identity_crosswalk/decreto_380_2024_adriana_serquis.html",
        "historical_role_tokens": ("COMISION NACIONAL DE ENERGIA ATOMICA", "PRESIDENTA"),
        "bridge_label": "Presidencia de la CNEA",
    },
    "dip-pareja-sebastian": {
        "identity_url": "https://www.argentina.gob.ar/normativa/nacional/decreto-145-2024-396662/texto",
        "identity_local": "sources/identity_crosswalk/decreto_145_2024_sebastian_pareja.html",
        "historical_role_tokens": ("INTEGRACION SOCIO URBANA", "SUBSECRETARIO"),
        "bridge_label": "Subsecretaría de Integración Socio-urbana",
        "identity_name": "Sebastián Miguel Pareja",
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
    starts = [match.start() for match in re.finditer(re.escape(normalized_name), source_text)]
    assert starts, f"No aparece el nombre completo en la fuente identificatoria: {full_name}"
    pattern = re.compile(r"D\s*N\s*I(?:\s+N(?:\s*O)?)?\s+(\d{1,2})\s+(\d{3})\s+(\d{3})")
    values = set()
    for start in starts:
        window = source_text[max(0, start - 80) : start + len(normalized_name) + 650]
        for match in pattern.finditer(window):
            values.add("".join(match.groups()).lstrip("0"))
    return values


with IDENTITY_PATH.open(encoding="utf-8-sig", newline="") as handle:
    identity_by_id = {row["persona_id"]: row for row in csv.DictReader(handle)}
with CANDIDATE_SERIES_PATH.open(encoding="utf-8-sig", newline="") as handle:
    candidate_rows = list(csv.DictReader(handle))

candidate_by_id: dict[str, list[dict[str, str]]] = {person_id: [] for person_id in CASES}
for row in candidate_rows:
    if row["persona_id"] in candidate_by_id:
        candidate_by_id[row["persona_id"]].append(row)

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
    assert identity["nivel_cargo"] in {"Diputados nacionales", "Senado nacional"}
    assert identity["presentacion_cargo_actual_localizada"] == "sí"
    assert identity["oa_personas_por_cuit"] == "1"
    assert identity["oa_anios_seleccionados"]
    assert set(normalize(identity["persona"]).split()).issubset(set(normalize(identity["oa_nombre"]).split()))

    source_path = ROOT / str(case["identity_local"])
    assert source_path.is_file(), f"Falta respaldo identificatorio para {person_id}"
    source_text = visible_text(source_path.read_text(encoding="utf-8", errors="replace"))
    official_candidates = dni_candidates_near_name(
        source_text, str(case.get("identity_name", identity["persona"]))
    )

    cuits = oa_cuits_by_name[identity["oa_nombre"]]
    assert len(cuits) == 1
    cuit = next(iter(cuits))
    assert masked_person_key(cuit) == identity["oa_person_key"]
    oa_document = re.sub(r"\D", "", cuit)[2:-1].lstrip("0")
    assert oa_document in official_candidates, f"El identificador oficial no coincide con OA: {person_id}"

    oa_role_text = normalize(
        " ".join(f"{row['organismo_oa']} {row['cargo_oa']}" for row in candidate_by_id[person_id])
    )
    assert all(normalize(token) in oa_role_text for token in case["historical_role_tokens"])

    rows.append(
        {
            "persona_id": person_id,
            "persona": identity["persona"],
            "nivel_cargo_actual": identity["nivel_cargo"],
            "jurisdiccion_actual": identity["jurisdiccion"],
            "oa_nombre_resuelto": identity["oa_nombre"],
            "oa_person_key": identity["oa_person_key"],
            "metodo_resolucion": "presentacion_camara_actual_y_decreto_con_documento_oa_coincidente",
            "nivel_evidencia": "identificador_oficial_coincidente_y_puente_cargo_oa",
            "identificador_oficial_vs_oa": "sí · cotejo reservado",
            "puente_institucional_oa": str(case["bridge_label"]),
            "fuente_identidad_url": str(case["identity_url"]),
            "respaldo_identidad_local": str(case["identity_local"]),
            "fuente_serie_url": DATASET_URL,
            "nota_evidencia": (
                f"La presentación de la Cámara acredita el cargo legislativo vigente. El decreto oficial vincula "
                f"a {identity['persona']} con {case['bridge_label']} y su documento coincide de forma reservada "
                "con la única clave fiscal OA; no se publica el identificador."
            ),
        }
    )

assert len(rows) == 4
with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print("OK: 4 puentes institucionales auditados · 4 cotejos reservados de identificador")
