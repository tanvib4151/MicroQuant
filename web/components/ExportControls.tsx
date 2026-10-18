import type { Result } from "@/lib/types";
function download(value: string, type: string, name: string) {
  const url = URL.createObjectURL(new Blob([value], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export default function ExportControls({
  result,
  opacity,
}: {
  result: Result;
  opacity: number;
}) {
  return (
    <section>
      <h2>Export this analysis</h2>
      <div className="exports">
        <button
          onClick={() =>
            download(
              result.csv,
              "text/csv;charset=utf-8",
              "neuroquant-results.csv",
            )
          }
        >
          Results CSV
        </button>
        <button
          onClick={() => {
            const { original_png, channel_png, overlay_png, csv, ...settings } =
              result;
            void original_png;
            void channel_png;
            void overlay_png;
            void csv;
            download(
              JSON.stringify(
                { ...settings, overlay_opacity: opacity },
                null,
                2,
              ),
              "application/json",
              "neuroquant-settings.json",
            );
          }}
        >
          Settings JSON
        </button>
        <a
          className="button"
          href={result.overlay_png}
          download="neuroquant-overlay.png"
        >
          Overlay PNG
        </a>
      </div>
    </section>
  );
}
