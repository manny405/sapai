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
        fish = Pet("fish")

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, fish.attack + 3)
        self.assertEqual(player.team[0].health, fish.health + 3)

        player.end_turn()
        player.start_turn()

        self.assertEqual(player.team[0].attack, fish.attack)
        self.assertEqual(player.team[0].health, fish.health)

    def test_apple(self):
        player = Player(shop=Shop(["apple"]), team=Team([Pet("beaver")]))

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 4)
        self.assertEqual(player.team[0].health, 3)

    def test_cake_in_food_data(self):
        cake = Food("cake")
        self.assertEqual(cake.name, "food-cake")
        self.assertEqual(cake.cost, 3)
        self.assertEqual(cake.fd["effect"]["status"], "status-cake")

    def test_cake_increases_sell_value_each_end_turn(self):
        player = Player(shop=Shop(["cake"]), team=Team([Pet("fish")]))

        player.buy_food(0, 0)
        self.assertEqual(player.gold, 7)
        self.assertEqual(player.team[0].pet.sell_value, 1)

        player.end_turn()
        self.assertEqual(player.team[0].pet.sell_value, 2)

        player.end_turn()
        self.assertEqual(player.team[0].pet.sell_value, 3)

        player.start_turn()
        player.sell(0)
        self.assertEqual(player.gold, 13)

    def test_sell_value_increases_on_level_up(self):
        player = Player(shop=Shop(["chocolate", "chocolate"]), team=Team([Pet("fish")]))
        self.assertEqual(player.team[0].pet.level, 1)
        self.assertEqual(player.team[0].pet.sell_value, 1)

        player.buy_food(0, 0)
        player.buy_food(0, 0)

        self.assertEqual(player.team[0].pet.level, 2)
        self.assertEqual(player.team[0].pet.sell_value, 2)

    def test_sell_value_level2_merge_to_level3(self):
        fish1 = Pet("fish")
        fish2 = Pet("fish")
        fish1.level = 2
        fish1.sell_value = 2
        fish2.level = 2
        fish2.sell_value = 2
        player = Player(team=Team([fish1, fish2]))

        player.combine(0, 1)
        self.assertEqual(player.team[0].pet.level, 3)
        self.assertEqual(player.team[0].pet.sell_value, 3)

    def test_combine_two_level1_pets_with_one_exp_each_keeps_level2_progress(self):
        fish1 = Pet("fish")
        fish2 = Pet("fish")
        fish1.experience = 1
        fish2.experience = 1
        player = Player(team=Team([fish1, fish2]))

        player.combine(0, 1)
        self.assertEqual(player.team[0].pet.level, 2)
        self.assertEqual(player.team[0].pet.experience, 1)
        self.assertEqual(player.team[0].pet.sell_value, 2)

    def _assert_combine_stat_bonus(self, flip_order=False):
        ant1 = Pet("ant")
        ant1.level = 1
        ant1.experience = 1
        ant1._attack = 3
        ant1._health = 3
        ant2 = Pet("ant")
        ant2.level = 2
        ant2.experience = 1
        ant2._attack = 5
        ant2._health = 5
        player = Player(team=Team([ant1, ant2]))

        if flip_order:
            player.combine(1, 0)
            combined = player.team[1].pet
        else:
            player.combine(0, 1)
            combined = player.team[0].pet

        self.assertEqual(combined.level, 3)
        self.assertEqual(combined.attack, 7)
        self.assertEqual(combined.health, 7)

    def _assert_combine_stat_bonus_over_leveled(self, flip_order=False):
        ant1 = Pet("ant")
        ant1.level = 1
        ant1.experience = 1
        ant1._attack = 3
        ant1._health = 3
        ant2 = Pet("ant")
        ant2.level = 2
        ant2.experience = 2
        ant2._attack = 6
        ant2._health = 6
        player = Player(team=Team([ant1, ant2]))

        if flip_order:
            player.combine(1, 0)
            combined = player.team[1].pet
        else:
            player.combine(0, 1)
            combined = player.team[0].pet

        self.assertEqual(combined.level, 3)
        self.assertEqual(combined.attack, 8)
        self.assertEqual(combined.health, 8)

    def _assert_combine_stat_bonus_both_pets_level_2(self, flip_order=False):
        ant1 = Pet("ant")
        ant1.level = 2
        ant1._attack = 4
        ant1._health = 4
        ant2 = Pet("ant")
        ant2.level = 2
        ant2._attack = 4
        ant2._health = 4
        player = Player(team=Team([ant1, ant2]))

        if flip_order:
            player.combine(1, 0)
            combined = player.team[1].pet
        else:
            player.combine(0, 1)
            combined = player.team[0].pet

        self.assertEqual(combined.level, 3)
        self.assertEqual(combined.attack, 7)
        self.assertEqual(combined.health, 7)

    def test_combine_stat_bonus(self):
        self._assert_combine_stat_bonus(flip_order=False)

    def test_combine_stat_bonus_flipped(self):
        self._assert_combine_stat_bonus(flip_order=True)

    def test_combine_stat_bonus_over_leveled(self):
        self._assert_combine_stat_bonus_over_leveled(flip_order=False)

    def test_combine_stat_bonus_over_leveled_flipped(self):
        self._assert_combine_stat_bonus_over_leveled(flip_order=True)

    def test_combine_stat_bonus_both_pets_level_2(self):
        self._assert_combine_stat_bonus_both_pets_level_2(flip_order=False)

    def test_combine_stat_bonus_both_pets_level_2_flipped(self):
        self._assert_combine_stat_bonus_both_pets_level_2(flip_order=True)


    def test_level3_combine_not_allowed(self):
        fish1 = Pet("fish")
        fish2 = Pet("fish")
        fish1.level = 3
        player = Player(team=Team([fish1, fish2]))

        with self.assertRaises(Exception):
            player.combine(0, 1)

    def test_level3_buy_combine_not_allowed(self):
        fish1 = Pet("fish")
        fish1.level = 3
        player = Player(shop=Shop(["fish"]), team=Team([fish1]))

        with self.assertRaises(Exception):
            player.buy_combine(0, 0)

    def test_cake_sell_value_with_end_turn_and_levelup(self):
        player = Player(
            shop=Shop(["cake", "chocolate", "chocolate"]),
            team=Team([Pet("fish")]),
        )

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.sell_value, 1)

        player.end_turn()
        self.assertEqual(player.team[0].pet.sell_value, 2)

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.level, 1)
        self.assertEqual(player.team[0].pet.sell_value, 2)

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.level, 2)
        self.assertEqual(player.team[0].pet.sell_value, 3)

        player.end_turn()
        self.assertEqual(player.team[0].pet.sell_value, 4)

    def test_shop_levelup_from_combine(self):
        player = Player(shop=Shop(["fish", "fish"]), team=Team([Pet("fish")]))
        player.buy_combine(1, 0)
        player.buy_combine(0, 0)
        self.assertEqual(len(player.shop), 2)

    def test_no_levelup_reward_from_level2_plus_level2_combine(self):
        fish1 = Pet("fish")
        fish2 = Pet("fish")
        fish1.level = 2
        fish2.level = 2
        player = Player(shop=Shop([]), team=Team([fish1, fish2]))

        levelup_slots = [s for s in player.shop.slots if s.slot_type == "levelup"]
        self.assertEqual(len(levelup_slots), 0)

        player.combine(0, 1)

        levelup_slots = [s for s in player.shop.slots if s.slot_type == "levelup"]
        self.assertEqual(player.team[0].pet.level, 3)
        self.assertEqual(len(levelup_slots), 0)

    def test_levelup_reward_choices_are_without_replacement(self):
        for _ in range(1000):
            shop = Shop([])
            shop.levelup()
            choices = [s.obj.name for s in shop.slots if s.slot_type == "levelup"]
            self.assertEqual(len(choices), 2)
            self.assertEqual(len(set(choices)), 2)

    def test_levelup_rewards_are_independent_between_events(self):
        found_overlap_between_reward_sets = False
        max_attempts = 1000

        for _ in range(max_attempts):
            shop = Shop(slots=[], fixed_rules=True)
            shop.levelup()
            shop.levelup()

            reward_names = [s.obj.name for s in shop.slots if s.slot_type == "levelup"]
            self.assertEqual(len(reward_names), 4)
            self.assertNotEqual(reward_names[0], reward_names[1])
            self.assertNotEqual(reward_names[2], reward_names[3])

            first_set = set(reward_names[:2])
            second_set = set(reward_names[2:])
            if len(first_set.intersection(second_set)) > 0:
                found_overlap_between_reward_sets = True
                break

        self.assertTrue(found_overlap_between_reward_sets)

    def test_shop_levelup_from_ability(self):
        pet = Pet("caterpillar")
        pet.level = 2
        pet.experience = 2
        player = Player(shop=Shop([]), team=Team([pet]))
        pet.sot_trigger()
        self.assertEqual(len(player.shop.filled), 6)

    def test_buy_multi_target_food(self):
        base_seal = Pet("seal")
        base_rabbit = Pet("rabbit")
        base_ladybug = Pet("ladybug")

        player = Player(shop=["sushi"], team=["seal", "rabbit", "ladybug"])
        player.buy_food(0)
        self.assertEqual(player.team[0].attack, base_seal.attack + 1)  # sushi
        self.assertEqual(player.team[0].health, base_seal.health + 1 + 1)  # sushi + rabbit
        self.assertEqual(player.team[1].attack, base_rabbit.attack + 1 + 1)  # sushi + seal
        self.assertEqual(player.team[1].health, base_rabbit.health + 1 + 1)  # sushi + rabbit
        self.assertEqual(player.team[2].attack, base_ladybug.attack + 1 + 1 + 1)  # sushi + ladybug + seal
        self.assertEqual(player.team[2].health, base_ladybug.health + 1 + 1 + 1)  # sushi + rabbit + ladybug

    def test_buy_multi_target_food_empty_team(self):
        player = Player(shop=["sushi"], team=[])
        player.buy_food(0)

    def test_buy_chocolate(self):
        base_seal = Pet("seal")
        base_rabbit = Pet("rabbit")
        base_ladybug = Pet("ladybug")

        player = Player(shop=["chocolate"], team=["seal", "rabbit", "ladybug"])
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.experience, 1)
        self.assertEqual(player.team[0].attack, base_seal.attack)
        self.assertEqual(player.team[0].health, base_seal.health + 1)  # rabbit
        self.assertEqual(player.team[1].attack, base_rabbit.attack + 1) #seal
        self.assertEqual(player.team[1].health, base_rabbit.health)
        self.assertEqual(player.team[2].attack, base_ladybug.attack + 1 + 1)  # ladybug + seal
        self.assertEqual(player.team[2].health, base_ladybug.health + 1)  # ladybug

    def test_buy_apple(self):
        base_seal = Pet("seal")
        base_rabbit = Pet("rabbit")
        base_ladybug = Pet("ladybug")

        player = Player(shop=["apple"], team=["seal", "rabbit", "ladybug"])
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, base_seal.attack + 1)  # apple
        self.assertEqual(player.team[0].health, base_seal.health + 1 + 1)  # apple + rabbit
        self.assertEqual(player.team[1].attack, base_rabbit.attack + 1) # seal
        self.assertEqual(player.team[1].health, base_rabbit.health)
        self.assertEqual(player.team[2].attack, base_ladybug.attack + 1 + 1)  # ladybug + seal
        self.assertEqual(player.team[2].health, base_ladybug.health + 1)  # ladybug

    def test_cow_replaces_food_shop_then_stocks_two_milk(self):
        player = Player(shop=Shop(["apple", "pear", "cow"]), team=Team())
        player.buy_pet(2)

        shop_food_names = [slot.obj.name for slot in player.shop.slots if slot.slot_type == "food"]
        self.assertNotIn("food-apple", shop_food_names)
        self.assertNotIn("food-pear", shop_food_names)
        self.assertEqual(shop_food_names.count("food-milk"), 2)

    def test_cow_stocked_milk_after_buy_combine_levelup(self):
        team_cow = Pet("cow")
        team_cow.level = 2
        team_cow.experience = 2
        shop_cow = Pet("cow")
        player = Player(shop=Shop([shop_cow]), team=Team([team_cow]))

        player.buy_combine(0, 0)
        self.assertEqual(player.team[0].pet.level, 3)

        milk_slots = [slot for slot in player.shop.slots if slot.obj.name == "food-milk"]
        self.assertEqual(len(milk_slots), 2)
        for slot in milk_slots:
            self.assertEqual(slot.cost, 0)
            self.assertEqual(slot.obj.attack, 3)
            self.assertEqual(slot.obj.health, 6)

    def test_pigeon_sell_stocks_bread_crumbs_by_level(self):
        for level, expected in [(1, 1), (2, 2), (3, 3)]:
            pigeon = Pet("pigeon")
            pigeon.level = level
            player = Player(shop=Shop(["apple"]), team=Team([pigeon]))

            player.sell(0)
            crumb_slots = [
                slot for slot in player.shop.slots if slot.slot_type == "food" and slot.obj.name == "food-bread-crumbs"
            ]
            self.assertEqual(len(crumb_slots), expected)
            for slot in crumb_slots:
                self.assertEqual(slot.cost, 0)

    def test_worm_start_turn_stocks_two_gold_apple_by_level(self):
        for level, expected in [(1, (1, 1)), (2, (2, 2)), (3, (3, 3))]:
            worm = Pet("worm")
            worm.level = level
            player = Player(shop=Shop(["fish"]), team=Team([worm]))

            activated, targets, _ = player.team[0].pet.sot_trigger()
            self.assertTrue(activated)
            self.assertEqual(len(targets), 1)

            stocked_slot = targets[0]
            self.assertEqual(stocked_slot.slot_type, "food")
            self.assertEqual(stocked_slot.obj.name, "food-apple")
            self.assertEqual(stocked_slot.cost, 2)
            self.assertEqual(stocked_slot.obj.attack, expected[0])
            self.assertEqual(stocked_slot.obj.health, expected[1])

    def test_bread_crumbs_buy_gives_plus_one_attack(self):
        player = Player(shop=Shop(["bread-crumbs"]), team=Team([Pet("fish")]))
        base_attack = player.team[0].pet.attack
        base_health = player.team[0].pet.health

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.attack, base_attack + 1)
        self.assertEqual(player.team[0].pet.health, base_health)

    def test_stock_shop_food_respects_capacity(self):
        player = Player(
            shop=Shop(
                [
                    "apple",
                    "pear",
                    "honey",
                    "cupcake",
                    "salad-bowl",
                ]
            ),
            team=Team([Pet("pigeon")]),
        )

        player.sell(0)
        self.assertEqual(len(player.shop.slots), 5)
        crumb_count = sum(1 for slot in player.shop.slots if slot.obj.name == "food-bread-crumbs")
        self.assertEqual(crumb_count, 0)

    def test_stock_shop_food_partial_capacity(self):
        pigeon = Pet("pigeon")
        pigeon.level = 3
        player = Player(
            shop=Shop(["apple", "pear", "honey", "cupcake"]),
            team=Team([pigeon]),
        )

        player.sell(0)
        food_count = sum(1 for slot in player.shop.slots if slot.slot_type == "food")
        self.assertEqual(food_count, 5)
        crumb_count = sum(
            1 for slot in player.shop.slots if slot.slot_type == "food" and slot.obj.name == "food-bread-crumbs"
        )
        self.assertEqual(crumb_count, 1)

    def test_shop_pet_cap_prevents_eighth_pet_slot(self):
        shop = Shop(["ant", "beaver", "cricket", "fish", "mosquito", "otter", "pig"])

        shop.append(Pet("horse"))

        self.assertEqual(sum(1 for slot in shop.slots if slot.slot_type in ["pet", "levelup"]), 7)
        self.assertNotIn("pet-horse", [slot.obj.name for slot in shop.slots if slot.slot_type == "pet"])

    def test_chicken(self):
        state = np.random.RandomState(seed=1).get_state()
        player = Player(shop=Shop(["fish", "fish"], seed_state=state), team=["chicken"])
        player.buy_pet(0)
        self.assertEqual(player.shop[0].obj.attack, player.shop[0].obj.fd["baseAttack"] + 1)
        self.assertEqual(player.shop[0].obj.health, player.shop[0].obj.fd["baseHealth"] + 1)

        ### check result after 1 roll
        player.roll()
        self.assertEqual(player.shop[0].obj.attack, player.shop[0].obj.fd["baseAttack"] + 1)
        self.assertEqual(player.shop[0].obj.health, player.shop[0].obj.fd["baseHealth"] + 1)

        ### check result in a new turn
        player.end_turn()
        player.start_turn()

        self.assertEqual(player.shop[0].obj.attack, player.shop[0].obj.fd["baseAttack"] + 1)
        self.assertEqual(player.shop[0].obj.health, player.shop[0].obj.fd["baseHealth"] + 1)

    def test_canned_food(self):
        state = np.random.RandomState(seed=1).get_state()
        player = Player(
            shop=Shop(["fish", "canned-food"], seed_state=state), team=["fish"]
        )
        player.buy_food(1)

        ### check immediate result
        self.assertEqual(player.shop[0].obj.attack, player.shop[0].obj.fd["baseAttack"] + 1)
        self.assertEqual(player.shop[0].obj.health, player.shop[0].obj.fd["baseHealth"] + 1)

        ### check result after 1 roll
        player.roll()
        self.assertEqual(player.shop[0].obj.attack, player.shop[0].obj.fd["baseAttack"] + 1)
        self.assertEqual(player.shop[0].obj.health, player.shop[0].obj.fd["baseHealth"] + 1)

        ### check result in a new turn
        player.end_turn()
        player.start_turn()
        self.assertEqual(player.shop[0].obj.attack, player.shop[0].obj.fd["baseAttack"] + 1)
        self.assertEqual(player.shop[0].obj.health, player.shop[0].obj.fd["baseHealth"] + 1)

    def test_canned_food_future_buff_applies_once_with_multiple_current_targets(self):
        state = np.random.RandomState(seed=1).get_state()
        player = Player(shop=Shop(["fish", "ant", "canned-food"], seed_state=state))

        player.buy_food(2)
        player.roll()

        for slot in player.shop.slots:
            if slot.slot_type != "pet":
                continue
            self.assertEqual(slot.obj.attack, slot.obj.fd["baseAttack"] + 1)
            self.assertEqual(slot.obj.health, slot.obj.fd["baseHealth"] + 1)

    def test_canned_food_future_buff_applies_when_no_current_shop_pets(self):
        state = np.random.RandomState(seed=1).get_state()
        player = Player(shop=Shop(["fish", "ant", "canned-food"], seed_state=state))

        player.buy_pet(0)
        player.buy_pet(0)
        player.buy_food(0)
        player.roll()

        for slot in player.shop.slots:
            if slot.slot_type != "pet":
                continue
            self.assertEqual(slot.obj.attack, slot.obj.fd["baseAttack"] + 1)
            self.assertEqual(slot.obj.health, slot.obj.fd["baseHealth"] + 1)


# %%
