import unittest
from unittest.mock import patch
from deck import Deck
from player import Player

class TestCase(unittest.TestCase):
    @patch('builtins.input', return_value='3')
    # This tells Python: “Whenever input() is called during this test, return '3'.”

    def test_bid_placement(self, mock_input):
        player = Player("Player 1")
        player.place_bid()
        self.assertEqual(player.bid, 3)
    def test_card_play(self):
        pass