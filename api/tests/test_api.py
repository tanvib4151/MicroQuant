import base64
import csv
import io
import hashlib
import numpy as np
import pytest
from PIL import Image
from conftest import encode, request_analysis

def test_health(client):assert client.get("/health").json()=={"status":"ok"}

def test_exports_and_determinism(client):
    a=np.zeros((10,10),np.uint8);a[:5,:5]=200
    first=request_analysis(client,a,marker="Iba1").json()
    second=request_analysis(client,a,marker="Iba1").json()
    assert first==second
    assert first["sha256"]==hashlib.sha256(encode(a)).hexdigest()
    row=next(csv.DictReader(io.StringIO(first["csv"])))
    for key in ["positive_pixels","total_pixels","positive_area_percent","lower_threshold","upper_threshold"]:
        assert float(row[key])==first[key]
    assert first["roi"]=={"x0":0,"y0":0,"x1":10,"y1":10}
    for key in ["original_png","channel_png","overlay_png"]:
        im=Image.open(io.BytesIO(base64.b64decode(first[key].split(",")[1])))
        assert im.size==(10,10)
    other=request_analysis(client,a,overlay_opacity=0).json()
    assert other["positive_area_percent"]==first["positive_area_percent"]
    assert other["overlay_png"]!=first["overlay_png"]

@pytest.mark.parametrize("params",[{"channel":"red"},{"lower_threshold":300},{"lower_threshold":"x"},{"lower_threshold":200,"upper_threshold":100},{"roi_x0":0},{"roi_x0":0,"roi_y0":0,"roi_x1":0,"roi_y1":1},{"overlay_opacity":"nan"}])
def test_invalid_parameters(client,params):
    assert request_analysis(client,np.zeros((2,2),np.uint8),**params).status_code==422

def test_missing_file(client):assert client.post("/analyze").status_code==422

def test_byte_limit(client,monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_BYTES","10")
    assert request_analysis(client,np.zeros((2,2),np.uint8)).status_code==413

def test_bad_file(client):
    r=client.post("/analyze",files={"image":("image.png",b"not an image","image/png")})
    assert r.status_code==422
    assert "Traceback" not in r.text

def test_spreadsheet_formula_escaped(client):
    r=request_analysis(client,np.zeros((2,2),np.uint8),marker="=1+1").json()
    assert next(csv.DictReader(io.StringIO(r['csv'])))['marker']=="'=1+1"
    assert r['marker']=='=1+1'


def test_total_multipart_limit_before_decode(client, monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    response = client.post("/analyze", content=b"x" * 70000, headers={"content-type": "multipart/form-data; boundary=test"})
    assert response.status_code == 413
