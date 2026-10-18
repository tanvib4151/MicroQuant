import hashlib
import os
from typing import Literal
from fastapi import APIRouter, UploadFile, File, Form
from ..models import AnalysisResult
from ..services.image_loader import load_image, InputError
from ..services.fluorescence import extract_channel, channels_for
from ..services.segmentation import analyze_plane, validate_roi
from ..services.thresholding import otsu_threshold
from ..services.quality_control import quality_control
from ..services.visualization import previews
from ..services.exports import make_csv

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
def analyze(image: UploadFile = File(...), channel: str = Form("auto"), marker: str = Form("", max_length=200), lower_threshold: int = Form(66), upper_threshold: int = Form(255), roi_x0: int | None = Form(None), roi_y0: int | None = Form(None), roi_x1: int | None = Form(None), roi_y1: int | None = Form(None), overlay_opacity: float = Form(0.45, ge=0, le=1), threshold_method: Literal["manual", "otsu"] = Form("manual")):
    limit = int(os.getenv("MAX_UPLOAD_BYTES", "20971520"))
    data = image.file.read(limit + 1)
    if len(data) > limit:
        raise InputError("Upload exceeds the configured byte limit.", 413)
    loaded = load_image(data)
    values = loaded.values
    plane, selected = extract_channel(values, channel)
    bounds = (roi_x0, roi_y0, roi_x1, roi_y1)
    if threshold_method == "otsu":
        rectangle = validate_roi(plane.shape, bounds)
        lower_threshold, upper_threshold = otsu_threshold(plane[rectangle.y0:rectangle.y1, rectangle.x0:rectangle.x1])
    roi, mask, positive, total, percentage = analyze_plane(plane, lower_threshold, upper_threshold, (roi_x0, roi_y0, roi_x1, roi_y1))
    saturation, notes = quality_control(plane, roi, positive, total)
    if threshold_method == "otsu":
        notes.append("Otsu automatically separates darker and brighter ROI intensities; bright pixels are treated as positive. This is not a validated biological threshold. Each channel or ROI change recomputes it; per-image thresholds do not establish comparability between samples.")
    original, channel_preview, overlay = previews(values, plane, roi, mask, overlay_opacity)
    result = AnalysisResult(filename=(image.filename or "image").replace("\\", "/").split("/")[-1][:255], marker=marker, channel=selected, width=values.shape[1], height=values.shape[0], dtype=str(values.dtype), channels=channels_for(values), format=loaded.format, sha256=hashlib.sha256(data).hexdigest(), roi=roi, threshold_method=threshold_method, lower_threshold=lower_threshold, upper_threshold=upper_threshold, positive_pixels=positive, total_pixels=total, positive_area_percent=percentage, saturation_fraction=saturation, warnings=notes, preview_mapping="uint16: floor(value/257); uint8: identity; stored pixel orientation", original_png=original, channel_png=channel_preview, overlay_png=overlay, csv="")
    result.csv = make_csv(result.model_dump())
    return result
