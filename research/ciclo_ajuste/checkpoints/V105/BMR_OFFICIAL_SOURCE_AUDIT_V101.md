# Banco Municipal de Rosario — official source audit V101

## Sources
- 9M official PDF: https://www.bmros.com.ar/uploads/documents/1702642924151.pdf
- FY official PDF: https://www.bmros.com.ar/uploads/documents/1710333709333.pdf

Both documents contain a separated/individual section and regulatory annexes.

## 9M separated
Anexo Q explicitly reports:
- repo income: **5,210,550k**;
- BCRA: **5,210,550k**;
- no Other-FI repo-income leg;
- interest expenses are exhaustively presented without a repo-expense category.

Raw BCRA `511108=5,210,550k` matches exactly. The full selected raw interest-income set sums to **43,703,872k**, exactly the separated Anexo-Q total; the selected raw interest-expense set sums to **20,420,895k**, also exact.

## FY separated and header anomaly
The annual file's separated Anexo-Q first page is incorrectly headed "AL PERÍODO DE NUEVE MESES FINALIZADO EL 30 DE SEPTIEMBRE DE 2023", even though its values are FY values. This is treated as a document-label error, not silently corrected.

Independent within-file evidence establishes the period:
- separated Note 6 is headed for the exercise ended **31/12/2023** and states repo gain **11,420,465k**;
- the same annual separated Anexo-Q shows repo income/BCRA **11,420,465k**;
- Dec raw `511108=11,420,465k` exactly;
- full raw interest income **91,880,037k** and expense **44,248,000k** reconcile exactly to that annual separated Anexo-Q.

Therefore BCRA repo income is identified and the Other-FI/BCRA expense legs are zero by exhaustive same-entity reconciliation, not by visual omission alone.

## Preservation gate
Both issuer PDFs remain web-readable but their original bytes could not be persisted by this runtime. No strict promotion until both are physically stored + SHA-256 verified.
