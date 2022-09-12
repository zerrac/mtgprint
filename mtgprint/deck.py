from requests.exceptions import HTTPError
from pathlib import Path
import os
import logging
import mtgprint.scryfall as scryfall
import mtg_parser
from tqdm import tqdm

class Card:
    def __init__(self, qty, card):
        self.qty = qty
        self.card = card
        
    def __getitem__(self, key):
        return self.card[key]

    def __contains__(self, key):
        return key in self.card
    
    
    def select_best_candidate(self, preferred_lang='fr'):
        self.card = select_best_candidate(self.card, preferred_lang)
class Deck:
    def __init__(self,deck_name):
        self.name = deck_name
        self.cards=list()
        self.tokens=list()
        self.len = 0
        
    def __len__(self):
        return self.len
    
    def count_cards(self):
        return sum([card.qty for card in self.cards])

    def count_tokens(self):
        return sum([token.qty for token in self.tokens])
    
    def add_card(self, card_name, qty, preferred_lang='fr', preferred_set='', preferred_number=''):
        card = scryfall.named(card_name)
        
        selected_print = select_best_candidate(card, preferred_lang)

        card = Card(qty, selected_print)
        
        token_ids = scryfall.get_tokens(card)
        for token_id in token_ids:
            self._add_token(token_id, preferred_lang)

        self.len += qty
        self.cards.append(card)


    def _has_token(self, token_name):
        i = next((i for i, token in enumerate(self.tokens) if token['name'] == token_name), -1)
        return i >= 0, i

    def _add_token(self, token_id, preferred_lang, qty=1):
        token = scryfall.get_card_by_id(token_id)
        self.len += qty
        has_token, token_indice = self._has_token(token['name'])

        if has_token:
            self.tokens[token_indice].qty += qty
        else:
            token = select_best_candidate(token,preferred_lang)
            token = Card(qty, token)
            self.tokens.append(token)

def evaluate_card_score(card, preferred_lang="fr"):
    score = 0    
    if card["lang"] == preferred_lang:
        score += 200
    elif card["lang"] == 'en':
        score += 100

    if card["collector_number"].isnumeric():
        score += 80

    if  card['type_line'].lower().startswith('basic land') and card['full_art']:
        score += 50

    if card['frame'] == '2015':
        score += 40

    if card['set'] != 'sld':    
        score += 10 
        
    if card["image_status"] == 'highres_scan':
        score += 2
    elif card["image_status"] == 'lowres':
        score += 1
        
    return score

def select_best_candidate(card, preferred_lang='fr'):
    
    if card['type_line'].lower().startswith('basic land'):
        prints = scryfall.get_prints(card["oracle_id"], set_filter='thb')
    else:
        prints = scryfall.get_prints(card["oracle_id"])

    count = 0

    best_score = 0
    best_content_length = 0
    for unique_print in tqdm(prints, desc="Scanning prints of %s " % card['name'], unit="print"):
        if unique_print['lang'] != preferred_lang:
            try:
                localized_print = scryfall.get_localized_card(unique_print["set"],unique_print['collector_number'], preferred_lang)
            except HTTPError:
                # 404 -> The print is not available in preferred language
                localized_print = unique_print
        else:
            localized_print = unique_print

        if localized_print["image_status"] == 'placeholder':
            # We dont want placeholders, better use english version
            localized_print = card

        print_score = evaluate_card_score(localized_print,preferred_lang)
        if print_score > best_score:
            selected_print = localized_print
            best_score = print_score

            selected_print_content_length = scryfall.image_getsize(scryfall.get_face_url(selected_print))

        elif print_score ==  best_score:
            localized_print_content_length = scryfall.image_getsize(scryfall.get_face_url(localized_print))
            if localized_print_content_length > selected_print_content_length:
                selected_print = localized_print
                selected_print_content_length = localized_print_content_length
    logging.info("Selected print for %s has a score of %i (localized in '%s' and with image quality '%s')" % (card['name'], best_score, selected_print['lang'], selected_print['image_status'] )) 
    return selected_print


def parse_deckfile(decklist, preferred_lang='fr'):
    if os.path.isfile(decklist):
        file = Path(decklist)
        deck = Deck(file.stem)
        with open(file, "r", encoding="utf-8") as f:
            decklist = f.read()
        
    cards = mtg_parser.decklist.parse_deck(decklist)
    for card in cards:
        try:
            deck.add_card(card.name, card.quantity, card.extension, card.number)
        except HTTPError:
            print("Card %s not found, skipping..." % card_name)
            continue           
            
    if len(deck) == 0:
        raise BaseException("No cards have been found in your deck list")
    return deck