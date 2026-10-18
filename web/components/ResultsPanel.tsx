import type { Result } from "@/lib/types";
export default function ResultsPanel({ result }: { result: Result }) {
  return (
    <section aria-label="Analysis results">
      <h2>Positive staining area</h2>
      <div className="percentage" data-testid="positive-area">
        {result.positive_area_percent.toFixed(3)}
        <span>%</span>
      </div>
      <dl>
        <dt>Marker</dt>
        <dd>{result.marker || "Not specified"}</dd>
        <dt>Channel</dt>
        <dd>{result.channel}</dd>
        <dt>Threshold</dt>
        <dd>
          {result.lower_threshold}–{result.upper_threshold}
        </dd>
        <dt>Positive pixels</dt>
        <dd>{result.positive_pixels.toLocaleString()}</dd>
        <dt>ROI pixels</dt>
        <dd>{result.total_pixels.toLocaleString()}</dd>
        <dt>Saturated pixels</dt>
        <dd>{(100 * result.saturation_fraction).toFixed(3)}%</dd>
      </dl>
      {result.warnings.map((note) => (
        <p className="warning" key={note}>
          {note}
        </p>
      ))}
    </section>
  );
}
