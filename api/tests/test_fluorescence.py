import numpy as np
from conftest import request_analysis

def test_rgb_isolation(client):
    a=np.zeros((2,2,3),np.uint8);a[:,:,0]=200;a[0,0,1]=200
    for channel,expected in [("red",4),("green",1),("blue",0)]:
        r=request_analysis(client,a,channel=channel).json()
        assert r["positive_pixels"]==expected

def test_16bit_integrity(client):
    a=np.array([[0,256,1000,65535]],np.uint16)
    for fmt in ["PNG","TIFF"]:
        r=request_analysis(client,a,fmt=fmt,lower_threshold=1000,upper_threshold=65535)
        assert r.status_code==200,r.text
        assert r.json()["dtype"]=="uint16"
        assert r.json()["positive_pixels"]==2
        assert r.json()["saturation_fraction"]==.25
