import mtgprint.scryfall as scryfall
import shutil
import os
from pathlib import Path
from mtgprint.deck import Card, Token
from urllib.error import HTTPError

def download(url, dest):
    if not os.path.exists(dest):
        try:
            with scryfall.rate_limiter:
                re = scryfall.http.get(url, stream=True)
            re.raise_for_status()

            with open(dest, 'xb') as f:
                re.raw.decode_content = True
                shutil.copyfileobj(re.raw, f)
        except HTTPError as err:
            os.remove(dest)
            if err.code == 404:
                print("404 lors de la récupération de l'image. Peut etre qu'il faut mettre à jour la base de l'api ?")
            else:
                raise
    else:
        print("Previous copy of the card found. Reusing it!")

def clean(filename):
    return  filename.replace(':', '_').replace('/', '_').replace('\x00', '_')

def fetch_card(unique_print, deck_name='deckname'):

    card_name = unique_print.name
    try:
        pathes = list()

        base_dir = Path('./output/', clean(deck_name))
        dest_front = Path(base_dir, 'front')
        dest_front.mkdir(parents=True, exist_ok=True)
        dest_back = Path(base_dir, 'back')
        dest_back.mkdir(parents=True, exist_ok=True)
        
        indice=0
        for face_name in card_name.split(" // "):

            url = "https://card-api.zerrac.fr/cards/?image_format=png&lang=fr&face_name=%s" % face_name
                
            if isinstance(unique_print, Token):
                url = "%s&oracle_id=%s" % (url, unique_print.oracle_id)
                face_filename = "%s - %s.png" % (face_name, unique_print.oracle_id)
            else:
                face_filename = "%s.png" % face_name

            if unique_print.preferred_set:
                url = "%s&preferred_set=%s" % (url, unique_print.preferred_set)
            if unique_print.preferred_number:
                url = "%s&preferred_number=%s" % (url, unique_print.preferred_number)

            if (indice % 2) != 0:
                dest = Path(dest_back, clean(face_filename))
            else:
                dest = Path(dest_front, clean(face_filename))
            indice += 1
            pathes.append(dest)
            download(url, dest)
        if indice != 2:
            dest = Path(dest_back, clean(card_name)+'.png')
            pathes.append(dest)
            shutil.copyfile("./MPC_Back.png", dest)
    except KeyError:
        print(unique_print['uri'])
        raise
    
    return pathes



        