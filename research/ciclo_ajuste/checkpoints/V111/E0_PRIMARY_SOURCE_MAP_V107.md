# Mapa primario E0 2001–2003 — V107

## Corrección material respecto de V106

El bootstrap V106 clasificó E0 como si el repositorio sólo conservara una planilla larga de tasas. El censo binario y de hojas de V107 demuestra que esa descripción era incompleta: antes de descargar nada ya existían siete fuentes oficiales BCRA que cubren 2001–2003, entre ellas balances/resultados, préstamos y depósitos por titular privado y jurisdicción pública, tenencias de títulos y archivos diarios de activos/pasivos.

V107 agrega diez originales oficiales: cuatro PDF BCRA y seis textos legales InfoLeg. Las 17 fuentes están inventariadas con ruta, bytes, SHA-256, cobertura y quiebres en `E0_LOCAL_PRIMARY_SOURCE_CENSUS_V107.csv`.

## Qué queda establecido

- **Cronología institucional:** hay base primaria preservada para restricciones de diciembre de 2001, emergencia/salida del régimen, pesificación, conversión de deuda pública, canjes y compensaciones. No existe un `t0` único: deben coexistir fechas de anuncio, norma, publicación, implementación y reacción de mercado.
- **Hogares y crédito:** el BCRA permite separar préstamos y depósitos privados por tipo de titular, incluidas personas físicas, y observar tasas. Eso mide stocks/condiciones financieras; no sustituye salarios, empleo, pobreza, consumo ni bienestar.
- **Riesgo y bancos:** los balances históricos contienen clasificación de deudores, resultados, capital y datos físicos. Hay quiebres severos por moneda constante, entidades revocadas/no informantes, fideicomisos y cambios de clasificación.
- **Estado/BCRA:** las normas y series de títulos documentan instrumentos compensatorios y absorción pública. Falta conciliar autorización, emisión, devengamiento, valuación, recepción y pago para obtener un monto fiscal realizado comparable.
- **Falsificador bancario:** el BEF BCRA de 1S 2004 registra pérdidas récord en 2002, caída real de depósitos de 42% hasta el piso, caída real de 37% del patrimonio neto consolidado durante dos años y recuperación apenas parcial en 2003. Esto contradice una versión simple de “los bancos ganaron inmediatamente”, pero no distribuye todos los costos finales.

## Reglas de uso

1. No sumar stocks, valuaciones y flujos como si fueran la misma magnitud.
2. No etiquetar una compensación jurídica como ganancia neta sin restar pérdidas, costos, deterioros y aportes de capital.
3. No usar depósitos totales como sinónimo de depósitos de hogares; cuando corresponda, usar el desglose por titular.
4. No empalmar 2001–2003 sin registrar moneda, inflación, quiebre contable, universo de entidades e imputaciones.
5. Mantener `PRIMARY/PARTIAL`: el mapa documental está construido, pero la reconstrucción comparable y la incidencia causal no.

## Próximos vacíos P0

- INDEC: salarios, empleo, pobreza y metodología/vintages 2001–2003.
- BCRA: diccionario y normalización de archivos diarios; relojes exactos de mora, previsiones y quebrantos.
- Tesoro/AGN: monto fiscal realizado y auditoría de cada mecanismo compensatorio.
- Emisores/CNV/AGN: heterogeneidad entre bancos materiales y conciliación con agregados BCRA.
- Sensibilidad temporal: tabla de ventanas para anuncio, norma, implementación, piso y recuperación.

Hasta resolver esos puntos, E0 puede refutar afirmaciones simples y sostener una cronología documental, pero no validar una transferencia causal neta hogares → bancos.
