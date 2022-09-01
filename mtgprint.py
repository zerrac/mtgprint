#!/usr/bin/env python3

import argparse
from pathlib import Path
from mtgprint.deck import parse_deckfile
from mtgprint.scryfall import scryfall_image_download
from mtgprint.print import fetch_card, add_borders
import shutil
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare decks for printing as proxies.')
    parser.add_argument('--decklist', default="decklist.txt",
                        dest="decklist",
                        help='load deck list from a file (default : decklist.txt)')
    parser.add_argument('--language', '-l', default="fr",
                        dest="preferred_lang",
                        help='Card prints localized in specified language will be prioritized. Please use ISO code. (default : fr)')

    args = parser.parse_args()

    print("Loading deck list...")
    deck = parse_deckfile(args.decklist, args.preferred_lang)
    
    print("Fetchings source images...")
    for card in deck.cards:
        card.pathes = fetch_card(card)
    
    print("Preparing for impression...")
    for card in deck.cards:
        for path in card.pathes:
            bordered = add_borders(path) 
            os.remove(path)
            if card.qty>1:
                for i in range(card.qty - 1):
                    copy_name = "%s - %i%s"% (bordered.stem, i+2, ''.join(bordered.suffixes))
                    copy = Path(bordered.parents[0], copy_name)
                    shutil.copy(bordered, copy)

