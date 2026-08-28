# Auditoría V74

## Baseline

V73 se preserva íntegramente bajo `BASE_V73_SNAPSHOT/`. No se reabre ninguna fila exacta cerrada.

## Nuevo control primario

Se incorporó el archivo `BCRA_202309_ENTITY_LEVEL_REGULATORY_CONTROL_V74.csv` con datos entity-level de la publicación mensual BCRA al 30/09/2023 para Credicoop, Ciudad, BNA y BAPRO.

Estos datos son **controles regulatorios 9M**, no cuatro patas de pases. No pueden alimentar la fórmula de bridge Q4 por sí solos.

## Revalidación Banco Ciudad

Se reabrió el PDF 9M ya conocido y se verificó el encabezado del Anexo Q: la apertura de resultados es de los **estados financieros consolidados condensados**. Los resultados de pases están íntegramente atribuidos a `Otras Entidades Financieras`, pero el basis consolidado mantiene la fila fuera del panel estricto individual.

## Gates congelados

1. Consolidado = control si el target estricto es individual/separado.
2. FY != Q4.
3. Stock != flow.
4. Asset share != flow weight.
5. Anexo Q 9M no es requisito regulatorio general en 2023.
6. Bridge Q4 sólo con misma entidad, basis, definición, período y moneda homogénea.
7. No inferir split BCRA/otras entidades a partir de totales financieros agregados.
8. No usar la publicación mensual BCRA como sustituto de una apertura de pases por contraparte que no contiene.

## Resultado

`STRICT_Q4_FOUR_LEG_EXACT_COVERAGE` permanece en **11.260968%**.
