# Auditoría de `InfBanc_Anexo.xlsx` — V81

## Veredicto corto

El archivo recuperado es **útil como control agregado histórico**, pero **no es un anexo congelado a septiembre de 2023** y **no contiene observaciones por entidad individual**.

Su fingerprint dentro del repo es:

`SHA-256 9b1b48b18039389889ee7d480a9c6d8958fb99630f169339e46ab953e7133251`

## 1. Corrección de versionado

La hoja `Estado de Resultado desde 2020` llega hasta **enero de 2026** y la hoja `Metodología y Referencias` indica que, desde enero de 2020, los estados se expresan en moneda homogénea **a precios de la última fecha de información**.

La metadata interna del XLSX registra modificación el **2026-03-19**. La página oficial del BCRA del Informe sobre Bancos de enero de 2026 fue publicada el **2026-03-20** y expone un archivo estático llamado `Anexo (XLSX)`.

Conclusión: el binario preservado bajo `inputs/bcra/2023-09/` fue recuperado durante la búsqueda de septiembre de 2023, pero el contenido corresponde a una **versión viva/actual del anexo**, no a una snapshot 09/2023.

La página oficial del Informe sobre Bancos de septiembre de 2023 actualmente publica Informe, Normativa, Glosario y Series de Datos; no lista ese `Anexo (XLSX)` vivo como archivo de aquella edición.

## 2. Base y alcance

`Metodología y Referencias` establece:

- balance de saldos y plan de cuentas: **balances no consolidados**;
- datos de grupos: agregados por grupos de entidades;
- rentabilidad: resultados mensuales estimados a partir de la evolución de resultados acumulados;
- desde enero de 2020: estados en moneda homogénea a precios de la última fecha disponible;
- `Primas por pases` integra el margen financiero;
- `Por operaciones de pase activo` incluye todas las contrapartes.

Esto es valioso para controles de consistencia y magnitud, pero no crea un dataset `entidad × cuenta`.

## 3. `Bancos públicos → Primas por pases`

Fila auditada: **252**, hoja `Estado de Resultado desde 2020`.

Fuente en precios de enero-2026, millones de ARS:

- Ene–Sep 2023: **4252362.478538**
- Oct 2023: **1058443.288798**
- Nov 2023: **1144654.163588**
- Dic 2023: **1617427.944539**
- Q4 2023: **3820525.396925**
- FY 2023: **8072887.875463**

La suma mensual reconstruye el anual salvo ruido de coma flotante sub-millonésimo.

## 4. Reexpresión para comparabilidad con el panel congelado

IPC Nacional repo:

- enero-2026 = `10413.0309`
- diciembre-2023, valor congelado del proyecto = `3533.2`

Factor Dic-2023 → Ene-2026:

`2.947195431903091`

Por lo tanto, el candidato agregado `Bancos públicos → Primas por pases` es:

- Q4-2023: **1296325.773163 millones ARS de dic-2023**
- FY-2023: **2739176.298957 millones ARS de dic-2023**

## 5. Reconciliación agregada

Los grupos cierran numéricamente:

- `Bancos privados + Bancos públicos + EFNB = Sistema financiero`;
- `Bancos privados nacionales + Bancos privados extranjeros = Bancos privados`;

tanto para FY-2023 como para Q4-2023, con diferencias sólo de representación numérica.

Ver `BCRA_PASS_AGGREGATE_RECONCILIATION_V81.csv`.

## 6. Lo que NO se puede concluir

No existe en este XLSX un crosswalk explícito que pruebe que `Primas por pases` sea idéntico a:

`income_BCRA - expense_BCRA + income_otherFI - expense_otherFI`

bajo la misma taxonomía del Anexo Q por entidad.

Por eso:

- no promover BNA;
- no promover Ciudad;
- no repartir el residual del grupo público;
- no tratar el residual como bound individual duro;
- no sumar esta fila al panel strict four-leg.

BAPRO representa aritméticamente **31.536037%** del control público Q4 reexpresado, dejando **887516.002150 millones** para el resto del grupo. Ese residual es sólo diagnóstico agregado, no una imputación a BNA/Ciudad.

## Resultado V81

**CONTROL AGREGADO VALIDADO + CORRECCIÓN DE VERSIONADO. SIN PROMOCIÓN INDIVIDUAL.**
