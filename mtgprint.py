#!/usr/bin/env python3

import argparse
from pathlib import Path
from mtgprint.deck import parse_deckfile, select_best_candidate
from mtgprint.print import fetch_card
from mtgprint.images import add_borders, measure_blurriness, keep_blurry
from mtgprint.scryfall import scryfall_named
import shutil
import os
import cv2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare decks for printing as proxies.')
    parser.add_argument('--decklist', default="decklist.txt",
                        dest="decklist",
                        help='load deck list from a file (default : decklist.txt)')
    parser.add_argument('--language', '-l', default="fr",
                        dest="preferred_lang",
                        help='Card prints localized in specified language will be prioritized. Please use ISO code. (default : fr)')
    parser.add_argument('--threshold', '-t', default="100", type=float,
                        dest="threshold",
                        help='Threshold for blurriness detection. For image that does not reach this treshold you will be proposed to use english version of the card instead.')

    args = parser.parse_args()

    print("Loading deck list...")
    deck = parse_deckfile(args.decklist, args.preferred_lang)
    print("Found %i cards and %i tokens in your deck." % (len(deck.cards), len(deck.tokens)))
    
    
    print("Fetchings source images...")
    for card in deck.cards + deck.tokens:
        card.pathes = fetch_card(card)
    
        blurriness = measure_blurriness(card.pathes[0])
        if blurriness < args.threshold and args.preferred_lang != 'en':
            print("Image %s seems blurry... " % card['name'], end="")
            if keep_blurry(card):
                print('keeping blurry card...')
            else:
                for path in card.pathes:
                    print('Using english version...')
                    os.remove(path)
                card.card = select_best_candidate(scryfall_named(card['name']), 'en')
                card.pathes = fetch_card(card)

    print("Preparing for impression...")
    for card in deck.cards + deck.tokens:
        for path in card.pathes:
            bordered = add_borders(path) 
            os.remove(path)
            if card.qty>1:
                for i in range(card.qty - 1):
                    copy_name = "%s - %i%s"% (bordered.stem, i+2, ''.join(bordered.suffixes))
                    copy = Path(bordered.parents[0], copy_name)
                    shutil.copy(bordered, copy)

