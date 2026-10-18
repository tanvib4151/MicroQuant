import numpy as np
from ..models import ROI
from .image_loader import InputError

def validate_roi(shape, bounds):
    height, width = shape
    if all(v is None for v in bounds):
        bounds = (0, 0, width, height)
    if any(v is None for v in bounds):
        raise InputError("Supply all four ROI bounds or omit all of them.")
    x0, y0, x1, y1 = bounds
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise InputError("ROI must be a nonempty half-open rectangle within the image.")
    return ROI(x0=x0, y0=y0, x1=x1, y1=y1)

def analyze_plane(plane, lower, upper, bounds):
    rectangle = validate_roi(plane.shape, bounds)
    x0, y0, x1, y1 = rectangle.x0, rectangle.y0, rectangle.x1, rectangle.y1
    maximum = np.iinfo(plane.dtype).max
    if not 0 <= lower <= upper <= maximum:
        raise InputError(f"Thresholds must satisfy 0 ≤ lower ≤ upper ≤ {maximum}.")
    roi = plane[y0:y1, x0:x1]
    mask = (roi >= lower) & (roi <= upper)
    count = int(np.count_nonzero(mask))
    return rectangle, mask, count, roi.size, 100.0 * count / roi.size
