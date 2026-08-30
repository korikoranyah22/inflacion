# V107

V107 convierte el episodio E0 (2001–2003) de un bootstrap incompleto en un mapa primario auditable. Corrige el censo local de V106, preserva diez fuentes oficiales nuevas y mantiene congelado el panel microbancario.

## Delta material

- El censo local identifica **17 fuentes primarias preservadas** útiles para E0: siete ya estaban en el repo y diez se incorporan en V107.
- Las siete heredadas incluyen balances/resultados, depósitos y préstamos por titular, títulos públicos, tasas y archivos diarios BCRA.
- Las diez nuevas son cuatro PDF BCRA y seis textos legales InfoLeg, todos con bytes y SHA-256 congelados.
- Se construyen un mapa de fuentes, una cronología de mecanismos y una cobertura E0 por seis familias.
- E0 pasa de `NOT_ENOUGH_EVIDENCE` a `PRIMARY_MAP_PARTIAL`; no pasa a comparable ni causal.
- El BEF oficial aporta falsificadores a una historia simple de ganancia bancaria inmediata: depósitos reales -42% al piso, patrimonio neto consolidado -37% en dos años y pérdidas récord en 2002.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- numerador: **59,812,903.504 millones ARS**;
- denominador: **96,697,695.5 millones ARS**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k** sin reconciliar;
- contrato exacto de attachments CNV: no observado.

## Estado de fuentes

- entradas catalogadas: **215**;
- copias locales físicas: **210**;
- copias con hash exacto: **210**;
- brecha binaria catalogada: Banco Rioja FY (P1);
- acciones discovery sin binario propio: siete.

## Leer primero

1. `VEREDICTO_V107.md`
2. `AUDITORIA_V107.md`
3. `E0_PRIMARY_SOURCE_MAP_V107.md`
4. `E0_LOCAL_PRIMARY_SOURCE_CENSUS_V107.csv`
5. `E0_LEGAL_MECHANISM_TIMELINE_V107.csv`
6. `HISTORICAL_EPISODE_MATRIX_2001_2026_V107.csv`
7. `HISTORICAL_EVIDENCE_COVERAGE_V107.csv`
8. `HISTORICAL_SOURCE_QUEUE_V107.csv`
9. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V107_A_V108.md`
10. `qa_v107.py`

V107 no completa la reconstrucción social INDEC, no concilia el costo fiscal realizado y no atribuye causalidad distributiva.
