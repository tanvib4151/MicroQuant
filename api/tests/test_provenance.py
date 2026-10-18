import csv
import io
import json
import numpy as np
import pytest
from conftest import request_analysis


def test_published_provenance_and_qc_survive_csv_and_json(client):
    values = np.array([[0, 255]], dtype=np.uint8)
    response = request_analysis(client, values, image_source='published', sample_id='sample-1', acquisition_notes='Exposure 30 ms, gain 2\nUnprocessed original', control_reference='negative-01', threshold_method='otsu')
    assert response.status_code == 200
    result = response.json()
    row = next(csv.DictReader(io.StringIO(result['csv'])))
    for key, expected in [('image_source','published'),('sample_id','sample-1'),('acquisition_notes','Exposure 30 ms, gain 2\nUnprocessed original'),('control_reference','negative-01')]:
        assert result[key] == row[key] == expected
    assert result['export_schema_version'] == row['export_schema_version'] == '1.1.0'
    assert json.loads(row['warnings']) == result['warnings']
    assert json.loads(row['interpretation_notes']) == result['interpretation_notes']
    assert any('Published-figure' in note for note in result['warnings'])
    assert any('not a validated biological threshold' in note for note in result['warnings'])
    assert 'not an instrument saturation measurement' in row['saturation_definition']
    assert 'no tissue mask' in row['measurement_definition']
    assert result['datatype_max_fraction'] == result['saturation_fraction'] == .5
    assert float(row['datatype_max_fraction']) == .5


def test_old_clients_default_to_unspecified_provenance(client):
    result = request_analysis(client, np.array([[0,200]],np.uint8)).json()
    assert result['image_source'] == 'unspecified'
    assert result['sample_id'] == result['acquisition_notes'] == result['control_reference'] == ''
    assert any('source is unspecified' in note for note in result['warnings'])


@pytest.mark.parametrize('params', [dict(image_source='invalid'),dict(sample_id='x'*201),dict(acquisition_notes='x'*2001),dict(control_reference='x'*501)])
def test_provenance_validation(client, params):
    assert request_analysis(client,np.zeros((2,2),np.uint8),**params).status_code == 422


@pytest.mark.parametrize('source', ['unspecified','laboratory','synthetic','published'])
def test_provenance_never_changes_scientific_measurements(client,source):
    values = np.array([[0,1000,4095,65535]],np.uint16)
    baseline = request_analysis(client,values,lower_threshold=1000,upper_threshold=65535).json()
    changed = request_analysis(client,values,lower_threshold=1000,upper_threshold=65535,image_source=source,sample_id='notes only',acquisition_notes='a',control_reference='b').json()
    for key in ('positive_pixels','total_pixels','positive_area_percent','datatype_max_fraction','sha256','original_png','channel_png','overlay_png','lower_threshold','upper_threshold'):
        assert changed[key] == baseline[key]


def test_uint16_ceiling_is_not_inferred_detector_clipping(client):
    values = np.array([[0,4095]], np.uint16)
    result = request_analysis(client,values,lower_threshold=1000,upper_threshold=65535).json()
    assert result['datatype_max_fraction'] == 0
    assert 'Zero does not exclude detector clipping' in result['saturation_definition']


@pytest.mark.parametrize('field', ['sample_id','acquisition_notes','control_reference'])
def test_csv_escapes_new_user_text_without_changing_json(client,field):
    result = request_analysis(client,np.array([[0,200]],np.uint8),**{field:'=1+1'}).json()
    row = next(csv.DictReader(io.StringIO(result['csv'])))
    assert result[field] == '=1+1'
    assert row[field] == "'=1+1"
