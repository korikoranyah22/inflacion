# Registro de correcciones V184

## Corrección 1 · falso negativo del XLSX 2020

El archivo descargado desde el enlace oficial rotulado “Anexo 4.37 · Cuadro de Cuentas Bancarias” contiene internamente `ANEXO 4.36` en la hoja `F21` (`A1:BJ51`). Por lo tanto, la ausencia de MY4002 en ese libro no era evidencia sobre el verdadero cuadro bancario.

## Corrección 2 · cero del programa ≠ cero de la cuenta

El Anexo 4.21 registra en cero los movimientos financieros del programa y señala que el cierre definitivo no estaba certificado. Ese dato no extingue MY4002. El verdadero Anexo 4.37 en la separata PDF conserva la fila MY4002, deja vacíos los campos numéricos 2020 y declara que la cuenta continuaba activa y manejada por FONDyF.

## Estado corregido

Se reemplaza `ZERO_ACCOUNT_EXTINGUISHED` o cualquier lectura equivalente por `ACTIVE_REPORTED_UNDER_FONDYF_2020_BALANCE_NOT_PUBLISHED`. Siguen abiertos: saldo 2020, cuenta/CBU, convenio ejecutado, destino fiduciario, extractos, contraparte, vínculo Res1406, deuda firme, pago, daño y responsabilidad.
