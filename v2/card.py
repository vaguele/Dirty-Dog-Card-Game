class Card:
    type = ['♥', '♦', '♣', '♠']
    weight = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def strength(self):
        return Card.weight[self.value]

    def __str__(self):
        return f"{self.value}{self.suit}"

    def __repr__(self):
        return self.__str__()