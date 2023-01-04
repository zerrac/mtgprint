from requests.exceptions import HTTPError
from dataclasses import dataclass
from pathlib import Path
import os
import logging
from tqdm import tqdm
import mtgprint.scryfall as scryfall
import mtg_parser

@dataclass
class Cardboard:
    qty: str
    name: str
    preferred_set: str = None
    oracle_id: str = None
    preferred_number: str = None
    def __str__(self):
        return "%s %s" % (self.qty, self.name)

@dataclass
class Card(Cardboard):
    pass
    
@dataclass
class Token(Cardboard):
    def __str__(self):
        return "%s (oracle_id: %s)" % (super().__str__(), self.oracle_id)

class Deck:
    def __init__(self,deck_name):
        self.name = deck_name
        self.cards=list()
        self.tokens=list()
        self.len = 0
        
    def __len__(self):
        return self.len
    
    def __str__(self):
        if len(self.cards) > 0:
            out = "CARDS :\n"
            for card in self.cards:
                out += str(card) + "\n"
        if len(self.tokens) > 0:
            out += "TOKENS :\n"
            for token in self.tokens:
                out += str(token) + "\n"
        return  out

    def count_cards(self):
        return sum([card.qty for card in self.cards])

    def count_tokens(self):
        return sum([token.qty for token in self.tokens])
    
    def has_card(self, card):
        if isinstance(card, Card):
            card_list = self.cards
        elif isinstance(card, Token):
            card_list = self.tokens
        else:
            raise ValueError('Unknown type %s' % type(card))

        i = next((i for i, c in enumerate(card_list) if c.name == card.name and c.oracle_id==card.oracle_id), -1)

        return i >= 0, card_list, i
    
    def add_card(self, card):
        
        has_card, card_list, card_indice = self.has_card(card)
        if has_card:
                card_list[card_indice].qty += card.qty
        else:
            card_list.append(card)
        
        self.len += card.qty

def parse_deckfile(decklist, preferred_lang='fr'):
    if os.path.isfile(decklist):
        file = Path(decklist)
        deck = Deck(file.stem)
        with open(file, "r", encoding="utf-8") as f:
            decklist = f.read()
        
    cards = mtg_parser.decklist.parse_deck(decklist)
    for parsed_card in cards:
        try:
            card = scryfall.named(parsed_card.name)
            card_tokens = scryfall.get_tokens(card)
            
            card = Card(qty=parsed_card.quantity,name=card['name'], preferred_set=parsed_card.extension, preferred_number=parsed_card.number)
            deck.add_card(card)
            
            for token_id in card_tokens:
                token = scryfall.get_card_by_id(token_id)
                token = Token(qty=1, name=token['name'], oracle_id=token['oracle_id'])
                deck.add_card(token)
            
        except HTTPError:
            print("Card %s not found, skipping..." % parsed_card.name)
            continue
    return deck