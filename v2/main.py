import random

class Card:
    type = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    weight = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def strength(self):
        return Card.weight[self.value]

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def __repr__(self):
        return self.__str__()

class Deck:
    def __init__(self):
        self.cards = []
        for suit in Card.type:
            for value in Card.weight:
                self.cards.append(Card(suit, value))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, players, cards_per_player):
        for _ in range(cards_per_player):
            for player in players:
                player.hand.append(self.cards.pop(0))

    def reveal_trump(self):
        if self.cards:
            top_card = self.cards.pop(0)
            if top_card.value == 'A':
                return None  # NO TRUMP rule
            return top_card.suit
        return None


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.bid = 0
        self.tricks = 0
        self.hand = []
        self.played_card = ""

    def place_bid(self):
        self.bid = int(input(f"\nHow much does {self.name} wanna bid? "))

    def play_card(self, leading_suit):
        choices = {}
        print(f"Remember, {leading_suit} lead")
        for i in range(len(self.hand)):
            choices[i+1] = self.hand[i]
        
        print(f"\n{choices}")
        play = int(input(f"\nWhich card would {self.name} like to play? "))
        
        suit_match = []
        for i in choices:
            suit_match.append(choices[i].suit)

        while leading_suit in suit_match and suit_match[play - 1] != leading_suit:
            print(f"{self.name} can still match the leading suit")
            play = int(input(f"\nWhich card would {self.name} like to play? "))

        self.played_card = self.hand.pop(play - 1)
        print(f"\n{self.name}'s new hand: {self.hand}")

    def round_reset(self):
        self.bid = 0
        self.tricks = 0
        self.hand = []

    def __str__(self):
        return f"\n{self.name}'s score is {self.score} {self.hand} "
    
    def __repr__(self):
        return self.__str__()
    

if __name__ == "__main__":
    #num_players = int(input("Please enter the number of players"))
    players  = [Player("Jake"), Player("Finn")]
    cards_per_player = 3

    """
    for _ in range(num_players):
        players.append(Player(input("Enter Name: ")))
    """

    deck = Deck()
    deck.deal(players, cards_per_player)

    trump = deck.reveal_trump()
    leading_suit = None
    winner  = ""

    for player in players:
        print(f"\n{player.name}'s hand: {player.hand}")
    
    """
    for player in players:
        player.bid = input(f"What is {player.name}'s bid? ")
    """

    if trump:
        print(f"\nTrump suit: {trump}")
    else:
        print(f"\nNO TRUMP")

    # Check point for later, 
    # - Determine which card wins based on the leading suit and trump
    # - you HAVE to match the leading_suit if you can
    # - trumps overrule all
    # - Update tricks won, update player score at the end

    for i in range(cards_per_player):
        for player in players:
            player.play_card(leading_suit)
            if leading_suit == None:
                leading_suit = player.played_card.suit
                print(f"\n{leading_suit} lead")
            

    for player in players:
        player.round_reset()
