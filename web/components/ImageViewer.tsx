/* eslint-disable @next/next/no-img-element */
"use client";
import { useRef, useState } from "react";
import type { ROI, Result } from "@/lib/types";
export default function ImageViewer({
  result,
  roi,
  onRoi,
}: {
  result: Result;
  roi: ROI;
  onRoi: (roi: ROI) => void;
}) {
  const start = useRef<{ x: number; y: number } | null>(null);
  const [draft, setDraft] = useState<ROI | null>(null);
  function point(e: React.PointerEvent<HTMLDivElement>) {
    const r = e.currentTarget.getBoundingClientRect();
    return {
      x: Math.max(
        0,
        Math.min(result.width, ((e.clientX - r.left) / r.width) * result.width),
      ),
      y: Math.max(
        0,
        Math.min(
          result.height,
          ((e.clientY - r.top) / r.height) * result.height,
        ),
      ),
    };
  }
  function rectangle(a: { x: number; y: number }, b: { x: number; y: number }) {
    return {
      x0: Math.floor(Math.min(a.x, b.x)),
      y0: Math.floor(Math.min(a.y, b.y)),
      x1: Math.ceil(Math.max(a.x, b.x)),
      y1: Math.ceil(Math.max(a.y, b.y)),
    };
  }
  const box = draft || roi;
  return (
    <div className="viewers">
      <figure>
        <figcaption>01 / Original · draw ROI</figcaption>
        <div
          className="image-wrap"
          data-testid="roi-surface"
          onPointerDown={(e) => {
            start.current = point(e);
            e.currentTarget.setPointerCapture(e.pointerId);
          }}
          onPointerMove={(e) => {
            if (start.current) setDraft(rectangle(start.current, point(e)));
          }}
          onPointerUp={(e) => {
            if (start.current) {
              const next = rectangle(start.current, point(e));
              start.current = null;
              setDraft(null);
              if (next.x1 > next.x0 && next.y1 > next.y0) onRoi(next);
            }
          }}
          onPointerCancel={() => {
            start.current = null;
            setDraft(null);
          }}
        >
          <img
            draggable={false}
            src={result.original_png}
            alt="Original microscopy image"
          />
          <div
            className="roi-box"
            style={{
              left: `${(box.x0 / result.width) * 100}%`,
              top: `${(box.y0 / result.height) * 100}%`,
              width: `${((box.x1 - box.x0) / result.width) * 100}%`,
              height: `${((box.y1 - box.y0) / result.height) * 100}%`,
            }}
          />
        </div>
      </figure>
      <figure>
        <figcaption>02 / Selected {result.channel} channel</figcaption>
        <img src={result.channel_png} alt="Selected intensity channel" />
      </figure>
      <figure>
        <figcaption>03 / Threshold-positive overlay · cyan ROI</figcaption>
        <img src={result.overlay_png} alt="Segmentation overlay" />
      </figure>
      <p className="muted">
        Display mapping: {result.preview_mapping}. Measurement always uses raw
        decoded intensities.
      </p>
    </div>
  );
}
