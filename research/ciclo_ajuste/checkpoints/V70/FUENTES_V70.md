# FUENTES V70

## Banco Nación — 9M 2023

1. **AGN — Informe 210/2023 / Actuación 298/2023**
   - Página oficial: https://www.agn.gob.ar/informes/Informe-210-2023
   - Identifica estados financieros intermedios consolidados condensados y separados condensados para 01/01/2023–30/09/2023.
   - Los links `Informe` y `Anexo` detectados devolvieron HTTP 502 durante V70.

2. **Banco Nación — Balance Condensado Sept 2023**
   - https://www.bna.com.ar/Downloads/Institucional_MemoriayBalances_BALANCE%20CONDENSADO%20SEPT%202023.pdf
   - Fuente primaria del emisor, período de nueve meses al 30/09/2023.
   - La propia hoja declara que incluye casas del país, filiales del exterior, subsidiarias y entes estructurados.
   - Es resumen de una página y no contiene Anexo Q.
   - Se clasifica `CONSOLIDATED_INCLUSIVE_CONTROL_ONLY`.

3. **BNA FY 2023 individual Schedule Q**
   - Fuente primaria heredada/auditada en V69.
   - `income_BCRA = 766170919k`, `income_otherFI = 0`, `expense_BCRA = 0`, `expense_otherFI = 0`.

## Banco Provincia — septiembre 2023

4. **Disciplina de Mercado — septiembre 2023**
   - https://www.bancoprovincia.com.ar/CDN/Get/Disciplina_de_Mercado_septiembre_2023
   - Documento oficial basado en datos vigentes al 30/09/2023; remite a Estados Contables/portal institucional.
   - No es el Anexo Q separado y no cierra Q4.

5. **Bapro FY 2023**
   - Fuente oficial heredada V65–V69; Anexo Q separado FY exacto.

## Banco Credicoop

6. FY 2023 Anexo Q separado exacto heredado.
7. Evidencia secundaria de calificación encontrada en V70 refiere análisis a 30/09/2023 basado en EEFF; se usa sólo para existencia documental, nunca para números del bridge.

## Banco Ciudad

8. **EEFF consolidados 30/09/2023**
   - https://www.bancociudad.com.ar/cms/recursos/institucional/carpetarecurso/Balances%20Trimestrales/EstadosFinancieros/2023.09_-_EEFF_consolidados.pdf
   - Fuente primaria oficial, pero consolidada. Control únicamente.

## Reglas de uso

- fuente primaria > secundaria;
- consolidado no se sustituye por individual;
- FY no se sustituye por Q4;
- stock no se usa como proxy del flujo de pases;
- no se crea `BNA_Q4_AQ_BRIDGE_V70.csv` porque el 9M individual compatible sigue sin recuperarse.
