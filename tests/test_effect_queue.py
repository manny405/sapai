#%%
import unittest
from functools import partial

import numpy as np

from sapai import *
from sapai.battle import Battle, run_looping_effect_queue, battle_phase
from sapai.graph import graph_battle
from sapai.compress import *

### Remember: Can always graph result with graph_battle(b,verbose=True) to
###   visualize behavior of the run_looping_effect_queue
g = partial(graph_battle, verbose=True)

### Always check identical behavior of t0,t1 reordering indifference


class TestEffectQueue(unittest.TestCase):
    def test_summon_sob(self):
        ref_team = Team(["pet-zombie-cricket"], battle=True)
        ref_team[0].obj._attack = 1
        ref_team[0].obj._health = 1

        ### Simple sob test for effect loop behavior
        t0 = Team(["cricket"])
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Dolphin should kill cricket, then mosquito has no target, so
        ###   ref_state should remain the same
        t0 = Team(["cricket"])
        t1 = Team(["dolphin", "mosquito"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Dolphin should kill cricket, then dolphin should hit camel for 5
        ###   leaving it with 1 hp, then mosquito only be able to hit camel
        ###   for 1 leaving only the zombie cricket
        t0 = Team(["cricket", "camel"])
        t1 = Team(["dolphin", "dolphin", "mosquito"])
        t1[2].obj.level = 3
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_blowfish_pingpong(self):
        ref_team = Team(["blowfish"], battle=True)
        ref_team[0].obj._health = 1

        ### Check puffer-fish ping-pong, even though not part of start of
        ### battle it should work if hurt is triggered manufriend
        t0 = Team(["blowfish"])
        t1 = Team(["blowfish"])
        t0[0].obj.hurt(1)
        b = run_sob(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t0.state, ref_team.state)

        ### Blowfish should trigger multiple hurt triggers in a row when
        ###   hurt multiple times in a single effect queue loop. Therefore,
        ###   in this case, t0 blowfish should only take 4 points of damage
        ###   not 6, which would be the case if hurt triggers always alternated
        ref_team = Team(["blowfish"], battle=True)
        ref_team[0].obj._health = 46

        t0 = Team(["blowfish"])
        t1 = Team(["hedgehog", "blowfish"])
        t0[0].obj._health = 50
        t1[0].obj._health = 1
        t1[0].obj.hurt(1)
        t1[1].obj._attack = 50
        t1[1].obj._health = 6
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_bee_sob(self):
        ref_team = Team(["pet-bee"], battle=True)
        t0 = Team(["ant"])
        t0[0].obj.eat(Food("honey"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_badger_sob(self):
        """
        Fairly complex example, where badger has honey, friend fish has one-up,
        then dolphin kills badger for sob, badger kills dolphin and fish,
        then bee spawns and one-up fish spawns, all in the correct locations.
        """
        ref_team = Team(["pet-bee", "fish", "fish"], battle=True)
        ref_team[1].obj._attack = 1
        ref_team[1].obj._health = 1

        t0 = Team(["badger", "fish", "fish"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_badger_honey_fly_sob(self):
        """
        Same as above but with fly for friend. Badger and fish should spawn
        their status pets first, then fly should place zombie-flies in the
        correct locations.

        This is a very complex example. All these cases succeed demonstrating
        the validity of the code to replicate the game auto-battle mechanics.
        """
        ref_team = Team(["zombie-fly", "bee", "zombie-fly", "fish", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 4
        ref_team[2].obj._health = 4
        ref_team[3].obj._attack = 1
        ref_team[3].obj._health = 1
        ref_team[4].obj.ability_counter = 2

        t0 = Team(["badger", "fish", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Another fish, then ability counter of fly should be only 1
        ref_team = Team(["zombie-fly", "bee", "fish", "fish", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 1
        ref_team[2].obj._health = 1
        ref_team[4].obj.ability_counter = 1
        t0 = Team(["badger", "fish", "fish", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_badger_honey_fly_shark_sob(self):
        """
        Same as above but with shark for friend
        """
        ### Shark should activate twice
        ref_team = Team(["zombie-fly", "bee", "fish", "fly", "shark"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 1
        ref_team[2].obj._health = 1
        ref_team[4].obj._attack = 4 + 4
        ref_team[4].obj._health = 4 + 4
        ref_team[3].obj.ability_counter = 1
        ref_team[4].obj.ability_counter = 2

        t0 = Team(["badger", "fish", "fly", "shark"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_badger_hedgehog(self):
        """
        Badger should kill dolphin and hedgehog, hedgehog's ability should
        activate, the bee should spawn leaving bee as pet left and t0 as winner
        """
        ref_team = Team(["pet-bee"], battle=True)
        t0 = Team(["badger", "hedgehog"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_sheep_fly(self):
        ref_team = Team(["zombie-fly", "bee", "pet-ram", "pet-ram", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 2
        ref_team[2].obj._health = 2
        ref_team[3].obj._attack = 2
        ref_team[3].obj._health = 2
        ref_team[4].obj.ability_counter = 1

        t0 = Team(["sheep", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_spider_fly(self):
        ref_team = Team(["zombie-fly", "spider", "turtle", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[1].obj._attack = 1
        ref_team[1].obj._health = 1
        ref_team[1].obj.level = 3
        ### Spider spaws everything at 2/2
        ref_team[2].obj._attack = 2
        ref_team[2].obj._health = 2
        ref_team[2].obj.level = 3
        ref_team[3].obj.ability_counter = 1

        seed_state = np.random.RandomState(seed=3).get_state()
        t0 = Team(["spider", "fly"], seed_state=seed_state)
        t0[0].obj.eat(Food("mushroom"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(minimal_state(b.t0), minimal_state(ref_team))

    def test_ox_fly(self):
        ref_team = Team(["bee", "ram", "ram", "ox", "fly"], battle=True)
        ref_team[1].obj._attack = 2
        ref_team[1].obj._health = 2
        ref_team[2].obj._attack = 2
        ref_team[2].obj._health = 2
        ref_team[3].obj._attack = 2
        ref_team[3].obj.ability_counter = 2
        ref_team[3].obj.status = "status-melon-armor"

        t0 = Team(["sheep", "ox", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_butterfly_dolphin(self):
        """
        If caterpillar is higher attack than dolphin, then it should be killed
        when it transforms to butterfly. Otherwise, dolphin attacks caterpillar.
        Fly does not activate for caterpillar because it's Evolve, not Faint
        effect.

        """
        ### First check default behavior of butterfly
        ref_team = Team(["butterfly", "fish", "fly"], battle=True)
        ref_team[0].obj._attack = 50
        ref_team[0].obj._health = 50
        ref_team[1].obj._attack = 50
        ref_team[1].obj._health = 50

        t0 = Team(["caterpillar", "fish", "fly"])
        t0[0].obj._attack = 50
        t0[0].obj._health = 1
        t0[0].obj.level = 3
        t0[1].obj._attack = 50
        t0[1].obj._health = 50
        t1 = Team(["fish"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Check that dolphin will kill butterfly when it's lowest health
        ref_team = Team(["zombie-fly", "fish", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[1].obj._attack = 50
        ref_team[1].obj._health = 50
        ref_team[2].obj.ability_counter = 1

        t0 = Team(["caterpillar", "fish", "fly"])
        t0[0].obj._attack = 50
        t0[0].obj._health = 1
        t0[0].obj.level = 3
        t0[1].obj._attack = 50
        t0[1].obj._health = 50
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Check that dolphin will attack fly first before caterpiller when
        ###   caterpillar attack is lower
        ref_team = Team(["butterfly", "fish"], battle=True)
        ref_team[0].obj._attack = 50
        ref_team[0].obj._health = 50
        ref_team[1].obj._attack = 50
        ref_team[1].obj._health = 50

        t0 = Team(["caterpillar", "fish", "fly"])
        t0[0].obj._attack = 1
        t0[0].obj._health = 50
        t0[0].obj.level = 3
        t0[1].obj._attack = 50
        t0[1].obj._health = 50
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)

        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_sob(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_kangaroo_ability(self):
        """
        Ensure that kangaroo ability activates before any hurt or faint triggers

        """
        ### If kangaroo ability doesn't activate first, then it would faint
        ###   from blowfish ability
        ref_team = Team(["kangaroo"], battle=True)
        ref_team[0].obj._attack = 3
        ref_team[0].obj._health = 2

        t0 = Team(["fish", "kangaroo"])
        t1 = Team(["blowfish"])
        t1[0].obj._attack = 50
        b = run_attack(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_attack(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_rhino_loop(self):
        """
        Ant abilities should not activate until rhino has killed all. Therefore
        enemy team should be empty.
        Ant abilities should find no targets if pet is summoned (? need ref for this)
        """
        ref_team = Team([], battle=True)
        t0 = Team(["rhino"])
        t1 = Team(["ant", "ant", "ant", "ant", "ant"])
        t1[0].obj.level = 3
        t1[1].obj.level = 3
        t1[2].obj.level = 3
        t1[3].obj.level = 3
        t1[4].obj.level = 3
        b = run_attack(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)
        b = run_attack(t1, t0)
        self.assertEqual(b.t0.state, ref_team.state)

        ref_team = Team(["zombie-cricket"], battle=True)
        ref_team[0].obj._attack = 1
        ref_team[0].obj._health = 1
        t0 = Team(["rhino"])
        t1 = Team(["cricket", "ant", "ant", "ant", "ant"])
        t1[1].obj.level = 3
        t1[2].obj.level = 3
        t1[3].obj.level = 3
        t1[4].obj.level = 3
        b = run_attack(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)
        b = run_attack(t1, t0)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_rhino_turtle(self):
        """
        Turtle, with BeforeFaint ability, should trigger before the rhino.
        Therefore, the pet behind turtle should not be hurt.
        """
        ref_team = Team(["ant"], battle=True)
        t0 = Team(["rhino"])
        t1 = Team(["turtle", "ant"])
        b = run_attack(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)
        b = run_attack(t1, t0)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_rhino_double(self):
        """
        Test that rhino damage is double against tier 1 pets
        """
        t0 = Team(["rhino"])
        t1 = Team(["fish", "fish"])
        t1[1].obj._health = 50
        ref_team = Team(["fish"], battle=True)
        ref_team[0].obj._health = 50
        ref_team[0].obj._health -= t0[0].ability["effect"]["amount"] * 2
        b = run_attack(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)
        b = run_attack(t1, t0)
        self.assertEqual(b.t0.state, ref_team.state)

        t0 = Team(["rhino"])
        t1 = Team(["fish", "dog"])
        t1[1].obj._health = 50
        ref_team = Team(["dog"], battle=True)
        ref_team[0].obj._health = 50
        ref_team[0].obj._health -= t0[0].ability["effect"]["amount"]
        b = run_attack(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)
        b = run_attack(t1, t0)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_elephant(self):
        """
        Testing variety of elephant behaviors
        """
        ### Peacock
        ref_team = Team(["peacock"], battle=True)
        ref_team[0].obj._health -= 3
        ref_team[0].obj._attack += ref_team[0].ability["effect"]["attackAmount"] * 3
        t0 = Team(["elephant", "peacock"])
        t0[0].obj.level = 3
        t1 = Team(["dragon"])
        b = run_attack(t0, t1, run_before=True)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_attack(t1, t0, run_before=True)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Should kill three pets behind if they're health is 1
        ref_team = Team([], battle=True)
        t0 = Team(["elephant", "pig", "pig", "pig"])
        t0[0].obj.level = 3
        t1 = Team(["dragon"])
        b = run_attack(t0, t1, run_before=True)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_attack(t1, t0, run_before=True)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Blowfish kills three
        ref_team = Team(["elephant", "blowfish"], battle=True)
        ref_team[0].obj.level = 3
        ref_team[1].obj._health -= 3
        t0 = Team(["elephant", "blowfish"])
        t0[0].obj.level = 3
        t1 = Team(["pig", "pig", "pig"])
        b = run_attack(t0, t1, run_before=True)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_attack(t1, t0, run_before=True)
        self.assertEqual(b.t1.state, ref_team.state)

        ### Kill all without ever attacking
        ref_team = Team(["elephant", "blowfish"], battle=True)
        ref_team[0].obj.level = 3
        ref_team[1].obj._health = 50
        ref_team[1].obj._health -= 6
        t0 = Team(["elephant", "blowfish"])
        t0[0].obj.level = 3
        t0[1].obj._health = 50
        t1 = Team(["pig", "pig", "pig", "pig", "pig"])
        b = run_battle(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)
        b = run_battle(t1, t0)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_crab(self):
        """
        Test that if crab's attack is smaller than dolphin, it should faint,
        otherwise it should live
        """
        pass

    def test_scorpion(self):
        """
        When scorpion comes back from one-up, it should gain peanut
        """
        pass

    def test_turkey_horse(self):
        """
        Test turkey and horse are giving buffs properly to summoned pets
        """
        ### Sheep

        ### Rooster

        ### Sheep fly
        pass

    def test_boar(self):
        """
        Ensure boar receives buff before attack correctly
        """
        pass

    def test_leopard_tiger_blowfish(self):
        """
        Test start of turn for leopard tiger versus blowfish
        """
        pass

    def test_skunk(self):
        pass

    def test_whale(self):
        """
        Check that whale's Swallow is performed correctly and that the pet
        is spit out at the right attack and health
        """
        pass

    def test_whale_tiger(self):
        """
        Ensure that whale and tiger are performing properly together.
        """
        pass

    def test_crocodile(self):
        """
        Test crocodile is multiple triggers and hurts multiple pets if the
        back one faints
        """
        pass
    
    def test_rat(self):
        pass

    def test_gorilla(self):
        pass

    def test_tiger(self):
        """
        Test tiger for nearly all pets
        """
        pass

    


def run_sob(t0, t1):
    b = Battle(t0, t1)
    phase_dict = {
        "init": [[str(x) for x in b.t0], [str(x) for x in b.t1]],
        "start": {
            "phase_start": [],
        },
    }
    run_looping_effect_queue(
        "sob_trigger",
        ["oteam"],
        b,
        "phase_start",
        [b.t0, b.t1],
        b.pet_priority,
        phase_dict["start"],
    )
    phase_dict["start"]["phase_move_end"] = [
        [
            [str(x) for x in b.t0],
            [str(x) for x in b.t1],
        ]
    ]
    b.battle_history = phase_dict
    return b


def run_attack(t0, t1, run_before=False):
    b = Battle(t0, t1)
    phase_dict = {
        "init": [[str(x) for x in b.t0], [str(x) for x in b.t1]],
        "attack 0": {},
    }
    if run_before:
        phase_dict["attack 0"]["phase_attack_before"] = []
    phase_dict["attack 0"]["phase_attack"] = []
    phase_dict["attack 0"]["phase_move_end"] = []
    phase_str = "attack 0"
    for temp_phase in phase_dict[phase_str]:
        battle_phase(b, temp_phase, [b.t0, b.t1], b.pet_priority, phase_dict[phase_str])
    b.battle_history = phase_dict
    phase_dict[phase_str]["phase_move_end"] = [
        [
            [str(x) for x in b.t0],
            [str(x) for x in b.t1],
        ]
    ]
    b.battle_history = phase_dict
    return b


def run_battle(t0, t1):
    b = Battle(t0, t1)
    b.battle()
    return b


# %%

# t = b.t0.state
# r = ref_team.state
# for i in range(len(t["team"])):
#     print(i, t["team"][i] == r["team"][i])
# print(b.t0.state == ref_team.state)

# %%
# t0 = Team(["rhino"])
# t1 = Team(["ant", "ant", "ant", "ant", "ant"])
# b = run_attack(t0, t1)


#%%
