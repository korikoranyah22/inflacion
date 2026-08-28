# AUDITORÍA V57 — Régimen post-2020 y bridge de resultados en moneda homogénea

## 1. Corrección principal a V56

V56 verificó correctamente la continuidad **metadata** de 23 IDs históricos, pero dejó abierta una expectativa equivocada: que esos IDs necesariamente tuvieran observaciones mensuales Sep–Dic 2023. La metodología oficial del BCRA dice que la publicación de **resultados mensuales** fue discontinuada desde enero de 2020 por la adopción de estados contables en moneda homogénea.

Por eso `MONTHLY_SUBACCOUNT_VALUES_2023_V57.csv` conserva las 92 combinaciones esperadas, pero todas quedan explícitamente como `NOT_PUBLISHED_AS_LEGACY_MONTHLY_RESULT_POST_2020`. No se imputan ceros ni se fabrican valores.

## 2. Fuente post-2020 correcta

`Información de Entidades Financieras` publica el estado de resultados **acumulado** y en moneda homogénea. P24 ofrece Jun-2023, Sep-2023 y Dec-2023 para el sistema financiero.

Para recuperar flujos trimestrales hay que reexpresar el acumulado del cierre anterior a la moneda del nuevo cierre antes de restarlo.

V57 usa, de forma aproximada, los IPC mensuales INDEC publicados con un decimal:

- Jun→Sep: factor ≈ 1.346553
- Sep→Dec: factor ≈ 1.533138

Los factores son aproximados porque las variaciones mensuales publicadas están redondeadas.

## 3. Broad-flow bridge

En una base común de pesos de diciembre de 2023:

- resultado total integral: Q3 ≈ $0.736 billones; Q4 ≈ $3.134 billones; +326.0% en magnitud;
- ingresos financieros: Q4 ≈ +32.9% vs Q3;
- línea amplia `Por Intereses`: Q4 ≈ +13.1% vs Q3;
- otros ingresos financieros: Q4 ≈ +71.0% vs Q3.

Esto es **descriptivo**, no una reconciliación de los puntos porcentuales del IEF.

## 4. Por qué no se convierte el broad bridge en +7,3 / +2,1 / -0,2 / +11,3 pp

El IEF usa componentes analíticos y expresa la rentabilidad en porcentaje anualizado del activo neteado. P24 expone un estado de resultados agregado en millones y sólo divide ingresos/egresos financieros entre `Por Intereses` y `Otros`. No prueba identidad con:

- títulos +7,3 pp;
- ingresos por intereses +2,1 pp;
- CER -0,2 pp;
- FX +11,3 pp;
- pases +7,7 pp.

Por eso `PP_TARGET_RECONCILIATION_V57.csv` deja una sola mejora: la línea amplia de intereses aporta **dirección compatible**, pero no magnitud ni contraparte sectorial.

## 5. Nuevo bridge conceptual útil

La metodología de `Información de Entidades` define R8 con un numerador `Flujo de Intereses por Préstamos + ajustes`. Esto demuestra que existe una noción post-2020 de flujo devengado de intereses de préstamos compatible conceptualmente con el viejo 1153. Pero P24 no publica ese numerador ni lo divide entre hogares y empresas.

## 6. Contrapartes

No se eleva ningún share nuevo. Permanece:

- pases → BCRA: 7,7 pp = 26,83% del subtotal positivo bruto, `STRONG_SUPPORT`;
- resto: 21,0 pp = 73,17%, `UNRESOLVED`;
- hogar directo: `N/D`;
- transferencia hogar→banco a nivel del abnormal gap: `NOT_IDENTIFIED`.

## 7. Gate para V58

La siguiente iteración debe materializar los XLSX modernos `Infbanc0623/0923/1223.xlsx`, el anexo, o la base por entidad, y buscar el dataset que alimenta los componentes analíticos del IEF. No volver al esquema pre-2020 como si fuera una fuente de valores 2023.
