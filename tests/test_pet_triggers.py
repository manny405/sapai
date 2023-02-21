# %%
import unittest
import numpy as np
from torch import seed

from sapai import *
from sapai.compress import compress, decompress


class TestPetTriggers(unittest.TestCase):
    @staticmethod
    def print_pet_list(pet_list):
        n = []
        trigger_list = []
        triggerby_list = []
        effect_kind_list = []
        effect_target_kind_list = []
        for iter_idx, pet in enumerate(pet_list):
            n.append(iter_idx)
            trigger_list.append(pet.ability["trigger"])
            triggerby_list.append(pet.ability["triggeredBy"]["kind"])
            effect_kind_list.append(pet.ability["effect"]["kind"])
            if "target" in pet.ability["effect"]:
                effect_target_kind_list.append(pet.ability["effect"]["target"]["kind"])
            else:
                effect_target_kind_list.append("NONE")

        str_fmt = "{:3s}{:20s}{:15s}{:15s}{:20s}{:20s}\n"
        print_str = str_fmt.format(
            "N", "Pet", "Trigger", "TriggerBy", "EffectKind", "EffectTarget"
        )
        print_str += "-------------------------------------------------------------------------------\n"
        for iter_idx in range(len(pet_list)):
            print_str += str_fmt.format(
                str(n[iter_idx]),
                pet_list[iter_idx].name,
                trigger_list[iter_idx],
                triggerby_list[iter_idx],
                effect_kind_list[iter_idx],
                effect_target_kind_list[iter_idx],
            )

        print(print_str)

    def test_start_of_turn_triggers(self):
        test_pet_names = ["dromedary", "swan", "caterpillar", "squirrel"]
        test_pet_list = [
            Pet(x, shop=Shop(), team=Team(), player=Player()) for x in test_pet_names
        ]
        caterpillar = Pet("hatching-chick", shop=Shop(), team=Team(), player=Player())
        caterpillar.level = 3
        test_pet_list.append(caterpillar)
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.sot_trigger()
            self.assertTrue(activated_bool)

    def test_sell_triggers_self(self):
        test_team = Team([Pet("dragon"), Pet("cat"), Pet("horse")])

        test_pet_names = ["beaver", "duck", "pig", "shrimp", "owl"]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Sell Self
        test_bool_list = [True, True, True, False, True]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.sell_trigger(pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_sell_triggers_other(self):
        test_team = Team([Pet("dragon"), Pet("cat"), Pet("horse")])
        test_pet_names = ["beaver", "duck", "pig", "shrimp", "owl"]

        # Sell Other
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy()) for x in test_pet_names
        ]
        test_bool_list = [False, False, False, True, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.sell_trigger(pet.team[0].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_eats_shop_food_triggers_self(self):
        test_team = Team([Pet("dragon"), Pet("cat")])
        test_pet_names = ["beetle", "tabby-cat", "rabbit", "worm", "seal"]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Buy food for self
        for pet in test_pet_list:
            activated_bool, targets, possible = pet.eats_shop_food_trigger(pet)
            self.assertTrue(activated_bool)

    def test_eats_shop_food_triggers_other(self):
        test_team = Team([Pet("dragon"), Pet("cat")])
        test_pet_names = ["beetle", "tabby-cat", "rabbit", "worm", "seal"]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]

        # Buy food for other
        test_bool_list = [False, False, True, False, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.eats_shop_food_trigger(
                pet.team[0].pet
            )
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_food_triggers_self(self):
        test_team = Team([Pet("dragon"), Pet("cat")])
        test_pet_names = ["ladybug", "sauropod"]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Buy food for self
        for pet in test_pet_list:
            activated_bool, targets, possible = pet.buy_food_trigger(pet)
            self.assertTrue(activated_bool)

    def test_buy_food_triggers_other(self):
        test_team = Team([Pet("dragon"), Pet("cat")])
        test_pet_names = ["ladybug", "sauropod"]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]

        # Buy food for other
        test_bool_list = [True, True]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_food_trigger(pet.team[0].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_friend_triggers_self(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = [
            "otter",
            "crab",
            "snail",
            "buffalo",
            "chicken",
            "cow",
            "goat",
            "dragon",
        ]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Buy friend as self
        test_bool_list = [True, False, True, False, False, True, False, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_friend_trigger(pet)
            if pet.name == "pet-snail":
                continue
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_friend_triggers_self_other_tier_1(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = [
            "otter",
            "crab",
            "snail",
            "buffalo",
            "chicken",
            "cow",
            "goat",
            "dragon",
        ]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Buy other friend tier1
        test_bool_list = [False, False, False, True, True, False, True, True]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_friend_trigger(pet.team[0].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_friend_triggers_self_other_not_tier_1(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = [
            "otter",
            "crab",
            "snail",
            "buffalo",
            "chicken",
            "cow",
            "goat",
            "dragon",
        ]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Buy other friend not tier1
        test_bool_list = [False, False, False, True, False, False, True, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_friend_trigger(pet.team[1].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_friend_summoned_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["horse", "dog", "lobster", "turkey"]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.friend_summoned_trigger(
                pet.team[0].pet
            )
            self.assertTrue(activated_bool)

    def test_levelup_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["fish", "octopus"]
        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.levelup_trigger(pet.team[0].pet)
            self.assertTrue(activated_bool)

    def test_end_of_turn_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])
        test_team[0].pet.level = 3
        test_player = Player()

        test_pet_names = [
            "bluebird",
            "hatching-chick",
            "giraffe",
            "puppy",
            "tropical-fish",
            "bison",
            "llama",
            "penguin",
            "parrot",
            "monkey",
            "poodle",
            "tyrannosaurus",
        ]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=test_player)
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.eot_trigger(pet.team[0].pet)
            self.assertTrue(activated_bool)

    def test_faint_triggers_self(self):
        test_team = Team([Pet("fish")], battle=True)
        test_pet_names = [
            "ant",
            "cricket",
            "flamingo",
            "hedgehog",
            "spider",
            "badger",
            "ox",
            "sheep",
            "turtle",
            "deer",
            "rooster",
            "microbe",
            "eagle",
            "shark",
            "fly",
            "mammoth",
        ]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        # Self faint
        test_bool_list = [
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            True,
        ]
        for iter_idx, pet in enumerate(test_pet_list):
            pet.team.append(Pet("tiger"))
            te_idx = [0, pet.team.index(pet)]
            activated_bool, targets, possible = pet.faint_trigger(pet, te_idx)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_faint_triggers_self_friend_in_front(self):
        test_team = Team([Pet("fish")], battle=True)
        test_pet_names = [
            "ant",
            "cricket",
            "flamingo",
            "hedgehog",
            "spider",
            "badger",
            "ox",
            "sheep",
            "turtle",
            "deer",
            "rooster",
            "microbe",
            "eagle",
            "shark",
            "fly",
            "mammoth",
        ]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        test_bool_list = [
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            False,
        ]
        for iter_idx, pet in enumerate(test_pet_list):
            pet.team.append(Pet("tiger"))
            friend_ahead = pet.team.get_ahead(pet)[0]
            te_idx = [0, pet.team.index(friend_ahead)]
            activated_bool, targets, possible = pet.faint_trigger(friend_ahead, te_idx)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_start_of_battle_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")], battle=True)
        cteam = compress(test_team)
        test_pet_names = [
            "mosquito",
            "bat",
            "crab",
            "whale",
            "dolphin",
            "skunk",
            "crocodile",
            "leopard",
        ]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        caterpillar = Pet(
            "caterpillar", shop=Shop(), team=test_team.copy(), player=Player()
        )
        caterpillar.level = 3
        test_pet_list.append(caterpillar)
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            pet.team.append(Pet("tiger"))
            trigger = decompress(cteam)
            activated_bool, targets, possible = pet.sob_trigger(trigger)
            self.assertTrue(activated_bool)

    def test_before_attack_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")], battle=True)
        cteam = compress(test_team)

        test_pet_names = ["elephant", "boar", "octopus"]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        test_pet_list[-1].level = 3
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            pet.team.append(Pet("tiger"))
            trigger = decompress(cteam)
            activated_bool, targets, possible = pet.before_attack_trigger(trigger)
            self.assertTrue(activated_bool)

    def test_after_attack_triggers(self):
        test_team = Team([Pet("fish")], battle=True)
        cteam = compress(test_team)
        test_pet_names = ["kangaroo", "snake"]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        test_pet_list[-1].level = 3
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            pet.team.append(Pet("tiger"))
            trigger = decompress(cteam)
            activated_bool, targets, possible = pet.after_attack_trigger(trigger)
            self.assertTrue(activated_bool)

    def test_hurt_triggers(self):
        test_team = Team([Pet("fish")], battle=True)
        cteam = compress(test_team)

        test_pet_names = ["peacock", "blowfish", "camel", "gorilla"]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            pet.team.append(Pet("tiger"))
            pet.hurt(1)
            trigger = decompress(cteam)
            activated_bool, targets, possible = pet.hurt_trigger(trigger)
            self.assertTrue(activated_bool)

    def test_knockout_triggers(self):
        test_team = Team([Pet("fish")], battle=True)
        cteam = compress(test_team)

        test_pet_names = ["hippo", "rhino"]

        test_pet_list = [
            Pet(x, shop=Shop(), team=test_team.copy(), player=Player())
            for x in test_pet_names
        ]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            pet.team.append(Pet("tiger"))
            trigger = decompress(cteam)
            activated_bool, targets, possible = pet.knockout_trigger(trigger)
            self.assertTrue(activated_bool)

    def test_dragon_ability(self):
        player = Player(shop=Shop(["ant"]), team=Team([Pet("fish"), Pet("dragon")]))
        self.assertEqual(player.team[0].attack, 2)
        self.assertEqual(player.team[0].health, 2)
        self.assertEqual(player.team[1].attack, 6)
        self.assertEqual(player.team[1].health, 8)

        player.buy_pet(0)
        self.assertEqual(player.team[0].attack, 3)
        self.assertEqual(player.team[0].health, 3)
        self.assertEqual(player.team[1].attack, 6)
        self.assertEqual(player.team[1].health, 8)

    def test_shop_hurt(self):
        player = Player(
            shop=Shop(["sleeping-pill"]),
            team=Team(["hedgehog", "gorilla", "camel", "blowfish", "peacock"]),
        )
        player.buy_food(0, 0)

        self.assertEqual(player.team[1].pet.status, "status-coconut-shield")
        self.assertGreater(player.team[3].pet.attack, Pet("blowfish").attack)
        self.assertGreater(player.team[4].pet.attack, Pet("peacock").attack)

    def test_dodo(self):
        dodo = Pet("dodo")
        dodo._attack = 11
        fish = Pet("fish")
        t = Team([fish, dodo])
        dodo.sob_trigger(Team())
        self.assertEqual(
            fish.attack,
            Pet("fish").attack
            + int(dodo.attack * dodo.ability["effect"]["percentage"] * 0.01),
        )

    def test_crab(self):
        t = Team(["crab", "dragon"])
        activated_bool, targets, possible = t[0].obj.sob_trigger(t)
        self.assertEqual(t[0].health, 4)

        t[0].obj.level = 2
        activated_bool, targets, possible = t[0].obj.sob_trigger(t)
        self.assertEqual(t[0].health, 8)

        t[0].obj.level = 3
        activated_bool, targets, possible = t[0].obj.sob_trigger(t)
        self.assertEqual(t[0].health, 12)

    def test_horse(self):
        player = Player(shop=Shop(["fish"]), team=Team([Pet("horse")]))

        player.buy_pet(0)
        self.assertEqual(player.team[1].attack, 3)
        self.assertEqual(player.team[1].health, 2)

        player.end_turn()
        player.start_turn()

        self.assertEqual(player.team[1].attack, 2)
        self.assertEqual(player.team[1].health, 2)

    def test_cupcake_cat(self):
        player = Player(shop=Shop(["cupcake"]), team=Team([Pet("cat")]))
        player.buy_food(0, 0)

        self.assertEqual(player.team[0].attack, 10)
        self.assertEqual(player.team[0].health, 11)

        player.end_turn()
        player.start_turn()

        self.assertEqual(player.team[0].attack, 4)
        self.assertEqual(player.team[0].health, 5)

    def test_ant_pill_in_shop(self):
        player = Player(
            shop=Shop(["sleeping-pill"]), team=Team([Pet("ant"), Pet("beaver")])
        )
        player.buy_food(0, 0)
        self.assertEqual(player.team[1].attack, 5)
        self.assertEqual(player.team[1].health, 3)

    def test_beaver_sell(self):
        player = Player(team=Team([Pet("beaver"), Pet("fish"), Pet("fish")]))
        player.sell(0)
        self.assertEqual(player.team[1].health, 3)
        self.assertEqual(player.team[2].health, 3)

    def test_beaver_sell_only_one_other_pet_on_team(self):
        player = Player(team=Team([Pet("fish"), Pet("beaver")]))
        player.sell(1)
        self.assertEqual(player.team[0].health, 3)

    def test_cricket_pill_in_shop(self):
        player = Player(shop=Shop(["sleeping-pill"]), team=Team([Pet("cricket")]))
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.name, "pet-zombie-cricket")
        self.assertEqual(player.team[0].attack, 1)
        self.assertEqual(player.team[0].health, 1)

    def test_sell_multiple_ducks(self):
        player = Player(shop=Shop(["beaver"]), team=Team([Pet("duck"), Pet("duck")]))
        player.sell(0)
        player.sell(1)
        self.assertEqual(player.shop.pets[0].health, 4)

    def test_fish_combine(self):
        fish = Pet("fish")
        fish.experience = 1
        player = Player(
            shop=Shop(["fish"]), team=Team([fish, Pet("beaver"), Pet("beaver")])
        )
        player.buy_combine(0, 0)
        self.assertEqual(player.team[0].pet.level, 2)
        self.assertEqual(player.team[1].attack, 4)
        self.assertEqual(player.team[1].health, 3)
        self.assertEqual(player.team[2].attack, 4)
        self.assertEqual(player.team[2].health, 3)

    def test_otter(self):
        player = Player(shop=Shop(["otter"]), team=Team([Pet("beaver")]))
        player.buy_pet(0)
        self.assertEqual(player.team[0].attack, 4)
        self.assertEqual(player.team[0].health, 3)
        self.assertEqual(player.team[1].attack, 1)
        self.assertEqual(player.team[1].health, 2)

    def test_buy_otter_on_empty_team(self):
        player = Player(shop=Shop(["otter"]))
        player.buy_pet(0)
        self.assertEqual(player.team[0].attack, 1)
        self.assertEqual(player.team[0].health, 2)

    def test_buy_otter_on_level_up(self):
        otter = Pet("otter")
        player = Player(shop=Shop(["otter"]), team=Team([otter, Pet("beaver")]))
        player.buy_combine(0, 0)
        self.assertEqual(player.team[1].attack, 4)
        self.assertEqual(player.team[1].health, 3)

        otter = Pet("otter")
        otter.experience = 1
        player = Player(
            shop=Shop(["otter"]), team=Team([otter, Pet("beaver"), Pet("fish")])
        )
        player.buy_combine(0, 0)
        self.assertEqual(player.team[1].attack, 4)
        self.assertEqual(player.team[1].health, 3)
        self.assertEqual(player.team[2].attack, 3)
        self.assertEqual(player.team[2].health, 3)

        otter = Pet("otter")
        otter.experience = 4
        player = Player(
            shop=Shop(["otter"]),
            team=Team([otter, Pet("beaver"), Pet("fish"), Pet("ant")]),
        )
        player.buy_combine(0, 0)
        self.assertEqual(player.team[1].attack, 4)
        self.assertEqual(player.team[1].health, 3)
        self.assertEqual(player.team[2].attack, 3)
        self.assertEqual(player.team[2].health, 3)
        self.assertEqual(player.team[3].attack, 3)
        self.assertEqual(player.team[3].health, 2)

    def test_pig(self):
        player = Player(team=Team([Pet("pig")]))
        player.sell(0)
        self.assertEqual(player.gold, 12)

    def test_cricket_pill_in_shop_with_turkey(self):
        player = Player(
            shop=Shop(["sleeping-pill"]), team=Team([Pet("cricket"), Pet("turkey")])
        )
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 4)
        self.assertEqual(player.team[0].health, 4)

    def test_sheep_pill_in_shop_with_turkey(self):
        player = Player(
            shop=Shop(["sleeping-pill"]), team=Team([Pet("sheep"), Pet("turkey")])
        )
        player.buy_food(0, 0)
        print(player.team)
        self.assertEqual(player.team[0].attack, 5)
        self.assertEqual(player.team[0].health, 5)
        self.assertEqual(player.team[1].attack, 5)
        self.assertEqual(player.team[1].health, 5)

    def test_cricket_pill_in_shop_with_horse(self):
        player = Player(
            shop=Shop(["sleeping-pill"]), team=Team([Pet("cricket"), Pet("horse")])
        )
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 2)

    def test_faint_hurt_summon_trigger_priority(self):
        # force ant to hit spider summon, since spider summons before ant triggers
        state = np.random.RandomState(seed=3).get_state()
        # force same spider summon just to be sure
        state2 = np.random.RandomState(seed=1).get_state()

        horse = Pet("horse")
        horse._health = 3  # survive hedgehog
        ant = Pet("ant", seed_state=state)
        spider = Pet("spider", seed_state=state2)
        spider._attack = 3  # more than ant
        player = Player(
            shop=["sleeping-pill"],
            team=Team(["peacock", ant, spider, "hedgehog", horse]),
        )
        player.buy_food(0, 3)
        self.assertEqual(player.team[2].attack, 5)  # base 2 + horse + ant
        self.assertEqual(player.team[2].health, 3)  # base 2 + ant

    def test_mushroom_scorpion_in_shop(self):
        scorpion = Pet("scorpion")
        scorpion.status = "status-extra-life"
        player = Player(shop=["sleeping-pill"], team=[scorpion])
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.status, "status-poison-attack")

    def test_honey_in_shop(self):
        fish = Pet("fish")
        fish.status = "status-honey-bee"
        player = Player(shop=["sleeping-pill"], team=[fish])
        player.buy_food(0, 0)
        self.assertEqual(player.team[0].pet.name, "pet-bee")

    def test_mushroom_deer_in_shop(self):
        deer = Pet("deer")
        deer.status = "status-extra-life"
        player = Player(shop=["sleeping-pill"], team=[deer])
        player.buy_food(0, 0)
        # deer should be in front of bus
        self.assertEqual(player.team[0].pet.name, "pet-deer")
        self.assertEqual(player.team[1].pet.name, "pet-bus")

    def test_zombie_fly_location(self):
        player = Player(
            shop=["sleeping-pill"], team=["fish", "fish", "fish", "fish", "fly"]
        )
        player.buy_food(0, 0)
        print(player.team)
        self.assertEqual(
            player.team[0].pet.name, "pet-zombie-fly"
        )  # zombie fly spawned in front of fly, not on fainted target location

    def test_flamingo(self):
        t = Team(["flamingo", "dragon", "dragon", "dragon"])
        t[0].obj.level = 1
        pet = t[0].obj
        te_idx = [0, 0]
        t[0].obj.faint_trigger(pet, te_idx)
        self.assertEqual(t[1].attack, 6 + 1)
        self.assertEqual(t[1].health, 8 + 1)
        self.assertEqual(t[2].attack, 6 + 1)
        self.assertEqual(t[2].health, 8 + 1)
        self.assertEqual(t[3].attack, 6)
        self.assertEqual(t[3].health, 8)

        t = Team(["flamingo", "dragon", "dragon", "dragon"])
        t[0].obj.level = 2
        pet = t[0].obj
        te_idx = [0, 0]
        t[0].obj.faint_trigger(pet, te_idx)
        self.assertEqual(t[1].attack, 6 + 2)
        self.assertEqual(t[1].health, 8 + 2)
        self.assertEqual(t[2].attack, 6 + 2)
        self.assertEqual(t[2].health, 8 + 2)
        self.assertEqual(t[3].attack, 6)
        self.assertEqual(t[3].health, 8)

        t = Team(["flamingo", "dragon", "dragon", "dragon"])
        t[0].obj.level = 3
        pet = t[0].obj
        te_idx = [0, 0]
        t[0].obj.faint_trigger(pet, te_idx)
        self.assertEqual(t[1].attack, 6 + 3)
        self.assertEqual(t[1].health, 8 + 3)
        self.assertEqual(t[2].attack, 6 + 3)
        self.assertEqual(t[2].health, 8 + 3)
        self.assertEqual(t[3].attack, 6)
        self.assertEqual(t[3].health, 8)

    def test_peacock(self):
        t = Team(["peacock"])
        enemy = Team(["fish"])
        t[0].obj.level = 1
        t[0].obj.hurt(1)
        t[0].obj.hurt_trigger(enemy)
        self.assertEqual(t[0].attack, 6)

        t = Team(["peacock"])
        enemy = Team(["fish"])
        t[0].obj.level = 2
        t[0].obj.hurt(1)
        t[0].obj.hurt_trigger(enemy)
        self.assertEqual(t[0].attack, 10)

        t = Team(["peacock"])
        enemy = Team(["fish"])
        t[0].obj.level = 3
        t[0].obj.hurt(1)
        t[0].obj.hurt_trigger(enemy)
        self.assertEqual(t[0].attack, 14)

    def test_badger(self):
        t = Team(["badger", "dragon"])
        pet = t[0].obj
        ally = t[1].obj
        other_team = Team(["fish"])
        enemy = other_team[0].obj
        t[0].obj.level = 1
        t[0].obj.hurt(3)
        t[0].obj.faint_trigger(t[0].obj, [0, 0], other_team)
        self.assertEqual(pet.health, 0)
        self.assertEqual(ally.health, 8 - 2)
        self.assertEqual(enemy.health, 2 - 2)

        t = Team(["badger", "dragon"])
        pet = t[0].obj
        ally = t[1].obj
        other_team = Team(["fish"])
        enemy = other_team[0].obj
        t[0].obj.level = 2
        t[0].obj.hurt(3)
        t[0].obj.faint_trigger(t[0].obj, [0, 0], other_team)
        self.assertEqual(pet.health, 0)
        self.assertEqual(ally.health, 8 - 5)
        self.assertEqual(enemy.health, 2 - 5)

        t = Team(["badger", "dragon"])
        pet = t[0].obj
        ally = t[1].obj
        other_team = Team(["fish"])
        enemy = other_team[0].obj
        t[0].obj.level = 3
        t[0].obj.hurt(3)
        t[0].obj.faint_trigger(t[0].obj, [0, 0], other_team)
        self.assertEqual(pet.health, 0)
        self.assertEqual(ally.health, 8 - 7)
        self.assertEqual(enemy.health, 2 - 7)


# %%
