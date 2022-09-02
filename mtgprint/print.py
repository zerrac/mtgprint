from mtgprint.scryfall import scryfall_image_download
import shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from os import listdir, remove
from os.path import isfile, join

def clean(filename):
    return  filename.replace(':', '_').replace('/', '_').replace('\x00', '_')

def fetch_card(unique_print):
    try:
        card_name=unique_print['printed_name']
    except:
        card_name=unique_print['name']
        
    try:
        pathes = list()
        filename="%s - %s %s - %s" % (card_name, unique_print['set'], unique_print['collector_number'], unique_print['image_status'])
        dest_dir="./cards/front/"
        if 'card_faces' in unique_print:
            indice=0
            for face in unique_print['card_faces']:
                try:
                    face_name=face['printed_name']
                except:
                    face_name=face['name']

                if (indice % 2) != 0:
                    dest_dir="./cards/back/"
                indice += 1  

                url = face['image_uris']['png']
                face_filename = "%s - %s.png" %(filename, face_name)
                dest = Path(dest_dir + clean(face_filename))
                pathes.append(dest)
                scryfall_image_download(url, dest) 
                
        else:
            url = unique_print['image_uris']['png']
            dest = Path(dest_dir + clean(filename+'.png'))
            pathes.append(dest)
            scryfall_image_download(url, dest)

    except:
        print(unique_print['uri'])
        raise
    
    return pathes



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


def add_borders(path, border_width = 36):
  try:
    img = Image.open(path)
    x,y = img.size
    pix = img.load()
  except:
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
  dest = Path(path.parents[0], "bordered-" + path.name)
  img_with_border.save(dest)
  
  return dest