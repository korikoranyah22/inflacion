# Auditoría V73

## Baseline

Se conserva íntegramente V72 como snapshot. V73 no reabre ni reinterpreta filas exactas ya cerradas.

## Gates congelados

1. **Consolidado = control**, no elegible para el panel estricto si el target es separado/individual.
2. **FY != Q4**.
3. **Stock != flow**.
4. **Asset share != flow weight**.
5. Un Anexo Q 9M **no es requisito regulatorio general** en 2023: BCRA A7809 lo clasifica como anual.
6. Para construir Q4 por diferencia se exige misma entidad, base contable, definición de contraparte, período y moneda homogénea.
7. No se inventan patas faltantes ni se redistribuyen totales entre BCRA y otras entidades financieras sin disclosure explícito.

## Banco Ciudad

El control 30/09/2023 consolidado ya estaba incorporado en V72 como control. No se eleva a cobertura estricta porque falta el equivalente separado/individual compatible.

## Banco Credicoop

La página oficial de Memoria y Balance lista explícitamente `30-09-2023`. La publicación primaria existe, pero el enlace de descarga se resuelve dinámicamente y el binario no quedó recuperado en el checkpoint.

**Acción:** obtener el archivo manualmente o resolver endpoint/API/JS real. Una vez recuperado, inspeccionar estados/notas por operaciones de pase, ingresos/egresos por intereses y contrapartes BCRA vs otras entidades financieras. No exigir Anexo Q.

## BNA

Los tres adjuntos AGN recuperados quedan archivados en `BASE_V72_SNAPSHOT/RECOVERED_AGN_ATTACHMENTS/`. Son evidencia de revisión y alcance; no sustituyen el filing separado completo con cifras de cuatro patas.

## Resultado de auditoría

No hay base para modificar la cobertura exacta Q4 en V73. El siguiente cambio cuantitativo sólo debe ocurrir si se recupera un 9M compatible y se cruza contra FY compatible.
