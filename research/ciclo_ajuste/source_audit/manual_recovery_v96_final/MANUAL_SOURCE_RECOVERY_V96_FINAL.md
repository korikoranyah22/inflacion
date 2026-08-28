# Manual source recovery V96 — cierre final

Fecha: 2026-08-28

Esta tanda cierra los gaps físicos restantes sin cambiar cifras analíticas de V96.

| ID | Estado | Path local | SHA-256 |
|---|---|---|---|
| `bcra_boldat202505_tipo_titular` | RECOVERED_MANUAL_VERIFIED | `/data/fuentes/manual_recovery_v96_final/bcra_boldat202505_tipo_titular.pdf` | `0b466df43189cfef6e96083b5fbe47c28570f933fa108aaae7099fb1a1a73b52` |
| `bcra_pases_esquema_20231218` | RECOVERED_MANUAL_VERIFIED | `/data/fuentes/manual_recovery_v96_final/bcra_pases_esquema_20231218_web_snapshot.pdf` | `5a5fcb71b6d3ccdb48cbd7b237ddf98320cc9282bc03248eb9d399f4828f116e` |
| `bcra_prestamos_activos_sector_mapping` | RECOVERED_MANUAL_VERIFIED | `/data/fuentes/manual_recovery_v96_final/bcra_prestamos_activos_sector_mapping.xls` | `484bd080a2d35c635daed23e7f9c087b01eebeac0bf0ab6a49515f31f6de7a3a` |
| `capital_humano_auh_alimentar_cba_2024` | RECOVERED_MANUAL_VERIFIED | `/data/fuentes/manual_recovery_v96_final/capital_humano_auh_alimentar_cba_2024_web_snapshot.pdf` | `cdc86d5c3b1283ad4705ed3ebd731cfda3493cf1455c632aba79fd828373b4dc` |
| `indec_supermercados_archivo` | RECOVERED_MANUAL_VERIFIED | `/data/fuentes/manual_recovery_v96_final/indec_archivo_historico_y_discontinuidades_bundle.zip` | `08bc2123a58f0562c7eefa88b1731711e35eb04ce8963f3c5ff4c0dcc09a1c0c` |
| `indec_supermercados_tema` | RECOVERED_MANUAL_VERIFIED | `/data/fuentes/manual_recovery_v96_final/indec_encuesta_supermercados_download_bundle.zip` | `d221978a04bfd3590901a9568418b41813ca684d1003ae3c4bbbcee8eab29d43` |
| `santander_9m2023_comision_fiscalizadora_supplement` | SUPPLEMENT_PRESERVED_VERIFIED | `/data/fuentes/manual_recovery_v96_final/santander_9m2023_comision_fiscalizadora.pdf` | `4cfe775561c3733562ec1975925e73f8727780274e4f8e8715e89da1d92b783a` |
| `santander_9m_official_cnv_equivalence` | OFFICIAL_CNV_BYTE_IDENTICAL_TO_PRESERVED_BINARY | `/data/fuentes/ciclo_ajuste/backfill_v96/santander_eeff_9m2023_sep_mirror.pdf` | `dd043602ac6fe0685e3d683e2d26e39650c5411548a0cb062b3ad8ff542f958a` |
| `santander_fy_official_cnv_equivalence` | OFFICIAL_CNV_BYTE_IDENTICAL_TO_PRESERVED_BINARY | `/data/fuentes/ciclo_ajuste/backfill_v96/santander_eeff_fy2023_aq_mirror.pdf` | `3f324e4c932b6e33f8da9abba5e967ca8c9ffacc8d253637f9e8f3783d73faec` |

## Santander

Los EEFF separados 9M y FY descargados manualmente desde CNV resultaron byte-idénticos a los binarios ya preservados desde el mirror regulatorio. No se duplicaron. Se actualizó la provenance del catálogo y se preservó el informe de Comisión Fiscalizadora como adjunto suplementario.

## Todo Sobre la Mora

Se mantiene intacto como referencia/objeto de análisis y se conservan los artefactos históricos existentes. La única corrección es que deja de contarse como un gap físico: si una afirmación requiere respaldo, la unidad de preservación son sus fuentes primarias, no una copia obligatoria del sitio secundario.

## XLS duplicado

`AUH + Tarjeta Alimentar cubren 100% de la CBA.xls` y `Préstamos y otros activos de las entidades financieras.xls` tienen el mismo SHA-256 `484bd080a2d35c635daed23e7f9c087b01eebeac0bf0ab6a49515f31f6de7a3a`. Se conserva una única copia canónica bajo el ID BCRA; el alias con nombre de AUH no se usa como evidencia de Capital Humano.
