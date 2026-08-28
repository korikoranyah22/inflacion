# Fuentes V55

## Material local del usuario

- `inflacion-backup(2).zip` → `data/fuentes/tasas/bcra/es_series.txt`. Copia local de catálogo de series del BCRA.
- SHA256: `46089e8501001529f6a089e9981fb72f1e5f46e8817504ddc76f18996f28dd2b`
- Bytes: `5827774`

## Verificación web oficial (27-08-2026)

- BCRA, **Consulta de series estadísticas en formato TXT**: confirma formato `código;fecha;valor`, el endpoint `es_series.txt`, y que `din1_ser.txt` contiene balances consolidados, operaciones a futuro y situación de deudores. La propia página advierte que la versión TXT del catálogo está actualizada hasta 2021.
  https://www.bcra.gob.ar/consulta-de-series-estadisticas-en-formato-txt/
- BCRA, **Balances y agregados monetarios**: mantiene como archivo XLS `Operaciones a futuro. Estado de situación de deudores. Cuadro de resultados`.
  https://www.bcra.gob.ar/balances-y-agregados-monetarios/
- BCRA, **Informe sobre Bancos, diciembre de 2023**: confirma el contexto 2023 y los archivos Series de Datos/Anexo, pero sus bytes XLSX no pudieron materializarse en este runtime.
  https://www.bcra.gob.ar/publicaciones/informe-sobre-bancos-diciembre-de-2023/
- BCRA, **Préstamos y otros activos de las entidades financieras**: confirma endpoints de stocks por titular/emisor/UVA.
  https://www.bcra.gob.ar/prestamos-y-otros-activos-de-las-entidades-financieras/

## Regla de uso

La copia `es_series.txt` se usa sólo como **diccionario/metodología de cuentas**. No se usa como evidencia de valores 2023 ni de continuidad post-NIIF sin recuperar las observaciones correspondientes.
