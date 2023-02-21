# %%
import unittest

from sapai import Player, Team
from sapai.shop import *


class TestShop(unittest.TestCase):
    def test_shop_slot_pet(self):
        slot = ShopSlot("pet")
        slot.obj = Pet("ant")
        slot.roll()
        self.assertIsInstance(slot.obj, Pet)

    def test_shop_slot_food(self):
        slot = ShopSlot("food")
        slot.obj = Food("apple")
        slot.roll()
        self.assertIsInstance(slot.obj, Food)

    def test_shop_level_up(self):
        slot = ShopSlot("levelup")
        tier = slot.obj.tier
        self.assertEqual(tier, 2)

    def test_max_shop(self):
        s = Shop(turn=11)
        s.freeze(0)
        ref_state = s[0].state
        for index in range(10):
            s.roll()
        self.assertEqual(ref_state, s[0].state)

    def test_rabbit_buy_food(self):
        test_player = Player(shop=["honey"], team=["rabbit"])
        start_health = 2
        self.assertEqual(test_player.team[0].pet.health, start_health)

        test_player.buy_food(0, 0)
        expected_end_health = start_health + 1
        self.assertEqual(test_player.team[0].pet.health, expected_end_health)

    def test_empty_shop_from_state(self):
        pet = Pet("fish")
        orig_shop = Shop(slots=[pet])
        orig_shop.buy(pet)
        self.assertEqual(len(orig_shop.slots), 0)

        copy_shop = Shop.from_state(orig_shop.state)
        self.assertEqual(len(copy_shop.slots), 0)

    def test_combine_scorpions(self):
        player = Player(team=["scorpion", "scorpion"])
        player.combine(0, 1)

    def test_combine_coconut_shield(self):
        gorilla = Pet("gorilla")
        gorilla.status = "status-coconut-shield"
        gorilla2 = Pet("gorilla")
        gorilla2.status = "status-melon-armor"
        player = Player(team=[gorilla, gorilla2])
        player.combine(1, 0)
        self.assertEqual(
            gorilla.status, "status-coconut-shield"
        )  # same priority, therefore pet-to-keep keeps its status

    def test_squirrel(self):
        player = Player(team=Team([Pet("squirrel")]))
        player.start_turn()
        self.assertEqual(player.shop[3].cost, 2)

        player.roll()
        self.assertEqual(player.shop[3].cost, 3)

    def test_pill_1gold(self):
        player = Player(shop=Shop(["sleeping-pill"]), team=Team(["fish"]))
        player.buy_food(0, 0)
        self.assertEqual(player.gold, 9)

    def test_cupcake(self):
        player = Player(shop=Shop(["cupcake"]), team=Team([Pet("fish")]))

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 5)  # fish 2/2
        self.assertEqual(player.team[0].health, 5)

        player.end_turn()
        player.start_turn()

        self.assertEqual(player.team[0].attack, 2)
        self.assertEqual(player.team[0].health, 2)

    def test_apple(self):
        player = Player(shop=Shop(["apple"]), team=Team([Pet("beaver")]))

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 4)
        self.assertEqual(player.team[0].health, 3)

    def test_shop_levelup_from_combine(self):
        player = Player(shop=Shop(["fish", "fish"]), team=Team([Pet("fish")]))
        player.buy_combine(1, 0)
        player.buy_combine(0, 0)
        self.assertEqual(len(player.shop), 1)

    def test_shop_levelup_from_ability(self):
        pet = Pet("caterpillar")
        pet.level = 2
        pet.experience = 2
        player = Player(shop=Shop([]), team=Team([pet]))
        pet.sot_trigger()
        self.assertEqual(len(player.shop.filled), 5)

    def test_buy_multi_target_food(self):
        player = Player(shop=["sushi"], team=["seal", "rabbit", "ladybug"])
        player.buy_food(0)
        self.assertEqual(player.team[0].attack, 4)  # 3 + sushi
        self.assertEqual(player.team[0].health, 10)  # 8 + sushi + rabbit
        self.assertEqual(player.team[1].attack, 3)  # 1 + sushi + seal
        self.assertEqual(player.team[1].health, 5)  # 2 + sushi + seal + rabbit
        self.assertEqual(player.team[2].attack, 4)  # 1 + sushi + seal + ladybug
        self.assertEqual(
            player.team[2].health, 7
        )  # 3 + sushi + seal + rabbit + ladybug

    def test_buy_multi_target_food_empty_team(self):
        player = Player(shop=["sushi"], team=[])
        player.buy_food(0)

    def test_buy_chocolate(self):
        player = Player(shop=["chocolate"], team=["seal", "rabbit", "ladybug"])
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.experience, 1)
        self.assertEqual(player.team[0].attack, 3)  # 3
        self.assertEqual(player.team[0].health, 9)  # 8 + rabbit
        self.assertEqual(player.team[1].attack, 2)  # 1 + seal
        self.assertEqual(player.team[1].health, 3)  # 2 + seal
        self.assertEqual(player.team[2].attack, 3)  # 1 + seal + ladybug
        self.assertEqual(player.team[2].health, 5)  # 3 + seal + ladybug

    def test_buy_apple(self):
        player = Player(shop=["apple"], team=["seal", "rabbit", "ladybug"])
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 4)  # 3 + apple
        self.assertEqual(player.team[0].health, 10)  # 8 + apple + rabbit
        self.assertEqual(player.team[1].attack, 2)  # 1 + seal
        self.assertEqual(player.team[1].health, 3)  # 2 + seal
        self.assertEqual(player.team[2].attack, 3)  # 1 + seal + ladybug
        self.assertEqual(player.team[2].health, 5)  # 3 + seal + ladybug

    def test_chicken(self):
        state = np.random.RandomState(seed=1).get_state()
        player = Player(shop=Shop(["fish", "fish"], seed_state=state), team=["chicken"])
        player.buy_pet(0)
        self.assertEqual(player.shop[0].obj.attack, 3)  # fish 2/2
        self.assertEqual(player.shop[0].obj.health, 3)

        ### check result after 1 roll
        player.roll()
        self.assertEqual(player.shop[0].obj.attack, 3)  # duck 2/3
        self.assertEqual(player.shop[0].obj.health, 4)

        ### check result in a new turn
        player.end_turn()
        player.start_turn()

        self.assertEqual(player.shop[0].obj.attack, 3)  # mosquito 2/2
        self.assertEqual(player.shop[0].obj.health, 3)

    def test_canned_food(self):
        state = np.random.RandomState(seed=1).get_state()
        player = Player(
            shop=Shop(["fish", "canned-food"], seed_state=state), team=["fish"]
        )
        player.buy_food(1)

        ### check immediate result
        self.assertEqual(player.shop[0].obj.attack, 4)  # fish 2/2
        self.assertEqual(player.shop[0].obj.health, 3)

        ### check result after 1 roll
        player.roll()
        self.assertEqual(player.shop[0].obj.attack, 4)  # duck 2/3
        self.assertEqual(player.shop[0].obj.health, 4)

        ### check result in a new turn
        player.end_turn()
        player.start_turn()
        self.assertEqual(player.shop[0].obj.attack, 4)  # mosquito 2/2
        self.assertEqual(player.shop[0].obj.health, 3)


# %%
