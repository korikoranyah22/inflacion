# VEREDICTO V64 — Closed pass network coverage and sector mapping

## Estado

```text
V64_ICBC_FOUR_LEG_Q4 = IDENTIFIED_EXACT
FULL_FOUR_LEG_Q4_ENTITY_COUNT = 2_DIFFERENT_BASES
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_CLOSED_COVERAGE_AND_BASIS_HARMONIZATION_MISSING
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_PRODUCT_PROXY = RETAINED_NOT_STRICT_SECTOR
HOUSEHOLD_FLOW_TO_INSTITUTIONAL_SECTOR_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Hallazgo nuevo 1 — ICBC cierra cuatro patas Q4

Los estados oficiales 9M y FY 2023 de ICBC publican en Anexo Q ingresos y egresos de pases con separación BCRA / otras entidades financieras. Aplicando la regla congelada de moneda homogénea:

```text
Q4_DecPesos = FY_DecPesos - 9M_SepPesos × 1.532908152197
```

se obtiene, en miles de ARS constantes de diciembre de 2023:

```text
income_BCRA    = 199,396,505.327
expense_BCRA   = 0.000
net_BCRA       = 199,396,505.327

income_otherFI = 41,833.725
expense_otherFI= 943,870.859
net_otherFI    = -902,037.134
```

Equivale aproximadamente a **+199.397 mil millones ARS** netos contra BCRA y **-0.902 mil millones ARS** netos contra otras entidades financieras.

Esto es una posición de entidad, no una conclusión del sistema. Además, el filing usado es standalone/individual, por lo que no se mezcla con Ciudad consolidado para simular una red cerrada.

Fuentes: https://www.icbc.com.ar/wcm/connect/4de3ed09-cb4e-4064-b6a5-0aa3f0bca5fd/Estados%2BFinancieros%2BICBC%2B202309_ESPA%C3%91OL%2BLEGALIZADO.pdf?CVID=oNG1sHj&MOD=AJPERES ; https://www.icbc.com.ar/wcm/connect/09254af5-2d9a-4742-bec0-bbd0018305d5/Estados%2BFinancieros%2BICBC%2B202312_ESPA%C3%91OL%2BLEGALIZADO.pdf?CVID=oUU1Wae&MOD=AJPERES

## Hallazgo nuevo 2 — el mapping hogar mejora, pero bloquea una identidad fuerte

El BCRA publica series mensuales de préstamos por tipo de titular y, específicamente para hipotecarios/prendarios, aperturas que distinguen personas humanas y jurídicas. Esto permite elevar una conclusión negativa importante:

```text
HIPOTECARIOS_OR_PRENDARIOS_AS_100PCT_HOUSEHOLD = REJECTED_AS_IDENTITY
```

La existencia de una apertura PH/PJ prueba que el nombre del producto no alcanza para convertir el flujo de Anexo Q en sector institucional hogar. Para personales y tarjetas hay evidencia directa de financiamiento a personas en CENDEU/inclusión financiera, pero no se identificó una fuente que haga equivalente **todo** el renglón contable de Anexo Q a personas/hogares.

Por tanto:

```text
HOUSEHOLD_PRODUCT_PROXY = SUPPORTED_DESCRIPTIVE_DIRECT_CONTRACT_CANDIDATE
STRICT_HOUSEHOLD_SECTOR = NO
HOUSEHOLD_INTEREST_FLOW_POINT_ESTIMATE_SYSTEM = N/D
```

Fuentes: https://www.bcra.gob.ar/prestamos-y-otros-activos-de-las-entidades-financieras/ ; https://www7.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/BoletinEstadistico/boldat202505.pdf ; https://web2.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/bolmetes.pdf ; https://www.bcra.gob.ar/conocer-que-es-la-central-de-deudores/

## Implicancia para la tesis bancaria

V64 agrega contraparte contractual exacta para una entidad importante, pero **no** convierte el +7,7 pp de pases del IEF en BCRA ni permite sumar posiciones de bancos con bases contables incompatibles. El strict floor revocado sigue revocado.

La investigación avanza porque reduce N/D a nivel entidad y fortalece los límites metodológicos a nivel sistema.
