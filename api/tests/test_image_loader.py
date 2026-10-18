import io
import numpy as np
import pytest
import tifffile
from PIL import Image
from conftest import encode
from app.services.image_loader import load_image, InputError

@pytest.mark.parametrize("fmt",["PNG","JPEG","TIFF"])
def test_formats(fmt):
    loaded=load_image(encode(np.zeros((3,4,3),np.uint8),fmt))
    assert loaded.values.shape==(3,4,3)
    assert loaded.format==fmt

@pytest.mark.parametrize("data",[b"",b"broken",b"GIF89a"])
def test_corrupt(data):
    with pytest.raises(InputError):load_image(data)

@pytest.mark.parametrize("array",[np.zeros((2,3,4),np.uint8),np.zeros((3,4),np.float32),np.zeros((3,4),np.int16)])
def test_unsupported_tiff(array):
    with pytest.raises(InputError):load_image(encode(array,"TIFF"))

@pytest.mark.parametrize("alpha", [0, 128, 254])
def test_transparent_rgba_rejected(alpha):
    values = np.full((3, 4, 4), 255, np.uint8)
    values[0, 0, 3] = alpha
    with pytest.raises(InputError, match="transparent"):
        load_image(encode(values))


def test_opaque_rgba_preserves_rgb_exactly():
    values = np.arange(48, dtype=np.uint8).reshape(3, 4, 4)
    values[:, :, 3] = 255
    original = values.copy()
    loaded = load_image(encode(values))
    np.testing.assert_array_equal(loaded.values, original[:, :, :3])
    assert loaded.values.dtype == np.uint8
    assert loaded.format == "PNG"

def test_decoded_limit(monkeypatch):
    monkeypatch.setenv("MAX_DECODED_PIXELS","10")
    with pytest.raises(InputError) as exc:load_image(encode(np.zeros((4,4),np.uint8)))
    assert exc.value.status==413

def test_big_endian_uint16():
    a=np.array([[0,1000,65535]],dtype=">u2")
    assert load_image(encode(a,"TIFF")).values.tolist()==a.tolist()

def test_tiff_orientation():
    out=io.BytesIO();tifffile.imwrite(out,np.zeros((3,4),np.uint8),extratags=[(274,'H',1,3,False)])
    with pytest.raises(InputError,match="orientation"):load_image(out.getvalue())
