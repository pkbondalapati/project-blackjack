from deck import Deck
from deck import Card
from player import Player
from player import Dealer
from collections import Counter
import copy
import re

class Table:
    def __init__(self):
        self.players = []
        self.shoe = Deck(6)
        self.shoe.shuffle_deck()
        self.shoe.draw_card()
        self.players.append(Dealer())
        self.running_count = 0
    
    # Adds player to the Blackjack table.
    def add_player(self, name, money):
        player = Player(name, money)
        self.players.append(player)
    
    # Adds bot to the table as specified.
    def add_bot(self, name, money, bet, strategy):
        bot = Player(name, money)
        bot.bot = True
        bot.bet = bet
        bot.strategy = strategy
        self.players.append(bot)
    
    # Returns an array of active players still in a round.
    def active_players(self):
        players = []
        for player in self.players:
            if player.name != 'Dealer' and not player.inactive:
                players.append(player)
        return players
    
    # Player draws another card.
    def hit(self, name, false_draw=False):
        if len(self.shoe) < 52:
            next_shoe = Deck(6)
            next_shoe.shuffle_deck()
            next_shoe.draw_card()
            self.shoe.add_deck(next_shoe.deck)
        elif len(self.shoe) == 312:
            self.running_count = 0
        for player in self.players:
            if player.name == name:
                if player.name != 'Dealer' and false_draw:
                    card = self.shoe.get_card_at(player.index)
                    player.hand.append(card)
                    player.update_points()
                    player.index += 1
                    if player.strategy == 4:
                        self.update_counts(card)
                else:
                    card = self.shoe.draw_card()
                    player.hand.append(card)
                    player.update_points()
                    self.update_counts(card)
    
    # Player stays with this hand;
    # returns the points of the hand.
    def stand(self, name):
        for player in self.players:
            if player.name == name:
                player.inactive = True
                return int(player.points)
    
    # Player doubles the bet and only draws one card.
    def double(self, name, false_draw=False):
        for player in self.players:
            if player.name == name:
                player.bet += player.bet
                if false_draw:
                    self.hit(player.name, false_draw=True)
                else:
                    self.hit(player.name)
                player.inactive = True
    
    # Player surrenders his hand if eligible.
    def surrender(self, name):
        for player in self.players:
            if player.name == name and len(player.hand) == 2:
                player.surrendered = True
                player.inactive = True

    # Player splits the hand if he has an eligible pair.
    def split(self, name, false_draw=False):
        for player in self.players:
            if player.name == name and player.can_split():
                player.split_record = copy.copy(player.record)
                card1 = player.hand[0]
                card2 = player.hand[1]
                copied_player = copy.deepcopy(player)
                # Regular expression for identifying player's hand.
                hand_regex = re.compile(r'\s\(\d\)')
                match = hand_regex.search(player.name)
                if match is None:
                    # Modify player's current hand.
                    player.name += ' (1)'
                    player.hand = [card1]
                    if false_draw:
                        self.hit(player.name, false_draw=True)
                    else:
                        self.hit(player.name)
                    # Modify current player's name to incorporate hand index.
                    copied_player.name += ' (2)'
                    index = self.players.index(player)
                    self.players.insert(index+1, copied_player)
                else:
                    max_number = 0
                    for name in self.split_names(player.name[0:-4]):
                        # Regular expression for identifying player's hand index. 
                        hand_index_regex = re.compile(r'\d')
                        hand_index = hand_index_regex.search(name)
                        number = int(hand_index.group())
                        if number > max_number:
                            max_number = number
                    # Modify current player's name to incorporate hand index.
                    player.hand = [card1]
                    if false_draw:
                        self.hit(player.name, false_draw=True)
                    else:
                        self.hit(player.name)
                    copied_player.name = copied_player.name[0:-2] + str(max_number+1) + ')'

                    # Properly insert player back into players.
                    max_name = player.name[0:-2] + str(max_number) + ')'
                    for member in self.players:
                        if member.name == max_name:
                            index = self.players.index(member)
                            self.players.insert(index+1, copied_player)
                            break

                # Update copied player's hand.
                copied_player.hand = [card2]
                copied_player.index = self.get_index(player.name) + 1
                if false_draw:
                    self.hit(copied_player.name, false_draw=True)
                else:
                    self.hit(copied_player.name)
    
    # Returns the index for a specified player.
    def get_index(self, name):
        for player in self.players:
            if player.name == name:
                return player.index

    # Returns the split hand names for a specified player name
    def split_names(self, name):
        names = []
        for player in self.players:
            hand_regex = re.compile(r'\s\(\d\)')
            match = hand_regex.search(player.name)
            if match is not None and name in player.name:
                names.append(player.name)
        return names


    # Player takes insurance if eligible.
    def insurance(self, name):
        dealer = self.players[0]
        for player in self.players:
            if player.name == name and dealer.can_offer_insurance():
                if dealer.has_blackjack():
                    player.bet = 0
                else:
                    player.bet += int(player.bet/2)
    
    # Merges the record of split hands for a participating player.
    def merge_split(self):
        names = self.split_players()
        for name in names:
            records = []
            for player in self.players:
                if player.name.find(name) == 0:
                    records.append(player.record)
            # Sums the records of the player's split hands.
            merged_record = Counter()
            for record in records:
                merged_record.update(record)
            # Updates the original player's record with merged record.
            for player in self.players:
                if player.name == (name + ' (1)'):
                    for i in range(len(self.split_names(player.name[0:-4]))-1):
                        merged_record.subtract(player.split_record)
                        i += 1
                    player.record = dict(merged_record)
                    player.name = name
            # Selects the copied players needed to be removed.
            remove_players = []
            for player in self.players:
                if player.name.find(name) == 0:
                    # Regular expression for identifying split hands.
                    regex = re.compile(r'\s\(\d\)')
                    match = regex.search(player.name)
                    if match is not None:
                        remove_players.append(player)
            # Removes the copied players.
            for player in remove_players:
                self.players.remove(player)
        
    # Returns an array of players that have split their hands.
    def split_players(self):
        names = []
        # Regular expression for identifying split hands.
        regex = re.compile(r'\s\(\d\)')
        for player in self.players:
            match = regex.search(player.name)
            if match is not None:
                name = player.name[0:-4]
                if name not in names:
                    names.append(name)
        return names
    
    # Updates the counts for the deck for a new card.
    def update_counts(self, card):
        count = card.get_numerical_value()
        if count in [2, 3, 4, 5, 6]:
            self.running_count += 1
        elif count in [10, 11]:
            self.running_count -= 1
    
    # Removes the cards the bots played from previous round. 
    def remove_cards(self):
        index = 0
        for player in self.players:
            if player.name != 'Dealer':
                if player.strategy == 4:
                    index = player.index
        for i in range(index):
            self.shoe.draw_card()
            i += 1

    # Prints the records of all the players in the game.
    def print_record(self):
        self.merge_split()
        print('\nPlayer Records')
        for player in self.players:
            if player.name != 'Dealer':
                print(str(player.name) + ': ' + str(player.record))

    # Prints the hands of all the players in the game.
    # Conceals the dealer's first card if needed.
    def print_table(self, hide_dealer=True):
        hands = []
        for player in self.players:
            cards = copy.deepcopy(player.hand)
            points = player.points
            if player.name == 'Dealer' and hide_dealer:
                cards.pop(0)
                cards.insert(0, Card('Hidden', 'X'))
                points = cards[1].get_numerical_value()
            hand = []
            for card in cards:
                hand.append(str(card))
            output = str(player.name) + ': ' + str(hand) + ', Points: ' + str(points)
            hands.append(output)
        print('\nBlackjack Table')
        for hand in hands:
            print(hand)
