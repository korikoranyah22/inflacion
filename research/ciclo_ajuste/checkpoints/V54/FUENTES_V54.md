# Fuentes V54

## Primarias BCRA verificadas

- Préstamos y otros activos de las entidades financieras — página oficial con enlaces a `perser_priv.xls`, `perser_pub.xls`, `titpubser.xls` y `finuva_mensual.xls`.
- Depósitos y otros pasivos — página oficial con enlaces a `perser_priv.xls`, `perser_pub.xls` y `depuva_mensual.xls`.
- Informe sobre Bancos, diciembre de 2023 — página oficial y PDF; publica `Infbanc1223.xlsx` y Anexo Estadístico.
- Balances y agregados monetarios — página oficial con `baldethis.xls` para operaciones a futuro, situación de deudores y cuadro de resultados.
- Información sobre entidades financieras — el BCRA declara que ofrece datos abiertos mensuales del régimen informativo en `.7z`, TXT más PDF de layout.
- Consulta de series estadísticas TXT — catálogo y archivos abiertos de activos/pasivos.
- Informe sobre Bancos, diciembre de 2018 / glosario — definición contable de `Diferencias de cotización` y `Resultado por títulos valores`.

## Definiciones críticas usadas

1. **Diferencias de cotización** no es una cuenta puramente de mark-to-market: incluye actualización mensual de activos/pasivos en moneda extranjera y también resultados de compra/venta de moneda extranjera.
2. **Resultado por títulos valores** mezcla instrumentos y tratamientos; para títulos públicos incluye renta devengada, diferencias de cotización, acrecentamiento por TIR, ventas y previsiones por desvalorización.
3. Los XLS por titular/emisor publicados en las páginas estadísticas son series de **saldos/stock**. No pueden transformarse en shares de resultado sin un bridge de devengamiento/resultado.

## Gate de bytes

Los endpoints binarios fueron identificados desde páginas oficiales, pero el runtime de esta sesión no pudo resolver/descargar sus bytes. Por eso `SHA256 = N/D` y V54 no eleva ningún split dependiente de esos archivos.
