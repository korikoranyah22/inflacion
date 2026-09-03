from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
SOURCES = ROOT / "sources" / "active_roster"

parser = argparse.ArgumentParser(description="Construye una tanda verificada de trayectorias patrimoniales.")
parser.add_argument("--batch", type=int, default=1, help="Número de tanda; 1 usa la cola inicial y 2+ toma bloques de 30 de la cola 2.")
arguments = parser.parse_args()
BATCH_NUMBER = arguments.batch
assert BATCH_NUMBER >= 1

QUEUE_PATH = DERIVED / "active_politician_research_queue_2026-09-01.csv"
IDENTITY_PATH = DERIVED / "active_politician_oa_identity_review_2026-09-01.csv"
CANDIDATE_SERIES_PATH = DERIVED / "active_politician_oa_candidate_series_2017_2024.csv"
HCDN_ROSTER_PATH = SOURCES / "hcdn_diputados_vigentes_2026-09-01.csv"
HCDN_DDJJ_PATH = SOURCES / "hcdn_ddjj_ejercicio_2025_2026-09-01.html"
SENATE_ROSTER_PATH = SOURCES / "senado_listado_vigente_2026-09-01.html"
SENATE_DDJJ_PATH = SOURCES / "senado_ddjj_2025_2026-09-01.html"
CFI_GOVERNORS_PATH = SOURCES / "cfi_gobernadores_2026-09-01.html"
CABA_ROSTER_PATH = ROOT / "sources" / "subnational_roster" / "caba_legisladores_vigentes_2026-09-01.xml"
PBA_DEPUTIES_ROSTER_PATH = (
    ROOT / "sources" / "subnational_roster" / "buenos_aires_diputados_vigentes_2026-09-01.html"
)
PBA_SENATORS_ROSTER_PATH = (
    ROOT / "sources" / "subnational_roster" / "buenos_aires_senadores_vigentes_2026-09-01.html"
)
SANTA_FE_DEPUTIES_ROSTER_PATHS = tuple(
    ROOT / "sources" / "subnational_roster" / filename
    for filename in (
        "santa_fe_diputados_vigentes_2026-09-01.html",
        "santa_fe_diputados_vigentes_p2_2026-09-01.html",
        "santa_fe_diputados_vigentes_p3_2026-09-01.html",
        "santa_fe_diputados_vigentes_p4_2026-09-01.html",
        "santa_fe_diputados_vigentes_p5_2026-09-01.html",
    )
)
SANTA_FE_SENATORS_ROSTER_PATH = (
    ROOT / "sources" / "subnational_roster" / "santa_fe_senadores_vigentes_2026-09-01.html"
)
RIO_NEGRO_ROSTER_PATH = (
    ROOT / "sources" / "subnational_roster" / "rio_negro_legisladores_vigentes_2026-09-01.csv"
)
CORDOBA_ROSTER_PATH = (
    ROOT / "sources" / "subnational_roster" / "cordoba_legisladores_vigentes_2026-09-01.json"
)
MISIONES_ROSTER_PATH = (
    ROOT / "sources" / "subnational_roster" / "misiones_diputados_vigentes_2026-09-01.html"
)
MACRO_PATH = DERIVED / "macro_deflators_2017_2025.csv"
BENCHMARK_RETURNS_PATH = DERIVED / "benchmark_annual_returns_2017_2025.csv"
PEN_RESOLUTIONS_PATH = (
    DERIVED / "active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv"
)
CROSS_INSTITUTION_RESOLUTIONS_PATH = (
    DERIVED / "active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv"
)

AUDIT_PATH = DERIVED / f"active_politician_identity_audit_iteration_{BATCH_NUMBER}_2026-09-01.csv"
SERIES_PATH = DERIVED / f"active_politician_verified_series_iteration_{BATCH_NUMBER}_2017_2024.csv"
BENCHMARK_PATH = DERIVED / f"active_politician_verified_benchmarks_iteration_{BATCH_NUMBER}_2017_2024.csv"
DASHBOARD_PATH = DERIVED / f"active_politician_verified_dashboard_iteration_{BATCH_NUMBER}.json"

DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
HCDN_ROSTER_URL = "https://www.hcdn.gob.ar/diputados/"
HCDN_DDJJ_URL = "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/index.html"
SENATE_ROSTER_URL = "https://www.senado.gob.ar/senadores/listados/listaSenadoRes"
SENATE_DDJJ_URL = "https://www.senado.gob.ar/administrativo/ddjj/"
CFI_GOVERNORS_URL = "https://cfi.org.ar/quienes_somos"
CABA_ROSTER_URL = "https://parlamentaria.legislatura.gob.ar/webservices/Json.asmx/GetDiputadosActivosNuevo"
CABA_DDJJ_URL = "https://www.legislatura.gob.ar/seccion/listado-diputados-djpi.html"
PBA_DEPUTIES_ROSTER_URL = "https://www.hcdiputados-ba.gov.ar/index.php?page=diputados&search=seccionBloques"
PBA_SENATORS_ROSTER_URL = "https://senado-ba.gov.ar/Senadores.aspx"
SANTA_FE_DEPUTIES_ROSTER_URL = "https://diputadossantafe.gov.ar/web/camara/diputados"
SANTA_FE_SENATORS_ROSTER_URL = "https://www.senadosantafe.gob.ar/"
RIO_NEGRO_ROSTER_URL = "https://web.legisrn.gov.ar/institucional/legisladores"
CORDOBA_ROSTER_URL = (
    "https://legislaturacba.gob.ar/wp-content/uploads/2026/01/COMPOSICI%C3%93N-DE-LA-C%C3%81MARA-2026-.json"
)
CORDOBA_DDJJ_URL = "https://legislaturacba.gob.ar/declaraciones-juradas/"
MISIONES_ROSTER_URL = "https://www.diputadosmisiones.gov.ar/nuevo/diputados"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^A-Za-z0-9]+", " ", value).upper()
    return " ".join(value.split())


def clean(value: str) -> str:
    return " ".join((value or "").split())


def decimal_or_none(value: str) -> Decimal | None:
    try:
        return Decimal(value) if clean(value) else None
    except InvalidOperation:
        return None


def text(value: Decimal | None, places: int = 2) -> str:
    if value is None:
        return ""
    quantum = Decimal("1").scaleb(-places)
    return str(value.quantize(quantum))


def percent_change(end: Decimal, start: Decimal) -> Decimal | None:
    if start == 0:
        return None
    return (end / start - Decimal("1")) * Decimal("100")


def cagr(end: Decimal, start: Decimal, years: int) -> Decimal | None:
    if years <= 0 or start <= 0 or end < 0:
        return None
    return Decimal(str((float(end / start) ** (1 / years) - 1) * 100))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def canonical_district(value: str) -> str:
    normalized = normalize(value)
    if normalized in {"CABA", "CIUDAD DE BUENOS AIRES", "CIUDAD AUTONOMA DE BUENOS AIRES"}:
        return "CABA"
    return normalized


def official_name_match_kind(oa_name: str, surname: str, given: str) -> str:
    oa = normalize(oa_name)
    chamber = normalize(f"{surname} {given}")
    if oa == chamber:
        return "exacta"
    if oa.startswith(chamber + " "):
        return "compatible_con_nombre_adicional_en_oa"
    if chamber.startswith(oa + " "):
        return "compatible_con_nombres_adicionales_en_camara"
    return "sin_coincidencia"


def unordered_name_match_kind(first: str, second: str) -> str:
    first_tokens = normalize(first).split()
    second_tokens = normalize(second).split()
    return "exacta_por_tokens" if sorted(first_tokens) == sorted(second_tokens) else "sin_coincidencia"


def unordered_name_compatibility(oa_name: str, current_name: str) -> str:
    oa_tokens = normalize(oa_name).split()
    current_tokens = normalize(current_name).split()
    if sorted(oa_tokens) == sorted(current_tokens):
        return "exacta_por_tokens"
    if set(current_tokens).issubset(set(oa_tokens)):
        return "compatible_con_nombres_adicionales_en_oa"
    if set(oa_tokens).issubset(set(current_tokens)):
        return "compatible_con_nombres_adicionales_en_fuente_actual"
    return "sin_coincidencia"


class HcdnTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_target_table = False
        self.in_cell = False
        self.current_cell: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and attributes.get("id") == "tabla":
            self.in_target_table = True
        elif self.in_target_table and tag == "tr":
            self.current_row = []
        elif self.in_target_table and tag == "td":
            self.in_cell = True
            self.current_cell = []

    def handle_data(self, data: str) -> None:
        if self.in_target_table and self.in_cell:
            self.current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_target_table and tag == "td":
            self.current_row.append(clean(" ".join(self.current_cell)))
            self.in_cell = False
        elif self.in_target_table and tag == "tr":
            if self.current_row:
                self.rows.append(self.current_row)
        elif self.in_target_table and tag == "table":
            self.in_target_table = False


def parse_hcdn_presentations() -> list[dict[str, str]]:
    parser = HcdnTableParser()
    parser.feed(HCDN_DDJJ_PATH.read_text(encoding="utf-8", errors="replace"))
    rows = []
    for cells in parser.rows:
        if len(cells) >= 4:
            rows.append(
                {
                    "apellido": cells[0],
                    "nombre": cells[1],
                    "distrito": cells[2],
                    "tipo": cells[3],
                }
            )
    assert rows, "No se pudieron leer las presentaciones HCDN 2025 respaldadas"
    return rows


class AllTableRowsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.table_depth = 0
        self.in_cell = False
        self.current_cell: list[str] = []
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.table_depth += 1
        elif self.table_depth and tag == "tr":
            self.current_row = []
        elif self.table_depth and tag == "td":
            self.in_cell = True
            self.current_cell = []

    def handle_data(self, data: str) -> None:
        if self.table_depth and self.in_cell:
            self.current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.table_depth and tag == "td":
            self.current_row.append(clean(" ".join(self.current_cell)))
            self.in_cell = False
        elif self.table_depth and tag == "tr":
            if self.current_row:
                self.rows.append(self.current_row)
        elif tag == "table" and self.table_depth:
            self.table_depth -= 1


class SenateRosterNameParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        if str(attributes.get("href", "")).startswith("/senadores/senador/") and attributes.get("title"):
            self.names.add(clean(str(attributes["title"])))


class CFIGovernorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.fragments: list[str] = []
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = str(attributes.get("class", "")).split()
        if tag == "div" and not self.depth and "prov-item" in classes:
            self.depth = 1
            self.fragments = []
        elif tag == "div" and self.depth:
            self.depth += 1

    def handle_data(self, data: str) -> None:
        if self.depth:
            value = clean(data)
            if value:
                self.fragments.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag != "div" or not self.depth:
            return
        self.depth -= 1
        if self.depth:
            return
        for value in self.fragments:
            match = re.match(r"^Gobernador(?:a)?\s+(.+)$", value, flags=re.IGNORECASE)
            if match:
                self.names.add(clean(match.group(1)))
                break


class PBADeputiesRosterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_person_link = False
        self.fragments: list[str] = []
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        href = str(attributes.get("href", ""))
        classes = str(attributes.get("class", "")).split()
        if tag == "a" and href.startswith("index.php?page=diputado&id=") and "text-info" in classes:
            self.in_person_link = True
            self.fragments = []

    def handle_data(self, data: str) -> None:
        if self.in_person_link:
            self.fragments.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.in_person_link:
            name = clean(" ".join(self.fragments))
            if name:
                self.names.add(name)
            self.in_person_link = False


class PBASenatorsRosterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_hidden_name = False
        self.fragments: list[str] = []
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = str(attributes.get("class", "")).split()
        if tag == "div" and "nombreHidden" in classes:
            self.in_hidden_name = True
            self.fragments = []

    def handle_data(self, data: str) -> None:
        if self.in_hidden_name:
            self.fragments.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.in_hidden_name:
            name = clean(" ".join(self.fragments))
            if name:
                self.names.add(name)
            self.in_hidden_name = False


class SantaFeDeputiesRosterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.card_depth = 0
        self.in_heading = False
        self.fragments: list[str] = []
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = str(attributes.get("class", "")).split()
        if tag == "div" and not self.card_depth and "autoridad-little" in classes:
            self.card_depth = 1
        elif tag == "div" and self.card_depth:
            self.card_depth += 1
        elif tag == "h4" and self.card_depth:
            self.in_heading = True
            self.fragments = []

    def handle_data(self, data: str) -> None:
        if self.in_heading:
            self.fragments.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h4" and self.in_heading:
            name = clean(" ".join(self.fragments))
            if name:
                self.names.add(name)
            self.in_heading = False
        elif tag == "div" and self.card_depth:
            self.card_depth -= 1


class SantaFeSenatorsRosterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.field_depth = 0
        self.field_kind = ""
        self.fragments: list[str] = []
        self.given_names: list[str] = []
        self.surnames: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = str(attributes.get("class", "")).split()
        if tag == "div" and not self.field_depth:
            if "field-name-field-nombre" in classes:
                self.field_kind = "given"
                self.field_depth = 1
                self.fragments = []
            elif "field-name-field-apellido" in classes:
                self.field_kind = "surname"
                self.field_depth = 1
                self.fragments = []
        elif tag == "div" and self.field_depth:
            self.field_depth += 1

    def handle_data(self, data: str) -> None:
        if self.field_depth:
            self.fragments.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "div" or not self.field_depth:
            return
        self.field_depth -= 1
        if self.field_depth:
            return
        value = clean(" ".join(self.fragments))
        if value:
            target = self.given_names if self.field_kind == "given" else self.surnames
            target.append(value)
        self.field_kind = ""


class MisionesRosterParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_name = False
        self.fragments: list[str] = []
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = str(attributes.get("class", "")).split()
        if tag == "p" and {"card_description", "m-2"}.issubset(classes):
            self.in_name = True
            self.fragments = []

    def handle_data(self, data: str) -> None:
        if self.in_name:
            self.fragments.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self.in_name:
            name = clean(" ".join(self.fragments))
            if name:
                self.names.add(name)
            self.in_name = False


def parse_senate_presentations() -> list[dict[str, str]]:
    parser = AllTableRowsParser()
    parser.feed(SENATE_DDJJ_PATH.read_text(encoding="utf-8", errors="replace"))
    rows = [
        {"apellido": cells[0], "nombre": cells[1], "distrito": cells[2], "tipo": f"{cells[3]} {cells[4]}"}
        for cells in parser.rows
        if len(cells) == 5 and cells[4] == "2025"
    ]
    assert rows, "No se pudieron leer las presentaciones Senado 2025 respaldadas"
    return rows


def parse_senate_roster_names() -> set[str]:
    parser = SenateRosterNameParser()
    parser.feed(SENATE_ROSTER_PATH.read_text(encoding="utf-8", errors="replace"))
    assert len(parser.names) == 72, f"Se esperaban 72 nombres vigentes del Senado y llegaron {len(parser.names)}"
    return parser.names


def parse_cfi_governor_names() -> set[str]:
    parser = CFIGovernorParser()
    parser.feed(CFI_GOVERNORS_PATH.read_text(encoding="utf-8", errors="replace"))
    assert len(parser.names) == 23, (
        f"Se esperaban 23 gobernadores provinciales vigentes en CFI —CABA publica Jefe de Gobierno— "
        f"y llegaron {len(parser.names)}"
    )
    return parser.names


def parse_caba_roster() -> list[dict[str, str]]:
    root = ET.parse(CABA_ROSTER_PATH).getroot()
    rows = []
    for person in root:
        values = {child.tag.split("}")[-1]: clean(child.text or "") for child in person}
        if values.get("apellido") and values.get("nombre"):
            rows.append({"apellido": values["apellido"], "nombre": values["nombre"]})
    assert len(rows) == 60, f"Se esperaban 60 legisladores vigentes de CABA y llegaron {len(rows)}"
    return rows


def parse_pba_deputies_roster_names() -> set[str]:
    parser = PBADeputiesRosterParser()
    parser.feed(PBA_DEPUTIES_ROSTER_PATH.read_text(encoding="utf-8", errors="replace"))
    assert len(parser.names) == 92, (
        f"Se esperaban 92 diputados provinciales vigentes de Buenos Aires y llegaron {len(parser.names)}"
    )
    return parser.names


def parse_pba_senators_roster_names() -> set[str]:
    parser = PBASenatorsRosterParser()
    parser.feed(PBA_SENATORS_ROSTER_PATH.read_text(encoding="utf-8", errors="replace"))
    assert len(parser.names) == 46, (
        f"Se esperaban 46 senadores provinciales vigentes de Buenos Aires y llegaron {len(parser.names)}"
    )
    return parser.names


def parse_santa_fe_deputies_roster_names() -> set[str]:
    names: set[str] = set()
    for path in SANTA_FE_DEPUTIES_ROSTER_PATHS:
        parser = SantaFeDeputiesRosterParser()
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        names.update(parser.names)
    assert len(names) == 50, f"Se esperaban 50 diputados santafesinos vigentes y llegaron {len(names)}"
    return names


def parse_santa_fe_senators_roster_names() -> set[str]:
    parser = SantaFeSenatorsRosterParser()
    parser.feed(SANTA_FE_SENATORS_ROSTER_PATH.read_text(encoding="utf-8", errors="replace"))
    assert len(parser.given_names) == len(parser.surnames) == 19, (
        "La nómina santafesina debía contener 19 pares de nombres y apellidos de senadores"
    )
    names = {f"{given} {surname}" for given, surname in zip(parser.given_names, parser.surnames)}
    assert len(names) == 19, f"Se esperaban 19 senadores santafesinos vigentes y llegaron {len(names)}"
    return names


def parse_misiones_roster_names() -> set[str]:
    parser = MisionesRosterParser()
    parser.feed(MISIONES_ROSTER_PATH.read_text(encoding="utf-8", errors="replace"))
    assert len(parser.names) == 40, (
        f"Se esperaban 40 representantes misioneros vigentes y llegaron {len(parser.names)}"
    )
    return parser.names


queue = read_csv(QUEUE_PATH)
identity_rows = read_csv(IDENTITY_PATH)
candidate_rows = read_csv(CANDIDATE_SERIES_PATH)
hcdn_roster = read_csv(HCDN_ROSTER_PATH)
hcdn_presentations = parse_hcdn_presentations()
senate_roster_names = parse_senate_roster_names()
senate_presentations = parse_senate_presentations()
cfi_governor_names = parse_cfi_governor_names()
caba_roster = parse_caba_roster()
pba_deputies_roster_names = parse_pba_deputies_roster_names()
pba_senators_roster_names = parse_pba_senators_roster_names()
santa_fe_deputies_roster_names = parse_santa_fe_deputies_roster_names()
santa_fe_senators_roster_names = parse_santa_fe_senators_roster_names()
rio_negro_roster = read_csv(RIO_NEGRO_ROSTER_PATH)
assert len(rio_negro_roster) == 46, f"Se esperaban 46 legisladores rionegrinos y llegaron {len(rio_negro_roster)}"
cordoba_roster = [
    row
    for row in json.loads(CORDOBA_ROSTER_PATH.read_text(encoding="utf-8-sig"))
    if clean(str(row.get("nombre", ""))) and clean(str(row.get("apellido", "")))
]
assert len(cordoba_roster) == 70, f"Se esperaban 70 legisladores cordobeses y llegaron {len(cordoba_roster)}"
misiones_roster_names = parse_misiones_roster_names()
macro_rows = read_csv(MACRO_PATH)
benchmark_return_rows = read_csv(BENCHMARK_RETURNS_PATH)
homonym_resolutions_by_iteration: dict[int, list[dict[str, str]]] = {}
for resolution_path in sorted(DERIVED.glob("active_politician_homonymy_resolutions_iteration_*_2026-09-01.csv")):
    match = re.search(r"iteration_(\d+)_", resolution_path.name)
    assert match
    homonym_resolutions_by_iteration[int(match.group(1))] = read_csv(resolution_path)
assert {iteration: len(rows) for iteration, rows in homonym_resolutions_by_iteration.items()} == {13: 7, 14: 5, 15: 1, 17: 1}
homonym_resolution_by_id = {
    row["persona_id"]: row
    for rows in homonym_resolutions_by_iteration.values()
    for row in rows
}
assert len(homonym_resolution_by_id) == 14

queue_by_id = {row["persona_id"]: row for row in queue}
strong_pool = sorted(
    (
        queue_by_id[row["persona_id"]]
        for row in identity_rows
        if row["estado_revision_identidad"]
        in {"preclasificacion_fuerte_misma_institucion", "identidad_confirmada_cruce_oficial"}
        and row["nivel_cargo"] in {"Diputados nacionales", "Senado nacional"}
        and row["persona_id"] not in homonym_resolution_by_id
    ),
    key=lambda row: (row["nivel_cargo"], normalize(row["persona"])),
)
assert len(strong_pool) == 149
if BATCH_NUMBER <= 5:
    start = (BATCH_NUMBER - 1) * 30
    batch = strong_pool[start : start + 30]
    expected_batch_size = min(30, max(0, len(strong_pool) - start))
    batch_scope = "cargo_legislativo_nacional_actual"
    assert expected_batch_size > 0, (
        f"La tanda {BATCH_NUMBER} queda fuera de las {len(strong_pool)} preclasificaciones fuertes"
    )
    assert all(row["nivel_cargo"] in {"Diputados nacionales", "Senado nacional"} for row in batch)
elif BATCH_NUMBER == 6:
    governor_pool = sorted(
        (
            queue_by_id[row["persona_id"]]
            for row in identity_rows
            if row["nivel_cargo"] == "Gobernaciones"
            and row["oa_personas_por_cuit"] == "1"
            and row["oa_anios_seleccionados"]
            and row["presentacion_cargo_actual_localizada"] == "no"
        ),
        key=lambda row: normalize(row["persona"]),
    )
    assert len(governor_pool) == 11, f"Se esperaban 11 gobernadores con historial federal y llegaron {len(governor_pool)}"
    batch = governor_pool
    expected_batch_size = len(governor_pool)
    batch_scope = "historial_federal_previo_no_ddjj_provincial_actual"
elif BATCH_NUMBER == 7:
    caba_pool = sorted(
        (
            queue_by_id[row["persona_id"]]
            for row in identity_rows
            if row["nivel_cargo"] == "Legislaturas provinciales"
            and row["jurisdiccion"] == "Ciudad Autónoma de Buenos Aires"
            and row["oa_personas_por_cuit"] == "1"
            and row["oa_anios_seleccionados"]
        ),
        key=lambda row: normalize(row["persona"]),
    )
    assert len(caba_pool) == 21, f"Se esperaban 21 legisladores CABA con historial OA y llegaron {len(caba_pool)}"
    batch = caba_pool
    expected_batch_size = len(caba_pool)
    batch_scope = "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual"
elif BATCH_NUMBER == 8:
    pba_pool = sorted(
        (
            row
            for row in queue
            if row["nivel_cargo"] == "Legislaturas provinciales"
            and row["jurisdiccion"] == "Buenos Aires"
            and row["oa_historial_estado"] == "nombre_compatible_unico_en_oa"
        ),
        key=lambda row: (row["cargo"], normalize(row["persona"])),
    )
    assert len(pba_pool) == 45, (
        f"Se esperaban 45 legisladores bonaerenses con historial OA y llegaron {len(pba_pool)}"
    )
    assert sum(row["persona_id"].startswith("prov-ba-dip-") for row in pba_pool) == 26
    assert sum(row["persona_id"].startswith("prov-ba-sen-") for row in pba_pool) == 19
    batch = pba_pool
    expected_batch_size = len(pba_pool)
    batch_scope = "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual"
elif BATCH_NUMBER == 9:
    santa_fe_pool = sorted(
        (
            row
            for row in queue
            if row["nivel_cargo"] == "Legislaturas provinciales"
            and row["jurisdiccion"] == "Santa Fe"
            and row["oa_historial_estado"] == "nombre_compatible_unico_en_oa"
        ),
        key=lambda row: (row["cargo"], normalize(row["persona"])),
    )
    assert len(santa_fe_pool) == 16, (
        f"Se esperaban 16 legisladores santafesinos con historial OA y llegaron {len(santa_fe_pool)}"
    )
    assert sum(row["persona_id"].startswith("prov-sf-dip-") for row in santa_fe_pool) == 15
    assert sum(row["persona_id"].startswith("prov-sf-sen-") for row in santa_fe_pool) == 1
    batch = santa_fe_pool
    expected_batch_size = len(santa_fe_pool)
    batch_scope = "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual"
elif BATCH_NUMBER == 10:
    rio_negro_pool = sorted(
        (
            row
            for row in queue
            if row["nivel_cargo"] == "Legislaturas provinciales"
            and row["jurisdiccion"] == "Río Negro"
            and row["oa_historial_estado"] == "nombre_compatible_unico_en_oa"
        ),
        key=lambda row: normalize(row["persona"]),
    )
    assert len(rio_negro_pool) == 14, (
        f"Se esperaban 14 legisladores rionegrinos con historial OA y llegaron {len(rio_negro_pool)}"
    )
    batch = rio_negro_pool
    expected_batch_size = len(rio_negro_pool)
    batch_scope = "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual"
elif BATCH_NUMBER == 11:
    cordoba_pool = sorted(
        (
            row
            for row in queue
            if row["nivel_cargo"] == "Legislaturas provinciales"
            and row["jurisdiccion"] == "Córdoba"
            and row["oa_historial_estado"] == "nombre_compatible_unico_en_oa"
        ),
        key=lambda row: normalize(row["persona"]),
    )
    assert len(cordoba_pool) == 7, (
        f"Se esperaban 7 legisladores cordobeses con historial OA y llegaron {len(cordoba_pool)}"
    )
    batch = cordoba_pool
    expected_batch_size = len(cordoba_pool)
    batch_scope = "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual"
elif BATCH_NUMBER == 12:
    misiones_pool = sorted(
        (
            row
            for row in queue
            if row["nivel_cargo"] == "Legislaturas provinciales"
            and row["jurisdiccion"] == "Misiones"
            and row["oa_historial_estado"] == "nombre_compatible_unico_en_oa"
        ),
        key=lambda row: normalize(row["persona"]),
    )
    assert len(misiones_pool) == 7, (
        f"Se esperaban 7 representantes misioneros con historial OA y llegaron {len(misiones_pool)}"
    )
    batch = misiones_pool
    expected_batch_size = len(misiones_pool)
    batch_scope = "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual"
elif BATCH_NUMBER in {13, 14, 15, 17}:
    batch_resolutions = homonym_resolutions_by_iteration[BATCH_NUMBER]
    batch_resolution_by_id = {row["persona_id"]: row for row in batch_resolutions}
    batch = sorted(
        (queue_by_id[person_id] for person_id in batch_resolution_by_id),
        key=lambda row: (row["nivel_cargo"], normalize(row["persona"])),
    )
    expected_batch_size = len(batch_resolution_by_id)
    batch_scope = "homonimia_resuelta_con_fuente_oficial"
elif BATCH_NUMBER == 18:
    batch_resolutions = read_csv(PEN_RESOLUTIONS_PATH)
    batch_resolution_by_id = {row["persona_id"]: row for row in batch_resolutions}
    assert len(batch_resolution_by_id) == 8
    batch = sorted(
        (queue_by_id[person_id] for person_id in batch_resolution_by_id),
        key=lambda row: normalize(row["persona"]),
    )
    assert all(row["nivel_cargo"] == "Conducción superior PEN" for row in batch)
    expected_batch_size = len(batch_resolution_by_id)
    batch_scope = "autoridad_pen_actual_con_historial_oa_2017_2024"
elif BATCH_NUMBER == 19:
    batch_resolutions = read_csv(CROSS_INSTITUTION_RESOLUTIONS_PATH)
    batch_resolution_by_id = {row["persona_id"]: row for row in batch_resolutions}
    assert len(batch_resolution_by_id) == 4
    batch = sorted(
        (queue_by_id[person_id] for person_id in batch_resolution_by_id),
        key=lambda row: (row["nivel_cargo"], normalize(row["persona"])),
    )
    assert all(row["nivel_cargo"] in {"Diputados nacionales", "Senado nacional"} for row in batch)
    expected_batch_size = len(batch_resolution_by_id)
    batch_scope = "legislador_nacional_actual_con_historial_oa_otro_organismo"
else:
    raise AssertionError(f"La selección auditada todavía no define una tanda {BATCH_NUMBER}")
assert len(batch) == expected_batch_size, (
    f"Se esperaban {expected_batch_size} personas en la tanda {BATCH_NUMBER} y llegaron {len(batch)}"
)
expected_confirmed_size = {8: 44, 10: 13, 12: 6}.get(BATCH_NUMBER, expected_batch_size)

identity_by_id = {row["persona_id"]: row for row in identity_rows}
candidate_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in candidate_rows:
    candidate_by_id[row["persona_id"]].append(row)

audit_rows: list[dict[str, object]] = []
confirmed_ids: set[str] = set()
for item in batch:
    person_id = item["persona_id"]
    identity = identity_by_id[person_id]
    oa_name = identity["oa_nombre"]
    identity_evidence_url = ""
    identity_evidence_local = ""
    if item["nivel_cargo"] == "Diputados nacionales":
        chamber = "Diputados"
        roster_matches = [
            {"full_name": f'{row["Apellido"]}, {row["Nombre"]}', "district": row["Distrito"]}
            for row in hcdn_roster
            if normalize(f'{row["Nombre"]} {row["Apellido"]}') == normalize(item["persona"])
            and canonical_district(row["Distrito"]) == canonical_district(item["jurisdiccion"])
        ]
        presentations = hcdn_presentations
        roster_url = HCDN_ROSTER_URL
        filing_url = HCDN_DDJJ_URL
        roster_local = "sources/active_roster/hcdn_diputados_vigentes_2026-09-01.csv"
        filing_local = "sources/active_roster/hcdn_ddjj_ejercicio_2025_2026-09-01.html"
    elif item["nivel_cargo"] == "Senado nacional":
        chamber = "Senado"
        roster_matches = [
            {"full_name": name, "district": item["jurisdiccion"]}
            for name in senate_roster_names
            if normalize(name) == normalize(item["persona"])
        ]
        presentations = senate_presentations
        roster_url = SENATE_ROSTER_URL
        filing_url = SENATE_DDJJ_URL
        roster_local = "sources/active_roster/senado_listado_vigente_2026-09-01.html"
        filing_local = "sources/active_roster/senado_ddjj_2025_2026-09-01.html"
    elif item["nivel_cargo"] == "Conducción superior PEN":
        chamber = "Conducción superior PEN"
        resolution = batch_resolution_by_id[person_id]
        current_source_path = ROOT / resolution["respaldo_cargo_actual_local"]
        assert current_source_path.is_file(), f"Falta respaldo de cargo actual para {person_id}"
        current_source_text = normalize(current_source_path.read_text(encoding="utf-8", errors="replace"))
        assert normalize(resolution["nombre_fuente_actual"]) in current_source_text
        roster_matches = [
            {"full_name": resolution["nombre_fuente_actual"], "district": "Nación"}
        ]
        presentations = []
        roster_url = resolution["fuente_cargo_actual_url"]
        filing_url = resolution["fuente_identidad_url"]
        roster_local = resolution["respaldo_cargo_actual_local"]
        filing_local = resolution["respaldo_identidad_local"]
    elif item["nivel_cargo"] == "Gobernaciones":
        chamber = "Gobernaciones"
        roster_matches = [
            {"full_name": name, "district": item["jurisdiccion"]}
            for name in cfi_governor_names
            if unordered_name_match_kind(name, item["persona"]) == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = CFI_GOVERNORS_URL
        filing_url = ""
        roster_local = "sources/active_roster/cfi_gobernadores_2026-09-01.html"
        filing_local = ""
    elif item["jurisdiccion"] == "Ciudad Autónoma de Buenos Aires":
        assert item["jurisdiccion"] == "Ciudad Autónoma de Buenos Aires"
        chamber = "Legislatura CABA"
        roster_matches = [
            {
                "full_name": f'{row["nombre"]} {row["apellido"]}',
                "district": "Ciudad Autónoma de Buenos Aires",
            }
            for row in caba_roster
            if unordered_name_match_kind(f'{row["nombre"]} {row["apellido"]}', item["persona"])
            == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = CABA_ROSTER_URL
        filing_url = CABA_DDJJ_URL
        roster_local = "sources/subnational_roster/caba_legisladores_vigentes_2026-09-01.xml"
        filing_local = "sources/subnational_roster/caba_ddjj_listado_2026-09-01.html"
    elif item["jurisdiccion"] == "Buenos Aires":
        assert item["jurisdiccion"] == "Buenos Aires"
        assert item["persona_id"].startswith(("prov-ba-dip-", "prov-ba-sen-"))
        is_deputy = item["persona_id"].startswith("prov-ba-dip-")
        chamber = "Diputados PBA" if is_deputy else "Senado PBA"
        current_roster_names = pba_deputies_roster_names if is_deputy else pba_senators_roster_names
        roster_matches = [
            {"full_name": name, "district": "Buenos Aires"}
            for name in current_roster_names
            if unordered_name_match_kind(name, item["persona"]) == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = PBA_DEPUTIES_ROSTER_URL if is_deputy else PBA_SENATORS_ROSTER_URL
        filing_url = ""
        roster_local = (
            "sources/subnational_roster/buenos_aires_diputados_vigentes_2026-09-01.html"
            if is_deputy
            else "sources/subnational_roster/buenos_aires_senadores_vigentes_2026-09-01.html"
        )
        filing_local = ""
    elif item["jurisdiccion"] == "Santa Fe":
        assert item["jurisdiccion"] == "Santa Fe"
        assert item["persona_id"].startswith(("prov-sf-dip-", "prov-sf-sen-"))
        is_deputy = item["persona_id"].startswith("prov-sf-dip-")
        chamber = "Diputados Santa Fe" if is_deputy else "Senado Santa Fe"
        current_roster_names = santa_fe_deputies_roster_names if is_deputy else santa_fe_senators_roster_names
        roster_matches = [
            {"full_name": name, "district": "Santa Fe"}
            for name in current_roster_names
            if unordered_name_match_kind(name, item["persona"]) == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = SANTA_FE_DEPUTIES_ROSTER_URL if is_deputy else SANTA_FE_SENATORS_ROSTER_URL
        filing_url = ""
        roster_local = (
            " | ".join(
                f"sources/subnational_roster/{path.name}" for path in SANTA_FE_DEPUTIES_ROSTER_PATHS
            )
            if is_deputy
            else "sources/subnational_roster/santa_fe_senadores_vigentes_2026-09-01.html"
        )
        filing_local = ""
    elif item["jurisdiccion"] == "Río Negro":
        assert item["jurisdiccion"] == "Río Negro"
        chamber = "Legislatura Río Negro"
        roster_matches = [
            {
                "full_name": f'{row["nombre"]} {row["apellido"]}',
                "district": "Río Negro",
            }
            for row in rio_negro_roster
            if unordered_name_match_kind(f'{row["nombre"]} {row["apellido"]}', item["persona"])
            == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = RIO_NEGRO_ROSTER_URL
        filing_url = ""
        roster_local = "sources/subnational_roster/rio_negro_legisladores_vigentes_2026-09-01.csv"
        filing_local = ""
    elif item["jurisdiccion"] == "Córdoba":
        assert item["jurisdiccion"] == "Córdoba"
        chamber = "Legislatura Córdoba"
        roster_matches = [
            {
                "full_name": f'{clean(row["nombre"])} {clean(row["apellido"])}',
                "district": "Córdoba",
            }
            for row in cordoba_roster
            if unordered_name_match_kind(
                f'{clean(row["nombre"])} {clean(row["apellido"])}', item["persona"]
            )
            == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = CORDOBA_ROSTER_URL
        filing_url = CORDOBA_DDJJ_URL
        roster_local = "sources/subnational_roster/cordoba_legisladores_vigentes_2026-09-01.json"
        filing_local = "sources/subnational_roster/cordoba_ddjj_2026-09-01.html"
    else:
        assert item["jurisdiccion"] == "Misiones"
        chamber = "Cámara de Representantes de Misiones"
        roster_matches = [
            {"full_name": name, "district": "Misiones"}
            for name in misiones_roster_names
            if unordered_name_match_kind(name, item["persona"]) == "exacta_por_tokens"
        ]
        presentations = []
        roster_url = MISIONES_ROSTER_URL
        filing_url = ""
        roster_local = (
            "sources/subnational_roster/misiones_diputados_vigentes_2026-09-01.html | "
            "sources/subnational_roster/misiones_bloques_2026-09-01.html"
        )
        filing_local = ""
    filing_matches = (
        [
            row
            for row in presentations
            if official_name_match_kind(oa_name, row["apellido"], row["nombre"]) != "sin_coincidencia"
            and canonical_district(row["distrito"]) == canonical_district(item["jurisdiccion"])
            and "2025" in row["tipo"]
        ]
        if presentations
        else []
    )
    unique_key = bool(identity["oa_person_key"]) and identity["oa_personas_por_cuit"] == "1"
    same_institution_years = bool(identity["evidencia_misma_institucion_anios"])
    prior_public_history = bool(candidate_by_id[person_id])
    if BATCH_NUMBER in {13, 14, 15, 17}:
        resolution = batch_resolution_by_id[person_id]
        assert resolution["oa_person_key"] == identity["oa_person_key"]
        assert normalize(resolution["oa_nombre_resuelto"]) == normalize(oa_name)
        identity_backup_path = ROOT / resolution["respaldo_identidad_local"]
        assert identity_backup_path.exists(), f"Falta respaldo de identidad para {person_id}"
        if resolution["metodo_resolucion"].startswith("presentacion_hcdn"):
            current_name_match = (
                official_name_match_kind(oa_name, filing_matches[0]["apellido"], filing_matches[0]["nombre"])
                if filing_matches
                else "sin_coincidencia"
            )
            evidence_ok = bool(filing_matches) and same_institution_years
        elif resolution["metodo_resolucion"].startswith("hcdn_opciones_2025"):
            current_name_match = "exacta"
            evidence_ok = same_institution_years
        elif resolution["metodo_resolucion"].startswith("padron_senado"):
            current_name_match = (
                unordered_name_compatibility(oa_name, roster_matches[0]["full_name"])
                if roster_matches
                else "sin_coincidencia"
            )
            evidence_ok = current_name_match == "exacta_por_tokens" and same_institution_years
        elif resolution["metodo_resolucion"].startswith("biografia_oficial_caba"):
            current_name_match = (
                unordered_name_compatibility(oa_name, roster_matches[0]["full_name"])
                if roster_matches
                else "sin_coincidencia"
            )
            oa_role_text = normalize(" ".join(row.get("cargo_oa", "") for row in candidate_by_id[person_id]))
            evidence_ok = (
                current_name_match == "exacta_por_tokens"
                and "ETICA PUBLICA" in oa_role_text
                and "CORRUPCION" in oa_role_text
            )
        elif resolution["metodo_resolucion"].startswith("perfil_hcdn_y_boletin_oficial"):
            current_name_match = (
                unordered_name_compatibility(oa_name, roster_matches[0]["full_name"])
                if roster_matches
                else "sin_coincidencia"
            )
            evidence_ok = current_name_match == "exacta_por_tokens"
        else:
            assert resolution["metodo_resolucion"] == "acta_electoral_oficial_con_documento_y_clave_oa_coincidente"
            current_name_match = (
                unordered_name_compatibility(oa_name, roster_matches[0]["full_name"])
                if roster_matches
                else "sin_coincidencia"
            )
            evidence_ok = current_name_match == "exacta_por_tokens"
        confirmed = (
            len(roster_matches) == 1
            and unique_key
            and prior_public_history
            and evidence_ok
        )
        criterion = resolution["nota_evidencia"]
        scope_note = (
            "La resolución separa una única clave fiscal del conjunto de homónimos. Para cargos provinciales, "
            "el historial OA federal o electoral no equivale a una DDJJ del mandato provincial actual."
        )
        filing_url = resolution["fuente_identidad_url"]
        filing_local = resolution["respaldo_identidad_local"]
    elif BATCH_NUMBER == 18:
        resolution = batch_resolution_by_id[person_id]
        assert resolution["oa_person_key"] == identity["oa_person_key"]
        assert normalize(resolution["oa_nombre_resuelto"]) == normalize(oa_name)
        identity_backup_path = ROOT / resolution["respaldo_identidad_local"]
        assert identity_backup_path.is_file(), f"Falta respaldo identificatorio para {person_id}"
        current_name_match = unordered_name_compatibility(oa_name, item["persona"])
        identifier_ok = resolution["identificador_oficial_vs_oa"].startswith("sí")
        trajectory_ok = (
            resolution["nivel_evidencia"] == "nombre_completo_cargo_y_trayectoria_oa_unica"
            and same_institution_years
        )
        confirmed = (
            len(roster_matches) == 1
            and current_name_match == "exacta_por_tokens"
            and unique_key
            and prior_public_history
            and (identifier_ok or trajectory_ok)
        )
        criterion = resolution["nota_evidencia"]
        scope_note = (
            "La fuente oficial acredita el cargo PEN vigente y la serie corresponde a DDJJ OA 2017–2024. "
            "No se infieren valores 2025–2026 ni se publica el identificador usado en el cotejo."
        )
    elif BATCH_NUMBER == 19:
        resolution = batch_resolution_by_id[person_id]
        assert resolution["oa_person_key"] == identity["oa_person_key"]
        assert normalize(resolution["oa_nombre_resuelto"]) == normalize(oa_name)
        identity_backup_path = ROOT / resolution["respaldo_identidad_local"]
        assert identity_backup_path.is_file(), f"Falta respaldo identificatorio para {person_id}"
        current_name_match = (
            official_name_match_kind(oa_name, filing_matches[0]["apellido"], filing_matches[0]["nombre"])
            if filing_matches
            else "sin_coincidencia"
        )
        confirmed = (
            len(roster_matches) == 1
            and bool(filing_matches)
            and current_name_match != "sin_coincidencia"
            and unique_key
            and prior_public_history
            and resolution["identificador_oficial_vs_oa"].startswith("sí")
            and resolution["nivel_evidencia"] == "identificador_oficial_coincidente_y_puente_cargo_oa"
        )
        criterion = resolution["nota_evidencia"]
        scope_note = (
            "La Cámara acredita el cargo vigente; los importes corresponden al historial OA 2017–2024, que puede "
            "provenir de otro organismo. No se atribuyen valores 2025–2026 ni se publica el identificador."
        )
        identity_evidence_url = resolution["fuente_identidad_url"]
        identity_evidence_local = resolution["respaldo_identidad_local"]
    elif chamber == "Gobernaciones":
        current_name_match = (
            unordered_name_match_kind(oa_name, roster_matches[0]["full_name"])
            if roster_matches
            else "sin_coincidencia"
        )
        confirmed = (
            len(roster_matches) == 1
            and current_name_match == "exacta_por_tokens"
            and unique_key
            and prior_public_history
        )
        criterion = (
            "Nómina CFI vigente con nombre completo y provincia + coincidencia exacta de tokens con una sola "
            "clave fiscal reservada en OA + DDJJ oficiales de un cargo público nacional previo."
        )
        scope_note = (
            "Historial federal previo: la serie no representa una DDJJ del mandato provincial actual ni permite "
            "inferir el patrimonio presente."
        )
    elif chamber in {
        "Legislatura CABA", "Diputados PBA", "Senado PBA", "Diputados Santa Fe", "Senado Santa Fe",
        "Legislatura Río Negro", "Legislatura Córdoba", "Cámara de Representantes de Misiones"
    }:
        current_name_match = (
            unordered_name_compatibility(oa_name, roster_matches[0]["full_name"])
            if roster_matches
            else "sin_coincidencia"
        )
        confirmed = (
            len(roster_matches) == 1
            and current_name_match != "sin_coincidencia"
            and unique_key
            and prior_public_history
        )
        if chamber == "Legislatura CABA":
            criterion = (
                "Servicio oficial de legisladores CABA vigente + nombre exacto o compatible por tokens con una sola "
                "clave fiscal reservada en OA + historial oficial OA. La ruta institucional DJPI de CABA se conserva "
                "como contexto y no se interpreta como una presentación individual vigente."
            )
        elif chamber == "Legislatura Río Negro":
            criterion = (
                "Transcripción estructurada y fechada de la nómina oficial rionegrina, con URL de bloque por fila, "
                "+ nombre exacto o compatible por tokens con una sola clave fiscal reservada en OA + historial "
                "oficial OA. El respaldo no se presenta como descarga HTML cruda del portal."
            )
        elif chamber == "Legislatura Córdoba":
            criterion = (
                "Archivo JSON oficial con las 70 bancas cordobesas vigentes + nombre exacto o compatible por tokens "
                "con una sola clave fiscal reservada en OA + historial oficial OA. La ruta institucional de DDJJ se "
                "conserva como contexto y no se interpreta como una presentación individual vigente."
            )
        elif chamber == "Cámara de Representantes de Misiones":
            criterion = (
                "Nómina oficial vigente de 40 representantes y composición de bloques respaldada + nombre exacto o "
                "compatible por tokens con una sola clave fiscal reservada en OA + historial oficial OA. No se "
                "interpreta el historial nacional previo como DDJJ del mandato provincial actual."
            )
        else:
            criterion = (
                f"Nómina oficial vigente de {chamber} + nombre exacto o compatible por tokens con una sola clave "
                "fiscal reservada en OA + historial oficial OA. No se localizó una presentación provincial actual "
                "en una fuente nominal reutilizable para este cruce."
            )
        scope_note = (
            "Historial público OA previo al corte: puede incluir Legislatura CABA o cargos nacionales anteriores; "
            "no equivale por sí solo a la DDJJ del mandato actual."
        )
    else:
        current_name_match = (
            official_name_match_kind(oa_name, filing_matches[0]["apellido"], filing_matches[0]["nombre"])
            if filing_matches
            else "sin_coincidencia"
        )
        confirmed = len(roster_matches) == 1 and bool(filing_matches) and unique_key and same_institution_years
        criterion = (
            f"Nómina {chamber} vigente + presentación {chamber} 2025 con apellido, nombres compatibles y distrito + "
            "una sola clave fiscal reservada en OA + evidencia de cargo legislativo nacional."
        )
        scope_note = "DDJJ del cargo legislativo nacional actual dentro del consolidado OA disponible."
    if confirmed:
        confirmed_ids.add(person_id)
    audit_rows.append(
        {
            "persona_id": person_id,
            "persona": item["persona"],
            "camara": chamber,
            "jurisdiccion": item["jurisdiccion"],
            "oa_nombre": oa_name,
            "oa_person_key": identity["oa_person_key"],
            "oa_anios": identity["oa_anios_seleccionados"],
            "evidencia_misma_institucion_anios": identity["evidencia_misma_institucion_anios"],
            "nombre_padron_camara": roster_matches[0]["full_name"] if roster_matches else "",
            "distrito_padron_camara": roster_matches[0]["district"] if roster_matches else "",
            "nombre_presentacion_camara_2025": (
                f'{filing_matches[0]["apellido"]}, {filing_matches[0]["nombre"]}' if filing_matches else ""
            ),
            "distrito_presentacion_camara_2025": filing_matches[0]["distrito"] if filing_matches else "",
            "tipo_presentacion_camara_2025": " | ".join(sorted({row["tipo"] for row in filing_matches})),
            "coincidencia_nombre_presentacion": current_name_match,
            "coincidencia_nombre_fuente_actual": current_name_match,
            "cuit_unico_en_consolidado": "sí" if unique_key else "no",
            "estado_revision_identidad": (
                "identidad_confirmada_cruce_oficial" if confirmed else "requiere_revision_adicional"
            ),
            "publicable_en_tab": "sí" if confirmed else "no",
            "alcance_serie": batch_scope,
            "nota_alcance": scope_note,
            "criterio": criterion,
            "fuente_padron_url": roster_url,
            "fuente_presentacion_url": filing_url,
            "fuente_serie_url": DATASET_URL,
            "respaldo_padron_local": roster_local,
            "respaldo_presentacion_local": filing_local,
            "fuente_identidad_independiente_url": identity_evidence_url,
            "respaldo_identidad_independiente_local": identity_evidence_local,
            "respaldo_oa_local": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
        }
    )

if len(confirmed_ids) != expected_batch_size:
    for row in audit_rows:
        if row["estado_revision_identidad"] != "identidad_confirmada_cruce_oficial":
            print(
                "REVISAR:", row["persona"],
                "| padrón:", row["nombre_padron_camara"],
                "| presentación:", row["nombre_presentacion_camara_2025"],
                "| OA:", row["oa_nombre"],
            )
assert len(confirmed_ids) == expected_confirmed_size, (
    f"La revisión estricta de la tanda {BATCH_NUMBER} confirmó {len(confirmed_ids)} de "
    f"{expected_confirmed_size} identidades esperadas tras resolver excepciones"
)

macro = {int(row["anio"]): row for row in macro_rows}
ipc_2025 = Decimal(macro[2025]["ipc_indice_dic_2016_100"])

verified_series: list[dict[str, object]] = []
numeric_by_id: dict[str, list[dict[str, object]]] = defaultdict(list)
people = []
series_scope_suffix = {
    "historial_federal_previo_no_ddjj_provincial_actual": (
        " Corresponde a un cargo federal previo y no a una DDJJ del mandato provincial actual."
    ),
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": (
        " Es historial público OA previo al corte y no equivale por sí solo a la DDJJ del mandato actual."
    ),
    "homonimia_resuelta_con_fuente_oficial": (
        " La clave fiscal fue separada de homónimos mediante evidencia oficial independiente."
    ),
    "autoridad_pen_actual_con_historial_oa_2017_2024": (
        " La autoridad actual fue cotejada con fuente oficial; la serie OA termina en 2024 y no infiere 2025–2026."
    ),
    "legislador_nacional_actual_con_historial_oa_otro_organismo": (
        " La Cámara acredita el cargo vigente y una fuente independiente enlaza el historial OA de otro organismo."
    ),
}.get(batch_scope, "")
for item in batch:
    person_id = item["persona_id"]
    if person_id not in confirmed_ids:
        continue
    people.append(
        {
            "persona_id": person_id,
            "persona": item["persona"],
            "lote_auditoria": BATCH_NUMBER,
            "alcance_serie": batch_scope,
        }
    )
    by_year = {int(row["anio"]): row for row in candidate_by_id[person_id]}
    observed: list[dict[str, object]] = []
    for year, source in sorted(by_year.items()):
        gross = decimal_or_none(source["total_bienes_ars"])
        debt = decimal_or_none(source["deudas_ars"])
        if gross is None:
            continue
        real = gross * ipc_2025 / Decimal(macro[year]["ipc_indice_dic_2016_100"])
        usd = gross / Decimal(macro[year]["a3500_ars_por_usd"])
        observed.append({"year": year, "source": source, "gross": gross, "debt": debt, "real": real, "usd": usd})
    assert observed, f"{item['persona']} no tiene importes observados"
    first = next((row for row in observed if row["gross"] > 0), observed[0])
    observed_by_year = {int(row["year"]): row for row in observed}
    for year in range(2017, 2026):
        current = observed_by_year.get(year)
        if current:
            source = current["source"]
            gross = current["gross"]
            debt = current["debt"]
            real = current["real"]
            usd = current["usd"]
            row = {
                "persona_id": person_id,
                "persona": item["persona"],
                "anio": year,
                "estado_fuente": "oficial_consolidado_oa",
                "tipo_ddjj": source["tipo_ddjj"],
                "rectificativa": source["rectificativa"],
                "dj_id": source["dj_id"],
                "total_bienes_ars": text(gross),
                "deudas_ars": text(debt),
                "patrimonio_neto_ars": text(gross - debt) if debt is not None else "",
                "total_bienes_real_ars_2025": text(real),
                "total_bienes_usd_a3500": text(usd),
                "ipc_indice": macro[year]["ipc_indice_dic_2016_100"],
                "a3500_ars_por_usd": macro[year]["a3500_ars_por_usd"],
                "indice_nominal_base": text(gross / first["gross"] * 100) if first["gross"] else "",
                "indice_real_base": text(real / first["real"] * 100) if first["real"] else "",
                "indice_usd_base": text(usd / first["usd"] * 100) if first["usd"] else "",
                "fuente_url": DATASET_URL,
                "nota": (
                    "Identidad confirmada por cruce oficial; selección Anual > Baja > Inicial, luego rectificativa y dj_id."
                    + series_scope_suffix
                ),
            }
            numeric_by_id[person_id].append({"row": row, "gross": gross, "real": real, "usd": usd})
        else:
            row = {
                "persona_id": person_id,
                "persona": item["persona"],
                "anio": year,
                "estado_fuente": "no_localizada",
                "tipo_ddjj": "",
                "rectificativa": "",
                "dj_id": "",
                "total_bienes_ars": "",
                "deudas_ars": "",
                "patrimonio_neto_ars": "",
                "total_bienes_real_ars_2025": "",
                "total_bienes_usd_a3500": "",
                "ipc_indice": macro[year]["ipc_indice_dic_2016_100"],
                "a3500_ars_por_usd": macro[year]["a3500_ars_por_usd"],
                "indice_nominal_base": "",
                "indice_real_base": "",
                "indice_usd_base": "",
                "fuente_url": DATASET_URL,
                "nota": (
                    "No se localizó una DJPI consolidada para esta persona y año; no equivale a patrimonio cero."
                    + series_scope_suffix
                ),
            }
        verified_series.append(row)

coverage_rows: list[dict[str, object]] = []
for person in people:
    values = numeric_by_id[person["persona_id"]]
    first_observed = min(values, key=lambda item: int(item["row"]["anio"]))
    first = min(
        (item for item in values if item["gross"] > 0),
        key=lambda item: int(item["row"]["anio"]),
        default=first_observed,
    )
    last = max(values, key=lambda item: int(item["row"]["anio"]))
    first_observed_year = int(first_observed["row"]["anio"])
    first_year = int(first["row"]["anio"])
    last_year = int(last["row"]["anio"])
    official_years = sorted(int(item["row"]["anio"]) for item in values)
    missing = [year for year in range(2017, 2025) if year not in official_years]
    elapsed = last_year - first_year
    coverage_rows.append(
        {
            "persona_id": person["persona_id"],
            "persona": person["persona"],
            "primer_anio_con_dato": first_observed_year,
            "ultimo_anio_con_dato": last_year,
            "anio_base_metricas": first_year,
            "anios_oficiales_2017_2024": len(official_years),
            "cobertura_oficial_pct": text(Decimal(len(official_years)) / Decimal("8") * 100, 1),
            "anios_faltantes_2017_2024": "|".join(map(str, missing)) or "ninguno",
            "dato_2025": "no_disponible",
            "cambio_nominal_primero_ultimo_pct": text(percent_change(last["gross"], first["gross"])),
            "cambio_real_primero_ultimo_pct": text(percent_change(last["real"], first["real"])),
            "cambio_usd_primero_ultimo_pct": text(percent_change(last["usd"], first["usd"])),
            "cagr_real_anual_pct": text(cagr(last["real"], first["real"], elapsed)),
            "cagr_usd_anual_pct": text(cagr(last["usd"], first["usd"], elapsed)),
            "nota": (
                f"Identidad confirmada en la iteración {BATCH_NUMBER}. La ausencia de dato no se interpola "
                "ni se interpreta como patrimonio cero." + series_scope_suffix
            ),
        }
    )

annual_returns: dict[str, dict[int, Decimal]] = defaultdict(dict)
for row in benchmark_return_rows:
    annual_returns[row["benchmark_id"]][int(row["anio"])] = Decimal(row["retorno_total_usd_pct"])
benchmark_lookup = {
    "tbill_3m_proxy": ("T-bill EE.UU. 3 meses · rollover proxy", "poco"),
    "vbiax_60_40": ("Vanguard Balanced Index · 60/40", "medio"),
    "msci_acwi_net": ("MSCI ACWI · net return USD", "mucho"),
}
benchmark_rows: list[dict[str, object]] = []
for person in people:
    values = numeric_by_id[person["persona_id"]]
    first_observed = min(values, key=lambda item: int(item["row"]["anio"]))
    first = min(
        (item for item in values if item["gross"] > 0),
        key=lambda item: int(item["row"]["anio"]),
        default=first_observed,
    )
    last = max(values, key=lambda item: int(item["row"]["anio"]))
    first_year = int(first["row"]["anio"])
    last_year = int(last["row"]["anio"])
    elapsed = last_year - first_year
    if elapsed <= 0 or first["gross"] <= 0:
        continue
    observed_usd_cagr = cagr(last["usd"], first["usd"], elapsed)
    observed_real_cagr = cagr(last["real"], first["real"], elapsed)
    if observed_usd_cagr is None or observed_real_cagr is None:
        continue
    for benchmark_id, (label, risk) in benchmark_lookup.items():
        factor = Decimal("1")
        for year in range(first_year + 1, last_year + 1):
            factor *= Decimal("1") + annual_returns[benchmark_id][year] / Decimal("100")
        benchmark_cagr = Decimal(str((float(factor) ** (1 / elapsed) - 1) * 100))
        hypothetical_end = (
            first["gross"] / Decimal(macro[first_year]["a3500_ars_por_usd"])
            * factor
            * Decimal(macro[last_year]["a3500_ars_por_usd"])
        )
        benchmark_rows.append(
            {
                "persona_id": person["persona_id"],
                "persona": person["persona"],
                "anio_inicio": first_year,
                "anio_fin": last_year,
                "anios_transcurridos": elapsed,
                "benchmark_id": benchmark_id,
                "benchmark": label,
                "riesgo": risk,
                "patrimonio_cagr_real_pct": text(observed_real_cagr),
                "patrimonio_cagr_usd_a3500_pct": text(observed_usd_cagr),
                "benchmark_retorno_acumulado_usd_pct": text((factor - 1) * 100),
                "benchmark_cagr_usd_pct": text(benchmark_cagr),
                "brecha_cagr_vs_patrimonio_usd_pp": text(observed_usd_cagr - benchmark_cagr),
                "patrimonio_final_observado_ars": text(last["gross"]),
                "capital_final_contrafactual_ars_a3500": text(hypothetical_end),
                "estado_ultimo_dato": "oficial_consolidado_oa",
                "supuesto": "Sin aportes ni retiros; retorno total reinvertido; antes de impuestos; sin apalancamiento.",
            }
        )

audit_fields = list(audit_rows[0])
series_fields = list(verified_series[0])
benchmark_fields = list(benchmark_rows[0])
write_csv(AUDIT_PATH, audit_rows, audit_fields)
write_csv(SERIES_PATH, verified_series, series_fields)
write_csv(BENCHMARK_PATH, benchmark_rows, benchmark_fields)

dashboard = {
    "metadata": {
        "lote": BATCH_NUMBER,
        "corte": "2026-09-01",
        "identidades_confirmadas": len(confirmed_ids),
        "criterio": (
            "Cruce reproducible de fuentes oficiales; el CUIT se conserva únicamente como clave hash reservada. "
            + {
                "historial_federal_previo_no_ddjj_provincial_actual": (
                    "La tanda muestra historial federal previo y no una DDJJ provincial actual."
                ),
                "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": (
                    "La tanda muestra historial público OA previo y no equivale por sí sola a la DDJJ del mandato actual."
                ),
                "homonimia_resuelta_con_fuente_oficial": (
                    "La tanda separa claves fiscales homónimas mediante presentaciones, padrones o actas oficiales."
                ),
                "autoridad_pen_actual_con_historial_oa_2017_2024": (
                    "La tanda acredita autoridades PEN vigentes y publica únicamente su historial OA 2017–2024."
                ),
                "legislador_nacional_actual_con_historial_oa_otro_organismo": (
                    "La tanda acredita legisladores vigentes y enlaza mediante fuente oficial su historial OA en otro organismo."
                ),
            }.get(batch_scope, "")
        ).strip(),
        "alcance_serie": batch_scope,
    },
    "people": people,
    "series": verified_series,
    "coverage": coverage_rows,
    "benchmark_comparisons": benchmark_rows,
}
DASHBOARD_PATH.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(
    f"OK: iteración {BATCH_NUMBER} · {len(confirmed_ids)} identidades confirmadas · "
    f"{sum(len(rows) for rows in candidate_by_id.values() if rows and rows[0]['persona_id'] in confirmed_ids)} "
    f"registros OA observados · {len(benchmark_rows)} contrafactuales"
)
