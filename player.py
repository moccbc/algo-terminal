from card import Card, CardColor
from copy import deepcopy

class GuessMetadata:
    def __init__(self, number, color, time, guesses):
        self.number = number
        self.color = color
        self.time = time
        self.guesses = []

class Player:
    def __init__(self, name):
        self.hand = [] # This is a list of type Card
        self.name = name
        self.guess_metadatas = []

    def add_to_hand(self, new_card):
        self.hand.append(new_card)
        if 4 < len(self.hand):
            self.hand[-1].is_new = True
        self.hand.sort()

    def reveal_newest(self):
        for card in self.hand:
            if card.is_new:
                card.is_new = False
                card.reveal()
                break

    def get_hand(self):
        hand = deepcopy(self.hand)
        return hand

    def reset_newest(self):
        for card in self.hand:
            card.is_new = False

    def reset(self):
        self.hand = []

    def look_at_opponents_hand(self, cards):
        cards.sort()
        for card in cards:
            self.guess_metadatas.append(GuessMetadata(
                (card.number if card.is_revealed else -1),
                (1 if card.color == CardColor.WHITE else 0),
                card.time,
                []
            ))

    def print_for_ai(self):
        print(len(self.guess_metadatas))
        for metadata in self.guess_metadatas:
            print(metadata.number, metadata.color, metadata.time, (len(metadata.guesses)), end=" ")
            if len(metadata.guesses) > 0:
                for guess in metadata.guesses:
                    print(guess, end=" ")
            print()
        print(len(self.hand))
        for card in self.hand:
            print(card.number, (1 if card.color == CardColor.WHITE else 0))
        print()
