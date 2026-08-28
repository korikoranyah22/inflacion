# Credicoop — auditoría de índice primario V72

La página oficial `Memoria y Balance` de Banco Credicoop lista explícitamente dentro de 2023:

- `31-12-2023`
- `30-09-2023`

Esto eleva la existencia del filing 9M desde evidencia secundaria a **índice primario del emisor**.

El sitio carga el enlace de descarga de forma dinámica y el crawler actual no expone su URL/ID. No se infiere el ID desde documentos adyacentes porque se comprobó que la numeración no es secuencial por trimestre.

```text
CREDICOOP_30_09_2023_PUBLICATION
= PRIMARY_ISSUER_INDEX_CONFIRMED

CREDICOOP_30_09_2023_BINARY
= NOT_RECOVERED

CREDICOOP_30_09_2023_ANNEX_Q
= NOT_INSPECTED

CREDICOOP_Q4_FOUR_LEG
= N/D
```


## Corrección V72
La Comunicación BCRA A 7809 clasifica el Anexo Q como anual. Recuperar el binario 30-09-2023 sigue siendo prioritario, pero ya no para exigir un Q trimestral: hay que inspeccionar cualquier disclosure 9M de pases por contraparte que el filing contenga.
