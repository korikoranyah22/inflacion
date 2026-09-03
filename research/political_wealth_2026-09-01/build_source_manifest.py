from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "source_manifest.csv"

SOURCE_FILES = {
    "oa_consulta": "sources/oa/consultar_ddjj_2026-09-01.html",
    "oa_f1245": "sources/oa/preguntas_f1245_2026-09-01.html",
    "ley_26857": "sources/normativa/ley_26857.html",
    "ley_23966": "sources/normativa/ley_23966_actualizada.html",
    "datos_justicia": "sources/datos/dataset_ddjj_2026-09-01.html",
    "hcdn_maximo": "sources/politica/hcdn_maximo_2026-09-01.html",
    "indec_ipc_2023": "sources/indec/ipc_2023.pdf",
    "indec_ipc_series": "sources/indec/ipc_portal_2026-09-01.html",
    "indec_ipc_2025": "sources/indec/ipc_2025.pdf",
    "cronista_maximo_2025": "sources/descubrimiento/cronista_maximo_2025_2026-08-13.html",
    "lanacion_karina_2025": "sources/descubrimiento/lanacion_karina_2025_2026-09-01.html",
    "datos_justicia_ckan": "sources/datos_justicia/ckan_package_show_2026-09-01.json",
    "datos_justicia_modelo": "sources/datos_justicia/metadata_modelo_datos_2026-09-01.md",
    "datos_justicia_2012_2024": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
    "bcra_a3500_2017_2025": "sources/bcra/a3500_2017_2025_2026-09-01.json",
    "indec_ipc_csv": "sources/indec/serie_ipc_divisiones_2016_2026.csv",
    "fred_gs3m": "sources/benchmarks/fred_gs3m_2017_2025_2026-09-01.csv",
    "vanguard_vbiax": "sources/benchmarks/vanguard_vbiax_prospectus_2025_2026-09-01.pdf",
    "msci_acwi": "sources/benchmarks/msci_acwi_factsheet_usd_2026-07-31.pdf",
    "hcdn_roster_html_2026": "sources/active_roster/hcdn_diputados_vigentes_2026-09-01.html",
    "hcdn_roster_csv_2026": "sources/active_roster/hcdn_diputados_vigentes_2026-09-01.csv",
    "hcdn_ddjj_2025": "sources/active_roster/hcdn_ddjj_ejercicio_2025_2026-09-01.html",
    "hcdn_ddjj_2026": "sources/active_roster/hcdn_ddjj_ejercicio_2026_2026-09-01.html",
    "senado_roster_2026": "sources/active_roster/senado_listado_vigente_2026-09-01.html",
    "senado_ddjj_2025": "sources/active_roster/senado_ddjj_2025_2026-09-01.html",
    "cfi_gobernadores_2026": "sources/active_roster/cfi_gobernadores_2026-09-01.html",
    "dine_poder_provincial_2026": "sources/active_roster/dine_mapa_poder_provincial_julio_2026.pdf",
    "argentina_ministerios_2026": "sources/active_roster/argentina_ministerios_nacionales_2026-09-01.html",
    "oa_alcance_pen_2026": "sources/active_roster/oa_alcance_ddjj_pen_2026-09-01.html",
    "jgm_decreto_548_2026": "sources/active_roster/decreto_548_2026_jefe_gabinete.html",
    "interior_autoridades_2026": "sources/active_roster/vicejefatura_interior_autoridades_2026-09-01.html",
    "presidencia_autoridades_2026": "sources/active_roster/presidencia_autoridades_2026-09-01.html",
    "senado_presidencia_2026": "sources/active_roster/senado_presidencia_2026-09-01.html",
    "cancilleria_autoridad_2026": "sources/active_roster/cancilleria_autoridad_2026-09-01.html",
    "defensa_autoridades_2026": "sources/active_roster/defensa_autoridades_2026-09-01.html",
    "economia_autoridades_2026": "sources/active_roster/economia_autoridades_2026-09-01.html",
    "justicia_autoridades_2026": "sources/active_roster/justicia_autoridades_2026-09-01.html",
    "seguridad_autoridades_2026": "sources/active_roster/seguridad_autoridades_2026-09-01.html",
    "salud_autoridades_2026": "sources/active_roster/salud_autoridades_2026-09-01.html",
    "capital_humano_autoridades_2026": "sources/active_roster/capital_humano_autoridades_2026-09-01.html",
    "desregulacion_autoridad_2026": "sources/active_roster/desregulacion_autoridad_2026-09-01.html",
    "salud_ddjj_obligados_2026": "sources/active_roster/salud_ddjj_obligados_2026-09-01.html",
    "ba_diputados_vigentes_2026": "sources/subnational_roster/buenos_aires_diputados_vigentes_2026-09-01.html",
    "ba_senadores_vigentes_2026": "sources/subnational_roster/buenos_aires_senadores_vigentes_2026-09-01.html",
    "caba_legisladores_home_2026": "sources/subnational_roster/caba_legisladores_vigentes_2026-09-01.html",
    "caba_composicion_actual_2026": "sources/subnational_roster/caba_composicion_actual_2026-09-01.html",
    "caba_legisladores_xml_2026": "sources/subnational_roster/caba_legisladores_vigentes_2026-09-01.xml",
    "caba_ddjj_listado_2026": "sources/subnational_roster/caba_ddjj_listado_2026-09-01.html",
    "cordoba_composicion_portal_2026": "sources/subnational_roster/cordoba_composicion_portal_2026-09-01.html",
    "cordoba_legisladores_json_2026": "sources/subnational_roster/cordoba_legisladores_vigentes_2026-09-01.json",
    "cordoba_ddjj_2026": "sources/subnational_roster/cordoba_ddjj_2026-09-01.html",
    "santa_fe_diputados_p1_2026": "sources/subnational_roster/santa_fe_diputados_vigentes_2026-09-01.html",
    "santa_fe_diputados_p2_2026": "sources/subnational_roster/santa_fe_diputados_vigentes_p2_2026-09-01.html",
    "santa_fe_diputados_p3_2026": "sources/subnational_roster/santa_fe_diputados_vigentes_p3_2026-09-01.html",
    "santa_fe_diputados_p4_2026": "sources/subnational_roster/santa_fe_diputados_vigentes_p4_2026-09-01.html",
    "santa_fe_diputados_p5_2026": "sources/subnational_roster/santa_fe_diputados_vigentes_p5_2026-09-01.html",
    "santa_fe_senadores_2026": "sources/subnational_roster/santa_fe_senadores_vigentes_2026-09-01.html",
    "rio_negro_legisladores_snapshot_2026": "sources/subnational_roster/rio_negro_legisladores_vigentes_2026-09-01.csv",
    "rio_negro_acta_proclamacion_2023": "sources/subnational_roster/rio_negro_acta_proclamacion_2023.pdf",
    "misiones_diputados_2026": "sources/subnational_roster/misiones_diputados_vigentes_2026-09-01.html",
    "misiones_bloques_2026": "sources/subnational_roster/misiones_bloques_2026-09-01.html",
    "hcdn_opciones_viajes_2025": "sources/identity_crosswalk/hcdn_opciones_viajes_nacionales_2025.pdf",
    "senado_ba_roxana_alejandra_lopez_2026": "sources/identity_crosswalk/senado_ba_roxana_alejandra_lopez_2026.html",
    "santa_fe_marcelo_omar_gonzalez_2026": "sources/identity_crosswalk/santa_fe_marcelo_omar_gonzalez_2026.html",
    "santa_fe_sergio_javier_rojas_2024": "sources/identity_crosswalk/santa_fe_sergio_javier_rojas_2024.pdf",
    "caba_legislatura_laura_alonso_2026": "sources/identity_crosswalk/caba_legislatura_laura_alonso_2026.html",
    "jusbaires_laura_alonso_cv": "sources/identity_crosswalk/jusbaires_laura_alonso_cv.html",
    "decreto_252_2015_laura_alonso_oa": "sources/identity_crosswalk/decreto_252_2015_laura_alonso_oa.html",
    "san_luis_registro_candidatos_jorge_fernandez": "sources/identity_crosswalk/san_luis_registro_candidatos_jorge_fernandez.html",
    "santa_fe_educacion_marcelo_omar_gonzalez_2014": "sources/identity_crosswalk/santa_fe_educacion_marcelo_omar_gonzalez_2014.pdf",
    "misiones_candidatos_oficializados_2025": "sources/identity_crosswalk/misiones_candidatos_oficializados_2025.pdf",
    "hcdn_alvaro_garcia_profile_2026": "sources/identity_crosswalk/hcdn_alvaro_garcia_profile_2026.html",
    "boletin_oficial_alvaro_garcia_2023": "sources/identity_crosswalk/boletin_oficial_alvaro_garcia_2023.pdf",
    "ba_maria_laura_fernandez_profile_2026": "sources/identity_crosswalk/buenos_aires_maria_laura_fernandez_profile_2026.html",
    "ba_diputados_ddjj_2018": "sources/identity_crosswalk/buenos_aires_diputados_ddjj_2018.pdf",
    "decreto_586_2024_sturzenegger": "sources/identity_crosswalk/decreto_586_2024_sturzenegger.html",
    "decreto_6_2023_patricia_bullrich": "sources/identity_crosswalk/decreto_6_2023_patricia_bullrich.html",
    "decreto_225_2021_martin_soria": "sources/identity_crosswalk/decreto_225_2021_martin_soria.html",
    "decreto_380_2024_adriana_serquis": "sources/identity_crosswalk/decreto_380_2024_adriana_serquis.html",
    "decreto_145_2024_sebastian_pareja": "sources/identity_crosswalk/decreto_145_2024_sebastian_pareja.html",
    "oa_f1245_manual_2025": "sources/oa/instructivo_f1245_2025_2026-09-02.pdf",
    "arca_valuaciones_2025": "sources/arca/valuaciones_bienes_personales_2025_2026-09-02.html",
    "cronista_karina_revaluacion_2025": "sources/descubrimiento/cronista_karina_revaluacion_2025_2026-09-02.html",
    "lanacion_milei_karina_2025": "sources/descubrimiento/lanacion_milei_karina_2025_2026-09-02.html",
    "oa_javier_milei_ddjj_2024_mirror": "sources/oa/javier_milei_ddjj_anual_2024_copia_espejo_2026-09-02.pdf",
    "oa_javier_milei_ddjj_2023_mirror": "sources/oa/javier_milei_ddjj_anual_2023_copia_espejo_2026-09-02.pdf",
    "hcdn_ddjj_2024": "sources/active_roster/hcdn_ddjj_ejercicio_2024_2026-09-03.html",
    "decreto_127_1996_nuda_propiedad": "sources/legal/decreto_127_1996_bienes_personales_usufructo_2026-09-03.html",
}

RETRIEVED_AT = {
    "oa_f1245_manual_2025": "2026-09-02",
    "arca_valuaciones_2025": "2026-09-02",
    "cronista_karina_revaluacion_2025": "2026-09-02",
    "lanacion_milei_karina_2025": "2026-09-02",
    "oa_javier_milei_ddjj_2024_mirror": "2026-09-02",
    "oa_javier_milei_ddjj_2023_mirror": "2026-09-02",
    "hcdn_ddjj_2024": "2026-09-03",
    "decreto_127_1996_nuda_propiedad": "2026-09-03",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


with (ROOT / "source_registry.csv").open(encoding="utf-8", newline="") as handle:
    registry = {row["id"]: row for row in csv.DictReader(handle)}

assert set(SOURCE_FILES) == set(registry), "El registro y el mapa de copias no coinciden"

rows = []
for source_id, relative in SOURCE_FILES.items():
    path = ROOT / relative
    assert path.is_file(), f"Falta copia local: {relative}"
    rows.append(
        {
            "id": source_id,
            "local_path": relative,
            "url": registry[source_id]["url"],
            "retrieved_at": RETRIEVED_AT.get(source_id, "2026-09-01"),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "tipo": registry[source_id]["tipo"],
        }
    )

with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"OK: {len(rows)} fuentes respaldadas y verificables")
