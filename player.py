class Player:
    def __init__(self, name, money):
        self.hand = []
        self.points = 0
        self.bet = 0
        self.index = 0
        self.name = name
        self.bot = False
        self.inactive = False
        self.surrendered = False
        self.strategy = 0
        self.record = {'Wins': 0, 'Losses': 0, 'Draws': 0, 'Money': money}
        self.split_record = None
    
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
    
    # Checks if the player's hand is hard.
    def is_hard(self):
        points = self.points
        for card in self.hand:
            if card.value != 'A':
                points -= card.get_numerical_value()
        if points >= 11 and not self.has_blackjack():
            return False
        else:
            return True
    
    # Checks if the player has no more money.
    def is_broke(self):
        if self.record['Money'] == 0:
            return True
        else:
            return False
    
    # Checks if the player has an eligible hand to split.
    def can_split(self):
        if len(self.hand) == 2 and self.hand[0].value == self.hand[1].value:
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
    
    # Returns a string of the player's hand
    def get_hand(self):
        hand = []
        for card in self.hand:
            hand.append(str(card))
        return str(hand)
    
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
        self.index = 0
        self.bot = False
        
    # Checks if dealer can offer insurance. 
    def can_offer_insurance(self):
        if len(self.hand) == 2 and self.hand[1].value == 'A':
            return True
        else:
            return False