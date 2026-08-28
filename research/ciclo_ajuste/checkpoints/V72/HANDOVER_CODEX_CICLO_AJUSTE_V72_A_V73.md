# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V72 → ejecutar V73

**Fecha de corte:** 2026-08-28  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V72  
**Próxima:** `V73_CREDICOOP_DYNAMIC_BINARY_AND_BNA_ALTERNATE_9M_COUNTERPARTY_DISCLOSURE`

## Estado congelado

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro = 11.260968% bank assets
BNA_FY_INDIVIDUAL_ANNEX_Q = EXACT_RECOVERED_ANNUAL
BNA_9M_SEPARATED_STATEMENTS_REVIEWED = SUPPORTED_BY_AGN
BNA_9M_AGN_SC_REVIEW_ATTACHMENT = RECOVERED_ARCHIVED_LOCAL
BNA_9M_AGN_CC_REVIEW_ATTACHMENT = RECOVERED_ARCHIVED_LOCAL
BNA_9M_AGN_RESOLUTION = RECOVERED_ARCHIVED_LOCAL
BNA_9M_FULL_SEPARATED_STATEMENT_PAYLOAD = NOT_ESTABLISHED
BNA_9M_REVIEW_SCOPE_ANNEXES = A,B,C,D,H,I,J,L,O,R
BCRA_2023_ANNEX_Q_REPORTING_FREQUENCY = ANNUAL
MANDATORY_9M_ANNEX_Q_GATE = REMOVED
BNA_9M_FOUR_LEG = N/D
CREDICOOP_30_09_2023_PUBLICATION = PRIMARY_ISSUER_INDEX_CONFIRMED
CREDICOOP_30_09_2023_BINARY = NOT_RECOVERED_DYNAMIC_LINK
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Corrección V72 crítica

No buscar "Anexo Q 9M" como obligación regulatoria general. BCRA A7809 (vigencia 30/06/2023) marca A-Q = **Anual**. Un Q 9M sigue siendo utilizable si un emisor efectivamente lo publicó, pero su ausencia en 30/09 no es un gap por sí misma.

SC1 ya fue inspeccionado: es el informe de revisión separado y lista Notas 1-19 + A,B,C,D,H,I,J,L,O,R. No contiene las cifras de cuatro patas buscadas.

## Prioridad V73

1. **Credicoop**: resolver el target dinámico de 30-09-2023 desde endpoint/JS/API/cache/regulador. Una vez recuperado, inspeccionar estados y notas por intereses de pases y contrapartes; no exigir Q.
2. **BNA**: buscar alternativa primaria 9M para el split de pases:
   - estado de resultados/notas del filing separado completo;
   - datos regulatorios BCRA/machine-readable de presentación trimestral;
   - cualquier tabla primaria que distinga BCRA vs otras entidades financieras y preserve ingreso/egreso.
3. **Provincia** y **Ciudad**: mismo criterio, separado/individual 9M.
4. Santander/BBVA sólo si aparece ruta nueva capaz de mejorar el split, no sólo totals.

## Si aparece 9M compatible

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

Exigir cuatro patas de misma base/período. Si sólo aparece total, construir bound explícito o dejar N/D.

## Reglas congeladas

- consolidado = control;
- FY != Q4;
- stock != flow;
- asset share != flow weight;
- producto != sector hogar;
- Q4-2023 != post-10/12 limpio;
- no elevar +7.7 pp a BCRA sin bridge sistémico;
- no modificar HTML.
