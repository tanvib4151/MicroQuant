# Biological QA review — NeuroQuant positive-area/1.1.0

Scope: code review, rerun numerical suite, and synthetic biological-interpretation stress cases. Review baseline: commit 7a9abee. No biological specimens, original microscopy files, matching assay controls, acquisition records, or Fiji measurements were supplied for this review. This is not an assay validation, literature review, diagnostic evaluation, or certification of research validity.

**Assessment:** the tested threshold-positive pixel calculations are internally consistent. The app is suitable for exploratory image-threshold workflows with expert review. It has not established that its positive pixels represent specific biological staining, and unattended biological interpretation or group comparisons are not validated. No counting defect was identified in these checks. Several interpretation and provenance limitations remain.

## Findings, ordered by research impact

### 1. High: automatic Otsu is not a biological-positive detector

Source: `api/app/services/thresholding.py`, `api/app/routers/analysis.py`, `web/components/ResultsPanel.tsx`.

Otsu partitions nonuniform intensities into two classes regardless of whether staining exists. A synthetic background-only distribution with equal counts at raw intensities 10–29 returned lower=20 and **5000/10000 = 50%** positive. A synthetic illumination gradient returned **5120/10240 = 50%**. These are correct outputs for the algorithm, but a user could mistake the panel heading “Positive staining area” for evidence of specific staining. The app does show an Otsu limitation warning; that warning is essential and does not itself validate a result.

Classification: expected algorithm limitation with high biological interpretation risk, not an off-by-one/counting bug. Neither a histogram with two classes nor an apparently convincing overlay proves specificity. Do not automatically turn a nonuniform negative control into zero or invent a universal background cutoff.

Recommended action: use the primary label “Threshold-positive ROI area,” explicitly distinguish image-derived from control-informed thresholds, and validate the analysis protocol using appropriate experimental controls. A control-informed method must specify the control material, acquisition settings, tolerated false-positive behavior, tissue sampling and threshold application procedure before it is implemented or described as validated. Otsu may remain an exploratory option.

### 2. Medium: the displayed saturation fraction is a datatype-ceiling fraction

Source: `api/app/services/quality_control.py:5`, `web/components/ResultsPanel.tsx:25`.

The implementation counts values equal to 255 or 65535. It cannot determine the instrument's actual saturation/clipping point. A hypothetical 12-bit detector clipped at 4095 and exported into uint16 was simulated with `[100,100,4095,4095]`: the reported saturation fraction was **0%**, even though half the values were at the assumed acquisition ceiling. Conversely, a datatype-max value alone does not prove detector clipping.

Classification: the numerical implementation matches its documented definition; the UI label “Saturated pixels” can overstate the biological/acquisition QC information available.

Recommended action: relabel the existing result “Pixels at datatype maximum” and state that zero does not exclude detector saturation. If instrument-level clipping QC is added, require a separately recorded acquisition ceiling derived from acquisition metadata or the user's instrument protocol. Do not infer it merely from the brightest observed pixel or rescale the scientific data.

### 3. Medium: published-figure provenance is not retained in exports

Source: `web/app/page.tsx` image-source state, `web/components/ExportControls.tsx`, `api/app/models.py`, `api/app/services/exports.py`.

The published/laboratory source selection controls an on-screen warning, but is not passed to the backend or exported in JSON/CSV. A downloaded result can therefore lose its explicit exploratory/published-figure context. JSON retains backend QC warnings, while CSV omits those warnings as well as source designation. Acquisition settings, specimen/control identities and annotation exclusions are also not captured.

Classification: a reproducibility/provenance gap, not a changed numerical measurement.

Recommended action: carry image-source designation into both export formats, export or explicitly reference QC/interpretation notes, and provide optional specimen, acquisition and control identifiers. Collect no unnecessary personal information. Preserve exact image hash, algorithm version, method, thresholds and ROI, which already work.

### 4. Medium: the denominator is rectangular ROI area, not identified tissue area

Source: `api/app/services/segmentation.py`.

The same 25 positive pixels yielded **25%** in a 100-pixel rectangle and **100%** in the 25-pixel bright subrectangle. This is correct mathematics, but comparing these percentages would be misleading without a consistent sampling rule. Background, tissue holes, borders, scale bars or annotations inside a rectangle enter the denominator and may enter the numerator. The app does not identify tissue automatically.

Classification: documented measurement scope requiring a sampling protocol, not a denominator bug.

Recommended action: predefine anatomical regions and inclusion/exclusion rules, use consistent sampling, and report the result explicitly as a fraction of selected ROI pixels. Tissue masking would be a separate feature requiring its own validation; selecting only the brightest region after seeing outcomes introduces selection bias.

### 5. Research-use limitation: per-image adaptive thresholds do not establish comparability

A two-class image with intensities 10/20 and a second image with every intensity doubled to 20/40 both yielded **50%** under Otsu, with lower bounds 11 and 21 respectively. This illustrates how per-image adaptation can preserve area fraction despite a global intensity shift. It does not establish whether that shift arose from staining, acquisition gain/exposure, or processing. Positive area is not a measurement of total protein abundance or intensity.

Recommended action: define one appropriate, documented thresholding procedure in the experimental protocol, ideally before inspecting group outcomes. Fixed control-derived thresholds can be appropriate under consistent acquisition, but are not universally appropriate either. Do not treat automatic thresholds as automatic normalization or assume that equal percentages imply equal biology.

## Marker-specific interpretation boundaries

These are assay-interpretation considerations, not claims established by the app or by these synthetic tests:

- **Iba1:** can label microglia and macrophage-associated populations; positive area alone does not distinguish resident microglia from infiltrating macrophages, count cells, or establish activation state. Changes may involve morphology, intensity, cellular density or sampling. Those alternatives require appropriate independent evidence.
- **GFAP:** GFAP-positive area is not a count of all astrocytes or a stand-alone measure of astrocyte activation. Cell processes, expression patterns, sectioning and acquisition affect coverage.
- **CD31:** threshold-positive area does not by itself establish vessel number, vascular perfusion, barrier integrity or blood–brain barrier permeability. Marker specificity and segmentation context require review.
- **ALPL/TNAP:** fluorescence staining is not directly a measurement of enzyme activity or catalytic function. Interpretation depends on the actual assay and controls.
- Marker identity must come from experimental knowledge. Green/red/blue are detector/display channels, not biological identities. The app's optional marker string does not validate specificity or compensate spectral bleed-through.

For group inference, independent biological units must be defined (for example animals); pixels, multiple fields and sections from the same specimen are not automatically independent biological replicates. This app does not implement statistics or establish experimental independence.

## Executed verification

1. `cd api && ../.venv/bin/python -m pytest -q`: **63 passed**, zero failed/skipped, one upstream Starlette/httpx deprecation warning. This reruns software checks for inclusive thresholds, channel isolation, ROI counts, uint16 preservation, deterministic Otsu, errors and exports.
2. ` .venv/bin/python scripts/bio_qa.py`: **8 synthetic stress cases completed with assertions passing**, through the real FastAPI endpoint using TestClient. Results are in `docs/BIO_QA_RESULTS.json`. Cases: background-only distribution, illumination gradient, two-class pattern, doubled intensity pattern, one bright pixel, full rectangular denominator, cropped denominator, and an assumed 12-bit clipping ceiling within uint16. Every image is synthetic; the “background-only” designation comes from how the simulation was constructed, not from a biological ground-truth assay.
3. Code trace of published-source state and export fields confirms the provenance gap described above. No frontend/browser suite was rerun for this documentation/QA-only change; prior application browser checks remain recorded in VALIDATION.md.

No application calculation, threshold choice, warning behavior or UI was changed during this review. The new script and results make the stress cases repeatable. Passing these checks establishes only the stated software behaviors; several of the passing cases deliberately demonstrate research-use limitations.

## Minimum next validation protocol

- Obtain original, lossless single-plane source images, including an appropriate known-positive sample and controls selected for the assay (for example unstained/autofluorescence controls, no-primary/secondary-only controls where applicable, and single-label controls for spectral bleed-through). Controls answer different questions and are not interchangeable or sufficient individually to establish antibody specificity.
- Record marker/antibody and staining protocol, fluorophore/channel mapping, specimen/section/anatomical region, objective and pixel sampling, exposure/laser power, detector gain/offset, acquisition bit depth/ceiling, and any upstream processing. Consistency and documented deviations matter.
- Define ROI inclusion rules and a thresholding protocol independently of desired group outcomes. Review representative controls and images with the assay scientist. Predefine acceptable control/background behavior and comparison tolerances for the actual assay; no universal numerical cutoff is justified by this review.
- Compare identical pixels, channels, bit depth, half-open ROI equivalents and manual intensity bounds in Fiji/ImageJ and NeuroQuant on uint8, RGB and uint16 references. Exact synthetic positive-pixel counts should match under identical semantics. Document software versions, differences and resolution of discrepancies. Auto-Otsu comparison additionally requires matching histogram, tie and bright-foreground conventions.
- Evaluate representative real images, including weak signal, dense signal, background/autofluorescence, uneven illumination, saturation, artifacts and tissue boundaries. Have blinded reviewers assess segmentation suitability under the predefined protocol; document disagreements rather than tuning to a historical target.
- Check sensitivity to justified threshold/ROI perturbations and assess repeatability across operators, staining/acquisition sessions and biological samples. Do not substitute many technical images for independent biological replication.

**Release position:** exploratory quantitative image analysis only. Direct Fiji equivalence, specificity, biological threshold validity, comparative assay performance and research conclusions remain unverified. Prioritize the saturation-label and provenance improvements, then validate a control-informed analysis protocol before using outputs as biological evidence.
