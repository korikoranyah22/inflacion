# Handover V145 → V145

## Estado

- QA V145: PASS.
- Quince manuales oficiales nuevos preservados; 453 fuentes maestras y 213 E0.
- Tablas exactas: `BCUENTA`, `ACTA_FUE`, `ACTABAN_CTAESC`, `BGRUPMOVBCO`, `BMOVBCO`, `BMOVEXTERNO`, `AMOV_FORG`, `ACLB_MOB`, `BCODLIBBCO`, `BEMPRESA`, `BERROR_AUD`, `BPROCESO`.
- Las tablas centrales se documentan `sin historia`; la consulta vigente no puede negar 2008.
- Vía forense: backups/snapshots 2006-2009 + bajas/rehabilitaciones + migraciones v7→v9.0 + correcciones.
- Captura oficial: `SLU v9.0`, 26/11/2008, ejercicio 2008 y BNA; ejemplo CUM023 es recurso, no target.
- Cadena: cuenta → externo BNA → interno/grupo → AMOV_FORG → C55 → Libro Banco/extracto → corrección/reversa.
- C10 separa recurso/crédito de C55/gasto; C55-DEP/REP/DEG y cheque son controles negativos.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V145

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Buscar inventarios públicos o archivísticos de respaldos SLU 2006-2009 y responsables de custodia.
3. Localizar exportación/snapshot poblado de `BMOVEXTERNO` y `AMOV_FORG` de 2008.
4. Buscar documentación de migración v7→v9.0 y versión desplegada en SAF 355.
5. Localizar una salida `conc_01/conc_02`, C55 o historial de correcciones con cuenta/referencia target.
6. Mantener C10, reversas y cheques como controles, sin elevar esquema a ejecución.
