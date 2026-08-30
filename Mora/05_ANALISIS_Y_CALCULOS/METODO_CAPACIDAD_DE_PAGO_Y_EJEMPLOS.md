# Método de capacidad de pago y ejemplos

## Por qué no alcanza con “cuota / ingreso”

Dos hogares con el mismo ingreso no tienen la misma capacidad si difieren en alquiler, integrantes, discapacidad, medicación o tareas de cuidado. Por eso el articulado aplica dos límites simultáneos:

`CMP = mínimo (20 % del ingreso neto; 70 % del excedente sobre el mínimo vital)`

En vulnerabilidad:

`CMP_v = mínimo (15 % del ingreso neto; 60 % del excedente sobre el mínimo vital)`

El primer límite impide una afectación nominal excesiva. El segundo protege los gastos esenciales y deja una reserva para variaciones imprevistas.

## Variables

1. `INCH`: ingreso regular neto del hogar consentido por sus integrantes.
2. `CBT_H`: Canasta Básica Total para su composición por adulto equivalente.
3. `AV`: suplemento indispensable de vivienda y servicios, sin duplicar lo ya implícito en la CBT.
4. `AS`: salud, discapacidad y medicación no cubiertas.
5. `AC`: cuidado, educación, transporte, conectividad y trabajo indispensables no captados adecuadamente.
6. `MVH = CBT_H + AV + AS + AC`.
7. `ED = máximo(0; INCH − MVH)`.

Las prestaciones específicamente destinadas a niñez, discapacidad, salud, vivienda o cuidado no se cuentan como ingreso disponible para acreedores.

## Ejemplo A — Hogar sin excedente

- INCH: $1.200.000
- MVH: $1.250.000
- ED: $0
- 20 % del ingreso: $240.000
- 70 % del excedente: $0
- **CMP: $0**

No corresponde imponer una cuota. Debe evaluarse espera, procedimiento sin activos y eventual exoneración. Fijar $240.000 sólo por aplicar un porcentaje del ingreso quitaría recursos ya insuficientes para vivir.

## Ejemplo B — Capacidad positiva limitada por el excedente

- INCH: $2.000.000
- MVH: $1.600.000
- ED: $400.000
- 20 % del ingreso: $400.000
- 70 % del excedente: $280.000
- **CMP: $280.000**

El hogar conserva el MVH y $120.000 de reserva. Si el pasivo no se amortiza en sesenta meses, se necesita una quita acordada o decisión judicial; no una cuota globo.

## Ejemplo C — Límite nominal

- INCH: $3.000.000
- MVH: $1.500.000
- ED: $1.500.000
- 20 % del ingreso: $600.000
- 70 % del excedente: $1.050.000
- **CMP: $600.000**

Aunque el excedente sea amplio, la ley evita afectar más de una quinta parte del ingreso en el procedimiento de alivio.

## Ejemplo D — Persona vulnerable

- INCH: $1.800.000
- MVH reforzado: $1.500.000
- ED: $300.000
- 15 % del ingreso: $270.000
- 60 % del excedente: $180.000
- **CMP vulnerable: $180.000**

## Originación de crédito nuevo

Para una nueva deuda de consumo:

`servicio máximo consumo = mínimo (25 % × INCH; 60 % × ED)`

Para todas las deudas, incluidas las garantizadas:

`servicio máximo total = mínimo (35 % × INCH; ED)`

El cálculo se hace luego de agregar la cuota nueva y con prueba de tensión si la tasa o el ingreso son variables.

## Actualización y revisión

- La CBT se actualiza con la publicación oficial.
- Los suplementos deben usar parámetros regionales, públicos y auditables.
- Un tope administrativo es una presunción revisable: un gasto esencial probado no puede rechazarse sólo por superar el promedio.
- Ningún gasto puede duplicarse.
- La fórmula debe probarse con microdatos anonimizados antes de fijar topes definitivos.

## Sensibilidades a simular antes de la presentación

1. CMP general con 15 %, 20 % y 25 % del ingreso.
2. Reserva sobre excedente de 20 %, 30 % y 40 %.
3. Plazos de 36, 48 y 60 meses.
4. Tasa de plan bajo TRCC, tasa original y TAMAR convertida + 25 puntos.
5. Hogares de uno a seis integrantes, con y sin alquiler, cuidados y discapacidad.
6. Tasa de recuperación del acreedor frente a cobranza, ejecución y liquidación.

El objetivo no es maximizar una cuota teórica, sino maximizar el valor esperado de cumplimiento sin empujar al hogar nuevamente a la mora.
