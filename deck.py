import random

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def get_numerical_value(self):
        if self.value == 'A':
            value = 11
        elif self.value in ['J', 'Q', 'K']:
            value = 10
        else:
            value = int(self.value)
        return value
    
    def __str__(self):
        return str(self.suit) + ': ' + str(self.value)

class Deck:
    def __init__(self, sets=1):
        self.deck = []
        self.__create_deck(sets)
    
    def __create_deck(self, sets):
        deck = []
        suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for suit in suits:
            for value in values:
                deck.append(Card(suit, value))
        master_deck = []
        for i in range(sets):
            master_deck += deck
            i += 1
        self.deck = master_deck
    
    def shuffle_deck(self):
        random.shuffle(self.deck)
    
    def draw_card(self):
        return self.deck.pop()
    
    def __str__(self):
        deck = []
        for card in self.deck:
            deck.append(str(card))
        return str(deck)
    
    def __len__(self):
        return len(self.deck)
            
if __name__ == '__main__':
    d = Deck(6)
    d.shuffle_deck()
    print(d)
    print(len(d))
    c1 = d.draw_card()
    print(c1)
    print(len(d))