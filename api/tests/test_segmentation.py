import numpy as np
import pytest
from app.services.segmentation import analyze_plane
from app.services.image_loader import InputError

@pytest.mark.parametrize("positive",[0,25,100])
def test_known_percentages(positive):
    image=np.zeros((10,10),np.uint8);image.flat[:positive]=200
    _,_,count,total,percent=analyze_plane(image,100,255,(None,)*4)
    assert (count,total,percent)==(positive,100,float(positive))

def test_inclusive():
    _,mask,count,total,percentage=analyze_plane(np.array([[65,66,100,255]],np.uint8),66,255,(None,)*4)
    assert mask.tolist()==[[False,True,True,True]]
    assert (count,total,percentage)==(3,4,75)

@pytest.mark.parametrize("lo,hi",[(-1,255),(100,99),(0,256)])
def test_invalid_threshold(lo,hi):
    with pytest.raises(InputError):analyze_plane(np.zeros((2,2),np.uint8),lo,hi,(None,)*4)
