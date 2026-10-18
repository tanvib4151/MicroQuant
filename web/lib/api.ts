import type { ROI, Result } from "./types";
export async function analyze(
  file: File,
  channel: string,
  marker: string,
  lower: number,
  upper: number,
  roi: ROI | null,
  opacity: number,
  signal: AbortSignal,
): Promise<Result> {
  const form = new FormData();
  form.set("image", file);
  form.set("channel", channel);
  form.set("marker", marker);
  form.set("lower_threshold", String(lower));
  form.set("upper_threshold", String(upper));
  form.set("overlay_opacity", String(opacity));
  if (roi)
    for (const [key, value] of Object.entries(roi))
      form.set(`roi_${key}`, String(value));
  const response = await fetch("/api/analyze", {
    method: "POST",
    body: form,
    signal,
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Invalid analysis parameters. Check thresholds, file, and ROI.",
    );
  return data;
}
