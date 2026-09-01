# Fe de erratas y corrección metodológica V163

V162 afirmó que la cuenta `141222` no aparecía en diciembre de 2023 y calculó una diferencia de stock de **238.183 miles de pesos** contra `141144` solamente. La extracción completa de `00309.txt` demuestra que `141222 = 79.394` sí existe. Por lo tanto:

- stock crudo de diciembre: `28.978.965 + 79.394 = 29.058.359`;
- stock auditado: `29.217.148`;
- diferencia correcta de stock: **158.789**;
- ingreso crudo `511108`: `14.250.267`;
- ingreso auditado: `14.409.056`;
- diferencia de ingreso: **158.789**.

Los **238.183** de V162 eran la distancia entre el stock auditado y el capital crudo aislado, no una conciliación completa de stock. Los controles `BR162_02`, el README y el veredicto V162 quedan supersedidos por V163. Se conserva V162 como registro histórico del error; no se reescribe retroactivamente.

La igualdad de ambos residuos hace algebraicamente coherente un único asiento de cierre —débito al activo de pases y crédito al ingreso por 158.789—, pero no prueba que ese asiento haya existido. Sin diario, papel de trabajo, conciliación firmada o apertura de resultados 9M del emisor, la causa sigue sin autenticar y no hay promoción.
