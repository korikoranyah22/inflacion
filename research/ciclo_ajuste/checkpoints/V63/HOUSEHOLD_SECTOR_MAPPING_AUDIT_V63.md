# HOUSEHOLD SECTOR MAPPING AUDIT V63

## Finding
The Annex Q product rows (`Hipotecarios`, `Prendarios`, `Personales`, `Tarjetas de Crédito`) are useful candidates for direct household-bank contractual flows, but they are not by themselves a strict institutional-sector household classification.

## Why
1. Annex Q is an accounting/product disclosure, not a population-sector microdata table.
2. Product labels can include edge cases outside ordinary households.
3. `interest accrued on a product family` is not identical to household total financial cost, CFTEA, commissions, VAT, insurance, default cost, or bank net profit.
4. The project gate therefore remains: `PRODUCT_PROXY != STRICT_HOUSEHOLD_SECTOR`.

## Permitted use
- entity-level direct-contract candidate flow;
- descriptive bundle;
- lower-resolution audit target for later sector mapping.

## Not permitted
- system household point estimate without homogeneous high coverage;
- household loss = bank revenue;
- direct household-to-bank transfer from product sums alone.
