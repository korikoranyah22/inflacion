from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
DERIVED = ROOT / "derived"
REGISTRY = ROOT / "source_registry.csv"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> None:
    with REGISTRY.open(encoding="utf-8-sig", newline="") as handle:
        registry = list(csv.DictReader(handle))
    rows: list[dict[str, object]] = []
    for row in registry:
        path = SOURCES / row["ruta_relativa"]
        assert path.is_file(), f"Falta fuente respaldada: {path}"
        rows.append(
            {
                **row,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    write_csv(
        ROOT / "source_manifest.csv",
        ["ruta_relativa", "url_origen", "fecha_recuperacion", "bytes", "sha256"],
        rows,
    )


def latest_bcra_usd_rates() -> list[dict[str, object]]:
    wanted = {
        "1214": "Caja de ahorro en dólares",
        "1215": "Plazo fijo en dólares · total",
        "1216": "Plazo fijo en dólares · 30 a 59 días",
        "1217": "Plazo fijo en dólares · 30 días",
        "1218": "Plazo fijo en dólares · 60 días o más",
    }
    latest: dict[str, tuple[datetime, float]] = {}
    archive_path = SOURCES / "bcra_tasas_depositos_series.zip"
    with zipfile.ZipFile(archive_path) as archive:
        entry = archive.namelist()[0]
        with archive.open(entry) as raw, io.TextIOWrapper(raw, encoding="latin-1") as text:
            for row in csv.reader(text, delimiter=";"):
                if len(row) != 3 or row[0] not in wanted:
                    continue
                date = datetime.strptime(row[1], "%d/%m/%Y")
                value = float(row[2].replace(",", "."))
                if row[0] not in latest or date > latest[row[0]][0]:
                    latest[row[0]] = (date, value)
    assert set(latest) == set(wanted)
    expected = {"1214": 0.22, "1215": 1.34, "1216": 1.19, "1217": 1.21, "1218": 2.05}
    rows: list[dict[str, object]] = []
    for series_id, label in wanted.items():
        date, value = latest[series_id]
        assert date.date().isoformat() == "2026-08-27"
        assert abs(value - expected[series_id]) < 0.0001
        rows.append(
            {
                "serie_id": series_id,
                "instrumento": label,
                "fecha": date.date().isoformat(),
                "tna_pct": f"{value:.2f}",
                "fuente": "BCRA · tas1_ser.txt (copia completa comprimida)",
            }
        )
    return rows


def build_income_distribution() -> None:
    shares = [1.8, 3.2, 4.2, 5.3, 6.3, 7.6, 9.3, 12.1, 16.6, 33.5]
    assert abs(sum(shares) - 99.9) < 0.001  # redondeo publicado por INDEC
    assert abs(sum(shares[:4]) - 14.5) < 0.001
    assert abs(sum(shares[-2:]) - 50.1) < 0.001
    cumulative = 0.0
    rows = []
    for decile, share in enumerate(shares, start=1):
        cumulative += share
        rows.append(
            {
                "decil": decile,
                "participacion_ingreso_pct": f"{share:.1f}",
                "acumulado_pct": f"{cumulative:.1f}",
                "nota": "Ingreso corriente individual; no mide patrimonio ni tenencia de dólares",
                "fuente": "INDEC · Distribución del ingreso, 2026-T1",
            }
        )
    write_csv(
        DERIVED / "income_distribution_2026_q1.csv",
        ["decil", "participacion_ingreso_pct", "acumulado_pct", "nota", "fuente"],
        rows,
    )


def build_headlines() -> None:
    rows = [
        {"indicador": "Ingreso del 20% superior", "valor": 50.1, "unidad": "% del ingreso corriente", "calidad": "medición oficial", "fuente": "INDEC ingresos 2026-T1", "advertencia": "No mide riqueza"},
        {"indicador": "Ingreso del 40% inferior", "valor": 14.5, "unidad": "% del ingreso corriente", "calidad": "medición oficial", "fuente": "INDEC ingresos 2026-T1", "advertencia": "No mide riqueza"},
        {"indicador": "Hogares con alguna estrategia extraordinaria", "valor": 71.778, "unidad": "% de hogares", "calidad": "estimación EPH auditada", "fuente": "EPH 2026-T1", "advertencia": "No equivale a falta de ahorro"},
        {"indicador": "Proxy hogares sólo con recursos corrientes", "valor": 24.534, "unidad": "% de hogares", "calidad": "proxy EPH", "fuente": "EPH 2026-T1", "advertencia": "No es una medición de excedente invertible"},
        {"indicador": "Depósitos privados en dólares", "valor": 40.3, "unidad": "USD miles de millones", "calidad": "dato oficial comunicado", "fuente": "Ministerio de Economía 2026-08-13", "advertencia": "Stock bancario"},
        {"indicador": "Préstamos privados en dólares", "valor": 24.6, "unidad": "USD miles de millones", "calidad": "dato oficial comunicado", "fuente": "Ministerio de Economía 2026-08-13", "advertencia": "Crédito vigente"},
        {"indicador": "Capacidad crediticia adicional al ratio teórico de 75%", "valor": 5.8, "unidad": "USD miles de millones", "calidad": "cálculo oficial aproximado", "fuente": "Ministerio de Economía 2026-08-13", "advertencia": "Capacidad no usada; no implica demanda solvente"},
        {"indicador": "Moneda y depósitos de otros sectores en el exterior", "valor": 259.305, "unidad": "USD miles de millones", "calidad": "estadística oficial agregada", "fuente": "INDEC PII 2026-T1", "advertencia": "Incluye hogares, empresas e ISFLSH; no es sólo colchón"},
    ]
    write_csv(DERIVED / "headline_indicators.csv", ["indicador", "valor", "unidad", "calidad", "fuente", "advertencia"], rows)


def build_channel_comparison(rates: list[dict[str, object]]) -> None:
    rate_by_id = {row["serie_id"]: float(row["tna_pct"]) for row in rates}
    rows = [
        {"canal": "Efectivo físico", "tasa_anual_referencia_pct": 0.0, "fecha_tasa": "no aplica", "ganancia_bruta_usd_sobre_10000": 0, "ventaja_privada": "Liquidez física y fuera de intermediarios", "costo_o_riesgo": "Robo, pérdida, sin rendimiento", "efecto_local_directo": "Ninguno mientras permanezca inmóvil"},
        {"canal": "Caja de ahorro bancaria en USD", "tasa_anual_referencia_pct": rate_by_id["1214"], "fecha_tasa": "2026-08-27", "ganancia_bruta_usd_sobre_10000": round(10000 * rate_by_id["1214"] / 100, 2), "ventaja_privada": "Pagos locales, simplicidad y garantía hasta el límite aplicable", "costo_o_riesgo": "Rendimiento bajo; cobertura limitada en pesos equivalentes", "efecto_local_directo": "Fondea al banco; el crédito posterior no es automático"},
        {"canal": "Plazo fijo bancario USD · 60 días o más", "tasa_anual_referencia_pct": rate_by_id["1218"], "fecha_tasa": "2026-08-27", "ganancia_bruta_usd_sobre_10000": round(10000 * rate_by_id["1218"] / 100, 2), "ventaja_privada": "Mayor tasa bancaria y operatoria local", "costo_o_riesgo": "Inmovilización; tasa nominal simple de referencia", "efecto_local_directo": "Fondea al banco; puede ampliar crédito en USD"},
        {"canal": "Letra del Tesoro de EE.UU. a 52 semanas", "tasa_anual_referencia_pct": 4.14, "fecha_tasa": "2026-08-28", "ganancia_bruta_usd_sobre_10000": 414.00, "ventaja_privada": "Activo soberano externo de alta liquidez y bajo riesgo crediticio", "costo_o_riesgo": "Comisiones, impuestos, custodia, acceso y riesgo de precio si se vende antes", "efecto_local_directo": "No fondea crédito bancario argentino"},
    ]
    write_csv(
        DERIVED / "channel_comparison.csv",
        ["canal", "tasa_anual_referencia_pct", "fecha_tasa", "ganancia_bruta_usd_sobre_10000", "ventaja_privada", "costo_o_riesgo", "efecto_local_directo"],
        rows,
    )


def build_claims_audit() -> None:
    rows = [
        {"pregunta": "¿La frase fue localizada textualmente?", "clasificacion": "no localizada", "veredicto": "Se conserva como paráfrasis; el argumento oficial equivalente sí fue localizado.", "fuente_principal": "Ministerio de Economía 2026-08-13"},
        {"pregunta": "¿Quién tiene margen para invertir?", "clasificacion": "indicio fuerte, no medición directa", "veredicto": "La capacidad está concentrada: el 20% superior capta 50,1% del ingreso; ingreso no equivale a patrimonio.", "fuente_principal": "INDEC ingresos 2026-T1"},
        {"pregunta": "¿Depositar equivale a inversión productiva?", "clasificacion": "falso como automatismo", "veredicto": "El depósito sólo crea fondeo potencial; requiere banco dispuesto, empresa elegible, demanda solvente y uso productivo.", "fuente_principal": "BCRA y Ministerio de Economía 2026-08-13"},
        {"pregunta": "¿El banco ofrece el mejor incentivo privado?", "clasificacion": "no demostrado", "veredicto": "Las tasas bancarias USD observadas quedan por debajo de una letra del Tesoro estadounidense a 52 semanas antes de costos e impuestos.", "fuente_principal": "BCRA 2026-08-27 y US Treasury 2026-08-28"},
        {"pregunta": "¿Cuál es el beneficio buscado por el Gobierno?", "clasificacion": "probado", "veredicto": "Formalización, más crédito, actividad, empleo y recaudación asociada al crecimiento.", "fuente_principal": "Ministerio de Economía 2026-07-22 y 2026-08-13"},
        {"pregunta": "¿La urgencia se explica sólo por falta de depósitos?", "clasificacion": "contrapunto", "veredicto": "No: la propia presentación estima USD 5,8 mil millones de capacidad crediticia ya disponible.", "fuente_principal": "Ministerio de Economía 2026-08-13"},
        {"pregunta": "¿Busca rescatar bancos o financiar deuda soberana?", "clasificacion": "no demostrado", "veredicto": "Las fuentes revisadas no prueban ese propósito; además limitan la tenencia de deuda pública respecto del crédito en USD.", "fuente_principal": "Ministerio de Economía 2026-08-13"},
        {"pregunta": "¿Está desesperado?", "clasificacion": "no observable", "veredicto": "No se infiere un estado mental. Se analizan objetivos, restricciones e incentivos observables.", "fuente_principal": "criterio metodológico"},
    ]
    write_csv(DERIVED / "policy_claims_audit.csv", ["pregunta", "clasificacion", "veredicto", "fuente_principal"], rows)


def build_results_markdown() -> None:
    text = """# Resultados · auditoría “dólares del colchón”

Fecha de corte: **31/08/2026**.

## Veredicto corto

La frase suministrada se trata como **paráfrasis**: no fue localizada literalmente en las transcripciones oficiales revisadas. El argumento oficial equivalente sí es inequívoco: Caputo propone que los dólares fuera del sistema entren a los bancos para ampliar el crédito empresarial y, por esa vía, la actividad y el empleo.

Ese beneficio macroeconómico no coincide necesariamente con el incentivo privado del ahorrista. Al 27/08/2026, las referencias del BCRA eran 0,22% TNA para caja de ahorro USD y 2,05% para plazos de 60 días o más; la letra del Tesoro estadounidense a 52 semanas rendía 4,14% el 28/08/2026. La comparación es ilustrativa: antes de elegir hay que descontar comisiones, impuestos, custodia, liquidez, acceso y riesgo de precio.

## Quiénes pueden invertir

INDEC muestra que el 20% de mayores ingresos concentra 50,1% del ingreso corriente y el 40% inferior, 14,5%. Esto respalda la idea de una capacidad concentrada, pero no identifica quién posee dólares: la EPH mide ingresos, no riqueza ni efectivo atesorado. Como contexto, 71,778% de los hogares usó al menos una estrategia extraordinaria de sostenimiento en 2026-T1; tampoco es una medición directa de falta de ahorro.

## Por qué el Gobierno quiere el canal bancario

La cadena pretendida es: depósito USD → fondeo bancario → crédito a una empresa → liquidación del préstamo en el mercado de cambios → fondos en pesos/FX adicional → eventual inversión, empleo y recaudación. Cada flecha es contingente. Depositar no convierte automáticamente el dinero en reservas del BCRA ni en capital productivo.

La urgencia no puede atribuirse a un estado psicológico. Las presiones observables son formalizar activos, profundizar el crédito y conseguir crecimiento sin expandir el gasto o la emisión. Hay un contrapunto importante: la propia presentación oficial calcula que ya existían unos USD 5,8 mil millones de capacidad crediticia sin usar. Por eso, una escasez inmediata de depósitos no explica por sí sola el impulso político.

## Precauciones

- La PII registra USD 259,305 mil millones de moneda y depósitos de “otros sectores”, pero mezcla hogares, empresas e ISFLSH: no es una medición del “colchón” de las familias.
- La garantía de depósitos rige hasta ARS 50 millones por persona/entidad desde el 01/04/2026; los depósitos en moneda extranjera se convierten al tipo de referencia aplicable.
- No se encontró evidencia suficiente para afirmar que el objetivo central sea rescatar bancos o financiar deuda soberana.
- El módulo es análisis económico y de incentivos, no recomendación financiera individual.
"""
    (ROOT / "CAPUTO_COLCHON_RESULTS.md").write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    build_manifest()
    rates = latest_bcra_usd_rates()
    write_csv(DERIVED / "bank_usd_rates_latest.csv", ["serie_id", "instrumento", "fecha", "tna_pct", "fuente"], rates)
    build_income_distribution()
    build_headlines()
    build_channel_comparison(rates)
    build_claims_audit()
    build_results_markdown()
    print("OK: manifiesto, cinco datasets derivados y memo de resultados generados")


if __name__ == "__main__":
    main()
