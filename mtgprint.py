#!/usr/bin/env python3

import argparse
from pathlib import Path
from mtgprint.deck import parse_deckfile, select_best_candidate
from mtgprint.print import fetch_card
from mtgprint.images import add_borders, measure_blurriness, keep_blurry, set_dpi
import mtgprint.scryfall as scryfall
import shutil
import os
import cv2
def print_action(action: str):
    GREEN = '\033[92m'
    ENDC = '\033[0m'
    print(GREEN + action + ENDC)
    

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
    parser.add_argument('--threshold', '-t', default="300", type=float,
                        dest="threshold",
                        help='Threshold for blurriness detection. For image that does not reach this treshold you will be proposed to use english version of the card instead.')
    parser.add_argument('--dontKeepBlurry', default=True,
                        dest="dontkeepblurry", action='store_false',
                        help='Always use english version when the translated version is bellow blurriness treshold')

    args = parser.parse_args()

    print_action("Loading deck list...")
    deck = parse_deckfile(args.decklist, args.preferred_lang)
    print("Found %i cards and %i tokens in your deck." % (deck.count_cards(), deck.count_tokens()))

    if args.deckname:
        deck.name = args.deckname
        
    print_action("Fetchings source images...")
    for card in deck.cards + deck.tokens:
        card.pathes = fetch_card(card, deck.name)
    
        blurriness = measure_blurriness(card.pathes[0])
        if blurriness < args.threshold and args.preferred_lang != 'en':
            print("Image %s seems blurry... " % card['name'], end="")
            if args.dontkeepblurry and keep_blurry(card):
                print('keeping blurry card...')
            else:
                for path in card.pathes:
                    print('Using english version...')
                    os.remove(path)
                card.card = select_best_candidate(scryfall.named(card['name']), 'en')
                card.pathes = fetch_card(card, deck.name)

    print_action("Preparing for impression...")
    counter=0
    for card in deck.cards + deck.tokens:
        counter += 1
        for path in card.pathes:
            set_dpi(path, 300)
            add_borders(path)
            bordered = Path(path.parents[0], "%02d-bordered-%s" % (counter, path.name))
            os.rename(path, bordered)
            # if card.qty>1:
            #     for i in range(card.qty - 1):
            #         copy_name = "%s - %i%s"% (bordered.stem, i+2, ''.join(bordered.suffixes))
            #         copy = Path(bordered.parents[0], copy_name)
            #         shutil.copy(bordered, copy)

print_action("Deck '%s' is ready for printing !" % deck.name)