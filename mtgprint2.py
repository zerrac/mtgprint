#!/usr/bin/env python3

import argparse
from pathlib import Path
from mtgprint.deck import parse_deckfile, Deck, Card
from mtgprint.print import fetch_card
from mtgprint.images import add_borders, measure_blurriness, keep_blurry, set_dpi
import mtgprint.scryfall as scryfall
import shutil
import os
import mtg_parser
from PIL import Image
import random

def colored_print(string: str, color):
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    print(color + BOLD + string + ENDC)

def print_header(string: str):
    HEADER = '\033[95m'
    colored_print(string,HEADER)

def print_ok(string: str):
    OK = '\033[92m'
    colored_print(string, OK)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare decks for printing as proxies.')
    parser.add_argument('--decklist', default="decklist.txt",
                        dest="decklist",
                        help='load deck list from a file (default : decklist.txt)')
    parser.add_argument('--deckname', type=str,
                        dest="deckname",
                        help='Name of the deck aka name of the folder where the deck will be printed. (default: decklist file name without extension')
    parser.add_argument('--language', '-l', default="fr", type=str,
                        dest="preferred_lang",
                        help='Card prints localized in specified language will be prioritized. Please use ISO code. (default : fr)')

    args = parser.parse_args()

    print_header("Loading deck list...")
    deck = parse_deckfile(args.decklist, args.preferred_lang)    

    print_header("Fetchings source images...")
    for card in deck.cards + deck.tokens:
        card.pathes = fetch_card(card, deck.name)
    

    print_header("Preparing for impression...")
    counter=0
    for card in deck.cards + deck.tokens:
        for _ in range(card.qty):
            counter += 1
            for path in card.pathes:
                set_dpi(path, 300)
                bordered = Path(path.parents[0], "%02d-bordered-%s" % (counter, path.name))
                add_borders(path, bordered)
                if _ == card.qty - 1:
                    os.remove(path)
                randomize_image(bordered)
print_ok("Deck '%s' is ready for printing !" % deck.name)

print(deck)