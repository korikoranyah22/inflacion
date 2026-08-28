# Handover — Ciclo de ajuste / red de pases bancarios V84 → V85

**Fecha de corte:** 2026-08-28  
**Checkpoint formal cerrado:** V84  
**Próxima iteración:** V85

## Estado congelado

- strict Q4 four-leg coverage = **27.36550851928007%**
- exactos elegibles: ICBC, Banco de Valores, Macro, Credicoop, BAPRO, **Banco Ciudad**
- gate = NO
- factor Sep→Dic = 1.532908152197492

## Qué cambió en V84

Miyu recuperó los `.7z` oficiales BCRA de Sep-2023 y Dic-2023, más sus PDFs. Fueron extraídos y auditados. `cta_impu`/`baldet` exponen cuentas por entidad y `h_imput.txt` contiene historia mensual.

Banco Ciudad queda promovido desde raw `INDIVIDUAL_ENTITY_REGULATORY`:
- Sep 9M: income otherFI 64,710,954; expense otherFI 302,748; BCRA legs 0.
- FY: income otherFI 469,990,158; expense otherFI 791,821; BCRA legs 0.
- Q4 Dec-homogeneous: income otherFI 370794209.0769231; expense otherFI 327736.1227385137.

## BNA

No promover todavía. Raw:
- 511108 Sep 276,317,950 / Dec 766,170,918 (BCRA active passes)
- 511027 absent
- 521108 absent
- 521022 absent
- 521007 Sep 2 / Dec 49,898,208 (`otros pases pasivos`)

El 521007 no puede autoasignarse a 0302030200: el frozen separated FY BNA Annex Q dice pass expense 0, mientras Macro demuestra que el tratamiento de 521007 en presentación puede depender de crosswalk/subcuentas.

## Prioridad V85

Resolver BNA por uno de estos caminos, sin inventar:
1. mapping BCRA explícito de Plan de Cuentas/subcuentas → 0302030200;
2. full separated BNA 30/09/2023 con Annex Q;
3. full separated 30/09/2024 si imprime comparativa 2023 útil.

No pedir más `.7z` mensuales por ahora: `h_imput.txt` ya contiene historia.
