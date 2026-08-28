# Arqueología de backups — tanda 1 (post-V96)

**Fecha:** 2026-08-28  
**Estado de investigación:** V96 sin cambios numéricos  
**Objetivo:** verificar si fuentes binarias hoy marcadas como faltantes estaban ocultas en checkpoints/archives antiguos y confirmar que los BCRA raw históricos no se hubieran perdido.

## Tanda examinada

- **20 carriers** entregados por la usuaria: **15 ZIP + 5 7z**.
- Los ZIP abarcan checkpoints/frontiers V70–V89, incluidos V72 AGN, V75 Credicoop, V78 BAPRO y el bundle repo V80.
- Los 7z abarcan Sep-2023, Dic-2023 y Jun-2024 BCRA, incluidos aliases duplicados (`sep2023`, `dic2023`).
- Todos los ZIP pasan `ZipFile.testzip()` sin miembro corrupto.

## Resultado criptográfico

Se recorrieron recursivamente también los ZIP contenidos dentro de los ZIP históricos.

- Ocurrencias de binarios fuente dentro de ZIP históricos (`pdf/xls/xlsx/7z`): **838**.
- SHA-256 únicos entre esas ocurrencias: **415**.
- Ocurrencias cuyo SHA-256 ya existe en el repo V96 auditado: **838/838**.
- SHA-256 únicos nuevos aportados por esta tanda: **0**.

**Conclusión fuerte:** la tanda 1 no contiene ningún PDF/Excel/7z fuente que se haya perdido del repo actual. Todo binario fuente cargado dentro de esos ZIP históricos ya está preservado byte-a-byte en V96.

## BCRA 7z

Los 7z entregados fuera de los ZIP también fueron hasheados: 

- `sep2023(1).7z` = `202309d.7z` actual, SHA-256 `31a0a315444496d4336695b6bd48deb562456df10e47fbc46de3703a77528bdb`.
- `dic2023(1).7z` = `202312d.7z` actual, SHA-256 `60ef86addba5e6646a2bfd42853ca077ea7970e9fa6effe54f1179049868f0d4`.
- `202406d(3).7z` = `202406d.7z` actual, SHA-256 `316c6c80f1206b08e13753bb4ac8b8ffe6239fbbf523dc7bddf9154e0e95385d`.

Por lo tanto los raw regulatorios de esos tres cortes están respaldados exactamente; los aliases no aportan una variante distinta.

## Cruce contra la cola de faltantes

La cola preexistente conserva **49** huecos (**20 P0, 18 P1, 11 P2**).

- La búsqueda por basename normalizado de los 49 targets contra los **17892** miembros inventariados de la tanda produjo **0 matches**.
- Como además **todos** los binarios históricos de la tanda ya existen por SHA-256 en el repo actual, esta tanda **no puede aportar un binario nuevo** para cerrar esos huecos.
- Esto no elimina la posibilidad de que algún gap del screening original sea en realidad un archivo ya existente con nombre completamente distinto; resolver eso requiere identificación por contenido/documento, no sólo arqueología de carriers. En esta tanda no apareció evidencia documental que permita reasignar uno de esos hashes a un gap con seguridad.

## Qué confirma esta tanda

Los rescates históricos de AGN/BNA, Credicoop, BAPRO y el paquete BCRA V80 que aparecen en estos checkpoints **no se perdieron** durante las consolidaciones posteriores: sus binarios ya están en el repo V96 actual.

Los P0 tardíos (NBSF/NBER/San Juan/Santa Cruz/BICE issuer/BIND/NBCH/La Pampa/BPN/Formosa/BST/CMF) **no aparecieron como binarios nuevos** en esta tanda; siguen necesitando backfill desde otros zips o desde sus URLs originales.

## Evidencia machine-readable

- `ARCHAEOLOGY_BATCH1_CARRIER_FINGERPRINTS.csv`: hash/tamaño/estado de cada carrier recibido.
- `ARCHAEOLOGY_BATCH1_ARCHIVE_INVENTORY.csv`: inventario recursivo de miembros.
- `ARCHAEOLOGY_BATCH1_SHA256_BINARY_VALIDATION.csv`: comparación SHA-256 de cada binario histórico contra el repo actual.
- `ARCHAEOLOGY_BATCH1_GAP_TEXT_CONTEXT.csv`: ocurrencias documentales de los 49 gaps dentro del repo.
- `SOURCE_BACKUP_GAPS_V96_AFTER_BATCH1.csv`: cola posterior a tanda 1; no se cerró ningún gap.

**Veredicto tanda 1:** conservación histórica de lo que contenían esos backups = **OK**; recuperación de gaps actuales = **0**. Seguir con tandas anteriores/alternativas antes de recurrir a re-descarga web.
