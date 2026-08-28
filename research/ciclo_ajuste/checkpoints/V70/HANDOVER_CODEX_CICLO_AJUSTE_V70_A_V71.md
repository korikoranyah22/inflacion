# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V70 → ejecutar V71

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V70  
**Próxima:** `V71_REGULATORY_ARCHIVE_RECOVERY_AND_PUBLIC_BANK_9M_AQ`

## Estado congelado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

STRICT_Q4_FOUR_LEG_EXACT
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

BNA_FY_INDIVIDUAL_ANNEX_Q
= EXACT_RECOVERED

BNA_9M_AGN_SEPARATED_PACKAGE
= OFFICIAL_SOURCE_IDENTIFIED

BNA_9M_AGN_ATTACHMENTS
= HTTP_502_CURRENT_ROUTE

BNA_9M_ISSUER_CONDENSED
= PRIMARY_RECOVERED
= CONSOLIDATED_INCLUSIVE_CONTROL_ONLY
= NO_ANNEX_Q

BNA_Q4_FOUR_LEG
= N/D

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

## Hallazgo crítico V70

No usar `BALANCE CONDENSADO SEPT 2023.pdf` de BNA para cerrar Q4 individual. La fuente es primaria y 9M, pero declara inclusión de filiales del exterior, subsidiarias y entes estructurados y no contiene Anexo Q. Es `CONTROL_ONLY`.

## Prioridad V71

1. Recuperar los binarios AGN/BNA 9M **separados** mediante:
   - variantes de path/encoding del attachment;
   - mirrors/cache/Wayback si disponible;
   - copia BCRA/regulatoria;
   - repositorios institucionales de BNA;
   - índices de documentos por nombre/hash.
2. Provincia:
   - usar el documento oficial Sep-2023 ya recuperado para enumerar enlaces del repositorio de EEFF;
   - localizar `Anexo_Q_sep` o paquete unificado 30/09/2023.
3. Ciudad:
   - partir del path oficial consolidado 2023.09 y enumerar nombres separados/individuales del mismo directorio.
4. Credicoop:
   - recuperar primary 30/09/2023 por índice de descargas, regulador o mirror.
5. Sólo después: BBVA/Santander.

## Reglas congeladas

- consolidado = control, no sumable;
- FY != Q4;
- stock != flow;
- asset share != flow weight;
- producto != sector hogar;
- Q4-2023 != post-10/12 limpio;
- no elevar IEF +7.7 pp BCRA share sin bridge sistémico;
- no modificar HTML.
