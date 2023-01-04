#!/usr/bin/env python3
from pathlib import Path
import argparse
import os
from PIL import Image

from mtgprint.images import Template, cover_trademark, TrademarkNotFound
import mtgprint.utils as utils

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Cover trademarks on images in a given folder")
    parser.add_argument('images_folder',
                        help="Path to a folder containing images")
    parser.add_argument('--template', type=str,
                        dest="template", default=None,
                        help='Path to the template for trademark detection')
    parser.add_argument('--notforsale', type=str,
                        dest="notforsale", default=None,
                        help='Path to the image to put over the trademark')

    args = parser.parse_args()


    if args.template:
        if not os.path.exists(args.template):
            raise BaseException("Cant find template %s" % args.template)
        else:
            templates = [Template(image_path=args.template)]
    else:
        #load default templates
        templates = [
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt2.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt3.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt4.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt5.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt6.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt7.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt8.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt9.png"),
            Template(image_path=os.path.dirname(__file__)+"/resources/trademark_alt10.png"),
        ]
    if args.notforsale:
        if not os.path.exists(args.notforsale):
            raise BaseException("Cant find 'not for sale' cover at %s" % args.notforsale)
        else:
            not_for_sale = Image.open(args.notforsale)
    else:
        not_for_sale = Image.open(os.path.dirname(__file__)+"/resources/not_for_sale.png")



    for file in [x for x in Path(args.images_folder).iterdir() if x.is_file()]:

        print(file)
        with Image.open(file) as img:
            try:
                img = cover_trademark(img, templates, not_for_sale)
            except TrademarkNotFound:
                utils.print_error("Trademark was not detected on " + str(file))
            else:
                img.save(file)