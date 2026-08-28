# GitHub-safe packing de fuentes grandes — V96

Objetivo: preservar físicamente fuentes >50 MiB dentro de GitHub sin depender de `.gitignore` para su única copia.

Los archivos crudos se reemplazaron por ZIP individuales trackeables. Cada ZIP contiene exactamente un original y fue verificado por SHA-256 después de extraerlo.

| Original | MiB | ZIP | MiB | Original SHA-256 |
|---|---:|---|---:|---|
| `data/fuentes/tasas/bcra/tas1_ser.txt` | 160.32 | `data/fuentes/tasas/bcra/tas1_ser.txt.zip` | 40.16 | `be3d0b8f57fd3531766c70d293af6734a5517610bfa2f5c994be78afba684410` |
| `data/fuentes/tasas/bcra/tas2_ser.txt` | 130.11 | `data/fuentes/tasas/bcra/tas2_ser.txt.zip` | 30.84 | `e71e938a9000c6c6ca78a2c9e58243de11aee1f875d14d78ecb4e9a01e98a181` |
| `data/fuentes/ciclo_ajuste/backfill_v96_round2/hist_bcra_din4_ser.txt` | 53.54 | `data/fuentes/ciclo_ajuste/backfill_v96_round2/hist_bcra_din4_ser.txt.zip` | 13.19 | `ba88bb6aeb80500ce1a5d8241628444abdb2a808be6974c56d901ebfd3b50bb8` |
| `research/ciclo_ajuste/inputs/issuer_retrieval/v95/binaries/007_118254.pdf` | 52.01 | `research/ciclo_ajuste/inputs/issuer_retrieval/v95/binaries/007_118254.pdf.zip` | 48.07 | `a3a4f91b8e3e9c668a0f572f865420de743ed09739310df77111f6b5c1b7b84e` |

Restauración local: ejecutar `RESTORE_LARGE_SOURCES.ps1` desde la raíz del repo. Los originales restaurados permanecen ignorados por Git; los `.zip` son las copias canónicas versionadas.

Esto no altera datos derivados ni el estado numérico V96.
