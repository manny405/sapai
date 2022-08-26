import unittest

from sapai import *
from sapai.battle import *
from sapai.effects import *
from sapai.compress import *


class TestEffects(unittest.TestCase):
    def test_target_function(self):
        shop = Shop()
        shop.roll()
        t0 = Team(["fish", "dragon", "owl", "ant", "badger"], shop=shop)
        t1 = Team(["cat", "hippo", "horse", "ant"], shop=shop)
        for slot in t0:
            slot.pet.shop = shop
        for slot in t1:
            slot.pet.shop = shop
        t1[0].pet._health = 7
        t0[0].pet.level = 2
        t0[1].pet.level = 3
        t0[0].pet._health = 8

    def test_all_functions(self):
        all_func = [x for x in func_dict.keys()]
        pet_func = {}
        for pet, fd in data["pets"].items():
            if "level1Ability" not in fd:
                continue
            kind = fd["level1Ability"]["effect"]["kind"]
            if kind not in pet_func:
                pet_func[kind] = []
            pet_func[kind].append(pet)

        shop = Shop()
        shop.roll()
        base_team = Team(["fish", "dragon"])
        for slot in base_team:
            slot.pet.shop = shop
            slot.pet.team = base_team
        tc = compress(base_team)
        for func_name in all_func:
            print(func_name)
            if func_name not in pet_func:
                continue
            for pet in pet_func[func_name]:
                temp_team = decompress(tc)
                temp_team.append(pet)
                temp_team[2].pet.shop = shop
                temp_team.append("bison")
                temp_team[3].pet.shop = shop
                temp_enemy_team = decompress(tc)
                func = get_effect_function(temp_team[2])
                apet = temp_team[2].pet
                apet_idx = [0, 2]
                teams = [temp_team, temp_enemy_team]
                te = temp_team[2].pet
                te_idx = [0, 2]
                fixed_targets = []

                if func_name == "RepeatAbility":
                    te = temp_team[1].pet
                if func_name == "FoodMultiplier":
                    te = Food("pear")
                targets, possible = func(
                    apet, apet_idx, teams, te, te_idx, fixed_targets
                )

    def test_tiger_func(self):
        t = Team(["spider", "tiger"], battle=True)
        slot_list = [x for x in t]
        for slot in slot_list:
            if slot.empty:
                continue
            slot.pet.faint_trigger(slot.pet, [0, t.index(slot)])

    def test_eagle_stats(self):
        # seed for Snake 6/6
        state = np.random.RandomState(seed=4).get_state()

        pet = Pet("eagle", seed_state=state)
        pet.level = 3
        t = Team([pet], battle=True)
        t[0].pet.faint_trigger(t[0].pet, [0, t.index(t[0])])

        # should spawn Snake Lvl3 18/18 since Eagle was lvl 3
        self.assertEqual(t[0].level, 3)
        self.assertEqual(t[0].attack, 18)
        self.assertEqual(t[0].health, 18)

    def test_multiple_cats(self):
        player = Player(shop=Shop(["pear"]), team=Team([Pet("cat")]))
        player.buy_food(0, 0)

        # should add +4/+4
        self.assertEqual(player.team[0].attack, 8)
        self.assertEqual(player.team[0].health, 9)

        player = Player(shop=Shop(["pear"]), team=Team([Pet("cat"), Pet("cat")]))
        player.buy_food(0, 0)

        # should add +6/+6
        self.assertEqual(player.team[0].attack, 10)
        self.assertEqual(player.team[0].health, 11)

        player = Player(
            shop=Shop(["pear"]), team=Team([Pet("cat"), Pet("cat"), Pet("cat")])
        )
        player.buy_food(0, 0)

        # should add +8/+8
        self.assertEqual(player.team[0].attack, 12)
        self.assertEqual(player.team[0].health, 13)

    def test_melon(self):
        leopard = Pet("leopard")
        leopard.status = "status-melon-armor"
        leopard._health = 50
        leopard._attack = 50
        fish = Pet("fish")
        fish.status = "status-melon-armor"
        fish._health = 50
        fish._attack = 50

        t0 = Team([leopard], battle=True)
        t1 = Team([fish], battle=True)

        leopard.sob_trigger(t1)
        self.assertEqual(fish.health, 45)  # 25 damage, -20 melon
        self.assertEqual(fish.status, "none")

        attack_phase = get_attack(leopard, fish)
        self.assertEqual(attack_phase[1], 30)  # fish hits melon
        self.assertEqual(leopard.status, "none")

    def test_garlic(self):
        fish = Pet("fish")
        fish.status = "status-garlic-armor"
        fish._health = 50
        fish._attack = 50

        t = Team(["dolphin", "otter", "mosquito"], battle=True)
        t2 = Team([fish], battle=True)
        t[0].pet.sob_trigger(t2)
        self.assertEqual(fish.health, 47)  # 5 damage, -2 garlic

        t[2].pet.sob_trigger(t2)
        self.assertEqual(fish.health, 46)  # should still do 1 damage

        attack_phase = get_attack(t[0].pet, fish)
        self.assertEqual(attack_phase[0], 2)  # dolphin 4/6

        attack_phase = get_attack(t[1].pet, fish)
        self.assertEqual(attack_phase[0], 1)  # otter 1/2

    def test_coconut(self):
        gorilla = Pet("gorilla")
        gorilla.status = "status-coconut-shield"
        t = Team([gorilla], battle=True)
        t2 = Team(["crocodile"], battle=True)
        t3 = Team(["dragon"], battle=True)

        t2[0].pet.sob_trigger(t)
        self.assertEqual(gorilla.health, 9)  # unchanged
        self.assertEqual(gorilla.status, "none")

        gorilla.status = "status-coconut-shield"
        attack_phase = get_attack(gorilla, t3[0].pet)
        self.assertEqual(attack_phase[1], 0)  # dragon hits coconut
        self.assertEqual(gorilla.status, "none")

    def test_weak(self):
        fish = Pet("fish")
        fish.status = "status-weak"
        fish._health = 50
        fish._attack = 50
        t = Team([fish], battle=True)
        t2 = Team(["dolphin"], battle=True)
        t3 = Team(["dragon"], battle=True)

        t2[0].pet.sob_trigger(t)
        self.assertEqual(fish.health, 42)  # 5 + 3

        attack_phase = get_attack(fish, t3[0].pet)
        self.assertEqual(attack_phase[1], 9)  # 6/8 + 3

    def test_hatching_chick_level_3(self):
        hc = Pet("hatching-chick")
        hc.level = 3
        t = Team(["dragon", hc])
        hc.sot_trigger(t)
        self.assertEqual(t[0].pet.experience, 1)
