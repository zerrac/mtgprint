#!/usr/bin/env python3

from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

from skimage.io import imread
from skimage.feature import match_template
from skimage.color import rgb2gray
import cv2
import numpy as np
import argparse
import os

def read_transparent_png(filename):
    image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    alpha_channel = image_4channel[:,:,3]
    rgb_channels = image_4channel[:,:,:3]

    # White Background Image
    white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * 255

    # Alpha factor
    alpha_factor = alpha_channel[:,:,np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor,alpha_factor,alpha_factor), axis=2)

    # Transparent Image Rendered on White Background
    base = rgb_channels.astype(np.float32) * alpha_factor
    white = white_background_image.astype(np.float32) * (1 - alpha_factor)
    final_image = base + white
    return final_image.astype(np.uint8)

def detect_trademark(template, image):
    image_gray = rgb2gray(image)
    template_gray = rgb2gray(template)
    result = match_template(image_gray, template_gray)
    ij = np.unravel_index(np.argmax(result), result.shape)    
    return ij[::-1] # TRADEMARK POS


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Cover trademarks on images in a given folder")
    parser.add_argument('images_folder',
                        help="Path to a folder containing images")
    parser.add_argument('--template', type=str,
                        dest="template", default=os.path.dirname(__file__)+"/resources/tradmark.png",
                        help='Path to the template for trademark detection')
    parser.add_argument('--notforsale', type=str,
                        dest="notforsale", default=os.path.dirname(__file__)+"/resources/not_for_sale.png",
                        help='Path to the image to put over the trademark')

    args = parser.parse_args()

    if not os.path.exists(args.template):
        raise BaseException("Cant find template %s" % args.template)
    template = read_transparent_png(args.template)
    PILtemplate = Image.open(args.template)

    template_alt = read_transparent_png(os.path.dirname(__file__)+"/resources/tradmark_alt.png")
    PILtemplate_alt = Image.open(os.path.dirname(__file__)+"/resources/tradmark_alt.png")  
      
    if not os.path.exists(args.notforsale):
        raise BaseException("Cant find 'not for sale' cover at %s" % args.notforsale)
    
    not_for_sale = Image.open(args.notforsale)

    for file in [x for x in Path(args.images_folder).iterdir() if x.is_file()]:

        if file.name.startswith('altered-') :
            continue

        PILimage = Image.open(file)
  
        ## DETECT TRADEMARK POSITION
        image = read_transparent_png(str(file))
        x, y = detect_trademark(template, image)

        width, height = PILtemplate.size

        
        
        if y < (PILimage.height / 4) * 3:
            """
            Le trademark detecté n'est pas dans le quart inférieur de l'image, c'est signe d'un probème
            la detéction n'a probablement pas marché car la carte est dans un format ancien
            on essaie avec un autre template de trademark plus adapté aux cartes anciennes
            """
            x, y = detect_trademark(template_alt, image)
            width, height = PILtemplate_alt.size


        ## DETECT MEAN COLOR FOR THE ZONE TO COVER
        im_crop = PILimage.crop((x, y+height, x+width, y+height+1))
        avg_color_per_row = np.average(im_crop, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        color = tuple([int(color) for color in tuple(avg_color)[:-1]])

        #CREATE THE COVER FOR THE ZONE
        base_cache = Image.new('RGBA', not_for_sale.size, color = color)
        # ADD "not_for_sale.png"
        base_cache = Image.alpha_composite(base_cache, not_for_sale)
        
        PILimage.paste(base_cache, (x, y-1))


        dest = Path(file.parents[0], "altered-" + file.name)
        print(dest)
        PILimage.save(dest)

