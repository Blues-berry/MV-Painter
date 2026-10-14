# V4 evidence-reintegration build verification

Starting remote HEAD: `0aa1c9b3`, itself continuing `c3017645`. All four final PDFs rebuilt from current V4 TeX/Markdown and original-submission marked-source baseline. Main 14 pages, Supplement 71, response 5, marked 21. Manuscript and Supplement build passes found no undefined citation/reference. Main Tables 1–7 and their actual PDF pages were inspected; details in `TABLE_1_TO_7_LAYOUT_AUDIT.md`.

Tables 1, 2, 4 and 6 retain their original numeric entries; redesigned Tables 3, 5 and 7 retain their numerical estimates, interval endpoints and p values. The original GeoTex Middle−mean(Early,Late) primary remains Table 7's first row. The two separate bake LPIPS primaries remain Table 5. `quality_review/FROZEN_CONTENT_CHECK_V4.json` records this limited frozen-content check; no GPU work or inferential recomputation occurred.

The marked TeX is regenerated from authenticated original 01549 source SHA `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01` against current V4 source; the complete expanded-source diff is supplied. Layout and scientific readiness are judged separately from build success in `quality_review/INDEPENDENT_CG_ASSESSMENT_V4.md`.
