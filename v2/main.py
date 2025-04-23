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
        self.power = 0
        self.hand = []
        self.played_card = ""

    def place_bid(self):
        self.bid = int(input(f"\nHow much does {self.name} wanna bid? "))

    def play_card(self, leading_suit, trump):
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

        if self.played_card.suit == trump:
            self.power = self.played_card.weight[self.played_card.value] + 50
        elif self.played_card.suit == leading_suit:
            self.power = self.played_card.weight[self.played_card.value]
        else:
            self.power = 0

        print(f"\n{self.name}'s new hand: {self.hand}")

    def round_reset(self):
        self.bid = 0
        self.tricks = 0
        self.power = 0
        self.hand = []
        self.played_card = ""

    def __str__(self):
        return f"\n{self.name}'s score is {self.score} {self.hand}"
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other):
        return self.power < other.power

if __name__ == "__main__":
    players = []
    num_players = int(input("Please enter the number of players"))

    for _ in range(num_players):
        players.append(Player(input("Enter Name: ")))

    deck = Deck()
    max_cards = len(deck.cards) // num_players
    cards_per_player = 3
    deck.deal(players, cards_per_player)

    trump = deck.reveal_trump()

    for player in players:
        print(f"\n{player.name}'s hand: {player.hand}")

    for player in players:
        player.place_bid()

    if trump:
        print(f"\nTrump suit: {trump}")
    else:
        print(f"\nNO TRUMP")

    """
    1. Multiple Rounds Support

        - Start with 1 card/player, go up to a max (e.g., 5), then back down to 1

        - Track the full game, not just one round
        
        while cards_per_player != max_cards:
            cards_per_player += 1

        remember to pause at the max cards for a bit, maybe 5 turns
            
        while cards_per_player != 0:
            cards_per_player -= 1

    3. Bid Rule Enforcement

        - Last bidder can't make total bids equal to number of cards dealt


    5. Replay Option

        - Ask if players want to play another game

    6. Alternate who leads every round
    """

    for i in range(cards_per_player):
        leading_suit = None
        for player in players:
            player.play_card(leading_suit, trump)
            if leading_suit == None:
                leading_suit = player.played_card.suit
                print(f"\n{leading_suit} lead")
        print(f"\n----{max(players).name} takes the trick")  
        max(players).tricks += 1
    
    for player in players:
        if player.bid == player.tricks:
            player.score += player.bid + 5
        else:
            player.score -= max(player.bid, player.tricks)
        print(f"{player.name}'s current score is {player.score}")
        player.round_reset()
    
