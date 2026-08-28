# Delta de handover — V96 source preservation final

Este archivo **complementa** el handover maestro generado antes del cierre manual. Sus métricas de source-completeness `189 / 181 / 8` quedan supersedidas por este estado final:

```text
ANALYTIC_CHECKPOINT = V96
STRICT_COVERAGE = 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
EXACT_ENTITIES = 24
CLOSED_NETWORK_GATE = NO

SOURCE_CATALOG_ENTRIES = 189
PHYSICAL_LOCAL_COPIES = 187
PHYSICAL_HASH_OK = 187/187
REFERENCE_ONLY_NONBINARY_EXEMPT = 2
PHYSICAL_GAPS_REQUIRED = 0
P0 = 0
P1 = 0
P2 = 0
FILES_OVER_50_MIB = 0
NUMERIC_V96_CHANGED_BY_SOURCE_CLOSE = FALSE
```

Las dos referencias no binarias exentas son la landing CNV de Santander (índice; filings subyacentes preservados) y Todo Sobre la Mora (objeto secundario de análisis; preservar fuentes primarias).

Los EEFF oficiales CNV Santander 30/09/2023 y 31/12/2023 entregados manualmente fueron verificados byte-a-byte contra las copias ya preservadas.

Siguiente trabajo analítico: retomar V97 desde Banco Columbia S.A.; source-completeness ya no bloquea ese avance.
