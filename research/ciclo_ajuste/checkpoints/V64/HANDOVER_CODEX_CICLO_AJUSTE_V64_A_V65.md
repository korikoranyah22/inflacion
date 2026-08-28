# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V64 → ejecutar V65

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V64  
**Próxima iteración:** `V65_BASIS_HARMONIZATION_AND_REMAINING_CLOSED_NETWORK_COVERAGE`

## Estado nuevo que no debe perderse
```text
V64_ICBC_FOUR_LEG_Q4 = IDENTIFIED_EXACT
ICBC_Q4_BCRA_NET_PASS ≈ +199.397 bn ARS
ICBC_Q4_OTHERFI_NET_PASS ≈ -0.902 bn ARS
FULL_FOUR_LEG_Q4_ENTITY_COUNT = 2_DIFFERENT_BASES
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_PRODUCT_PROXY = RETAINED_NOT_STRICT_SECTOR
HOUSEHOLD_FLOW_TO_INSTITUTIONAL_SECTOR_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Qué falsificó/reforzó V64
- ICBC proves a large exact BCRA pass leg at entity level, but it is not a system floor.
- ICBC also has an other-FI expense leg; pass counterparties remain heterogeneous.
- Mortgage/pledged BCRA datasets distinguish human vs legal holders at stock level, so product labels cannot be promoted to 100% household identity.
- No stock-to-interest-flow bridge was inferred.
- No consolidated/individual mixing was allowed.

## Primera acción V65
Read `VEREDICTO_V64.md`, `AUDITORIA_V64.md`, `FOUR_LEG_PASS_PANEL_V64.csv`, `CLOSED_NETWORK_COVERAGE_V64.csv`, `HOUSEHOLD_SECTOR_MAPPING_V64.csv`, then execute the included V65 prompt.
