# Revisión analítica de adjuntos oficiales V166

## Resultado acumulado

El antecedente V161 promovió Banco BMA, Banco Mariva y Banco de Corrientes, llevando el panel de 30 a 33 entidades y la cobertura a 63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063%. V166 suma Banco Rioja sin flexibilizar la regla de cuatro patas: el panel pasa de 33 a 34 entidades, el numerador de activos de 61248719.753 a 61345602.215 millones de pesos y la cobertura a 63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825% (+0.1001910764253942328956536508152875266815433052383342475829736811049442227917417121900283549156556683401002043528534762 puntos porcentuales frente a V165).

## Método acumulado

1. Se preservaron y verificaron por SHA-256 los estados oficiales y los cortes raw.
2. Se inspeccionaron visualmente las páginas relevantes y se controlaron unidad, período y base individual/separada.
3. Se extrajeron de los archivos BCRA sólo las cuentas de resultado de cada entidad.
4. El conjunto se aceptó únicamente cuando reconciliaba el Anexo Q de la misma entidad y ejercicio.
5. Los puentes se transfirieron sólo dentro de la misma entidad, año y base; nunca como diccionario universal.
6. Q4 se calculó como FY homogéneo de diciembre menos 9M homogéneo de septiembre por 1.532908152197492, sin redondear residuos.

## Banco Rioja

El Anexo Q anual asigna pases exclusivamente al BCRA: ingreso 14.409.056k y gasto 7.844k; las patas otras entidades son cero. El censo completo deja sólo `511108` y `521108` en septiembre y diciembre. El IEF BCRA de junio de 2024 vuelve a publicar diciembre de 2023 en la capa corregida y ubica +158,8m enteramente dentro de ingresos por intereses, mientras las demás aperturas financieras permanecen invariantes. Esta cadena autentica el componente anual y permite el puente Rioja-2023-misma base.

Q4 resulta en ingreso BCRA 5652853.165516943874708k, gasto BCRA 0.108985205433436k, ingreso y gasto otras entidades 0/0, y neto BCRA 5652853.056531738441272k. No se infiere un diario contable no publicado.

## Control negativo HSBC

HSBC continúa N/D_STRICT: publica totales con el sector financiero, pero no separa BCRA de otras entidades. Un stock no identifica la contraparte de los flujos.

## Resguardos

- La huella declarada por CNV y la huella de los bytes servidos se conservan por separado; una diferencia no se interpreta automáticamente como alteración.
- Activos agregados no sustituyen cuatro patas de resultados.
- SAF355 permanece 0/5, ejecución bancaria histórica 0/10 y seis pedidos siguen DRAFT_NOT_SENT.
