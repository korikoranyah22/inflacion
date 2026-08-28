# BCRA Información de Entidades Financieras — raw `.7z` audit — V84

## Binarios recuperados

- 2023-09 open-data `.7z`: `31a0a315444496d4336695b6bd48deb562456df10e47fbc46de3703a77528bdb`
- 2023-12 open-data `.7z`: `60ef86addba5e6646a2bfd42853ca077ea7970e9fa6effe54f1179049868f0d4`
- 2024-06 open-data `.7z`: `316c6c80f1206b08e13753bb4ac8b8ffe6239fbbf523dc7bddf9154e0e95385d`

Los tres archives contienen `Entfin/Tec_Cont/cta_impu`, `baldet`, `cuentas`, `imput/h_imput.txt` y archivos por código de entidad. El `h_imput.txt` confirma además historicidad mensual.

## Base

La publicación BCRA declara información individual por entidad. La metodología BCRA de balance de saldos trabaja con balances no consolidados; el raw se trata como `INDIVIDUAL_ENTITY_REGULATORY`.

## Crosswalk contable validado

El Plan de Cuentas BCRA define:

- `511108` = intereses por pases activos con BCRA;
- `511027` = intereses por pases activos con el sector financiero;
- `521108` = intereses por pases pasivos con BCRA;
- `521022` = intereses por pases pasivos con el sector financiero;
- `521007` = intereses por otros pases pasivos.

La extracción V84 reconcilia exactamente `511108`, `511027` y `521022` contra las patas ya congeladas de ICBC, Banco de Valores, Credicoop y BAPRO. Macro reconcilia ingreso BCRA/otherFI exactamente; su egreso Annex-Q otherFI reconcilia con `521007 + 521022`, lo que demuestra que `521007` **no debe autoasignarse universalmente** sin crosswalk de presentación.

## Ciudad

Ciudad no presenta `521007` ni cuentas BCRA ambiguas. Sus únicas cuentas de resultado por pases en 9M/FY son `511027` y `521022`, y coinciden exactamente con el control Annex Q heredado. La fuente raw, sin embargo, es de base individual/regulatoria y por eso permite atravesar el gate de base.

Resultado: **Ciudad promovido**.

## BNA

BNA queda pendiente. `511108` recupera el ingreso BCRA, pero `521007` pasa de 2k en Sep a 49,898,208k en Dic. Ese rubro no puede repartirse automáticamente a `0302030200` y entra en conflicto con el Annex Q separado FY congelado (pass expense = 0). Por política de no forzar crosswalk, BNA no se promueve en V84.
