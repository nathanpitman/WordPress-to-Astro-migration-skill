# Stage 4: Verify and review

**Steps:** the full verifier run, the SEO carry-over check (Phase 7), the asset check (Phase 9), the local review server (Phase 12, section 2) and the visual comparison (`reference/visual-comparison.md`), then the finishing touches to Phase 11 that need the build.

**Order**
1. Run the verifier over every page (in batches if disk is tight), then the SEO check and the asset check against the same build. Fix genuine regressions in the build and re-run until the numbers are stable.
2. Start the local review server, probe it as set out in Phase 12 section 2, and run the visual comparison if a browser tool is available. Classify every difference (hosting-layer artefact, genuine regression, defect of the original) and fix only genuine regressions.
3. Finish Phase 11: the known cutover breakages list, the built-site asset result, and the themed 404 if it was not captured earlier.
4. Stop the server.

**Gate: end of stage 4.** Checkpoint: verification numbers (HTML, SEO, assets), the local review probe results, the visual comparison table with classified differences, defects of the original recorded, and any open decisions. Next: Stage 5.
