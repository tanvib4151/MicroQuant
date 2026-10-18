from typing import Literal
from pydantic import BaseModel, Field

ImageSource = Literal["unspecified", "laboratory", "synthetic", "published"]
MEASUREMENT_DEFINITION = "100 × threshold-positive pixels / all pixels in the selected rectangular ROI; no tissue mask is inferred."
SATURATION_DEFINITION = "Fraction at the datatype maximum (255 or 65535), not an instrument saturation measurement. Zero does not exclude detector clipping."
INTERPRETATION_NOTES = [
    "Threshold-positive ROI area does not establish specific biological staining, cell number, protein abundance or activation.",
    "Biological validation and direct Fiji equivalence are pending; inspect controls and overlays before interpretation.",
    "ROI pixels include any background, tissue holes, annotations or scale bars within the rectangle. Use consistent predefined sampling rules.",
    "Per-image thresholds do not establish comparability across samples; acquisition and analysis protocols require justification.",
]
ALGORITHM_VERSION = "positive-area/1.1.0"

class ROI(BaseModel):
    x0: int
    y0: int
    x1: int
    y1: int

class AnalysisResult(BaseModel):
    export_schema_version: str = "1.1.0"
    image_source: ImageSource
    sample_id: str
    acquisition_notes: str
    control_reference: str
    measurement_definition: str = MEASUREMENT_DEFINITION
    saturation_definition: str = SATURATION_DEFINITION
    interpretation_notes: list[str]
    filename: str
    marker: str
    channel: str
    width: int
    height: int
    dtype: str
    channels: list[str]
    format: str
    sha256: str
    roi: ROI
    threshold_method: Literal["manual", "otsu"]
    lower_threshold: int
    upper_threshold: int
    positive_pixels: int
    total_pixels: int
    positive_area_percent: float
    datatype_max_fraction: float
    saturation_fraction: float = Field(description="Legacy alias of datatype_max_fraction; not detector saturation", deprecated=True)
    warnings: list[str]
    algorithm_version: str = ALGORITHM_VERSION
    preview_mapping: str
    original_png: str
    channel_png: str
    overlay_png: str
    csv: str
