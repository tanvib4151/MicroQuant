import io
import numpy as np
import pytest
from PIL import Image
import tifffile
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def encode(values, fmt="PNG", **kwargs):
    out=io.BytesIO()
    if fmt=="TIFF": tifffile.imwrite(out, values, **kwargs)
    else: Image.fromarray(values).save(out, format=fmt)
    return out.getvalue()

def request_analysis(client, values, fmt="PNG", **params):
    return client.post("/analyze",files={"image":("synthetic.dat",encode(values,fmt),"application/octet-stream")},data={"channel":"gray","lower_threshold":100,"upper_threshold":255,**params})
