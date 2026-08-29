# Ciclo de ajuste — checkpoint V98

V98 is a **source-body / presentation-metadata re-audit checkpoint with no strict promotion**.

- frozen Sep→Dec factor: `1.532908152197492`
- exact entities: `24` (unchanged)
- asset numerator: `57803557.512` million ARS (unchanged)
- system denominator: `96697695.5` million ARS
- strict asset coverage: `59.777595746322620480650441147276358824911189326119979767253088259998915899707248%` (unchanged)
- increment vs V97: `0` percentage points
- closed-network gate: `NO`

Material progress:

1. **Banco CMF**: the historical official ZIPs were already physically preserved. V98 opens them, extracts and separately preserves exact FY-2023 and 9M-2023 **separated** PDFs, validates their SHA-256, renders/inspects the relevant pages, and reconciles pass income/expense totals exactly to raw BCRA. CMF still cannot be promoted because the issuer flow presentation does not split BCRA vs Other-FI; BCRA-only closing stock is not a valid substitute for flow classification.
2. **HSBC**: exact CNV individual presentation numbers are pinned: #3121099 (30/09/2023) and #3163537 (31/12/2023), with the known UUIDs. Attachment bodies remain unrecovered.
3. **Banco de Corrientes**: the exact official FY download endpoint (`documentid=1193`) is identified. The binary still cannot be persisted in this environment.
4. **Columbia** remains analytically solved but physically source-held. **Mariva** remains attachment-body held.
