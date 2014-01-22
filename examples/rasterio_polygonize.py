# Emulates GDAL's gdal_polygonize.py

import argparse
import logging
import subprocess
import sys

import fiona
import numpy as np
import rasterio
from rasterio.features import shapes


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger('rasterio_polygonize')


def main(raster_file, vector_file, driver):
    
    with rasterio.drivers():
        
        with rasterio.open(raster_file) as src:
            image = src.read_band(1)
        
        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) 
            in enumerate(shapes(image, transform=src.transform)))

        with fiona.open(
                vector_file, 'w', 
                driver=driver,
                crs=src.crs,
                schema={'properties': [('raster_val', 'int')],
                        'geometry': 'Polygon'}) as dst:
            dst.writerecords(results)
    
    return dst.name

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Writes shapes of raster features to a vector file")
    parser.add_argument(
        'input', 
        metavar='INPUT', 
        help="Input file name")
    parser.add_argument(
        'output', 
        metavar='OUTPUT',
        help="Output file name")
    parser.add_argument(
        '--output-driver',
        metavar='OUTPUT DRIVER',
        help="Output vector driver name")
    args = parser.parse_args()

    name = main(args.input, args.output, args.output_driver)
    
    print subprocess.check_output(
            ['ogrinfo', '-so', args.output, name])
