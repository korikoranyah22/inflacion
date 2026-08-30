# Reconstrucción fiscal E0 · V127

## Hallazgo principal

La línea Q4 `Recompra Bonos del Canje - Dto. 1735/04` deja de estar sin especie. Entre 30/09 y 31/12/2008, `Par en Pesos` y `Cuasipar en Pesos` conservan su nominal nativo; su variación en miles de USD se explica por el tipo de cambio 3,135→3,452. El único nominal que cae es `Discount en Pesos`: ARS 15.012,460651m→ARS 12.263,982382m, reducción ARS 2.748,478269m.

El informe oficial del Decreto 1735/04 identifica para el año de referencia 2006 una recompra de `Discount en Pesos 5,83% 2033`, ISIN `ARARGE03E121`, por VNO ARS 2.748,50m y valor efectivo ARS 1.415,50m. El delta entre el VNO derivado y el informe redondeado es ARS -0,021731m (0,00079%).

Al multiplicar el VNO reducido por el factor actualizado/nominal del Discount al 30/09, 1,7186005287, se obtienen ARS 4.723.536,206 miles: delta ARS 0,016 miles frente al renglón oficial ARS 4.723.536,19 miles. Al dividir por el TC 3,135 se reproduce USD 1.506.710,11 miles al redondeo publicado.

## Control SIGADE

La base SIGADE Q3 preservada contiene `Discount en $ ajustado por CER` con saldo USD 8.229.799.942,95 y TC ARS/USD 3,135. El saldo coincide con A.12.2 H31 dentro del redondeo visible. La página oficial no publica una base Q4 equivalente para 31/12/2008; el XLS Q4 sigue siendo el extremo final.

## Separación de magnitudes

- VNO ARS 2.748,50m: nominal adquirido reportado.
- Valor efectivo ARS 1.415,50m: consideración agregada reportada.
- Baja contable ARS 4.723,53619m / USD 1.506,71011m: stock actualizado eliminado.

No son cifras aditivas ni intercambiables.

## Frontera probatoria

Se cierra la asignación agregada Q4 a especie y tramo: Discount en Pesos, año de referencia 2006. Siguen abiertos fecha y vendedor de cada operación, matching y asiento Caja, informe de liquidación, orden/débito BCRA y beneficiarios finales. GDP Units continúan expresamente excluidas del cuadro contable. `CLOSED_NETWORK_GATE=NO`.
