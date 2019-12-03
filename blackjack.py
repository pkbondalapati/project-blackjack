from table import Table
from player import Player
import random
import csv
import os

class Blackjack:
    def __init__(self):
        self.table = Table()
        self.first_iter = True
        self.rounds = 0
        self.count = 0

    # Lists the general rules of Blackjack.
    # Adds players to the table as specified. 
    def setup(self):
        print('\nWelcome to Blackjack!')
        print('Dealer must draw until 16 and at soft 17')
        print('Dealer must stand on 17')
        print('Blackjack pays 3 to 2')
        print('Insurance pays 2 to 1')
        print('Minimum bet is $10\n')

        print('What is the buy-in? (e.g. 1000)')
        money = 1000
        #money = input()
        print('\nHow many players?')
        count = 0
        #count = input()
        print('\nHow many rounds do you want to play?')
        rounds = 1000
        #rounds = input()
        self.rounds = int(rounds)
        self.count = int(count)
        
        for i in range(int(count)):
            print('\nWhat is Player ' + str(i+1) + '\'s name?')
            name = input()
            self.table.add_player(name, int(money))
        
        # Add bots to table if there are no players.
        if self.count == 0:
            self.table.add_bot('Dealer-Bot', 1000, 50, 1)
            self.table.add_bot('Random-Bot', 1000, 50, 2)
            self.table.add_bot('Basic-Bot', 1000, 50, 3)
            self.table.add_bot('Biased-Bot', 1000, 50, 4)
    
    # Takes bets from the opening round.
    def place_bets(self):
        for player in self.table.active_players():
            print('\nWhat is your bet, ' + str(player.name) + '?')
            bet = input()
            while int(bet) < 10:
                print('\nMinimum bet is $10')
                print('Would you like to continue playing? (y/n)')
                response = input()
                if response in ['No', 'no', 'N', 'n']:
                    self.table.players.remove(player)
                    print('\nThank you for playing Blackjack!')
                    return
                elif response in ['Yes', 'yes', 'Y', 'y']:
                    print('\nWhat is your bet, ' + str(player.name) + '?')
                    bet = input()
                else:
                    print('\nInvalid input. Please try again.')
            player.bet = int(bet)

    # Draws two cards for all the players.
    def start_round(self):
        for player in self.table.players:
            if player.name != 'Dealer' and player.strategy == 4:
                self.biased_strategy(player)
        for player in self.table.players:
            self.table.hit(player.name)
        for player in self.table.players:
            self.table.hit(player.name)
        self.table.print_table()
    
    # Plays one iteration of a hit/stand round.
    def play_round(self):
        dealer = self.table.players[0]
        # Checks if the dealer is eligible to offer insurance.
        if dealer.can_offer_insurance() and self.first_iter:
            for player in self.table.active_players():
                if player.strategy == 0:
                    print('\nWould you like to purchase insurance against a Blackjack, ' + str(player.name) + '? (y/n)')
                    insurance_response = input()
                    if insurance_response in ['Yes', 'yes', 'Y', 'y']:
                        self.table.insurance(player.name)
        
        for player in self.table.active_players():
            # Play ends immediately when the dealer has Blackjack.
            if dealer.has_blackjack():
                print('\n' + str(dealer.name) + ' has Blackjack.')
                for member in self.table.active_players():
                    member.inactive = True
                return
            # Notifies player if he has made Blackjack.
            if player.has_blackjack():
                print('\n' + str(player.name) + ' has Blackjack!')
            
            if player.strategy == 0:
                options = self.get_options(player)
                response = self.get_response(options, player)

                if response in ['hit', 'h', 'H']:
                    self.table.hit(player.name)
                elif response in ['stand', 's', 'S']:
                    self.table.stand(player.name)
                elif response in ['double', 'd', 'D']:
                    self.table.double(player.name)
                elif response in ['surrender', 'u', 'U']:
                    self.table.surrender(player.name)
                elif response in ['split', 'p', 'P']:
                    self.table.split(player.name)
            else:
                self.run_strategy(player)

            if player.has_busted():
                player.inactive = True
                print('\n' + str(player.name) + ' has busted.')
            self.table.print_table()
    
    # Returns an array of a options for a specified player.
    def get_options(self, player):
        options = ['hit', 'stand']
        if len(player.hand) == 2:
            options.append('double')
            options.append('surrender')
        if player.can_split():
             options.append('split')
        return options
    
    # Prints a message of eligilbe options and returns a valid user response.
    def get_response(self, options, player):
        sub_options = ''
        if len(options) == 2:
            message = 'Would you like to hit (h) or stand (s), ' + str(player.name) + '?'
            sub_options = 'hs'
        elif len(options) == 4:
            message = 'Would you like to hit (h), stand (s), double (d) or surrender (u), ' + str(player.name) + '?'
            sub_options = 'hsdu'
        elif len(options) == 5:
            message = 'Would you like to hit (h), stand (s), split (p), double (d) or surrender (u), ' + str(player.name) + '?'
            sub_options = 'hspdu'
        
        print('\n'+str(message))
        response = input()
        
        # Checks if user provides a valid response; otherwise reprints the message.
        while not (response in options or response in sub_options or response in sub_options.upper()):
            print('\nInvalid input. Please try again.')
            print(message)
            response = input()
        return response   

    # Runs a game of Blackjack for a specified number of rounds.
    def run(self):
        self.setup()
        for i in range(self.rounds):
            print('\nRound: ' + str(i+1))
            if self.count != 0:
                self.place_bets()
            self.start_round()
            while len(self.table.active_players()) != 0:
                self.play_round()
                self.first_iter = False
            self.dealer_plays()
            self.score_game()
            self.reset()
            i += 1
    
    # Dealer plays his hand to completion as predefined.
    def dealer_plays(self):
        dealer = self.table.players[0]
        self.table.print_table(hide_dealer=False)
        print()
        
        # Dealer does not play if everyone busts.
        active = False
        for player in self.table.players:
           if not player.has_busted() and player.name != 'Dealer':
               active = True
        
        if active:
            # Dealer must draw until 16 and at soft 17.
            while dealer.points < 17:
                self.table.hit(dealer.name)
                print(str(dealer.name) + ' hits.')
            if dealer.points == 17:
                for card in dealer.hand:
                    if card.value == 'A':
                        self.table.hit(dealer.name)
                        print(str(dealer.name) + ' hits.')
                        break
            while dealer.points < 17:
                self.table.hit(dealer.name)
                print(str(dealer.name) + ' hits.')
        else:
            print('Everyone has busted.')

        if dealer.points <= 21:
            print(str(dealer.name) + ' stands.')
        elif dealer.has_busted():
            print(str(dealer.name) + ' has busted.')        
        self.table.print_table(hide_dealer=False)
    
    # Pays out winners and prints each player's updated record.
    def score_game(self):
        dealer = self.table.players[0]
        for player in self.table.players:
            if player.name != dealer.name:
                # Player has surrendered their hand.
                if player.surrendered:
                    player.record['Money'] -= int(player.bet/2)
                    player.record['Losses'] += 1
                # Player has winning Blackjack.
                elif player.has_blackjack() and not dealer.has_blackjack():
                    player.record['Money'] += int(player.bet*1.5)
                    player.record['Wins'] += 1
                # Player has busted their hand.
                elif player.has_busted():
                    player.record['Money'] -= player.bet
                    player.record['Losses'] += 1
                # Dealer has busted their hand.
                elif dealer.has_busted():
                    player.record['Money'] += player.bet
                    player.record['Wins'] += 1
                # Dealer has equal points as player.
                elif dealer.points == player.points:
                    player.record['Draws'] += 1
                # Dealer has more points than player.
                elif dealer.points > player.points:
                    player.record['Money'] -= player.bet
                    player.record['Losses'] += 1
                # Player has more points than dealer.
                elif player.points > dealer.points:
                    player.record['Money'] += player.bet
                    player.record['Wins'] += 1
        self.table.print_record()

    # Empties the hand of each player on the table.
    def reset(self):
        for player in self.table.players:
            player.hand = []
            player.points = 0
            player.inactive = False
            player.surrendered = False
            player.soft = False
            player.bet = 50
        self.first_iter = True
    
    # Runs the specific strategy designated to the player.
    def run_strategy(self, player):
        if player.strategy == 1:
            response = self.dealers_strategy(player)
        elif player.strategy == 2:
            response = self.random_strategy(player)
        elif player.strategy == 3:
            response = self.basic_strategy(player)
        elif player.strategy == 4:
            response = self.basic_strategy(player)

        if response in ['hit', 'h', 'H']:
            self.table.hit(player.name)
            print('\n' + str(player.name) + ' hits.')
        elif response in ['stand', 's', 'S']:
            self.table.stand(player.name)
            print('\n' + str(player.name) + ' stands.')
        elif response in ['double', 'd', 'D']:
            self.table.double(player.name)
            print('\n' + str(player.name) + ' doubles.')
        elif response in ['surrender', 'u', 'U']:
            self.table.surrender(player.name)
            print('\n' + str(player.name) + ' surrendered.')
        elif response in ['split', 'p', 'P']:
            self.table.split(player.name)
            print('\n' + str(player.name) + ' split.')

    # Follows the dealer's strategy for a given hand to completion.
    def dealers_strategy(self, player):
        if player.points < 17:
            return 'hit'
        elif player.points == 17 and not player.is_hard():
            return 'hit'
        else:
            return 'stand'
    
    # Follows the dealer's strategy for a given hand;
    # the decision to hit or stand at 17 is random.
    def random_strategy(self, player):
        if player.points < 16:
            return 'hit'
        elif player.points == 16:
            if random.getrandbits(1):
                return 'hit'
            else:
                return 'stand'
        else:
            return 'stand'

    # Follows basic strategy defined in Blackjack.
    # FMI: https://wizardofodds.com/games/blackjack/strategy/4-decks/
    def basic_strategy(self, player):
        dealer = self.table.players[0]
        points = dealer.hand[1].get_numerical_value()

        if player.can_split():
            if player.points in [4, 6]:
                if points in [2, 3, 4, 5, 6, 7]:
                    return 'split'
                elif points in [8, 9, 10, 11]:
                    return 'hit'
            if player.points == 8:
                if points in [5, 6]:
                    return 'split'
                elif points in [2, 3, 4, 7, 8, 9, 10, 11]:
                    return 'hit'
            elif player.points == 10:
                if points in [2, 3, 4, 5, 6, 7, 8, 9]:
                    return 'double'
                else:
                    return 'hit'
            elif player.points in [12, 14, 16, 18, 22] and points in [2, 3, 4, 5, 6]:
                return 'split'
            elif player.points == 12 and points in [7, 8, 9, 10, 11] and player.hand[1].value != 'A':
               return 'hit'
            elif player.points == 14:
                if points == 7:
                    return 'split'
                elif points in [8, 9, 10, 11]:
                    return 'hit'
            elif player.points == 16:
                if points in [7, 8, 9, 10]:
                    return 'split'
                elif points == 11:
                    return 'surrender'
            elif player.points == 18:
                if points in [7, 10, 11]:
                    return 'stand'
                elif points in [8, 9]:
                    return 'split'
            elif player.points == 20:
                return 'stand'
            elif player.points == 12 and player.hand[1].value == 'A':
                return 'split'
        elif player.is_hard():
            if player.points in [4, 5, 6, 7, 8]:
               return 'hit'
            elif player.points == 9:
                if points in [2, 7, 8, 9, 10, 11]:
                    return 'hit'
                else:
                    if len(player.hand) == 2:
                        return 'double'
                    else:
                        return 'hit'
            elif player.points == 10:
                if points in [2, 3, 4, 5, 6, 7, 8, 9] and len(player.hand) == 2:
                    return 'double'
                else:
                    return 'hit'
            elif player.points == 11:
                if len(player.hand) == 2:
                        return 'double'
                else:
                    return 'hit'
            elif player.points == 12:
                if points in [2, 3, 7, 8, 9, 10, 11]:
                    return 'hit'
                else:
                    return 'stand'
            elif player.points in [13, 14, 15, 16, 17] and points in [2, 3, 4, 5, 6]:
                return 'stand'
            elif player.points in [13, 14] and points in [7, 8, 9, 10, 11]:
               return 'hit'
            elif player.points == 15:
                if points in [7, 8, 9]:
                    return 'hit'
                elif points in [10, 11]:
                    if len(player.hand) == 2:
                        return 'surrender'
                    else:
                        return 'hit'
            elif player.points == 16:
                if points in [7, 8]:
                    return 'hit'
                elif points in [9, 10, 11]:
                    if len(player.hand) == 2:
                        return 'surrender'
                    else:
                        return 'hit'
            elif player.points == 17:
                if points in [7, 8, 9, 10]:
                    return 'stand'
                elif points == 11:
                    if len(player.hand) == 2:
                        return 'surrender'
                    else:
                        return 'stand'
            elif player.points in [18, 19, 20, 21]:
                return 'stand'
        else:
            if player.points in [13, 14, 15, 16, 17] and points in [7, 8, 9, 10, 11]:
               return 'hit'
            elif player.points in [13, 14]:
                if points in [2, 3, 4]:
                    return 'hit'
                elif points in [5, 6]:
                    if len(player.hand) == 2:
                        return 'double'
                    else:
                        return 'hit'
            elif player.points in [15, 16]:
                if points in [2, 3]:
                    return 'hit'
                elif points in [4, 5, 6]:
                    if len(player.hand) == 2:
                        return 'double'
                    else:
                        return 'hit'
            elif player.points == 17:
                if points == 2:
                    return 'hit'
                elif points in [3, 4, 5, 6]:
                    if len(player.hand) == 2:
                        return 'double'
                    else:
                        return 'hit'
            elif player.points == 18:
                if points in [2, 3, 4, 5, 6]:
                    if len(player.hand) == 2:
                        return 'double'
                    else:
                        return 'stand'
                elif points in [7, 8]:
                    return 'stand'
                elif points in [9, 10, 11]:
                    return 'hit'
            elif player.points == 19:
                if points == 6:
                    if len(player.hand) == 2:
                        return 'double'
                    else:
                        return 'stand'
                else:
                    return 'stand'
            elif player.points in [20, 21]:
                return 'stand'         
    
    # Follows basic strategy and biases each bet on the cards
    # that have previously been played (i.e. counting cards).
    def biased_strategy(self, player):
        decks_left = int(len(self.table.shoe)/52)
        if decks_left != 0:
            true_count = self.table.running_count/decks_left
            if true_count > 3:
                player.bet += int(50*0.75)
            elif true_count <= 3 and true_count > 2:
                player.bet += int(50*0.50)
            elif true_count <= 2 and true_count > 1:
                player.bet += int(50*0.25)
            elif true_count <= 1 and true_count > 0:
                player.bet += int(50*0.125)
            elif true_count <= 0 and true_count > -1:
                player.bet -= int(50*0.125)
            elif true_count <= -1 and true_count > -2:
                player.bet -= int(50*0.25)
            elif true_count <= -2:
                player.bet = 0

        if player.bet < 0:
            player.bet = 0
    
    def write_file(self, rounds, iterations):
        player_output = []
        run_output = []
        self.rounds = rounds
        for i in range(iterations):
            self.run()
            for player in self.table.players:
                if player.name != 'Dealer':
                    player_output.append(i)
                    player_output.append(player.name)
                    player_output.append(player.record['Wins'])
                    player_output.append(player.record['Losses'])
                    player_output.append(player.record['Draws'])
                    player_output.append(player.record['Money'])
                    performance = ((player.record['Losses']/player.record['Wins'])*player.record['Money'])/1000
                    player_output.append(performance)
                    run_output.append(player_output)
                    player_output = []
            self.table = Table()
            i += 1
        
        cwd = os.getcwd()
        file_to_open = cwd+'\\blackjack_output250.csv'
        with open(file_to_open, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Iteration', 'Name', 'Wins', 'Losses', 'Draws', 'Money', 'Performance'])
            for run in run_output:
                writer.writerow(run)            

if __name__ == '__main__':
    b = Blackjack()
    #b.run()
    b.write_file(1000, 10)