# Source references — V83

## Upload de Miyu

- `2023-210-Informe CC 2(3).pdf`
  - SHA-256 `563b4e6f30ff13bd7a8cec6f794ad90a64383866cf907c434d9c7841a703ffd5`
  - byte-a-byte igual a `research/ciclo_ajuste/inputs/manual_recovery/bna_agn/2023-210-Informe CC 2.pdf`
  - informe consolidado de tres páginas; no contiene el paquete largo separado.

## BCRA oficial

- Información sobre entidades financieras:
  `https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/`
  - información individual y agregada;
  - datos abiertos total entidades en `.7z`;
  - TXT + PDF descriptor.

## Evidencia de historicidad del `.7z`

- Universidad de San Andrés, Paula Carolina González, Trabajo Final de Maestría en Finanzas (2025):
  `https://dspaceapi.live.udesa.edu.ar/server/api/core/bitstreams/0fa4cdf2-3f83-40ad-8b6c-8f6e9bfe0369/content`
  - Anexo A, p.57 del PDF: identifica el archive junio-2024 de BCRA como `Información de Entidades Financieras - Datos Abiertos (7z)` y dice que contiene información histórica.
  - fuente secundaria para estrategia de retrieval; los valores finales deben salir del archive oficial.

## BNA — estructura separada 2025

- Full pack BNA 30/09/2025:
  `https://www.bna.com.ar/Downloads/Institucional_BalancesTrimestrales_2025-09%20EEFF%20para%20subir%20a%20la%20WEB.pdf`
  - sección separada, Nota/estructura p.127 del PDF;
  - líneas documentales: remite aperturas de `Ingresos por intereses` (Nota 25) y `Egresos por intereses` (Nota 26) a estados consolidados porque la apertura resulta representativa y coincide o no difiere significativamente de la separada.
  - consecuencia: no asumir que un comparator 2024 imprimirá four-leg separado.

## AGN — 30/09/2024 BNA

- Informe 187/2024, título oficial: Estados Financieros Intermedios Consolidados Condensados y Separados Condensados al 30/09/2024 — Banco de la Nación Argentina.
  - confirma existencia del artefacto 2024; binario largo aún no recuperado.

## Códigos BCRA congelados

- `0301060100` ingreso pases BCRA
- `0301060200` ingreso pases otras EF
- `0302030100` egreso pases BCRA
- `0302030200` egreso pases otras EF
