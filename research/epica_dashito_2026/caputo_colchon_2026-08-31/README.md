# Preguntas sobre los “dólares del colchón”

Fecha de corte: **31/08/2026**.

La hipótesis inicial de Miyu queda registrada como parte del recorrido en el **Storytelling** del dashboard. Este módulo no la trata como un examen binario: la traduce a cuatro preguntas abiertas que conviene analizar por separado:

1. quién dispone de ahorro o patrimonio invertible;
2. qué incentivo privado existe para depositarlo en un banco argentino;
3. qué alternativa ofrece una cuenta comitente y un activo internacional de bajo riesgo crediticio;
4. qué objetivos macroeconómicos persigue el Gobierno al intentar movilizar esos dólares.

La frase propuesta por la usuaria se conserva como **paráfrasis de trabajo**. No se encontró esa redacción literal en las transcripciones oficiales revisadas. El análisis usa, en cambio, las formulaciones oficiales del 22/05/2025, 22/07/2026 y 13/08/2026.

Los originales descargados se guardan en `sources/`. La serie completa de tasas del BCRA se conserva comprimida para mantenerse por debajo del límite de tamaño por archivo de GitHub; las respuestas crudas de la API monetaria también quedan preservadas. `source_registry.csv` registra cada URL y `source_manifest.csv` agrega tamaño y SHA-256. Los cuadros del tab se encuentran en `derived/`.

La comparación de canales incluye un punto de equilibrio de costos: la brecha bruta observada de 2,09 puntos porcentuales se usa como umbral, no como estimación de comisiones o impuestos individuales. El mapa de transmisión bancaria separa depósito, capacidad de prestar, decisión del banco, demanda empresarial, liquidación cambiaria y resultado posterior.

La profundización del 31/08 agrega nueve piezas reproducibles:

- una contabilidad de intermediación que distingue el ratio observado de 61%, la referencia prudente histórica de 65% y el máximo regulatorio de 75%;
- una lectura de los destinos estimados por el BCRA para las compras de personas humanas en julio: banco local, activos externos y consumos con tarjeta;
- una matriz del marco prudencial para nuevos deudores, con cupo de 15%, exigencia de capital de 125%, factor de exposición 1,25 y prueba de repago bajo escenarios cambiarios.
- una auditoría de numeradores y denominadores que separa la retención onshore de 75%/≈80%, el ratio bancario de 61%, las referencias de 65%/75%, la capacidad ociosa de 17% y la liquidez agregada de 48,6%;
- una medición de concentración por tramos de cuentas y saldos en moneda extranjera, con la advertencia de que las cuentas no identifican personas únicas ni efectivo fuera del sistema;
- una reconstrucción trimestral 2023–2026 que separa proliferación de cuentas de bajo saldo y concentración del dinero;
- una apertura del crédito privado en dólares por línea, acompañada por la historia reciente de tasas activas y pasivas y escenarios mecánicos de margen bruto.
- una radiografía del crédito por actividad, tipo de prestatario, tramo y plazo, acompañada por la Encuesta de Condiciones Crediticias para separar fondeo, demanda y estándares de aprobación.
- un primer corte posterior a la Comunicación A 8467 que compara depósitos y préstamos entre el 18 y el 27 de agosto, explicita qué universo jurídico quedó habilitado y fija el calendario de próximas pruebas sin atribuir causalidad a los agregados.

Con los stocks oficiales redondeados, el margen hasta la referencia prudente es aproximadamente USD 1.595 millones. La cifra oficial de USD 5.800 millones corresponde al máximo regulatorio teórico. Se muestran ambas porque responden preguntas distintas.

Límites importantes:

- la EPH mide ingresos corrientes, no patrimonio ni dólares físicos;
- “otros sectores” de la posición de inversión internacional agrupa hogares, empresas e ISFLSH;
- depositar dólares en un banco no los convierte automáticamente en reservas del BCRA ni en inversión productiva;
- comparar rendimientos requiere considerar comisiones, impuestos, custodia, liquidez y riesgo de precio;
- el informe bancario de junio y el ratio comunicado en agosto tienen fechas y definiciones distintas y no se equiparan mecánicamente;
- el 75% poselectoral de ahorro onshore y el 75% de capacidad regulatoria son indicadores completamente distintos;
- el propio IPOM reconoce al mercado de capitales como alternativa competitiva en dólares, aunque lo considera un sustituto incompleto del banco por escala, exigencias de información y capilaridad;
- la forma contractual del crédito no identifica por sí sola la actividad del deudor ni el uso final de los fondos;
- la actividad identifica la actividad principal del deudor, no el destino de cada préstamo, y la última apertura disponible termina el 30/06/2026, antes del nuevo cupo anunciado en agosto;
- los montos operados mensuales son flujos brutos, no nuevos prestatarios únicos ni creación neta de crédito;
- la brecha entre tasas activas y pasivas no es una medida de rentabilidad bancaria neta;
- las motivaciones personales del ministro quedan fuera del alcance: se estudian declaraciones, incentivos, restricciones y mecanismos observables.
