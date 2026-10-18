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

def test_rgba_rejected():
    with pytest.raises(InputError):load_image(encode(np.zeros((3,4,4),np.uint8)))

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
