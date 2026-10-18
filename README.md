# NeuroQuant V1

Reproducible fluorescence microscopy quantification using transparent, raw-intensity thresholding. Built for exploratory Iba1, GFAP, CD31, ALPL/TNAP and other marker-labelled workflows; marker names do not determine channels or algorithms. No AI, database, accounts or cloud storage.

## Local setup (macOS)

Prerequisites: Git, Python 3.11+ (tested on 3.12), Node.js 22+ (tested on 24), npm. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r api/requirements.lock
cd web
npm ci
cd ..
```

Alternatively, `bash scripts/setup.sh` installs both locked dependency sets. `api/requirements.txt` lists direct dependencies; `api/requirements.lock` pins the full tested Python environment.

Terminal 1, repository root:

```bash
source .venv/bin/activate
cd api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, repository root:

```bash
cd web
API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Open the frontend on port 3000 in your local browser. GET /health on backend port 8000 returns `{"status":"ok"}`. No credentials required. To run a production build locally, use `npm run build` then `API_BASE_URL=http://127.0.0.1:8000 npm start` in web/. This does not publish or deploy anything.

Configuration examples are in `.env.example`. Python reads exported process variables; Next.js can read `web/.env.local`. Default MAX_UPLOAD_BYTES=20971520 (20 MiB), MAX_DECODED_PIXELS=4000000. Export the upload limit to both services if changing it; only Python uses the pixel limit. Keep the backend URL server-only. Services bind to loopback, and no CORS permission is granted for external browser origins.

## Workflow

1. Upload a PNG, JPEG or TIFF. Contents are decoded and validated regardless of extension. Supported: single-frame uint8 grayscale, uint16 grayscale, uint8 RGB. Unsupported stacks, actual transparency, TIFF alpha, palettes, signed/float pixels and ambiguous TIFFs show errors.
2. Inspect filename, dimensions, bit depth, channel count and format. Assign an optional marker label and choose a channel explicitly. Grayscale uses a single plane. Green is an inspection default for RGB, not a marker inference.
3. Draw a rectangle on the original preview, adjust numeric coordinates, or reset to the entire image. Coordinates are original pixels with half-open bounds. Browser fitting and high DPI do not change the coordinate space. Exclude annotations, scale bars and non-tissue manually.
4. Choose **Auto: Otsu (bright signal)** under Threshold method to compute a threshold from the current channel and ROI, or set inclusive lower and upper raw intensity bounds manually using numeric controls or sliders. Default 66 is only a demonstration. uint16 analysis remains in 0–65535. Changing channel, ROI or thresholds recalculates on FastAPI.
5. Inspect the original, selected channel and red overlay. Cyan outlines the ROI. Opacity affects visualization only. uint16 previews use fixed floor(value/257) display mapping, never measurement conversion.
6. Read positive pixels / ROI pixels × 100. Display rounds percent to three decimals; exports preserve precision. Review saturation and zero/all-positive warnings.
7. Download CSV measurements, JSON settings (including source SHA-256) and full-resolution overlay PNG. Match the JSON source hash before reproducing with the same file and settings. Automatic settings import is not part of V1.

Select published-figure source to show an exploratory-use notice. Uploads remain within the local browser/Next/Python workflow, with no third-party image services or persistent server upload store. Downloaded exports are retained only where you save them.

**Positive area measures pixels meeting an intensity threshold. It does not measure cell number or establish biological activation.** Background, controls, acquisition consistency and ROI choices matter. Do not treat separately acquired samples as comparable without a justified protocol.

## Checks

```bash
# repository root, activated Python environment
cd api
python -m pytest -q
cd ../web
npm run typecheck
npm run lint
npm run build
# Install browser once; Linux may additionally need OS browser libraries.
npx playwright install chromium
# Start backend and frontend first as above, then:
TEST_PYTHON=../.venv/bin/python npm run test:e2e
```

In this cloud image, use `PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium TEST_PYTHON=../.venv/bin/python npm run test:e2e` to use installed Chromium without downloading a browser. Browser tests run against local ports 3000 and 8000 and generate synthetic files in a temporary directory. For cloud development, use the existing isolated checkout; do not create a worktree. See [validation](docs/VALIDATION.md) for actual results and unverified comparisons.

## Architecture and scientific scope

`web/` is strict TypeScript Next.js App Router + React + Tailwind. Its server route forwards bounded multipart requests to `api/`, a modular FastAPI/NumPy/Pillow/tifffile engine. Separate loading, channel extraction, segmentation, QC, rendering and export services keep future methods testable. Hive's frontend/backend separation was reviewed as an architectural reference; its unrelated infrastructure was not adopted. See [architecture](docs/ARCHITECTURE.md) and [exact methods](docs/ANALYSIS_METHODS.md).

Limits: one image at a time; full-file resend and full-resolution preview responses on updates; no sessions/batch/statistics, automatic tissue detection, color normalization, validated biological thresholds, zoom/pan, AI or deployment. Only supported single-frame layouts are accepted; export complex microscopy formats into a supported raw plane first. Temporary multipart spooling may occur during requests. This is local research software foundation, not a validated diagnostic or multi-user service.

Fiji equivalence is pending direct comparison of identical source pixels, channels, ROIs and thresholds. The historical 536×286, threshold 66–255, ~4.860% Iba1 example is not an expected result: its original cropped image has not been supplied. Never use a red-overlay screenshot as measurement input or tune calculations to match that number.

Next milestone: perform and document direct Fiji comparisons on the included synthetic cases and an exact laboratory reference image. Later algorithms (mean fluorescence, background correction, cell segmentation, morphology, colocalization, batches) should be added as separately validated modules and are not implemented in V1.

Fully opaque RGBA PNGs are accepted automatically: only the all-255 alpha plane is discarded, preserving every RGB value. PNGs with any transparent or partially transparent pixel are rejected with an explanation; no background compositing occurs. The source hash still identifies the original RGBA upload. TIFF alpha and palette images remain unsupported.

## Automatic threshold selection

Choose **Auto: Otsu (bright signal)** after uploading an image. FastAPI chooses a raw-intensity split from the selected ROI histogram; lower becomes split+1 and upper is the datatype maximum. It recalculates when you change the channel or ROI. Manual remains the default for compatibility, and switching back restores your manual values. Both CSV and JSON record `threshold_method`, actual bounds, ROI and algorithm version `positive-area/1.1.0`.

Otsu is a deterministic image-statistics method, not AI and not biological validation. It assumes brighter pixels are foreground. It can perform poorly with uneven illumination, weak signal, large backgrounds or unimodal images. Uniform/one-pixel ROIs have no valid two-class split and require Manual. Image-specific thresholds can differ between samples; automated selection does not make samples comparable or replace controls. Inspect the overlay and establish a consistent acquisition and analysis protocol. Histogram and tie semantics are specified in ANALYSIS_METHODS.md.

See [Biological QA review](docs/BIO_QA.md) for interpretation risks, executed synthetic stress cases and a proposed laboratory validation protocol. Run `.venv/bin/python scripts/bio_qa.py` from the repository root to reproduce those cases; they are not biological validation.

## Provenance and biological QA safeguards

Results are labelled **Threshold-positive ROI area**: the denominator is all pixels in your rectangle, not automatically detected tissue. **Pixels at datatype maximum** describes values at 255/65535 and is not an instrument saturation measurement; zero does not exclude detector clipping. No acquisition ceiling is inferred from the brightest pixel. The old API/CSV `saturation_fraction` field remains a compatibility alias of `datatype_max_fraction`, with its meaning defined in exports.

After uploading each image, choose **Image source** (unspecified, laboratory, synthetic or published), and optionally expand **Provenance and controls** to record sample/specimen ID, acquisition notes and a control reference. Both CSV and JSON retain those fields plus QC warnings, interpretation notes, definitions and export schema version. Source and provenance reset with each new upload to avoid attributing the previous image's metadata to a new file. Changing them refreshes the backend result before exports are enabled. Notes are descriptive user entries, not proof of validation, and are not used to change measurements. Use only non-sensitive identifiers where possible; downloaded exports retain whatever notes you enter.

Open **Before biological interpretation** for the laboratory validation checklist. It is guidance, not completed validation. Real original images, assay controls, acquisition records and direct Fiji comparisons are still required. The Bio QA report records which issues were addressed and which scientific limitations remain.
