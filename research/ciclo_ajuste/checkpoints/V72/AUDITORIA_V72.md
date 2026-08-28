# AUDITORÍA V72 — BNA AGN BINARY RECOVERY + ANNEX Q FREQUENCY CORRECTION

**Fecha de corte:** 2026-08-28  
**Base:** V71  
**Rama:** contrapartes / pases / cobertura bancaria / incidencia distributiva

## Resultado de la iteración

V72 resuelve el bloqueo documental que quedó abierto en V71: los PDF exactos de AGN 210/2023 fueron suministrados y se archivaron dentro del paquete. El endpoint externo podía devolver 502; el contenido ya no depende de esa ruta.

El hallazgo más importante no es numérico sino metodológico:

1. `2023-210-Informe SC 1.pdf` es el **informe de revisión** de los estados intermedios separados condensados, no el paquete completo. Declara revisión de los estados al 30/09/2023 y enumera Notas 1-19 + Anexos A,B,C,D,H,I,J,L,O,R.
2. `2023-210-Informe CC 2.pdf` es el informe de revisión equivalente para consolidados, con Notas 1-51 + Anexos B,C,D,H,I,R.
3. La Comunicación **BCRA A 7809** vigente desde 30/06/2023 clasifica **Anexo Q / A-Q como ANUAL**. Por lo tanto, perseguir un Q obligatorio al 30/09/2023 era un gate incorrecto.

## Corrección de estrategia

A partir de V72, `9M Annex Q` deja de ser requisito general. Para derivar Q4 por diferencia, alcanza cualquier fuente primaria 9M compatible que exponga las cuatro patas de pases por contraparte:

- ingreso de pases con BCRA;
- egreso de pases con BCRA;
- ingreso de pases con otras entidades financieras;
- egreso de pases con otras entidades financieras.

Los Anexos Q 9M ya recuperados de Macro/Banco de Valores se mantienen: son disclosures oficiales efectivamente publicados y siguen siendo válidos. La corrección sólo impide inferir que todas las entidades debían publicar Q trimestralmente.

## BNA

```text
BNA_9M_AGN_SC_REVIEW_ATTACHMENT = RECOVERED_AND_ARCHIVED
BNA_9M_AGN_CC_REVIEW_ATTACHMENT = RECOVERED_AND_ARCHIVED
BNA_9M_AGN_RESOLUTION = RECOVERED_AND_ARCHIVED
BNA_9M_FULL_SEPARATED_STATEMENT_PAYLOAD = NOT_ESTABLISHED
BNA_9M_REVIEWED_SEPARATED_ANNEX_LIST = A,B,C,D,H,I,J,L,O,R
BNA_9M_ANNEX_Q_IN_REVIEW_SCOPE = NO
BCRA_2023_ANNEX_Q_REPORTING_FREQUENCY = ANNUAL
BNA_9M_FOUR_LEG = N/D
BNA_Q4_FOUR_LEG = N/D
```

La revisión de SC1 es no modificada, con énfasis sobre diferencias BCRA/NIIF para instrumentos de deuda pública, procesos de administración/control y metodología de pérdidas crediticias esperadas. Es evidencia de alcance y calidad de revisión, no de los importes de pases buscados.

## Credicoop

El índice oficial sigue confirmando publicación al 30/09/2023, pero el target dinámico no fue recuperado en esta iteración. BCRA A7809 cambia la pregunta: una vez obtenido el binario, inspeccionar estados/notas por pases; no exigir Anexo Q.

## Cobertura estricta

No se agrega entidad exacta Q4. Se congela:

```text
STRICT_Q4_FOUR_LEG_EXACT = ICBC + Banco de Valores + Banco Macro
ASSET_COVERAGE = 11.260967847987649%
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Siguiente gate

Prioridad V73:

1. resolver binario dinámico Credicoop 30/09/2023;
2. BNA: buscar disclosure 9M primario alternativo de pases por contraparte, incluyendo rutas BCRA/machine-readable/estado de resultados/notas, sin asumir A-Q;
3. Provincia y Ciudad: repetir estrategia sobre filing individual/separado 9M;
4. no convertir totals, stocks, asset shares o consolidados en cuatro patas por inferencia.
