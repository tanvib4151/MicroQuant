"""Deterministic histogram threshold selection on raw ROI intensities."""
import numpy as np
from .image_loader import InputError


def otsu_threshold(values):
    """Return inclusive bright-class bounds; use the earliest maximizing split.

    No bin reduction: uint8 uses 256 bins and uint16 uses 65536 bins.
    A split t separates [0,t] from [t+1,max], so lower is t+1.
    """
    maximum = int(np.iinfo(values.dtype).max)
    counts = np.bincount(values.ravel(), minlength=maximum + 1).astype(np.float64)
    if np.count_nonzero(counts) < 2:
        raise InputError("Otsu needs at least two distinct intensities inside the ROI. Switch to Manual thresholds for a uniform or one-pixel region.")
    weights = np.cumsum(counts)[:-1]
    sums = np.cumsum(counts * np.arange(maximum + 1, dtype=np.float64))
    total = float(values.size)
    other_weights = total - weights
    valid = (weights > 0) & (other_weights > 0)
    score = np.full(maximum, -np.inf)
    # Equivalent to w0*w1*(mean0-mean1)^2, up to a constant.
    score[valid] = (sums[-1] * weights[valid] - sums[:-1][valid] * total) ** 2 / (weights[valid] * other_weights[valid])
    split = int(np.argmax(score))
    return split + 1, maximum
