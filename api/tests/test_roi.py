import numpy as np
import pytest
from app.services.segmentation import analyze_plane
from app.services.image_loader import InputError

def test_outside_excluded():
    a=np.full((4,4),200,np.uint8);a[1:3,1:3]=0
    assert analyze_plane(a,100,255,(1,1,3,3))[2:]==(0,4,0)

@pytest.mark.parametrize("bounds,total",[((0,0,4,4),16),((3,3,4,4),1),((0,0,1,1),1)])
def test_boundary_and_single_pixel(bounds,total):
    assert analyze_plane(np.full((4,4),200,np.uint8),100,255,bounds)[2:]==(total,total,100)

@pytest.mark.parametrize("bounds",[(0,0,0,1),(-1,0,2,2),(0,0,5,4),(3,3,2,4),(None,0,2,2)])
def test_invalid_roi(bounds):
    with pytest.raises(InputError):analyze_plane(np.zeros((4,4),np.uint8),100,255,bounds)
