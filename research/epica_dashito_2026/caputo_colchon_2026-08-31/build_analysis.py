from __future__ import annotations

import csv
import hashlib
import io
import json
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
        {"indicador": "Préstamos / depósitos privados en dólares", "valor": 61, "unidad": "%", "calidad": "ratio oficial comunicado", "fuente": "Ministerio de Economía 2026-08-13", "advertencia": "Cercano al 65% histórico prudente; por debajo del 75% regulatorio"},
        {"indicador": "Margen aproximado hasta referencia prudente de 65%", "valor": 1.595, "unidad": "USD miles de millones", "calidad": "cálculo derivado con stocks redondeados", "fuente": "Ministerio de Economía 2026-08-13", "advertencia": "No equivale a crédito demandado o aprobado"},
        {"indicador": "Capacidad crediticia adicional al ratio teórico de 75%", "valor": 5.8, "unidad": "USD miles de millones", "calidad": "cálculo oficial aproximado", "fuente": "Ministerio de Economía 2026-08-13", "advertencia": "Capacidad no usada; no implica demanda solvente"},
        {"indicador": "Crédito USD en producción primaria e industria", "valor": 73.7214, "unidad": "% del stock por actividad", "calidad": "cálculo sobre planilla oficial", "fuente": "BCRA act2026.xls · 2026-T2", "advertencia": "Actividad principal del deudor; no destino final"},
        {"indicador": "Nuevas operaciones USD a otras personas jurídicas", "valor": 74.5857, "unidad": "% del flujo bruto mensual", "calidad": "cálculo sobre planilla oficial", "fuente": "BCRA preser_mon.xls · 2026-07", "advertencia": "Categoría complementaria a PyMEs; no identifica grandes empresas una a una"},
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


def build_questions_matrix() -> None:
    rows = [
        {"dimension": "origen del análisis", "pregunta": "¿Qué formulación oficial se localizó?", "tipo_de_evidencia": "fuente oficial", "lectura_actual": "La redacción entregada se conserva como paráfrasis; sí se localizó el argumento depósitos → crédito → actividad y empleo.", "limite_o_pregunta_abierta": "No se atribuye literalidad a la paráfrasis.", "fuente_principal": "Ministerio de Economía 2026-08-13"},
        {"dimension": "distribución", "pregunta": "¿Cómo se distribuye la capacidad potencial de ahorro?", "tipo_de_evidencia": "medición indirecta", "lectura_actual": "El 20% superior capta 50,1% del ingreso corriente, lo que muestra una capacidad potencial concentrada.", "limite_o_pregunta_abierta": "Ingreso corriente no equivale a patrimonio ni identifica tenencias de dólares.", "fuente_principal": "INDEC ingresos 2026-T1"},
        {"dimension": "transmisión", "pregunta": "¿Qué pasos separan el depósito de la inversión productiva?", "tipo_de_evidencia": "mecanismo regulatorio", "lectura_actual": "El depósito crea fondeo potencial; la transmisión también requiere un banco dispuesto, una empresa elegible, demanda solvente y uso productivo.", "limite_o_pregunta_abierta": "La evidencia disponible no mide la probabilidad de cada paso.", "fuente_principal": "BCRA y Ministerio de Economía 2026-08-13"},
        {"dimension": "canales", "pregunta": "¿Qué atributos ofrece cada alternativa de inversión?", "tipo_de_evidencia": "comparación de referencia", "lectura_actual": "Las tasas bancarias USD observadas son menores que la letra del Tesoro estadounidense a 52 semanas; el banco aporta funciones transaccionales y la comitente acceso a activos.", "limite_o_pregunta_abierta": "La elección depende además de comisiones, impuestos, custodia, liquidez, acceso y riesgo de precio.", "fuente_principal": "BCRA 2026-08-27 y US Treasury 2026-08-28"},
        {"dimension": "política pública", "pregunta": "¿Qué objetivos y mecanismos declara el Gobierno?", "tipo_de_evidencia": "declaración oficial", "lectura_actual": "Las fuentes mencionan formalización, más crédito, actividad, empleo y recaudación asociada al crecimiento.", "limite_o_pregunta_abierta": "Las declaraciones no permiten establecer el peso relativo de cada objetivo.", "fuente_principal": "Ministerio de Economía 2026-07-22 y 2026-08-13"},
        {"dimension": "capacidad bancaria", "pregunta": "¿Qué otros límites pueden intervenir además de los depósitos?", "tipo_de_evidencia": "estimación oficial y cálculo derivado", "lectura_actual": "El ratio préstamos/depósitos era 61%. El margen es cercano a USD 1,6 mil millones hasta la referencia prudente de 65% y a USD 5,8 mil millones hasta el máximo regulatorio de 75%.", "limite_o_pregunta_abierta": "La capacidad depende del techo elegido y no mide demanda, aprobación, riesgo ni uso efectivo.", "fuente_principal": "Ministerio de Economía 2026-08-13"},
        {"dimension": "actividad del deudor", "pregunta": "¿Qué actividades concentraban el crédito en dólares antes de la medida?", "tipo_de_evidencia": "stock oficial por actividad", "lectura_actual": "Producción primaria e industria manufacturera reunían 73,72% del stock en moneda extranjera a junio de 2026.", "limite_o_pregunta_abierta": "La actividad principal del deudor no identifica el uso del préstamo y el corte antecede al anuncio del 13 de agosto.", "fuente_principal": "BCRA act2026.xls"},
        {"dimension": "tipo de prestatario", "pregunta": "¿Qué prestatarios concentraron las nuevas operaciones en dólares?", "tipo_de_evidencia": "flujo bruto mensual oficial", "lectura_actual": "En julio, otras personas jurídicas reunieron 74,59% del flujo de préstamos de efectivo y 77,72% de los documentos a sola firma; las PyMEs, 20,83% y 18,22%, respectivamente.", "limite_o_pregunta_abierta": "Son operaciones brutas, no stock ni prestatarios únicos; la categoría 'otras' no equivale exactamente a grandes empresas.", "fuente_principal": "BCRA preser_mon.xls"},
        {"dimension": "plazo y uso", "pregunta": "¿El crédito observado puede identificarse como inversión de largo plazo?", "tipo_de_evidencia": "plazo y tramo de operaciones", "lectura_actual": "Los documentos de otras personas jurídicas tuvieron un plazo promedio de 150 días y 53,49% se concertó por debajo de 90 días; su tramo promedio ponderado fue USD 5–10 millones.", "limite_o_pregunta_abierta": "El plazo es compatible con financiamiento corporativo de corto plazo, pero no distingue capital de trabajo, refinanciación, comercio exterior o inversión.", "fuente_principal": "BCRA preser_pla.xls, preser_tra.xls y preser_mon.xls"},
        {"dimension": "demanda empresarial", "pregunta": "¿El fondeo parece ser la única restricción?", "tipo_de_evidencia": "encuesta de bancos", "lectura_actual": "En 2026-T2 los bancos percibieron una caída más intensa de la demanda PyME (ID -29,7%) y esperaban estándares más restrictivos para ese segmento en 2026-T3 (ID -24,9%).", "limite_o_pregunta_abierta": "La encuesta cubre crédito empresario general y no es una contabilidad específica de préstamos en dólares.", "fuente_principal": "BCRA ECC 2026-T2"},
        {"dimension": "elección observada", "pregunta": "¿Qué hicieron efectivamente las personas con los dólares comprados?", "tipo_de_evidencia": "estimación oficial de flujos", "lectura_actual": "Para julio, el BCRA estimó unos USD 1.000 millones en bancos locales y otros USD 1.000 millones como aumento de activos externos.", "limite_o_pregunta_abierta": "Es una estimación mensual sobre un subconjunto de compras, no una distribución del stock de riqueza.", "fuente_principal": "BCRA Balance Cambiario 2026-07"},
        {"dimension": "regulación prudencial", "pregunta": "¿Qué límites acompañan la ampliación del crédito en dólares?", "tipo_de_evidencia": "mecanismo regulatorio", "lectura_actual": "El nuevo universo de deudores tiene un tope agregado de 15% de los depósitos USD por banco, exigencia de capital de 125%, cómputo de exposición a 1,25 veces y pruebas de estrés cambiario.", "limite_o_pregunta_abierta": "Falta observar cuánto de ese cupo se utiliza y con qué desempeño.", "fuente_principal": "BCRA 2026-08-13"},
        {"dimension": "observación posterior", "pregunta": "¿Qué movimiento agregado se observa desde la emisión de la Comunicación A 8467?", "tipo_de_evidencia": "stocks diarios oficiales", "lectura_actual": "Entre el 18 y el 27 de agosto, los depósitos privados USD aumentaron USD 188 millones y los préstamos privados USD, USD 150 millones; el ratio pasó de 62,03% a 62,11%.", "limite_o_pregunta_abierta": "La serie agregada no identifica origen de los depósitos, prestatarios del cupo ni causalidad.", "fuente_principal": "BCRA API monetaria al 2026-08-27"},
        {"dimension": "trazabilidad del cupo", "pregunta": "¿La publicación permite identificar las financiaciones otorgadas bajo el nuevo cupo?", "tipo_de_evidencia": "auditoría de publicación", "lectura_actual": "La A 8467 define como elegibles a otras personas jurídicas fuera de los destinos antes admitidos, pero no introduce un identificador público específico para seguir esas operaciones.", "limite_o_pregunta_abierta": "Las aperturas disponibles no cruzan cupo, prestatario, moneda, plazo, mora y uso final.", "fuente_principal": "BCRA Comunicación A 8467, 2026-08-18"},
        {"dimension": "otros objetivos", "pregunta": "¿Qué lugar ocupan los bancos y la deuda soberana en las fuentes revisadas?", "tipo_de_evidencia": "delimitación de alcance", "lectura_actual": "No aparecen como objetivo central en el corpus revisado; la regulación citada limita ciertas tenencias de deuda pública respecto del crédito en USD.", "limite_o_pregunta_abierta": "Esto no prueba su ausencia en el conjunto más amplio de la política económica.", "fuente_principal": "Ministerio de Economía 2026-08-13"},
        {"dimension": "motivaciones personales", "pregunta": "¿Qué puede decirse sobre las motivaciones personales del ministro?", "tipo_de_evidencia": "fuera del alcance", "lectura_actual": "El análisis se concentra en objetivos declarados, restricciones, incentivos y mecanismos observables.", "limite_o_pregunta_abierta": "Las fuentes utilizadas no permiten inferir estados psicológicos.", "fuente_principal": "criterio metodológico"},
    ]
    write_csv(
        DERIVED / "policy_questions_matrix.csv",
        ["dimension", "pregunta", "tipo_de_evidencia", "lectura_actual", "limite_o_pregunta_abierta", "fuente_principal"],
        rows,
    )


def build_channel_break_even() -> None:
    rows = []
    for incremental_cost in (0, 0.5, 1, 1.5, 2, 2.09, 2.5, 3):
        external_net = 4.14 - incremental_cost
        gap = external_net - 2.05
        rows.append(
            {
                "costo_incremental_anual_comitente_pct_escenario": incremental_cost,
                "tasa_tbill_bruta_pct": 4.14,
                "tasa_plazo_fijo_usd_pct": 2.05,
                "tasa_externa_neta_de_costo_escenario_pct": round(external_net, 2),
                "brecha_vs_plazo_fijo_pct": round(gap, 2),
                "lectura": "referencia externa mayor" if gap > 0 else "punto de equilibrio" if gap == 0 else "plazo fijo mayor",
                "alcance": "escenario de costo incremental; no estima comisión ni impuesto individual",
            }
        )
    write_csv(
        DERIVED / "channel_break_even_scenarios.csv",
        ["costo_incremental_anual_comitente_pct_escenario", "tasa_tbill_bruta_pct", "tasa_plazo_fijo_usd_pct", "tasa_externa_neta_de_costo_escenario_pct", "brecha_vs_plazo_fijo_pct", "lectura", "alcance"],
        rows,
    )


def build_bank_transmission_map() -> None:
    rows = [
        {"orden": 1, "etapa": "ahorro fuera o dentro del sistema", "evidencia_disponible": "La política busca formalizar ahorros; la PII no separa efectivo de hogares.", "estado": "parcial", "pregunta_abierta": "¿Quién posee los dólares y en qué forma?", "fuente_principal": "Economía 2025-05-22 e INDEC PII 2026-Q1"},
        {"orden": 2, "etapa": "depósito bancario en USD", "evidencia_disponible": "La presentación informa alrededor de USD 40.300 M de depósitos privados.", "estado": "observado en fuente oficial", "pregunta_abierta": "¿Qué parte es nueva y qué parte ya estaba bancarizada?", "fuente_principal": "Economía 2026-08-13"},
        {"orden": 3, "etapa": "capacidad de prestar", "evidencia_disponible": "Con un ratio de 61%, el margen aproximado es USD 1.595 M hasta la referencia prudente de 65%; la estimación oficial informa USD 5.800 M hasta el máximo regulatorio de 75%.", "estado": "estimación oficial y cálculo derivado", "pregunta_abierta": "¿Qué techo describe mejor la capacidad económicamente utilizable?", "fuente_principal": "Economía 2026-08-13"},
        {"orden": 4, "etapa": "decisión bancaria", "evidencia_disponible": "El marco prudencial limita el nuevo universo de deudores al 15% de los depósitos USD por banco y eleva capital, exposición y pruebas de estrés. Antes de la medida, producción primaria e industria concentraban 73,72% del stock por actividad.", "estado": "mecanismo regulatorio y stock observado", "pregunta_abierta": "¿Cuánto crédito nuevo se aprueba fuera del universo tradicional y bajo qué cobertura cambiaria?", "fuente_principal": "BCRA 2026-08-13 y act2026.xls"},
        {"orden": 5, "etapa": "demanda y elegibilidad empresarial", "evidencia_disponible": "En julio, otras personas jurídicas concentraron 74,59% de las nuevas operaciones USD. La ECC registró demanda PyME débil y expectativas más restrictivas, aunque no es específica de dólares.", "estado": "flujo observado y encuesta contextual", "pregunta_abierta": "¿Hay proyectos rentables y demanda solvente dentro del nuevo cupo?", "fuente_principal": "BCRA preser_mon.xls y ECC 2026-T2"},
        {"orden": 6, "etapa": "liquidación en mercado de cambios", "evidencia_disponible": "Los préstamos alcanzados se liquidan según el marco cambiario aplicable.", "estado": "mecanismo regulatorio", "pregunta_abierta": "¿Qué parte suma oferta neta y cuánto permanece en reservas?", "fuente_principal": "BCRA 2026-08-13"},
        {"orden": 7, "etapa": "inversión, producción y empleo", "evidencia_disponible": "Es el resultado buscado en la comunicación oficial.", "estado": "resultado esperado", "pregunta_abierta": "¿Qué uso efectivo, producción y empleo se observan después?", "fuente_principal": "Economía 2026-08-13"},
    ]
    write_csv(DERIVED / "bank_usd_transmission_map.csv", ["orden", "etapa", "evidencia_disponible", "estado", "pregunta_abierta", "fuente_principal"], rows)


def build_bank_intermediation() -> None:
    rows = [
        {"fecha": "2023-12", "metrica": "depósitos privados en USD", "valor": 14100, "unidad": "USD millones", "naturaleza": "dato oficial comunicado", "formula_o_definicion": "stock", "fuente": "Economía 2026-08-13", "advertencia": "punto inicial redondeado"},
        {"fecha": "2023-12", "metrica": "préstamos privados en USD", "valor": 3700, "unidad": "USD millones", "naturaleza": "dato oficial comunicado", "formula_o_definicion": "stock", "fuente": "Economía 2026-08-13", "advertencia": "punto inicial redondeado"},
        {"fecha": "2023-12", "metrica": "préstamos / depósitos", "valor": 26, "unidad": "%", "naturaleza": "ratio oficial comunicado", "formula_o_definicion": "préstamos ÷ depósitos", "fuente": "Economía 2026-08-13", "advertencia": "ratio redondeado"},
        {"fecha": "2026-08-13", "metrica": "depósitos privados en USD", "valor": 40300, "unidad": "USD millones", "naturaleza": "dato oficial comunicado", "formula_o_definicion": "stock", "fuente": "Economía 2026-08-13", "advertencia": "stock redondeado"},
        {"fecha": "2026-08-13", "metrica": "préstamos privados en USD", "valor": 24600, "unidad": "USD millones", "naturaleza": "dato oficial comunicado", "formula_o_definicion": "stock", "fuente": "Economía 2026-08-13", "advertencia": "stock redondeado; la exposición oral también usa USD 24.700 M"},
        {"fecha": "2026-08-13", "metrica": "préstamos / depósitos", "valor": 61, "unidad": "%", "naturaleza": "ratio oficial comunicado", "formula_o_definicion": "préstamos ÷ depósitos", "fuente": "Economía 2026-08-13", "advertencia": "ratio redondeado"},
        {"fecha": "2026-08-13", "metrica": "referencia prudente histórica", "valor": 65, "unidad": "% de depósitos", "naturaleza": "referencia declarada", "formula_o_definicion": "25% de encaje + aproximadamente 10 p.p. de liquidez adicional", "fuente": "Economía 2026-08-13", "advertencia": "no es un máximo legal"},
        {"fecha": "2026-08-13", "metrica": "máximo regulatorio teórico", "valor": 75, "unidad": "% de depósitos", "naturaleza": "límite regulatorio", "formula_o_definicion": "100% − 25% de efectivo mínimo", "fuente": "Economía 2026-08-13", "advertencia": "no implica utilización plena"},
        {"fecha": "2026-08-13", "metrica": "margen hasta referencia prudente", "valor": 1595, "unidad": "USD millones", "naturaleza": "cálculo derivado", "formula_o_definicion": "40.300 × 65% − 24.600", "fuente": "cálculo propio sobre Economía 2026-08-13", "advertencia": "aproximación con stocks redondeados"},
        {"fecha": "2026-08-13", "metrica": "capacidad adicional hasta máximo regulatorio", "valor": 5800, "unidad": "USD millones", "naturaleza": "estimación oficial aproximada", "formula_o_definicion": "capacidad total aproximada USD 30.500 M − préstamos aproximados USD 24.700 M", "fuente": "Economía 2026-08-13", "advertencia": "capacidad contable; no demanda ni aprobación"},
    ]
    write_csv(
        DERIVED / "usd_bank_intermediation_2023_2026.csv",
        ["fecha", "metrica", "valor", "unidad", "naturaleza", "formula_o_definicion", "fuente", "advertencia"],
        rows,
    )


def build_observed_usd_channels() -> None:
    rows = [
        {"periodo": "2026-07", "universo": "personas humanas · mercado de cambios", "concepto": "compras netas de moneda extranjera", "valor_usd_millones": 4124, "naturaleza": "flujo observado", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "incluye conceptos con distinta finalidad"},
        {"periodo": "2026-07", "universo": "personas humanas · mercado de cambios", "concepto": "compras netas de billetes", "valor_usd_millones": 2916, "naturaleza": "flujo observado", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "no equivale a retiro físico final"},
        {"periodo": "2026-07", "universo": "personas humanas · mercado de cambios", "concepto": "servicios y otros gastos corrientes", "valor_usd_millones": 786, "naturaleza": "flujo observado", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "rubro de uso corriente"},
        {"periodo": "2026-07", "universo": "personas humanas · mercado de cambios", "concepto": "giros sin fines específicos", "valor_usd_millones": 546, "naturaleza": "flujo observado", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "transferencias al exterior"},
        {"periodo": "2026-07", "universo": "compras netas de billetes y divisas sin fin específico", "concepto": "quedó depositado en bancos locales", "valor_usd_millones": 1000, "naturaleza": "estimación oficial", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "aproximación sobre un subconjunto; no sumar al total general"},
        {"periodo": "2026-07", "universo": "compras netas de billetes y divisas sin fin específico", "concepto": "aumento de activos externos", "valor_usd_millones": 1000, "naturaleza": "estimación oficial", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "aproximación sobre un subconjunto; no identifica instrumento"},
        {"periodo": "2026-07", "universo": "compras netas de billetes y divisas sin fin específico", "concepto": "entregado a entidades para cubrir consumos con tarjeta", "valor_usd_millones": 900, "naturaleza": "estimación oficial", "fuente": "BCRA Balance Cambiario 2026-07", "advertencia": "aproximación sobre un subconjunto"},
    ]
    write_csv(
        DERIVED / "usd_channel_observed_july_2026.csv",
        ["periodo", "universo", "concepto", "valor_usd_millones", "naturaleza", "fuente", "advertencia"],
        rows,
    )


def build_prudential_framework() -> None:
    rows = [
        {"regla": "cupo agregado para nuevos deudores antes no admitidos", "valor": 15, "unidad": "% de depósitos en USD por entidad", "funcion": "limitar concentración del nuevo universo", "fuente": "BCRA 2026-08-13"},
        {"regla": "exigencia de capital relativa", "valor": 125, "unidad": "% de una financiación comparable", "funcion": "absorber riesgo adicional", "fuente": "BCRA 2026-08-13"},
        {"regla": "factor para límites de exposición", "valor": 1.25, "unidad": "veces", "funcion": "computar mayor exposición regulatoria", "fuente": "BCRA 2026-08-13"},
        {"regla": "evaluación bajo escenarios cambiarios", "valor": "obligatoria", "unidad": "condición cualitativa", "funcion": "evaluar repago ante movimientos del tipo de cambio", "fuente": "BCRA 2026-08-13"},
    ]
    write_csv(
        DERIVED / "usd_prudential_framework_2026.csv",
        ["regla", "valor", "unidad", "funcion", "fuente"],
        rows,
    )


def load_bcra_monetary_series(filename: str) -> dict[str, float]:
    payload = json.loads((SOURCES / filename).read_text(encoding="utf-8"))
    assert payload["status"] == 200
    detail = payload["results"][0]["detalle"]
    return {row["fecha"]: float(row["valor"]) for row in detail}


def build_a8467_tracker() -> None:
    series_files = {
        "loan_total": "bcra_api_usd_private_loans_total_1355.json",
        "loan_other_advances": "bcra_api_usd_private_loans_other_advances_1358.json",
        "loan_notes": "bcra_api_usd_private_loans_notes_1359.json",
        "loan_mortgages": "bcra_api_usd_private_loans_mortgages_1362.json",
        "loan_pledged": "bcra_api_usd_private_loans_pledged_1363.json",
        "loan_cards": "bcra_api_usd_private_loans_cards_1365.json",
        "loan_other": "bcra_api_usd_private_loans_other_1367.json",
        "deposit_total": "bcra_api_usd_private_deposits_total_1564_2026-08.json",
        "deposit_savings": "bcra_api_usd_private_deposits_savings_1569_2026-08.json",
        "deposit_term": "bcra_api_usd_private_deposits_term_1571_2026-08.json",
    }
    series = {name: load_bcra_monetary_series(filename) for name, filename in series_files.items()}
    month_start = "2026-07-31"
    start = "2026-08-18"
    end = "2026-08-27"

    def change(name: str, from_date: str = start, to_date: str = end) -> dict[str, object]:
        initial = series[name][from_date]
        final = series[name][to_date]
        return {
            "start_usd_millions": round(initial, 4),
            "end_usd_millions": round(final, 4),
            "change_usd_millions": round(final - initial, 4),
            "change_pct": round((final / initial - 1) * 100, 4),
        }

    ratio_start = series["loan_total"][start] / series["deposit_total"][start] * 100
    ratio_end = series["loan_total"][end] / series["deposit_total"][end] * 100
    month_change = series["loan_total"][end] - series["loan_total"][month_start]
    accumulated_by_issuance = series["loan_total"][start] - series["loan_total"][month_start]
    payload = {
        "cutoff_date": "2026-08-31",
        "regulation": {
            "announcement_date": "2026-08-13",
            "communication": "A 8467",
            "issuance_date": start,
            "eligible_borrowers": "Other legal persons outside the previously eligible destinations",
            "households_eligible_under_new_bucket": False,
            "public_bucket_identifier_in_communication": False,
            "explicit_separate_effective_date_in_document": False,
            "scope_note": "The communication defines eligibility and prudential safeguards but does not identify individual borrowers or create a public reporting series for the bucket.",
        },
        "observed_window": {
            "start_date": start,
            "end_date": end,
            "calendar_days": 9,
            "stocks_usd_millions": {
                "private_loans_total": change("loan_total"),
                "private_deposits_total": change("deposit_total"),
                "private_deposits_savings": change("deposit_savings"),
                "private_deposits_term": change("deposit_term"),
            },
            "loan_deposit_ratio_pct": {
                "start": round(ratio_start, 4),
                "end": round(ratio_end, 4),
                "change_percentage_points": round(ratio_end - ratio_start, 4),
            },
            "selected_loan_lines_change_usd_millions": {
                "other_advances": change("loan_other_advances")["change_usd_millions"],
                "single_name_notes": change("loan_notes")["change_usd_millions"],
                "mortgages": change("loan_mortgages")["change_usd_millions"],
                "pledged": change("loan_pledged")["change_usd_millions"],
                "cards": change("loan_cards")["change_usd_millions"],
                "other_loans": change("loan_other")["change_usd_millions"],
            },
            "month_to_date_context": {
                "from_date": month_start,
                "loan_change_to_end_usd_millions": round(month_change, 4),
                "loan_change_accumulated_by_issuance_usd_millions": round(accumulated_by_issuance, 4),
                "share_accumulated_by_issuance_pct": round(accumulated_by_issuance / month_change * 100, 4),
            },
        },
        "availability_calendar": [
            {"date": "2026-09-09", "publication": "Monetary Report", "possible_use": "First August aggregate monetary snapshot", "limitation": "Does not isolate the A 8467 bucket."},
            {"date": "2026-09-14", "publication": "Statistical Bulletin", "possible_use": "Additional August aggregate series", "limitation": "Crosses remain limited."},
            {"date": "2026-09-18", "publication": "Bank Report", "possible_use": "Likely July banking period if the recent lag holds", "limitation": "Would still precede the communication; period mapping is an inference."},
            {"date": "2026-10-16", "publication": "Bank Report", "possible_use": "Likely first general August delinquency snapshot if the recent lag holds", "limitation": "General bank delinquency, not the A 8467 bucket; period mapping is an inference."},
        ],
        "interpretation": [
            "The observed window shows deposits and loans growing by similar orders of magnitude, leaving the aggregate loan-deposit ratio nearly stable.",
            "The rise in deposits was concentrated in term deposits while savings balances were roughly flat.",
            "Most of the August-to-date loan increase through August 27 had already accumulated by the communication issuance date.",
            "None of these aggregate movements identifies mattress cash, a unique depositor, a borrower under A 8467, the final use of credit, or a causal policy effect.",
            "Delinquency is not yet meaningfully observable: only nine calendar days separate issuance and the latest daily stock, while Situation 2 begins after more than 31 days past due.",
        ],
        "sources": [
            "BCRA Communication A 8467, 2026-08-18",
            "BCRA Monetary Statistics API, series 1355, 1358, 1359, 1362, 1363, 1365, 1367, 1564, 1569 and 1571",
            "BCRA publication calendar and Central de Deudores methodology, retrieved 2026-08-31",
        ],
    }
    (DERIVED / "a8467_post_policy_tracker_2026-08-31.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_results_markdown() -> None:
    text = """# Resultados · preguntas sobre los “dólares del colchón”

Fecha de corte: **31/08/2026**.

## Síntesis de alcance

La intuición inicial de Miyu queda registrada en el Storytelling del dashboard. Este módulo la traduce a preguntas abiertas sobre distribución, alternativas de inversión, transmisión bancaria y objetivos de política. La frase suministrada se conserva como **paráfrasis de trabajo**: no fue localizada literalmente en las transcripciones oficiales revisadas. Sí se encontró el argumento de que los dólares fuera del sistema podrían entrar a los bancos, ampliar el crédito empresarial y, por esa vía, favorecer la actividad y el empleo.

El beneficio macroeconómico buscado y el incentivo privado del ahorrista son dimensiones diferentes. Al 27/08/2026, las referencias del BCRA eran 0,22% TNA para caja de ahorro USD y 2,05% para plazos de 60 días o más; la letra del Tesoro estadounidense a 52 semanas rendía 4,14% el 28/08/2026. La comparación es ilustrativa: antes de elegir hay que considerar comisiones, impuestos, custodia, liquidez, acceso y riesgo de precio.

La brecha bruta entre la T-Bill y el plazo fijo era **2,09 puntos porcentuales**. Ese es el costo incremental anual combinado que igualaría ambas referencias antes de diferencias tributarias individuales y riesgo de precio. El dataset de escenarios no estima comisiones reales: permite observar cómo cambia la comparación cuando el usuario explicita un supuesto de costo.

## Capacidad potencial para invertir

INDEC muestra que el 20% de mayores ingresos concentra 50,1% del ingreso corriente y el 40% inferior, 14,5%. Esto respalda la idea de una capacidad concentrada, pero no identifica quién posee dólares: la EPH mide ingresos, no riqueza ni efectivo atesorado. Como contexto, 71,778% de los hogares usó al menos una estrategia extraordinaria de sostenimiento en 2026-T1; tampoco es una medición directa de falta de ahorro.

La estadística bancaria por tramos agrega una pieza más cercana, aunque todavía no identifica personas únicas. En junio de 2026, al sumar cajas de ahorro y plazos fijos de personas físicas residentes en moneda extranjera, los instrumentos con saldo en el tramo de 10.000 o más representaban **1,14% de las cuentas-instrumento y reunían 77,89% del saldo**. El tramo de 100.000 o más representaba **0,067% de las cuentas-instrumento y 29,12% del saldo**. Una cuenta no es una persona: un mismo titular puede tener varias cuentas o ambos instrumentos, y el universo no incluye efectivo fuera del sistema. El resultado prueba concentración dentro de los depósitos bancarios observados, no cuántos argentinos tienen dólares para invertir.

La trayectoria histórica evita otra equivalencia engañosa. Entre diciembre de 2023 y junio de 2026 el stock combinado aumentó en 28,31 millones de cuentas-instrumento, pero sólo 336.516 de la variación neta correspondieron al tramo de 10.000 o más. Aritméticamente, **98,81% del aumento neto del número de cuentas quedó debajo de ese umbral**. Esto no prueba que hayan aparecido 28 millones de nuevos ahorristas: el stock mezcla aperturas, cierres y posibles cambios de reporte. Sí demuestra que “más cuentas” no puede leerse como “más personas con dólares invertibles”. Al mismo tiempo, la proporción del saldo en el tramo de 10.000 o más subió 7,77 puntos y la del tramo de 100.000 o más, 4,51 puntos: la base se amplió por abajo mientras la concentración del dinero se mantuvo alta y aumentó.

## Objetivos y mecanismos declarados

La cadena pretendida es: depósito USD → fondeo bancario → crédito a una empresa → liquidación del préstamo en el mercado de cambios → fondos en pesos/FX adicional → eventual inversión, empleo y recaudación. Cada flecha es contingente. Depositar no convierte automáticamente el dinero en reservas del BCRA ni en capital productivo.

El mapa reproducible separa siete etapas y, para cada una, registra evidencia disponible, estado y pregunta abierta. La presentación informa aproximadamente USD 40.300 millones de depósitos privados y estima USD 5.800 millones de capacidad crediticia disponible: por eso el análisis distingue stock bancarizado, fondeo potencial, decisión bancaria, demanda empresarial y resultado observado.

La profundización agrega una distinción decisiva. Los préstamos en dólares representaban 61% de los depósitos. Si se usa como referencia la práctica prudente histórica descripta por el propio ministro —prestar alrededor de 65% y mantener unos 10 puntos adicionales de liquidez además del encaje—, el margen calculado con los stocks redondeados es cercano a **USD 1.595 millones**. Si se usa el máximo regulatorio teórico de 75%, la estimación oficial asciende a **USD 5.800 millones**. “Capacidad ociosa” no tiene entonces un único valor: depende de si el comparador es una conducta prudente o el límite normativo.

## Auditoría de porcentajes y denominadores

Los porcentajes cercanos no forman una sola identidad contable. El IPOM informa que, en el promedio poselectoral hasta junio, 75% de los dólares comprados para atesoramiento quedó dentro del sistema financiero local, unos USD 1.100 millones por mes. En las palabras iniciales del 6 de agosto, el presidente del BCRA elevó la referencia a “aproximadamente 80%”, después de datos hasta julio, pero no publicó el puente de cálculo que permite reproducir el cambio. Ese 75% de retención local no tiene relación matemática con el otro 75%: el máximo teórico de depósitos que un banco podría prestar luego del encaje de 25%.

El resto de las referencias también usa perímetros distintos: 61% es préstamos privados sobre depósitos privados al 13 de agosto; 65% es una práctica prudente histórica; 17% es la capacidad prestable ociosa estimada por el IPOM en junio; y 48,6% es una medida más amplia de liquidez agregada en moneda extranjera del sistema bancario en junio. Por eso no corresponde sumar 61% y 48,6%, ni restar 17% de cualquiera de ellos. El archivo `percentage_denominator_audit.json` preserva numerador, denominador, fecha, alcance y advertencia de cada cifra.

## Banco local y mercado de capitales

El propio IPOM reconoce que el mercado de capitales es un canal alternativo para ofrecer al ahorrista doméstico una tasa competitiva en dólares. También explica por qué la política busca sostener el canal bancario: lo considera un sustituto imperfecto para financiar firmas de menor escala, con menos capacidad de cumplir exigencias de información pública y fuera de los centros con mayor profundidad de mercado. La discusión no es entonces “banco o comitente” como si uno fuera inválido. Para el ahorrista son opciones con rendimiento, liquidez, costos y riesgos diferentes; para la política cumplen funciones de originación y distribución distintas.

Según el IPOM, el mercado de capitales aportó en el primer semestre de 2026 financiamiento bruto equivalente a USD 20.000 millones y el segmento en dólares representó 43%. La cifra incluye ON, fideicomisos financieros, pagarés, cheques de pago diferido, facturas, acciones y fondos cerrados, valuados al MEP: no debe leerse como stock comparable con depósitos o préstamos bancarios.

## Qué líneas absorbieron el crédito en dólares

La API del BCRA permite abrir el stock por línea. Entre el 29/12/2023 y el 27/08/2026, los préstamos privados en dólares pasaron de USD 3.412 millones a USD 25.367 millones. Los **documentos a sola firma** explicaron USD 16.603 millones, o **75,62% del aumento total**, y representaban 74,07% del stock final. “Otros préstamos” explicaron 13,10% de la expansión; prendarios, 5,28%; hipotecarios, 2,73%; tarjetas, 2,03%; y otros adelantos, 1,12%.

Esto afina el destino financiero, pero todavía no identifica el sector productivo ni el uso final. “Documento a sola firma” es una forma contractual que puede financiar actividades diferentes. La evidencia muestra una expansión fuertemente comercial/documentaria, no que tres cuartas partes hayan ido a construcción, automotrices o inversión nueva.

## Qué actividades concentraban el stock

La planilla trimestral por actividad permite avanzar un paso, con corte anterior a la nueva medida. Al 30/06/2026, el stock de préstamos de efectivo en moneda extranjera ascendía a USD 24.145,64 millones. **Producción primaria reunía 42,38% e industria manufacturera 31,34%**: juntas concentraban **73,72%**. Comercio mayorista y minorista representaba 10,64%; servicios, 6,88%; electricidad, gas y agua, 5,77%; personas físicas en relación de dependencia, 2,01%; y construcción, apenas 0,60%.

La apertura siguiente muestra dónde estaba la masa principal: agricultura, ganadería, caza y silvicultura explicaban 27,01%; alimentos y bebidas, 15,10%; minería y canteras, 15,04%; y comercio mayorista, 9,41%. Entre marzo y junio, producción primaria explicó 47,71% del aumento del stock e industria, 28,39%. La concentración es consistente con el universo tradicional de firmas con ingresos vinculados al comercio exterior, pero la tabla clasifica por actividad principal del deudor y no por destino del dinero.

La estructura de prestamistas también estaba concentrada en bancos: los privados nacionales tenían 38,80% del stock, los extranjeros 36,89%, los públicos 22,47% y las entidades financieras no bancarias 1,84%.

## Quiénes concentraron las operaciones nuevas

La apertura mensual por tipo de prestatario aporta una aproximación al tamaño. En julio de 2026 se registraron USD 3.175,13 millones de operaciones brutas de préstamos de efectivo en moneda extranjera: **otras personas jurídicas concentraron 74,59%**, las personas jurídicas PyME 20,83% y las personas físicas 4,59%. En documentos a sola firma —USD 2.574,84 millones— las participaciones fueron 77,72%, 18,22% y 4,06%.

El contraste aparece también en monto y plazo. Para otras personas jurídicas, el tramo promedio ponderado de los documentos fue **USD 5–10 millones**, el plazo promedio 150 días y 53,49% del monto se concertó a menos de 90 días. Para PyMEs, el tramo promedio fue USD 0,5–0,75 millones, el plazo promedio 422 días y sólo 7,67% quedó debajo de 90 días. El tramo es un código ordinal ponderado, no un préstamo promedio ni una distribución de operaciones.

El patrón es compatible con financiamiento corporativo grande y de corto plazo, pero no prueba su uso. Un documento puede financiar capital de trabajo, comercio exterior, refinanciación, inventarios, sustitución de otra deuda o inversión. El BCRA no publica en estas tablas un cruce simultáneo entre actividad, tamaño, línea, proyecto y destino final.

## Demanda y condiciones antes de la medida

La Encuesta de Condiciones Crediticias de 2026-T2 agrega contexto sobre otro posible cuello de botella. Los bancos percibieron una caída de la demanda empresaria, más intensa en PyMEs (índice de difusión de -29,7%) que en grandes empresas (-16,4%). Para 2026-T3 esperaban una leve suba entre grandes empresas (11,7%), una nueva baja PyME (-9,4%) y estándares especialmente más restrictivos para PyMEs (-24,9%). A la vez, informaron menores spreads sobre el fondeo, pero plazos y garantías más restrictivos.

La encuesta no es específica de moneda extranjera y no debe combinarse contablemente con los flujos anteriores. Sí debilita una explicación de “sólo faltan depósitos”: demanda, elegibilidad, garantías y plazo también aparecen como restricciones observables.

## Tasa activa, tasa pasiva y margen ilustrativo

En julio de 2026, la tasa promedio de nuevas operaciones de documentos a sola firma en dólares fue 3,824% TNA y la de plazos fijos en dólares a 30–44 días, 1,124%. La brecha cotizada fue **2,70 puntos porcentuales**, frente a 5,39 puntos en julio de 2025. Es una compresión importante, pero no un margen contable del banco.

Si se aplica sólo como escenario la tasa activa de julio sobre 61%, 65% o 75% de cada dólar depositado y se resta la tasa pasiva, el carry bruto ilustrativo es 1,21, 1,36 o 1,74 puntos respectivamente. Antes de interpretar ganancia faltan mezcla de fondeo, plazos, capital, liquidez, costos operativos, comisiones, mora y pérdidas crediticias. La comparación sugiere que atraer depósitos no es suficiente: el banco también necesita activos prestables con rendimiento y riesgo compatibles.

## Qué hicieron efectivamente las personas

El Balance Cambiario de julio aporta una observación de flujo. Las personas humanas realizaron compras netas por USD 4.124 millones. Para el subconjunto de billetes y divisas sin fines específicos, el BCRA estimó que aproximadamente **USD 1.000 millones quedaron depositados en bancos locales**, otros **USD 1.000 millones aumentaron activos externos** y unos **USD 900 millones** cubrieron consumos con tarjeta. El dato no distribuye el stock de riqueza ni identifica instrumentos, pero muestra que el canal local y el externo coexistieron en magnitudes similares durante ese mes.

Esos montos de julio no reproducen por sí solos el 75% poselectoral ni el “aproximadamente 80%” de la conferencia: son flujos netos de un solo mes, con destinos redondeados y un universo diferente. La conclusión segura es más acotada: durante julio coexistieron ahorro bancario local, acumulación de activos externos y pagos corrientes.

## Qué limita el crédito nuevo

La ampliación del universo elegible no elimina el control prudencial. Para las financiaciones a clientes antes no admitidos, el BCRA fijó un cupo agregado de 15% de los depósitos en dólares por entidad, una exigencia de capital equivalente a 125% de una financiación comparable, un cómputo de exposición de 1,25 veces y evaluación de repago bajo movimientos del tipo de cambio. Esto vuelve más precisa la cadena: el depósito es fondeo potencial, pero el banco enfrenta cupos, capital, exposición y riesgo cambiario antes de decidir el préstamo.

La Comunicación A 8467, emitida el 18/08/2026, precisó quién puede acceder al nuevo cupo: **otras personas jurídicas que no encuadren en los destinos antes admitidos**. No habilita a los hogares como prestatarios de ese cupo. También exige que el banco preste especial atención al flujo de fondos y al patrimonio del deudor para evaluar si puede absorber aumentos de sus obligaciones cuando sus ingresos no acompañen al tipo de cambio.

## Primer corte posterior a la A 8467

Entre el 18 y el 27 de agosto, los depósitos privados en dólares aumentaron de USD 40.655 millones a USD 40.843 millones: **USD 188 millones**. Los plazos fijos explicaron USD 187 millones, mientras las cajas de ahorro disminuyeron USD 5 millones. En el mismo período, los préstamos privados en dólares pasaron de USD 25.217 millones a USD 25.367 millones: **USD 150 millones**. El ratio préstamos/depósitos apenas cambió de **62,03% a 62,11%**.

La composición publicada tampoco muestra una irrupción concentrada en documentos a sola firma: entre esos dos cortes, las tarjetas aumentaron USD 149 millones y “otros préstamos”, USD 134 millones, mientras los documentos disminuyeron USD 86 millones. Las líneas seleccionadas no reconcilian exactamente con el total por líneas menores y posibles reclasificaciones, de modo que no se fuerzan participaciones causales.

Además, de los USD 833 millones que el stock total de préstamos había aumentado entre el 31 de julio y el 27 de agosto, USD 683 millones —**82,0%**— ya se habían acumulado al día de emisión de la comunicación. Esto no separa movimientos ocurridos dentro del 18 de agosto ni establece cuál habría sido la trayectoria sin la norma. Sí evita atribuir automáticamente toda la expansión mensual al nuevo cupo.

El corte diario permite describir stocks agregados, no identificar dólares físicos que ingresaron desde fuera del sistema, depositantes únicos, transferencias desde cuentas o comitentes, prestatarios bajo A 8467 ni el uso final de sus préstamos. La comunicación no crea en sus dos páginas un identificador público del cupo. Por eso este primer corte es una **línea de base de seguimiento**, no una estimación de efecto causal.

## Calendario de prueba

El calendario del BCRA anuncia el Informe Monetario del 9/09 y el Boletín Estadístico del 14/09, primeras oportunidades para revisar agregados de agosto. El Informe sobre Bancos del 18/09 probablemente corresponda a julio si se mantiene el rezago reciente; el del 16/10 sería la primera ventana probable sobre mora bancaria general de agosto. La asignación de período a fecha es una inferencia, no una promesa del calendario.

Incluso entonces, la mora seguirá sin distinguir el cupo A 8467. La Central de Deudores es mensual, informa entidad, saldo y situación, pero no moneda, uso final ni identificador del programa. Además, la situación 2 comienza después de más de 31 días de atraso: entre la emisión y el último stock diario disponible sólo transcurrieron nueve días. Actividad, plazo, mora y destino final seguirán requiriendo publicaciones diferentes y no existe hoy un cruce público que los reúna.

Las fuentes permiten observar objetivos como formalizar activos, profundizar el crédito y favorecer el crecimiento sin expandir el gasto o la emisión. También muestran por qué fondeo, demanda, elegibilidad y uso deben analizarse por separado. La pregunta siguiente ya no es solamente si crecen los agregados, sino si futuras publicaciones permiten distinguir quién usa el cupo, en qué condiciones y con qué resultados.

## Preguntas abiertas y límites

- La PII registra USD 259,305 mil millones de moneda y depósitos de “otros sectores”, pero mezcla hogares, empresas e ISFLSH: no es una medición del “colchón” de las familias.
- El informe bancario de junio muestra que el crédito privado en moneda extranjera crecía 53,2% interanual frente a 27,4% de los depósitos, y una liquidez agregada en moneda extranjera de 48,6%. Son datos de otra fecha y definición: describen aceleración y colchón sistémico, pero no deben equipararse mecánicamente con el ratio préstamos/depósitos del 13 de agosto ni con el 17% de capacidad ociosa del IPOM.
- La tabla de tramos sólo permite medir concentración entre cuentas y saldos bancarios; no identifica titulares únicos, efectivo, cuentas en el exterior ni tenencias en comitentes.
- El aumento del número de cuentas se concentró aritméticamente debajo del tramo de 10.000, pero la fuente no permite distinguir aperturas genuinas de cambios de perímetro o cuentas automáticas de bajo saldo.
- La apertura por actividad y prestatario muestra concentración sectorial y por categoría jurídica, pero el BCRA no publica en estas tablas un cruce simultáneo entre actividad, tamaño, línea y uso final.
- El stock por actividad termina en junio y la encuesta en 2026-T2: ambos anteceden al anuncio del 13/08 y no miden el nuevo cupo.
- “Otras personas jurídicas” es la categoría complementaria a PyMEs en la planilla de operaciones; no equivale perfectamente a “grandes empresas” en la encuesta.
- El plazo corto y el tramo alto son compatibles con financiamiento corporativo de corto plazo, pero no identifican por sí solos capital de trabajo ni descartan inversión.
- La brecha entre tasa activa y pasiva no es el margen neto del banco; sólo se usa como escenario mecánico y conserva todos sus costos y riesgos fuera del cálculo.
- La CNV exige que los agentes informen comisiones, derechos, gastos e impuestos de cada operación. Por eso no existe un único “costo de comitente” generalizable; el simulador conserva el costo como supuesto explícito del usuario.
- La garantía de depósitos rige hasta ARS 50 millones por persona/entidad desde el 01/04/2026; los depósitos en moneda extranjera se convierten al tipo de referencia aplicable.
- ¿Qué peso relativo tienen la formalización, el crédito, la actividad, la recaudación y otros objetivos no explicitados en estas fuentes?
- Las motivaciones personales del ministro quedan fuera del alcance empírico; el módulo se limita a declaraciones, incentivos, restricciones y mecanismos observables.
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
    build_questions_matrix()
    build_channel_break_even()
    build_bank_transmission_map()
    build_bank_intermediation()
    build_observed_usd_channels()
    build_prudential_framework()
    build_a8467_tracker()
    build_results_markdown()
    print("OK: manifiesto, datasets derivados y memo de resultados generados")


if __name__ == "__main__":
    main()
