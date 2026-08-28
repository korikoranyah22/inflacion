# Repo checkpoint — Ciclo de Ajuste / V80 + BCRA septiembre 2023

Este bundle congela el estado del proyecto antes de continuar con V81.

Incluye:
- `repo/`: snapshot completo del repo fuente utilizado en esta rama de investigación.
- `research/`: bundle V80 íntegro, que ya arrastra los checkpoints/documentos anteriores relevantes.
- `inputs/bcra_2023_09/`: archivos oficiales BCRA recuperados manualmente para septiembre de 2023.
- `inputs/manual_recovery/`: binarios primarios BAPRO y Credicoop que destrabaron V78 y V75.
- `MANIFEST_SHA256.json`: tamaños y SHA-256 para integridad/reproducibilidad.

Nota: `Infbanc0923(1).xlsx` no se duplica porque es byte-a-byte idéntico a `Infbanc0923.xlsx` (mismo SHA-256).

Estado al checkpoint:
- cobertura estricta four-leg Q4: 23.543324980273%
- BAPRO: cerrado/promovido
- Credicoop: cerrado/promovido
- BNA: pendiente 9M separado o dataset regulatorio equivalente
- Banco Ciudad: pendiente base separada/individual o dataset regulatorio equivalente
- siguiente frente: explotar `InfBanc_Anexo.xlsx` como control agregado y continuar recuperación entidad×cuenta BCRA/BNA/Ciudad.
