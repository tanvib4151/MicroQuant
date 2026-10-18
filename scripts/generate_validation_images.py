"""Generate lossless reference inputs; no Fiji comparison is implied."""
import argparse
import json
from pathlib import Path
import numpy as np
import tifffile
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('output', type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
a = np.zeros((10, 10), dtype=np.uint8)
a[:5, :5] = 200
Image.fromarray(a).save(args.output / 'gray8.png')
rgb = np.zeros((10, 10, 3), dtype=np.uint8)
rgb[:, :, 0] = 200
rgb[:, :, 1] = a
Image.fromarray(rgb).save(args.output / 'rgb8.png')
a16 = np.zeros((10, 10), dtype=np.uint16)
a16[:5, :5] = 1000
a16[0, 0] = 65535
tifffile.imwrite(args.output / 'gray16.tif', a16, photometric='minisblack')
settings = []
for name, channel, lower, upper in [('gray8.png', 'gray', 100, 255), ('rgb8.png', 'green', 100, 255), ('gray16.tif', 'gray', 1000, 65535)]:
    settings.append(dict(filename=name, channel=channel, lower_threshold=lower, upper_threshold=upper, roi=dict(x0=0,y0=0,x1=10,y1=10), expected_positive_pixels=25, expected_total_pixels=100, expected_positive_area_percent=25.0))
(args.output / 'expected.json').write_text(json.dumps(settings, indent=2) + '\n')
print(f'Created three synthetic reference images and expected.json in {args.output}')
