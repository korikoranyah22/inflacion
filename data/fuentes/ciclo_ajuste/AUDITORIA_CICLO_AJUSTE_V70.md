# AUDITORIA V70 — BNA 9M SOURCE AUDIT AND PUBLIC BANK RETRIEVAL GATE

## Objetivo

Recuperar fuentes 9M individuales compatibles para Banco Nación y bancos públicos/cooperativos de alto peso, sin relajar la base sistémica.

## Banco Nación

### 1. AGN

La página oficial del Informe 210/2023 confirma explícitamente que el paquete al 30/09/2023 contiene estados intermedios **consolidados condensados y separados condensados**. La fuente objetivo, por lo tanto, existe.

Durante V70 los dos attachments oficiales (`Informe` y `Anexo`) continúan devolviendo HTTP 502. El Anexo Q del 9M separado no pudo inspeccionarse.

### 2. BNA issuer — Balance Condensado Sept 2023

Se recuperó un PDF primario oficial de una página correspondiente a los nueve meses finalizados el 30/09/2023. Incluye, entre otros, `OPERACIONES DE PASE = 536,910,181k` en activo y `302k` en pasivo, junto con resultados acumulados.

Pero el propio documento declara que los estados incluyen casas del país, filiales operativas del exterior, subsidiarias y entes estructurados. Además, el PDF no contiene Anexo Q.

Veredicto de base:

```text
BNA_9M_ISSUER_CONDENSED
= PRIMARY_RECOVERED
= CONSOLIDATED_INCLUSIVE_CONTROL_ONLY
= NOT_ELIGIBLE_FOR_INDIVIDUAL_Q4_BRIDGE
```

No se resta este documento del FY individual.

## Banco Provincia

Se recuperó la publicación oficial `Disciplina de Mercado — septiembre 2023`. Confirma información con fecha 30/09/2023 y remite al repositorio de Estados Contables. No contiene el Anexo Q separado requerido. FY exacto permanece como control.

## Credicoop

Se mantiene FY exacto. Evidencia secundaria localizada confirma análisis basado en EEFF a 30/09/2023, pero no se obtuvo el binario primario ni Anexo Q; no se extraen números.

## Banco Ciudad

Se recuperó/localizó el PDF oficial consolidado 30/09/2023. Queda explícitamente fuera del panel estricto hasta recuperar el separado/individual.

## Cobertura

No se incorpora ninguna nueva entidad exacta Q4.

```text
STRICT_Q4_FOUR_LEG_EXACT_ASSET_COVERAGE
= 11.260968%
```

Sigue siendo una red abierta.

## Gates

```text
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Valor de V70

V70 cierra una falsa vía de solución: el `Balance Condensado Sept 2023` del BNA parece a primera vista el 9M faltante, pero no es compatible con el panel individual y no contiene Anexo Q. La investigación debe seguir por el attachment separado AGN/BCRA/BNA regulatorio, no por el resumen consolidado del emisor.
