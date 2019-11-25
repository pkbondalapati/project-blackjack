from deck import Deck
from player import Player
from player import Dealer

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
    
    # Player surrenders his hand if eligible.
    def surrender(self, name):
        for player in self.players:
            if player.name == name and player.can_surrender():
                player.bet /= 2

    # Player splits the hand if he has an eligible pair.
    def split(self, name):
        for player in self.players:
            if player.name == name and player.can_split():
                # Modify player's current hand
                split_card = player.hand[0]
                player.hand = [split_card]
                self.hit(player.name)
                
                # Copy current player to a new player in order to 
                # incorporate the current player's split hand
                copied_player = Player(player.name, player.money)
                copied_player.bet = player.bet
                copied_player.record = player.record
                copied_player.hand = [split_card]
                self.hit(player.name)

                # Add the new player to self.players
                index = self.players.index(player)
                self.players.insert(index+1, copied_player)

    # Player takes insurance if eligible.
    def insurance(self, name):
        dealer = self.players[0]
        for player in self.players:
            if player.name == name and dealer.can_offer_insurance():
                player.bet += player.bet/2
