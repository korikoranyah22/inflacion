# Auditoría de cobertura y presentación de fuentes · v149

Fecha de revisión: 22 de agosto de 2026.  
Archivo auditado: `index.html`.  
Alcance: las 33 pestañas visibles del dashboard.

## Qué audita este documento

Esta revisión responde una pregunta acotada: **¿cada pestaña permite identificar de dónde salen sus datos y dónde se documentan sus transformaciones?**

Los criterios mínimos son:

1. existe una ficha visible de fuentes y trazabilidad dentro del tab;
2. la ficha contiene al menos una referencia resoluble;
3. las publicaciones de origen, los archivos/series y las auditorías/cálculos se distinguen visualmente;
4. las rutas locales de auditoría y archivos existen en el repositorio;
5. cuando un tab sintetiza otros, conserva un mapa de fuentes propio y remite al panel especializado;
6. una reconstrucción, escenario o cálculo derivado no se presenta como si fuera un dato publicado.

Esto **no** reemplaza una nueva auditoría estadística completa de cada valor ni una comprobación permanente de disponibilidad de todos los servidores externos. La consistencia numérica se documenta en las auditorías temáticas enlazadas.

## Resultado

- Pestañas revisadas: **33**.
- Pestañas con ficha normalizada visible: **33**.
- Pestañas sin ninguna referencia visible después de la corrección: **0**.
- Rutas locales nuevas o reutilizadas verificadas en disco: **16 de 16**.
- Presentación común: publicación/institución de origen, dato/serie/archivo y auditoría/método/cálculo.

## Carencias encontradas y corregidas

### 1. Morosidad

No tenía un bloque de fuentes visible, aunque sus archivos estaban registrados en `data/fuentes/FUENTES.csv` y existía una auditoría reproducible.

Se añadieron enlaces directos a:

- Informe sobre Bancos y series de mayo de 2026;
- informe y series PNFC/Fintech de junio de 2026;
- Informe de Inclusión Financiera y su anexo;
- `data/derivados/morosidad/AUDITORIA_MOROSIDAD.md`;
- manifiesto general con fechas y SHA-256.

La nota de cobertura separa saldo irregular bancario, mora PNFC mayor a 90 días y snapshots de personas.

### 2. “Lo que te robó Milei”

El tab remitía a paneles especializados, pero no tenía un mapa de fuentes propio. Eso dificultaba auditar la cuenta madre sin abandonar primero la pestaña.

Se añadió una ficha directa para:

- Índice de salarios, CSV oficial, EPH urbana e IPC de INDEC;
- tasas BCRA para la pinza financiera;
- SEC para beneficios documentados de Mercado Libre;
- Boletín Oficial para SIDE;
- Senado para dietas;
- auditoría de la cuenta de $18,43 billones;
- auditoría de la pinza financiera;
- manifiesto general de archivos.

La ficha aclara que los componentes no forman automáticamente una única identidad contable.

### 3. Grandes fortunas

WID estaba mencionado como contexto, pero no tenía un enlace visible. Se añadió la ficha país del World Inequality Report 2026. También se normalizaron las rutas locales de ARCA, Aporte Solidario, AFIP y la auditoría reproducible para que funcionen tanto en `index.html` como en el snapshot dentro de `data/`.

### 4. EMAE

Las cuatro fuentes de datos estaban visibles, pero faltaba acceso directo a la auditoría que documenta empalme poblacional, per cápita, ventana espejo y drawdowns. Se agregó `AUDITORIA_EMAE.md`.

### 5. Péndulo del poder económico

La capa de producción mostraba fuentes, pero la trazabilidad de finanzas, vivienda, fiscal y activos quedaba repartida entre otros tabs y documentos. Se añadió una ficha global por capa con las seis auditorías del Péndulo y sus fuentes institucionales principales.

### 6. Rutas y Turismo

Ya tenían fuentes y auditorías completas, pero con componentes visuales propios. Se incorporaron a la misma ficha de trazabilidad sin eliminar sus explicaciones de cobertura.

### 7. La historia del dashboard

El nuevo tab es un relato editorial en primera persona: no introduce una serie estadística adicional. Su ficha distingue esa condición y remite al repositorio y a las auditorías globales de fuentes y escalas. Los documentos internos del proceso de rediseño no se presentan como fuentes. Los importes destacados funcionan como accesos narrativos a cálculos ya documentados en los paneles temáticos; no sustituyen sus fuentes ni forman por sí solos una identidad contable nueva.

## Inventario final por pestaña

La columna “referencias” cuenta enlaces temáticos dentro de la ficha principal del tab, sin contar botones de navegación ni el enlace repetido a esta auditoría global.

| Pestaña | Referencias | Estado |
|---|---:|---|
| La historia del dashboard | 3 | Completa · relato editorial con rutas a auditorías |
| Poder adquisitivo | 18 | Completa |
| Tasas e inflación | 8 | Completa |
| Inflación por presidencia | 3 | Completa |
| Pobreza: nivel absoluto | 4 | Completa |
| Asistencia social / transferencias | 7 | Completa |
| Desigualdad (Gini) | 6 | Completa |
| Más allá de la pobreza | 6 | Completa |
| ¿Cuánto necesita una familia? | 6 | Completa |
| Riesgo país | 2 | Completa con fuente secundaria declarada |
| Índice Big Mac | 5 | Completa |
| Precios mayoristas | 5 | Completa con salvedad metodológica visible |
| Salud y educación | 6 | Completa |
| Consumo | 34 | Completa |
| Trabajo | 9 | Completa |
| Inversión | 4 | Completa |
| Vivienda | 10 | Completa |
| Crecimiento | 5 | Completa |
| Actividad real / EMAE | 5 | Completa |
| Morosidad | 8 | Completada en v149 |
| Péndulo del poder económico | 11 | Completada por capa en v149 |
| Resultado fiscal | 5 | Completa |
| Balanza comercial | 4 | Completa |
| BCRA · reservas y dólar | 5 | Completa |
| Espiral de deuda | 4 | Completa |
| Programa y escenarios | 13 | Completa; escenarios identificados |
| Grandes fortunas | 5 | Completada con cita WID en v149 |
| Lo que te robó Milei | 11 | Completada con mapa propio en v149 |
| Privilegios fiscales | 11 | Completa |
| La casta | 21 | Completa |
| Rutas · ¿Público o privado? | 7 | Completa |
| Vacaciones · Turismo | 7 | Completa |
| Deuda pública | 5 | Completa |

## Salvedades que deben conservarse

- **Riesgo país:** el EMBI+ es propiedad de J.P. Morgan y el histórico abierto usa una reproducción pública secundaria, rotulada como tal.
- **Big Mac:** el dataset de The Economist y las interpretaciones del dashboard son capas distintas.
- **Mayoristas:** los cambios de base y la normalización de unidades del tramo histórico siguen documentados.
- **Péndulo:** sus capas no deben sumarse en una sola cifra factual.
- **Morosidad:** saldo bancario, saldo PNFC y personas no comparten denominador.
- **Lo que te robó Milei:** una asignación presupuestaria, un beneficio documentado y un contrafactual salarial no son la misma clase de medida.

## Implementación de referencia

- Estilo común: `#source-register-v149-style`.
- Normalización y comprobación: `#source-register-v149-script`.
- Cada tab recibe `.source-register` y `data-source-coverage="ok"`.
- Las rutas locales usan `data-source-path` y `sourceProjectAsset()` para funcionar desde raíz o snapshot.
- El arreglo de comprobación de ejecución queda expuesto como `SOURCE_COVERAGE_AUDIT_V149` en el contexto de la página.

## Pruebas mínimas de aceptación

- [x] 33 tabs detectados.
- [x] 33 fichas `.source-register` generadas.
- [x] 0 fichas con `data-source-coverage="missing"`.
- [x] Toda ficha contiene al menos una referencia visible.
- [x] Las 16 rutas `data-source-path` existen en disco.
- [x] Morosidad muestra ocho referencias.
- [x] Lo que te robó Milei muestra once referencias.
- [x] Presentación comprobada en escritorio y a 390 px.
