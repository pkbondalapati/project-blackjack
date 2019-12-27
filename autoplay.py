from blackjack import Blackjack
from table import Table
from player import Player
import random
import csv
import os
import copy
import sys
import time

class AutoPlay(Blackjack):
    def __init__(self, rounds, iterations):
        self.table = Table()
        self.rounds = rounds
        self.iterations = iterations
        self.shoe_size = 0
        self.count = 0
        self.run_output = []
        self.past_records = []
        self.bet_spreads = []
        self.gains = []
        self.performances = []
        self.index = 0

    # Initalizes bot to be added to the table as specified.
    def init_bot(self, name, money, bet, strategy):
        self.table.add_bot(name, money, bet, strategy)

    # Draws two cards for all the players.
    def start_round(self):
        for player in self.table.players:
            if player.name == 'Dealer':
                self.table.hit(player.name)
                self.table.hit(player.name)
            else:
                self.table.hit(player.name, false_draw=True)
                self.table.hit(player.name, false_draw=True)
        self.table.print_table()

    # Plays one iteration of a hit/stand round.
    def play_round(self):
        dealer = self.table.players[0]        
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
            
            self.run_strategy(player)

            if player.has_busted():
                player.inactive = True
                print('\n' + str(player.name) + ' has busted.')
            self.table.print_table()

    # Runs a game of Blackjack for a specified number of rounds.
    def run(self):
        for row in range(1):
            self.index = row
            performances = []
            gains = []
            for iteration in range(self.iterations):
                for i in range(self.rounds):
                    print('\nRound: ' + str(i+1))
                    self.start_round()
                    while len(self.table.active_players()) != 0:
                        self.play_round()
                    self.dealer_plays()
                    self.past_records = []
                    for player in self.table.players:
                        if player.name == 'Dealer':
                            self.past_records.append(None)
                        else:
                            record = copy.deepcopy(player.record)
                            self.past_records.append(record)
                    self.score_game()
                    self.record_round(i, iteration)
                    self.reset()
                
                for player in self.table.players:
                    if player.name == 'Biased-Bot':
                        if player.record['Wins'] == 0:
                                performance = 0
                        else:
                            performance = ((player.record['Losses']/player.record['Wins'])*player.record['Money'])/1000
                performances.append(performance)

                gain = self.table.players[2].record['Money'] - self.table.players[1].record['Money']
                gains.append(gain)

                table = Table()
                for bot in self.table.players:
                    if bot.name != 'Dealer':
                        table.add_bot(bot.name, 1000, 50, bot.strategy)
                self.table = table
            self.performances.append(performances)
            self.gains.append(gains)
            #self.write_round()
        #self.write_performances()
        #self.write_gains()
    
    # Empties the hand of each player on the table.
    def reset(self):
        self.table.remove_cards()
        for player in self.table.players:
            player.hand = []
            player.points = 0
            player.index = 0
            player.inactive = False
            player.surrendered = False
            player.soft = False
            if player.name != 'Dealer':
                player.bet = 50

    # Runs the specific strategy designated to the player.
    def run_strategy(self, player):
        if player.strategy == 1:
            response = self.dealers_strategy(player)
        elif player.strategy == 2:
            response = self.random_strategy(player)
        elif player.strategy == 3:
            response = self.basic_strategy(player)
        elif player.strategy == 4:
            response = self.biased_strategy(player)

        if response in ['hit', 'h', 'H']:
            self.table.hit(player.name, false_draw=True)
            print('\n' + str(player.name) + ' hits.')
        elif response in ['stand', 's', 'S']:
            self.table.stand(player.name)
            print('\n' + str(player.name) + ' stands.')
        elif response in ['double', 'd', 'D']:
            self.table.double(player.name, false_draw=True)
            print('\n' + str(player.name) + ' doubles.')
        elif response in ['surrender', 'u', 'U']:
            self.table.surrender(player.name)
            print('\n' + str(player.name) + ' surrendered.')
        elif response in ['split', 'p', 'P']:
            self.table.split(player.name, false_draw=True)
            print('\n' + str(player.name) + ' split.')

    # Follows the dealer's strategy for a given hand;
    # the decision to hit or stand at 16 is random.
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
        if len(self.table.shoe) > 312:
            true_count = self.table.running_count/((len(self.table.shoe) - 312)/52)
            self.shoe_size = len(self.table.shoe) - 312
        else:
            true_count = self.table.running_count/(len(self.table.shoe)/52)
            self.shoe_size = len(self.table.shoe)
        
        self.count = true_count
        
        bet_spread = self.bet_spreads[8]

        if len(self.table.shoe) < 260:
            for i in range(0, -10, -1):
                if true_count < -11:
                    player.bet = int(float(bet_spread[10]))
                elif true_count < i and true_count > (i - 1):
                    player.bet = int(float(bet_spread[abs(i)]))
                    break
            for i in range(10):
                if true_count > 11:
                    player.bet = int(float(bet_spread[21]))
                elif true_count > i and true_count < (i + 1):
                    player.bet = int(float(bet_spread[11+i]))
                    break
        else:
            player.bet = 5
        
        return self.basic_strategy(player)
    
    # Writes the records of all players to a .csv file.
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
        file_to_open = cwd+'\\blackjack_output_'+str(rounds)+'.csv'
        with open(file_to_open, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Iteration', 'Name', 'Wins', 'Losses', 'Draws', 'Money', 'Performance'])
            for run in run_output:
                writer.writerow(run)
    
    def record_round(self, round_num, iter_num):
        player_output = []
        dealer = self.table.players[0]
        for i in range(len(self.table.players)):
            player = self.table.players[i]
            if player.name != 'Dealer':
                player_output.append(iter_num+1)
                player_output.append(round_num+1)
                player_output.append(player.name)
                player_output.append(self.table.running_count)
                player_output.append(self.shoe_size)
                player_output.append(self.count)
                player_output.append(player.bet)
                player_output.append(player.get_hand())
                player_output.append(dealer.get_hand())
                player_output.append(player.points)
                player_output.append(dealer.points)
                player_output.append(len(player.hand))
                player_output.append(len(dealer.hand))
                record = self.past_records[i]
                player_output.append(player.record['Wins'] - record['Wins'])
                player_output.append(player.record['Losses'] - record['Losses'])
                player_output.append(player.record['Draws'] - record['Draws'])
                player_output.append(player.record['Money'] - record['Money'])
                player_output.append(player.record['Wins'])
                player_output.append(player.record['Losses'])
                player_output.append(player.record['Draws'])
                player_output.append(player.record['Money'])
                if player.record['Wins'] == 0:
                    performance = 0
                else:
                    performance = ((player.record['Losses']/player.record['Wins'])*player.record['Money'])/1000
                player_output.append(performance)
                self.run_output.append(player_output)
                player_output = []
    
    def write_round(self):
        cwd = os.getcwd()
        file_to_open = cwd+'\\blackjack_summary_'+str(self.rounds)+'.csv'
        with open(file_to_open, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Iteration', 'Round', 'Name', 'Running Count', 'Deck Size', 'True Count', 'Bet', 'Hand', 'Dealer Hand', 'Points', 'Dealer Points', 'Hand Size', 'Dealer Hand Size', 'Win', 'Loss', 'Draw', 'Money', 'Total Wins', 'Total Losses', 'Total Draws', 'Total Money', 'Performance'])
            for run in self.run_output:
                writer.writerow(run)
    
    def write_performances(self):
        cwd = os.getcwd()
        file_to_open = cwd+'\\blackjack_performances.csv'
        with open(file_to_open, 'w', newline='') as file:
            writer = csv.writer(file)
            #writer.writerow(['Performance'])
            for run in self.performances:
                writer.writerow(run)
    
    def write_gains(self):
        cwd = os.getcwd()
        file_to_open = cwd+'\\blackjack_gains.csv'
        with open(file_to_open, 'w', newline='') as file:
            writer = csv.writer(file)
            #writer.writerow(['Gains'])
            for run in self.gains:
                writer.writerow(run)
    
    def load_spreads(self):
        cwd = os.getcwd()
        file_to_open = cwd+'\\bet_spreads.csv'
        with open(file_to_open, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                bets = []
                for i in range(len(row)):
                    bets.append(row[i])
                self.bet_spreads.append(bets)
        self.bet_spreads.pop(0)
    
    def blockPrint(self):
        sys.stdout = open(os.devnull, 'w')
    
    def enablePrint(self):
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    start = time.time()
    ap = AutoPlay(60, 10000)
    #ap.blockPrint()
    ap.init_bot('Basic-Bot', 1000, 50, 3)
    ap.init_bot('Biased-Bot', 1000, 50, 4)
    ap.load_spreads()
    ap.run()
    #ap.enablePrint()
    print('%s seconds' %(time.time() - start))
