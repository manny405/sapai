import unittest

from sapai import *
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
                targets, possible = func(apet, apet_idx, teams, te, te_idx, fixed_targets)

    def test_tiger_func(self):
        t = Team(["spider", "tiger"], battle=True)
        slot_list = [x for x in t]
        for slot in slot_list:
            if slot.empty:
                continue
            slot.pet.faint_trigger(slot.pet, [0, t.index(slot)])