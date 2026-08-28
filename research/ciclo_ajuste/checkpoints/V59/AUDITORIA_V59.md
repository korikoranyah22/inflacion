# AUDITORÍA V59 — Entity-level real-margin bridge

## 1. Pregunta
¿Podemos explicar y reconciliar la transformación del lado positivo del estado de resultados post-NIIF hacia los componentes analíticos del `Margen financiero integral real` (MFIR) del IEF, y desde allí identificar flujos por contraparte/sector?

## 2. Fórmula analítica del IEF: gate cerrado
La Tabla 2 del IEF usa una definición común: `% anualizado del activo neteado`. La identidad analítica es:

`MFIR ≈ intereses ingresados + intereses egresados + CER/CVS + FX + pases + títulos c/ORI + resultado monetario + otros financieros`

Q3-2023: `13,5 - 36,9 + 8,1 + 6,9 + 8,8 + 28,1 - 14,2 + 0,0 = 14,3`, frente a MFIR publicado `14,4`.

Q4-2023: `15,6 - 39,8 + 7,9 + 18,2 + 16,5 + 35,4 - 23,4 + 0,3 = 30,7`, frente a MFIR publicado `30,6`.

El residual de ±0,1 pp es compatible con redondeo de componentes publicados.

**Estado:** `IEF_MFIR_COMPONENT_FORMULA = EXACT_WITH_ROUNDING`.

## 3. Por qué P24 broad no es IEF interest income
V58 ya había rechazado el mapeo directo por el test de denominador. V59 identifica ahora una razón estructural en el régimen informativo post-NIIF.

El Estado de Resultados 015 contiene la línea broad `0501010010 Ingresos por intereses`. El Anexo Q abre esa familia en, entre otros:
- títulos privados (`0301020000`);
- títulos públicos (`0301030000`);
- préstamos y otras financiaciones (`0301050000`);
- pases/cauciones (`0301060000`), con BCRA (`0301060100`) y otras entidades financieras (`0301060200`).

Por lo tanto, la línea broad contiene rubros que el IEF vuelve a presentar en buckets analíticos separados como títulos y pases, además de distinguir indexación y otros resultados. No es válido sustituir broad interest por `IEF Ingresos por intereses`.

**Estado:** `POST_NIIF_BROAD_INTEREST_COMMINGLING = STRONG_SUPPORT`.

## 4. Control empírico a nivel entidad: BNA 2023
El Anexo Q consolidado de BNA 2023 muestra `Ingresos por intereses = 10.667.808.775` miles de pesos constantes. Dentro de ese total:
- títulos públicos: 66.03% del broad total;
- pases: 7.22%;
- préstamos y otras financiaciones: 26.62%;
- sólo el bundle producto `hipotecarios + prendarios + personales + tarjetas` equivale a 5.79% del broad total.

BCRA aparece explícitamente como contraparte de `766.170.918` miles dentro de pases. La política contable de BNA confirma que los intereses devengados de pases activos se acreditan contra `Ingresos por intereses`.

Esto **no** es una estimación del sistema financiero: BNA es una sola entidad y los datos son anuales. Se usa sólo como worked example que demuestra que el broad interest puede estar dominado por títulos/pases y contener simultáneamente productos de crédito.

La Nota 27 además divulga `Ajustes CER, UVA y UVI = 1.222.766.498` miles. No se fuerza una reconciliación con el total del Anexo Q porque las presentaciones no son idénticas; se usa únicamente para demostrar que la indexación puede estar embebida en la presentación de intereses.

## 5. Frecuencia: el límite que queda
El Anexo Q es **anual**. Esto impide usar directamente sus subcuentas para obtener Q3 y Q4 del sistema. La continuidad del schema no es un permiso para inventar flujos trimestrales.

El BCRA sí publica mensualmente información de entidades y agregados sistémicos y declara que ofrece datos abiertos `.7z`/`.txt` del régimen informativo. Sin embargo, en este runtime no se resolvió/materializó la URL del archivo histórico 2023 correspondiente.

**Estado:**
- `A_Q_ANNUAL_SUBACCOUNT_SCHEMA = STRONG_SUPPORT`
- `Q3_A_Q_RAW_AVAILABILITY = REJECTED_BY_REPORTING_FREQUENCY`
- `RAW_ENTITY_OPEN_DATA_ENDPOINT_DISCOVERY = PAGE_CONFIRMED_BUT_FILE_URL_UNRESOLVED`

## 6. Reconciliación de denominador común
Se preservan los controles V58 realmente observados/reconstruidos:
- egresos por intereses: denominador ≈ ancla en Q3 y Q4;
- resultado monetario: ≈ ancla;
- administración: ≈ ancla;
- incobrabilidad: razonablemente próxima.

Para los componentes positivos se calculan `IMPLIED_TARGET_FLOW_FROM_IEF = pct_a/4 × activo_neteado_medio`. Son objetivos matemáticos de reconciliación, **no** subcuentas observadas.

Así se cumple el control de usar un mismo denominador sin fingir haber recuperado los flujos positivos crudos.

## 7. Hogares
El régimen informativo identifica subcuentas de intereses por `Personales` y `Tarjetas de Crédito`, además de `Hipotecarios` y `Prendarios`. Eso vuelve técnicamente plausible una futura cuantificación de flujos household-like.

Pero:
1. Anexo Q es anual;
2. producto no equivale exactamente a sector institucional hogar;
3. el agregado sistémico Q4 compatible con el IEF no fue materializado;
4. no se puede extrapolar BNA al sistema.

Por eso:
`HOUSEHOLD_PRODUCT_LEVEL_FLOW_SCHEMA = IDENTIFIED`
`HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D`.

## 8. Títulos / emisor
El schema distingue resultados/intereses de títulos públicos y privados y modos contables (costo amortizado, FVOCI, FVTPL), pero no permite convertir el bucket sistémico `títulos c/ORI` en un share Treasury/BCRA sin valores de flujo y una apertura de emisor compatible.

`TREASURY_SECURITIES_RESULT_SHARE = N/D`
`BCRA_SECURITIES_RESULT_SHARE = N/D`.

No se usa stock para asignar resultado.

## 9. FX / CER / pases
- FX sigue mezclando reexpresión, compraventa y derivados: contraparte directa `N/D/MIXED`.
- CER/CVS tuvo gap anormal Q4-Q3 de -0,2 pp, por lo que no fue fuente positiva del gap; además atraviesa activos/pasivos distintos.
- Pases conserva la contraparte directa BCRA para el canal anormal identificado: `+7,7 pp`.

## 10. Incidencia congelada
El resultado distributivo no cambia:

`PASSES_DIRECT_BCRA = 7,7 pp = 26,83%`
`UNRESOLVED_COUNTERPARTY = 21,0 pp = 73,17%`
`DIRECT_HOUSEHOLD_POINT_ESTIMATE = N/D`
`DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED`.

## 11. Qué corrigió/añadió V59
V59 no inventa un nuevo share; logra algo previo y necesario: explica estructuralmente la falla de V58 y localiza la reclasificación post-NIIF. El próximo paso debe aprovechar que el Anexo Q y el IEF anual 2023 **sí son frequency-compatible**, en lugar de exigirle al Anexo Q un trimestre que no publica.
