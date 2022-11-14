import shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from os import listdir, remove
from os.path import isfile, join
import cv2

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


def set_dpi(path, dpi = 300):
    img = Image.open(path)
    img.save(path, dpi=(dpi,dpi))
    
def add_borders(path, dest, border_width = 36):
  try:
    img = Image.open(path)
    x,y = img.size
    pix = img.load()
  except FileNotFoundError:
    print(path)
    raise
  
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
  img_with_border.save(dest)


def randomize_image(path):
    """
        Make 4 pixels of the image (the 4 corners) random color. This way they wont be regrouped on MPC.
    """
    PILimage = Image.open(path)
    x,y = PILimage.size
    PILimage.putpixel((0, y-1), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.putpixel((0, 0), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.putpixel((x-1, 0), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.putpixel((x-1, y-1), (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)))
    PILimage.save(path)