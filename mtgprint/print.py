import mtgprint.scryfall as scryfall
import shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from os import listdir, remove
from os.path import isfile, join


def clean(filename):
    return  filename.replace(':', '_').replace('/', '_').replace('\x00', '_')

def fetch_card(unique_print, deck_name='deckname'):
    try:
        card_name=unique_print['printed_name']
    except KeyError:
        card_name=unique_print['name']
        
    try:
        pathes = list()
        filename="%s - %s %s - %s" % (card_name, unique_print['set'], unique_print['collector_number'], unique_print['image_status'])
        base_dir = Path('./output/', clean(deck_name))
        dest_front = Path(base_dir, 'front')
        dest_front.mkdir(parents=True, exist_ok=True)
        dest_back = Path(base_dir, 'back')
        dest_back.mkdir(parents=True, exist_ok=True)
        
        if 'card_faces' in unique_print and not unique_print['layout'] == 'split':
            indice=0
            for face in unique_print['card_faces']:
                try:
                    face_name=face['printed_name']
                except KeyError:
                    face_name=face['name']
                face_filename = "%s - %s.png" %(filename, face_name)

                if (indice % 2) != 0:
                    dest = Path(dest_back, clean(face_filename))
                else:
                    dest = Path(dest_front, clean(face_filename))
                indice += 1  

                url = face['image_uris']['png']
                pathes.append(dest)
                scryfall.download(url, dest) 
                
        else:
            url = unique_print['image_uris']['png']
            dest = Path(dest_front, clean(filename+'.png'))
            pathes.append(dest)
            scryfall.download(url, dest)

    except KeyError:
        print(unique_print['uri'])
        raise
    
    return pathes



        