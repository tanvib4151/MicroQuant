import csv
import io
import numpy as np
import pytest
from app.services.thresholding import otsu_threshold
from app.services.image_loader import InputError
from conftest import request_analysis


@pytest.mark.parametrize('values,expected', [
    (np.array([[0, 0, 200, 200]], np.uint8), (1, 255)),
    (np.array([[1000, 1000, 60000, 60000]], np.uint16), (1001, 65535)),
    (np.array([[0, 1, 2]], np.uint8), (1, 255)),
])
def test_known_splits_and_earliest_tie(values, expected):
    assert otsu_threshold(values) == expected


@pytest.mark.parametrize('dtype', [np.uint8, np.uint16])
def test_matches_independent_partition_calculation(dtype):
    rng = np.random.default_rng(7)
    values = rng.integers(0, np.iinfo(dtype).max + 1, size=(4, 5), dtype=dtype)
    candidates = np.unique(values)[:-1]
    scores = []
    for cutoff in candidates:
        dark, bright = values[values <= cutoff], values[values > cutoff]
        scores.append(dark.size * bright.size * (float(dark.mean()) - float(bright.mean())) ** 2)
    expected = int(candidates[int(np.argmax(scores))]) + 1
    assert otsu_threshold(values)[0] == expected
    assert otsu_threshold(values) == otsu_threshold(values.copy())


@pytest.mark.parametrize('value,dtype', [(0,np.uint8),(255,np.uint8),(65535,np.uint16)])
def test_uniform_rois_require_manual(value, dtype):
    with pytest.raises(InputError, match='at least two distinct'):
        otsu_threshold(np.full((2,2),value,dtype))


def test_auto_uses_roi_exports_method_and_retains_inclusive_measurement(client):
    values = np.array([[0, 10, 100, 100]], dtype=np.uint8)
    full = request_analysis(client, values, threshold_method='otsu').json()
    response = request_analysis(client, values, threshold_method='otsu', roi_x0=0,roi_y0=0,roi_x1=2,roi_y1=1)
    assert response.status_code == 200
    result = response.json()
    assert full['lower_threshold'] == 11
    assert result['lower_threshold'] == 1
    assert result['upper_threshold'] == 255
    assert (result['positive_pixels'], result['total_pixels'],result['positive_area_percent']) == (1,2,50.0)
    assert result['threshold_method'] == 'otsu'
    assert result['algorithm_version'] == 'positive-area/1.1.0'
    exported = next(csv.DictReader(io.StringIO(result['csv'])))
    assert exported['threshold_method'] == 'otsu'
    assert exported['lower_threshold'] == '1'
    assert any('not a validated biological threshold' in note for note in result['warnings'])


def test_auto_uint16_uses_full_raw_histogram(client):
    values = np.array([[1000,1000,60000,60000]],np.uint16)
    result = request_analysis(client,values,threshold_method='otsu', lower_threshold=0,upper_threshold=0).json()
    assert (result['lower_threshold'],result['upper_threshold'],result['positive_pixels']) == (1001,65535,2)


@pytest.mark.parametrize('params', [dict(threshold_method='unknown'),dict(threshold_method='otsu',roi_x0=0,roi_y0=0,roi_x1=0,roi_y1=1),dict(threshold_method='otsu',roi_x0=0,roi_y0=0,roi_x1=1,roi_y1=1)])
def test_invalid_auto_settings(client,params):
    assert request_analysis(client,np.array([[0,200]],np.uint8),**params).status_code==422


def test_manual_remains_default(client):
    result = request_analysis(client,np.array([[65,66,255]],np.uint8),lower_threshold=66).json()
    assert result['threshold_method']=='manual'
    assert result['positive_pixels']==2
