# AUDITORÍA V79

## 1. BNA basis divergence is now explicit
The official BNA FY-2023 Annex Q gives **different pass counterparty flows by basis**:

| Basis | BCRA income | otherFI income | BCRA expense | otherFI expense |
|---|---:|---:|---:|---:|
| Separated / individual | 766,170,919 | 0 | 0 | 0 |
| Consolidated control | 766,170,918 | 3,980,009 | 0 | 0 |

The ~3.98bn-thousand-ARS otherFI income appears only in consolidation. This directly validates the project's hard basis gate: a consolidated 9M observation cannot be combined with a separated FY observation to manufacture strict Q4.

## 2. BNA 9M source status
The official September-2023 BNA summary is genuine and period-correct, but only exposes a pass **stock** (536,910,181k) and aggregate interest income/expense. It does not expose the required four pass-interest legs. AGN proves the full separated 9M package existed, but its public attachments remain review reports only.

Result: **no BNA promotion**.

## 3. BCRA archive route upgraded from hypothesis to scoped target
The BCRA explicitly states that its monthly entity publication comes from regulatory submissions and that the complete entity data are offered as an open-data `.7z` containing TXT files. Its data catalog gives monthly coverage **07/2021–06/2025**, so **2023-09 is definitely in scope**.

The exact dynamic download endpoint is still unresolved. Therefore the correct status is **SCOPE_CONFIRMED_ENDPOINT_UNRESOLVED**, not recovered.

## 4. Banco Ciudad annual control revalidated
The official 2023 annual consolidated Annex Q reports:
- pass-income otherFI = **469,990,158k**
- pass-expense otherFI = **791,821k**
- BCRA pass legs = 0

This confirms the inherited consolidated Q4 control bridge. But the annual audit text says a separate report on separated statements was issued, while the accessible annual Annex Q is consolidated. Because BNA demonstrates that consolidation can materially alter pass counterparty flows, Ciudad remains control-only.

## 5. Coverage / network verdict
Strict exact Q4 four-leg asset coverage remains **23.543324980273%**. No entity is promoted in V79.

Closed-system cancellation remains **NOT TESTABLE** at this coverage.
