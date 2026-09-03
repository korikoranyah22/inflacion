from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources" / "active_roster"
DERIVED = ROOT / "derived"
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"

HCDN_ROSTER = SOURCES / "hcdn_diputados_vigentes_2026-09-01.csv"
HCDN_DDJJ_2025 = SOURCES / "hcdn_ddjj_ejercicio_2025_2026-09-01.html"
HCDN_DDJJ_2026 = SOURCES / "hcdn_ddjj_ejercicio_2026_2026-09-01.html"
SENATE_ROSTER = SOURCES / "senado_listado_vigente_2026-09-01.html"
SENATE_DDJJ_2025 = SOURCES / "senado_ddjj_2025_2026-09-01.html"
CFI_GOVERNORS = SOURCES / "cfi_gobernadores_2026-09-01.html"
SUBNATIONAL = ROOT / "sources" / "subnational_roster"
BA_DEPUTIES = SUBNATIONAL / "buenos_aires_diputados_vigentes_2026-09-01.html"
BA_SENATORS = SUBNATIONAL / "buenos_aires_senadores_vigentes_2026-09-01.html"
CABA_LEGISLATORS = SUBNATIONAL / "caba_legisladores_vigentes_2026-09-01.xml"
CORDOBA_LEGISLATORS = SUBNATIONAL / "cordoba_legisladores_vigentes_2026-09-01.json"
SANTA_FE_DEPUTIES = [
    SUBNATIONAL / "santa_fe_diputados_vigentes_2026-09-01.html",
    *(
        SUBNATIONAL / f"santa_fe_diputados_vigentes_p{page}_2026-09-01.html"
        for page in range(2, 6)
    ),
]
SANTA_FE_SENATORS = SUBNATIONAL / "santa_fe_senadores_vigentes_2026-09-01.html"
RIO_NEGRO_LEGISLATORS = SUBNATIONAL / "rio_negro_legisladores_vigentes_2026-09-01.csv"
MISIONES_LEGISLATORS = SUBNATIONAL / "misiones_diputados_vigentes_2026-09-01.html"

HCDN_URL = "https://www.hcdn.gob.ar/diputados/"
HCDN_DDJJ_URL = "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/index.html"
SENATE_URL = "https://www.senado.gob.ar/senadores/listados/listaSenadoRes"
SENATE_DDJJ_URL = "https://www.senado.gob.ar/administrativo/ddjj/"
CFI_URL = "https://cfi.org.ar/quienes_somos"
OA_DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
BA_DEPUTIES_URL = "https://www.hcdiputados-ba.gov.ar/index.php?page=diputados&search=seccionBloques"
BA_SENATORS_URL = "https://senado-ba.gov.ar/Senadores.aspx"
CABA_LEGISLATORS_URL = "https://www.legislatura.gob.ar/seccion/composicion-actual.html"
CABA_DDJJ_URL = "https://www.legislatura.gob.ar/seccion/listado-diputados-djpi.html"
CORDOBA_LEGISLATORS_URL = "https://legislaturacba.gob.ar/composicion-de-la-camara/"
CORDOBA_DDJJ_URL = "https://legislaturacba.gob.ar/declaraciones-juradas/"
SANTA_FE_DEPUTIES_URL = "https://diputadossantafe.gov.ar/web/camara/diputados"
SANTA_FE_SENATORS_URL = "https://www.senadosantafe.gob.ar/"
RIO_NEGRO_LEGISLATORS_URL = "https://web.legisrn.gov.ar/institucional/legisladores"
MISIONES_LEGISLATORS_URL = "https://www.diputadosmisiones.gov.ar/nuevo/diputados"

PROVINCIAL_STRUCTURE = [
    ("Buenos Aires", "Buenos Aires", "Bicameral", 92, 46, 135),
    ("Catamarca", "Catamarca", "Bicameral", 41, 16, 36),
    ("Chaco", "Chaco", "Unicameral", 32, 0, 70),
    ("Chubut", "Chubut", "Unicameral", 27, 0, 47),
    ("Ciudad Autónoma de Buenos Aires", "CABA", "Unicameral", 60, 0, 0),
    ("Córdoba", "Córdoba", "Unicameral", 70, 0, 259),
    ("Corrientes", "Corrientes", "Bicameral", 30, 15, 74),
    ("Entre Ríos", "Entre Ríos", "Bicameral", 34, 17, 83),
    ("Formosa", "Formosa", "Unicameral", 30, 0, 37),
    ("Jujuy", "Jujuy", "Unicameral", 48, 0, 28),
    ("La Pampa", "La Pampa", "Unicameral", 30, 0, 61),
    ("La Rioja", "La Rioja", "Unicameral", 36, 0, 18),
    ("Mendoza", "Mendoza", "Bicameral", 48, 38, 18),
    ("Misiones", "Misiones", "Unicameral", 40, 0, 78),
    ("Neuquén", "Neuquén", "Unicameral", 35, 0, 26),
    ("Río Negro", "Río Negro", "Unicameral", 46, 0, 39),
    ("Salta", "Salta", "Bicameral", 60, 23, 60),
    ("San Juan", "San Juan", "Unicameral", 36, 0, 19),
    ("San Luis", "San Luis", "Bicameral", 43, 9, 66),
    ("Santa Cruz", "Santa Cruz", "Unicameral", 24, 0, 15),
    ("Santa Fe", "Santa Fe", "Bicameral", 50, 19, 56),
    ("Santiago del Estero", "Santiago del Estero", "Unicameral", 40, 0, 28),
    ("Tierra del Fuego", "Tierra del Fuego", "Unicameral", 15, 0, 3),
    ("Tucumán", "Tucumán", "Unicameral", 49, 0, 19),
]

PROVINCIAL_NOMINAL_SOURCES = {
    "Buenos Aires": (BA_DEPUTIES_URL, "nómina oficial incorporada", "ruta provincial por relevar"),
    "Ciudad Autónoma de Buenos Aires": (CABA_LEGISLATORS_URL, "nómina oficial incorporada", "listado DJPI 2025 publicado; cruce nominal pendiente"),
    "Córdoba": (CORDOBA_LEGISLATORS_URL, "nómina oficial incorporada", "ruta oficial localizada; cruce nominal pendiente"),
    "Santa Fe": (SANTA_FE_DEPUTIES_URL, "nómina oficial incorporada", "ruta provincial por relevar"),
    "Río Negro": (RIO_NEGRO_LEGISLATORS_URL, "nómina oficial incorporada", "ruta provincial por relevar"),
    "Misiones": (MISIONES_LEGISLATORS_URL, "nómina oficial incorporada", "ruta provincial por relevar"),
}

CURATED_SERIES = {
    "MAXIMO KIRCHNER": "maximo",
    "CRISTINA FERNANDEZ DE KIRCHNER": "cristina",
    "SERGIO MASSA": "massa",
    "MAURICIO MACRI": "macri",
    "LUIS CAPUTO": "caputo",
    "JAVIER MILEI": "javier",
    "MARTIN MENEM": "martin",
    "KARINA MILEI": "karina",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.upper().replace("Ñ", "N")
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    return " ".join(value.split())


def slug(value: str) -> str:
    return normalize(value).lower().replace(" ", "-")


def clean(value: str) -> str:
    return " ".join((value or "").replace('""', "").split()).strip('" ')


def parse_tree(path: Path):
    return html.fromstring(path.read_bytes())


def parse_hcdn_roster() -> list[dict[str, str]]:
    with HCDN_ROSTER.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 257, f"Se esperaban 257 diputados y llegaron {len(rows)}"
    return [{key: clean(value) for key, value in row.items()} for row in rows]


def parse_senate_roster() -> list[dict[str, str]]:
    tree = parse_tree(SENATE_ROSTER)
    rows = []
    for tr in tree.xpath('//table[@id="senadoresTabla"]/tbody/tr'):
        cells = [" ".join(td.text_content().split()) for td in tr.xpath("./td")]
        if len(cells) < 5 or "," not in cells[1]:
            continue
        surname, given = [clean(part) for part in cells[1].split(",", 1)]
        dates = re.findall(r"\d{2}/\d{2}/\d{4}", cells[4])
        rows.append(
            {
                "Apellido": surname,
                "Nombre": given,
                "Distrito": clean(cells[2]),
                "Partido": clean(cells[3]),
                "IniciaMandato": dates[0] if dates else "",
                "FinalizaMandato": dates[1] if len(dates) > 1 else "",
            }
        )
    assert len(rows) == 72, f"Se esperaban 72 senadores y llegaron {len(rows)}"
    return rows


def parse_hcdn_presentations(path: Path) -> list[dict[str, str]]:
    tree = parse_tree(path)
    rows = []
    for tr in tree.xpath('//table[@id="tabla"]/tbody/tr'):
        cells = [" ".join(td.text_content().split()) for td in tr.xpath("./td")]
        if len(cells) >= 4:
            rows.append(
                {
                    "apellido": clean(cells[0]),
                    "nombre": clean(cells[1]),
                    "distrito": clean(cells[2]),
                    "tipo": clean(cells[3]),
                }
            )
    return rows


def parse_senate_presentations() -> list[dict[str, str]]:
    tree = parse_tree(SENATE_DDJJ_2025)
    rows = []
    for tr in tree.xpath("//table//tbody/tr"):
        cells = [" ".join(td.text_content().split()) for td in tr.xpath("./td")]
        if len(cells) == 5 and cells[4] == "2025":
            rows.append(
                {
                    "apellido": clean(cells[0]),
                    "nombre": clean(cells[1]),
                    "distrito": clean(cells[2]),
                    "tipo": clean(cells[3]) + " 2025",
                }
            )
    assert rows, "No se encontraron presentaciones 2025 del Senado"
    return rows


def load_oa_index() -> dict[str, set[int]]:
    result: dict[str, set[int]] = defaultdict(set)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        for year in range(2017, 2025):
            member = f"declaraciones-juradas-{year}-consolidado-al-20251222.csv"
            with archive.open(member) as binary:
                with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                    for row in csv.DictReader(text):
                        name = clean(row.get("funcionario_apellido_nombre", ""))
                        if name:
                            result[name].add(year)
    return result


def match_name(surname: str, given: str, candidate_name: str) -> bool:
    surname_norm = normalize(surname)
    given_tokens = normalize(given).split()
    candidate_norm = normalize(candidate_name)
    if not surname_norm or not given_tokens:
        return False
    if not candidate_norm.startswith(surname_norm + " "):
        return False
    remaining = candidate_norm[len(surname_norm) :].split()
    return remaining[: len(given_tokens)] == given_tokens


def matched_oa(
    surname: str,
    given: str,
    search_index: list[tuple[str, str, set[int]]],
) -> tuple[list[str], list[int]]:
    surname_norm = normalize(surname)
    given_tokens = normalize(given).split()
    if not surname_norm or not given_tokens:
        return [], []
    prefix = surname_norm + " "
    matches_with_years = [
        (name, years)
        for name, candidate_norm, years in search_index
        if candidate_norm.startswith(prefix)
        and candidate_norm[len(prefix) :].split()[: len(given_tokens)] == given_tokens
    ]
    matches = sorted(name for name, _ in matches_with_years)
    years = sorted({year for _, item_years in matches_with_years for year in item_years})
    return matches, years


def matched_oa_full_name(
    full_name: str,
    search_index: list[tuple[str, str, set[int]]],
) -> tuple[list[str], list[int]]:
    target = normalize(full_name)
    matches_with_years = [
        (name, years)
        for name, candidate_norm, years in search_index
        if candidate_norm == target
    ]
    matches = sorted(name for name, _ in matches_with_years)
    years = sorted({year for _, item_years in matches_with_years for year in item_years})
    return matches, years


def parse_ba_deputies() -> list[dict[str, str]]:
    tree = parse_tree(BA_DEPUTIES)
    tables = tree.xpath("//table")
    assert len(tables) >= 2, "No se encontró la tabla completa de Diputados bonaerenses"
    rows = []
    for tr in tables[1].xpath(".//tbody/tr"):
        cells = tr.xpath("./td")
        if len(cells) < 4:
            continue
        name = clean(cells[0].text_content())
        info = " ".join(cells[3].text_content().split())
        district_match = re.search(r"DISTRITO:\s*(.*?)\s*SECCIÓN ELECTORAL:", info, re.I)
        section_match = re.search(r"SECCIÓN ELECTORAL:\s*(.*?)\s*OFICINA:", info, re.I)
        rows.append(
            {
                "full_name": name,
                "block": clean(cells[1].text_content()),
                "mandate": clean(cells[2].text_content()),
                "district": clean(district_match.group(1)) if district_match else "",
                "section": clean(section_match.group(1)) if section_match else "",
            }
        )
    assert len(rows) == 92, f"Se esperaban 92 diputados bonaerenses y llegaron {len(rows)}"
    return rows


def parse_ba_senators() -> list[dict[str, str]]:
    tree = parse_tree(BA_SENATORS)
    rows = []
    for article in tree.xpath('//article[contains(@class,"mix-3")]'):
        name = clean(" ".join(article.xpath('.//*[contains(@class,"NombreSenador2")]/text()'))).replace("&nbsp", "")
        block = clean(" ".join(article.xpath('.//*[contains(@class,"BloqueSenador")]/text()'))).replace("&nbsp", "")
        section = clean(" ".join(article.xpath('.//*[contains(@class,"SeccionSenador")]/text()'))).replace("&nbsp", "")
        mandate = clean(" ".join(article.xpath('.//*[contains(@class,"MandatoSenador")]/text()'))).replace("&nbsp", "")
        if "," not in name:
            continue
        surname, given = [clean(part) for part in name.split(",", 1)]
        rows.append({"surname": surname, "given": given, "block": block, "section": section, "mandate": mandate})
    assert len(rows) == 46, f"Se esperaban 46 senadores bonaerenses y llegaron {len(rows)}"
    return rows


def parse_caba_legislators() -> list[dict[str, str]]:
    tree = etree.parse(str(CABA_LEGISLATORS))
    rows = []
    for item in tree.xpath('//*[local-name()="diputados"]'):
        value = lambda name: clean("".join(item.xpath(f'./*[local-name()="{name}"]/text()')))
        rows.append(
            {
                "surname": value("apellido"),
                "given": value("nombre"),
                "block": value("bloque"),
                "start": value("fecha_inicio_mandato"),
                "end": value("fecha_fin_mandato"),
            }
        )
    assert len(rows) == 60, f"Se esperaban 60 legisladores porteños y llegaron {len(rows)}"
    return rows


def parse_cordoba_legislators() -> list[dict[str, str]]:
    raw = json.loads(CORDOBA_LEGISLATORS.read_text(encoding="utf-8-sig"))
    rows = [item for item in raw if clean(str(item.get("apellido", "")))]
    assert len(rows) == 70, f"Se esperaban 70 legisladores cordobeses y llegaron {len(rows)}"
    return rows


def parse_santa_fe_deputies() -> list[dict[str, str]]:
    rows = []
    for path in SANTA_FE_DEPUTIES:
        tree = parse_tree(path)
        for card in tree.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " autoridad-little ")]'):
            name = clean(" ".join(card.xpath(".//h4//text()")))
            block = clean(" ".join(card.xpath(".//h5//text()")))
            if "," not in name:
                continue
            surname, given = [clean(part) for part in name.split(",", 1)]
            rows.append(
                {
                    "surname": surname,
                    "given": given,
                    "block": re.sub(r"^BLOQUE\s+", "", block, flags=re.IGNORECASE),
                    "local": f"sources/subnational_roster/{path.name}",
                }
            )
    assert len(rows) == 50, f"Se esperaban 50 diputados santafesinos y llegaron {len(rows)}"
    return rows


def parse_santa_fe_senators() -> list[dict[str, str]]:
    tree = parse_tree(SANTA_FE_SENATORS)
    rows = []
    seen = set()
    for card in tree.xpath('//article[contains(@class, "node-autoridades-senadores")]'):
        card_id = clean(card.get("id", ""))
        if card_id in seen:
            continue
        seen.add(card_id)
        given = clean(" ".join(card.xpath('.//div[contains(@class, "field-name-field-nombre")]//div[contains(@class, "field-item")]/text()')))
        surname = clean(" ".join(card.xpath('.//div[contains(@class, "field-name-field-apellido")]//div[contains(@class, "field-item")]/text()')))
        department = clean(" ".join(card.xpath('.//div[contains(@class, "departamento-title")]//h2//text()')))
        mandate = clean(" ".join(card.xpath('.//div[contains(@class, "field-name-field-mandato")]//div[contains(@class, "field-item")]/text()')))
        block = clean(" ".join(card.xpath('.//div[contains(@class, "field-name-field-bloque")]//div[contains(@class, "field-item")]/text()')))
        if given and surname:
            rows.append(
                {
                    "surname": surname,
                    "given": given,
                    "department": department,
                    "mandate": mandate,
                    "block": block,
                }
            )
    assert len(rows) == 19, f"Se esperaban 19 senadores santafesinos y llegaron {len(rows)}"
    return rows


def parse_rio_negro_legislators() -> list[dict[str, str]]:
    with RIO_NEGRO_LEGISLATORS.open(encoding="utf-8", newline="") as handle:
        rows = [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    assert len(rows) == 46, f"Se esperaban 46 legisladores rionegrinos y llegaron {len(rows)}"
    assert len({normalize(row["apellido"] + " " + row["nombre"]) for row in rows}) == 46
    return rows


def parse_misiones_legislators() -> list[dict[str, str]]:
    tree = parse_tree(MISIONES_LEGISLATORS)
    rows = []
    no_comma_names = {
        normalize("Mendez Ason Maria del Carmen"): ("Mendez Ason", "Maria del Carmen"),
        normalize("Tartaglino Lilian Catalina"): ("Tartaglino", "Lilian Catalina"),
    }
    for card in tree.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " slider-item ")]//div[contains(concat(" ", normalize-space(@class), " "), " card ")]'):
        texts = [clean(" ".join(item.xpath(".//text()"))) for item in card.xpath(".//p")]
        if not texts or not texts[0]:
            continue
        full_name = texts[0]
        if "," in full_name:
            surname, given = [clean(part) for part in full_name.split(",", 1)]
        else:
            surname, given = no_comma_names[normalize(full_name)]
        rows.append({"surname": surname, "given": given, "block": texts[1] if len(texts) > 1 else ""})
    assert len(rows) == 40, f"Se esperaban 40 legisladores misioneros y llegaron {len(rows)}"
    assert len({normalize(row["surname"] + " " + row["given"]) for row in rows}) == 40
    return rows


def normalize_district(value: str) -> str:
    normalized = normalize(value)
    if normalized in {"CABA", "CIUDAD DE BUENOS AIRES", "CIUDAD AUTONOMA DE BUENOS AIRES"}:
        return "CABA"
    if normalized.startswith("TIERRA DEL FUEGO"):
        return "TIERRA DEL FUEGO"
    return normalized


def matched_presentations(
    surname: str,
    given: str,
    district: str,
    rows: list[dict[str, str]],
) -> list[str]:
    surname_norm = normalize(surname)
    given_first = normalize(given).split()[0] if normalize(given) else ""
    district_norm = normalize_district(district)
    return sorted(
        {
            row["tipo"]
            for row in rows
            if normalize(row["apellido"]) == surname_norm
            and normalize(row["nombre"]).split()[:1] == [given_first]
            and normalize_district(row["distrito"]) == district_norm
        }
    )


def display_name(given: str, surname: str) -> str:
    return clean(f"{given} {surname}")


EXECUTIVE = [
    {
        "surname": "Milei", "given": "Javier Gerardo", "cargo": "Presidente de la Nación",
        "jurisdiccion": "Nación", "inicio": "10/12/2023", "alianza": "La Libertad Avanza",
        "source_url": "https://www.argentina.gob.ar/presidencia", "source_local": "sources/active_roster/presidencia_autoridades_2026-09-01.html",
    },
    {
        "surname": "Villarruel", "given": "Victoria Eugenia", "cargo": "Vicepresidenta de la Nación",
        "jurisdiccion": "Nación", "inicio": "10/12/2023", "alianza": "La Libertad Avanza",
        "source_url": "https://www.senado.gob.ar/presidencia", "source_local": "sources/active_roster/senado_presidencia_2026-09-01.html",
    },
    {
        "surname": "Santilli", "given": "Diego César", "cargo": "Jefe de Gabinete de Ministros",
        "jurisdiccion": "Nación", "inicio": "29/06/2026", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/normativa/nacional/norma-427132/texto", "source_local": "sources/active_roster/decreto_548_2026_jefe_gabinete.html",
    },
    {
        "surname": "Coria", "given": "Gustavo Javier", "cargo": "Vicejefe de Gabinete del Interior",
        "jurisdiccion": "Nación", "inicio": "02/07/2026", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/interior/transparencia/autoridades-personal", "source_local": "sources/active_roster/vicejefatura_interior_autoridades_2026-09-01.html",
    },
    {
        "surname": "Milei", "given": "Karina Elizabeth", "cargo": "Secretaria General de la Presidencia",
        "jurisdiccion": "Nación", "inicio": "10/12/2023", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/node/81433", "source_local": "sources/active_roster/presidencia_autoridades_2026-09-01.html",
    },
    {
        "surname": "Quirno", "given": "Pablo", "cargo": "Ministro de Relaciones Exteriores, Comercio Internacional y Culto",
        "jurisdiccion": "Nación", "inicio": "", "alianza": "Designación PEN",
        "source_url": "https://www.cancilleria.gob.ar/es/ministerio-de-relaciones-exteriores-comercio-internacional-y-culto", "source_local": "sources/active_roster/cancilleria_autoridad_2026-09-01.html",
    },
    {
        "surname": "Presti", "given": "Carlos Alberto", "cargo": "Ministro de Defensa",
        "jurisdiccion": "Nación", "inicio": "10/12/2025", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/defensa/transparencia/autoridades-personal", "source_local": "sources/active_roster/defensa_autoridades_2026-09-01.html",
    },
    {
        "surname": "Caputo", "given": "Luis Andrés", "cargo": "Ministro de Economía",
        "jurisdiccion": "Nación", "inicio": "10/12/2023", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/node/72493", "source_local": "sources/active_roster/economia_autoridades_2026-09-01.html",
    },
    {
        "surname": "Mahiques", "given": "Juan Bautista", "cargo": "Ministro de Justicia",
        "jurisdiccion": "Nación", "inicio": "05/03/2026", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/justicia/transparencia/autoridades-personal", "source_local": "sources/active_roster/justicia_autoridades_2026-09-01.html",
    },
    {
        "surname": "Monteoliva", "given": "Alejandra Susana", "cargo": "Ministra de Seguridad Nacional",
        "jurisdiccion": "Nación", "inicio": "09/12/2025", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/seguridad/transparencia/autoridades-personal", "source_local": "sources/active_roster/seguridad_autoridades_2026-09-01.html",
    },
    {
        "surname": "Lugones", "given": "Mario Iván", "cargo": "Ministro de Salud",
        "jurisdiccion": "Nación", "inicio": "27/09/2024", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/salud/transparencia/autoridades-personal", "source_local": "sources/active_roster/salud_autoridades_2026-09-01.html",
    },
    {
        "surname": "Pettovello", "given": "Sandra Viviana", "cargo": "Ministra de Capital Humano",
        "jurisdiccion": "Nación", "inicio": "10/12/2023", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/capital-humano/transparencia-ministerio-de-capital-humano/organigrama-autoridades-y-personal", "source_local": "sources/active_roster/capital_humano_autoridades_2026-09-01.html",
    },
    {
        "surname": "Sturzenegger", "given": "Federico Adolfo", "cargo": "Ministro de Desregulación y Transformación del Estado",
        "jurisdiccion": "Nación", "inicio": "05/07/2024", "alianza": "Designación PEN",
        "source_url": "https://www.argentina.gob.ar/desregulacion", "source_local": "sources/active_roster/desregulacion_autoridad_2026-09-01.html",
    },
]


GOVERNORS = [
    ("Kicillof", "Axel", "Buenos Aires", "Fuerza Patria"),
    ("Jalil", "Raúl Alejandro", "Catamarca", "PJ"),
    ("Zdero", "Leandro César", "Chaco", "Chaco Puede + LLA"),
    ("Torres", "Ignacio Agustín", "Chubut", "Despierta Chubut"),
    ("Macri", "Jorge", "Ciudad Autónoma de Buenos Aires", "Vamos por más"),
    ("Llaryora", "Martín Miguel", "Córdoba", "Hacemos Unidos por Córdoba"),
    ("Valdés", "Juan Pablo", "Corrientes", "Vamos Corrientes"),
    ("Frigerio", "Rogelio", "Entre Ríos", "Juntos + LLA"),
    ("Insfrán", "Gildo", "Formosa", "PJ"),
    ("Sadir", "Carlos Alberto", "Jujuy", "Cambia Jujuy"),
    ("Ziliotto", "Sergio Raúl", "La Pampa", "PJ"),
    ("Jaldo", "Osvaldo Francisco", "Tucumán", "PJ"),
    ("Quintela", "Ricardo Clemente", "La Rioja", "Fuerza Patria"),
    ("Melella", "Gustavo Adrián", "Tierra del Fuego", "Unidos Hacemos Futuro"),
    ("Cornejo Neila", "Alfredo Víctor", "Mendoza", "Cambia Mendoza + LLA"),
    ("Suárez", "Elías", "Santiago del Estero", "Frente Cívico por Santiago"),
    ("Passalacqua", "Hugo Mario", "Misiones", "Frente Renovador de la Concordia"),
    ("Pullaro", "Maximiliano Nicolás", "Santa Fe", "Unidos para Cambiar Santa Fe"),
    ("Figueroa", "Rolando Ceferino", "Neuquén", "Comunidad"),
    ("Vidal", "Claudio Orlando", "Santa Cruz", "Por Santa Cruz"),
    ("Poggi", "Claudio Javier", "San Luis", "Ahora San Luis"),
    ("Orrego", "Marcelo Humberto", "San Juan", "Unidos por San Juan"),
    ("Weretilneck", "Alberto Edgardo", "Río Negro", "Juntos Somos Río Negro"),
    ("Sáenz", "Gustavo Adolfo", "Salta", "Identidad Salteña"),
]


def series_id_for(person: str) -> str:
    normalized = normalize(person)
    for key, series_id in CURATED_SERIES.items():
        if all(token in normalized.split() for token in key.split()):
            return series_id
    return ""


def make_row(
    *, prefix: str, surname: str, given: str, ambito: str, poder: str, nivel: str,
    cargo: str, jurisdiccion: str, alliance: str, start: str, end: str,
    roster_url: str, roster_local: str, ddjj_regime: str, ddjj_state: str,
    ddjj_detail: str, ddjj_url: str, oa_index: list[tuple[str, str, set[int]]], note: str,
    person_override: str = "", oa_full_name: str = "",
) -> dict[str, object]:
    person = clean(person_override) or display_name(given, surname)
    matches, years = matched_oa_full_name(oa_full_name, oa_index) if oa_full_name else matched_oa(surname, given, oa_index)
    if len(matches) == 1:
        history_state = "nombre_compatible_unico_en_oa"
    elif len(matches) > 1:
        history_state = "coincidencia_multiple_revisar_homonimia"
    else:
        history_state = "sin_nombre_compatible_oa_2017_2024"
    return {
        "persona_id": f"{prefix}-{slug(oa_full_name or surname + ' ' + given)}",
        "persona": person,
        "ambito": ambito,
        "poder": poder,
        "nivel_cargo": nivel,
        "cargo": cargo,
        "jurisdiccion": jurisdiccion,
        "partido_o_alianza": alliance,
        "mandato_inicio": start,
        "mandato_fin": end,
        "estado_actividad": "activo_al_2026-09-01",
        "fuente_padron_url": roster_url,
        "fuente_padron_local": roster_local,
        "regimen_ddjj_actual": ddjj_regime,
        "estado_ddjj_cargo_actual": ddjj_state,
        "detalle_ddjj_cargo_actual": ddjj_detail,
        "fuente_ddjj_actual_url": ddjj_url,
        "oa_historial_2017_2024_estado": history_state,
        "oa_historial_nombres": " | ".join(matches),
        "oa_anios_2017_2024": "|".join(map(str, years)),
        "oa_cantidad_anios_2017_2024": len(years),
        "oa_primer_anio": years[0] if years else "",
        "oa_ultimo_anio": years[-1] if years else "",
        "serie_tab_id": series_id_for(person),
        "nota_cobertura": note,
    }


def main() -> None:
    oa_raw_index = load_oa_index()
    oa_index = [(name, normalize(name), years) for name, years in oa_raw_index.items()]
    hcdn_presentations = parse_hcdn_presentations(HCDN_DDJJ_2025) + parse_hcdn_presentations(HCDN_DDJJ_2026)
    senate_presentations = parse_senate_presentations()
    rows: list[dict[str, object]] = []

    for item in parse_hcdn_roster():
        presentations = matched_presentations(item["Apellido"], item["Nombre"], item["Distrito"], hcdn_presentations)
        state = "presentacion_2025_2026_localizada" if presentations else "sin_presentacion_localizada_en_listados_2025_2026"
        rows.append(
            make_row(
                prefix="dip", surname=item["Apellido"], given=item["Nombre"], ambito="Nacional",
                poder="Legislativo", nivel="Diputados nacionales", cargo="Diputado/a nacional",
                jurisdiccion=item["Distrito"].title(), alliance=item["Bloque"], start=item["IniciaMandato"],
                end=item["FinalizaMandato"], roster_url=HCDN_URL,
                roster_local="sources/active_roster/hcdn_diputados_vigentes_2026-09-01.csv",
                ddjj_regime="Cámara de Diputados · Ley 25.188 / DSAD 545/2025", ddjj_state=state,
                ddjj_detail=" | ".join(presentations), ddjj_url=HCDN_DDJJ_URL, oa_index=oa_index,
                note="La Cámara publica cumplimiento. El cruce OA es nominal y no sustituye la verificación de CUIT, organismo y cargo antes de sumar una serie.",
            )
        )

    for item in parse_senate_roster():
        presentations = matched_presentations(item["Apellido"], item["Nombre"], item["Distrito"], senate_presentations)
        state = "presentacion_2025_localizada" if presentations else "sin_presentacion_2025_localizada"
        rows.append(
            make_row(
                prefix="sen", surname=item["Apellido"], given=item["Nombre"], ambito="Nacional",
                poder="Legislativo", nivel="Senado nacional", cargo="Senador/a nacional",
                jurisdiccion=item["Distrito"], alliance=item["Partido"], start=item["IniciaMandato"],
                end=item["FinalizaMandato"], roster_url=SENATE_URL,
                roster_local="sources/active_roster/senado_listado_vigente_2026-09-01.html",
                ddjj_regime="Senado · Ley 25.188 / RC 03/2013", ddjj_state=state,
                ddjj_detail=" | ".join(presentations), ddjj_url=SENATE_DDJJ_URL, oa_index=oa_index,
                note="El Senado publica cumplimiento. El cruce OA es nominal y no sustituye la verificación de CUIT, organismo y cargo antes de sumar una serie.",
            )
        )

    for item in EXECUTIVE:
        rows.append(
            make_row(
                prefix="pen", surname=item["surname"], given=item["given"], ambito="Nacional",
                poder="Ejecutivo", nivel="Conducción superior PEN", cargo=item["cargo"],
                jurisdiccion=item["jurisdiccion"], alliance=item["alianza"], start=item["inicio"], end="",
                roster_url=item["source_url"], roster_local=item["source_local"],
                ddjj_regime="Oficina Anticorrupción · Ley 25.188 / 26.857",
                ddjj_state="verificacion_2025_2026_pendiente",
                ddjj_detail="La base consolidada respaldada llega al ejercicio 2024.",
                ddjj_url=OA_DATASET_URL, oa_index=oa_index,
                note="Una designación posterior a 2024 puede no tener todavía un ejercicio anual en el consolidado respaldado.",
            )
        )

    cfi_text = normalize(CFI_GOVERNORS.read_text(encoding="utf-8", errors="ignore"))
    for surname, given, jurisdiction, alliance in GOVERNORS:
        assert normalize(surname) in cfi_text and normalize(given).split()[0] in cfi_text, f"No se corroboró {given} {surname} en CFI"
        cargo = "Jefe de Gobierno" if jurisdiction == "Ciudad Autónoma de Buenos Aires" else "Gobernador/a"
        rows.append(
            make_row(
                prefix="gov", surname=surname, given=given, ambito="Provincial/CABA", poder="Ejecutivo",
                nivel="Gobernaciones", cargo=cargo, jurisdiccion=jurisdiction, alliance=alliance,
                start="", end="", roster_url=CFI_URL,
                roster_local="sources/active_roster/cfi_gobernadores_2026-09-01.html",
                ddjj_regime="Régimen provincial o de CABA · heterogéneo",
                ddjj_state="ruta_provincial_por_relevar", ddjj_detail="No existe un repositorio federal único.",
                ddjj_url="", oa_index=oa_index,
                note="Una coincidencia nominal en OA puede corresponder a un cargo nacional previo y no sustituye la DDJJ del cargo provincial actual.",
            )
        )

    for item in parse_ba_deputies():
        tokens = item["full_name"].split()
        start, end = (item["mandate"].split("-", 1) + [""])[:2]
        rows.append(
            make_row(
                prefix="prov-ba-dip", surname=tokens[0], given=" ".join(tokens[1:]),
                person_override=item["full_name"].title(), oa_full_name=item["full_name"],
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Diputado/a provincial", jurisdiccion="Buenos Aires",
                alliance=item["block"], start=start, end=end, roster_url=BA_DEPUTIES_URL,
                roster_local="sources/subnational_roster/buenos_aires_diputados_vigentes_2026-09-01.html",
                ddjj_regime="Régimen provincial · ruta documental por relevar",
                ddjj_state="ruta_provincial_por_relevar",
                ddjj_detail=f"Distrito {item['district']} · sección {item['section']}", ddjj_url="",
                oa_index=oa_index,
                note="El orden oficial Apellido y Nombre se preserva. El cruce OA exige coincidencia nominal exacta para evitar dividir apellidos compuestos por inferencia.",
            )
        )

    for item in parse_ba_senators():
        start, end = (item["mandate"].split("-", 1) + [""])[:2]
        rows.append(
            make_row(
                prefix="prov-ba-sen", surname=item["surname"], given=item["given"],
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Senador/a provincial", jurisdiccion="Buenos Aires", alliance=item["block"],
                start=start, end=end, roster_url=BA_SENATORS_URL,
                roster_local="sources/subnational_roster/buenos_aires_senadores_vigentes_2026-09-01.html",
                ddjj_regime="Régimen provincial · ruta documental por relevar",
                ddjj_state="ruta_provincial_por_relevar", ddjj_detail=item["section"], ddjj_url="",
                oa_index=oa_index,
                note="La nómina y el mandato provienen de la Cámara; la ruta provincial de DDJJ queda separada.",
            )
        )

    for item in parse_caba_legislators():
        rows.append(
            make_row(
                prefix="prov-caba-leg", surname=item["surname"], given=item["given"],
                ambito="CABA", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Legislador/a de la Ciudad", jurisdiccion="Ciudad Autónoma de Buenos Aires",
                alliance=item["block"], start=item["start"], end=item["end"],
                roster_url=CABA_LEGISLATORS_URL,
                roster_local="sources/subnational_roster/caba_legisladores_vigentes_2026-09-01.xml",
                ddjj_regime="OIP Legislatura CABA · Ley 6.357",
                ddjj_state="listado_ddjj_2025_publicado_sin_cruce_nominal",
                ddjj_detail="La Legislatura publica el listado 2025; falta cruzar cada registro nominal.",
                ddjj_url=CABA_DDJJ_URL, oa_index=oa_index,
                note="La publicación del listado de DJPI confirma la ruta institucional, no la presentación individual hasta completar el cruce nominal.",
            )
        )

    for item in parse_cordoba_legislators():
        rows.append(
            make_row(
                prefix="prov-cba-leg", surname=clean(str(item["apellido"])), given=clean(str(item["nombre"])),
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Legislador/a provincial", jurisdiccion="Córdoba",
                alliance=clean(str(item.get("bloque", ""))), start="2023", end="2027",
                roster_url=CORDOBA_LEGISLATORS_URL,
                roster_local="sources/subnational_roster/cordoba_legisladores_vigentes_2026-09-01.json",
                ddjj_regime="Legislatura de Córdoba · publicación institucional",
                ddjj_state="ruta_provincial_localizada_sin_cruce_nominal",
                ddjj_detail="La sección oficial de DDJJ fue respaldada; falta verificación persona por persona.",
                ddjj_url=CORDOBA_DDJJ_URL, oa_index=oa_index,
                note=f"Banca {item.get('banca', '')} · distrito {clean(str(item.get('distrito', '')))}. No se publican DNI ni datos de contacto en el derivado.",
            )
        )

    for item in parse_santa_fe_deputies():
        rows.append(
            make_row(
                prefix="prov-sf-dip", surname=item["surname"], given=item["given"],
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Diputado/a provincial", jurisdiccion="Santa Fe", alliance=item["block"],
                start="2023", end="2027", roster_url=SANTA_FE_DEPUTIES_URL,
                roster_local=item["local"],
                ddjj_regime="Régimen provincial · ruta documental por relevar",
                ddjj_state="ruta_provincial_por_relevar",
                ddjj_detail="No se localizó todavía un listado nominal institucional de presentaciones.",
                ddjj_url="", oa_index=oa_index,
                note="La nómina y el bloque provienen de la Cámara de Diputadas y Diputados de Santa Fe.",
            )
        )

    for item in parse_santa_fe_senators():
        start, end = (item["mandate"].split("-", 1) + [""])[:2]
        rows.append(
            make_row(
                prefix="prov-sf-sen", surname=item["surname"], given=item["given"],
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Senador/a provincial", jurisdiccion="Santa Fe", alliance=item["block"],
                start=start, end=end, roster_url=SANTA_FE_SENATORS_URL,
                roster_local="sources/subnational_roster/santa_fe_senadores_vigentes_2026-09-01.html",
                ddjj_regime="Régimen provincial · ruta documental por relevar",
                ddjj_state="ruta_provincial_por_relevar", ddjj_detail=f"Departamento {item['department']}",
                ddjj_url="", oa_index=oa_index,
                note="La nómina, el departamento, el mandato y el bloque provienen de la Cámara de Senadores de Santa Fe.",
            )
        )

    for item in parse_rio_negro_legislators():
        rows.append(
            make_row(
                prefix="prov-rn-leg", surname=item["apellido"], given=item["nombre"],
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Legislador/a provincial", jurisdiccion="Río Negro", alliance=item["bloque"],
                start="", end="", roster_url=RIO_NEGRO_LEGISLATORS_URL,
                roster_local="sources/subnational_roster/rio_negro_legisladores_vigentes_2026-09-01.csv",
                ddjj_regime="Régimen provincial · ruta documental por relevar",
                ddjj_state="ruta_provincial_por_relevar",
                ddjj_detail="No se localizó todavía un listado nominal institucional de presentaciones.",
                ddjj_url="", oa_index=oa_index,
                note="Transcripción estructurada de la nómina y los ocho bloques publicados por la Legislatura de Río Negro; cada fila conserva su URL oficial de bloque.",
            )
        )

    for item in parse_misiones_legislators():
        rows.append(
            make_row(
                prefix="prov-mis-leg", surname=item["surname"], given=item["given"],
                ambito="Provincial", poder="Legislativo", nivel="Legislaturas provinciales",
                cargo="Representante provincial", jurisdiccion="Misiones", alliance=item["block"],
                start="", end="", roster_url=MISIONES_LEGISLATORS_URL,
                roster_local="sources/subnational_roster/misiones_diputados_vigentes_2026-09-01.html",
                ddjj_regime="Régimen provincial · ruta documental por relevar",
                ddjj_state="ruta_provincial_por_relevar",
                ddjj_detail="No se localizó todavía un listado nominal institucional de presentaciones.",
                ddjj_url="", oa_index=oa_index,
                note="La nómina y el bloque provienen del período vigente publicado por la Cámara de Representantes de Misiones; el bloque de Carlos Rovira figura vacío en la fuente.",
            )
        )

    assert len(rows) == 789, f"El universo ampliado debía contener 789 cargos y contiene {len(rows)}"
    ids = [str(row["persona_id"]) for row in rows]
    assert len(ids) == len(set(ids)), "Hay identificadores duplicados"

    fieldnames = list(rows[0])
    output_csv = DERIVED / "active_politicians_roster_2026-09-01.csv"
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    by_level = Counter(str(row["nivel_cargo"]) for row in rows)
    by_status = Counter(str(row["estado_ddjj_cargo_actual"]) for row in rows)
    with_history = sum(row["oa_historial_2017_2024_estado"] == "nombre_compatible_unico_en_oa" for row in rows)
    ambiguous_history = sum(row["oa_historial_2017_2024_estado"] == "coincidencia_multiple_revisar_homonimia" for row in rows)
    with_series = sum(bool(row["serie_tab_id"]) for row in rows)
    provincial_indexed = Counter(
        str(row["jurisdiccion"])
        for row in rows
        if row["nivel_cargo"] == "Legislaturas provinciales"
    )
    provincial_coverage = []
    for jurisdiction, short_name, system, lower_or_single, senate, municipalities in PROVINCIAL_STRUCTURE:
        roster_url, nominal_state, ddjj_state = PROVINCIAL_NOMINAL_SOURCES.get(
            jurisdiction,
            ("", "pendiente de fuente nominal", "ruta provincial por relevar"),
        )
        seats = lower_or_single + senate
        provincial_coverage.append(
            {
                "jurisdiccion": jurisdiction,
                "jurisdiccion_corta": short_name,
                "tipo_legislatura": system,
                "bancas_diputados_o_unica": lower_or_single,
                "bancas_senado": senate,
                "bancas_total_ficha_dne": seats,
                "intendencias_ficha_dne": municipalities,
                "legisladores_nominales_incorporados": provincial_indexed[jurisdiction],
                "estado_nominal": nominal_state,
                "fuente_nominal_url": roster_url,
                "estado_ruta_ddjj": ddjj_state,
            }
        )
    assert len(provincial_coverage) == 24
    assert sum(item["bancas_total_ficha_dne"] for item in provincial_coverage) == 1199
    assert sum(item["intendencias_ficha_dne"] for item in provincial_coverage) == 1275
    assert sum(item["legisladores_nominales_incorporados"] for item in provincial_coverage) == 423

    provincial_output = DERIVED / "provincial_coverage_matrix_2026-09-01.csv"
    with provincial_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(provincial_coverage[0]))
        writer.writeheader()
        writer.writerows(provincial_coverage)

    payload = {
        "generated_at": "2026-09-01",
        "scope": {
            "title": "Capas 1–2 · Nación, gobernaciones y primera tanda legislativa subnacional",
            "included": "257 diputados nacionales, 72 senadores nacionales, 13 autoridades de conducción superior del PEN, 24 gobernadores/jefe de Gobierno y 423 legisladores de Buenos Aires, CABA, Córdoba, Misiones, Río Negro y Santa Fe.",
            "not_yet_included": "Las restantes legislaturas provinciales, 1.275 intendencias, concejos deliberantes, autoridades partidarias y el resto de secretarías/subsecretarías del PEN.",
            "reason": "No existe un padrón federal único ni un régimen uniforme de DDJJ. La ausencia se conserva como pendiente, nunca como patrimonio cero.",
            "next_layer_reference": "El texto introductorio DNE contabiliza 1.201 bancas provinciales, pero la suma de los 24 tamaños de cámara publicados en sus fichas da 1.199; se conserva la discrepancia. Estas tandas identifican 423 de esas 1.199 bancas y el informe contabiliza además 1.275 intendencias.",
        },
        "summary": {
            "cargos_activos": len(rows),
            "legisladores_provinciales_nominales": 423,
            "bancas_provinciales_suma_fichas_dne": 1199,
            "bancas_provinciales_total_intro_dne": 1201,
            "intendencias_total_dne": 1275,
            "personas_con_nombre_compatible_unico_oa_2017_2024": with_history,
            "coincidencias_oa_ambiguas": ambiguous_history,
            "personas_con_serie_curada_tab": with_series,
            "presentaciones_camara_localizadas": sum(str(row["estado_ddjj_cargo_actual"]).startswith("presentacion_") for row in rows),
            "por_nivel": dict(sorted(by_level.items())),
            "por_estado_ddjj_actual": dict(sorted(by_status.items())),
        },
        "provincial_coverage": provincial_coverage,
        "rows": rows,
    }
    output_json = DERIVED / "active_politicians_coverage_2026-09-01.json"
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"OK: padrón activo · {len(rows)} cargos · {with_history} coincidencias OA únicas · "
        f"{payload['summary']['presentaciones_camara_localizadas']} presentaciones de cámara localizadas"
    )


if __name__ == "__main__":
    main()
