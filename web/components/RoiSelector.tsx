import type { ROI } from "@/lib/types";
export default function RoiSelector({
  roi,
  width,
  height,
  onChange,
}: {
  roi: ROI;
  width: number;
  height: number;
  onChange: (r: ROI | null) => void;
}) {
  return (
    <section>
      <h2>Region of interest</h2>
      <p className="muted">
        Draw on the original image or edit bounds. Half-open pixels: [x0, x1) ×
        [y0, y1).
      </p>
      <div className="roi-fields">
        {(["x0", "y0", "x1", "y1"] as const).map((key) => (
          <label key={key}>
            {key}
            <input
              aria-label={`ROI ${key}`}
              type="number"
              min={0}
              max={key.startsWith("x") ? width : height}
              value={roi[key]}
              onChange={(e) =>
                onChange({ ...roi, [key]: Number(e.target.value) })
              }
            />
          </label>
        ))}
      </div>
      <p>
        {roi.x1 - roi.x0} × {roi.y1 - roi.y0} pixels
      </p>
      <button onClick={() => onChange(null)}>Reset to entire image</button>
      <small>
        Manually exclude scale bars, annotations and non-tissue regions.
      </small>
    </section>
  );
}
