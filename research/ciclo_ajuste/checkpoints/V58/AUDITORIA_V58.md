# AUDITORÍA V58 — IEF reconciliation gate

## 1. Pregunta
¿Podemos reconciliar los componentes Q3/Q4-2023 del IEF con los estados contables agregados post-2020 y, desde allí, abrir contraparte/sector?

## 2. Fuente objetivo exacta
La Tabla 2 del IEF diciembre 2024 fija la misma definición y denominador para Q3-23 y Q4-23: `% anualizado del activo neteado`.

Se verificaron exactamente los targets congelados:
`interest +2.1`, `passes +7.7`, `securities +7.3`, `CER -0.2`, `FX +11.3`, además de `monetary -9.2` y `ROA +9.0` pp.

## 3. Gate de bytes XLSX
Los endpoints oficiales de junio, septiembre y diciembre 2023 existen y son devueltos por las páginas oficiales como XLSX.
Este runtime no materializó sus bytes. Por lo tanto:
- no hay SHA256 inventado;
- no se infieren hojas/rangos de los archivos 2023;
- no se sustituye silenciosamente un workbook 2026.

El `InfBanc0526.xlsx` cacheado se inspeccionó sólo como schema analogue. Tiene 17 hojas (`IB`, `Índice`, `1..15`); la hoja 13 contiene ROA acumulado 3/12 meses por grupo, no subcuentas P&L.

## 4. Test nuevo: denominador implícito cruzado
V57 reconstruyó aproximadamente flujos trimestrales post-2020 desde estados acumulados, usando IPC mensual redondeado.
Para una línea que fuera idéntica a la del IEF:

`AN_implícito ≈ 4 × flujo_trimestral / (%a/100)`

Si varias líneas comparten la definición del IEF, deberían implicar aproximadamente el mismo activo neteado medio.

### Q3-2023
Anclas:
- egresos por intereses: 63.666 billones
- cargos por incobrabilidad: 67.362 billones
- gastos de administración: 63.870 billones
- resultado monetario: 63.568 billones
- mediana: 63.768 billones

P24 `Por Intereses` (ingreso) implica 208.908 billones = 3.28× la ancla.

### Q4-2023
Anclas:
- egresos por intereses: 93.071 billones
- cargos por incobrabilidad: 90.577 billones
- gastos de administración: 92.248 billones
- resultado monetario: 92.174 billones
- mediana: 92.211 billones

P24 `Por Intereses` (ingreso) implica 313.415 billones = 3.40× la ancla.

## 5. Resultado del test
`P24 Por Intereses == IEF Ingresos por intereses` queda **REJECTED** como mapeo directo.

La distancia no es marginal ni explicable por el redondeo de IPC: es superior a 3 veces el denominador común aproximado.

En cambio, egresos por intereses, resultado monetario y administración sí generan denominadores muy cercanos entre sí. Incobrabilidad también queda razonablemente próxima.

Esto localiza el problema: no es que toda P24 sea inutilizable. La incompatibilidad fuerte está en la construcción/reclasificación del lado de ingresos financieros positivos.

## 6. Lo que NO se infiere
No se atribuye la diferencia entre el `Por Intereses` broad y la línea IEF a CER, títulos, FX o pases sin fórmula contable.
No se usa la diferencia residual como share.
No se transforma stock por sector en flujo.
No se transforma tasa promedio en ingreso devengado.

## 7. Contrapartes
Pases mantiene identidad directa BCRA y 7.7 pp.
Para FX, títulos, CER e intereses sigue faltando una apertura de flujo compatible.
El share hogar directo sigue N/D.

## 8. Caveats
- Q4-23 no es ventana post-10/12 pura.
- Los flujos P24 de V57 son aproximados por redondeo del IPC mensual.
- El test de denominador es diagnóstico de compatibilidad, no una reconstrucción contable exacta.
