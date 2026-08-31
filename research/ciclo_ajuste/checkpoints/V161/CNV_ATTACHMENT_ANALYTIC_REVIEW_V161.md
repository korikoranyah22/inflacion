# Revisión analítica de adjuntos oficiales V161

## Resultado

V161 promueve tres entidades sin flexibilizar la regla de cuatro patas: Banco BMA, Banco Mariva y Banco de Corrientes. El panel estricto pasa de 30 a 33 entidades. El numerador de activos sube de 59812903.504 a 61248719.753 millones de pesos y la cobertura de 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549% a 63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063% (+1.4848505350367941291837714994976276347764668290362721208800679226114545821828814937994049713418454685184995437662731063 puntos porcentuales).

## Método

1. Se preservaron y verificaron por SHA-256 los estados oficiales.
2. Se inspeccionaron visualmente las páginas relevantes y se controlaron texto, unidad, período y base individual/separada.
3. Se extrajeron, desde los archivos oficiales BCRA de septiembre y diciembre, sólo las cuentas de resultado de la entidad analizada.
4. El conjunto de cuentas se aceptó únicamente cuando reconciliaba exactamente el Anexo Q de la misma entidad y el mismo ejercicio.
5. Para Mariva y Corrientes, el conjunto validado al cierre anual se trasladó sólo a septiembre de la misma entidad, año y base. No se convirtió en un diccionario universal de etiquetas.
6. Q4 se calculó como FY en moneda homogénea de diciembre menos 9M en moneda homogénea de septiembre multiplicado por el factor congelado 1.532908152197492. No se redondearon ni truncaron residuos.

## BMA

Los Anexos Q de septiembre y diciembre publican directamente las cuatro patas. Además, los conjuntos regulatorios de la entidad 00259 coinciden exactamente en ambos cortes. La cuenta 511007 integra ingreso BCRA y la 521007 integra gasto otras entidades financieras en este banco; ese hallazgo es una identidad BMA/Itaú 2023, no una semántica global del número o del rótulo.

## Mariva

El estado intermedio preservado es separado pero no incluye Anexo Q. El anual sí lo incluye: todo el ingreso y gasto por pases corresponde a otras entidades financieras, con patas BCRA en cero. Los totales anuales igualan exactamente la suma de 511027+515034 y 521022+525042. Se usa el mismo conjunto completo en septiembre sólo como puente Mariva 2023.

## Corrientes

El Anexo Q anual oficial asigna 40.870.153 miles de pesos a ingreso BCRA y cero a las otras tres patas. El archivo regulatorio anual contiene exactamente 40.870.153 en 511108 y ninguna otra cuenta de resultado por pases; el mismo conjunto se usa en septiembre sólo para Corrientes 2023.

## HSBC: control negativo

HSBC publica totales exactos de pases activos y pasivos con “el sector financiero”, pero no separa BCRA de otras entidades. El archivo BCRA reproduce los totales, no la apertura. La exposición de stock con el BCRA no identifica la contraparte de los flujos. Por eso HSBC permanece N/D_STRICT aun cuando sus totales Q4 son calculables.

## Resguardos

- La diferencia entre la huella declarada por CNV y el SHA-256 de los bytes servidos se conserva como metadato de archivo; no se interpreta como alteración.
- Activos agregados no sustituyen cuatro patas de resultados.
- Un stock de pases no asigna automáticamente un flujo de intereses.
- Seis pedidos históricos permanecen DRAFT_NOT_SENT; SAF355 sigue 0/5 y ejecución bancaria histórica 0/10.
