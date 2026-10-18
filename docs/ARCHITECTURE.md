# Architecture

NeuroQuant is an independent Next.js App Router / FastAPI monorepo. Hive's README, web/app/api/search/route.ts, and api/README.md were inspected at reference commit e8cc2c73c8c8ca2fdcc917df3c192adacbe05198. We reuse its web/api separation and server-only backend forwarding convention, without copying its search logic, authentication, databases or infrastructure. Hive was inspected in a temporary checkout and was not modified.

Browser → same-origin Next.js POST /api/analyze → FastAPI POST /analyze. GET /health reports backend liveness. No browser-to-backend CORS is needed or enabled. API_BASE_URL is server-only. Bind both services to loopback for local use.

The API separates decoding, fluorescence plane extraction, rectangular segmentation, QC, rendering and CSV serialization. Pydantic defines the response contract and algorithm version. Future metrics should be independent scientific services with their own contracts and tests; V1 includes only positive area.

The browser holds one File in memory. Requests are debounced 250 ms, aborted on changes and guarded by a generation number. Results and exports are hidden whenever settings differ from the completed result. Marker/channel persist across threshold changes; new uploads reset image-dependent state. Original files and decoded scientific arrays are not cached server-side or retained after a request. Multipart handling may use a temporary spooled upload during a request; FastAPI closes it afterward. No persistent upload store, analytics, external image service or accounts exist.

Requests currently resend the file and return three full-resolution PNG data URLs. This keeps a stateless, inspectable workflow at the cost of bandwidth and memory. Defaults: 20 MiB file, 4 million decoded pixels; request multipart overhead capped at 64 KiB beyond the file limit. Multiple simultaneous requests can consume proportionally more memory. Aborting a browser fetch cannot guarantee cancellation of a Python job already running. Use locally with one image at a time; this is not a hardened multi-user public deployment.

Display opacity is rendered by the backend and never changes segmentation. ROI drawing maps pointer CSS coordinates by the rendered image's bounding rectangle to original dimensions, floor at minimum edges and ceil at maximum edges. Device pixel ratio is never used. Numeric bounds permit exact reproducibility. The image fits its container; no zoom/pan transformation complicates coordinates.

Limits are configured separately on Python and Next.js processes. Set MAX_UPLOAD_BYTES consistently in both; MAX_DECODED_PIXELS is Python-only. No .env loader is implicit on Python: export variables before launching. Next reads web/.env.local if supplied. Preview PNGs and exported files contain scientific image data; users control any downloaded copies.
