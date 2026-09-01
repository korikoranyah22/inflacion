from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"

EXACT_URLS = {
    "bcra_reservas/ipom_2025_t4.pdf": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/informe-politica-monetaria-2025-T4.pdf",
    "bcra_reservas/planilla_reservas_liquidez_2026-07-31.pdf": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/temp0726.pdf",
    "bcra_reservas/estado_resumido_2026-08-23.pdf": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/estado-resumido-activos-pasivos-bcra.pdf",
    "bcra_reservas/estado_resumido_aclaraciones.pdf": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/aclaraciones-estado-resumido-activos-pasivos-bcra.pdf",
    "bcra_reservas/nedd_reservas_2026-08-31.html": "https://www.bcra.gob.ar/normas-especiales-para-la-divulgacion-de-datos-fmi/",
    "bcra_reservas/swap_china_renovacion_2026-08-05.html": "https://www.bcra.gob.ar/noticias/el-banco-central-de-la-republica-argentina-y-el-banco-de-la-republica-popular-de-china-renuevan-su-acuerdo-de-swap-y-extienden-el-plazo-de-3-a-5-anos/",
    "bcra_reservas/reservas_internacionales_2026-08-27.pdf": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/reservas1.pdf",
    "bcra_reservas/imf_argentina_staff_report_2026_105_main.pdf": "https://www.elibrary.imf.org/downloadpdf/view/journals/002/2026/105/article-A001-en.pdf",
    "bcra_reservas/imf_argentina_staff_report_2026_105_supplement.pdf": "https://www.elibrary.imf.org/downloadpdf/view/journals/002/2026/105/article-A003-en.pdf",
    "deuda/datos_mensuales_2026-08-31.html": "https://www.argentina.gob.ar/economia/finanzas/datos-mensuales",
    "deuda/boletin_mensual_deuda_2026-07-31.xlsx": "https://www.argentina.gob.ar/sites/default/files/boletin_mensual_31_07_2026_0.xlsx",
    "deuda/datos_trimestrales_2026-08-31.html": "https://www.argentina.gob.ar/economia/finanzas/datos-trimestrales-de-la-deuda",
    "deuda/deuda_publica_2026-03-31.xlsx": "https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-03-2026.xlsx",
    "deuda/presentacion_grafica_2026_q1.pdf": "https://www.argentina.gob.ar/sites/default/files/presentacion_grafica_it_26_c.pdf",
    "deuda/base_sigade_2026-03-31.zip": "https://www.argentina.gob.ar/sites/default/files/base_sigade_31-03-2026.zip",
    "rigi/rigi_portal_2026-08-31.html": "https://www.argentina.gob.ar/economia/rigi",
    "rigi/rigi_dataset_2026-08-31.csv": "https://docs.google.com/spreadsheets/d/1eytHJrzUjIFOXI-P1Hx_wbmZiSqPxVle059Djdos6u8/gviz/tq?tqx=out:csv&sheet=dataset",
    "rigi/rigi_evaluacion_2026-08-31.csv": "https://docs.google.com/spreadsheets/d/1eytHJrzUjIFOXI-P1Hx_wbmZiSqPxVle059Djdos6u8/gviz/tq?tqx=out:csv&sheet=evaluacion",
    "sector_externo/indec_sector_externo_2026-08-31.html": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-35-45",
    "cuentas_sectoriales/indec_cuentas_sectoriales_2026-08-31.html": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-9-118",
    "capital_publico/cuenta_inversion_2024_resumen.pdf": "https://www.argentina.gob.ar/sites/default/files/libro_resumen_cdi_2024_5a-definitivo.pdf",
    "capital_publico/fbcf_gobierno_general_2024.pdf": "https://www.indec.gob.ar/uploads/informesdeprensa/formacion_capital_fijo_12_258E2CD715D3.pdf",
    "cuentas_sectoriales/gobierno_general_2024.pdf": "https://www.indec.gob.ar/uploads/informesdeprensa/cuentas_sectores_institucionales_12_25FAE281E126.pdf",
    "cuentas_sectoriales/sociedades_financieras_2024.pdf": "https://www.indec.gob.ar/uploads/informesdeprensa/cuentas_sociedades_financieras_12_254091CDBBA3.pdf",
    "cuentas_sectoriales/resto_del_mundo_2024.pdf": "https://www.indec.gob.ar/uploads/informesdeprensa/cuentas_resto_del_mundo_12_25376CBDB29E.pdf",
    "indec_eph/dosier_estrategias_manutencion_2025.pdf": "https://www.indec.gob.ar/ftp/cuadros/publicaciones/dosier_estrategias_manutencion_2025.pdf",
    "indec_eph/EPH_registro_2T2025.pdf": "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_registro_2T2025.pdf",
    "indec_eph/EPH_registro_1T2026.pdf": "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_registro_1T2026.pdf",
    "indec_eph/EPH_nota_metodologica_1_trim_2019.pdf": "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_nota_metodologica_1_trim_2019.pdf",
    "indec_eph/EPHContinua_CHogar.pdf": "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPHContinua_CHogar.pdf",
    "indec_eph/indec_bases_de_datos_2026-08-31.html": "https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos",
}

RETRIEVAL_DATES = {
    "bcra_reservas/reservas_internacionales_2026-08-27.pdf": "2026-09-01",
    "bcra_reservas/imf_argentina_staff_report_2026_105_main.pdf": "2026-09-01",
    "bcra_reservas/imf_argentina_staff_report_2026_105_supplement.pdf": "2026-09-01",
}


def source_url(relative: str) -> str:
    if relative in EXACT_URLS:
        return EXACT_URLS[relative]
    name = Path(relative).name
    if relative.startswith("rigi/resoluciones_html/norma-"):
        return f"https://www.argentina.gob.ar/normativa/nacional/{name.removesuffix('.html')}"
    if relative.startswith("indec_eph/EPH_usu_"):
        return f"https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/{name}"
    if relative.startswith("indec_eph/"):
        return "https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos"
    return "URL_documentada_en_archivo_padre"


rows = []
for file in sorted(path for path in SOURCES.rglob("*") if path.is_file()):
    relative = file.relative_to(SOURCES).as_posix()
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    rows.append(
        {
            "ruta_relativa": relative,
            "url_origen": source_url(relative),
            "fecha_recuperacion": RETRIEVAL_DATES.get(relative, "2026-08-31"),
            "bytes": file.stat().st_size,
            "sha256": digest,
        }
    )

with (ROOT / "source_manifest.csv").open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print(f"OK: {len(rows)} archivos respaldados y hasheados")
