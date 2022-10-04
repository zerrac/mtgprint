#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

import argparse
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Cover trademarks on images in a given folder")
    parser.add_argument('images_folder',
                        help="Path to a folder containing images")

    args = parser.parse_args()

    for file in [x for x in Path(args.images_folder).iterdir() if x.is_file()]:
        if not file.name.startswith('altered-') :
            continue
        print(file)
        PILimage = Image.open(file)
        PILimage.save(file, dpi=(300,300))