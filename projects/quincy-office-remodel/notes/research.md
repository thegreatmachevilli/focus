# Research notes

## Quincy, Illinois permit fee
- The City of Quincy commercial, industrial, and multi-family permit schedule lists a **minimum permit fee of $75**.
- For **commercial remodeling and repairs**, the fee is **construction value x 0.005**.
- Working formula for this job: `permit_fee = max(75, contract_value * 0.005)`.

## Current price log
Retrieved on **2026-03-19 UTC**.

- 48 in. drywall T-square: **$21.99** from True Value for the Empire 48 in. blue drywall square.
- DeWalt DW088CG green cross-line laser: **$189.00** from Home Depot; listing specifically says it is ideal for drop ceiling, tile, or remodeling jobs.
- Hilti 1-5/8 in. collated drywall screw box: **$174.00** from Home Depot for the 5000-pack.
- Hilti 1-1/4 in. collated drywall screw box: **$266.00** from Home Depot for the 8000-pack.
- Big River Disposal allowance: **$400.00** per user direction.
- Menards delivery: **zip-code dependent**; Menards states the delivery cost appears in checkout after entering the delivery zip code.

## Source links
- City of Quincy building permit fee schedule PDF: https://www.quincyil.gov/files/assets/city/v/1/inspections/documents/826building-permit-fees-2018.pdf
- Empire 48 in. blue drywall square: https://www.truevalue.com/product/blue-drywall-square-48-in/
- DeWalt DW088CG laser: https://www.homedepot.com/p/304849047
- Hilti 1-5/8 in. collated screws: https://www.homedepot.com/b/Hardware-Fasteners-Collated-Fasteners-Collated-Screws/5000/N-5yc1vZc2c5Z1z13yt2
- Hilti 1-1/4 in. collated screws: https://www.homedepot.com/p/311697086
- Menards orders & shipping: https://www.menards.com/main/help-center/orders-shipping/c-19280.htm

## Known blockers
- The source bid PDF, the gold-line template, and the original logo file are still not present in this repository.
- Menards product pages are bot-protected in this environment, so exact Menards item pricing could not be fetched directly here. Accessible market prices were used for the priced add-on lines instead.
- Because the current bid package is still missing, the actual PDF page restyle, logo cleanup, and page-by-page floor-plan removal cannot be executed yet.

## User-directed estimate lines to preserve
- Include delivery as a separate line item.
- Include **$400** for Big River Disposal dumpster/trash removal.
- Leave out floor plans from the revised package.
