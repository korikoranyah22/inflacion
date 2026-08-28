# Handover — Ciclo de ajuste V89 → V90

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **56.3611969759920493658507094411572610848828346690020136002104%**
- exact asset numerator = **54499978.632 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **17**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

Exact entities: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, Ciudad, Galicia, BBVA, Patagonia, Citi, Supervielle, Comafi, Bancor, **Nuevo Banco de Santa Fe**, **Nuevo Banco de Entre Ríos**, **Banco de San Juan**, **Banco de Santa Cruz**.

## V89 promotions

### Nuevo Banco de Santa Fe
Q4: BCRA income **10033348.881166213280720k**; BCRA expense **0**; other-FI income **9965k**; other-FI expense **-5.141784892969824k**.

### Nuevo Banco de Entre Ríos
Q4: BCRA income **18164030.917133067050856k**; BCRA expense **0**; other-FI income **-0.052496854525848k**; other-FI expense **-0.752787539589068k**.

### Banco de San Juan
Q4: BCRA income **42575089.535207602541484k**; BCRA expense **0**; other-FI income **11653.107163000564560k**; other-FI expense **112611.590741463856564k**.

### Banco de Santa Cruz
Q4: BCRA income **4615230.007245434209288k**; the other three strict legs are **0**.

Tiny negative differencing residuals remain preserved and are not clamped.

## Active manual recoveries — process first in V90 if uploaded

### HSBC
Sep individual CNV presentation:
https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572

### BICE
AGN page:
https://www.agn.gob.ar/informes/Informe-209-2023

Target **Informe / separated-condensed candidate**:
https://www.agn.gob.ar/sites/default/files/informes/2023-209-Informe%20Anexo%201%20SC.pdf

Do not substitute `Anexo CC.pdf` consolidated candidate.

## Holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.
- Banco de Santiago del Estero: compatible 2023 separated package not recovered in V89.

## Suggested V90 order
1. Any user-rescued HSBC/BICE PDF.
2. Banco BMA / ex-Itaú individual CNV filing (Sep document id 3119515 if recoverable).
3. Banco Industrial separated 9M.
4. Nuevo Banco del Chaco / Banco de La Pampa where 9M issuer opening can be recovered.
5. Continue entity-by-entity. Never mass-map six-digit BCRA accounts.
