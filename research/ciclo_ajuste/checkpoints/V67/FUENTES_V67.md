# FUENTES V67 — Large-bank 9M retrieval and coverage scale-up

## Banco Macro — fuente primaria oficial

### 30-09-2023 — estados financieros intermedios, incluido bloque separado / Anexo Q
`https://www.macro.com.ar/relaciones-inversores/documento/1580934703038/banco_macro_sa_eeff_30-09-2023.pdf`

Anexo Q separado usado:
- cifras en miles de pesos en moneda homogénea;
- 9M ingreso pases BCRA = 73.509.754;
- 9M ingreso pases otras entidades financieras = 42.130;
- 9M egreso pases otras entidades financieras = 7.281.804;
- no se presenta una sublínea de egreso por pases BCRA en la categoría compatible.

### 31-12-2023 — estados financieros anuales, incluido bloque separado / Anexo Q
`https://www.macro.com.ar/relaciones-inversores/documento/1580935557769/eeff_bm_31-12-2023.pdf`

Anexo Q separado usado:
- FY ingreso pases BCRA = 174.358.904;
- FY ingreso pases otras entidades financieras = 5.794.175;
- FY egreso pases otras entidades financieras = 13.664.897;
- no se presenta una sublínea de egreso por pases BCRA en la categoría compatible.

## BCRA — Información de Entidades Financieras, diciembre 2023
`https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202312e.pdf`

Banco Macro S.A. — activo Dic-2023 = **5.851.533,4 millones ARS**.
Denominador bancario congelado = **96.697.695,5 millones ARS**.

## Santander — fuente primaria localizada pero no parseada
Página oficial de accionistas:
`https://www.santander.com.ar/nosotros/accionistas`

3T23:
`https://www.santander.com.ar/api/files/EEFF_BSA_Consolidados_y_Separados_30_09_2023_con_informes_con_resena_7ba99de550.pdf`

4T23:
`https://www.santander.com.ar/api/files/EEFF_NIIF_Consolidado_y_Separado_al_31_12_2023_con_informes_con_resena_ea34b47122.pdf`

Los nombres oficiales indican `Consolidados_y_Separados` / `Consolidado_y_Separado`, pero el fetch disponible devuelve un error de decodificación Unicode. Por disciplina probatoria V67 no elevó ningún valor del Anexo Q separado Santander.

## Fuentes heredadas
V66 contiene las fuentes exactas de ICBC, Banco de Valores, Galicia parcial, Supervielle bound, Provincia FY y Credicoop FY. Se conservan mediante `BASE_V66.zip` y los controles copiados.
