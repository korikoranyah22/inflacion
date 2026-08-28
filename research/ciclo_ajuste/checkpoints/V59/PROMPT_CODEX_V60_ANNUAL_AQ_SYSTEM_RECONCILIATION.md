# PROMPT CODEX V60 — Annual A-Q system reconciliation / household-flow gate

## Base congelada V59
No modificar HTML.

```text
IEF_MFIR_COMPONENT_FORMULA = EXACT_WITH_ROUNDING
P24_BROAD_INTEREST_TO_IEF_INTEREST_DIRECT_MAPPING = REJECTED
POST_NIIF_BROAD_INTEREST_COMMINGLING = STRONG_SUPPORT
A_Q_ANNUAL_SUBACCOUNT_SCHEMA = STRONG_SUPPORT
SYSTEM_Q3_Q4_POSITIVE_FLOW_RECONCILIATION = NOT_FULLY_IDENTIFIED
PASSES_DIRECT_BCRA = 7.7 pp = 26.83%
UNRESOLVED_COUNTERPARTY = 21.0 pp = 73.17%
HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
```

## Por qué V60 cambia la frecuencia
Anexo Q es anual. El Informe sobre Bancos diciembre 2023 publica para 2023 anual, en % del activo neteado:

- margen financiero 30,8
- ingresos por intereses 13,0
- CER/CVS 5,4
- diferencias de cotización 8,0
- títulos 28,1
- pases 9,1
- egresos por intereses -32,9
- otros financieros 0,1
- resultado monetario -14,1
- ROA 5,4

Esto crea por primera vez un target de frecuencia compatible con A-Q.

## Misión
1. Materializar el dataset abierto de entidades financieras correspondiente a dic-2023 (.7z/.txt) o, si no es posible, los Anexos Q anuales 2023 de entidades con cobertura sistémica suficiente.
2. Agregar **flujos anuales A-Q** por subcuenta, preservando entidad y consolidación para evitar doble conteo.
3. Construir una bridge table desde A-Q hacia las líneas anuales del Informe sobre Bancos:
   - conventional interest;
   - CER/CVS;
   - passes;
   - securities incl. ORI/FVTPL;
   - FX/derivatives;
   - other financial.
4. Exigir que la fórmula reproduzca simultáneamente al menos tres líneas positivas y dos negativas usando un único activo neteado medio/denominador anual.
5. Recién después agregar interés de productos household-like (`0301050600`, `0301050700`, etc.) y evaluar si puede construirse un bound sistémico anual.
6. No proyectar automáticamente ese bound anual a Q4. Crear un bridge de frecuencia separado si se intenta.

## Gates
- no stock × tasa;
- no extrapolar BNA al sistema;
- no confundir producto con sector institucional sin caveat;
- no usar A-Q anual para Q3/Q4 directamente;
- no asignar `títulos públicos = Tesoro` sin issuer gate;
- no convertir pases BCRA en taxpayer identity;
- no residual = componente identificado;
- no hashes inventados;
- no doble conteo entre consolidado/individual.

## Outputs
- RAW_ENTITY_2023_MANIFEST_V60.csv
- AQ_SYSTEM_AGGREGATE_2023_V60.csv
- AQ_TO_IEF_ANNUAL_BRIDGE_V60.csv
- HOUSEHOLD_LIKE_INTEREST_ANNUAL_V60.csv
- SECURITIES_PUBLIC_ISSUER_GATE_V60.csv
- COUNTERPARTY_UPDATE_V60.csv
- AUDITORIA_V60.md
- VEREDICTO_V60.md
- EVIDENCE_LEDGER_CICLO_AJUSTE_V60.csv
- README_V60.md
- MANIFEST_V60.json
- QA
