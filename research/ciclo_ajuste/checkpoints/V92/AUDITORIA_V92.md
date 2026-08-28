# Auditoría V92 — Nuevo Banco del Chaco

## 1. Scope

V92 processes the next autonomous target from the V91 handover: **Nuevo Banco del Chaco S.A.**

## 2. Primary official issuer evidence

The official Provincia del Chaco bulletin publishes NBCH's **separated** FY-2023 Annex Q. It reports pass income of **27,742,167k ARS**, split into **27,741,649k BCRA** and **518k other financial institutions**. The separated interest-expense opening has **no pass-expense line**.

## 3. Same-entity BCRA raw crosswalk

BCRA entity `00311` Dec raw matches the issuer FY opening exactly on the income legs: `511108=27,741,649k`, `511027=518k`; no nonzero pass-expense account is present. This validates the identity **for NBCH only**.

Sep raw for the same entity is `511108=10,833,268k`, `511027=338k`, again with no nonzero pass-expense result account. No six-digit account meaning is generalized to any other bank.

## 4. Q4 homogeneous four legs

Frozen Sep→Dec factor: **1.532908152197492**.

- BCRA income: **11135244.167859780236144k**
- BCRA expense: **0k**
- other-FI income: **-0.122955442752296k**
- other-FI expense: **0k**

The **-0.122955442752296k** other-FI differencing residual is preserved exactly and not clamped.

## 5. Promotion and coverage

**PROMOTE Nuevo Banco del Chaco S.A.** Asset added: **344934.073m ARS**.

- V91 numerator: **56003491.668m ARS**
- V92 numerator: **56348425.741m ARS**
- denominator: **96697695.5m ARS**
- strict coverage: **58.272770048589213793621379529153308519125980618638424532051024938851826101688225%**
- increment vs V91: **0.356713850538454662551911591316051580567398320262968417897818464556893188835095 pp**
- exact entities: **20**
- gate: **NO** — majority asset coverage does not prove a closed counterparty network.

## 6. Next

Autonomous priority becomes **Banco de La Pampa S.E.M.** HSBC and Banco BMA remain manual-recovery targets; BNA, Santander and Hipotecario remain under their entity-specific holds.
