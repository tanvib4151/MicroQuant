import numpy as np

def quality_control(plane, roi, positive, total):
    values = plane[roi.y0:roi.y1, roi.x0:roi.x1]
    fraction = float(np.count_nonzero(values == np.iinfo(plane.dtype).max) / total)
    notes = []
    if fraction > 0:
        notes.append(f"{100*fraction:.3f}% of ROI pixels are at maximum representable intensity. Review saturation; no universal cutoff is assumed.")
    if positive == total:
        notes.append("The threshold includes the entire ROI. Review the selected range.")
    if positive == 0:
        notes.append("No pixels meet this threshold. This does not establish absence of biological staining.")
    return fraction, notes
