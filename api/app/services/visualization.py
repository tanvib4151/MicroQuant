import base64
import io
import numpy as np
from PIL import Image, ImageDraw

def png_data(values):
    output = io.BytesIO()
    Image.fromarray(values).save(output, format="PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")

def previews(values, plane, roi, mask, opacity):
    # Fixed full-range display mapping; scientific arrays are never overwritten.
    original = (values // 257).astype(np.uint8) if values.dtype.itemsize == 2 else values
    selected = (plane // 257).astype(np.uint8) if plane.dtype.itemsize == 2 else plane
    rgb = np.repeat(original[:, :, None], 3, axis=2) if original.ndim == 2 else original.copy()
    overlay = rgb.copy()
    region = overlay[roi.y0:roi.y1, roi.x0:roi.x1]
    region[mask] = np.rint(region[mask].astype(float) * (1-opacity) + np.array([255,0,0]) * opacity).astype(np.uint8)
    image = Image.fromarray(overlay)
    ImageDraw.Draw(image).rectangle((roi.x0,roi.y0,roi.x1-1,roi.y1-1), outline=(0,255,255), width=1)
    return png_data(rgb), png_data(selected), png_data(np.array(image))
