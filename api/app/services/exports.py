import csv
import io

def make_csv(result):
    fields = ["filename", "marker", "channel", "width", "height", "dtype", "format", "sha256", "lower_threshold", "upper_threshold", "total_pixels", "positive_pixels", "positive_area_percent", "algorithm_version", "saturation_fraction", "preview_mapping"]
    row = {key: result[key] for key in fields}
    row.update({f"roi_{key}": value for key, value in result["roi"].items()})
    # Protect spreadsheet users from formula execution in user-controlled text.
    for key in ("filename", "marker"):
        if row[key].lstrip().startswith(("=", "+", "-", "@")):
            row[key] = "'" + row[key]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue()
