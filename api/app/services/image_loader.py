import io
import os
import warnings
from dataclasses import dataclass
import numpy as np
from PIL import Image
import tifffile

class InputError(ValueError):
    def __init__(self, message, status=422):
        super().__init__(message)
        self.status = status

@dataclass
class LoadedImage:
    values: np.ndarray
    format: str


def load_image(data: bytes) -> LoadedImage:
    max_pixels = int(os.getenv("MAX_DECODED_PIXELS", "4000000"))
    if not data:
        raise InputError("The uploaded file is empty.")
    if len(data) > int(os.getenv("MAX_UPLOAD_BYTES", "20971520")):
        raise InputError("Upload exceeds the configured byte limit.", 413)
    try:
        if data[:4] in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
            with tifffile.TiffFile(io.BytesIO(data)) as tif:
                if len(tif.pages) != 1 or len(tif.series) != 1:
                    raise InputError("Only single-frame TIFF images are supported; stacks are rejected.")
                page = tif.pages[0]
                if page.imagewidth * page.imagelength > max_pixels:
                    raise InputError("Decoded image exceeds the configured pixel limit.", 413)
                if page.tags.get("Orientation") and page.tags["Orientation"].value != 1:
                    raise InputError("TIFF orientation must be top-left (1). Export an explicitly oriented image first.")
                if page.imagedepth != 1 or page.shape not in ((page.imagelength, page.imagewidth), (page.imagelength, page.imagewidth, 3)):
                    raise InputError("TIFF must have exactly two spatial axes with optional contiguous RGB samples.")
                if page.bitspersample != page.dtype.itemsize * 8:
                    raise InputError("TIFF samples must be full unsigned 8-bit or 16-bit values.")
                rgb = page.photometric == 2
                gray = page.photometric == 1
                if not ((rgb and page.samplesperpixel == 3 and page.planarconfig == 1 and page.dtype == np.dtype('uint8')) or (gray and page.samplesperpixel == 1 and page.dtype.kind == 'u' and page.dtype.itemsize in (1, 2))):
                    raise InputError("Supported TIFF: unsigned 8/16-bit MINISBLACK grayscale or contiguous 8-bit RGB, without alpha or extra axes.")
                arr = page.asarray()
                fmt = "TIFF"
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(data)) as image:
                    fmt = image.format
                    if fmt not in ("PNG", "JPEG"):
                        raise InputError("Supported formats are PNG, JPEG and TIFF.")
                    if getattr(image, "n_frames", 1) != 1:
                        raise InputError("Animated or multi-frame images are unsupported.")
                    if image.width * image.height > max_pixels:
                        raise InputError("Decoded image exceeds the configured pixel limit.", 413)
                    if image.getexif().get(274, 1) != 1:
                        raise InputError("Non-default image orientation is unsupported; export a top-left oriented image first.")
                    if image.mode == "RGBA":
                        if image.getchannel("A").getextrema() != (255, 255):
                            raise InputError("This PNG contains transparent or partially transparent pixels. Export an opaque image from the original source; NeuroQuant does not composite transparency or infer the hidden background.")
                        # Every pixel is opaque: drop only alpha, preserving RGB exactly.
                        arr = np.array(image)[:, :, :3].copy()
                    elif image.mode in ("L", "RGB", "I;16", "I;16B", "I;16L"):
                        arr = np.array(image)
                    else:
                        raise InputError("Use 8-bit grayscale, unsigned 16-bit grayscale, RGB, or fully opaque RGBA PNG. Palette and other pixel formats are not supported.")
        if arr.ndim == 2 and arr.dtype.kind == 'u' and arr.dtype.itemsize in (1, 2):
            arr = arr.astype(np.uint16 if arr.dtype.itemsize == 2 else np.uint8, copy=False)
        elif not (arr.ndim == 3 and arr.shape[2] == 3 and arr.dtype == np.uint8):
            raise InputError("Unsupported pixel datatype or channel arrangement.")
        if not arr.size:
            raise InputError("Image has no pixels.")
        return LoadedImage(arr, fmt)
    except InputError:
        raise
    except Exception:
        raise InputError("Cannot decode this image. It may be corrupt or use an unsupported compression.") from None
