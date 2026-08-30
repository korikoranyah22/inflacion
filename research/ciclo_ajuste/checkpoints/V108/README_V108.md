# V108

V108 cierra la primera reconstrucción social primaria del episodio E0 2001–2003. Preserva diez fuentes oficiales nuevas, congela relojes de empleo, pobreza e ingreso registrado real y mantiene intacto el panel microbancario.

## Delta material

- El censo E0 sube de **17 a 27 fuentes primarias preservadas**.
- Se incorporan cuatro XLS EPH, dos PDF metodológicos de pobreza, un XLS de cuentas nacionales, la página/serie oficial RIPTE y el empalme histórico IPC-GBA.
- La EPH puntual congela empleo, desocupación y subocupación para mayo/octubre 2001–mayo 2003.
- Pobreza e indigencia quedan separadas por personas/hogares y por régimen puntual/continuo.
- El RIPTE real contiene **66 meses** entre julio de 2001 y diciembre de 2006, con fórmula, numerador y deflactor auditables.
- Con diciembre de 2001 = 100, el RIPTE real toca 70,730514 en abril de 2003 y recupera en diciembre de 2006; con noviembre de 2001 = 100 no recupera al cierre de 2006.
- Los quiebres EPH, cobertura geográfica, método de pobreza, población RIPTE y geografía del IPC se congelan en una matriz explícita.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k** sin reconciliar;
- no se identifica transferencia causal neta hogares → bancos.

## Estado de fuentes

- entradas catalogadas: **225**;
- copias locales físicas: **220**;
- copias con hash exacto: **220**;
- brecha binaria catalogada: Banco Rioja FY (P1);
- acciones discovery sin binario propio: siete.

## Leer primero

1. `VEREDICTO_V108.md`
2. `AUDITORIA_V108.md`
3. `E0_SOCIAL_RECONSTRUCTION_V108.md`
4. `E0_SOCIAL_RECOVERY_SUMMARY_V108.csv`
5. `E0_SOCIAL_METHOD_BREAKS_V108.csv`
6. `E0_SOCIAL_CLOCKS_V108.csv`
7. `E0_REAL_RIPTE_MONTHLY_V108.csv`
8. `HISTORICAL_EPISODE_MATRIX_2001_2026_V108.csv`
9. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V108_A_V109.md`
10. `qa_v108.py`

V108 mejora la cobertura descriptiva de hogares; no completa consumo, ingreso amplio, riesgo bancario exacto ni el ledger fiscal realizado.
