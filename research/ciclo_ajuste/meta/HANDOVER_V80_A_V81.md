# Handover repo checkpoint V80 -> V81

## Punto de partida
Usar `research/FRONTERA_CICLO_AJUSTE_V80_BCRA_LEGACY_DATE_ENDPOINT_AND_BNA_COMPARATIVE_BACKFILL_GATE.zip` como estado de investigación canónico y `repo/inflacion-backup_sources-v70-patched.zip` como snapshot de repo.

## Nuevos insumos
Los archivos de `inputs/bcra_2023_09/` provienen de la edición septiembre 2023 del Informe sobre Bancos del BCRA. `InfBanc_Anexo.xlsx` es el insumo nuevo más valioso: contiene series y anexos por sistema/grupos; funciona como control regulatorio agregado, pero no reemplaza el gate entidad×cuenta para BNA/Ciudad.

## Reglas que no deben romperse
1. No mezclar consolidado con separado/individual para construir four-leg.
2. No sustituir flujos por stocks de operaciones de pase.
3. No interpretar ausencia visual como cero salvo reconciliación exhaustiva/documentada.
4. Mantener cobertura estricta en 23.543324980273% hasta promover una entidad nueva con evidencia individual compatible.
5. Prioridad: BNA y Ciudad, idealmente vía dataset regulatorio BCRA de septiembre 2023 o EEFF separados completos.
