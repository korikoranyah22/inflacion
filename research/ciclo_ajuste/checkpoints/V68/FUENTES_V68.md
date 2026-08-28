# FUENTES V68 — Primary recovery / disclosure gap / Santander individual bound

## Santander — primarias / regulatorias

1. CNV — Banco Santander Argentina S.A. company filings. La metadata identifica la presentación individual trimestral al 30/09/2023 (#3120080), separada de la consolidada.
   - https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/30500008454

2. Santander Argentina — estados financieros condensados separados intermedios al 30/09/2023 (archivo primario recuperado vía mirror de filings regulatorios).
   - https://cdn.financialreports.eu/financialreports/media/filings/68743/2023/RNS/68743_rns_2023-11-24_514c3f88-1bff-43e7-9afe-b8e793c5e3e1.pdf
   - El índice de anexos muestra A, B, C, D, H, I, J, L, O, P y R; no incluye Anexo Q.
   - Nota 26.1: "Por operaciones de pase" 9M-2023 = 100,510,106 (miles de pesos de Sep-2023 homogéneos).

3. Santander Argentina — estados financieros separados FY 2023, Anexo Q.
   - https://cdn.financialreports.eu/financialreports/media/filings/68743/2024/RNS/68743_rns_2024-03-06_8a497326-fbc5-4ac4-bb14-21ece6df12e5.pdf
   - Por operaciones de pase = 354,485,360
   - BCRA = 354,462,410
   - Otras entidades financieras = 22,950
   - Egreso por operaciones de pase = 1,631,890, subfila otras entidades financieras.

4. SEFyC/BCRA — Información de Entidades Financieras, diciembre 2023 (mirror oficial argentina.gob.ar), Banco Santander Argentina, activo Dic-2023 = 8,577,090.6 millones ARS.
   - https://www.argentina.gob.ar/sites/default/files/202312cnv.pdf

## BBVA — metadata regulatoria

5. CNV — Banco BBVA Argentina S.A. La ruta recuperada muestra al banco padre con estados consolidados para 30/09/2023 y 31/12/2023; las entradas individuales visibles pertenecen a controladas/vinculadas.
   - https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/30500003193

## Fuentes heredadas

Se mantienen todas las fuentes V67 para ICBC, Banco de Valores, Macro, Galicia, Supervielle, Provincia, Credicoop y el denominador bancario. Ver `BASE_V67.zip` y `FUENTES_V67.md` dentro de la base.

## Regla de uso

La ausencia de Anexo Q en el filing intermedio Santander recuperado se interpreta como `DISCLOSURE_GAP_ON_THIS_FILING`, no como prueba de inexistencia absoluta de un reporte regulatorio separado en otra vía. No usar stocks de Nota 7/Anexo P para reconstruir contrapartes de flujo.
