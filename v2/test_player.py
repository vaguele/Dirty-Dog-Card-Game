import unittest
from unittest.mock import patch
from player import Player

# how to run: python3 -m unittest test_player.py

class TestPlayer(unittest.TestCase):
    # Test that a player's bid is recorded correctly.
    @patch('builtins.input', return_value='3')
    def test_place_bid(self, mock_input):
        player = Player("TestPlayer")
        player.place_bid()
        self.assertEqual(player.bid, 3)
        self.assertEqual(Player.total_bids, 3)
    
    # Test that the last player can't make total bids equal tricks available.
    @patch('builtins.input', side_effect=['2', '1'])
    def test_place_last_bid_rejects_invalid_total(self, mock_inputs):
        player = Player("TestPlayer")
        player.hand = [1, 2, 3]  # 3 cards in hand

        # First input is '2' -> will make total_bids 2
        Player.total_bids = 1
        player.place_last_bid()
        self.assertNotEqual(player.bid + Player.total_bids, 3)

    # Test that a lead card gains +50 if it matches the trump suit.
    @patch('builtins.input', return_value='1')
    def test_play_lead_card_trump(self, mock_input):
        player = Player("TestPlayer")
        class Card:
            suit = "Hearts"
            value = "A"
            weight = {"A": 14}
        player.hand = [Card()]
        trump = "Hearts"
        suit_played = player.play_lead_card(trump)
        self.assertEqual(player.strength, 64)  # 14 + 50 because it's trump
        self.assertEqual(suit_played, "Hearts")
    
    # Test a player following the leading suit.
    @patch('builtins.input', return_value='1')
    def test_play_card_follow_suit(self, mock_input):
        player = Player("TestPlayer")
        class Card:
            suit = "Spades"
            value = "10"
            weight = {"10": 10}
        player.hand = [Card()]
        player.play_card("Spades", "Hearts")
        self.assertEqual(player.strength, 10)

    # After a round, all player states (hand, bid, tricks, strength) are reset.
    def test_round_reset(self):
        player = Player("TestPlayer")
        player.bid = 5
        player.tricks = 3
        player.strength = 99
        player.hand = [1,2,3]
        Player.total_bids = 7

        player.round_reset()

        self.assertEqual(player.bid, 0)
        self.assertEqual(player.tricks, 0)
        self.assertEqual(player.strength, 0)
        self.assertEqual(player.hand, [])
        self.assertEqual(Player.total_bids, 0)

if __name__ == "__main__":
    unittest.main()
