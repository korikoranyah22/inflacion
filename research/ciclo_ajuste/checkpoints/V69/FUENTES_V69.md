# FUENTES V69

## Jerarquía
1. BCRA / estados regulatorios oficiales.
2. Estados financieros auditados / issuer-official.
3. AGN / CNV para localizar y validar presentaciones.
4. Fuentes secundarias sólo como localizador.

## Banco de la Nación Argentina

- BNA — Memoria y Estados Financieros 2023 (versión inglesa, issuer official):  
  https://www.bna.com.ar/Downloads/Institucional_MemoriayBalances_Memoria%202023%20Ingles.pdf
  - `SCHEDULE Q — INDIVIDUAL`: FY-2023 income por pases BCRA = 766,170,919 (miles ARS); otherFI = 0; pass expense = 0.
  - El mismo documento contiene `SCHEDULE Q — CONSOLIDATED`, donde otherFI income = 3,980,009 (miles ARS). Se conserva sólo como control de sensibilidad de base.

- AGN — Informe 210/2023, Actuación 298/2023:
  https://www.agn.gob.ar/informes/Informe-210-2023
  - Identifica estados financieros intermedios consolidados condensados y separados condensados por 01/01/2023–30/09/2023.
  - Attachment identificado: `2023-210-Informe CC 2.pdf`; en la recuperación V69 devuelve 502.
  - Attachment identificado: `2023-210-Informe SC 1.pdf`; en la recuperación V69 devuelve 502.
  - No se extrae ningún valor de Anexo Q 9M.

## BCRA — cobertura por activos diciembre 2023

- Entidades financieras — diciembre 2023:
  https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202312e.pdf

Valores usados sólo como diagnóstico de cobertura:
- Banco Nación: 21,288,252.0 millones ARS.
- Banco Provincia: 8,682,679.8 millones ARS.
- Credicoop: 3,194,076.5 millones ARS.
- Banco Ciudad: 3,695,963.4 millones ARS.
- Sistema bancos: 96,697,695.5 millones ARS.

`asset_share != pass_flow_weight`.

## Banco Provincia

- FY 2023 oficial:
  https://www.bancoprovincia.com.ar/CDN/Get/EEFF_unificado_31122023
- Arquitectura histórica oficial:
  https://www.bancoprovincia.com.ar/Content/EEFF_unificado_30092021.pdf
- Ejemplo de Anexo Q separado oficial:
  https://www.bancoprovincia.com.ar/CDN/Get/Anexo_Q_sep_31122022

La arquitectura permite documentar que existen paquetes intermedios/separados, pero V69 no recupera un `Anexo_Q_sep_30092023` ni un `EEFF_unificado_30092023` verificable. No se genera Q4.

## Banco Ciudad

- Estado consolidado oficial 30/09/2023:
  https://www.bancociudad.com.ar/cms/recursos/institucional/carpetarecurso/Balances%20Trimestrales/EstadosFinancieros/2023.09_-_EEFF_consolidados.pdf

El consolidado sigue siendo control. La existencia de estados separados al mismo corte está apoyada documentalmente, pero V69 no recupera el binario individual/separado compatible.

## Credicoop

Se conserva el FY individual exacto heredado. La publicación 30/09/2023 existe, pero V69 no recupera bytes compatibles de Anexo Q; no se realiza inferencia.

## Santander

No se recuperó una fuente regulatoria alternativa con Anexo Q 9M. El bound individual V68 se conserva sin cambios. No usar Nota 7 / Anexo P stocks para completar flujos.

## Regla de extracción

Q4 sólo puede reconstruirse con:
`FY_Dec - 9M_Sep × 1.532908152197`
sobre estados de la misma entidad, base, período contable y esquema de moneda homogénea.
