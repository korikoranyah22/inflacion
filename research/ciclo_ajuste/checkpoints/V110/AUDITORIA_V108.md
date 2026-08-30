# Auditoría V108 — rama social E0

## Alcance

Se siguió la prioridad social del handover V107: localizar, preservar y clasificar fuentes oficiales 2001–2003 sin empalmes retrospectivos ocultos. Los originales XLS/PDF/HTML no fueron modificados.

## Preservación y lectura

Se descargaron diez binarios oficiales: INDEC aporta EPH puntual/continua, pobreza puntual/continua, dos documentos metodológicos, una cuenta de generación del ingreso y el IPC-GBA empalmado; Trabajo aporta la definición y la serie histórica RIPTE. Cada archivo tiene ruta local, bytes y SHA-256 en el catálogo y el censo E0.

Los XLS se abrieron de manera de solo lectura. Los tres PDF relevantes se inspeccionaron por texto y por páginas renderizadas: RIPTE página 4; método histórico de pobreza páginas 1 y 4; Metodología 22 páginas 8, 17, 19 y 20. La tabla RIPTE y los cambios de metodología quedaron visualmente legibles.

## Relojes congelados

- EPH puntual: cinco ondas entre mayo de 2001 y mayo de 2003 para empleo, desocupación y subocupación.
- Pobreza puntual: cinco ondas para personas y hogares, pobreza e indigencia.
- EPH continua: 2003-S1 y 2003-S2 como bloque separado.
- RIPTE real: 66 meses julio de 2001–diciembre de 2006, deflactados con IPC-GBA oficial.
- CGI privada: puestos y masa salarial anual registrada/no registrada como contexto, no como reloj de hogar.

## Quiebres y restricciones

1. EPH puntual y continua no son un empalme automático.
2. Octubre de 2002 incorpora tres aglomerados.
3. Mayo/primer semestre de 2003 excluye Gran Santa Fe por inundación.
4. La pobreza 2001–2003 usa su método histórico; la reanudación 2016 cambia canastas, hábitos de consumo y regionalización.
5. RIPTE representa trabajadores registrados estables, no todos los ingresos de los hogares.
6. IPC-GBA no es IPC nacional.
7. Una fecha-base de un mes altera el veredicto de recuperación RIPTE a diciembre de 2006.

## Integridad

El catálogo sube a 225 entradas y 220 copias físicas/hash-válidas. La única brecha binaria catalogada y las siete acciones discovery anteriores permanecen; no se crea una brecha nueva. El panel Q4-2023 se replica sin cambios.

## Límite inferencial

La evidencia identifica una recuperación laboral más rápida que la pobreza y el salario real registrado estable. Eso falsifica un reloj social único, pero no prueba una cadena causal ni una transferencia neta hacia bancos. El monto fiscal realizado, la heterogeneidad bancaria y los relojes exactos de riesgo siguen abiertos.
