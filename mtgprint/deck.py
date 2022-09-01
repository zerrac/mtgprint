from mtgprint.scryfall import scryfall_named, scryfall_get_prints, scryfall_get_localized_card
from requests.exceptions import HTTPError

class Card:
    def __init__(self, qty, card):
        self.qty = qty
        self.card = card
        
    def __getitem__(self, key):
        return self.card[key]

    def __contains__(self, key):
        return key in self.card
    

class Deck:
    def __init__(self):
        self.cards=list()
    
    def __len__(self):
        return len(self.cards)
    
    def add_card(self, card, qty):
        card = Card(qty, card)
        self.cards.append(card)
        
            

def evaluate_card_score(card, preferred_lang="fr"):
    score = 0    
    if card["lang"] == preferred_lang:
        score += 20
    elif card["lang"] == 'en':
        score += 10


    if card["image_status"] == 'highres_scan':
        score += 2
    elif card["image_status"] == 'lowres':
        score += 1
        
    return score
         
def parse_deckfile(filepath, preferred_lang='fr'):
    deck = Deck()
    with open(filepath, "r", encoding="utf-8") as f:
        for x in f:
            qty = int(x.split(' ')[0].strip())
            card_name = " ".join(x.split(' ')[1:]).strip()
            try:
                card = scryfall_named(card_name)
            except:
                print("Card %s not found, skipping..." % card_name)
                continue
            prints = scryfall_get_prints(card["oracle_id"])
                        
            count = 0
            best_score = 0
            max_score = 22
            for unique_print in prints:
                count += 1
                print("Scanning prints of %s (%i/%i)" % (card_name, count, len(prints) ), end='\r')
                try:
                    localized_print = scryfall_get_localized_card(unique_print["set"],unique_print['collector_number'], preferred_lang)
                except HTTPError as e:
                    localized_print = unique_print
                except:
                    raise
                print_score = evaluate_card_score(localized_print,preferred_lang)
                if print_score > best_score or best_score == 0:
                    selected_print = localized_print
                    best_score = print_score
                    
                if best_score == max_score:
                    break
                
            print("Selected print for %s has a score of %i (localized in '%s' and with image quality '%s')" % (card_name, best_score, selected_print['lang'], selected_print['image_status'] )) 
            deck.add_card(selected_print, qty)
    if len(deck) == 0:
        raise BaseException("No cards have been found in your deck list")
    return deck