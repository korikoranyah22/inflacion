# AUDITORIA V67 — Large-bank 9M retrieval and coverage scale-up

## 1. Gate de base

Se mantuvo:

```text
SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
```

Macro fue elevado sólo porque se recuperó un par 9M/FY **separado** compatible. El antiguo control consolidado permanece únicamente como evidencia histórica/control.

## 2. Validación de que el bloque Macro es separado

El índice del 3T23 distingue explícitamente `Estados Financieros intermedios separados condensados` y `Anexos separados`. El informe de revisión del mismo archivo declara que revisó los estados separados de Banco Macro al 30/09/2023. El FY contiene notas y auditoría de estados financieros separados y el Anexo Q utilizado está dentro de ese bloque.

## 3. Inputs Macro

```text
factor Sep→Dic = 1.532908152197492

9M 2023
income BCRA      73,509,754
expense BCRA              0
income otherFI       42,130
expense otherFI   7,281,804

FY 2023
income BCRA     174,358,904
expense BCRA              0
income otherFI    5,794,175
expense otherFI  13,664,897
```

En ambos Anexo Q, bajo `egresos por operaciones de pase`, la única sublínea es `Otras entidades financieras`; no se inventó una sublínea BCRA faltante. Se registra BCRA expense = 0 por estructura explícita y consistente de la tabla.

## 4. Q4 homogéneo Macro

```text
income BCRA      = 61675202.827368
expense BCRA     = 0
income otherFI   = 5729593.579548
expense otherFI  = 2502560.285696
net BCRA         = 61675202.827368
net otherFI      = 3227033.293852
```

Calidad: `EXACT_FROM_OFFICIAL_9M_AND_FY_HOMOGENEOUS_DIFFERENCING`.

## 5. Cobertura

BCRA Dic-2023:

```text
Macro assets = 5,851,533.4 million ARS
bank denominator = 96,697,695.5 million ARS
Macro share = 6.051368%

strict exact V67 assets = 10889096.4 million ARS
strict exact V67 coverage = 11.260968%
```

No se usó la participación de activos para ponderar, proyectar ni imputar pases.

## 6. Test de red abierta

```text
ICBC + Banco Valores exact net otherFI
= -1,058,668.831 thousand ARS

+ Banco Macro exact
= 2168364.462536 thousand ARS
```

El cambio de signo se conserva como test de sensibilidad de cobertura, no como resultado sistémico.

## 7. Santander

La fuente primaria oficial de accionistas publica links 3T23 y 4T23. Los nombres de archivo confirman bloques consolidados y separados. El fetch del entorno devuelve `Unicode decoding error`, por lo que:

```text
SANTANDER_PRIMARY_PAIR = LOCATED
SANTANDER_SEPARATED_ANNEX_Q_VALUES = NOT_EXTRACTED
SANTANDER_Q4_FOUR_LEG = N/D
```

No se usó el contenido consolidado indexado por terceros para reemplazar la pata individual requerida.

## 8. Retrieval sin avance numérico

- Provincia: FY exacto, 9M compatible aún no extraído.
- Credicoop: FY exacto, 9M compatible aún no extraído.
- Nación: existencia documental separada conocida, Anexo Q pair no extraído.
- Ciudad: individual/separado pendiente.
- BBVA: publicación trimestral confirmada, par individual no recuperado en esta iteración.

## 9. Gates preservados

```text
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```
