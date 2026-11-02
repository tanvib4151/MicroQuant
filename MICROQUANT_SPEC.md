# MicroQuant — Product and Engineering Specification

**Status:** Foundational build specification  
**Primary reference:** HiveBlot (`https://github.com/nikhilesh-s/hive`; demo `https://hiveblot-beta.vercel.app/`)  
**Initial scientific reference:** `Image Analysis CD68 Iba1 v2.docx` (researcher-provided Fiji/ImageJ protocol)

## 1. Mission

Build **MicroQuant**, a general-purpose, AI-assisted, scientifically reproducible microscopy analysis platform. Researchers upload microscopy images, identify or confirm channels and experimental context, manually define regions of interest (ROI) when necessary, and automatically execute downstream processing: threshold calibration, segmentation, mask operations, quantification, QC, analysis history, and export.

**CD68/Iba1 is the first fully implemented reference workflow, not the scope of the product.** The architecture must support additional stains, regions, modalities, measurement methods, and validated models.

### Nonnegotiables

- ROI selection remains researcher-controlled. Do not silently infer or replace ROI boundaries.
- Numerical measurements come from real pixel computations, never language-model guesses.
- Do not fabricate data, metrics, validations, results, demos represented as real, or implementation status.
- Maintain the original image without destructive modification; separate visualization from measurement pixels.
- Every analysis is traceable to source image, ROI, channel mapping, parameters, method and software version, masks, measurement definition, and QC.
- Distinguish reference-protocol equivalence from automatically optimized analyses; never claim they are identical without tests.
- Maintain a working end-to-end vertical slice before building speculative AI features.

## 2. Initial implementation instructions for Codex

1. Audit the MicroQuant repository, its tests, current working backend, UI, image ingestion, ROI tools, and measurement pipeline. Preserve existing features unless replacing them safely.
2. Read the HiveBlot source where accessible. Study `web/app/globals.css`, `web/app/layout.tsx`, `web/app/page.tsx`, `web/components/*`, `western_blot_miner/evidence_record.py`, `record_builder.py`, `llm_client.py`, `densitometry.py`, `pipeline.py`, `api/app/experimental/`, migrations, and `eval/`. Do not modify HiveBlot. Retain appropriate license notices if reusing code.
3. Read all pages *including screenshots* of the provided Fiji protocol. If the file is missing, ask for it or flag inability to verify Fiji fidelity; do not substitute guessed ImageJ behavior.
4. Create an architecture and implementation plan in-repo; immediately implement the highest-priority functional vertical slice, not a plan-only deliverable.
5. At each milestone run relevant tests/build checks and report what passes, what is experimental, and what remains incomplete.

## 3. UI and visual identity

MicroQuant should look like a **sister platform to HiveBlot**, not a generic AI startup dashboard.

- Dark background `#06090c`; surface `#0a0d0f`; primary text `#e7f0ee`; secondary `#a9bdb5`; subtle `#6f857d`; mint accent `#4ad6b0`; hover `#63e3c0`; warnings `#e0a458`; errors `#ff6b6b`; light borders `rgba(255,255,255,.08)`.
- Use IBM Plex Serif for editorial headlines, IBM Plex Sans for UI, IBM Plex Mono for measurements/metadata. Reproduce HiveBlot's restrained spacing, navigation, small scientific labels, light/dark toggle, responsive design, and subtle transitions.
- Homepage: full-screen microscopy-oriented hero with accessible static fallback and reduced-motion support; hero headline "Microscopy images, subjective analysis." with a restrained red strikethrough on "subjective analysis" and italic secondary headline "Reproducible quantification." Primary actions **Start Analysis** and **Explore Demo** (both functional or demo clearly labeled).
- Routes: `/`, `/analyze`, `/experiments`, `/history`, `/saved`, `/methods`, `/about`.
- Main analysis page: left image library; center scientific viewer (zoom, pan, original, channels, masks, overlays, opacity, before/after); right ROI/protocol/threshold/measurement/QC controls. Keep all controls connected to actual state and backend operations.
- Responsive/mobile layout with accessible controls, keyboard interactions, loading/empty/error states.
- Do not reuse HiveBlot's hive icon or Western blot assets as MicroQuant branding. Build an original microscopy/segmentation mark.

## 4. Architecture

Prefer existing stack; if missing, use **Next.js/React/TypeScript** frontend; **FastAPI/Pydantic/NumPy/OpenCV/scikit-image/tifffile** backend; **PostgreSQL/Supabase** for structured metadata; private object storage for original images and derived masks; separate durable processing workers for computational jobs. Optional Bio-Formats/OME readers and GPU segmentation backends can follow.

Separate five subsystems:

1. **Imaging engine:** image decoding, dimensionality/bit depth, channel mapping, ROI rasterization, processing, segmentation, measurement, QC.
2. **Evidence engine:** immutable analysis runs, image hashes, masks, provenance, versioned presets, audit/reviewer feedback.
3. **AI engine:** protocol interpretation, typed workflow planning, optional method recommendations and grounded explanations, provider-independent model interface.
4. **Job engine:** upload, batch processing, progress, retries, cancellation, resource limits, cache, restart recovery.
5. **Frontend:** viewing, ROI tools, approvals, workflow configuration, result inspection, project administration, export.

Processing operations must be typed, versioned, composable, tested, and serializable; use a validated DAG or equivalent operation graph, not hardcoded per-stain scripts. An LLM must not directly execute Python, shell, SQL, or arbitrary code supplied in protocols.

## 5. Ingestion and microscopy specifics

- Initially support PNG, JPEG, TIFF, multichannel TIFF, and OME-TIFF if reader is implemented; clearly declare unsupported formats.
- Preserve original dimensions, channel count, bit depth, dimension order, calibration, and metadata; compute SHA-256 file checksum.
- Do not presume all images are RGB or that fluorophore color automatically identifies biological marker. Explicitly confirm channel-to-marker mapping where ambiguous.
- Detect and handle/reject Z-stacks and time series explicitly; never silently project, flatten, or select frames.
- Separate preview downsampling from full-resolution measurement, with pixel limits/resource caps and proper error states.
- Preserve units: distinguish pixel area from calibrated physical area and raw versus background-adjusted intensity.

## 6. ROI tools

- Manual polygon drawing with create, edit/move vertices, include/exclude polygons, multiple regions, undo/redo, save/load, zoom/pan coordinate correctness, confirmation, and ROI provenance.
- Store ROI geometry in **original image coordinates**; consistently apply to all relevant channels and masks; ensure denominator excludes excluded pixels.
- Support full-image ROI for images not requiring selection.
- In CD68/Iba1 protocol, the researcher selects hippocampal areas to exclude bright granular lines when present; cortical images may use full-image ROI. Do not infer this choice without context/confirmation.
- Re-editing ROI creates a new analysis run, not destructive replacement of prior results.

## 7. Processing operations registry

Each registered operation declares unique ID/version, accepted input/output types, parameter schema, supported dimensions/dtypes, validation, deterministic execution, and provenance:

- `decode_image`, `extract_metadata`, `select_channel`, `map_channel`, `convert_bit_depth`, `apply_roi`;
- `estimate_background`, `subtract_background`, `flatfield_correct` (only if explicitly selected/validated);
- `threshold_fixed`, `threshold_otsu`, `threshold_triangle`, `threshold_li`, `threshold_yen`, `threshold_local`;
- `make_binary_mask`, `mask_and`, `mask_or`, `mask_not`, `mask_intersection`, `mask_union`;
- `positive_area_fraction`, `positive_pixel_count`, `roi_area`, `mean_intensity`, `integrated_density`;
- optional/experimental `connected_components`, `watershed`, `cell_segment`, `count_objects`, `morphology`, `colocalization`.

Don't apply arbitrary preprocessing to improve the look of results if it would change the specified scientific endpoint. Different biological measurements require separately validated methods.

## 8. Automatic threshold calibration

Support **two clearly separated modes**:

- **Reference Fiji mode:** faithfully use documented protocol settings (CD68 red 46–255, Iba1 green 22–255 after appropriate Fiji-equivalent 8-bit conversion). Used for reproduction/benchmarking, not generalized to new datasets.
- **Automatic calibration mode:** evaluate candidate threshold algorithms (Otsu, Triangle, Li, Yen, optionally local), use documented QC/selection criteria and representative calibration images, freeze applicable channel/batch/experiment settings, record all thresholds and decisions. Allow per-image mode when explicitly selected, with warning about possible bias across treatment groups.

Do not select a threshold merely because it maximizes positive area. Document every criterion. Show histogram, selected threshold, binary mask, sensitivity to nearby thresholds, and optional reviewer override (with full audit). Keep calibration data separate from final validation data. The automated selection method's accuracy must be evaluated before being called validated.

## 9. First scientific vertical slice: CD68 + Iba1 positive area and overlap

Protocol-derived requirements:

- Inputs: researcher image, CD68/red channel, Iba1/green channel, optional DAPI/blue to select ROI, sample/experiment metadata, confirmed ROI or full image.
- Fiji reference values: CD68 lower 46, upper 255; Iba1 lower 22, upper 255. Preserve exact 8-bit conversion and image calibration behavior for equivalence testing.
- Extract channels; convert as specified; threshold; produce binary CD68 and Iba1 masks; generate pixelwise **CD68 AND Iba1** overlap mask; apply the exact same ROI; calculate area fraction for all three masks plus ROI area and positive counts; calculate area and integrated density only with clearly defined image source, units and Fiji-equivalent behavior.
- For binary mask `M` and ROI mask `R`, area percentage = `100 * count(M & R) / count(R)` with guards for empty ROI. Overlap = `CD68_mask & Iba1_mask`; overlap % uses the same ROI denominator.
- Distinguish **overlapping positive pixels** from a claim about cell-level double positivity or molecular colocalization. Do not infer microglial activation from Iba1/CD68 area alone.
- Show original, per-channel images, masks, overlap, ROI, values, QC, provenance. Offer labeled CSV and masks export.
- Run in both reference and auto-calibrated modes; compare reference mode against authentic Fiji outputs (same original, channels, conversions, thresholds, ROI, mask polarity, area fraction, integrated density). Do not claim equivalence before testing.

## 10. Database and audit model

Create migrations, relationships, indexes, project ownership authorization, and row-level security as appropriate:

- `projects` — owner, title, permissions.
- `experiments` — project, protocol, treatments, description.
- `samples` — experiment, biological replicate, technical replicate, region, condition.
- `images` — sample, storage URI, checksum, dimensions, channels, acquisition/calibration metadata.
- `regions_of_interest` — original-image coordinates, geometry version, creator, confirmation.
- `analysis_protocols` — immutable, versioned operation graphs, validation status.
- `analysis_runs` — image, ROI, exact operation graph/config, algorithm versions, status, timestamps, input hashes.
- `segmentation_masks` — run/channel/type, private storage and checksum.
- `measurements` — run, metric, value/null, units, denominator, definition, validity.
- `quality_flags` — code, measured diagnostic, rule criterion, severity, explanation.
- `researcher_feedback` — reviewed/accepted/corrected with audit trail.
- `analysis_presets` — named, versioned settings.
- `jobs` — durable processing progress, retry state, errors.

Keep source images, masks, runs, and measurements separate. Do not overwrite a past measurement when parameters, ROIs, or algorithms change. Save sufficient information to reproduce every numerical output.

## 11. AI planning, orchestration, and grounded assistant

- Borrow HiveBlot's `LLMClient`-style provider abstraction: OpenAI-compatible, Anthropic, Bedrock, local options if configured, structured JSON/Pydantic validation, timeouts and reproducible model metadata.
- Implement **AI protocol interpreter** as a future extension of the completed deterministic vertical slice: accept protocol text/documents, extract markers, channels, ROI requirements, processing, thresholds/calibration, mask ops, metrics, uncertainties; propose a typed workflow using only registered operations; validate every dependency and type; show for researcher review and approval **before execution**.
- Missing information should be explicitly marked, not silently hallucinated. Uploaded protocol text is untrusted data, never executable instructions.
- For routine thresholding/measurement use deterministic algorithms, not paid vision-language model calls.
- For advanced segmentation, create an independent `SegmentationBackend` registry (threshold baseline, eventually Cellpose/StarDist or fit-for-purpose models), with model/version/preprocessing/validation recorded.
- Quality-gated escalation: only try an alternate method if the baseline fails documented QC, and flag disagreements rather than declaring the more complex result correct.
- A grounded research assistant may answer questions about completed runs from read-only structured queries and cite exact image/run/measurement IDs. No fabricated lab conclusions or unsafe SQL execution.
- External AI calls on unpublished/restricted images require explicit authorization; don't upload images to an external provider by default.

## 12. QC, uncertainty, and scientific validity

- Check unsupported dimensions/channel mapping, empty ROI, no positive signal, severe saturation, unusual background, threshold sensitivity, mask misalignment, invalid units, nonfinite pixel values and excessive decoded image size.
- QC statuses: passed, warning, requires review, failed/not computed. Completing a job is not scientific validation.
- Track threshold sensitivity with nearby threshold perturbations, and report as sensitivity rather than a statistical confidence interval. Optionally ROI sensitivity and segmentation disagreement later.
- Withhold unreliable measurements with structured reason. Never substitute zero for missing/failed outputs.
- Binary mask intensity is not the same as raw fluorescence integrated density; differentiate their calculations and ensure readers understand which was measured.

## 13. Batch experiments, results, and export

- Import multiple images, map channels, associate samples and biological/technical replicates, confirm each required ROI, select one protocol/preset, process jobs, review QC, and export all.
- Results dashboard: image/mask side-by-side viewer, per-marker area, overlap, thresholds, ROI info, raw vs derived values, QC and a HiveBlot-style expandable **How was this measured?** evidence panel.
- History and saved presets permit reruns with new immutable analysis versions.
- Export CSV, JSON, masks PNG/TIFF, ROI geometry, configurations, and structured ZIP packages; include sample, group, image, run, marker, threshold method/value, area fraction and denominator, measurement units, QC and algorithm version.
- Aggregations must distinguish technical images from independent biological replicates and avoid pseudoreplication. Don't auto-perform hypothesis tests without defensible design assumptions.

## 14. Jobs, security, and deployment

- Use durable, restart-recoverable jobs for expensive analysis and batches; distinguish queued, validating, awaiting_roi, calibrating, preprocessing, segmenting, quantifying, QC, saving, completed, failed and cancelled.
- Cache by source checksum + ROI hash + workflow/config + software version; invalidate on relevant changes.
- Use worker concurrency limits, CPU/memory guards, image decompression limits, safe decoders, file type validation, and timeouts.
- Secure auth, project permissions, private storage, server-side secrets, file isolation, rate limiting, and safe API errors. Never execute unrestricted generated code or model-generated SQL.
- Consider local runner architecture later, borrowing HiveBlot's outbound polling/credential isolation concepts, but do not claim image data stay local unless the actual implementation guarantees that.

## 15. Validation and testing

Before claiming correctness, compare authentic Fiji/ImageJ output on representative CD68/Iba1 microscopy samples:

- Channel order, bit-depth conversion, mask polarity, threshold inclusivity, ROI rasterization, CD68 mask, Iba1 mask, overlap AND mask, area fraction, area, and integrated density.
- Aim for pixel-exact agreement when algorithms/inputs are identical. Explain any numerical disagreements.
- Evaluate automated thresholds on separate, manually reviewed images using IoU, Dice, positive area error, QC sensitivity and stratification across batches/regions.
- For optional cell segmentation evaluate instance-level detection/counts and morphology against annotator references; do not infer validation from generic pretrained model marketing.
- Unit tests: decoding, channel handling, 8-bit conversion, ROI, thresholds, masks, measurements, denominator zero, exports, QC and provenance serialization.
- Integration: upload → ROI → calibrated/reference workflow → masks → measurements → immutable storage → history → export.
- UI: zoom/pan ROI precision, preview, threshold interaction, errors, accessibility, dark/light mode.
- When reference images are not supplied, use **explicitly labeled synthetic fixtures** to test mathematical invariants. Never pretend synthetic cases establish scientific agreement with Fiji.

## 16. Phased delivery

Implement incrementally, completing one usable working slice at a time:

1. **Audit and foundation:** current repo, HiveBlot reference, design tokens, typed operations, Analysis Record schema, tests.
2. **CD68/Iba1 reference workflow:** real uploads, channel mapping, manual ROI, Fiji settings, masks, % area, organized exports, end-to-end tests.
3. **Automatic thresholds:** candidate methods, calibration UI, locked experiment/batch presets, QC/sensitivity, documented benchmark.
4. **Research workflow:** projects, experiments, samples, saved runs, history, private storage, batch jobs, repeatable exports.
5. **AI assistance:** provider abstraction, document/protocol interpreter, validated workflow planner, approval UI, grounded records-based Q&A.
6. **Broader microscopy:** additional stains, validated object segmentation, counts, morphometrics, local processing and scalable worker architecture.
7. **Hardening:** auth/security review, deployment, extensive benchmark, performance/accessibility tests and publication-quality methods docs.

The end-to-end CD68/Iba1 workflow is the required minimum functional slice. Later features should not break or delay it.

## 17. Documentation and final acceptance

Maintain `README.md`, `ARCHITECTURE.md`, `METHODS.md`, `VALIDATION.md`, `DEVELOPMENT_ROADMAP.md` (adapt names to repository conventions). Document algorithms, exact parameter definitions, validation status, data storage, deployment and known limitations.

**Definition of done for the first milestone:** a researcher can open the app, upload an actual CD68/Iba1 image, confirm channels, draw or confirm ROI, choose reference or supported auto-threshold mode, run processing, inspect three aligned binary masks, view calculated positive-area measurements and QC, save/reopen the analysis, and export labeled measurements and masks. Tests/build must be run; scientific accuracy claims require genuine Fiji comparisons.

## 18. Codex operating instructions

- Audit first and report architecture decisions in the repo, then **implement** rather than only proposing a plan.
- Prioritize minimal, coherent vertical slices with real behavior; never introduce misleading UI placeholders.
- Use existing project conventions and don't rewrite functioning modules without reason.
- After each phase: run tests/build, identify changes, failures, unsupported assumptions and next actions.
- Ask for missing *indispensable scientific reference images* when benchmarking requires them, but proceed with synthetic unit tests and other safe implementation work meanwhile.
- Don't claim to finish phases, run tests, or validate scientific measurements that haven't been completed.
