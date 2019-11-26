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

    # Prints the records of all the players in the game.
    def print_record(self):
        for player in self.players:
            if player.name != 'Dealer':
                print(str(player.name) + ': ' + str(player.record))
    
    # Prints the hands of all the players in the game.
    # Conceals the dealer's first card if needed.
    def print_table(self, show_dealer):
        hands = []
        if show_dealer:
            hidden_suit = self.players[0].hand[0].suit
            hidden_value = self.players[0].hand[0].value
        for player in self.players:
            cards = player.hand
            if player.name == 'Dealer' and show_dealer:
                cards[0].suit = 'Hidden'
                cards[0].value = 'X'
                player.points = cards[1].get_numerical_value()
            points = player.points
            hand = []
            for card in cards:
                hand.append(str(card))
            output = str(player.name) + ': ' + str(hand) + ', Points: ' + str(points)
            hands.append(output)
        if show_dealer:
            cards[0].suit = hidden_suit
            cards[0].value = hidden_value
            self.players[0].points = self.players[0].update_points()
        print(hands)
