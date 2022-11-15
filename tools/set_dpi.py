#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

import argparse
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="save every images in a given folder in 300dpi")
    parser.add_argument('images_folder',
                        help="Path to a folder containing images")

    args = parser.parse_args()

    for file in [x for x in Path(args.images_folder).glob('*') if x.is_file()]:
        print(file)
        with Image.open(file) as img:
            img.save(file, dpi=(300,300))