# %%
import unittest

from sapai import *


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.pack = "StandardPack"

    def test_buy_three_animals(self):
        player = Player(pack=self.pack)
        player.buy_pet(player.shop[0])
        player.buy_pet(player.shop[0])
        player.buy_pet(player.shop[0])

    def test_buy_two_animals_one_food(self):
        player = Player(pack=self.pack)
        player.buy_pet(player.shop[0])
        player.buy_pet(player.shop[0])
        player.buy_food(player.shop[-1], player.team[0])
        player.sell(player.team[0])

    def test_freeze(self):
        player = Player(pack=self.pack)
        player.freeze(0)
        player.shop.roll()

    def test_unfreeze(self):
        player = Player(pack=self.pack)
        player.unfreeze(0)
        player.shop.roll()

    def test_buy_combine_behavior(self):
        player = Player(
            shop=["ant", "fish", "fish", "apple"], team=["fish", "ant"], pack=self.pack
        )
        player.buy_combine(player.shop[1], player.team[0])
        player.buy_combine(player.shop[1], player.team[0])

    def test_buy_combine_behavior2(self):
        player = Player(
            shop=["ant", "octopus", "octopus", "apple"],
            team=["octopus", "ant"],
            pack=self.pack,
        )
        player.buy_combine(player.shop[1], player.team[0])
        player.buy_combine(player.shop[1], player.team[0])

    def test_combine_behavior(self):
        player = Player(
            shop=["ant", "fish", "fish", "apple"],
            team=["fish", "fish", "fish", "horse"],
            pack=self.pack,
        )
        player.combine(player.team[0], player.team[1])
        player.combine(player.team[0], player.team[2])

    def test_cat_behavior(self):
        player = Player(
            shop=["ant", "fish", "fish", "pear"], team=["fish", "cat"], pack=self.pack
        )
        player.buy_food(player.shop[-1], player.team[0])

    def test_start_of_turn_behavior(self):
        player = Player(
            shop=["ant", "fish", "fish", "pear"],
            team=["dromedary", "swan", "caterpillar", "squirrel"],
            pack=self.pack,
        )
        player.team[0]._pet.level = 2
        player.start_turn()

    def test_sell_buy_behavior(self):
        player = Player(
            shop=["otter", "fish", "fish", "pear"],
            team=["pig", "fish", "ant", "beaver", "pig"],
            pack=self.pack,
        )
        player.sell_buy(0, 0)

    def test_pill_behavior(self):
        player = Player(
            shop=["ant", "fish", "fish", "food-sleeping-pill"],
            team=["rooster", "ant", "cricket", "sheep"],
            pack=self.pack,
        )
        player.buy_food(player.shop[-1], player.team[1])

    def test_multi_faints(self):
        player = Player(
            shop=["ant", "fish", "fish", "food-sleeping-pill"],
            team=["hedgehog", "ant", "ox", "sheep", "dragon"],
            pack=self.pack,
        )
        player.buy_food(player.shop[-1], player.team[0])

    def test_deer_microbe_shark(self):
        player = Player(
            shop=["ant", "fish", "fish", "food-sleeping-pill"],
            team=["deer", "microbe", "eagle", "shark"],
            pack=self.pack,
        )
        player.buy_food(player.shop[-1], player.team[2])

    def test_deer_badger_fly_sheep(self):
        player = Player(
            shop=["ant", "fish", "fish", "food-sleeping-pill"],
            team=["deer", "badger", "sheep", "fly"],
            pack=self.pack,
        )
        player.buy_food(player.shop[-1], player.team[1])


# %%
