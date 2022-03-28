import unittest

from sapai import *


class BrokenTests(unittest.TestCase):

    def test_cricket_pill_in_shop_with_turkey(self):
        player = Player(shop=Shop(["sleeping-pill"]), team=Team([Pet("cricket"), Pet("turkey")]))
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 4)
        self.assertEqual(player.team[0].health, 4)


    def test_cricket_pill_in_shop_with_horse(self):
        player = Player(shop=Shop(["sleeping-pill"]), team=Team([Pet("cricket"), Pet("horse")]))
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 2)