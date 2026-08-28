# Auditoría V54 — microdatos BCRA y bridge contable

## 1. Misión

V54 debía reemplazar proxies de exposición por identidades contables reconciliables y, si era posible, transformar los `MIXED/N-D` de V53 en shares sectoriales o por emisor.

Gate congelado:

```text
raw official source
+ same accounting window
+ reconcilable flow/accrual identity
+ no double count
```

## 2. Ingesta oficial: endpoint sí, bytes no

Se verificaron los endpoints oficiales para:

- préstamos/depósitos privados por tipo de titular;
- préstamos/depósitos públicos por jurisdicción;
- títulos públicos por jurisdicción del emisor;
- préstamos y depósitos UVA mensuales;
- Series de Datos de diciembre de 2023 y diciembre de 2018;
- `baldethis.xls`, que BCRA publica como detalle de operaciones a futuro, situación de deudores y cuadro de resultados;
- la página de datos abiertos de entidades financieras, que declara ofrecer un `.7z` mensual con TXT del régimen informativo y un PDF de layout.

Pero el runtime no pudo materializar los binarios. Por tanto:

```text
OFFICIAL_ENDPOINT_DISCOVERY = PASS
RAW_SOURCE_BYTES_MATERIALIZED = FALSE
SHA256_GATE = FAIL_RUNTIME_NETWORK
```

No se fabricaron hashes ni se reconstruyeron bytes a partir de snippets web.

## 3. Corrección V53 #1 — contraparte y modo contable son ejes ortogonales

V53 había reportado 66,20% del subtotal positivo bruto como masa 'clasificada' sumando:

```text
pases → BCRA          7,7 pp
FX → valuation       11,3 pp
                    -------
                     19,0 pp
```

La suma aritmética es correcta, pero **no constituye una partición conjunta de contraparte**, porque `BCRA` describe quién está del otro lado y `valuation` describe cómo aparece contablemente el resultado.

Un mismo título del Tesoro puede tener:

```text
counterparty/issuer = Treasury
accounting mode      = market valuation
```

sin pago contemporáneo del Tesoro. Los ejes deben permanecer separados.

## 4. Corrección V53 #2 — FX no es 11,3 pp de valuación pura

La definición BCRA de `Diferencias de cotización` incluye dos familias:

```text
1. actualización mensual de activos y pasivos en moneda extranjera
2. resultado por compra y venta de moneda extranjera
```

Por tanto:

```text
FX_REMEASUREMENT_PRESENT = SUPPORTED
FX_TRADING_PRESENT_IN_ACCOUNT_DEFINITION = SUPPORTED
FX_REMEASUREMENT_SHARE = N/D
FX_TRADING_SHARE = N/D
MARKET_VALUATION_FLOOR_11_3PP = REVOKED
```

El descalce FX de diciembre y la devaluación siguen dando soporte mecánico fuerte a un componente de remeasurement, pero no permiten asignarle los 11,3 pp completos.

## 5. Corrección V53 #3 — +2,1 pp no es ceiling sectorial

V53 había usado el agregado:

```text
interest_income gap = +2,1 pp
```

como techo estricto aislado del canal hogar. Ese bound requiere una condición adicional no observada: que todas las contribuciones sectoriales al cambio sean no negativas.

Ejemplo algebraico compatible con el agregado:

```text
hogares  +3,0 pp
empresas -0,9 pp
----------------
neto     +2,1 pp
```

Así, sin subcuentas o restricciones de signo:

```text
HOUSEHOLD_[0,2.1]_STRICT_CEILING = REVOKED
HOUSEHOLD_INTEREST_CONTRIBUTION = N/D
```

Esto no prueba que hogares hayan contribuido más de 2,1 pp; sólo demuestra que el agregado no los acota matemáticamente.

## 6. Securities bridge

El BCRA publica stock de títulos públicos por jurisdicción/emisor. Sin embargo su propia definición del resultado por títulos mezcla:

- títulos públicos y privados;
- renta devengada;
- diferencias de cotización/precio;
- acrecentamiento por TIR;
- ventas;
- previsiones por desvalorización.

Entonces:

```text
issuer stock != issuer result share
Treasury-issued security != Treasury cash payment
```

El objetivo Q4-2023 de +7,3 pp queda `FAILED_RECONCILIATION`.

## 7. Interest-income bridge

Las páginas BCRA ofrecen stocks por tipo de titular y tasas por líneas/operaciones. Aun con esos archivos, una reconstrucción válida necesita:

```text
same-window average interest-bearing stock
× effective accrued yield compatible with that stock
→ sector accrued interest
→ reconciliation to aggregate interest-income line
```

No se recuperó esa identidad. Usar tasas de nuevas operaciones para todo el stock violaría el gate.

## 8. CER/UVA bridge

La coexistencia de préstamos UVA a personas y depósitos UVA de personas sigue falsificando un signo hogar único. El gap Q4-vs-Q3 agregado permanece -0,2 pp. Sin bytes/subcuentas no se obtiene gross result por activo/pasivo.

## 9. Partición conjunta Q4-2023 corregida

Subtotal positivo bruto congelado:

```text
FX             11,3
pases           7,7
títulos         7,3
intereses       2,1
otros           0,3
-------------- ----
TOTAL          28,7 pp
```

Sobre un único eje —**contraparte contable identificada**— sólo puede elevarse:

```text
BCRA direct via pases     7,7 pp   26.83%
unresolved               21,0 pp   73.17%
```

Esto no dice que 73,17% no tenga contraparte: dice que **no está identificada de forma disjunta y compatible** con la evidencia disponible.

## 10. Qué sobrevive de V53

Sobrevive:

```text
BCRA_DIRECT_FLOOR = 7,7 pp = 26,83%
DIRECT_HOUSEHOLD_POINT_ESTIMATE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
TAXPAYER_IDENTITY = REJECTED
```

Se revoca/refina:

```text
STRICT_CLASSIFIED_MASS_66_20_AS_JOINT_PARTITION = REVOKED
MARKET_VALUATION_FLOOR_39_37 = REVOKED
HOUSEHOLD_STRICT_[0,2.1]_BOUND = REVOKED
```

## 11. Resultado de V54

V54 no agrega una falsa cuantificación. Su aporte es **reducir la sobreidentificación** y dejar una especificación exacta de los bytes/subcuentas que todavía hacen falta.
