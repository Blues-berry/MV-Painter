# Control ownership in the current illustrative Figure 1

| Component | Identity | Actual semantics |
|---|---|---|
| TCAS requested profile | Studied intervention | C3 requests1.25/2.50/1.25 at steps0–16/17–32/33–49 |
| Native wrapper cap | Existing implementation | min(request,cap); deep3,middle3.5,shallow.8 |
| GeoTex residual | Existing pretrained adapter | Correction A(h,G) depends on hidden and geometry features |
| Scale and feature addition | Existing wrapper operations | s_app × A(h,G), then addition to frozen ResNet output |
| Actual FreshC groups | Run-bound up_only configuration | up0/up1/up2, three wrappers per group; optional middle-block injection inactive |
| UV projection/baking | Downstream workflow | No new model module or claim all FreshC objects were baked |
| Building panels | Author-supplied illustrative imagery | No experiment UID/protocol identity or effectiveness evidence is assigned |

Run-bound config SHA295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b; archived trace is in baseline_e943/source_files/C3_residual_trace.json. Original frozen code operations are compute_correction, min, multiplication, feature addition. The complete final review remains separate from author approval.
