import shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import cv2
import random
import numpy as np

DEFAULT_TEMPLATE_MATCHING_THRESHOLD = 0.4
NMS_THRESHOLD = 0.2

def _pascal_row(n, memo={}):
    # This returns the nth row of Pascal's Triangle
    if n in memo:
        return memo[n]
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n//2+1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n&1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    memo[n] = result
    return result


def _make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = _pascal_row(n-1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier


def _compute_iou(boxA, boxB):
    xA = max(boxA["TOP_LEFT_X"], boxB["TOP_LEFT_X"])
    yA = max(boxA["TOP_LEFT_Y"], boxB["TOP_LEFT_Y"])
    xB = min(boxA["BOTTOM_RIGHT_X"], boxB["BOTTOM_RIGHT_X"])
    yB = min(boxA["BOTTOM_RIGHT_Y"], boxB["BOTTOM_RIGHT_Y"])
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    boxAArea = (boxA["BOTTOM_RIGHT_X"] - boxA["TOP_LEFT_X"] + 1)*(boxA["BOTTOM_RIGHT_Y"] - boxA["TOP_LEFT_Y"] + 1)
    boxBArea = (boxB["BOTTOM_RIGHT_X"] - boxB["TOP_LEFT_X"] + 1)*(boxB["BOTTOM_RIGHT_Y"] - boxB["TOP_LEFT_Y"] + 1)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def _non_max_suppression(objects, non_max_suppression_threshold=0.5, score_key="MATCH_VALUE"):
    """
    Filter objects overlapping with IoU over threshold by keeping only the one with maximum score.
    Args:
        objects (List[dict]): a list of objects dictionaries, with:
            {score_key} (float): the object score
            {top_left_x} (float): the top-left x-axis coordinate of the object bounding box
            {top_left_y} (float): the top-left y-axis coordinate of the object bounding box
            {bottom_right_x} (float): the bottom-right x-axis coordinate of the object bounding box
            {bottom_right_y} (float): the bottom-right y-axis coordinate of the object bounding box
        non_max_suppression_threshold (float): the minimum IoU value used to filter overlapping boxes when
            conducting non max suppression.
        score_key (str): score key in objects dicts
    Returns:
        List[dict]: the filtered list of dictionaries.
    """
    sorted_objects = sorted(objects, key=lambda obj: obj[score_key], reverse=True)
    filtered_objects = []
    for object_ in sorted_objects:
        overlap_found = False
        for filtered_object in filtered_objects:
            iou = _compute_iou(object_, filtered_object)
            if iou > non_max_suppression_threshold:
                overlap_found = True
                break
        if not overlap_found:
            filtered_objects.append(object_)
    return filtered_objects

class Template:
    """
    A class defining a template
    """
    def __init__(self, image_path, matching_threshold=DEFAULT_TEMPLATE_MATCHING_THRESHOLD):
        """
        Args:
            image_path (str): path of the template image path
            matching_threshold (float): the minimum similarity score to consider an object is detected by template
                matching
        """
        self.image_path = image_path
        self.template = cv2.imread(image_path)
        self.template_height, self.template_width = self.template.shape[:2]
        self.matching_threshold = matching_threshold


   
def add_borders(img, border_width = 36):
    """
    - Add a border of {border_widh} pixel to image.
    - The color of added the border is picked from the pixel of the border of the source image
    """
    x,y = img.size
    pix = img.load()
    
    color = pix[x/2,y-1] # Couleur du pixel en bas au milieu de l'image 
    
    # cammouflage des coins en trensparence
    margin = 40
    curve_modifier = 4
    draw = ImageDraw.Draw(img)
    ts = [t/100.0 for t in range(101)]
    
    haut_gauche = [(0, margin), (curve_modifier, curve_modifier), (margin, 0)]
    bezier = _make_bezier(haut_gauche)
    points = bezier(ts)
    points.append((0.0,0.0))
    draw.polygon(points, fill = color)
    
    haut_droite = [(x-margin, 0), (x-curve_modifier,curve_modifier), (x, margin)]
    bezier = _make_bezier(haut_droite)
    points = bezier(ts)
    points.append((x,0.0))
    draw.polygon(points, fill = color)
    
    bas_gauche = [(0, y-margin), (curve_modifier,y-curve_modifier), (margin, y)]
    bezier = _make_bezier(bas_gauche)
    points = bezier(ts)
    points.append((0.0,y))
    draw.polygon(points, fill = color)
    
    bas_droite = [(x-margin, y), (x-curve_modifier,y-curve_modifier), (x, y-margin)]
    bezier = _make_bezier(bas_droite)
    points = bezier(ts)
    points.append((x,y))
    draw.polygon(points, fill = color)
    
    
    # Ajout de la bordure
    img_with_border = ImageOps.expand(
        img,
        border=border_width,
        fill=color
    )
    return img_with_border


def randomize_image(PILimage):
    """
        Make 4 pixels of the image (the 4 corners) random color. This way they wont be regrouped on MPC.
    """
    x,y = PILimage.size
    PILimage.putpixel((0, y-1), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.putpixel((0, 0), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.putpixel((x-1, 0), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.putpixel((x-1, y-1), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    return PILimage

class TrademarkNotFound(Exception):
    pass


def cover_trademark(PILimage, templates, cover):
    image = cv2.cvtColor(np.array(PILimage), cv2.COLOR_RGB2BGR)

    detections = []
    for template in templates:
        template_matching = cv2.matchTemplate(
            template.template, image, cv2.TM_CCOEFF_NORMED
        )
        match_locations = np.where(template_matching >= template.matching_threshold)
        
        for (x, y) in zip(match_locations[1], match_locations[0]):

            match = {
                "TOP_LEFT_X": x,
                "TOP_LEFT_Y": y,
                "BOTTOM_RIGHT_X": x + template.template_width,
                "BOTTOM_RIGHT_Y": y + template.template_height,
                "MATCH_VALUE": template_matching[y, x],
            }

            detections.append(match)

    detections = _non_max_suppression(detections, non_max_suppression_threshold=NMS_THRESHOLD)
    
    if len(detections) == 0:
        raise TrademarkNotFound()

    image_with_detections = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_with_detections = Image.fromarray(image_with_detections)
    for detection in detections:
        
        # ## DETECT MEAN COLOR FOR THE ZONE TO COVER
        im_crop = PILimage.crop((detection["TOP_LEFT_X"], detection["BOTTOM_RIGHT_Y"], detection["BOTTOM_RIGHT_X"],  detection["BOTTOM_RIGHT_Y"]+1))
        avg_color_per_row = np.average(im_crop, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        color = tuple([int(color) for color in tuple(avg_color)[:-1]])
        
        draw = ImageDraw.Draw(image_with_detections)
        draw.rectangle(
            [detection["TOP_LEFT_X"], detection["TOP_LEFT_Y"], detection["BOTTOM_RIGHT_X"], detection["BOTTOM_RIGHT_Y"]],
            fill=color,
            outline=None,
        )
        trademark_cache = Image.new('RGBA', cover.size, color = color)
        trademark_cache = Image.alpha_composite(trademark_cache, cover)
        image_with_detections.paste(trademark_cache, (detection["TOP_LEFT_X"], detection["TOP_LEFT_Y"]))
        

    return image_with_detections
