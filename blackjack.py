from deck import Deck
from deck import Card
import copy

class Player:
    def __init__(self, name, money=0, bet=0):
        self.hand = []
        self.points = 0
        self.bet = 0
        self.name = name
        self.record = {'Wins': 0, 'Losses': 0, 'Draws': 0, 'Money': money}
    
    # Updates the points of the player's current hand,
    # as according to the rules of Blackjack.
    def update_points(self):
        points = 0
        for card in self.hand:
            points += card.get_numerical_value()
        if points > 21:
            for card in self.hand:
                if card.value == 'A':
                    points -= 10
                if points < 21:
                    break
        self.points = points
    
    # Checks if the player has an eligible hand to split.
    def can_split(self):
        if len(self.hand) == 2 and self.hand[0].value == self.hand[1].value:
            return True
        else:
            return False
    
    # Checks if the player is eligible to surrender hand.
    def can_surrender(self):
        if len(self.hand) == 2:
            return True
        else:
            return False
    
    # Checks if the player has busted.
    def has_busted(self):
        if self.points > 21:
            return True
        else:
            return False
    
    # Checks if the player has 21.
    def has_blackjack(self):
        if len(self.hand) == 2 and self.points == 21:
            return True
        else:
            return False
    
    def __str__(self):
        hand = []
        for card in self.hand:
            hand.append(str(card))
        return str(self.name) + ': ' + str(hand) + ', Points: ' + str(self.points)

class Dealer(Player):
    def __init__(self):
        self.hand = []
        self.points = 0
        self.name = 'Dealer'
    
    # Checks if dealer can offer insurance. 
    def offer_insurance(self):
        if len(self.hand) == 2 and self.hand[1].value == 'A':
            return True
        else:
            return False

class Table:
    def __init__(self):
        self.players = []
        self.shoe = Deck(6)
        self.shoe.shuffle_deck()
        self.players.append(Dealer())
    
    def add_player(self, name, money):
        player = Player(name, money)
        self.players.append(player)
    
    def reset_game(self):
        for player in self.players:
            player.hand = []
            player.points = 0
    
    # Player draws another card.
    def hit(self, name):
        if len(self.shoe) == 0:
            self.shoe = Deck(6)
            self.shoe.shuffle_deck()
        for player in self.players:
            if player.name == name:
                card = self.shoe.draw_card()
                player.hand.append(card)
                player.update_points()
    
    # Player stays with this hand;
    # returns the points of the hand.
    def stand(self, name):
        for player in self.players:
            if player.name == name:
                return int(player.points)
    
    # Player doubles the bet and only draws one card.
    def double(self, name):
        for player in self.players:
            if player.name == name:
                player.bet += player.bet
                self.hit(player.name)

    # Player splits the hand if he has an eligible pair.    
    def split(self, name):
        #TODO:
        pass
    
    # Player takes insurance if eligible.
    def insurance(self, name):
        #TODO:
        pass
