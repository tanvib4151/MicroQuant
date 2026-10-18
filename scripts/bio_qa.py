"""Synthetic biological-interpretation stress cases, not biological validation."""
import io
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'api'))
from app.main import app


def run():
    results = []
    with TestClient(app) as client:
        def measure(name, values, **parameters):
            stream = io.BytesIO()
            Image.fromarray(values).save(stream, format='PNG')
            response = client.post('/analyze', files={'image': ('synthetic.png', stream.getvalue(), 'image/png')}, data={'channel':'gray','threshold_method':'otsu', **parameters})
            response.raise_for_status()
            result = response.json()
            results.append({'case': name, **{key: result[key] for key in ('threshold_method','lower_threshold','upper_threshold','positive_pixels','total_pixels','positive_area_percent','saturation_fraction')}, 'observed_max':int(values.max())})
            return result

        # Declared no-staining simulation: intensity variation alone, not specimen data.
        background = np.tile(np.arange(10,30,dtype=np.uint8),500).reshape(100,100)
        noise = measure('background_only_uniform_intensity_distribution',background)
        assert noise['positive_area_percent'] == 50.0
        gradient = np.tile(np.arange(256,dtype=np.uint8),40).reshape(80,128)
        ramp = measure('illumination_gradient_without_staining',gradient)
        assert ramp['positive_area_percent'] == 50.0
        weak = np.array([[10]*50+[20]*50],dtype=np.uint8)
        a = measure('two_intensity_classes',weak)
        b = measure('same_image_doubled_intensities',weak*2)
        assert a['positive_area_percent'] == b['positive_area_percent'] == 50.0
        assert a['lower_threshold'] != b['lower_threshold']
        rare = np.full((10,10),10,dtype=np.uint8); rare[0,0]=200
        point = measure('one_bright_pixel',rare)
        assert point['positive_pixels'] == 1
        tissue = np.zeros((10,10),np.uint8); tissue[:5,:5]=200
        full = measure('manual_full_rectangle_with_blank_background',tissue,threshold_method='manual',lower_threshold=100,upper_threshold=255)
        crop = measure('manual_bright_region_only',tissue,threshold_method='manual',lower_threshold=100,upper_threshold=255,roi_x0=0,roi_y0=0,roi_x1=5,roi_y1=5)
        assert full['positive_pixels'] == crop['positive_pixels'] == 25
        assert (full['positive_area_percent'],crop['positive_area_percent']) == (25.0,100.0)
        sensor = np.array([[100,100,4095,4095]],np.uint16)
        clipping = measure('hypothetical_12bit_detector_clipped_values_in_uint16_container',sensor,threshold_method='manual',lower_threshold=1000,upper_threshold=65535)
        assert clipping['saturation_fraction'] == 0.0
    print(json.dumps({'scope':'Synthetic interpretation stress cases; no real controls or biological validation','results':results},indent=2))

if __name__ == '__main__':
    run()
