# AUDITORÍA V60

## Correcciones principales
- `A_Q_ANNUAL_ONLY_ASSUMPTION` queda rechazado para estados intermedios efectivamente publicados.
- Q4 puede reconstruirse a nivel entidad como `FY_Dec - 9M_Sep × IPC_Dec/IPC_Sep`.
- IPC: Sep=2304.9; Dic=3533.2; factor=1.532908152197492.
- Las primas por pases tienen contrapartes heterogéneas (BCRA y otras entidades financieras).
- Se revoca `7.7 pp = strict BCRA floor`.

## Ejemplos Q4 reconstruidos (miles de ARS de dic-23)
Macro broad=552336409.847; household-like=163479310.568; BCRA passes=83520202.827; other-FI passes=647816.041.
Ciudad broad=620844795.150; household-like=95200458.097; BCRA passes=0.000; other-FI passes=370794209.077.

## Gates
- Macro+Ciudad = muestra descriptiva, no sistema.
- `hipotecarios+prendarios+personales+tarjetas` = proxy por producto, no sector hogar estricto.
- interés de títulos públicos != contraparte Tesoro identificada.
- el bucket IEF `primas por pases` no puede asignarse íntegramente al BCRA sin reconciliación sistémica.
