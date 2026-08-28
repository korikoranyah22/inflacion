# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V69 → ejecutar V70

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V69  
**Próxima:** `V70_BNA_9M_BINARY_RECOVERY_AND_PUBLIC_BANK_AQ_EXTRACTION`

## Estado congelado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

BCRA_BANK_ASSETS_DEC2023
= 96,697,695.5 million ARS

STRICT_Q4_FOUR_LEG_EXACT
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

BNA_FY_INDIVIDUAL_ANNEX_Q
= EXACT_RECOVERED
income_BCRA = 766170919k
income_otherFI = 0
expense_BCRA = 0
expense_otherFI = 0

BNA_9M_SEPARATED_SOURCE
= OFFICIAL_AGN_PACKAGE_IDENTIFIED

BNA_9M_BINARY
= NOT_RECOVERED_CURRENT_502

BNA_ASSET_SHARE
= 22.015263%

STRICT_IF_BNA_Q4_EXACT_HYPOTHETICAL
= 33.276231%

PUBLIC_COOP_UNRESOLVED_TARGET_ASSET_FOOTPRINT
= 38.119804%

STRICT_PLUS_ALL_FOUR_IF_EXACT_HYPOTHETICAL
= 49.380772%

CLOSED_PASS_NETWORK
= NOT_ACHIEVED

SYSTEM_INTERBANK_PASS_CANCELLATION
= NOT_IDENTIFIED_COVERAGE_TOO_LOW

SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Hallazgo metodológico nuevo

El FY 2023 oficial de BNA muestra:

```text
INDIVIDUAL:
BCRA income = 766,170,919k
otherFI income = 0

CONSOLIDATED:
BCRA income = 766,170,918k
otherFI income = 3,980,009k
```

No promediar ni restar entre bases. Sólo la fila individual puede entrar al target sistémico.

## Prioridad V70

1. **Banco Nación 9M**:
   - AGN Informe 210/2023 / Actuación 298/2023.
   - recuperar attachment binario por cache, mirror, BNA, BCRA o ruta alternativa.
   - verificar si contiene Anexo Q individual.
   - si aparece, aplicar exclusivamente:
     `Q4 = FY_Dec - 9M_Sep * 1.532908152197`.
2. **Banco Provincia 9M individual**:
   - explotar arquitectura histórica `EEFF_unificado_*` y `Anexo_Q_sep_*`.
3. **Credicoop 9M individual**:
   - recuperar bytes de publicación 30/09/2023.
4. **Banco Ciudad individual/separado**:
   - localizar separado 9M/FY; consolidado sigue control.
5. Luego BBVA y Santander sólo por rutas nuevas.

## Qué NO hacer

- no usar BNA consolidado para completar BNA individual;
- no usar FY como Q4;
- no usar stock de pases como flujo;
- no usar asset shares como flow weights;
- no considerar 49.38% hipotético como red cerrada;
- no reintentar indefinidamente el mismo filing Santander;
- no modificar HTML.

## Gate

Sólo elevar `SYSTEM_INTERBANK_PASS_CANCELLATION` con cobertura near-full/closed, misma base, cuatro patas, moneda homogénea y período compatible.
