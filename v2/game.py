from player import Player
from deck import Deck
import random

class Game:
    def __init__(self):
        self.players = {}  # conn: Player
        self.ready_players = set()
        self.min_players = 2
        self.game_started = False
        self.deck = Deck()
        self.turn_order = []
        self.current_turn_index = 0
        self.bids = {}

    def add_player(self, conn, name):
        self.players[conn] = Player(name)

    def remove_player(self, conn):
        if conn in self.players:
            del self.players[conn]
        if conn in self.ready_players:
            self.ready_players.remove(conn)
        if conn in self.turn_order:
            self.turn_order.remove(conn)

    def mark_ready(self, conn):
        self.ready_players.add(conn) 
        return (
            len(self.players) >= self.min_players
            and len(self.ready_players) == len(self.players)
        )
    
    def start_game(self):
        self.game_started = True
        self.deck.shuffle()
        self.deck.deal(list(self.players.values()), cards_per_player=3)

        self.turn_order = list(self.players.keys())
        random.shuffle(self.turn_order)
        self.current_turn_index = 0

    def place_bid(self, conn, bid):
        self.bids[conn] = bid

            
    def build_hands(self):
        hands = {}
        for conn, player in self.players.items():
            hand_str = ', '.join(str(card) for card in player.hand)
            hands[conn] = f"Your hand: {hand_str}"
        return hands

    def get_current_player_conn(self):
        return self.turn_order[self.current_turn_index]
    
    def is_player_turn(self, conn):
        return conn == self.get_current_player_conn()

    def advance_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def debug_state(self):
        print("Players:", [p.name for p in self.players.values()])
        print("Ready:", [self.players[c].name for c in self.ready_players])
        print("Turn order:", [self.players[c].name for c in self.turn_order])
        print("Current:", self.players[self.get_current_player_conn()].name)

    def reset(self):
        self.__init__()  # Simple reset