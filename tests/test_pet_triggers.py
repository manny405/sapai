import unittest

from sapai import *
from sapai.compress import compress,decompress


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

        str_fmt = "{:3s}{:15s}{:15s}{:15s}{:20s}{:20s}\n"
        print_str = str_fmt.format("N", "Pet", "Trigger", "TriggerBy", "EffectKind", "EffectTarget")
        print_str += "-------------------------------------------------------------------------------\n"
        for iter_idx in range(len(pet_list)):
            print_str += str_fmt.format(
                str(n[iter_idx]),
                pet_list[iter_idx].name,
                trigger_list[iter_idx],
                triggerby_list[iter_idx],
                effect_kind_list[iter_idx],
                effect_target_kind_list[iter_idx])

        print(print_str)

    def test_start_of_turn_triggers(self):
        test_pet_names = ["dromedary", "swan", "caterpillar", "squirrel"]
        test_pet_list = [Pet(x, shop=Shop(), team=Team(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.sot_trigger()
            self.assertTrue(activated_bool)

    def test_sell_triggers_self(self):
        test_team = Team([Pet("dragon"), Pet("cat"), Pet("horse")])

        test_pet_names = ["beaver", "duck", "pig", "shrimp", "owl"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
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
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy()) for x in test_pet_names]
        test_bool_list = [False, False, False, True, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.sell_trigger(pet.team[0].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_food_triggers_self(self):
        test_team = Team([Pet("dragon"), Pet("cat")])
        test_pet_names = ["beetle", "ladybug", "tabby-cat", "rabbit", "worm", "seal",
                          "sauropod"]

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        # Buy food for self
        for pet in test_pet_list:
            activated_bool, targets, possible = pet.buy_food_trigger(pet)
            self.assertTrue(activated_bool)

    def test_buy_food_triggers_other(self):
        test_team = Team([Pet("dragon"), Pet("cat")])
        test_pet_names = ["beetle", "ladybug", "tabby-cat", "rabbit", "worm", "seal",
                          "sauropod"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]

        # Buy food for other
        test_bool_list = [False, True, False, True, False, False, True]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_food_trigger(pet.team[0].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_friend_triggers_self(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["otter", "crab", "snail", "buffalo", "chicken", "cow",
                          "goat", "dragon"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        # Buy friend as self
        test_bool_list = [True, True, True, False, False, True, False, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_friend_trigger(pet)
            if pet.name == "pet-snail":
                continue
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_friend_triggers_self_other_tier_1(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["otter", "crab", "snail", "buffalo", "chicken", "cow",
                          "goat", "dragon"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        # Buy other friend tier1
        test_bool_list = [False, False, False, True, True, False, True, True]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_friend_trigger(pet.team[0].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_buy_friend_triggers_self_other_not_tier_1(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["otter", "crab", "snail", "buffalo", "chicken", "cow",
                          "goat", "dragon"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        # Buy other friend not tier1
        test_bool_list = [False, False, False, True, False, False, True, False]
        for iter_idx, pet in enumerate(test_pet_list):
            activated_bool, targets, possible = pet.buy_friend_trigger(pet.team[1].pet)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_friend_summoned_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["horse", "dog", "lobster", "turkey"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.friend_summoned_trigger(pet.team[0].pet)
            self.assertTrue(activated_bool)

    def test_levelup_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

        test_pet_names = ["fish", "octopus"]
        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.levelup_trigger(pet.team[0].pet)
            self.assertTrue(activated_bool)

    def test_end_of_turn_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])
        test_team[0].pet.level = 3
        test_player = Player()

        test_pet_names = [
            "bluebird", "hatching-chick", "giraffe", "puppy", "tropical-fish",
            "bison", "llama", "penguin", "parrot", "monkey", "poodle",
            "tyrannosaurus"]

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=test_player) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            activated_bool, targets, possible = pet.eot_trigger(pet.team[0].pet)
            self.assertTrue(activated_bool)

    def test_faint_triggers_self(self):
        test_team = Team([Pet("fish")], battle=True)
        test_pet_names = ["ant", "cricket", "flamingo", "hedgehog", "spider", "badger",
                          "ox", "sheep", "turtle", "deer", "rooster", "microbe",
                          "eagle", "shark", "fly", "mammoth"]

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        # Self faint
        test_bool_list = [True, True, True, True, True,
                          True, False, True, True, True,
                          True, True, True, False, False,
                          True]
        for iter_idx, pet in enumerate(test_pet_list):
            pet.team.append(Pet("tiger"))
            te_idx = [0, pet.team.index(pet)]
            activated_bool, targets, possible = pet.faint_trigger(pet, te_idx)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_faint_triggers_self_friend_in_front(self):
        test_team = Team([Pet("fish")], battle=True)
        test_pet_names = ["ant", "cricket", "flamingo", "hedgehog", "spider", "badger",
                          "ox", "sheep", "turtle", "deer", "rooster", "microbe",
                          "eagle", "shark", "fly", "mammoth"]

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        test_bool_list = [False, False, False, False, False,
                          False, True, False, False, False,
                          False, False, False, True, True,
                          False]
        for iter_idx, pet in enumerate(test_pet_list):
            pet.team.append(Pet("tiger"))
            friend_ahead = pet.team.get_ahead(pet)[0]
            te_idx = [0, pet.team.index(friend_ahead)]
            activated_bool, targets, possible = pet.faint_trigger(friend_ahead, te_idx)
            self.assertEqual(activated_bool, test_bool_list[iter_idx])

    def test_start_of_battle_triggers(self):
        test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")], battle=True)
        cteam = compress(test_team)
        test_pet_names = ["mosquito", "bat", "whale", "dolphin", "skunk", "crocodile",
                          "leopard"]

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
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

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
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

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
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

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
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

        test_pet_list = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
        self.print_pet_list(test_pet_list)

        for pet in test_pet_list:
            pet.team.append(Pet("tiger"))
            trigger = decompress(cteam)
            activated_bool, targets, possible = pet.knockout_trigger(trigger)
            self.assertTrue(activated_bool)

    def test_dragon_ability(self):
        player = Player(shop=Shop(["ant"]), team=Team([Pet("fish"), Pet("dragon")]))
        self.assertEqual(player.team[0].attack, 2)
        self.assertEqual(player.team[0].health, 3)
        self.assertEqual(player.team[1].attack, 6)
        self.assertEqual(player.team[1].health, 8)

        player.buy_pet(0)
        self.assertEqual(player.team[0].attack, 3)
        self.assertEqual(player.team[0].health, 4)
        self.assertEqual(player.team[1].attack, 6)
        self.assertEqual(player.team[1].health, 8)
