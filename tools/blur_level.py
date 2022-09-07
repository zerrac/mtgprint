import cv2
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from mtgprint.images import _variance_of_laplacian


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="print computed blur level for a given image.")
    parser.add_argument('image_path',
                        help="Path to an image")


    args = parser.parse_args()
    image = cv2.imread(args.image_path)


    print("Estimated blur level : %s" % _variance_of_laplacian(image))
