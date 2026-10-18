export default function ThresholdControls({
  lower,
  upper,
  max,
  onChange,
}: {
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
    </section>
  );
}
