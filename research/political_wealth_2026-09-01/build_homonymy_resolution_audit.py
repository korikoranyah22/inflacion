from __future__ import annotations

import csv
import hashlib
import io
import re
import unicodedata
import zipfile
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
QUEUE_PATH = DERIVED / "active_politician_research_queue_2026-09-01.csv"
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"
OUTPUT_PATH = DERIVED / "active_politician_homonymy_candidate_audit_2026-09-01.csv"
HCDN_DDJJ_PATH = ROOT / "sources" / "active_roster" / "hcdn_ddjj_ejercicio_2025_2026-09-01.html"
SENATE_ROSTER_PATH = ROOT / "sources" / "active_roster" / "senado_listado_vigente_2026-09-01.html"
RIO_NEGRO_ELECTION_PATH = (
    ROOT / "sources" / "subnational_roster" / "rio_negro_acta_proclamacion_2023.pdf"
)
HCDN_OPTIONS_2025_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "hcdn_opciones_viajes_nacionales_2025.pdf"
)
CABA_LAURA_ALONSO_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "caba_legislatura_laura_alonso_2026.html"
)
JUSBAIRES_LAURA_ALONSO_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "jusbaires_laura_alonso_cv.html"
)
OA_LAURA_ALONSO_DECREE_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "decreto_252_2015_laura_alonso_oa.html"
)
HCDN_ALVARO_GARCIA_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "hcdn_alvaro_garcia_profile_2026.html"
)
BOLETIN_ALVARO_GARCIA_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "boletin_oficial_alvaro_garcia_2023.pdf"
)
PBA_MARIA_LAURA_FERNANDEZ_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "buenos_aires_maria_laura_fernandez_profile_2026.html"
)
PBA_DDJJ_2018_PATH = (
    ROOT / "sources" / "identity_crosswalk" / "buenos_aires_diputados_ddjj_2018.pdf"
)

REVIEW_STATUSES = {
    "homonimia_oa_por_resolver",
    "historial_oa_posible_cargo_nacional_previo",
}
TYPE_PRIORITY = {"Inicial": 1, "Baja": 2, "Anual": 3}
RIO_NEGRO_ELECTION_SHA256 = "f3f38abb1777078a6c84d28fb80b0efeae5bf978e1af63002cb6e941de83f1f4"
HCDN_OPTIONS_2025_SHA256 = "919d11ca21d669c81c0952ce89542be5be93d7eba52d28b9b1b81fe8121af9ed"
ALVARO_GARCIA_IDENTIFIER_SHA256 = "28199dc98c1597374fad0a6a3c2969360ad5e54ea8d10296066366842a4a967a"

RESOLUTIONS_BY_ITERATION = {
    13: {
        "dip-alvarez-claudio": {
            "oa_nombre": "ALVAREZ CLAUDIO ARIEL",
            "oa_person_key": "93406d770418f0f6",
            "metodo": "presentacion_hcdn_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-farias-pablo": {
            "oa_nombre": "FARIAS PABLO GUSTAVO",
            "oa_person_key": "716bae744f13a4c6",
            "metodo": "presentacion_hcdn_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-gonzalez-alvaro": {
            "oa_nombre": "GONZALEZ ALVARO GUSTAVO",
            "oa_person_key": "a8a2c6ae6d411a72",
            "metodo": "presentacion_hcdn_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-marino-juan": {
            "oa_nombre": "MARINO JUAN",
            "oa_person_key": "96e4d1ad398bfe84",
            "metodo": "presentacion_hcdn_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-monzon-roxana": {
            "oa_nombre": "MONZON ROXANA ELIZABETH",
            "oa_person_key": "c7cd76b452d949d8",
            "metodo": "presentacion_hcdn_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "sen-recalde-mariano": {
            "oa_nombre": "RECALDE MARIANO",
            "oa_person_key": "0aa8ab40a874d3e5",
            "metodo": "padron_senado_vigente_nombre_exacto_y_serie_oa_misma_institucion",
        },
        "prov-rn-leg-martin-juan-carlos": {
            "oa_nombre": "MARTIN JUAN CARLOS",
            "oa_person_key": "5a396ed1992b7f51",
            "metodo": "acta_electoral_oficial_con_documento_y_clave_oa_coincidente",
        },
    },
    14: {
        "dip-garcia-carlos": {
            "oa_nombre": "GARCIA CARLOS DANIEL",
            "oa_person_key": "24fc20286595f8a4",
            "metodo": "hcdn_opciones_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-gomez-jose": {
            "oa_nombre": "GOMEZ JOSE EDGARDO",
            "oa_person_key": "1ced57f0d0101114",
            "metodo": "hcdn_opciones_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-gutierrez-carlos": {
            "oa_nombre": "GUTIERREZ CARLOS MARIO",
            "oa_person_key": "21184a5df7ac16f7",
            "metodo": "hcdn_opciones_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-montenegro-guillermo": {
            "oa_nombre": "MONTENEGRO GUILLERMO MAXIMILIANO",
            "oa_person_key": "101398818f48c660",
            "metodo": "hcdn_opciones_2025_nombre_completo_distrito_y_cargo_oa",
        },
        "dip-nunez-jose": {
            "oa_nombre": "NUÑEZ JOSE CARLOS",
            "oa_person_key": "8d9566d3eade51fa",
            "metodo": "hcdn_opciones_2025_nombre_completo_distrito_y_cargo_oa",
        },
    },
    15: {
        "prov-caba-leg-alonso-laura": {
            "oa_nombre": "ALONSO LAURA",
            "oa_person_key": "8c82568d76d60881",
            "metodo": "biografia_oficial_caba_vincula_legisladora_y_titular_oa",
        },
    },
    17: {
        "dip-garcia-alvaro": {
            "oa_nombre": "GARCIA ALVARO",
            "oa_person_key": "2cb302b8e2a70a23",
            "metodo": "perfil_hcdn_y_boletin_oficial_con_documento_y_clave_oa_coincidente",
        },
    },
}
ALL_RESOLUTIONS = {
    person_id: resolution
    for resolutions in RESOLUTIONS_BY_ITERATION.values()
    for person_id, resolution in resolutions.items()
}
assert len(ALL_RESOLUTIONS) == sum(len(rows) for rows in RESOLUTIONS_BY_ITERATION.values())

EXCLUSIONS_BY_ITERATION = {
    15: {
        "dip-fernandez-jorge": {
            "nombre_completo_oficial": "JORGE OMAR FERNANDEZ",
            "alcance_descarte": "parcial_candidato_abreviado_permanece",
            "oa_person_keys_no_descartadas": {"06d41b06983ab1fb"},
            "metodo": "presentacion_hcdn_2025_nombre_completo_y_cotejo_nominal_conservador",
            "fuente_identidad_url": "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/listado/c4f0658a-4249-11f0-87b7-00505689ffd4",
            "respaldo_identidad_local": "sources/active_roster/hcdn_ddjj_ejercicio_2025_2026-09-01.html",
            "nota_evidencia": "HCDN publica Jorge Omar Fernández. Se descartan candidatos con segundos nombres incompatibles, pero FERNANDEZ JORGE permanece abierto porque OA pudo omitir el segundo nombre.",
        },
        "dip-rodriguez-miguel": {
            "nombre_completo_oficial": "LUIS MIGUEL RODRIGUEZ",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "presentacion_hcdn_2025_nombre_completo_y_cotejo_nominal",
            "fuente_identidad_url": "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/listado/c4f0658a-4249-11f0-87b7-00505689ffd4",
            "respaldo_identidad_local": "sources/active_roster/hcdn_ddjj_ejercicio_2025_2026-09-01.html",
            "nota_evidencia": "HCDN publica Luis Miguel Rodríguez. Ninguna clave candidata OA conserva esa identidad: todas agregan Ángel, Alejandro o Marcelo y omiten Luis.",
        },
        "prov-ba-sen-lopez-roxana": {
            "nombre_completo_oficial": "ROXANA ALEJANDRA LOPEZ",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "jura_senado_ba_nombre_completo_y_cotejo_nominal",
            "fuente_identidad_url": "https://www.senado-ba.gov.ar/Prensa_Noticia_Individual.aspx?IdNoticia=18479",
            "respaldo_identidad_local": "sources/identity_crosswalk/senado_ba_roxana_alejandra_lopez_2026.html",
            "nota_evidencia": "El Senado bonaerense identifica a Roxana Alejandra López. Las dos claves OA candidatas corresponden a Roxana del Valle y Roxana Judith López.",
        },
        "prov-sf-dip-gonzalez-marcelo": {
            "nombre_completo_oficial": "MARCELO OMAR GONZALEZ",
            "alcance_descarte": "parcial_candidato_abreviado_permanece",
            "oa_person_keys_no_descartadas": {"d332b09d76d90417"},
            "metodo": "gobierno_santa_fe_nombre_completo_y_cotejo_nominal_conservador",
            "fuente_identidad_url": "https://www.santafe.gov.ar/noticias/noticia/imprimir/286178/",
            "respaldo_identidad_local": "sources/identity_crosswalk/santa_fe_marcelo_omar_gonzalez_2026.html",
            "nota_evidencia": "Santa Fe publica Marcelo Omar González. Se descartan las claves con otros segundos nombres, pero GONZALEZ MARCELO permanece abierta porque OA pudo omitir Omar.",
        },
        "prov-sf-dip-rojas-sergio": {
            "nombre_completo_oficial": "SERGIO JAVIER ROJAS",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "documento_camara_santa_fe_nombre_completo_y_cotejo_nominal",
            "fuente_identidad_url": "https://expedientes.diputadossantafe.gov.ar/datos/datos/tramitefinal/01-PROYECTOS/02-Con%20Tramite%20Parlamentario/Ley/dl5423624.pdf",
            "respaldo_identidad_local": "sources/identity_crosswalk/santa_fe_sergio_javier_rojas_2024.pdf",
            "nota_evidencia": "La Cámara santafesina publica Sergio Javier Rojas. Las claves OA candidatas corresponden a Sergio David y Sergio Eduardo Rojas.",
        },
    },
    16: {
        "dip-fernandez-jorge": {
            "nombre_completo_oficial": "JORGE OMAR FERNANDEZ",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "registro_electoral_san_luis_con_documento_y_cotejo_oa_reservado",
            "fuente_identidad_url": "https://electoral.justiciasanluis.gov.ar/?p=5338",
            "respaldo_identidad_local": "sources/identity_crosswalk/san_luis_registro_candidatos_jorge_fernandez.html",
            "identificador_oficial_sha256": "1ac604511bc814269a8cf27b706edebdb45aef5abf67a24a2abf8fd0a02bbd96",
            "nota_evidencia": "El registro electoral de San Luis identifica a Jorge Omar Fernández, Gato, con documento. La comparación reservada no coincide con ninguna de las 19 claves OA candidatas, incluida FERNANDEZ JORGE.",
        },
        "prov-sf-dip-gonzalez-marcelo": {
            "nombre_completo_oficial": "MARCELO OMAR GONZALEZ",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "antecedente_oficial_santa_fe_con_documento_y_cotejo_oa_reservado",
            "fuente_identidad_url": "https://archivoseducacion.santafe.gob.ar/licencias/rosario/nominas/16449-23-09-14-RAM-%20INDEFINIDO.pdf",
            "respaldo_identidad_local": "sources/identity_crosswalk/santa_fe_educacion_marcelo_omar_gonzalez_2014.pdf",
            "identificador_oficial_sha256": "1f40f1521c28af27a4722ae612142125cabbbe6949735e0491c1939839c855fa",
            "nota_evidencia": "Fuentes oficiales santafesinas conectan a Marcelo Omar González con San Cristóbal y conservan un documento en el antecedente educativo. El cotejo reservado no coincide con ninguna de las 12 claves OA, incluida GONZALEZ MARCELO.",
        },
        "prov-mis-leg-rodriguez-juan-manuel": {
            "nombre_completo_oficial": "JUAN MANUEL RODRIGUEZ",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "lista_electoral_misiones_con_documento_y_cotejo_oa_reservado",
            "fuente_identidad_url": "https://www.electoralmisiones.gov.ar/wp-content/uploads/2025/05/8-Lista-de-Candidatos-a-Cargos-Provinciales-Habilitadas.pdf",
            "respaldo_identidad_local": "sources/identity_crosswalk/misiones_candidatos_oficializados_2025.pdf",
            "identificador_oficial_sha256": "f48f28f1fe23b2632759bec670528bbc9626bc79e38a1f4b941ebc2b28d37dc9",
            "nota_evidencia": "La lista oficializada del Tribunal Electoral de Misiones publica el documento del candidato electo Juan Manuel Rodríguez. El cotejo reservado no coincide con ninguna de las tres claves OA homónimas.",
        },
    },
    17: {
        "prov-ba-dip-fernandez-maria-laura": {
            "nombre_completo_oficial": "FERNANDEZ MARIA LAURA",
            "alcance_descarte": "total_sin_candidato_oa_compatible",
            "oa_person_keys_no_descartadas": set(),
            "metodo": "perfil_hcdiputados_ba_con_documento_y_cotejo_oa_reservado",
            "fuente_identidad_url": "https://www.hcdiputados-ba.gov.ar/index.php?page=diputados&search=seccionBloques",
            "respaldo_identidad_local": "sources/identity_crosswalk/buenos_aires_maria_laura_fernandez_profile_2026.html",
            "identificador_oficial_sha256": "1a945711529948b1211af0e53c60b2e281f2c55ad2b70ba0add3b7923e405d69",
            "fuentes_complementarias_url": "https://intranet.hcdiputados-ba.gov.ar/transparencia/web/Declaraciones%20Juradas%202018.pdf",
            "respaldos_complementarios_locales": "sources/identity_crosswalk/buenos_aires_diputados_ddjj_2018.pdf",
            "nota_evidencia": "La Cámara bonaerense vincula el perfil vigente de María Laura Fernández con su identificador de persona. Una nómina oficial de DDJJ que etiqueta DNI permite verificar, mediante un caso de control, que el sitio usa ese mismo esquema de identificadores. El cotejo reservado no coincide con ninguna de las tres claves OA homónimas.",
        },
    },
}
ALL_EXCLUSIONS = {
    person_id: exclusion
    for exclusions in EXCLUSIONS_BY_ITERATION.values()
    for person_id, exclusion in exclusions.items()
}
assert len(ALL_EXCLUSIONS) == 7


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
        elif self.in_target_table and tag == "tr" and self.current_row:
            self.rows.append(self.current_row)
        elif self.in_target_table and tag == "table":
            self.in_target_table = False


class SenateNameParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.names: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and str(attributes.get("href", "")).startswith("/senadores/senador/"):
            title = clean(str(attributes.get("title", "")))
            if title:
                self.names.add(title)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^A-Za-z0-9]+", " ", value).upper()
    return " ".join(value.split())


def clean(value: str) -> str:
    return " ".join((value or "").replace('""', "").split()).strip('" ')


def canonical_district(value: str) -> str:
    normalized = normalize(value)
    if normalized in {"CABA", "CIUDAD DE BUENOS AIRES", "CIUDAD AUTONOMA DE BUENOS AIRES"}:
        return "CABA"
    return normalized


def masked_person_key(cuit: str) -> str:
    return hashlib.sha256(cuit.encode("utf-8")).hexdigest()[:16]


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


def compact_history(rows: list[dict[str, str]], field: str) -> str:
    values: list[str] = []
    for row in rows:
        value = clean(row.get(field, ""))
        if value and value not in values:
            values.append(value)
    return " | ".join(values)


with QUEUE_PATH.open(encoding="utf-8-sig", newline="") as handle:
    queue = [
        row
        for row in csv.DictReader(handle)
        if row["estado_busqueda_patrimonial"] in REVIEW_STATUSES
        or row["persona_id"] in ALL_RESOLUTIONS
        or row["persona_id"] in ALL_EXCLUSIONS
    ]

assert len(queue) == 21
names = {
    clean(candidate)
    for row in queue
    for candidate in row["oa_historial_nombres"].split("|")
    if clean(candidate)
}
raw_by_name: dict[str, list[dict[str, str]]] = defaultdict(list)

with zipfile.ZipFile(ZIP_PATH) as archive:
    for year in range(2017, 2025):
        member = f"declaraciones-juradas-{year}-consolidado-al-20251222.csv"
        with archive.open(member) as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for raw in csv.DictReader(text):
                    name = clean(raw.get("funcionario_apellido_nombre", ""))
                    if name in names:
                        raw_by_name[name].append({key: clean(value) for key, value in raw.items()})

assert names == set(raw_by_name)
output: list[dict[str, object]] = []
candidate_identifier_hash_by_pair: dict[tuple[str, str], str] = {}

for person in queue:
    oa_names = [clean(candidate) for candidate in person["oa_historial_nombres"].split("|") if clean(candidate)]
    by_cuit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for oa_name in oa_names:
        for raw in raw_by_name[oa_name]:
            by_cuit[raw["cuit"]].append(raw)

    for cuit, raw_rows in sorted(by_cuit.items(), key=lambda item: masked_person_key(item[0])):
        person_key = masked_person_key(cuit)
        cuit_digits = re.sub(r"\D", "", cuit)
        assert len(cuit_digits) == 11
        candidate_identifier_hash_by_pair[(person["persona_id"], person_key)] = hashlib.sha256(
            cuit_digits[2:-1].encode("utf-8")
        ).hexdigest()
        by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
        for raw in raw_rows:
            by_year[int(raw["anio"])].append(raw)
        selected = [max(rows, key=selection_key) for _, rows in sorted(by_year.items())]
        matching_years = [
            int(row["anio"])
            for row in selected
            if institution_match(person["nivel_cargo"], row.get("organismo", ""), row.get("cargo", ""))
        ]
        if matching_years:
            signal = "candidato_misma_institucion"
        elif person["nivel_cargo"] == "Legislaturas provinciales":
            signal = "requiere_puente_biografico_oficial"
        else:
            signal = "sin_coincidencia_institucional"

        output.append(
            {
                "persona_id": person["persona_id"],
                "persona": person["persona"],
                "nivel_cargo": person["nivel_cargo"],
                "jurisdiccion": person["jurisdiccion"],
                "estado_revision": person["estado_busqueda_patrimonial"],
                "oa_nombre": compact_history(selected, "funcionario_apellido_nombre"),
                "oa_person_key": person_key,
                "anios": "|".join(row["anio"] for row in selected),
                "presentaciones_seleccionadas": len(selected),
                "anios_misma_institucion": "|".join(map(str, matching_years)),
                "organismos": compact_history(selected, "organismo"),
                "cargos": compact_history(selected, "cargo"),
                "senal_preclasificacion": signal,
                "publicable": "no",
                "motivo_no_publicacion": "La clave fiscal permanece enmascarada y requiere evidencia oficial independiente que vincule esta trayectoria con la persona vigente.",
            }
        )

fieldnames = list(output[0])
with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)

assert len({(row["persona_id"], row["oa_person_key"]) for row in output}) == len(output)
assert all(len(str(row["oa_person_key"])) == 16 for row in output)
assert all(row["publicable"] == "no" for row in output)

candidate_by_pair = {
    (str(row["persona_id"]), str(row["oa_person_key"])): row
    for row in output
}
queue_by_id = {row["persona_id"]: row for row in queue}

hcdn_parser = HcdnTableParser()
hcdn_parser.feed(HCDN_DDJJ_PATH.read_text(encoding="utf-8", errors="replace"))
hcdn_names_by_district = {
    (normalize(f"{cells[0]} {cells[1]}"), canonical_district(cells[2]))
    for cells in hcdn_parser.rows
    if len(cells) >= 4 and "2025" in cells[3]
}

senate_parser = SenateNameParser()
senate_parser.feed(SENATE_ROSTER_PATH.read_text(encoding="utf-8", errors="replace"))
assert any(normalize(name) == "MARIANO RECALDE" for name in senate_parser.names)
assert hashlib.sha256(RIO_NEGRO_ELECTION_PATH.read_bytes()).hexdigest() == RIO_NEGRO_ELECTION_SHA256
assert hashlib.sha256(HCDN_OPTIONS_2025_PATH.read_bytes()).hexdigest() == HCDN_OPTIONS_2025_SHA256
for identity_path in (
    HCDN_ALVARO_GARCIA_PATH,
    BOLETIN_ALVARO_GARCIA_PATH,
    PBA_MARIA_LAURA_FERNANDEZ_PATH,
    PBA_DDJJ_2018_PATH,
):
    assert identity_path.is_file()

resolution_rows_by_iteration: dict[int, list[dict[str, object]]] = {}
for iteration, resolutions in RESOLUTIONS_BY_ITERATION.items():
    resolution_rows: list[dict[str, object]] = []
    for person_id, resolution in resolutions.items():
        person = queue_by_id[person_id]
        candidate = candidate_by_pair[(person_id, resolution["oa_person_key"])]
        assert normalize(str(candidate["oa_nombre"])) == normalize(resolution["oa_nombre"])
        complementary_urls = ""
        complementary_backups = ""

        method = resolution["metodo"]
        if method.startswith("presentacion_hcdn"):
            assert (
                normalize(resolution["oa_nombre"]),
                canonical_district(person["jurisdiccion"]),
            ) in hcdn_names_by_district
            identity_url = "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/index.html"
            identity_backup = "sources/active_roster/hcdn_ddjj_ejercicio_2025_2026-09-01.html"
            evidence = (
                "La presentación HCDN 2025 aporta apellido, nombres completos y distrito; el candidato OA conserva "
                "la misma identidad nominal y registra cargo de diputado nacional."
            )
        elif method.startswith("hcdn_opciones_2025"):
            assert candidate["anios_misma_institucion"]
            identity_url = "https://www3.hcdn.gob.ar/archivos/transparencia/Opciones2025.pdf"
            identity_backup = "sources/identity_crosswalk/hcdn_opciones_viajes_nacionales_2025.pdf"
            evidence = (
                "El listado HCDN de opciones de viajes 2025 publica nombre completo y distrito del diputado; "
                "esa combinación coincide con el candidato OA cuya clave registra cargo de diputado nacional y "
                "separa a los homónimos de otros organismos o distritos."
            )
        elif method.startswith("biografia_oficial_caba"):
            assert person_id == "prov-caba-leg-alonso-laura"
            assert candidate["anios"] == "2017|2018|2019"
            assert "ETICA PUBLICA" in normalize(str(candidate["cargos"]))
            for evidence_path in (
                CABA_LAURA_ALONSO_PATH,
                JUSBAIRES_LAURA_ALONSO_PATH,
                OA_LAURA_ALONSO_DECREE_PATH,
            ):
                assert evidence_path.is_file()
            identity_url = "https://consejo.jusbaires.gob.ar/2congreso-internacional-de-contrataciones-publicas/expositores/laura-alonso/"
            identity_backup = "sources/identity_crosswalk/jusbaires_laura_alonso_cv.html"
            evidence = (
                "El perfil vigente de la Legislatura identifica a Laura Alonso; la biografía institucional del "
                "Consejo de la Magistratura la vincula con la titularidad de la Oficina Anticorrupción entre 2015 "
                "y 2019, y el decreto 252/2015 documenta su designación. La clave OA exacta registra ese mismo cargo."
            )
            complementary_urls = (
                "https://www.legislatura.gob.ar/legislador/alonsolaura | "
                "https://www.argentina.gob.ar/normativa/nacional/norma-257350/texto"
            )
            complementary_backups = (
                "sources/identity_crosswalk/caba_legislatura_laura_alonso_2026.html | "
                "sources/identity_crosswalk/decreto_252_2015_laura_alonso_oa.html"
            )
        elif method.startswith("perfil_hcdn_y_boletin_oficial"):
            assert person_id == "dip-garcia-alvaro"
            assert resolution["oa_nombre"] == "GARCIA ALVARO"
            assert candidate_identifier_hash_by_pair[(person_id, resolution["oa_person_key"])] == ALVARO_GARCIA_IDENTIFIER_SHA256
            identity_url = "https://www.hcdn.gob.ar/diputados/algarcia/"
            identity_backup = "sources/identity_crosswalk/hcdn_alvaro_garcia_profile_2026.html"
            evidence = (
                "El perfil HCDN y el Boletín Oficial coinciden en nombre, fecha de nacimiento y profesión. "
                "El documento publicado por el Boletín coincide de forma reservada con una sola clave OA: "
                "GARCIA ALVARO. No se publican DNI ni CUIT."
            )
            complementary_urls = "https://otslist.boletinoficial.gob.ar/ots/download/f411488ef77dcbba85e5b190c542b6b24641bcf563eaa57b33157cc10c0fe90a/0/"
            complementary_backups = "sources/identity_crosswalk/boletin_oficial_alvaro_garcia_2023.pdf"
        elif method.startswith("padron_senado"):
            assert resolution["oa_nombre"] == "RECALDE MARIANO"
            assert candidate["anios_misma_institucion"] == "2018|2019|2020|2021|2022|2023|2024"
            identity_url = "https://www.senado.gob.ar/senadores/listados/listaSenadoRes"
            identity_backup = "sources/active_roster/senado_listado_vigente_2026-09-01.html"
            evidence = (
                "El padrón vigente del Senado coincide exactamente con RECALDE MARIANO; la única clave OA con ese "
                "nombre exacto registra Senado en los siete ejercicios, mientras el homónimo con segundo nombre "
                "pertenece a Gendarmería."
            )
        else:
            assert person_id == "prov-rn-leg-martin-juan-carlos"
            assert resolution["oa_nombre"] == "MARTIN JUAN CARLOS"
            identity_url = "https://www.electoral.gob.ar/nuevo/paginas/pdf/BEP%204-2023.pdf"
            identity_backup = "sources/subnational_roster/rio_negro_acta_proclamacion_2023.pdf"
            evidence = (
                "El acta de proclamación electoral 2023 identifica al legislador con documento. La comparación "
                "reservada contra el identificador fiscal OA coincide sólo con esta clave; no se publican DNI ni CUIT."
            )

        resolution_rows.append(
            {
                "persona_id": person_id,
                "persona": person["persona"],
                "jurisdiccion": person["jurisdiccion"],
                "oa_nombre_resuelto": resolution["oa_nombre"],
                "oa_person_key": resolution["oa_person_key"],
                "metodo_resolucion": method,
                "fuente_identidad_url": identity_url,
                "respaldo_identidad_local": identity_backup,
                "fuente_oa_url": "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales",
                "respaldo_oa_local": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
                "nota_evidencia": evidence,
                "fuentes_complementarias_url": complementary_urls,
                "respaldos_complementarios_locales": complementary_backups,
                "publicable_tras_auditoria": "sí",
            }
        )

    resolutions_path = DERIVED / f"active_politician_homonymy_resolutions_iteration_{iteration}_2026-09-01.csv"
    with resolutions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(resolution_rows[0]))
        writer.writeheader()
        writer.writerows(resolution_rows)
    resolution_rows_by_iteration[iteration] = resolution_rows

assert {iteration: len(rows) for iteration, rows in resolution_rows_by_iteration.items()} == {13: 7, 14: 5, 15: 1, 17: 1}

exclusion_rows_by_iteration: dict[int, list[dict[str, object]]] = {}
for iteration, exclusions in EXCLUSIONS_BY_ITERATION.items():
    exclusion_rows: list[dict[str, object]] = []
    for person_id, exclusion in exclusions.items():
        person = queue_by_id[person_id]
        candidates = [row for row in output if row["persona_id"] == person_id]
        retained_keys = exclusion["oa_person_keys_no_descartadas"]
        assert retained_keys <= {str(row["oa_person_key"]) for row in candidates}
        retained = [row for row in candidates if row["oa_person_key"] in retained_keys]
        discarded = [row for row in candidates if row["oa_person_key"] not in retained_keys]
        assert discarded
        if exclusion["alcance_descarte"].startswith("total_"):
            assert not retained
        else:
            assert len(retained) == 1
        assert (ROOT / exclusion["respaldo_identidad_local"]).is_file()
        official_identifier_hash = exclusion.get("identificador_oficial_sha256", "")
        if official_identifier_hash:
            candidate_identifier_hashes = {
                candidate_identifier_hash_by_pair[(person_id, str(row["oa_person_key"]))]
                for row in candidates
            }
            assert official_identifier_hash not in candidate_identifier_hashes
        exclusion_rows.append(
            {
                "persona_id": person_id,
                "persona": person["persona"],
                "jurisdiccion": person["jurisdiccion"],
                "nombre_completo_oficial": exclusion["nombre_completo_oficial"],
                "alcance_descarte": exclusion["alcance_descarte"],
                "oa_candidatos_descartados": " | ".join(str(row["oa_nombre"]) for row in discarded),
                "oa_person_keys_descartadas": "|".join(str(row["oa_person_key"]) for row in discarded),
                "oa_candidatos_no_descartados": " | ".join(str(row["oa_nombre"]) for row in retained),
                "oa_person_keys_no_descartadas": "|".join(str(row["oa_person_key"]) for row in retained),
                "metodo_descarte": exclusion["metodo"],
                "fuente_identidad_url": exclusion["fuente_identidad_url"],
                "respaldo_identidad_local": exclusion["respaldo_identidad_local"],
                "fuentes_complementarias_url": exclusion.get("fuentes_complementarias_url", ""),
                "respaldos_complementarios_locales": exclusion.get("respaldos_complementarios_locales", ""),
                "nota_evidencia": exclusion["nota_evidencia"],
                "cotejo_identificador_reservado": "sin_coincidencia" if official_identifier_hash else "no_aplica",
                "publicable_en_tab": "no",
            }
        )
    exclusions_path = DERIVED / f"active_politician_homonymy_exclusions_iteration_{iteration}_2026-09-01.csv"
    with exclusions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(exclusion_rows[0]))
        writer.writeheader()
        writer.writerows(exclusion_rows)
    exclusion_rows_by_iteration[iteration] = exclusion_rows

assert {iteration: len(rows) for iteration, rows in exclusion_rows_by_iteration.items()} == {15: 5, 16: 3, 17: 1}
assert sum(row["alcance_descarte"].startswith("total_") for row in exclusion_rows_by_iteration[15]) == 3
assert sum(row["alcance_descarte"].startswith("parcial_") for row in exclusion_rows_by_iteration[15]) == 2
assert all(row["alcance_descarte"].startswith("total_") for row in exclusion_rows_by_iteration[16])
assert all(row["cotejo_identificador_reservado"] == "sin_coincidencia" for row in exclusion_rows_by_iteration[16])
assert all(row["alcance_descarte"].startswith("total_") for row in exclusion_rows_by_iteration[17])
assert all(row["cotejo_identificador_reservado"] == "sin_coincidencia" for row in exclusion_rows_by_iteration[17])

print(
    f"Auditoría de homonimias: {len(queue)} personas, {len(output)} claves enmascaradas, "
    f"{sum(row['senal_preclasificacion'] == 'candidato_misma_institucion' for row in output)} candidatos con señal institucional; "
    f"{sum(len(rows) for rows in resolution_rows_by_iteration.values())} resoluciones respaldadas y "
    f"{sum(len(rows) for rows in exclusion_rows_by_iteration.values())} descartes documentados."
)
