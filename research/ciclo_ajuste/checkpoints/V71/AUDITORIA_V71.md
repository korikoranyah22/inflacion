# AUDITORIA V71 — REGULATORY ARCHIVE RECOVERY AND 9M SOURCE SCOPE REFINEMENT

## Objetivo

Romper el cuello archivístico de los 9M individuales sin inferir flujos faltantes ni mezclar bases.

## 1. Banco Nación — avance y corrección de scope

La página oficial AGN del Informe 210/2023 confirma que el examen cubrió estados intermedios consolidados condensados y separados condensados al 30/09/2023. V71 resolvió además los filenames exactos detrás de los enlaces: `2023-210-Informe SC 1.pdf` y `2023-210-Informe CC 2.pdf`; ambos retornan 502.

El avance más importante no es numérico sino epistemológico: esos nombres son de **informes** de revisión. Por analogía documental con la nomenclatura histórica de AGN, no debe asumirse que `SC 1` sea el paquete completo de estados separados con Anexo Q. Se corrige el lenguaje heredado `AGN_SEPARATED_PACKAGE_IDENTIFIED` por una formulación más precisa:

```text
BNA_9M_SEPARATED_STATEMENTS_AUDITED = SUPPORTED
BNA_9M_FULL_SEPARATED_STATEMENT_PAYLOAD = NOT_ESTABLISHED
BNA_9M_ANNEX_Q = NOT_RECOVERED
```

El Balance Condensado Sep-2023 y Disciplina de Mercado Sep-2023 del BNA siguen siendo controles primarios, no sustitutos del filing separado.

## 2. Credicoop — existencia primaria confirmada

El índice oficial del emisor lista expresamente `30-09-2023`. Esto reemplaza la dependencia anterior de una calificadora para probar que el estado 9M fue publicado. El link se resuelve dinámicamente y el crawler no expone su ID/binario, por lo cual no se extraen cifras.

```text
CREDICOOP_9M_PRIMARY_PUBLICATION = CONFIRMED_BY_ISSUER_INDEX
CREDICOOP_9M_BINARY = NOT_RECOVERED
CREDICOOP_9M_ANNEX_Q = NOT_INSPECTED
```

## 3. Banco Provincia

Se confirmó en documentación oficial histórica que el repositorio usó la convención `ESF_sep_30092022` para estados separados de septiembre. Esa arquitectura sirve para búsqueda archivística, pero no autoriza a afirmar que exista `ESF_sep_30092023` en una URL análoga. Ningún binario separado 2023 fue recuperado.

## 4. Banco Ciudad

La búsqueda por nomenclatura separada 2023 no produjo un binario primario surfacado. El consolidado 30/09/2023 heredado permanece `CONTROL_ONLY`.

## 5. Cobertura y gates

No se incorpora ninguna entidad exacta Q4.

```text
STRICT_Q4_FOUR_LEG_EXACT_ASSET_COVERAGE = 11.260968%
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Valor de V71

V71 reduce dos falsos positivos de retrieval: (a) no confundir un informe de revisión AGN con el payload completo de estados financieros; (b) no convertir patrones históricos de filename ni IDs dinámicos en documentos 2023 supuestamente recuperados. A cambio, deja dos targets mejor definidos: el filing separado real del BNA y el link dinámico primario 30/09/2023 de Credicoop.
