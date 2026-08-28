# BCRA — archive histórico entity×account — V83

## Primario oficial

La página oficial `Información sobre entidades financieras` declara que:

- publica información de cada entidad y agregados;
- pone a disposición datos abiertos del total de entidades en un archivo `.7z`;
- el `.7z` contiene datos `.txt` y un PDF descriptor;
- reemplaza el antiguo CD de Información de Entidades Financieras.

URL de página:
`https://www.bcra.gob.ar/informacion-sobre-entidades-financieras/`

## Evidencia reproducible secundaria

Un trabajo final de Maestría en Finanzas de UDESA documenta que tomó el período junio-2024 de esa misma sección, específicamente `Información de Entidades Financieras - Datos Abiertos (7z)`, y señala que **contiene la información histórica**. También documenta el uso de cuentas contables del Plan de Cuentas incluido en el archivo de referencia.

Esto convierte el `.7z` junio-2024 en el mejor objetivo manual concreto disponible: no hay necesidad metodológica de inventar un nombre de archivo septiembre-2023 si un archive oficial posterior contiene la historia.

## Extracción requerida al recibirlo

Filtrar por período `2023-09`, entidad BNA/Ciudad y los cuatro códigos congelados:

- `0301060100` — ingreso pases BCRA
- `0301060200` — ingreso pases otras entidades financieras
- `0302030100` — egreso pases BCRA
- `0302030200` — egreso pases otras entidades financieras

Antes de usar números, documentar layout TXT, unidad, campo de período, identificador de entidad y semántica exacta del descriptor PDF.
