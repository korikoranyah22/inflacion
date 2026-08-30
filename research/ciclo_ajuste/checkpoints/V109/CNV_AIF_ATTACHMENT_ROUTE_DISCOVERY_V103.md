# CNV AIF attachment route discovery — V103

## Result
V103 narrows the CNV binary-recovery problem without claiming a source recovery. The exact six bank presentations remain identified and current PublicView URLs resolve to the expected presentation identities, but the original attachment bytes were **not** recovered in this execution environment.

A recent public technical dataset description for CNV AIF crawling documents an attachment JSON carrying at least:
- attachment `guid`;
- filename;
- size;
- hash;
- a derived `pdf_blob_guid`, explicitly described as allowing programmatic re-download of the PDF.

Technical route evidence (secondary, not a substitute for CNV primary evidence):
- https://almanac.ar/datasets/cnv.ons.colocaciones

This changes the recovery hypothesis from “unknown hidden attachment mechanism” to “known attachment-JSON/blob mechanism, concrete endpoint and target blob GUIDs still unresolved”. It does **not** satisfy the repository physical-preservation rule.

## Exact targets revalidated
| Entity | Period | CNV presentation | PublicView GUID |
|---|---:|---:|---|
| Banco Mariva S.A. | 9M | 3122483 | c23edd68-9bf4-4b3d-a1d8-9cde4770d45c |
| Banco Mariva S.A. | FY | 3165651 | d28fcf1a-28dc-465b-8478-aad95e0d4539 |
| HSBC Bank Argentina S.A. | 9M | 3121099 | d483d33a-5c86-4fbb-ab9c-6528bf43f572 |
| HSBC Bank Argentina S.A. | FY | 3163537 | 39f37eb9-5637-4cb3-ab6b-715da7830bd1 |
| Banco BMA / ex Banco Itaú Argentina S.A. | 9M | 3119515 | 9d3ded55-6d87-4ca2-9feb-920d961f3acd |
| Banco BMA / ex Banco Itaú Argentina S.A. | FY ordinary | 3171909 | 36d0f59a-8e3f-42cd-bf18-db44e023f18d |

For BMA, presentation **3177414 remains excluded**: it is the special merger balance and must not substitute ordinary FY #3171909.

## Gate
No attachment JSON payload, blob GUID, original PDF bytes, or SHA-256 was recovered for these six targets in V103. Therefore:
- no strict promotion;
- no inferred six-digit account mapping;
- no synthetic/re-rendered PDF is admitted as an original;
- next step is exact endpoint/blob discovery or manual preservation of the original attachments.
