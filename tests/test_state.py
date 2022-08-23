import unittest

from sapai import *
from sapai.shop import *
from sapai.compress import *


# TODO : In most tests, assert states are equal once `__eq__` is implemented for classes
class TestState(unittest.TestCase):
    def test_pet_level_state(self):
        expected_level = 3
        p = Pet("ant")
        p.level = expected_level
        pet_from_state = Pet.from_state(p.state)
        self.assertEqual(pet_from_state.level, expected_level)

    def test_food_from_state(self):
        expected_food = Food("melon")
        actual_food = Food.from_state(expected_food.state)

    def test_team_from_state(self):
        expected_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])
        expected_level = 3
        expected_team[0].pet.level = expected_level
        actual_team = Team.from_state(expected_team.state)
        self.assertEqual(actual_team[0].pet.level, expected_level)

    def test_shop_slot_state(self):
        actual = ShopSlot("pet")
        actual.roll()
        expected = ShopSlot.from_state(actual.state)

    def test_shop_state(self):
        actual = Shop()
        expected = Shop.from_state(actual.state)

    def test_player_state(self):
        expected = Player(team=Team(["ant", "fish", "dragon"]))
        actual = Player.from_state(expected.state)

    def test_compress_shop(self):
        expected = Shop()
        compressed = compress(expected, minimal=True)
        actual = decompress(compressed)

    def test_shop_state_equality(self):
        expected = Shop()
        actual = Shop.from_state(expected.state)
        self.assertEqual(expected.state, actual.state)

    def test_compress_player(self):
        expected = Player()
        compressed = compress(expected, minimal=True)
        actual = decompress(compressed)
