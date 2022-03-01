import unittest

from sapai import *
from sapai.shop import *


class TestShop(unittest.TestCase):

    def test_shop_slot_pet(self):
        slot = ShopSlot("pet")
        slot.item = Pet("ant")
        slot.roll()
        self.assertIsInstance(slot.item, Pet)

    def test_shop_slot_food(self):
        slot = ShopSlot("food")
        slot.item = Food("apple")
        slot.roll()
        self.assertIsInstance(slot.item, Food)

    def test_shop_level_up(self):
        slot = ShopSlot("levelup")
        tier = slot.item.tier
        self.assertEqual(tier, 2)

    def test_max_shop(self):
        s = Shop(turn=11)
        s.freeze(0)
        for index in range(10):
            s.roll()

    def test_rabbit_buy_food(self):
        test_player = Player(shop=["honey"], team=["rabbit"])
        start_health = 2
        self.assertEqual(test_player.team[0].pet.health, start_health)

        test_player.buy_food(0, 0)
        expected_end_health = start_health + 1
        self.assertEqual(test_player.team[0].pet.health, expected_end_health)

    def test_empty_shop_from_state(self):
        pet = Pet("fish")
        orig_shop = Shop(shop_slots=[pet])
        orig_shop.buy(pet)
        self.assertEqual(len(orig_shop.shop_slots), 0)

        copy_shop = Shop.from_state(orig_shop.state)
        self.assertEqual(len(copy_shop.shop_slots), 0)

    def test_combine_scorpions(self):
        player = Player(team=["scorpion", "scorpion"])
        player.combine(0, 1)