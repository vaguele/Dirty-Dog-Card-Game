class Player:
    compare_by = ""
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.bid = 0
        self.tricks = 0
        self.power = 0
        self.hand = []
        self.played_card = ""
        self.tied = False

    #bids CANNOT equal number of cards in hand
    def place_bid(self):
        while True:
            try:
                self.bid = int(input(f"\nHow much does {self.name} wanna bid? "))
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

    def play_lead_card(self, trump):
        choices = {}
        for i in range(len(self.hand)):
            choices[i+1] = self.hand[i]
        print(f"\n{choices}")

        while True:
            try:
                play = int(input(f"\nWhich card would {self.name} like to play? "))
                if play > len(self.hand) or play < 1:
                    raise ValueError("Selected card not available")
                break
            except ValueError as e:
                print(f"Invalid Input: {e}")

        self.played_card = self.hand.pop(play - 1)
        print(f"\n{self.played_card} lead")

        if self.played_card.suit == trump:
            self.power = self.played_card.weight[self.played_card.value] + 50
        else:
            self.power = self.played_card.weight[self.played_card.value]
        return self.played_card.suit

    def play_card(self, leading_suit, trump):
        choices = {}
        print(f"Remember, {leading_suit} lead")
        for i in range(len(self.hand)):
            choices[i+1] = self.hand[i]
        
        suits_in_hand = []
        for i in choices:
            suits_in_hand.append(choices[i].suit) 

        print(f"\n{choices}")

        while True:
            try:
                play = int(input(f"\nWhich card would {self.name} like to play? "))
                if play > len(self.hand) or play < 1:
                    raise ValueError("Selected card not available")
                if leading_suit in suits_in_hand and suits_in_hand[play - 1] != leading_suit:
                    raise ValueError(f"{self.name} can still match the leading suit")
                break
            except ValueError as e:
                print(f"Invalid Input: {e}")

        self.played_card = self.hand.pop(play - 1)

        if self.played_card.suit == trump:
            self.power = self.played_card.weight[self.played_card.value] + 50
        elif self.played_card.suit == leading_suit:
            self.power = self.played_card.weight[self.played_card.value]
        else:
            self.power = 0

        print(f"\n{self.name}'s new hand: {self.hand}")
        print(f"{self.name}'s power is: {self.power}")

    def play_overtime_card(self):
        choices = {}
        for i in range(len(self.hand)):
            choices[i+1] = self.hand[i]
        
        suits_in_hand = []
        for i in choices:
            suits_in_hand.append(choices[i].suit) 

        print(f"\n{choices}")

        while True:
            try:
                play = int(input(f"\nWhich card would {self.name} like to play? "))
                if play > len(self.hand) or play < 1:
                    raise ValueError("Selected card not available")
                break
            except ValueError as e:
                print(f"Invalid Input: {e}")

        self.played_card = self.hand.pop(play - 1)
        self.power = self.played_card.weight[self.played_card.value]

        print(f"\n{self.name}'s new hand: {self.hand}")
        print(f"{self.name}'s power is: {self.power}")

    def round_reset(self):
        self.bid = 0
        self.tricks = 0
        self.power = 0
        self.hand = []
        self.played_card = ""

    def game_reset(self):
        self.score = 0
        self.tied = False

    def __str__(self):
        return f"\n{self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other):
        if Player.compare_by == "score":
            return self.score < other.score
        elif Player.compare_by == "power":
            return self.power < other.power
        else:
            raise ValueError("Unknown comparison type")