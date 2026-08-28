# AUDITORIA V84 — BCRA raw open-data breakthrough

## Resultado principal

Los `.7z` oficiales Sep-2023 y Dic-2023 fueron recuperados y extraídos. El raw contiene archivos por entidad y cuenta, incluyendo Ciudad, BNA, BAPRO y las entidades ya cerradas.

La reconciliación contra ICBC, Valores, Macro, Credicoop y BAPRO demuestra que las cuentas específicas de pases reproducen los valores 9M/FY congelados.

## Ciudad

9M Sep-2023 (miles ARS Sep homogéneos): otherFI income 64,710,954; otherFI expense 302,748; patas BCRA 0.
FY Dic-2023 (miles ARS Dic homogéneos): otherFI income 469,990,158; otherFI expense 791,821; patas BCRA 0.

Q4 = FY_Dec - 9M_Sep × 1.532908152197492

- income BCRA = 0
- expense BCRA = 0
- income otherFI = 370794209.076923072338
- expense otherFI = 327736.122738513688
- net otherFI = 370466472.954184532166

**Ciudad promovido a strict exact target basis.**

## BNA

No se promueve. El raw recupera 511108 BCRA income, pero aparece 521007 `otros pases pasivos` por 49,898,208k en Dic. Como la presentación separated Annex Q congelada informa pass expense 0 y el mapping no es universal (Macro requiere suma 521007+521022), se prohíbe autoasignar 521007.

## Cobertura

- V83: 23.54332498027319%
- V84: 27.36550851928007%
- incremento: 3.822183539006879 pp
- gate: NO
