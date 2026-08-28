# Source references — through V95

## Frozen baseline
- V88 handover/checkpoint: strict coverage 53.569372790275027805600599861244883545337437746901%, numerator 51,800,348.982m ARS, 13 exact entities.

## Nuevo Banco de Santa Fe — primary issuer
- 30/09/2023 separated: https://assets.ctfassets.net/h7wmg0jhythh/3KykEMuhRA2DZjWCd12wv/10e5d5dd2278b7501d23c2fe0815962b/092023_-_NBSF_-_EEFF_Separados.pdf
  - interim opening: BCRA pass income 7,241,340k; other-FI pass income 0; BCRA pass expense 0; other-FI pass expense 281,272k.
- 31/12/2023 separated: https://assets.ctfassets.net/h7wmg0jhythh/n0pbb6IBTuXKan3xDHFJI/0f0fbd42c71be085d2712976d1890ef9/122023_-_NBSF_-_EEFF_Separados.pdf
  - FY opening: BCRA pass income 21,133,658k; other-FI pass income 9,965k; BCRA pass expense 0; other-FI pass expense 431,159k.

## Nuevo Banco de Entre Ríos — primary issuer
- 30/09/2023: https://assets.ctfassets.net/h7wmg0jhythh/4298svWaPcM3FgQ8pspEtP/e19201d5d304fe5ff78ac1bbefcad978/NBERSA_09.2023_-_EEFF_.pdf
  - 9M: BCRA pass income 9,061,982k; other-FI income 4,894k; BCRA expense 0; other-FI expense 1,679k.
- 31/12/2023: https://assets.ctfassets.net/h7wmg0jhythh/2fLFeDK6jUhhYgrHlc1WNH/59c7096b296c83d4d6420a3bc3f28243/NBERSA_12.2023_-_EEFF_sin_pdu.pdf
  - FY: BCRA pass income 32,055,217k; other-FI income 7,502k; BCRA expense 0; other-FI expense 2,573k.

## Banco de San Juan — primary issuer / official comparative
- 30/09/2023 separated: https://assets.ctfassets.net/e7eu92ue673r/y9IVnh4fy1BgWES0TUbmZ/468b8e783fed7b6e18bd70a9ee7bebf9/30.09.2023__SEPARADOS_.pdf
  - 9M: BCRA pass income 4,494,873k; other-FI income 1,820k; BCRA expense 0; other-FI expense 62,383k.
- Official 2024/2023 comparative Annex Q: https://contenido.sanjuan.gob.ar/media/k2/attachments/%2803%29_%28MARZO%29_14-03-2025_ANEXO_BANCO_SAN_JUAN.pdf
  - FY-2023: BCRA pass income 49,465,317k; other-FI income 14,443k; BCRA expense 0; other-FI expense 208,239k.

## Banco de Santa Cruz — primary issuer
- 30/09/2023: https://assets.ctfassets.net/h7wmg0jhythh/67xmHobIaNPVJS8GHGQzkg/ef170bd735ee3a4dbe86a1f35d407799/092023_-_BSC_-_Estados_Financieros_NIIF.pdf
  - pass income 1,899,286k, all BCRA; no pass-expense line.
- 31/12/2023: https://assets.ctfassets.net/h7wmg0jhythh/4g79KmIvc3oFO0cOoxTWKs/431c9d8d065184e2c23525856a1d55ca/122023_-_BSC_-_Estados_Financieros.pdf
  - pass income 7,526,661k, all BCRA; no pass-expense line.

## BICE manual recovery
- AGN page: https://www.agn.gob.ar/informes/Informe-209-2023
- separated-condensed candidate: https://www.agn.gob.ar/sites/default/files/informes/2023-209-Informe%20Anexo%201%20SC.pdf

## HSBC manual recovery remains active
- Sep individual CNV: https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572


# V90 additions — BICE

## User-rescued AGN artifacts
- AGN page: https://www.agn.gob.ar/informes/Informe-209-2023
- SC review report: https://www.agn.gob.ar/sites/default/files/informes/2023-209-Informe%20Anexo%201%20SC.pdf
  - manual binary SHA-256 `f2851ac0049c1596bb8ae20529667ee61d79f83c81b1c2bfd831cb2768ba7ed1`; 2-page separated-condensed auditor review report only, no Annex Q tables.
- CC review report: https://www.agn.gob.ar/sites/default/files/informes/2023-209-Informe%20Anexo%20CC.pdf
  - manual binary SHA-256 `8f998f5bc342e61fc90f4b06388a0254508d9a1a2f4e1c358a7a4484056696b9`; consolidated review report, control only.
- Resolution: https://www.agn.gob.ar/sites/default/files/informes/2023-209-Resolucion.pdf
  - manual binary SHA-256 `be6b49a3f3708bd4c6e0e2a27465c86ce8f57d033f0cc7b84894ff46053489e0`.

## BICE issuer / CNV
- BICE Memoria y Balance 2023: https://www.bice.com.ar/wp-content/uploads/2025/03/Memoria-y-Balance-2023.pdf
  - FY separated Annex Q: pass income BCRA 76,247,460k; other-FI 104,997k; pass expense total 44,197k.
  - separated Note 5 incorporates the repo-operation detail from consolidated Note 5; consolidated Annex Q explicitly shows the 44,197k pass expense under Other Financial Institutions.
- CNV BICE registry: https://www.cnv.gov.ar/SitioWeb/RegistrosPublicos/DetallesRegistrosPublicos/30469?tipoEntidadId=2
  - individual 30/09/2023 presentation #3120979: https://aif2.cnv.gov.ar/Presentations/publicview/8A7369DC-5515-402B-A67F-D9CDBA8DB6CA

## BCRA raw open-data controls
- Sep archive: `research/ciclo_ajuste/inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z` SHA-256 `31a0a315444496d4336695b6bd48deb562456df10e47fbc46de3703a77528bdb`.
  - `Entfin/Tec_Cont/baldet/00300.txt`: 511027=68,496k; 511108=26,984,941k; no pass-expense result account.
- Dec archive: `research/ciclo_ajuste/inputs/bcra/2023-12/informacion_entidades_financieras_open_data/202312d.7z` SHA-256 `60ef86addba5e6646a2bfd42853ca077ea7970e9fa6effe54f1179049868f0d4`.
  - `Entfin/Tec_Cont/baldet/00300.txt`: 511027=104,997k; 511108=76,247,460k; 521007=44,197k.


# V91 additions — Banco BMA and Banco Industrial

## Banco BMA / ex-Itaú
- CNV company registry: https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/30580189411?fdesde=13%2F06%2F18
  - individual NIIF 30/09/2023 filing #3119515.
- CNV publicview: https://aif2.cnv.gov.ar/presentations/publicview/9d3ded55-6d87-4ca2-9feb-920d961f3acd
  - attachment body not recovered in V91; therefore BMA remains non-promoted.
- BCRA raw entity `00259` Sep/Dec extracted from preserved official archives; retained as non-promotional evidence until issuer crosswalk is recovered.

## Banco Industrial S.A.
- Public separated FY 2023 issuer statement mirror: https://www.garval.sba.com.ar/images/LEGALIZADOS-BIND---2023---12---EEFF-Separados.pdf
  - Annex Q FY-2023: BCRA pass income 292,074,698k; other-FI pass income 110,798k; BCRA pass expense 0; other-FI pass expense 2,892k.
- BIND/Garval institutional page identifies BIND Banco Industrial and points to its financial-information section: https://www.garval.sba.com.ar/informacion-institucional/politica-de-transparencia/estructura-organizacional
- Sep BCRA raw archive already preserved in repo: `research/ciclo_ajuste/inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z`
  - entity `00322`: 511108=91,303,079k; 511027=63,741k; 521022=605k.
- Dec BCRA raw archive already preserved in repo: `research/ciclo_ajuste/inputs/bcra/2023-12/informacion_entidades_financieras_open_data/202312d.7z`
  - entity `00322`: 511108=292,074,698k; 511027=110,798k; 521022=2,892k.


# V92 additions — Nuevo Banco del Chaco

- Official Provincia del Chaco bulletin, edition 11.076 (25 Mar 2024): https://chaco.gov.ar/uploads/boletines/25-03-24-11076-660183ddcbb40676491772.pdf
  - publishes Nuevo Banco del Chaco S.A. separated FY-2023 statements and Annex Q; pass income 27,742,167k, split BCRA 27,741,649k / other-FI 518k; no pass-expense line in the separated Annex Q.
- Nuevo Banco del Chaco official 2023 reports category: https://www.nbch.com.ar/documentos/categoria/informes-2023
  - confirms the bank's FY-2023 report publication set.
- Sep BCRA raw archive preserved in repo: `research/ciclo_ajuste/inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z`
  - entity `00311`: 511108=10,833,268k; 511027=338k; no nonzero pass-expense result account.
- Dec BCRA raw archive preserved in repo: `research/ciclo_ajuste/inputs/bcra/2023-12/informacion_entidades_financieras_open_data/202312d.7z`
  - entity `00311`: 511108=27,741,649k; 511027=518k; no nonzero pass-expense result account.


# V93 additions — Banco de La Pampa S.E.M.

## Official issuer FY-2023
- Memoria y Balance General 2023: https://www.bancodelapampa.com.ar/files/files/Dise%C3%B1o%20Memoria%20y%20Balance%20General%202023%20web.pdf
  - Annex Q p.95: BCRA pass income 54,227,326k; other-FI pass income 0; BCRA pass expense 0; other-FI pass expense 5,110k.
  - Note 3 independently reports FY-2023 positive active-repo results of 54,227,326k.

## CNV interim basis control
- Banco de La Pampa public registry: https://www.cnv.gov.ar/SitioWeb/RegistrosPublicos/DetallesRegistrosPublicos/30622?tipoEntidadId=2
  - 30/09/2023 filing #3121031 is listed as TIPO BALANCE: INDIVIDUAL.
- Publicview #3121031: https://aif2.cnv.gov.ar/Presentations/publicview/15298564-F56D-495D-A7C6-0DEDC1A77882

## Preserved BCRA raw
- Sep archive: research/ciclo_ajuste/inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z
- Dec archive: research/ciclo_ajuste/inputs/bcra/2023-12/informacion_entidades_financieras_open_data/202312d.7z
- entity 00093 rows audited in BANCO_LA_PAMPA_BCRA_RAW_ACCOUNT_AUDIT_V93.csv.


# V94 additions — Banco Provincia del Neuquén / BSE re-audit

## Banco Provincia del Neuquén — official issuer
- Official Memorias y Balances index: https://www.bpn.com.ar/Institucional/MemoriayBalances
  - links Balance 2023 General directly.
- Official Balance 2023 General: https://apiapp.bpn.com.ar/Resources/Files/3c8ae1e827054171978cb213a56891df.pdf
  - Annex Q p.83: BCRA pass income 129,240,317k; other-FI pass income 0; no pass-expense line.
- Official 2023 disclosure / Pillar III: https://apiapp.bpn.com.ar/Resources/Files/06c53b4c8d1a4285ae8685e7d02644a2.pdf
  - states `El BPN S.A. no forma parte de grupos económicos.`
- Official Balance 2024 General comparator: https://apiapp.bpn.com.ar/Resources/Files/82d95330e8d6472b90d506e198bd6549.pdf
  - corroborates 2023 BCRA-only pass-income taxonomy, but 2023 is reexpressed to 2024 homogeneous currency; control only.
- Preserved BCRA Sep/Dec archives: entity `00097`; audited in `BPN_BCRA_RAW_ACCOUNT_AUDIT_V94.csv`.

## Banco de Santiago del Estero — official BCRA control
- BCRA Información de Entidades Financieras Dec-2023: https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202312e.pdf
  - entity 00321 is present, but the publication does not provide the strict Annex-Q counterparty result split.
- Preserved BCRA Sep/Dec archives: entity `00321`; audited in `BSE_BCRA_RAW_ACCOUNT_AUDIT_V94.csv`.
- No compatible FY/9M issuer counterparty opening recovered in V94; no promotion.


# V95 additions — Banco de Formosa / Banco de Corrientes

## Banco de Formosa — primary Argentine issuer
- FY2023 official package (separated basis confirmed by auditor report): https://www.bancoformosa.com.ar/Multimedios/pdfs/117598.pdf
  - official annual pass-operation totals: positive 13,951,639k; negative 126,499k.
- 30/09/2023 official package: https://www.bancoformosa.com.ar/Multimedios/pdfs/117571.pdf
  - separated Annex Q accumulated 9M: BCRA income 3,377,992k; Other-FI income 1,420k; Other-FI expense 78,619k; BCRA expense zero.
- Official 2023 integrated report: https://www.bancoformosa.com.ar/Multimedios/pdfs/118254.pdf
  - Pases 13,949,461k; used as same-issuer FY BCRA-income component control.
- V95 uses exact entity-specific residual reconciliation for the remaining FY legs; no universal six-digit mapping.

## Banco de Corrientes — official Argentine issuer HOLD
- Official Memoria y Balance 2023 page: https://www.bancodecorrientes.com.ar/tasas-y-comisiones/category/memorias-y-balances/memoria-y-balance-2023
  - page exposes `Memoria y Estados Financieros Banco de Corrientes S.A. 31-12-2023` (3.27 MB).
  - attachment body was not recovered/parsed in V95; raw-only mapping remains prohibited.
