# BNA — auditoría de attachments AGN V71

## Fuente oficial

La página `Informe 210/2023`, Actuación `298/2023`, confirma que la AGN revisó estados financieros intermedios **consolidados condensados y separados condensados** del BNA para 01/01/2023–30/09/2023.

Al resolver los enlaces oficiales aparecen dos nombres binarios exactos:

- `2023-210-Informe SC 1.pdf`
- `2023-210-Informe CC 2.pdf`

Ambos endpoints devuelven HTTP 502 en la ruta actual.

## Refinamiento metodológico

V69–V70 llamaban a esto de forma abreviada `AGN_SEPARATED_PACKAGE_IDENTIFIED`. V71 lo vuelve más estricto. Los filenames contienen `Informe`, y la nomenclatura histórica de AGN usa archivos equivalentes `Informe Separ.condens` para **informes de revisión**. Por lo tanto no está probado que el binario `SC 1` contenga el juego completo de estados financieros ni sus Anexos Q.

```text
BNA_9M_SEPARATED_STATEMENTS_AUDITED
= SUPPORTED

BNA_9M_AGN_SC_REVIEW_ATTACHMENT
= EXACT_FILENAME_IDENTIFIED
= HTTP_502

BNA_9M_FULL_SEPARATED_STATEMENT_PAYLOAD
= NOT_ESTABLISHED

BNA_9M_ANNEX_Q
= NOT_RECOVERED
```

No construir Q4 desde el resumen condensado del emisor ni desde Disciplina de Mercado.
