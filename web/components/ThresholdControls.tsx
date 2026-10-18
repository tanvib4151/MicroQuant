import type { ThresholdMethod } from "@/lib/types";
export default function ThresholdControls({
  method,
  onMethodChange,
  lower,
  upper,
  max,
  onChange,
}: {
  method: ThresholdMethod;
  onMethodChange: (method: ThresholdMethod) => void;
  lower: number;
  upper: number;
  max: number;
  onChange: (lo: number, hi: number) => void;
}) {
  return (
    <section>
      <h2>Intensity threshold</h2>
      <p className="muted">
        Inclusive raw values · 66 is a demonstration default.
      </p>
      <label>
        Threshold method
        <select
          aria-label="Threshold method"
          value={method}
          onChange={(e) => onMethodChange(e.target.value as ThresholdMethod)}
        >
          <option value="manual">Manual</option>
          <option value="otsu">Auto: Otsu (bright signal)</option>
        </select>
      </label>
      {method === "otsu" && (
        <p className="warning">
          Calculated from raw ROI intensities. Otsu separates dark and bright
          pixels; it does not identify biological staining. Uniform ROIs require
          manual thresholds.
        </p>
      )}
      <fieldset disabled={method !== "manual"}>
        <label>
          Lower threshold
          <input
            aria-label="Lower threshold"
            type="number"
            min={0}
            max={upper}
            value={lower}
            onChange={(e) => {
              if (e.target.value !== "")
                onChange(
                  Math.max(
                    0,
                    Math.min(upper, Math.round(Number(e.target.value))),
                  ),
                  upper,
                );
            }}
          />
          <input
            aria-label="Lower threshold slider"
            type="range"
            min={0}
            max={max}
            value={lower}
            onChange={(e) =>
              onChange(Math.min(Number(e.target.value), upper), upper)
            }
          />
        </label>
        <label>
          Upper threshold
          <input
            aria-label="Upper threshold"
            type="number"
            min={lower}
            max={max}
            value={upper}
            onChange={(e) => {
              if (e.target.value !== "")
                onChange(
                  lower,
                  Math.min(
                    max,
                    Math.max(lower, Math.round(Number(e.target.value))),
                  ),
                );
            }}
          />
          <input
            aria-label="Upper threshold slider"
            type="range"
            min={0}
            max={max}
            value={upper}
            onChange={(e) =>
              onChange(lower, Math.max(lower, Number(e.target.value)))
            }
          />
        </label>
      </fieldset>
    </section>
  );
}
