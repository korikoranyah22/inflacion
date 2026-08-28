# VEREDICTO V65 — Basis harmonization and individual-network gate

## Estado cerrado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

CONSOLIDATED_GROUP_FILINGS_FOR_SYSTEM_PANEL
= CONTROL_ONLY

BCRA_BANK_ASSETS_DEC2023
= 96,697,695.5 million ARS

STRICT_Q4_FOUR_LEG_EXACT_INDIVIDUAL_COVERAGE
= 4.101042% of bank assets
= ICBC only

INDIVIDUAL_Q4_COUNTERPARTY_DETAIL_ASSET_FOOTPRINT
= 13.070316%
= ICBC + Galicia
= OPEN_SUBSET / GALICIA FOUR-LEG INCOMPLETE

BAPRO_FY2023_SEPARATE_FOUR_LEG
= IDENTIFIED_EXACT
BAPRO_Q4_FOUR_LEG
= N/D_OFFICIAL_9M_NOT_RETRIEVED

CREDICOOP_FY2023_SEPARATE_FOUR_LEG
= IDENTIFIED_EXACT
CREDICOOP_Q4_FOUR_LEG
= N/D_9M_COMPATIBLE_PDF_NOT_RETRIEVED

CLOSED_PASS_NETWORK
= NOT_ACHIEVED

SYSTEM_INTERBANK_PASS_CANCELLATION
= NOT_IDENTIFIED_COVERAGE_TOO_LOW

SYSTEM_BCRA_NET_PASS_FLOW
= N/D

SYSTEM_INTERBANK_NET_PASS_FLOW
= N/D

IEF_7_7PP_BCRA_SHARE
= N/D

HOUSEHOLD_ORIGINATION_HOLDER_DETAIL
= AVAILABLE_IN_BCRA_LENDING_STATISTICS

HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE
= NOT_IDENTIFIED

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED

HTML_MODIFICATION
= FORBIDDEN
```

## 1. V65 resuelve el problema de base, no el de cobertura

El BCRA publica información individual por entidad y agregados institucionales a partir del régimen informativo. También documenta neteos específicos para evitar duplicidades en indicadores agregados. Por eso el panel sistémico estricto queda fijado como **entidad individual regulatoria**, con neteos del sistema documentados explícitamente.

Consecuencia: Ciudad sigue siendo una observación Q4 exacta válida a nivel entidad/grupo, pero su filing consolidado deja de ser sumable al panel sistémico estricto junto con ICBC/Galicia. Lo mismo vale para controles consolidados de Macro, Santander, BBVA, Supervielle y BNA hasta recuperar base individual compatible.

Esto reduce el conteo estricto de entidades Q4 exactas de dos bases distintas a **una entidad elegible: ICBC**. Es una pérdida de cobertura aparente y una mejora de identificación real.

## 2. Por primera vez existe un denominador oficial de cobertura

Bancos, Dic-2023:

```text
Activos = 96,697,695.5 million ARS
Depósitos = 62,483,328.1 million ARS
Cantidad de bancos = 63
```

Con ese denominador:

```text
ICBC exact full-four-leg Q4
= 4.101042% de activos bancarios

ICBC + Galicia, ambos base individual con detalle otherFI Q4
= 13.070316% de activos bancarios
```

El segundo número **no** es cobertura full-four-leg: Galicia sigue sin expense_BCRA. Ambos porcentajes son sólo diagnósticos de retrieval. No se usan para ponderar ni extrapolar flujos de pases.

## 3. Primer subset interbancario armonizado

Sobre base individual compatible:

```text
ICBC + Galicia Q4-2023
otherFI income  = 6,192,393.115 thousand ARS
otherFI expense = 2,366,000.017 thousand ARS
otherFI net     = 3,826,393.098 thousand ARS
asset footprint = 13.070316%
```

Es un avance respecto de V64 porque ya no mezcla consolidado e individual. Pero sigue siendo una red abierta: **no** prueba cancelación interbancaria del sistema.

## 4. Banco Provincia — FY exacto, Q4 todavía no

Anexo Q separado FY 2023:

```text
income BCRA    = 1,040,489,497 thousand ARS
expense BCRA   = 0
income otherFI = 0
expense otherFI= 2,428 thousand ARS
```

La contraparte anual queda identificada exactamente. Sin 9M individual compatible no puede restarse para obtener Q4; el FY no se usa como sustituto.

## 5. Credicoop — FY exacto, Q4 todavía no

Anexo Q separado FY 2023:

```text
income BCRA    = 180,887,922 thousand ARS
expense BCRA   = 0
income otherFI = 0
expense otherFI= 0
```

La publicación 9M fue localizada como existencia documental, pero el PDF compatible no quedó recuperado. Por lo tanto Q4 permanece N/D.

## 6. Hogares: más sector, todavía sin puente contable

El BCRA ofrece estadísticas de préstamos por línea y por tipo de titular, incluyendo montos operados. Esto mejora la evidencia de que existe una dimensión sectorial explícita en datos de originación/operaciones. Sin embargo, no identifica cómo se distribuye el **interés devengado del Anexo Q** entre personas humanas y jurídicas.

No se hizo:
- stock share → interest-flow share;
- origination share → accrued-interest share;
- product name → household sector.

Por eso el punto sistémico de flujo hogar sigue `N/D`.

## Implicancia causal

V65 elimina un cuello metodológico pero hace visible que la cobertura compatible todavía es demasiado baja. El +7,7 pp de pases del IEF no puede repartirse entre BCRA e interbancario con rigor. El próximo trabajo no es reinterpretar el resultado: es recuperar **Anexo Q individual 9M/FY** de entidades grandes hasta que el numerador tenga cobertura materialmente cerrada.
