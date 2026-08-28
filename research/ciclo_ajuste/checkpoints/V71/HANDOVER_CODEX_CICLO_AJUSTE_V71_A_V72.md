# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V71 → ejecutar V72

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V71  
**Próxima:** `V72_DYNAMIC_ISSUER_ENDPOINT_RECOVERY_AND_BNA_REGULATORY_STATEMENT_SEARCH`

## Estado congelado

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro = 11.260968% bank assets
BNA_FY_INDIVIDUAL_ANNEX_Q = EXACT_RECOVERED
BNA_9M_SEPARATED_STATEMENTS_AUDITED = SUPPORTED_BY_AGN
BNA_9M_AGN_SC_REVIEW_ATTACHMENT = EXACT_FILENAME_IDENTIFIED_HTTP_502
BNA_9M_FULL_SEPARATED_STATEMENT_PAYLOAD = NOT_ESTABLISHED
BNA_9M_ANNEX_Q = NOT_RECOVERED
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

## Corrección V71 crítica

No llamar más `AGN_SEPARATED_PACKAGE_IDENTIFIED` como si el attachment inaccesible fuera necesariamente el juego completo de estados financieros. AGN prueba que los estados separados fueron revisados; el link `2023-210-Informe SC 1.pdf` parece un **informe de revisión**, no un payload completo probado.

## Prioridad V72

1. **Credicoop**: resolver el link dinámico del `30-09-2023` desde HTML/JS/API/caché/regulador. Es el target con existencia primaria más clara. No adivinar `descarga=`.
2. **BNA**: buscar los estados separados reales 30/09/2023 en rutas BNA/BCRA/regulatorias; el PDF AGN de revisión es secundario al target contable. Usar nombres/frases internas de estados 2024/2025 para localizar versiones 2023 archivadas, sin fabricar URLs.
3. **Provincia**: enumerar índice/repo 2023; usar `ESF_sep_30092022` sólo como patrón de búsqueda, nunca como prueba de `ESF_sep_30092023`.
4. **Ciudad**: recuperar separado/individual 30/09/2023 y FY compatible.
5. Luego Santander/BBVA sólo si aparece ruta nueva.

## Si aparece 9M compatible

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

Exigir cuatro patas de misma base/período.

## Reglas congeladas

- consolidado = control;
- FY != Q4;
- stock != flow;
- asset share != flow weight;
- producto != sector hogar;
- Q4-2023 != post-10/12 limpio;
- no elevar +7.7 pp a BCRA sin bridge sistémico;
- no modificar HTML.
