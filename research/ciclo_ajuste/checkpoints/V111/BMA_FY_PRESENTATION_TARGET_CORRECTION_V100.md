# Banco BMA / ex Banco Itaú — corrección del target FY, V100

V100 corrige la ruta de recuperación anual para evitar mezclar un balance regulatorio ordinario con un balance especial de fusión.

## CNV 2023

Para CUIT **30-58018941-1** la CNV lista:

- **#3119515** — 30/09/2023 — NIIF — balance **INDIVIDUAL** — periodicidad 3.
- **#3171909** — 31/12/2023 — NIIF — balance **INDIVIDUAL** — periodicidad 1. Este es el target FY ordinario compatible.
- **#3171902** — 31/12/2023 — NIIF — balance consolidado. Control-only.
- **#3177414** — 31/12/2023 — individual, pero documentación societaria/SEC identifica esta presentación como **Balance Especial Consolidado de Fusión** de Banco BMA para la absorción por Banco Macro. No debe sustituir #3171909 para el bridge strict FY.

## Decisión

```text
BMA_9M_TARGET = CNV #3119515
BMA_FY_STRICT_TARGET = CNV #3171909
BMA_FY_SPECIAL_MERGER_BALANCE_#3177414 = EXCLUDE_AS_STRICT_FY_SUBSTITUTE
```

Hasta recuperar los attachments reales de #3119515 y #3171909, BMA sigue `N/D_STRICT`. No se clasifica ningún raw de seis dígitos por nombre.
