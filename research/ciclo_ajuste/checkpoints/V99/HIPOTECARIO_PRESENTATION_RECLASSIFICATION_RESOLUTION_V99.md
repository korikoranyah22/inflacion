# Banco Hipotecario — resolución del aparente conflicto de presentación, V99

## Qué bloqueaba desde V88

El 30/09/2023 separado, Note 19 informa **157,005,580k** de intereses por pases activos. Raw BCRA entidad `00044` da `511108=156,378,434k` + `511027=627,146k`, suma exacta **157,005,580k**.

En gastos, el mismo 9M Note 20 presenta un opening exhaustivo de egresos por intereses por **276,244,246k**, pero no muestra una línea explícita de pases, mientras raw contiene `521022=158,630k`. Desde V88 esto se trató correctamente como una contradicción aparente y se evitó llevar hacia atrás el mapping FY.

## V99: el FY demuestra que la omisión de Note 20 no significa ausencia de gasto de pases

En FY separado, **Note 20** presenta:

- cuentas corrientes: 350,393,440k;
- cajas de ahorro: 177,998k;
- plazo fijo: 249,027,718k;
- préstamos interfinancieros recibidos: 478k;
- otras obligaciones negociables y títulos de deuda: 5,093,155k;
- ajustes CER/CVS/UVA/UVI: 5,791,882k;
- total: **610,484,671k**.

No hay una línea explícita de pases en Note 20. Sin embargo, el **Annex Q separado del mismo FY** presenta exactamente el mismo total **610,484,671k** y sí abre:

- plazo fijo e inversiones a plazo: 254,819,600k;
- financiaciones recibidas BCRA/otras IF: 478k;
- **operaciones de pase — otras entidades financieras: 526,688k**;
- otros pasivos financieros: 182,117k;
- obligaciones negociables: 4,384,350k.

Las identidades cierran exactamente:

```text
249,027,718 + 5,791,882 = 254,819,600
526,688 + 182,117 + 4,384,350 = 5,093,155
```

Por lo tanto, la ausencia visual de una línea de pases en Note 20 es una **agregación/reclasificación de presentación**. El propio FY prueba que Note 20 puede no mostrar "pases" como línea separada aun cuando Annex Q identifica un gasto de pases no cero.

## Consecuencia para el 9M raw

Esto elimina el único falsificador que impedía usar el crosswalk **same-entity/same-year** ya documentado en V88. No se generaliza ninguna cuenta a otros bancos.

Para Banco Hipotecario, dentro de 2023:

```text
9M BCRA income     = 156,378,434k   [511108]
9M Other-FI income =     627,146k   [511027]
9M BCRA expense    =           0k
9M Other-FI expense=     158,630k   [521022]
```

El ingreso 9M total vuelve a reconciliar exactamente a la fuente issuer: `156,378,434 + 627,146 = 157,005,580`.

FY Annex Q separado:

```text
FY BCRA income      = 405,189,892k
FY Other-FI income  =   1,052,960k
FY BCRA expense     =           0k
FY Other-FI expense =     526,688k
```

Aplicando exclusivamente el factor congelado `1.532908152197492`:

```text
Q4 BCRA income      = 165476115.693522542312472k
Q4 BCRA expense     = 0E-15k
Q4 Other-FI income  = 91602.783981951682168k
Q4 Other-FI expense = 283522.779816911844040k
```

## Gate de preservación post-V96

**ANALÍTICAMENTE RESUELTO, PERO NO PROMOVIDO TODAVÍA.**

Los dos PDFs oficiales directos de Banco Hipotecario estaban documentados en `SOURCE_REFERENCES_V88.md` y en los census históricos como `no_local_match`, pero nunca fueron incorporados físicamente al catálogo maestro. V99 corrige esa omisión: ambos pasan a `FUENTES.csv` como binarios pendientes.

Hasta preservar los originales + SHA-256, Hipotecario queda:

`ANALYTICALLY_RESOLVED_SOURCE_PRESERVATION_HOLD`.

Si esos dos binarios se preservan y su contenido coincide con el audit V99, la promoción es mecánica:

- exact entities: **25**;
- numerator: **59166265.710 million ARS**;
- strict coverage candidate: **61.186841531295851823066455601312649689774664795398355692975123693614808017839474%**;
- closed-network gate: **NO**.

Si además se preservan los dos Columbia ya resueltos:

- exact entities candidate: **26**;
- strict coverage candidate: **61.374786601817206698581560302023950508727480480649096751225058926042348134346180%**.
