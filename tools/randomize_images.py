#!/usr/bin/env python3

from pathlib import Path
from PIL import Image
import argparse
import random
from mtgprint.images import randomize_image

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Randomize 4 pixels (the four corners) to make the image unique so it will no be deduplicated on MPC")
    parser.add_argument('images_folder',
                        help="Path to a folder containing images")

    args = parser.parse_args()

    for file in [x for x in Path(args.images_folder).iterdir() if x.is_file()]:
        print(file)
        with Image.open(file) as img:
            img = randomize_image(img)
            img.save(file)
