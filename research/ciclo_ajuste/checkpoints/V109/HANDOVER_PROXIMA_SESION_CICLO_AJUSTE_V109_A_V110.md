# Handover V109 → V110

## Estado congelado

V109 cierra la primera rama primaria de riesgo E0 2001–2003. Hay 226 fuentes catalogadas, 221 copias físicas/hash-válidas y 28 fuentes primarias E0 preservadas. El panel Q4-2023 permanece en 30 entidades, 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549% de activos y `CLOSED_NETWORK_GATE=NO`.

## Resultado V109

- detalle mensual de irregularidad total/privada: 36 meses calendario, 31 disponibles y cinco `PUBLISHED_AS_DOT`;
- máximo observado octubre de 2002 y normalización parcial a diciembre de 2003;
- cierres anuales de irregularidad, cobertura, exposición neta, cargos por incobrabilidad, liquidez y patrimonio;
- seis diferencias de vintage `NOT_EXACTLY_RECONCILED`;
- ocho quiebres/restricciones metodológicas congelados;
- ningún empalme, interpolación ni inferencia causal nueva.

## Prioridad V110

Construir el ledger fiscal realizado de E0 por mecanismo, separando:

1. autorización normativa;
2. emisión o reconocimiento del instrumento;
3. recepción por beneficiario;
4. valuación/actualización;
5. pago, rescate o cancelación;
6. stock pendiente;
7. pagador, receptor y universo;
8. fuente de Tesoro/BCRA/AGN y vintage.

Empezar por las fuentes legales ya mapeadas en V107 y confrontarlas con cuentas públicas, memorias BCRA y auditorías AGN. No usar el monto autorizado como monto pagado ni compensación bancaria como ganancia neta.

## Pendientes que no deben mezclarse

- riesgo: exactos mensuales de previsiones, quebrantos y capital regulatorio;
- bancos: heterogeneidad por entidad y Banco Rioja 158,789k;
- hogares: ingreso amplio y consumo;
- CNV: seis binarios objetivo y contrato exacto de adjuntos;
- red: denominador documentado y contraparte exacta.

## Orden de lectura

1. `VEREDICTO_V109.md`
2. `E0_BCRA_RISK_RECONSTRUCTION_V109.md`
3. `E0_BCRA_RISK_METHOD_BREAKS_V109.csv`
4. `E0_LEGAL_MECHANISM_TIMELINE_V107.csv`
5. `E0_PRIMARY_SOURCE_MAP_V107.md`
6. `HISTORICAL_SOURCE_QUEUE_V109.csv`
7. `CURRENT_STATE_V109.csv`
8. `qa_v109.py`
