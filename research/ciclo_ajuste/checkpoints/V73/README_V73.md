# V73 — public-bank 9M recovery checkpoint

**Fecha de corte:** 2026-08-28

V73 es un checkpoint de continuidad construido sobre V72. No promueve nueva cobertura estricta mientras falte una fuente 9M **separada/individual** compatible para las entidades públicas/coop prioritarias.

## Estado principal

- Cobertura estricta Q4 cuatro patas: **11.260968% de activos bancarios**, sin cambios respecto de V72.
- Panel exacto vigente: **ICBC + Banco de Valores + Banco Macro**.
- Banco Ciudad: existe control oficial 30/09/2023 **consolidado**, pero no se incorpora al panel estricto individual/separado.
- Banco Credicoop: el índice oficial confirma publicación **30-09-2023**; el binario dinámico continúa pendiente de recuperación.
- BNA: los adjuntos AGN recuperados prueban revisión de EEFF 9M y corrigen el falso gate de Anexo Q trimestral; el filing separado completo / disclosure cuatro patas 9M sigue pendiente.
- BAPRO: FY exacto disponible; 9M separado compatible sigue pendiente.
- HTML: **no modificar**.

## Archivo externo que destraba más rápido V73

`Banco Credicoop — publicación 30-09-2023` descargada desde la página oficial de Memoria y Balance.

Ver `USER_FILE_REQUESTS_V73.md`.

## Estructura

- `BASE_V72_SNAPSHOT/`: bundle V72 completo que sirve de baseline reproducible.
- `CURRENT_STATE_V73.csv`: estado operativo de V73.
- `RECOVERY_QUEUE_V73.csv`: cola priorizada de recuperación.
- `SOURCE_REFERENCES_V73.md`: rutas primarias conocidas.
- `AUDITORIA_V73.md`: decisiones y gates metodológicos.
- `VEREDICTO_V73.md`: cierre del checkpoint.
- `HANDOVER_CODEX_CICLO_AJUSTE_V73_A_V74.md`: continuidad.
