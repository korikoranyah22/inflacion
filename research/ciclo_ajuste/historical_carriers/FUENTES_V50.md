# Fuentes V50

## 2014
- BCRA, Informe sobre Bancos junio 2014:
  https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/InfBanc0614.pdf
  - Q2 ROA 3,4%a vs 2,6%a;
  - margen 10,4%a, +1,5 pp;
  - BCRA atribuye el mayor ROA fundamentalmente a títulos.
- BCRA, BEF / Primer Semestre 2015:
  https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/bef0115e.pdf
  - tabla anual 2013/2014 y semestres con componentes completos.
  - 2013 ROA 3,4; 2014 4,1.
  - 2013 títulos 2,6; 2014 4,0.
  - 2013 FX 1,3; 2014 1,2.

## 2018
- BCRA, Informe sobre Bancos junio 2018:
  https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/InfBanc0618.pdf
  - H1 ROA 3,4, +0,4 pp i.a.
  - margen 10,7, +0,4 pp.
  - servicios 2,2, -0,7 pp.
  - incobrabilidad 1,3, +0,3 pp de costo.
  - gastos administración 6,5, -0,7 pp de costo.
  - positivos del margen: títulos, CER, intereses, FX.
  - offsets: egresos intereses/CER y menores pases.
- El residual +0,3 pp en V50 es una identidad derivada para reconciliar ROA y corresponde al agregado no descompuesto de impuestos/resto/ORI. No se presenta como valor leído directamente.

## 2023
- BCRA, IEF II-2024:
  https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/IEF0224.pdf
  Tabla 2, Q3-23 vs Q4-23, moneda homogénea.
  Permite bridge exacto de margen, intereses, CER, FX, pases, títulos, monetario, servicios, incobrabilidad, gastos, impuestos y ROA.

## Auditoría visual PDF
Se intentaron screenshots de las páginas relevantes de los PDFs BCRA mediante el runtime web. El backend devolvió cache/error de render; no se utilizó OCR ni se inventaron valores visuales. Se conservaron únicamente valores extraídos textualmente/tabularmente por las fuentes.

## Regla
- componente gap = observado - benchmark;
- no doble contar subcomponentes dentro del margen;
- no forzar reconciliación cuando faltan benchmarks exactos;
- Q4-23 = abnormal component window, no post-10Dec causal window.
