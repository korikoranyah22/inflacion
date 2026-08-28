# Handover — Ciclo de ajuste / red de pases bancarios — V83 → V84

**Fecha de corte:** 2026-08-28  
**Checkpoint formal cerrado:** V83  
**Próxima iteración:** V84

## Estado congelado

- cobertura strict Q4 four-leg = **23.54332498027319%**
- gate red cerrada = **NO**
- exactos elegibles = ICBC, Banco de Valores, Macro, Credicoop, BAPRO
- pendientes prioritarios = BNA, Banco Ciudad
- factor Sep→Dic = `1.532908152197492`
- base objetivo = individual/separada

## Hallazgo V83 — upload AGN

El archivo recibido como rescate durante la búsqueda del `Anexo` de AGN 210/2023 fue `2023-210-Informe CC 2(3).pdf`.

SHA-256:
`563b4e6f30ff13bd7a8cec6f794ad90a64383866cf907c434d9c7841a703ffd5`

Es byte-a-byte igual al `2023-210-Informe CC 2.pdf` ya preservado. Es el informe consolidado de tres páginas; no incorpora los estados/notas separados largos. **No volver a pedir este mismo archivo.**

## Hallazgo V83 — comparator BNA 2024

El full pack oficial 30/09/2025 muestra que la sección separada remite expresamente las aperturas de `Ingresos por intereses` y `Egresos por intereses` a las Notas 25/26 consolidadas cuando son representativas/coinciden o no difieren significativamente.

Consecuencia: el full pack 30/09/2024 sigue siendo deseable, pero **no asumir** que imprimirá four-leg separado 2023. Inspeccionar el binario real. Si sólo remite a consolidado, control-only.

## Prioridad 1 V84 — `.7z` BCRA

Manual rescue activo:

1. abrir `https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/`;
2. seleccionar **junio 2024**;
3. descargar **`Información de Entidades Financieras - Datos Abiertos (7z)`**;
4. subir el `.7z`, no el PDF sustituto.

La página oficial confirma TXT + descriptor PDF. Un trabajo UDESA documenta que ese archive junio-2024 contiene **información histórica**.

Al recibirlo:

1. preservar binario y hash;
2. leer descriptor PDF/layout TXT;
3. identificar campo período, entidad, cuenta, unidad/moneda;
4. filtrar período `2023-09`;
5. buscar BNA y Ciudad;
6. extraer exclusivamente:
   - `0301060100` ingreso pases BCRA
   - `0301060200` ingreso pases otras EF
   - `0302030100` egreso pases BCRA
   - `0302030200` egreso pases otras EF
7. validar que sean flujos/resultados y target-basis compatibles antes de diferenciar Q4;
8. no inferir ceros si el layout no prueba exhaustividad.

## Prioridades secundarias

- BNA full separated 30/09/2024: binary-inspection fallback, no comparator assumed.
- Ciudad separated 30/09/2023: existencia probada, binario pendiente.
- Si las rutas públicas se agotan: considerar solicitud formal de acceso a información BNA para el paquete separado 30/09/2023.

## Cierre esperado V84

Si el `.7z` contiene los cuatro códigos para BNA/Ciudad y la semántica es compatible, reconstruir Q4 con la fórmula congelada y recién entonces evaluar promoción. Si no, cerrar auditoría negativa sin mover cobertura.
