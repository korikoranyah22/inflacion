# PROMPT CODEX V73 — CREDICOOP DYNAMIC BINARY + BNA ALTERNATE 9M COUNTERPARTY DISCLOSURE

Continuar desde `HANDOVER_CODEX_CICLO_AJUSTE_V72_A_V73.md` y `BASE_V72` conceptual (el paquete V72 completo).

## Objetivo

Aumentar cobertura exacta Q4-2023 de las cuatro patas de pases por contraparte sin reintroducir el falso gate de Anexo Q trimestral.

## Hallazgo regulatorio congelado

BCRA Comunicación A 7809, Sección 12: **Anexo Q / A-Q = Anual**. No asumir que una entidad debía publicar Q al 30/09/2023.

## Tareas

### A. Credicoop
- Resolver el target dinámico del link oficial 30-09-2023.
- Priorizar endpoint real, JS/API, caché o copia regulatoria; no adivinar IDs `descarga=`.
- Una vez recuperado el filing, buscar términos y tablas equivalentes a: `operaciones de pase`, `ingresos por intereses`, `egresos por intereses`, `Banco Central`, `otras entidades financieras`.
- Extraer cuatro patas sólo si están explícitas y en base individual/separada compatible.

### B. BNA
- No perseguir SC1: ya está recuperado y es sólo informe de revisión.
- Buscar el filing separado completo 30/09/2023 o datos BCRA de presentación trimestral/machine-readable.
- Aceptar como target cualquier disclosure primario 9M que dé las cuatro patas; si sólo da total, registrar bound/total, no inventar split.

### C. Provincia/Ciudad
- Repetir el criterio de BNA sobre filings separados/individuales y datos regulatorios.

## Fórmula permitida

Si hay 9M compatible en moneda homogénea Sep-2023:

`Q4_Dec = FY_Dec - 9M_Sep * 1.532908152197`

No mezclar consolidado con separado, FY con Q4, stocks con flows ni asset shares con pesos de flujos.

## Salida

Crear V73 versionada, QA, manifest, verdict y handover. No modificar HTML.
