from deck import Deck
from deck import Card
import copy

class Player:
    def __init__(self, name, money):
        self.hand = []
        self.value = 0
        self.name = name
        self.money = money
        self.record = {'Wins': 0, 'Losses': 0, 'Draws': 0}

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

class Table:
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.deck.shuffle_deck()
        self.add_player('Dealer', 1000)

    def add_player(self, name, money):
        player = Player(name, money)
        self.players.append(player)
        
    def start_game(self):
        for player in self.players:
            self.hit(player.name)
            self.hit(player.name)
    
    def reset_game(self):
        for player in self.players:
            player.hand = []
            player.update_value()
    
    def blackjack(self):
        winners = []
        for player in self.players:
            if self.stay(player.name) == 21:
                winners.append(player)
        if len(winners) > 1:
            print('Blackjack! It\' is a tie game!')
            for player in winners:
                player.record['Draws'] += 1
            return True
        elif len(winners) == 1:
            print('Blackjack! ' + str(winners[0].name) + ' wins!')
            winners[0].record['Wins'] += 1
            for player in self.players:
                if player.name != winners[0].name:
                    player.record['Losses'] += 1
            return True
        else:
            return False
    
    def play_blackjack(self, rounds):
        for i in range(rounds):
            self.start_game()
            self.show_table()
            if self.blackjack():
                self.show_record()
                self.reset_game()
                print()
                continue
            for player in self.players:
                if player.name != 'Dealer':
                    while not self.is_busted(player.name):
                        print('What is your move: hit (h) or stay (s)?')
                        action = input()
                        if action in ['Hit', 'hit', 'H', 'h']:
                            self.hit(player.name)
                        else:
                            break
                        self.show_table()
            self.dealer_plays()
            self.show_record()
            self.reset_game()
            print()
            i += 1
    
    def hit(self, player_name):
        if len(self.deck) == 0:
            self.deck = Deck()
            self.deck.shuffle_deck()
        for player in self.players:
            if player_name == player.name:
                new_card = self.deck.draw_card()
                player.hand.append(new_card)
                player.update_value()
    
    def stay(self, player_name):
        for player in self.players:
            if player_name == player.name:
                return int(player.value)
    
    def is_busted(self, player_name):
        for player in self.players:
            if player_name == player.name:
                if player.value > 21:
                    return True
                else:
                    return False

    def show_table(self, dealers_play=False):
        hands = []
        for player in self.players:
            cards = player.hand
            if player.name == 'Dealer' and not dealers_play:
                cards[1].suit = 'Hidden'
                cards[1].value = 'X'
                player.value = cards[0].get_numerical_value()
            value = player.value

            hand = []
            for card in cards:
                hand.append(str(card))

            output = str(player.name) + ': ' + str(hand) + ', Value: ' + str(value)
            hands.append(output)
        print(hands)
    
    def score_game(self, dealers_play=False):
        eligible_players = copy.copy(self.players)
        for player in eligible_players:
            if self.is_busted(player.name):
                print(str(player.name) + ' busted.')
                eligible_players.remove(player)

        if len(eligible_players) == 1 and eligible_players[0].name == 'Dealer':
            print('Dealer wins!')
            eligible_players[0].record['Wins'] += 1
            for player in self.players:
                if player.name != 'Dealer':
                    player.record['Losses'] += 1
            return True
        elif dealers_play:
            return False
        
        highest_score = 0
        winner = None
        for player in eligible_players:
            if player.value > highest_score:
                highest_score = player.value
                winner = player
        
        winners = []
        for player in eligible_players:
            if player.value == winner.value:
                winners.append(player)
        
        if len(winners) > 1:
            print('It\'s a tie game!')
            for player in winners:
                player.record['Draws'] += 1
        else:
            print(str(winner.name) + ' has the highest score; ' + str(winner.name) + ' wins!')
            winner.record['Wins'] += 1
            for player in self.players:
                if player.name != winner.name:
                    player.record['Losses'] += 1
            return False

    def dealer_plays(self):
        dealer = self.players[0]
        dealer.hand[1].suit = dealer.hand[1].hidden_suit
        dealer.hand[1].value = dealer.hand[1].hidden_value
        dealer.update_value()

        self.show_table(dealers_play=True)
        if self.score_game(dealers_play=True):
            return

        while self.stay('Dealer') <= 16:
            self.hit('Dealer')
            self.show_table(dealers_play=True)

        if self.stay('Dealer') == 17:
            for card in dealer.hand:
                if card.value == 'A':
                    while self.stay('Dealer') <= 16:
                        self.hit('Dealer')
                        self.show_table(dealers_play=True)
                    if self.stay('Dealer') < 21:
                        break
        
        self.score_game()
    
    def show_record(self):
        for player in self.players:
            print(str(player.name) + ': ' + str(player.record))

    def __str__(self):
        hands = []
        for player in self.players:
            hands.append(str(player))
        return str(hands)
        
    
if __name__ == '__main__':
    t = Table()
    t.add_player('Pavan', 1000)
    t.play_blackjack(10)
