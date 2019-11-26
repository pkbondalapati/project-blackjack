from table import Table

class Blackjack:
    def __init__(self):
        self.table = Table()
        self.rounds = 0
    
    # Lists the general rules of Blackjack.
    # Adds players to the table as specified. 
    def setup(self):
        print('Welcome to Blackjack!')
        print('Dealer must draw until 16 and soft 17')
        print('Dealer must stand on 17')
        print('Blackjack pays 3 to 2')
        print('Insurance pays 2 to 1')
        print('Minimum bet is $10')

        print('What is the buy-in? (e.g. 1000)')
        money = input()
        print('How many players?')
        count = input()
        print('How many rounds do you want to play?')
        rounds = input()
        self.rounds = int(rounds)
        
        for i in range(int(count)):
            print('What is player ' + str(i+1) + '\'s name?')
            name = input()
            self.table.add_player(name, int(money))
    
    # Takes bets from the round
    def place_bets(self):
        for player in self.table.players:
            print('Place your bet, ' + str(player.name) + '?')
            bet = input()
            if int(bet) < 10:
                print('Minimum bet is $10')
                print('Would you like to continue playing? (y/n)')
                reponse = input()
            player.bet = int(bet)

    # Runs a game of Blackjack for a specified number of rounds.
    def run(self):
        for i in range(self.rounds):
            self.place_bets()



    # Empties the hand of each player on the table.
    def reset(self):
        for player in self.table.players:
            player.hand = []
            player.points = 0
    
    def score(self):
        #TODO:
        pass

    def dealer(self):
        #TODO:
        pass