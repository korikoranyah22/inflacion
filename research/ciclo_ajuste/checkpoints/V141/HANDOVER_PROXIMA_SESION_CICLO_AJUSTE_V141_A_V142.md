# Handover V141 → V142

## Estado

- QA V141: ejecutar y exigir PASS.
- SICHE conserva CUT-SIDIF Central 2007-2014: Entidades Básicas, Saldos por Apertura, Extractos y Logs de Impacto.
- Cobertura temporal exacta: incluye 2008; acceso publicado para Órganos Rectores.
- Cadena target: formulario 7.2.8/83106000 → log → extracto → Libro Banco → conciliación → AMIDDF.
- Campos posteriores útiles: fecha, secuencia, códigos, débito/crédito, referencia bancaria, comprobantes y estado.
- Cuenta 3855/19 no se presume para 2008; debe surgir de Entidades Básicas.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V142

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Buscar manual o pantalla específica del módulo CUT histórico de SICHE.
3. Buscar catálogo/diccionario de códigos de movimiento CUT-SIDIF Central 2008.
4. Intentar localizar identidad histórica de cuenta CUT y cuentas de operación sin proyectar 3855/19.
5. Explorar si publicaciones TGN/CGN preservan informes, logs o conciliaciones 2008.
6. Mantener formulario, log, extracto, Libro Banco y conciliación como capas separadas.
