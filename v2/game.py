from player import Player
from deck import Deck
import random

# Change this value to adjust the default maximum hand size used by the
# game. It's intentionally a single top-level constant so you can edit it
# quickly when you want a different default during testing or play.
DEFAULT_MAX_HANDS = 3

class Game:
    def __init__(self):
        self.players = {}  # conn: Player -> hand
        self.ready_players = set()
        self.min_players = 2
        self.deck = Deck()
        self.turn_order = []
        
        self.last_conn = None
        self.current_turn_index = 0
        # start with one card per player; will increment each round in reset()
        self.cards_per_player = 1
        self.max_cards = 0
        
        # lifecycle controls for dealing: when cards_per_player reaches the
        # computed max, play that size for `hold_rounds` additional rounds,
        # then enter decreasing phase where cards_per_player decreases by 1
        # each round until it reaches 0 (match over).
        self.hold_rounds = 3
        self.hold_rounds_remaining = None
        self.decreasing_phase = False
        self.match_over = False

        self.bids = {}
        self.bid_count = 0

        self.played_cards = {}

        self.game_started = False
        self.BID_PHASE = False
        self.PLAY_PHASE = False

        self.leading_suit = None
        self.trump = None

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

        # Compute maximum cards per player so that after dealing each player gets
        # the same number and one card remains to reveal trump.
        num_players = len(self.players)
        deck_size = len(self.deck.cards)
        computed_max = (deck_size - 1) // num_players if num_players > 0 else 0

        # Cap the default computed max to a reasonable play limit. Change
        # DEFAULT_MAX_HANDS at the top of this file to easily adjust the
        # default behavior for future sessions.
        self.max_cards = min(computed_max, DEFAULT_MAX_HANDS)

        self.deck.shuffle()
        self.deck.deal(list(self.players.values()), self.cards_per_player)

        self.turn_order = list(self.players.keys())
        random.shuffle(self.turn_order)
        self.current_turn_index = 0
        # Reveal trump from deck if any
        try:
            self.trump = self.deck.reveal_trump()
        except Exception:
            self.trump = None

    def place_bid(self, conn, bid):
        self.bids[conn] = bid
        self.bid_count += bid

            
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

    def get_last_player_conn(self):
        """Return the connection object for the last player in the turn order.

        Returns None if there is no turn order yet.
        """
        if not self.turn_order:
            return None
        return self.turn_order[-1]

    def advance_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def debug_state(self):
        print("Players:", [p.name for p in self.players.values()])
        print("Hands:", [p.hand for p in self.players.values()])
        print("Ready:", [self.players[c].name for c in self.ready_players])
        print("Turn order:", [self.players[c].name for c in self.turn_order])
        print("Current:", self.players[self.get_current_player_conn()].name)

    def reset(self):
        # Preserve player objects and connections, reset per-hand state
        for player in self.players.values():
            player.round_reset()

        self.ready_players = set()
        self.deck.refresh()
        self.turn_order = []
        self.last_conn = None
        self.current_turn_index = 0


        # Lifecycle transitions:
        if self.max_cards <= 0:
            # No cards can be dealt while leaving a trump card; match over
            self.cards_per_player = 0
            self.match_over = True
        elif not self.decreasing_phase:
            # Ramp up toward max_cards
            if self.cards_per_player < self.max_cards:
                self.cards_per_player += 1
            else:
                # We've reached or exceeded max; initialize hold counter if needed
                if self.hold_rounds_remaining is None:
                    self.hold_rounds_remaining = self.hold_rounds

                if self.hold_rounds_remaining > 0:
                    # Consume one of the hold rounds and remain at max
                    self.hold_rounds_remaining -= 1
                    self.cards_per_player = self.max_cards
                else:
                    # Finished holding at max -> begin decreasing next round
                    self.decreasing_phase = True
                    self.cards_per_player = self.max_cards - 1
        else:
            # Decreasing phase: reduce cards by one each round
            self.cards_per_player = self.cards_per_player - 1

        # If we've dropped to zero, the match is over
        if self.cards_per_player <= 0:
            self.match_over = True

        self.bids = {}
        self.bid_count = 0
        self.played_cards = {}

        self.game_started = False
        self.BID_PHASE = False
        self.PLAY_PHASE = False

        self.leading_suit = None
        self.trump = None