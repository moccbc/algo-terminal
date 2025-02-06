from enum import Enum

class CardColor(str, Enum):
    BLACK = "black"
    WHITE = "white"

class Card:
    def __init__(self, number, color, is_revealed=False, is_new=False):
        self.number = number
        self.color = color
        self.is_revealed = is_revealed
        self.is_new = is_new
        self.time = -1

    def reveal(self):
        self.is_revealed = True

    def __lt__(self, other):
        if self.number == other.number:
            return self.color < other.color
        return self.number < other.number

    def __gt__(self, other):
        if self.number == other.number:
            return self.color > other.color
        return self.number > other.number

    def __eq__(self, other):
        return self.number == other.number and self.color == other.color

    def __str__(self):
        return self.color + " " + str(self.number)
