# Registro de recuperación V144

Fecha: 2026-08-30.

1. Se preservaron quince fuentes oficiales nuevas del SLU: manuales de conciliación, tablas básicas, cuentas, programación/pagos, C10, desafectaciones y taller 2017.
2. Los manuales fijan doce tablas exactas: BCUENTA, ACTA_FUE, ACTABAN_CTAESC, BGRUPMOVBCO, BMOVBCO, BMOVEXTERNO, AMOV_FORG, ACLB_MOB, BCODLIBBCO, BEMPRESA, BERROR_AUD y BPROCESO.
3. BMOVEXTERNO vincula código bancario externo con interno/grupo; AMOV_FORG vincula cuenta+movimiento con partida; la relación de gasto puede generar C55 y enviarlo a SIDIF Central.
4. Las tablas centrales se declaran sin historia. La ruta idónea pasa a ser backup/dump/snapshot 2006-2009, Consulta de Bajas, rehabilitaciones y migraciones.
5. El PDF del taller conserva capturas SLU v9.0 fechadas en 2006 y 26/11/2008; el ejemplo CUM023 es recurso y no se usa como target.
6. El manual C10 prueba la rama recurso, marca A/M, tipos REC/REG/COR/DES/CMP, cuenta, SIGADE, estados y transmisiones; se usa como control negativo de la rama C55/gasto.
7. Desafectaciones y cheques agregan controles C55-DEP/REP, contraasiento y estados C/R/E/F; no prueban por sí solos la fila objetivo.
8. No se localizaron filas pobladas 2008 de BMOVEXTERNO/AMOV_FORG, backup histórico, C55, extracto, Libro Banco ni respaldo target. No se envió ningún pedido ni presentación externa.
