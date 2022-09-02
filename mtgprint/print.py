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
    except KeyError:
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
                except KeyError:
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

    except KeyError:
        print(unique_print['uri'])
        raise
    
    return pathes



        