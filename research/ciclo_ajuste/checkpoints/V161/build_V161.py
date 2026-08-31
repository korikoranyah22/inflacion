from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
V160 = CYCLE / "checkpoints" / "V160"
SYNC = CYCLE / "inputs" / "source_sync" / "v161"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
FACTOR = Decimal("1.532908152197492")
SYSTEM_ASSETS = Decimal("96697695.5")
OLD_NUMERATOR = Decimal("59812903.504")
ADDED_ASSETS = Decimal("1435816.249")
NEW_NUMERATOR = OLD_NUMERATOR + ADDED_ASSETS
getcontext().prec = 120
STRICT = NEW_NUMERATOR / SYSTEM_ASSETS * Decimal(100)
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            (name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold
        )
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def q4(fy, nine_month):
    return Decimal(str(fy)) - Decimal(str(nine_month)) * FACTOR


def clone_parent():
    excluded_prefixes = (
        "build_V160.py",
        "qa_v160.py",
        "MANIFEST_V160.json",
        "CURRENT_STATE_V160.csv",
        "FOUR_LEG_PASS_PANEL_V160.csv",
        "STRICT_Q4_FOUR_LEG_COVERAGE_V160.csv",
        "README_V160.md",
        "VEREDICTO_V160.md",
        "AUDITORIA_V160.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V160_A_V161.md",
    )
    for source in sorted(V160.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name.startswith(excluded_prefixes):
            continue
        target = HERE / source.name.replace("V160", "V161")
        text = source.read_text(encoding="utf-8-sig")
        target.write_text(text.replace("V160", "V161"), encoding="utf-8")


clone_parent()


current = read_csv(V160 / "CURRENT_STATE_V160.csv")
current_index = {row["entity"]: row for row in current}
current_index["Banco de Corrientes S.A."].update(
    {
        "target_basis": "INDIVIDUAL_ENTITY_REGULATORY_WITH_ISSUER_FY_VALIDATION",
        "fy_status": "OFFICIAL_FY_ANNEXQ_DIRECT_BCRA_ONLY_EXACT_BINARY_PRESERVED_V161",
        "nine_month_status": "BCRA_RAW_SEP_EXACT_WITH_CORRIENTES_SPECIFIC_SAME_YEAR_FY_CROSSWALK",
        "q4_four_leg_status": "EXACT",
        "strict_panel_status": "ELIGIBLE",
        "priority": "CLOSED_V161",
        "next_action": "retain; FY Annex Q maps 511108 to BCRA for Corrientes only; apply the same-entity same-year account-set bridge to Sep raw; never generalize the label",
    }
)
current_index["Banco Mariva S.A."].update(
    {
        "target_basis": "SEPARATED_INDIVIDUAL_WITH_ENTITY_SPECIFIC_RAW_BRIDGE",
        "fy_status": "OFFICIAL_SEPARATED_FY_ANNEXQ_DIRECT_OTHERFI_ONLY_EXACT_BINARY_PRESERVED_V161",
        "nine_month_status": "OFFICIAL_SEPARATED_9M_BASIS_CONFIRMED_NO_ANNEXQ_PLUS_MARIVA_SPECIFIC_SAME_YEAR_RAW_SET",
        "q4_four_leg_status": "EXACT",
        "strict_panel_status": "ELIGIBLE",
        "priority": "CLOSED_V161",
        "next_action": "retain; FY issuer totals reconcile the Mariva-only four-account set exactly; use that set at Sep 2023 only, with BCRA legs zero",
    }
)
current_index["HSBC Bank Argentina S.A."].update(
    {
        "target_basis": "SEPARATED_INDIVIDUAL",
        "fy_status": "OFFICIAL_FY_TOTAL_PASS_INCOME_AND_EXPENSE_EXACT_SECTOR_FINANCIERO_UNSPLIT_BINARY_PRESERVED_V161",
        "nine_month_status": "OFFICIAL_SEPARATED_9M_BASIS_BINARY_PRESERVED_NO_RESULT_OPENING_PLUS_RAW_TOTAL_RECONCILIATION",
        "q4_four_leg_status": "N/D_STRICT",
        "strict_panel_status": "PENDING",
        "priority": "COUNTERPARTY_SPLIT_LIMIT_V161",
        "next_action": "seek an issuer or regulatory opening that separates BCRA from other financial institutions; totals and repo stock do not identify the counterparty split",
    }
)
bma = {
    "entity": "Banco BMA S.A.U. (antes Banco Itaú Argentina S.A.)",
    "target_basis": "SEPARATED_INDIVIDUAL",
    "fy_status": "OFFICIAL_SEPARATED_FY_ANNEXQ_DIRECT_FOUR_LEG_EXACT_BINARY_PRESERVED_V161_RAW_SET_RECONCILED",
    "nine_month_status": "OFFICIAL_SEPARATED_9M_ANNEXQ_DIRECT_FOUR_LEG_EXACT_BINARY_PRESERVED_V161_RAW_SET_RECONCILED",
    "q4_four_leg_status": "EXACT",
    "strict_panel_status": "ELIGIBLE",
    "priority": "CLOSED_V161",
    "next_action": "retain; both issuer periods publish the counterparty split and reconcile the entity-specific raw account sets exactly",
}
current.append(bma)
write_csv(HERE / "CURRENT_STATE_V161.csv", current)


promotion_fields = [
    "entity",
    "basis",
    "period",
    "income_bcra",
    "expense_bcra",
    "income_otherfi",
    "expense_otherfi",
    "unit",
    "quality",
    "source_logic",
]


def promotion_rows(entity, basis, nine_month, fy, quality_9m, quality_fy, source_logic):
    q4_values = [q4(fy[index], nine_month[index]) for index in range(4)]
    return [
        dict(
            zip(
                promotion_fields,
                [
                    entity,
                    basis,
                    "9M-2023",
                    *nine_month,
                    "thousand_ARS_Sep2023_homogeneous",
                    quality_9m,
                    source_logic,
                ],
            )
        ),
        dict(
            zip(
                promotion_fields,
                [
                    entity,
                    basis,
                    "FY-2023",
                    *fy,
                    "thousand_ARS_Dec2023_homogeneous",
                    quality_fy,
                    source_logic,
                ],
            )
        ),
        dict(
            zip(
                promotion_fields,
                [
                    entity,
                    basis,
                    "Q4-2023",
                    *(str(value) for value in q4_values),
                    "thousand_ARS_Dec2023_homogeneous",
                    "EXACT_HOMOGENEOUS_DIFFERENCING_AT_PUBLISHED_PRECISION",
                    "Q4 = FY_Dec - 9M_Sep × frozen factor 1.532908152197492; no clamping",
                ],
            )
        ),
    ]


bma_promotion = promotion_rows(
    bma["entity"],
    "SEPARATED_INDIVIDUAL",
    ("29151547", "0", "329255", "874222"),
    ("79896235", "0", "574991", "7081885"),
    "EXACT_OFFICIAL_SEPARATED_9M_ANNEXQ_PLUS_ENTITY_SPECIFIC_RAW_RECONCILIATION",
    "EXACT_OFFICIAL_SEPARATED_FY_ANNEXQ_PLUS_ENTITY_SPECIFIC_RAW_RECONCILIATION",
    "Issuer Annex Q pages 130-131 / 203-204; BCRA raw entity 00259 crosscheck",
)
mariva_promotion = promotion_rows(
    "Banco Mariva S.A.",
    "SEPARATED_INDIVIDUAL_WITH_ENTITY_SPECIFIC_RAW_BRIDGE",
    ("0", "0", "11489237", "8559"),
    ("0", "0", "27573387", "13992"),
    "EXACT_MARIVA_SPECIFIC_SAME_YEAR_RAW_SET_WITH_SEPARATED_9M_BASIS",
    "EXACT_OFFICIAL_SEPARATED_FY_ANNEXQ_PLUS_ENTITY_SPECIFIC_RAW_RECONCILIATION",
    "FY Annex Q pages 189-190 maps the complete Mariva raw account set; Sep source is separated but lacks Annex Q",
)
corrientes_promotion = promotion_rows(
    "Banco de Corrientes S.A.",
    "INDIVIDUAL_ENTITY_REGULATORY_WITH_ISSUER_FY_VALIDATION",
    ("16968619", "0", "0", "0"),
    ("40870153", "0", "0", "0"),
    "EXACT_CORRIENTES_SPECIFIC_SAME_YEAR_RAW_SET",
    "EXACT_OFFICIAL_FY_ANNEXQ_PLUS_ENTITY_SPECIFIC_RAW_RECONCILIATION",
    "Official FY Annex Q page 130 maps Corrientes account 511108 to BCRA; same account set applied to Sep only",
)
write_csv(HERE / "BMA_Q4_FOUR_LEG_PROMOTION_V161.csv", bma_promotion, promotion_fields)
write_csv(HERE / "MARIVA_Q4_FOUR_LEG_PROMOTION_V161.csv", mariva_promotion, promotion_fields)
write_csv(HERE / "CORRIENTES_Q4_FOUR_LEG_PROMOTION_V161.csv", corrientes_promotion, promotion_fields)


cross_fields = [
    "period",
    "entity_code",
    "raw_account_set",
    "raw_values_thousand_ars",
    "raw_set_sum_thousand_ars",
    "target_leg",
    "issuer_value_thousand_ars",
    "issuer_page",
    "verdict",
    "scope_limit",
]


def cross(period, code, accounts, values, total, leg, issuer, page, verdict, limit):
    return dict(
        zip(
            cross_fields,
            [period, code, accounts, values, total, leg, issuer, page, verdict, limit],
        )
    )


bma_cross = [
    cross("9M-2023", "00259", "511007+511108", "2174590+26976957", "29151547", "income_bcra", "29151547", "9M PDF physical 54 / printed 130", "EXACT_ENTITY_SPECIFIC_SET", "BMA/Itaú 2023 only"),
    cross("9M-2023", "00259", "511027", "329255", "329255", "income_otherfi", "329255", "9M PDF physical 54 / printed 130", "EXACT_ENTITY_SPECIFIC", "BMA/Itaú 2023 only"),
    cross("9M-2023", "00259", "521007+521022", "1758+872464", "874222", "expense_otherfi", "874222", "9M PDF physical 55 / printed 131", "EXACT_ENTITY_SPECIFIC_SET", "BMA/Itaú 2023 only"),
    cross("9M-2023", "00259", "ABSENT_BCRA_EXPENSE_SET", "0", "0", "expense_bcra", "0", "9M PDF physical 55 / printed 131", "EXACT_ZERO", "BMA/Itaú 2023 only"),
    cross("FY-2023", "00259", "511007+511108", "3638320+76257915", "79896235", "income_bcra", "79896235", "FY PDF physical 65 / printed 203", "EXACT_ENTITY_SPECIFIC_SET", "BMA/Itaú 2023 only"),
    cross("FY-2023", "00259", "511027", "574991", "574991", "income_otherfi", "574991", "FY PDF physical 65 / printed 203", "EXACT_ENTITY_SPECIFIC", "BMA/Itaú 2023 only"),
    cross("FY-2023", "00259", "521007+521022", "5494+7076391", "7081885", "expense_otherfi", "7081885", "FY PDF physical 66 / printed 204", "EXACT_ENTITY_SPECIFIC_SET", "BMA/Itaú 2023 only"),
    cross("FY-2023", "00259", "ABSENT_BCRA_EXPENSE_SET", "0", "0", "expense_bcra", "0", "FY PDF physical 66 / printed 204", "EXACT_ZERO", "BMA/Itaú 2023 only"),
]
mariva_cross = [
    cross("9M-2023", "00254", "511027+515034", "11112903+376334", "11489237", "income_otherfi", "N/A_NO_9M_ANNEXQ", "9M PDF full-document search", "SUPPORTED_BY_SAME_ENTITY_SAME_YEAR_FY_SET", "Mariva 2023 only; not a universal account rule"),
    cross("9M-2023", "00254", "521022+525042", "2958+5601", "8559", "expense_otherfi", "N/A_NO_9M_ANNEXQ", "9M PDF full-document search", "SUPPORTED_BY_SAME_ENTITY_SAME_YEAR_FY_SET", "Mariva 2023 only; not a universal account rule"),
    cross("9M-2023", "00254", "ABSENT_BCRA_PASS_RESULT_SET", "0", "0", "income_bcra;expense_bcra", "N/A_NO_9M_ANNEXQ", "9M PDF full-document search", "EXACT_ZERO_WITH_ENTITY_SET_LIMIT", "Mariva 2023 only; not a universal account rule"),
    cross("FY-2023", "00254", "511027+515034", "26821231+752156", "27573387", "income_otherfi", "27573387", "FY PDF physical 78 / printed 190", "EXACT_ENTITY_SPECIFIC_SET", "Mariva 2023 only"),
    cross("FY-2023", "00254", "521022+525042", "5407+8585", "13992", "expense_otherfi", "13992", "FY PDF physical 78 / printed 190", "EXACT_ENTITY_SPECIFIC_SET", "Mariva 2023 only"),
    cross("FY-2023", "00254", "ABSENT_BCRA_PASS_RESULT_SET", "0", "0", "income_bcra;expense_bcra", "0", "FY PDF physical 78 / printed 190", "EXACT_ZERO", "Mariva 2023 only"),
]
corrientes_cross = [
    cross("9M-2023", "00094", "511108", "16968619", "16968619", "income_bcra", "N/A_NO_9M_ISSUER_OPENING", "BCRA Sep raw", "SUPPORTED_BY_SAME_ENTITY_SAME_YEAR_FY_CROSSWALK", "Corrientes 2023 only"),
    cross("9M-2023", "00094", "ABSENT_OTHER_PASS_RESULT_ACCOUNTS", "0", "0", "expense_bcra;income_otherfi;expense_otherfi", "N/A_NO_9M_ISSUER_OPENING", "BCRA Sep raw", "EXACT_ZERO_WITH_ENTITY_SET_LIMIT", "Corrientes 2023 only"),
    cross("FY-2023", "00094", "511108", "40870153", "40870153", "income_bcra", "40870153", "FY PDF physical 130", "EXACT_ENTITY_SPECIFIC", "Corrientes 2023 only"),
    cross("FY-2023", "00094", "ABSENT_OTHER_PASS_RESULT_ACCOUNTS", "0", "0", "expense_bcra;income_otherfi;expense_otherfi", "0", "FY PDF physical 130", "EXACT_ZERO", "Corrientes 2023 only"),
]
write_csv(HERE / "BMA_ENTITY_SPECIFIC_CROSSWALK_V161.csv", bma_cross, cross_fields)
write_csv(HERE / "MARIVA_ENTITY_SPECIFIC_CROSSWALK_V161.csv", mariva_cross, cross_fields)
write_csv(HERE / "CORRIENTES_ENTITY_SPECIFIC_CROSSWALK_V161.csv", corrientes_cross, cross_fields)


hsbc_q4_income = q4("204724664", "68481253")
hsbc_q4_expense = q4("542204", "169767")
hsbc_fields = [
    "period",
    "pass_income_total_thousand_ars",
    "pass_expense_total_thousand_ars",
    "issuer_counterparty_label",
    "four_leg_status",
    "reason",
]
hsbc_rows = [
    {"period": "9M-2023", "pass_income_total_thousand_ars": "68481253", "pass_expense_total_thousand_ars": "169767", "issuer_counterparty_label": "RAW_TOTAL_ONLY; issuer 9M opening absent", "four_leg_status": "N/D_STRICT", "reason": "One total does not determine BCRA versus other financial institutions."},
    {"period": "FY-2023", "pass_income_total_thousand_ars": "204724664", "pass_expense_total_thousand_ars": "542204", "issuer_counterparty_label": "sector financiero", "four_leg_status": "N/D_STRICT", "reason": "The issuer does not split sector financiero between BCRA and other financial institutions."},
    {"period": "Q4-2023", "pass_income_total_thousand_ars": str(hsbc_q4_income), "pass_expense_total_thousand_ars": str(hsbc_q4_expense), "issuer_counterparty_label": "sector financiero total only", "four_leg_status": "N/D_STRICT", "reason": "Homogeneous differencing preserves exact totals but cannot identify four legs; repo stock is not a flow allocation."},
]
write_csv(HERE / "HSBC_COUNTERPARTY_SPLIT_LIMIT_V161.csv", hsbc_rows, hsbc_fields)
(HERE / "HSBC_COUNTERPARTY_SPLIT_LIMIT_V161.md").write_text(
    """# HSBC: límite de separación de contraparte V161

El estado anual individual publica 204.724.664 miles de pesos de primas e intereses por pases activos y 542.204 miles de pesos de pases pasivos, ambos con el rótulo agregado “sector financiero”. Los archivos regulatorios crudos reproducen exactamente esos totales. El estado intermedio preservado no publica una apertura de resultados equivalente.

La diferencia homogénea produce totales Q4 exactos de 99.749.193,003601044382524 y 281.966,781725888375636 miles de pesos. No produce la asignación entre BCRA y otras entidades financieras: hay infinitas combinaciones de dos contrapartes que suman el mismo total. La exposición de stock “operaciones de pases con el BCRA” tampoco resuelve la composición del flujo de resultados. HSBC permanece N/D_STRICT y funciona como control contra la generalización de etiquetas de cuentas.
""",
    encoding="utf-8",
)


panel = read_csv(V160 / "FOUR_LEG_PASS_PANEL_V160.csv")


def panel_row(promotion, quality, note):
    row = promotion[-1]
    income_bcra = Decimal(row["income_bcra"])
    expense_bcra = Decimal(row["expense_bcra"])
    income_other = Decimal(row["income_otherfi"])
    expense_other = Decimal(row["expense_otherfi"])
    return {
        "entity": row["entity"],
        "basis": row["basis"],
        "period": "Q4-2023",
        "income_bcra": str(income_bcra),
        "expense_bcra": str(expense_bcra),
        "income_otherfi": str(income_other),
        "expense_otherfi": str(expense_other),
        "net_bcra": str(income_bcra - expense_bcra),
        "net_otherfi": str(income_other - expense_other),
        "quality": quality,
        "target_basis_compatible": "YES",
        "system_panel_eligible_v72": "YES_EXACT_Q4_TARGET_BASIS",
        "v72_note": note,
    }


panel.extend(
    [
        panel_row(bma_promotion, "EXACT_FROM_PRESERVED_OFFICIAL_SEPARATED_ISSUER_9M_FY_ANNEXQ_PLUS_ENTITY_SPECIFIC_RAW_RECONCILIATION", "V161 promotion: both direct Annex Q periods reconcile exactly; account sets are BMA/Itaú-specific."),
        panel_row(mariva_promotion, "EXACT_FROM_PRESERVED_OFFICIAL_SEPARATED_FY_ANNEXQ_PLUS_MARIVA_SPECIFIC_SAME_YEAR_RAW_SET", "V161 promotion: 9M basis is separated; FY maps the complete Mariva-only raw account set; no universal mapping."),
        panel_row(corrientes_promotion, "EXACT_FROM_PRESERVED_OFFICIAL_FY_ANNEXQ_PLUS_CORRIENTES_SPECIFIC_SAME_YEAR_RAW_CROSSWALK", "V161 promotion: official FY maps 511108 to BCRA for Corrientes; same-year Sep use is entity-specific."),
        {
            "entity": "HSBC Bank Argentina S.A.",
            "basis": "SEPARATED_INDIVIDUAL",
            "period": "Q4-2023",
            "income_bcra": f"0_to_{hsbc_q4_income}",
            "expense_bcra": f"0_to_{hsbc_q4_expense}",
            "income_otherfi": f"0_to_{hsbc_q4_income}",
            "expense_otherfi": f"0_to_{hsbc_q4_expense}",
            "net_bcra": "N/D",
            "net_otherfi": "N/D",
            "quality": "TOTAL_ONLY_SECTOR_FINANCIERO_COUNTERPARTY_UNSPLIT",
            "target_basis_compatible": "YES_BASIS_BUT_NOT_FOUR_LEG",
            "system_panel_eligible_v72": "NO",
            "v72_note": "V161 negative control: exact pass totals do not identify the BCRA/other-FI split; repo stock cannot allocate result flows.",
        },
    ]
)
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V161.csv", panel)


coverage_fields = [
    "coverage_set",
    "basis",
    "period",
    "asset_numerator_million_ars",
    "system_assets_million_ars",
    "asset_coverage_pct",
    "increment_vs_v105_pp",
    "quality",
    "closed_network_gate",
    "v161_change",
]
old_increment = Decimal("2.07796678256929090931644798091387813890559573883536862571869667773002925390295366449555154459249549")
old_coverage = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
coverage = [
    {
        "coverage_set": "V161 strict 33-entity set after BMA + Mariva + Corrientes promotion",
        "basis": "INDIVIDUAL_ENTITY_REGULATORY / INDIVIDUAL_ISSUER / SEPARATED_INDIVIDUAL / STANDALONE_ISSUER / ENTITY_SPECIFIC_SAME_YEAR_RAW_CROSSWALK",
        "period": "Q4-2023",
        "asset_numerator_million_ars": str(NEW_NUMERATOR),
        "system_assets_million_ars": str(SYSTEM_ASSETS),
        "asset_coverage_pct": str(STRICT),
        "increment_vs_v105_pp": str(old_increment + STRICT - old_coverage),
        "quality": "ALL_FOUR_LEGS_EXACT_THIRTY_THREE_ENTITIES",
        "closed_network_gate": "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN",
        "v161_change": "Adds BMA 883306.273m, Mariva 202982.416m and Corrientes 349527.560m assets; HSBC remains N/D_STRICT.",
    }
]
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V161.csv", coverage, coverage_fields)


review_fields = [
    "entity",
    "entity_code",
    "issuer_9m_evidence",
    "issuer_fy_evidence",
    "raw_reconciliation",
    "q4_decision",
    "coverage_assets_million_ars",
    "scope_guardrail",
]
review = [
    {"entity": bma["entity"], "entity_code": "00259", "issuer_9m_evidence": "Direct separated Annex Q four-leg split, physical pages 54-55", "issuer_fy_evidence": "Direct separated Annex Q four-leg split, physical pages 65-66", "raw_reconciliation": "Exact all nonzero account sets at Sep and Dec", "q4_decision": "PROMOTE_EXACT", "coverage_assets_million_ars": "883306.273", "scope_guardrail": "511007 joins BCRA income and 521007 joins Other-FI expense for BMA/Itaú only; no global label rule"},
    {"entity": "Banco Mariva S.A.", "entity_code": "00254", "issuer_9m_evidence": "Separated basis preserved; no Annex Q/result opening", "issuer_fy_evidence": "Direct separated Annex Q, BCRA zero and Other-FI totals on physical page 78", "raw_reconciliation": "FY totals equal complete four-account sets; same set applied to Sep", "q4_decision": "PROMOTE_EXACT_ENTITY_SPECIFIC", "coverage_assets_million_ars": "202982.416", "scope_guardrail": "Same entity, same year, same basis only"},
    {"entity": "Banco de Corrientes S.A.", "entity_code": "00094", "issuer_9m_evidence": "No compatible issuer result opening; Sep regulatory raw available", "issuer_fy_evidence": "Official Annex Q page 130: BCRA income 40,870,153 and all other legs zero", "raw_reconciliation": "FY 511108 exact; same account set applied to Sep", "q4_decision": "PROMOTE_EXACT_ENTITY_SPECIFIC", "coverage_assets_million_ars": "349527.560", "scope_guardrail": "511108 mapping is Corrientes-specific"},
    {"entity": "HSBC Bank Argentina S.A.", "entity_code": "00150", "issuer_9m_evidence": "Separated filing preserved; result opening absent; raw totals available", "issuer_fy_evidence": "Note 26 publishes total active/passive repos with sector financiero only", "raw_reconciliation": "Exact total reconciliation at Sep and Dec", "q4_decision": "KEEP_ND_STRICT", "coverage_assets_million_ars": "0", "scope_guardrail": "Totals and BCRA repo stock cannot allocate BCRA versus Other-FI result legs"},
]
write_csv(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V161.csv", review, review_fields)


source_manifest = read_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V161.csv")
selected_suffixes = {
    "/banco_corrientes_eeff_fy2023.pdf",
    "/bma_9m2023/estado_contable.pdf",
    "/bma_fy2023/estado_contable.pdf",
    "/hsbc_9m2023/estado_contable.pdf",
    "/hsbc_fy2023/estado_contable.pdf",
    "/mariva_9m2023/estado_contable.pdf",
    "/mariva_fy2023/estado_contable.pdf",
}
bundle = []
for row in source_manifest:
    if any(row["relative_path"].endswith(suffix) for suffix in selected_suffixes):
        bundle.append(
            {
                "role": "OFFICIAL_ISSUER_ANALYTIC_SOURCE",
                "path": row["relative_path"],
                "url": row["source_url"],
                "bytes": row["size_bytes"],
                "sha256": row["sha256"],
                "validation": row["format_verification"],
                "analytic_use": "four-leg direct/crosswalk or strict negative control",
            }
        )
for role, path in [
    ("BCRA_RAW_9M_ARCHIVE", REPO / "research" / "ciclo_ajuste" / "inputs" / "bcra" / "2023-09" / "informacion_entidades_financieras_open_data" / "202309d.7z"),
    ("BCRA_RAW_FY_ARCHIVE", REPO / "data" / "fuentes" / "credito_consumo" / "bcra_entidades" / "historico_2023_2026" / "202312d.7z"),
]:
    bundle.append(
        {
            "role": role,
            "path": "/" + path.relative_to(REPO).as_posix(),
            "url": "LOCAL_OFFICIAL_ARCHIVE_ALREADY_CATALOGUED",
            "bytes": str(path.stat().st_size),
            "sha256": sha256(path),
            "validation": "7Z_ARCHIVE_READABLE_ENTITY_BALDET_EXTRACTED",
            "analytic_use": "entity-specific regulatory result accounts and asset controls",
        }
    )
write_csv(HERE / "V161_BANK_ANALYTIC_SOURCE_BUNDLE.csv", bundle)


visual_fields = ["control_id", "artifact", "page", "method", "target", "result", "observation"]
visual = [
    {"control_id": "PV161_01", "artifact": "bma_9m2023/estado_contable.pdf", "page": "54 / printed 130", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q pass income split", "result": "PASS", "observation": "BCRA 29,151,547; Other-FI 329,255"},
    {"control_id": "PV161_02", "artifact": "bma_9m2023/estado_contable.pdf", "page": "55 / printed 131", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q pass expense split", "result": "PASS", "observation": "Other-FI 874,222; BCRA blank/zero"},
    {"control_id": "PV161_03", "artifact": "bma_fy2023/estado_contable.pdf", "page": "65 / printed 203", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q pass income split", "result": "PASS", "observation": "BCRA 79,896,235; Other-FI 574,991"},
    {"control_id": "PV161_04", "artifact": "bma_fy2023/estado_contable.pdf", "page": "66 / printed 204", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q pass expense split", "result": "PASS", "observation": "Other-FI 7,081,885; BCRA blank/zero"},
    {"control_id": "PV161_05", "artifact": "mariva_fy2023/estado_contable.pdf", "page": "77 / printed 189", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q opening identity", "result": "PASS", "observation": "Separated annual Annex Q confirmed"},
    {"control_id": "PV161_06", "artifact": "mariva_fy2023/estado_contable.pdf", "page": "78 / printed 190", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Pass income/expense counterparty split", "result": "PASS", "observation": "Other-FI 27,573,387 income and 13,992 expense; BCRA blank/zero"},
    {"control_id": "PV161_07", "artifact": "hsbc_fy2023/estado_contable.pdf", "page": "36", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Pass result disclosure", "result": "PASS_LIMIT", "observation": "204,724,664 income and 542,204 expense, both sector financiero unsplit"},
    {"control_id": "PV161_08", "artifact": "banco_corrientes_eeff_fy2023.pdf", "page": "130", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q pass four-leg split", "result": "PASS", "observation": "BCRA income 40,870,153; remaining legs zero"},
    {"control_id": "PV161_09", "artifact": "banco_corrientes_eeff_fy2023.pdf", "page": "131", "method": "Poppler render 140 dpi + original-detail visual inspection", "target": "Annex Q continuation/control", "result": "PASS", "observation": "Document continuity confirmed"},
    {"control_id": "TX161_10", "artifact": "mariva_9m2023/estado_contable.pdf", "page": "all 44 physical pages", "method": "pdfplumber full-document term search", "target": "Annex Q/pass result opening", "result": "ABSENT_CONFIRMED", "observation": "Separated basis confirmed; no Annex Q or pass result opening"},
    {"control_id": "TX161_11", "artifact": "hsbc_9m2023/estado_contable.pdf", "page": "full document", "method": "pdfplumber full-document term search", "target": "Pass result counterparty opening", "result": "ABSENT_CONFIRMED", "observation": "No compatible result split; stock disclosure not used as flow"},
]
write_csv(HERE / "V161_PDF_VISUAL_AND_TEXT_CONTROL.csv", visual, visual_fields)


(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V161.md").write_text(
    f"""# Revisión analítica de adjuntos oficiales V161

## Resultado

V161 promueve tres entidades sin flexibilizar la regla de cuatro patas: Banco BMA, Banco Mariva y Banco de Corrientes. El panel estricto pasa de 30 a 33 entidades. El numerador de activos sube de {OLD_NUMERATOR} a {NEW_NUMERATOR} millones de pesos y la cobertura de {old_coverage}% a {STRICT}% (+{STRICT - old_coverage} puntos porcentuales).

## Método

1. Se preservaron y verificaron por SHA-256 los estados oficiales.
2. Se inspeccionaron visualmente las páginas relevantes y se controlaron texto, unidad, período y base individual/separada.
3. Se extrajeron, desde los archivos oficiales BCRA de septiembre y diciembre, sólo las cuentas de resultado de la entidad analizada.
4. El conjunto de cuentas se aceptó únicamente cuando reconciliaba exactamente el Anexo Q de la misma entidad y el mismo ejercicio.
5. Para Mariva y Corrientes, el conjunto validado al cierre anual se trasladó sólo a septiembre de la misma entidad, año y base. No se convirtió en un diccionario universal de etiquetas.
6. Q4 se calculó como FY en moneda homogénea de diciembre menos 9M en moneda homogénea de septiembre multiplicado por el factor congelado {FACTOR}. No se redondearon ni truncaron residuos.

## BMA

Los Anexos Q de septiembre y diciembre publican directamente las cuatro patas. Además, los conjuntos regulatorios de la entidad 00259 coinciden exactamente en ambos cortes. La cuenta 511007 integra ingreso BCRA y la 521007 integra gasto otras entidades financieras en este banco; ese hallazgo es una identidad BMA/Itaú 2023, no una semántica global del número o del rótulo.

## Mariva

El estado intermedio preservado es separado pero no incluye Anexo Q. El anual sí lo incluye: todo el ingreso y gasto por pases corresponde a otras entidades financieras, con patas BCRA en cero. Los totales anuales igualan exactamente la suma de 511027+515034 y 521022+525042. Se usa el mismo conjunto completo en septiembre sólo como puente Mariva 2023.

## Corrientes

El Anexo Q anual oficial asigna 40.870.153 miles de pesos a ingreso BCRA y cero a las otras tres patas. El archivo regulatorio anual contiene exactamente 40.870.153 en 511108 y ninguna otra cuenta de resultado por pases; el mismo conjunto se usa en septiembre sólo para Corrientes 2023.

## HSBC: control negativo

HSBC publica totales exactos de pases activos y pasivos con “el sector financiero”, pero no separa BCRA de otras entidades. El archivo BCRA reproduce los totales, no la apertura. La exposición de stock con el BCRA no identifica la contraparte de los flujos. Por eso HSBC permanece N/D_STRICT aun cuando sus totales Q4 son calculables.

## Resguardos

- La diferencia entre la huella declarada por CNV y el SHA-256 de los bytes servidos se conserva como metadato de archivo; no se interpreta como alteración.
- Activos agregados no sustituyen cuatro patas de resultados.
- Un stock de pases no asigna automáticamente un flujo de intereses.
- Seis pedidos históricos permanecen DRAFT_NOT_SENT; SAF355 sigue 0/5 y ejecución bancaria histórica 0/10.
""",
    encoding="utf-8",
)


(HERE / "README_V161.md").write_text(
    f"""# Checkpoint V161

- Archivo fuente: 577/577 copias locales con hash válido; 30 adjuntos CNV y dos fuentes bancarias oficiales sincronizadas.
- Promociones estrictas: Banco BMA, Banco Mariva y Banco de Corrientes.
- Panel: 33 entidades exactas; activos {NEW_NUMERATOR} / {SYSTEM_ASSETS} millones de pesos; cobertura {STRICT}%.
- BMA tiene cuatro patas directas en 9M y FY y reconciliación regulatoria exacta.
- Mariva y Corrientes usan puentes limitados a la misma entidad, año y base, validados exactamente al cierre anual.
- HSBC conserva totales exactos pero queda N/D_STRICT por falta de separación BCRA/otras entidades.
- No se generalizan códigos o etiquetas; no se usa stock como sustituto de flujo.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""",
    encoding="utf-8",
)
(HERE / "VEREDICTO_V161.md").write_text(
    f"""# Veredicto V161

La sincronización archivística abrió tres cierres analíticos defendibles. Banco BMA publica el desglose completo y lo reconcilia exactamente con sus cuentas regulatorias en septiembre y diciembre. Banco Mariva y Banco de Corrientes no publican una apertura intermedia equivalente, pero sus Anexos Q anuales identifican de manera exacta el conjunto completo de cuentas de la misma entidad; el traslado a septiembre queda explícitamente limitado a 2023, la misma base y la misma entidad. Así, el panel estricto pasa a 33 entidades y {STRICT}% de activos. HSBC demuestra el límite del método: conciliar el total no permite inventar la contraparte. Permanece N/D_STRICT. La red no está cerrada; SAF355 0/5, ejecución histórica 0/10 y solicitudes 0/6 enviadas.
""",
    encoding="utf-8",
)
(HERE / "AUDITORIA_V161.md").write_text(
    f"""# Auditoría V161

- Catálogo maestro y copia local: 577/577; brechas físicas/hash: 0.
- Bundle analítico: {len(bundle)} archivos ({len(selected_suffixes)} estados oficiales + 2 archivos regulatorios BCRA).
- Control documental: {len(visual)} registros; 9 inspecciones visuales de páginas y 2 búsquedas documentales completas.
- Reconciliaciones: BMA {len(bma_cross)} filas; Mariva {len(mariva_cross)}; Corrientes {len(corrientes_cross)}.
- Promociones Q4: 3; entidades exactas: 33; cobertura: {STRICT}%.
- Control negativo: HSBC N/D_STRICT; no incluido en numerador.
- Quiebres preservados: cuenta/etiqueta no universal; stock no flujo; total no contraparte.
- SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0; seis DRAFT_NOT_SENT.
""",
    encoding="utf-8",
)
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V161_A_V162.md").write_text(
    f"""# Handover V161 → V162

## Cerrado en V161

- Banco BMA, Mariva y Corrientes promovidos a Q4 exacto con resguardos entidad-año-base.
- Panel estricto: 33 entidades; cobertura de activos: {STRICT}%.
- HSBC permanece N/D_STRICT: totales exactos, contraparte no separada.
- Archivo fuente V161: 577/577 local y hash-válido.

## Prioridad V162

1. Buscar apertura HSBC BCRA/otras entidades en notas complementarias o salida regulatoria específica; no usar stock.
2. Revisar los otros 24 adjuntos CNV ya preservados para nuevas aperturas, bases y controles negativos.
3. Resolver Banco Rioja: diferencia FY de 158.789 miles y apertura compatible 9M.
4. Retomar Plan SIGEN 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-informe.
5. Mantener SAF355 0/5 y banco histórico 0/10 hasta hallar cuerpos ejecutivos primarios.
6. No enviar solicitudes sin autorización expresa.
""",
    encoding="utf-8",
)


complete_path = AUDIT / "CURRENT_SOURCE_COMPLETENESS_V161.json"
complete = json.loads(complete_path.read_text(encoding="utf-8-sig"))
complete.update(
    {
        "checkpoint": "V161",
        "date": "2026-08-31",
        "state": "SOURCE_ARCHIVE_COMPLETE_THREE_BANK_FOUR_LEG_PROMOTIONS_HSBC_COUNTERPARTY_SPLIT_OPEN",
        "analytical_promotion": "BMA_MARIVA_CORRIENTES_EXACT_HSBC_ND_STRICT",
        "exact_entities": 33,
        "strict_asset_numerator_million_ars": str(NEW_NUMERATOR),
        "system_assets_million_ars": str(SYSTEM_ASSETS),
        "strict_coverage_pct": str(STRICT),
        "strict_coverage_increment_v160_pp": str(STRICT - old_coverage),
        "request_drafts_status": "DRAFT_NOT_SENT",
        "requests_submitted": 0,
        "responses_received": 0,
        "saf355_certifications_located": 0,
        "executed_historical_bank_rows_confirmed": 0,
    }
)
complete_path.write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checkpoint_manifest():
    files = [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold())
        if path.is_file() and path.name != "MANIFEST_V161.json"
    ]
    payload = {
        "checkpoint": "V161",
        "parent_checkpoint": "V160",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 33,
        "strict_coverage_pct": str(STRICT),
        "strict_asset_numerator_million_ars": str(NEW_NUMERATOR),
        "system_assets_million_ars": str(SYSTEM_ASSETS),
        "new_promotions": [bma["entity"], "Banco Mariva S.A.", "Banco de Corrientes S.A."],
        "negative_control": "HSBC Bank Argentina S.A. N/D_STRICT",
        "source_archive": "577/577 physical SHA-valid",
        "closed_network_gate": "NO",
        "saf355_certifications": "0/5",
        "executed_historical_bank_rows": "0/10",
        "requests_submitted": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V161.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def tree(root):
    lines = []
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            (name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold
        )
        base = Path(dirpath)
        lines.extend((base / name).relative_to(root).as_posix() + "/" for name in dirnames)
        lines.extend((base / name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [
    {"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
    for path in iter_files(REPO)
    if path != global_manifest
]
global_payload = {
    "checkpoint": "V161",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": str(STRICT),
    "exact_entities": 33,
    "closed_network_gate": "NO",
    "source_audit": "577 master; 577 physical SHA-valid; BMA, Mariva and Corrientes promoted; HSBC N/D_STRICT",
    "historical_workstream": "Plan SIGEN 2009, Nota 3672/09, SAF355 and bank execution remain open; six drafts not sent",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
temporary = global_manifest.with_suffix(".json.V161tmp")
temporary.write_text(json.dumps(global_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(
    f"V161 BUILD PASS · exact=33 · coverage={STRICT} · bundle={len(bundle)} · controls={len(visual)}"
)
