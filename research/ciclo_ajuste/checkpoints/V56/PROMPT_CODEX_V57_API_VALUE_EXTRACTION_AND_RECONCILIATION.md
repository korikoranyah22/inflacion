# PROMPT CODEX V57 — API value extraction + reconciliation

## Base

Usar V56 como base. No modificar HTML. No reabrir V34–V55 salvo auditoría puntual.

## Hallazgo congelado V56

Los IDs 1150–1162 y 1183–1192 sobreviven en el catálogo oficial moderno del BCRA como series mensuales DIN1. Esto soporta continuidad de **serie publicada**, no identidad exacta de cuenta NIIF.

## Misión

1. Ejecutar `fetch_bcra_v4_values.py` en un entorno con red o materializar `din1_ser.txt`.
2. Guardar bytes crudos y SHA256 antes de parsear.
3. Recuperar Sep–Dic 2023 para los 23 IDs.
4. Verificar cobertura de cada ID; si la API no expone alguno, documentar `API_SERIES_NOT_EXPOSED` y usar DIN1.
5. Reconciliar primero nominalmente, luego contra los targets congelados Q4-2023.
6. Buscar el bridge oficial SISCEN/NIIF/relaciones conceptuales para evitar empalmes por nombre.

## Gates

- `stock != flow`
- `published series ID continuity != underlying account identity`
- `component gross result != bank net profit`
- `counterparty != accounting mode`
- `household contract existence != household aggregate share`
- no asignar sector por stock si falta flujo devengado sectorial

## Targets congelados

```text
securities +7.3 pp
interest income +2.1 pp
CER -0.2 pp
FX +11.3 pp
passes +7.7 pp
```

## Output mínimo

- RAW_API_MANIFEST_V57.csv
- MONTHLY_SUBACCOUNT_VALUES_2023_V57.csv
- NOMINAL_RECONCILIATION_V57.csv
- PP_TARGET_RECONCILIATION_V57.csv
- ACCOUNT_MAPPING_NIIF_V57.csv
- COUNTERPARTY_UPDATE_V57.csv
- AUDITORIA_V57.md
- VEREDICTO_V57.md
- EVIDENCE_LEDGER_CICLO_AJUSTE_V57.csv
- README_V57.md
- MANIFEST_V57.json
- QA script
