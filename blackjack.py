from deck import Deck
from deck import Card
import copy

class Dealer:
    def __init__(self):
        self.hand = []
        self.value = 0
        self.name = 'Dealer'

    # Updates the value of the player's current hand,
    # as according to the rules of Blackjack.
    def update_value(self):
        value = 0
        for card in self.hand:
            value += card.get_numerical_value()
        if value > 21:
            for card in self.hand:
                if card.value == 'A':
                    value -= 10
                if value < 21:
                    break
        self.value = value
    
    def __str__(self):
        hand = []
        for card in self.hand:
            hand.append(str(card))
        return str(self.name) + ': ' + str(hand) + ', Value: ' + str(self.value)

class Player(Dealer):
    def __init__(self, name, money):
        self.hand = []
        self.value = 0
        self.bet = 0
        self.name = name
        self.record = {'Wins': 0, 'Losses': 0, 'Draws': 0, 'Money': money}
        
class Table:
    def __init__(self):
        self.players = []
    
    
