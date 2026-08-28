# AUDITORÍA V82 — Ciclo de ajuste / red de pases

## Objetivo

Convertir la búsqueda posterior a V81 en rutas de recuperación más concretas, sin promover ninguna entidad sin evidencia individual/separada exacta.

## Hallazgos

### 1. BCRA raw archive: la familia binaria queda confirmada y la ventana puede ampliarse

El BCRA confirma que **Información sobre entidades financieras** publica un `.7z` con TXT para el total de entidades y un PDF de descripción. Una fuente académica reproducible que trabajó con el `.7z` de junio-2024 documenta que ese paquete contiene información histórica.

Consecuencia: V83 puede perseguir cualquier `.7z` verificado cuyo contenido histórico alcance septiembre-2023, no necesariamente un filename fechado exactamente 202309. No se inventó href ni nombre de archivo.

### 2. BNA 30/09/2023: apareció un control `Anexo` concreto en AGN 210/2023

La superficie oficial de AGN muestra `Resolución · Informe · Anexo`. La página devuelve 502 desde la sesión, así que se activó rescate manual únicamente para **Anexo**. Estado: `PENDING_USER_UPLOAD`.

### 3. BNA comparator: la estructura está validada

El full pack oficial BNA 30/09/2025 contiene estados separados y comparativas del período de 3/9 meses contra 30/09/2024. Eso demuestra que la ruta “full pack del año siguiente → comparativo 9M previo” es real como estructura documental. Aún falta el full pack 30/09/2024 para saber si imprime las cuatro patas 2023.

### 4. Banco Ciudad: existencia del separado 9M-2023 confirmada

El auditor del paquete consolidado oficial 30/09/2023 declara expresamente que emitió por separado un informe sobre los estados financieros separados condensados a la misma fecha y períodos. El binario separado no quedó expuesto por un href verificable en V82.

### 5. Ruta CNV mensual probada y descartada para four-leg

El PDF oficial septiembre-2023 de información financiera mensual remitida por BCRA sirve como compilación por entidad para emisores, pero no expone los cuatro códigos objetivo y no destraba BNA/Ciudad.

## Resultado strict

No promotion.

Cobertura strict Q4 four-leg: **23.54332498027319%**.

Gate de red cerrada: **NO**.
