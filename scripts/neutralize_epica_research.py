from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "epica_dashito_2026"


LOGICAL_READINGS = {
    "not_an_identity": "relation_not_mechanical",
    "false_as_necessity": "relation_not_necessary",
    "false_by_accounting": "accounting_scope_mismatch",
    "false_inference": "inference_not_identified",
    "false_by_definition": "definition_scope_mismatch",
    "false_universal": "depends_on_conditions",
    "false_equivalence": "concepts_not_equivalent",
    "not_testable_as_written": "requires_operational_definition",
    "normative_or_unidentified": "normative_or_not_identified",
    "false_simplification": "mechanism_more_complex",
    "false_scope": "scope_incomplete",
    "unsupported_mapping": "mapping_not_supported",
    "unsupported_proxy": "proxy_not_supported",
    "not_identified": "not_identified",
    "not_yet_identified": "not_yet_identified",
}


def neutralize_claims_registry() -> None:
    path = RESEARCH / "claims_registry.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    normalized = []
    for row in rows:
        prior = row.get("logical_reading") or row.get("logical_verdict") or ""
        normalized.append(
            {
                "claim_id": row["claim_id"],
                "statement": row.get("statement") or row.get("claim") or "",
                "logical_reading": LOGICAL_READINGS.get(prior, prior),
                "evidence_status": row.get("evidence_status") or row.get("empirical_status") or "",
                "linked_analysis_ids": row["linked_analysis_ids"],
                "reason": row["reason"],
            }
        )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(normalized[0]))
        writer.writeheader()
        writer.writerows(normalized)


TEXT_REPLACEMENTS = {
    RESEARCH / "README.md": {
        "| `strong_partial` | 4 |": "| `strong_partial` | 8 |",
        "| `partial` | 26 |": "| `partial` | 22 |",
        "dobles conteos o falsas identidades": "dobles conteos o equivalencias mecánicas",
        "Esta corrida no modifica `index.html`. El repositorio tiene trabajo previo y cambios activos; integrar visualizaciones antes de cerrar universos y fórmulas aumentaría el riesgo de publicar dobles conteos o equivalencias mecánicas. Los paquetes de evidencia quedan listos para una segunda etapa de integración por super-tabs.": "La evidencia auditada ya alimenta los super-tabs de la épica. La integración conserva universos, fórmulas, estados `N/D` y escenarios visibles para evitar dobles conteos o equivalencias mecánicas.",
    },
    RESEARCH / "MASTER_RESULTS.md": {
        "La identidad “superávit comercial = superávit de cuenta corriente” queda rechazada.": "Los datos muestran que “superávit comercial” y “superávit de cuenta corriente” no describen la misma magnitud contable.",
        "sirve para rechazar una identidad mecánica, no para inferir un pass-through estructural": "muestra que la relación no es mecánica, pero no permite inferir un pass-through estructural",
        "## Hallazgos que sí pasan el gate": "## Resultados con respaldo suficiente para integrar",
    },
    RESEARCH / "dolares_externo" / "ANALISIS_DOLARES_SECTOR_EXTERNO.md": {
        "# Dólares, reservas y sector externo — ejecución empírica": "# Dólares, reservas y sector externo — análisis empírico",
        "El siguiente puente es una auditoría de stocks identificables": "El siguiente puente organiza stocks identificables",
        "### Las cuatro etiquetas pedidas, sin falsa precisión": "### Las cuatro etiquetas pedidas, con precisión compatible con las fuentes",
        "**Hipótesis que sobrevive:** el poder de fuego propio es menor que el bruto.": "**Lectura compatible con los datos:** el poder de fuego disponible bajo condiciones específicas es menor que el stock bruto.",
        "Esto refuta la identidad informal “superávit comercial = superávit externo”.": "Los datos muestran los límites de equiparar “superávit comercial” con “superávit externo”.",
        "**Hipótesis que sobrevive:** el pass-through depende del régimen, expectativas, actividad y composición del IPC.": "**Lectura compatible con los datos:** el pass-through varía con el régimen, las expectativas, la actividad y la composición del IPC.",
        "Eso es un resultado de auditoría, no un cero": "Eso es un resultado del análisis, no un cero",
        "sin falsa precisión": "sin una precisión que las fuentes no respaldan",
    },
    RESEARCH / "hogares_credito" / "INFORME_HOGARES_CREDITO.md": {
        "# Auditoría empírica — Hogares, crédito, transferencias y costo de vida": "# Análisis empírico — Hogares, crédito, transferencias y costo de vida",
        "**Hipótesis que sobrevive:** la fragilidad financiera puede alcanzar hogares no pobres y coexistir con ingresos laborales.": "**Lectura compatible con los datos:** la fragilidad financiera puede alcanzar hogares no pobres y coexistir con ingresos laborales.",
        "El resultado falsifica la equivalencia “bajó pobreza = se consolidó el bienestar financiero”": "El resultado muestra que “bajó pobreza” y “se consolidó el bienestar financiero” no son equivalentes",
        "Eso mantiene viva la hipótesis de expansión con selección/precio/capacidad de pago interactuando.": "La secuencia es compatible con una interacción entre expansión, selección, precio y capacidad de pago.",
    },
    RESEARCH / "fiscal_desarrollo" / "INFORME_AUDITORIA.md": {
        "# Auditoría empírica — fiscal, balances sectoriales, inversión-empleo e infraestructura": "# Análisis empírico — fiscal, balances sectoriales, inversión-empleo e infraestructura",
        "queda marcado para auditoría metodológica": "queda marcado para revisión metodológica",
    },
    RESEARCH / "fiscal_desarrollo" / "build_auditoria.mjs": {
        "# Auditoría empírica — fiscal, balances sectoriales, inversión-empleo e infraestructura": "# Análisis empírico — fiscal, balances sectoriales, inversión-empleo e infraestructura",
        "queda marcado para auditoría metodológica": "queda marcado para revisión metodológica",
    },
}


def neutralize_reports() -> None:
    for path, replacements in TEXT_REPLACEMENTS.items():
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            if old in text:
                text = text.replace(old, new)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    neutralize_claims_registry()
    neutralize_reports()
    print("OK: corpus de la épica expresado como preguntas, relaciones y límites")


if __name__ == "__main__":
    main()
