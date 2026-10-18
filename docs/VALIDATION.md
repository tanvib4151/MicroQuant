# Validation record

Executed in the cloud workspace on 2026-10-18 with Python 3.12.14, Node 24.19.0, Next.js 15.5.28, NumPy 2.4.3 and system Chromium through Playwright. This is software verification on synthetic images, not biological validation or demonstrated Fiji equivalence. macOS commands are documented, but macOS itself was not available for execution.

## Executed checks

| Check | Actual outcome |
| --- | --- |
| `bash scripts/setup.sh` | Passed; recreated the local `.venv` from the full Python lock and installed frontend using `npm ci` |
| `cd api && ../.venv/bin/python -m pytest -q` | **45 passed**, 0 failed, 0 skipped; one upstream Starlette/httpx deprecation warning |
| `cd web && npm run typecheck` | Passed, strict TypeScript |
| `cd web && npm run lint` | Passed, no remaining warnings |
| `cd web && npm run build` | Passed; production Next.js pages and API route built |
| `cd web && PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium TEST_PYTHON=../.venv/bin/python npm run test:e2e` | **4 passed**, 0 failed, 0 skipped, 12.7 seconds against the production server |
| `.venv/bin/python -m pip check` | Passed; no broken requirements |
| `cd web && npm audit --omit=dev --json` | 0 reported production vulnerabilities at check time |
| Backend restart and `GET /health` | Passed, `{"status":"ok"}` |
| Next.js production start and real multipart requests to `/api/analyze` | Passed for grayscale uint8 PNG, RGB uint8 PNG, and grayscale uint16 TIFF: each returned exactly 25 positive pixels / 100 ROI pixels = 25.0% |
| `git diff --check` | Passed |

Production dependency inspection found advisories in Next's pinned transitive PostCSS 8.4.31. An npm override to PostCSS 8.5.31 removed those findings; dependency installation, build and browser checks subsequently passed. This audit is a point-in-time package advisory check, not a comprehensive security assessment.

The first browser run passed the main workflow and uint16 tests, but two harness checks failed: Next's built-in route announcer made an alert selector ambiguous, and intercepted multipart forwarding omitted file content. The selectors were scoped to application alerts; the race test now submits the known synthetic source to the real analysis route before delaying the real response. No fabricated measurement is used. All four final browser checks passed. A final UI review also fixed the redundant reset case by making every settings invalidation trigger an analysis revision.

## Numerical coverage

- A: 10×10 with exactly 25 pixels at 200 and 75 at 0 → exact 25/100 and 25% at 100–255.
- B/C: zero-positive and all-positive images → exactly 0% and 100%, with appropriate QC notices.
- D: `[65,66,100,255]` at 66–255 → exactly three positive pixels; both bounds inclusive.
- E: distinct RGB patterns → red 4/4, green 1/4, blue 0/4; browser channel switching also verified.
- F: outside-ROI bright pixels excluded from both numerator and denominator. Full boundaries, one-pixel, zero-area, reversed, incomplete and out-of-bounds rectangles covered. Browser drag at device scale factor 2 maps to the expected original-image bounds.
- G: uint16 `[0,256,1000,65535]` at 1000–65535 → exactly 2/4, for PNG and TIFF, saturation fraction 0.25. Big-endian uint16 TIFF loading preserves values. Browser uint16 thresholds above 255 are verified.
- H: CSV measurement fields agree with API values; JSON downloads contain exact thresholds, ROI, counts and a 64-character source hash. All three preview dimensions and exported overlay PNG dimensions agree with the original. Opacity changes leave numeric measurements unchanged. Spreadsheet formula-like labels are escaped in CSV while original labels remain in JSON.
- I: corrupt/empty/unsupported files, alpha, unsupported TIFF layouts and pixel types, non-default TIFF orientation, invalid channels/thresholds/ROI, missing upload, file-byte limits, full-request limits and decoded-pixel limits are rejected. Actual content is used irrespective of filename/MIME hints.
- J: repeated identical inputs and settings produce identical full API results, including previews and CSV. Browser race test verifies that delayed older analysis does not replace the newer threshold result.

Browser tests also verify new-file state reset, metadata/channel selection, numeric and drawn ROI changes, full-image reset (including a redundant reset), marker preservation, overlay opacity, published-figure warning, all three downloads, corrupt-file messages and an injected backend-unavailable response. The failure-path test deliberately simulates unavailability; normal workflow tests use the real Python backend through Next.js.

## Fiji/ImageJ comparison: not yet executed

No Fiji/ImageJ executable was present in this environment. No direct Fiji comparison has been performed. The historical Iba1 cropped source image was not provided; its ~4.860% reference was never used as an expected output. A screenshot with a colored overlay is not a substitute for the source.

Generate reproducible, lossless reference inputs from the repository root:

```bash
.venv/bin/python scripts/generate_validation_images.py /tmp/neuroquant-validation
```

This command was executed. It produces gray8.png, rgb8.png, gray16.tif and expected.json. Each uses a 10×10 full-image ROI with exactly 25 positive pixels. Use 100–255 for grayscale/RGB uint8 (green plane for RGB) and 1000–65535 for grayscale uint16. These files were sent through the real Next.js→FastAPI pipeline and returned the expected counts.

For each reference file in Fiji: open without changing bit depth, extract exactly the specified channel (RGB: split channels and select green), retain the original intensity range, use the matching integer threshold bounds, select the full 10×10 rectangle and measure threshold-limited area fraction. Record Fiji version, settings, ROI, channel extraction and exact pixel counts/area fraction beside NeuroQuant's exported results. Both endpoints must be inclusive. If results differ, investigate channel interpretation, conversion, orientation, threshold and ROI conventions; do not alter expected values or analysis to force agreement. Repeat with a smaller identical ROI and an exact laboratory source image when available.

## Remaining limitations

No direct biological/clinical validation, Fiji equivalence, historical practice-image reproduction, macOS execution, Safari/Firefox coverage or public multi-user deployment testing is claimed. Supported TIFF layouts are intentionally narrow; some compressed TIFF codecs may require conversion to uncompressed supported TIFF. No unsupported automatic frame/channel selection occurs. No automatic settings import, zoom/pan, batch statistics or biological threshold selection is included. Browser downloads are browser-managed files; uploaded data are not retained in a server image store. The system Chromium fallback avoided the denied cdn.playwright.dev download domain without disabling TLS or signature checks.

All V1 functional acceptance items are implemented and covered by the checks above. Scientific equivalence and research validity remain separate pending milestones. Installation/start instructions were saved to the environment configuration draft. Draft saving is distinct from publication; no deployment, publication, merge or push was performed.

## Opaque RGBA compatibility fix

After a user encountered an opaque RGBA PNG, decoding was extended to accept RGBA PNGs only when every alpha sample equals 255. No RGB channel conversion, blending, normalization, or value changes occur. Any alpha value below 255 still produces a clear transparency-specific rejection. Added exact-array preservation, alpha=0/128/254 rejection, and end-to-end API equivalence tests. The original upload hash remains distinct from an RGB file with the same color values. The updated full Python suite ran: **49 passed**, one upstream deprecation warning. Earlier frontend/build/browser results above belong to the original V1 validation; those checks were not rerun for this backend-only decoding change.

## Automatic Otsu thresholding, algorithm 1.1.0

Added optional deterministic Otsu selection from the raw selected-channel ROI histogram, with full 256/65536-bin uint8/uint16 precision. Manual remains the default. Auto mode exports the method and selected inclusive bounds. Constant ROIs return an actionable validation error; no arbitrary split is invented. Biological correctness and Fiji auto-threshold equivalence remain unverified.

The updated Python suite ran: **63 passed**, zero failed/skipped, one upstream Starlette/httpx deprecation warning. New checks cover known two-class distributions, the earliest tie split, uint16 intensities above 255, agreement with an independently calculated class-variance reference, ROI-only histogram selection, valid exports, method validation, uniform ROI rejection, determinism and preservation of manual behavior. Strict TypeScript, ESLint and the Next.js production build passed. No dependency additions were needed.

The updated production-browser suite ran: **5 passed** in 14.5 seconds. The new test verifies choosing Auto: Otsu, the backend-selected lower bound, read-only auto controls, the method and exact bounds in downloaded JSON, uniform-ROI errors, stale export suppression and return to Manual. All four existing workflow tests also passed. Adding controls changed page scrolling; the ROI drag test was corrected to scroll its drawing surface into view before using pointer coordinates. No application assertions were removed.
