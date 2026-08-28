# Referencias — Ciclo del ajuste, contrapartes bancarias y hogares · V70

**Corte:** 27-08-2026  
**Estado documental acumulado:** V34–V70  
**Archivo anterior:** `REFERENCIAS_CICLO_AJUSTE_V51.md` queda preservado como snapshot histórico; este archivo lo reemplaza como mapa vigente.

## Contrato de lectura vigente

Nunca identificar automáticamente:

```text
costo soportado por el hogar
!= ingreso bruto del banco
!= utilidad neta bancaria

resultado observado
!= resultado anormal
!= efecto causal neto

stock
!= flujo

producto minorista
!= sector institucional hogar

submuestra interbancaria abierta
!= sistema cerrado
```

Q4-2023 contiene octubre, noviembre y diciembre. Por lo tanto:

```text
Q4_ABNORMALITY = SUPPORTED
POST_10_DEC_SHOCK_ATTRIBUTION = NOT_IDENTIFIED
```

## Claims revocados que no deben reaparecer

Las iteraciones V52–V70 falsificaron o revocaron explícitamente estas formulaciones:

```text
"todo pase = BCRA"
"7,7 pp de pases = BCRA"
"26,83% es un floor BCRA"
"66,2% está estrictamente clasificado como partición conjunta"
"39,37% FX es un floor de valuación"
"[0 ; 2,1 pp] es un techo estricto de hogar"
"stock de pases identifica la contraparte del flujo"
"producto hipotecario/prendario/personal/tarjeta = hogar"
"Macro + Ciudad / otra submuestra abierta prueba cancelación del sistema"
"ganancia bancaria = transferencia desde hogares"
```

Estado vigente:

```text
7_7PP_AS_STRICT_BCRA_FLOOR = REVOKED
IEF_7_7PP_BCRA_SHARE = N/D
STOCK_AS_PASS_FLOW_COUNTERPARTY_PROXY = REJECTED
SUBSET_INTERBANK_NETTING_AS_SYSTEM_TEST = REJECTED
HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
NET_CAUSAL_BANK_BENEFIT = NOT_IDENTIFIED
DELIBERATE_HOUSEHOLD_TO_BANK_COORDINATION = NOT_ESTABLISHED
```

## Base sistémica congelada desde V65

Para agregar entidades sin duplicar grupos ni mezclar perímetros:

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
```

Los estados consolidados sirven como controles de entidad/grupo, pero no se suman al panel sistémico individual.

Fuente de denominador y criterio individual/agregado:

- BCRA · Información de Entidades Financieras, diciembre 2023:  
  https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202312e.pdf

Denominador congelado para diagnóstico de cobertura:

```text
activos de bancos Dic-2023 = 96.697.695,5 millones ARS
```

`asset_share != pass_flow_weight`: el porcentaje de activos mide cobertura documental, no ponderación económica del flujo de pases.

## Pases — fórmula y gate

El Anexo Q puede separar conceptualmente:

```text
income passes BCRA
expense passes BCRA
income passes other financial institutions
expense passes other financial institutions
```

Q4 sólo se reconstruye sobre estados comparables en moneda homogénea:

```text
Q4_DecPesos
= FY_DecPesos - 9M_SepPesos × (IPC_Dec / IPC_Sep)

IPC Sep-2023 = 2304,9
IPC Dec-2023 = 3533,2
factor = 1,532908152197
```

No se ejecuta un test de cancelación sistémica mientras la red permanezca abierta.

## Entidades con Q4 four-leg exacto en base individual

### ICBC Argentina

- 9M 2023, Anexo Q:  
  https://www.icbc.com.ar/wcm/connect/4de3ed09-cb4e-4064-b6a5-0aa3f0bca5fd/Estados%2BFinancieros%2BICBC%2B202309_ESPA%C3%91OL%2BLEGALIZADO.pdf?CVID=oNG1sHj&MOD=AJPERES
- FY 2023, Anexo Q:  
  https://www.icbc.com.ar/wcm/connect/09254af5-2d9a-4742-bec0-bbd0018305d5/Estados%2BFinancieros%2BICBC%2B202312_ESPA%C3%91OL%2BLEGALIZADO.pdf?CVID=oUU1Wae&MOD=AJPERES

Estado: `EXACT_FOUR_LEG_Q4`.

### Banco de Valores

- 9M 2023, filing regulatorio recuperado vía mirror:  
  https://cdn.financialreports.eu/financialreports/media/filings/68513/2023/RNS/68513_rns_2023-11-23_b356ffca-3ad3-4121-b2bc-c9ff8ad7aa0e.pdf
- FY 2023, emisor:  
  https://www.valo.ar/wp-content/uploads/BVSA-2023-Estados-Financieros-con-PDU-e-ICF-Consolidado-Legalizado.pdf

Estado: `EXACT_FOUR_LEG_Q4`.

### Banco Macro

- 9M 2023, estados financieros oficiales:  
  https://www.macro.com.ar/relaciones-inversores/documento/1580934703038/banco_macro_sa_eeff_30-09-2023.pdf
- FY 2023, estados financieros oficiales:  
  https://www.macro.com.ar/relaciones-inversores/documento/1580935557769/eeff_bm_31-12-2023.pdf

Estado: `EXACT_FOUR_LEG_Q4`.

Cobertura estricta acumulada V70:

```text
ICBC + Banco de Valores + Banco Macro
= 11,260968% de activos bancarios
```

La red continúa abierta.

## Entidades con evidencia parcial / bounds

### Galicia

Existe detalle individual parcial de contraparte, pero falta una pata compatible para elevarlo a four-leg exacto. No se usa para cerrar el sistema.

### Santander Argentina

- CNV · metadata de presentaciones:  
  https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/30500008454
- 9M 2023 separado, filing recuperado vía mirror:  
  https://cdn.financialreports.eu/financialreports/media/filings/68743/2023/RNS/68743_rns_2023-11-24_514c3f88-1bff-43e7-9afe-b8e793c5e3e1.pdf
- FY 2023 separado, Anexo Q, filing recuperado vía mirror:  
  https://cdn.financialreports.eu/financialreports/media/filings/68743/2024/RNS/68743_rns_2024-03-06_8a497326-fbc5-4ac4-bb14-21ece6df12e5.pdf

El filing 9M recuperado no incluye Anexo Q, pero Nota 26.1 permite reconstruir el total Q4 de ingresos por pases. El FY abre contraparte. Esto sostiene un **bound de ingreso**, no four-leg Q4 completo. No usar stocks de Nota 7/Anexo P para completar el flujo.

### Supervielle

- 9M 2023:  
  https://content-us-7.content-cms.com/8ba19f21-9a97-4525-8886-f54d823a5cea/dxdam/02/025e5bb4-d630-480e-a03d-397a022080ff/EECC%20Banco%20Supervielle%2030.09.23.pdf
- FY 2023:  
  https://content-us-7.content-cms.com/8ba19f21-9a97-4525-8886-f54d823a5cea/dxdam/08/08afb7e5-b4c1-4396-925e-b66a2f5c13b1/EECC%20Banco%20Supervielle%2031.12.2023.pdf

Q4 total de pases puede reconstruirse; la contraparte queda acotada por bound, no identificada puntualmente en las cuatro patas.

## Bancos públicos/cooperativos — controles FY y retrieval pendiente

### Banco Nación

- FY 2023, Memoria y Estados Financieros, contiene Anexo Q individual y consolidado:  
  https://www.bna.com.ar/Downloads/Institucional_MemoriayBalances_Memoria%202023%20Ingles.pdf
- AGN · Informe 210/2023 / Actuación 298/2023:  
  https://www.agn.gob.ar/informes/Informe-210-2023
- BNA · Balance Condensado Sep-2023:  
  https://www.bna.com.ar/Downloads/Institucional_MemoriayBalances_BALANCE%20CONDENSADO%20SEPT%202023.pdf

El Balance Condensado de septiembre es primario, pero incluye filiales/subsidiarias/entes estructurados y no contiene Anexo Q. Es `CONSOLIDATED_INCLUSIVE_CONTROL_ONLY`; no se resta del FY individual. El paquete 9M separado está identificado por AGN pero su attachment no quedó recuperado en V70.

### Banco Provincia

- FY 2023 oficial:  
  https://www.bancoprovincia.com.ar/CDN/Get/EEFF_unificado_31122023
- Disciplina de Mercado Sep-2023:  
  https://www.bancoprovincia.com.ar/CDN/Get/Disciplina_de_Mercado_septiembre_2023

El FY tiene Anexo Q separado exacto. El documento de septiembre recuperado no es el Anexo Q separado requerido para aislar Q4.

### Banco Credicoop

- FY 2023 / Anexo Q separado:  
  https://www.bancocredicoop.coop/api/descargas/descargar.php?descarga=819

El 9M primario compatible no fue recuperado al cierre V70.

### Banco Ciudad

- 9M 2023 consolidado:  
  https://www.bancociudad.com.ar/cms/recursos/institucional/carpetarecurso/Balances%20Trimestrales/EstadosFinancieros/2023.09_-_EEFF_consolidados.pdf

Sirve como control consolidado; no sustituye el estado individual/separado.

## Mapping producto → sector hogar

Fuentes regulatorias usadas para auditar que producto no equivale automáticamente a sector institucional:

- BCRA · Préstamos y otros activos de las entidades financieras:  
  https://www.bcra.gob.ar/prestamos-y-otros-activos-de-las-entidades-financieras/
- BCRA · Boletín Estadístico, apertura por tipo de titular:  
  https://www7.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/BoletinEstadistico/boldat202505.pdf
- BCRA · notas metodológicas:  
  https://web2.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/bolmetes.pdf

Hipotecarios/prendarios pueden incluir personas humanas y jurídicas. Por lo tanto:

```text
HOUSEHOLD_PRODUCT_PROXY
= SUPPORTED_DIRECT_CONTRACT_CANDIDATE_NOT_SECTOR_IDENTITY

HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE
= NOT_IDENTIFIED

HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE
= N/D
```

## Estado sintético V70

```text
ABNORMAL_POSITIVE_BANK_RESULT = SUPPORTED_DESCRIPTIVELY
ABNORMAL_COMPONENT_BRIDGE = SUPPORTED
COMPONENT_LEVEL_MECHANISMS = SUPPORTED
NET_CAUSAL_BANK_BENEFIT = NOT_IDENTIFIED

STRICT_Q4_FOUR_LEG_EXACT_ASSET_COVERAGE = 11.260968%
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D

HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
DELIBERATE_HOUSEHOLD_TO_BANK_COORDINATION = NOT_ESTABLISHED
```

## Archivos reproducibles incluidos en el repositorio

- `AUDITORIA_CICLO_AJUSTE_V70.md`
- `VEREDICTO_CICLO_AJUSTE_V70.md`
- `v70/EVIDENCE_LEDGER_CICLO_AJUSTE_V70.csv`
- `v70/FOUR_LEG_PASS_PANEL_V70.csv`
- `v70/CLOSED_NETWORK_COVERAGE_V70.csv`
- `v70/BNA_9M_BINARY_RECOVERY_V70.csv`
- `v70/HOUSEHOLD_SECTOR_MAPPING_V70.csv`

Estos archivos son auditoría/derivados del proyecto; no reemplazan las fuentes primarias listadas arriba.
