"use client";
import { useEffect, useRef, useState } from "react";
import ImageUploader from "@/components/ImageUploader";
import ChannelSelector from "@/components/ChannelSelector";
import ThresholdControls from "@/components/ThresholdControls";
import RoiSelector from "@/components/RoiSelector";
import ImageViewer from "@/components/ImageViewer";
import ResultsPanel from "@/components/ResultsPanel";
import ExportControls from "@/components/ExportControls";
import { analyze } from "@/lib/api";
import type { Result, ROI, ThresholdMethod } from "@/lib/types";
export default function Home() {
  const [file, setFile] = useState<File | null>(null),
    [channel, setChannel] = useState("auto"),
    [marker, setMarker] = useState(""),
    [lower, setLower] = useState(66),
    [upper, setUpper] = useState(255),
    [roi, setRoi] = useState<ROI | null>(null),
    [opacity, setOpacity] = useState(0.45),
    [result, setResult] = useState<Result | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const [method, setMethod] = useState<ThresholdMethod>("manual");
  const generation = useRef(0);
  const [revision, setRevision] = useState(0);
  const [fresh, setFresh] = useState(false);
  const [source, setSource] = useState("laboratory");
  useEffect(() => {
    if (!file) return;
    const id = ++generation.current;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setBusy(true);
      setError("");
      analyze(
        file,
        channel,
        marker,
        lower,
        upper,
        roi,
        opacity,
        controller.signal,
        method,
      )
        .then((data) => {
          if (id !== generation.current) return;
          setResult(data);
          if (channel === "auto") {
            setFresh(false);
            setChannel(data.channel);
            if (data.dtype === "uint16") setUpper(65535);
          } else {
            setFresh(true);
          }
        })
        .catch((e) => {
          if (!controller.signal.aborted && id === generation.current) {
            setError(e.message);
            setFresh(false);
          }
        })
        .finally(() => {
          if (id === generation.current) setBusy(false);
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [file, channel, marker, lower, upper, roi, opacity, revision, method]);
  function invalidate() {
    generation.current++;
    setRevision((value) => value + 1);
    setFresh(false);
    setError("");
  }
  function upload(next: File) {
    invalidate();
    setFile(next);
    setResult(null);
    setChannel("auto");
    setMethod("manual");
    setLower(66);
    setUpper(255);
    setRoi(null);
    setOpacity(0.45);
    setMarker("");
  }
  const full = result
    ? { x0: 0, y0: 0, x1: result.width, y1: result.height }
    : null;
  return (
    <>
      <header>
        <div className="brand">
          N<span>Q</span>
        </div>
        <div>
          <h1>
            NeuroQuant <sup>V1</sup>
          </h1>
          <p>Reproducible fluorescence microscopy quantification</p>
        </div>
        <span className="badge">Local-first · raw pixel analysis</span>
      </header>
      <main>
        <aside className="panel">
          <h2>Image setup</h2>
          <ImageUploader onFile={upload} />
          {file && <p className="filename">{file.name}</p>}
          {result && (
            <>
              <dl>
                <dt>Dimensions</dt>
                <dd>
                  {result.width} × {result.height} px
                </dd>
                <dt>Pixel type</dt>
                <dd>{result.dtype}</dd>
                <dt>Channels</dt>
                <dd>{result.channels.length}</dd>
                <dt>Format</dt>
                <dd>{result.format}</dd>
              </dl>
              <label>
                Marker label (optional)
                <input
                  maxLength={200}
                  value={marker}
                  placeholder="e.g. Iba1"
                  onChange={(e) => {
                    invalidate();
                    setMarker(e.target.value);
                  }}
                />
              </label>
              <ChannelSelector
                channels={result.channels}
                value={channel === "auto" ? result.channel : channel}
                onChange={(v) => {
                  invalidate();
                  setChannel(v);
                }}
              />
              <RoiSelector
                roi={roi || full!}
                width={result.width}
                height={result.height}
                onChange={(r) => {
                  invalidate();
                  setRoi(r);
                }}
              />
            </>
          )}
          <label>
            Image source
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="laboratory">Laboratory / synthetic image</option>
              <option value="published">
                Published figure (exploratory only)
              </option>
            </select>
          </label>
          {source === "published" && (
            <p className="warning">
              Published figures may be adjusted, compressed or annotated.
              Measurements are exploratory and are not laboratory-grade
              evidence.
            </p>
          )}
        </aside>
        <section className="workspace">
          <div className="section-heading">
            <h2>Image analysis</h2>
            <span role="status">
              {error
                ? "Analysis failed"
                : busy
                  ? "Analyzing…"
                  : file && !fresh
                    ? "Settings changed · awaiting result"
                    : result
                      ? "Analysis complete"
                      : "Awaiting image"}
            </span>
          </div>
          {error && (
            <p role="alert" className="warning">
              {error}
            </p>
          )}
          {result ? (
            <ImageViewer
              result={result}
              roi={roi || full!}
              onRoi={(r) => {
                invalidate();
                setRoi(r);
              }}
            />
          ) : (
            <div className="empty">
              <div className="empty-mark">＋</div>
              <h2>Start with your image</h2>
              <p>
                Upload a single-frame microscopy image to inspect its channels,
                select tissue, and measure threshold-positive area.
              </p>
              <small>No image data is sent to third-party services.</small>
            </div>
          )}
        </section>
        <aside className="panel">
          <fieldset disabled={!result}>
            <ThresholdControls
              method={method}
              onMethodChange={(next) => {
                invalidate();
                setMethod(next);
              }}
              lower={
                method === "otsu" && result?.threshold_method === "otsu"
                  ? result.lower_threshold
                  : lower
              }
              upper={
                method === "otsu" && result?.threshold_method === "otsu"
                  ? result.upper_threshold
                  : upper
              }
              max={result?.dtype === "uint16" ? 65535 : 255}
              onChange={(lo, hi) => {
                invalidate();
                setLower(lo);
                setUpper(hi);
              }}
            />
            <label>
              Overlay opacity · {Math.round(opacity * 100)}%
              <input
                aria-label="Overlay opacity"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={opacity}
                onChange={(e) => {
                  invalidate();
                  setOpacity(Number(e.target.value));
                }}
              />
            </label>
          </fieldset>
          {result && fresh && !busy ? (
            <>
              <ResultsPanel result={result} />
              <ExportControls result={result} opacity={opacity} />
            </>
          ) : (
            <p className="muted">
              {file
                ? "Results and exports appear when current settings finish processing."
                : "Upload an image to calculate results."}
            </p>
          )}
          <p className="interpretation">
            Positive area measures the fraction of image pixels meeting the
            selected intensity threshold. It does not measure cell number or
            establish biological activation.
          </p>
        </aside>
      </main>
      <footer>
        Threshold selection is a scientific decision. Background fluorescence,
        autofluorescence, exposure, detector gain, saturation, tissue
        preparation, non-specific staining, compression and uneven illumination
        can affect results. Compare samples only with consistent acquisition and
        analysis procedures. No Fiji equivalence or research validation is
        claimed.
      </footer>
    </>
  );
}
