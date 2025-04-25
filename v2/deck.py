from card import Card
import random

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
    
    def refresh(self):
        self.cards = []
        for suit in Card.type:
            for value in Card.weight:
                self.cards.append(Card(suit, value))
        self.shuffle()