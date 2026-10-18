import csv
import json
import io

def make_csv(result):
    fields = ["export_schema_version", "image_source", "sample_id", "acquisition_notes", "control_reference", "measurement_definition", "saturation_definition", "datatype_max_fraction", "filename", "marker", "channel", "width", "height", "dtype", "format", "sha256", "threshold_method", "lower_threshold", "upper_threshold", "total_pixels", "positive_pixels", "positive_area_percent", "algorithm_version", "saturation_fraction", "preview_mapping"]
    row = {key: result[key] for key in fields}
    row["warnings"] = json.dumps(result["warnings"], ensure_ascii=False)
    row["interpretation_notes"] = json.dumps(result["interpretation_notes"], ensure_ascii=False)
    row.update({f"roi_{key}": value for key, value in result["roi"].items()})
    # Protect spreadsheet users from formula execution in user-controlled text.
    for key in ("filename", "marker", "sample_id", "acquisition_notes", "control_reference"):
        if row[key].lstrip().startswith(("=", "+", "-", "@")):
            row[key] = "'" + row[key]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(row))
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue()
