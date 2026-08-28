# Handover — Ciclo de ajuste / red de pases bancarios V82 → V83

**Fecha de corte:** 2026-08-28  
**Checkpoint formal cerrado:** V82  
**Próxima iteración:** V83

## 1. Arranque corto

Continuar desde V82. No reabrir V52–V81 ni las reglas metodológicas cerradas.

Cobertura strict Q4 four-leg = **23.54332498027319%**. Gate = **NO**.

Exactos elegibles: ICBC Argentina, Banco de Valores, Macro, Credicoop y BAPRO.

## 2. Primer evento a atender

Hay un rescate manual activo para **AGN Informe 210/2023 → Anexo**.

Si Miyu sube ese archivo, inspeccionarlo **antes de cualquier otra búsqueda**:

1. comprobar si es el paquete largo BNA 30/09/2023;
2. localizar la sección separada/individual;
3. buscar Annex Q/notas de resultados por pases;
4. recuperar, si están explícitas, las cuatro patas 9M;
5. reexpresar a dic-2023 con el factor congelado `1.532908152197492`;
6. diferenciar contra FY separado exacto;
7. promover BNA sólo si todo reconcilia en base compatible.

No volver a pedir Resolución / Informe SC 1 / Informe CC 2.

## 3. Nuevo hallazgo BCRA

La página oficial de Información sobre entidades financieras confirma un `.7z` con TXT del total de entidades + PDF descriptor.

Nueva pista: una tesis UDESA 2025 dice explícitamente que el `.7z` junio-2024 de esa publicación **contiene información histórica** y documenta extracción por cuentas contables. Por eso V83 puede recuperar un `.7z` posterior verificado y comprobar si incluye 2023-09; no es obligatorio encontrar un binario llamado 202309.

**No inventar nombre/href del `.7z`.**

Códigos congelados:

- `0301060100` ingreso pases BCRA
- `0301060200` ingreso pases otras EF
- `0302030100` egreso pases BCRA
- `0302030200` egreso pases otras EF

## 4. BNA comparator

El full pack BNA 30/09/2025 prueba que los estados separados de 3M/9M se presentan contra el mismo período del año anterior. La estrategia de buscar full 30/09/2024 para obtener comparativas 30/09/2023 queda estructuralmente validada.

Pero sólo promover si el PDF 2024 real imprime las filas necesarias.

## 5. Banco Ciudad

El paquete consolidado oficial 30/09/2023 contiene una declaración expresa del auditor: emitió por separado un informe sobre los estados financieros separados condensados a la misma fecha/períodos.

Por tanto el separado **existió**. No se encontró href verificado. No adivinar filename.

## 6. Ruta CNV

Se probó `argentina.gob.ar/cnv/informacion-financiera-mensual-remitida-por-bcra` para septiembre-2023. Es útil como publicación oficial/resumen por entidades emisoras, pero no muestra los cuatro códigos objetivo y no reemplaza el raw BCRA.

## 7. Reglas congeladas

- base strict: individual standalone o separated individual;
- jamás `9M consolidado + FY separado`;
- stock no reemplaza flujo;
- total pases no se reparte arbitrariamente por contraparte;
- consolidado/control-only nunca promueve;
- Q4: `FY_Dec - 9M_Sep × 1.532908152197492`.

## 8. Objetivo V83

Prioridad:

1. ingerir AGN `Anexo` si llega;
2. resolver un `.7z` BCRA verificable con historia 2023-09;
3. recuperar Ciudad separado 30/09/2023;
4. recuperar BNA full separado 30/09/2024 si el Anexo 2023 no destraba.

Cerrar V83 con promoción sólo si aparece evidencia four-leg compatible. Si no, mantener exactamente 23.54332498027319%.
