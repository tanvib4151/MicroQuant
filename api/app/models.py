from typing import Literal
from pydantic import BaseModel

ALGORITHM_VERSION = "positive-area/1.1.0"

class ROI(BaseModel):
    x0: int
    y0: int
    x1: int
    y1: int

class AnalysisResult(BaseModel):
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
    saturation_fraction: float
    warnings: list[str]
    algorithm_version: str = ALGORITHM_VERSION
    preview_mapping: str
    original_png: str
    channel_png: str
    overlay_png: str
    csv: str
