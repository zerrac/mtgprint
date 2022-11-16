#!/usr/bin/env python3

import argparse
from pathlib import Path
import mtgprint.scryfall as scryfall
import shutil
import os
import mtg_parser
from PIL import Image
import random

from mtgprint.deck import parse_deckfile, Deck, Card
from mtgprint.print import fetch_card
from mtgprint.images import add_borders, randomize_image, Template, cover_trademark, TrademarkNotFound
import mtgprint.utils as utils

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare decks for printing as proxies.')
    parser.add_argument('--decklist', default="decklist.txt",
                        dest="decklist",
                        help='load deck list from a file (default : decklist.txt)')
    parser.add_argument('--deckname', type=str,
                        dest="deckname",
                        help='Name of the deck aka name of the folder where the deck will be printed. (default: decklist file name without extension)')
    parser.add_argument('--language', '-l', default="fr", type=str,
                        dest="preferred_lang",
                        help='Card prints localized in specified language will be prioritized. Please use ISO code. (default : fr)')
    parser.add_argument('--notforsale', type=str,
                        dest="notforsale", default=os.path.dirname(__file__)+"/tools/resources/not_for_sale.png",
                        help='Path to the image to put over the trademark')

    args = parser.parse_args()

    utils.print_header("Loading deck list...")
    deck = parse_deckfile(args.decklist, args.preferred_lang)    

    utils.print_header("Fetchings source images...")
    for card in deck.cards + deck.tokens:
        card.pathes = fetch_card(card, deck.name)
    

    utils.print_header("Preparing for impression...")
    counter=0
    not_for_sale = Image.open(args.notforsale)
    templates = [
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt2.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt3.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt4.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt5.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt6.png"),
        Template(image_path=os.path.dirname(__file__)+"/tools/resources/trademark_alt7.png"),
    ]

    card_counter = 0
    for card in deck.cards + deck.tokens:
        for path in card.pathes:
            
            try:
                img = Image.open(path)
                x,y = img.size
                pix = img.load()
            except FileNotFoundError:
                print(path)
                raise
            img = add_borders(img)

            try:
                img = cover_trademark(img, templates, not_for_sale)
            except TrademarkNotFound:
                if not path.match("*/back/*"):
                    utils.print_warn("Trademark was not detected on " + str(path))
            img_copy = img.copy()
            counter=0    
            for _ in range(card.qty):
                counter += 1
                
                dest = Path(path.parents[0], "%02d-%s" % (card_counter+counter, path.name))
                img_copy = randomize_image(img)
                img_copy.save(dest, dpi=(300,300))
            img.close()
            os.remove(path)
        card_counter += counter

utils.print_ok("Deck '%s' is ready for printing !" % deck.name)

print(deck)