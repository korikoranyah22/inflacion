# BCRA open-data entity archive — audit V82

## What is now primary-source confirmed

The current BCRA page **Información sobre entidades financieras** states that:

- the monthly publication contains information for each financial entity as well as aggregates;
- additionally, open data for **all entities** are supplied in a compressed `.7z`;
- its data are `.txt`;
- the package contains a PDF describing the content;
- this replaced the former CD *Información de Entidades Financieras*.

Official page:
`https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/`

This confirms that the desired binary family is real. V82 still does **not** have a verified direct href or filename for the archive, so no filename is guessed or registered as evidence.

## New historical-coverage clue

A 2025 Universidad de San Andrés master's thesis documents a reproducible extraction from the BCRA publication for **June 2024**, naming the source **Información de Entidades Financieras - Datos Abiertos (7z)** and stating that the archive **contains historical information**. It then builds variables directly from BCRA account codes.

Source:
`https://dspaceapi.live.udesa.edu.ar/server/api/core/bitstreams/0fa4cdf2-3f83-40ad-8b6c-8f6e9bfe0369/content`
Anexo A, final page (PDF p.58).

### Consequence

The recovery target can be broadened safely: it may not be necessary to recover the exact September-2023 `.7z` if a later **verified** archive (for example June-2024) contains the historical entity×account records for 2023-09.

This is a retrieval-route improvement, not four-leg evidence by itself. The archive still has to be downloaded and its schema/account records verified.

## Account taxonomy already frozen from V81

- `0301060100` — pass income, BCRA
- `0301060200` — pass income, other financial entities
- `0302030100` — pass expense, BCRA
- `0302030200` — pass expense, other financial entities

## Gate

No numeric promotion in V82.
