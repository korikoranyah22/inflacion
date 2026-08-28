# Six-digit BCRA raw mapping limit — V85

## Universo

El `.7z` Dic-2023 contiene **63 bancos** y la suma de sus activos individuales es **96697695.493 millones ARS**, prácticamente idéntica al denominador congelado `96697695.5` millones. Esto valida que el raw cubre el universo bancario.

## Pero no habilita promoción masiva

La hipótesis preliminar de promover bancos por ausencia de cuentas `otros pases` fue rechazada. Santander es un falsificador directo: el Annex Q separado FY informa ingreso por pases BCRA 354,462,410 y otras EF 22,950, mientras el raw de seis dígitos concentra 354,483,344 en `511027` (sector financiero), además de valores menores en `511108`/`511007`.

La explicación contable es coherente con la existencia de subcuentas por contraparte bajo cuentas de seis dígitos; por tanto, el archivo IEF público agrega información que Annex Q vuelve a abrir.

Regla V85:

```text
SIX_DIGIT_RAW_ACCOUNT_NAME != UNIVERSAL_ANNEX_Q_COUNTERPARTY_CROSSWALK
```

El raw se conserva para: universo, controles, reconciliaciones y crosswalks **validados entidad por entidad**. No se usa para inferir patas strict de entidades sin fuente de presentación compatible.

Bancos con cuentas `otros pases` detectadas: **8**. Aun los demás no se promueven automáticamente por el contraejemplo Santander.
