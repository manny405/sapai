#%%
import unittest
from functools import partial

import numpy as np

from sapai import *
from sapai.battle import Battle, run_looping_effect_queue
from sapai.graph import graph_battle
from sapai.compress import *

### Remember: Can always graph result with graph_battle(b,verbose=True) to
###   visualize behavior of the run_looping_effect_queue
g = partial(graph_battle, verbose=True)


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


class TestEffectQueue(unittest.TestCase):
    def test_summon_sob(self):
        ref_team = Team(["pet-zombie-cricket"], battle=True)

        ### Simple sob test for effect loop behavior
        t0 = Team(["cricket"])
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        ref_team[0].obj._attack = 1
        ref_team[0].obj._health = 1
        self.assertEqual(b.t0.state, ref_team.state)

        ### Dolphin should kill cricket, then mosquito has no target, so
        ###   ref_state should remain the same
        t0 = Team(["cricket"])
        t1 = Team(["dolphin", "mosquito"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

        ### Dolphin should kill cricket, then dolphin should hit camel for 5
        ###   leaving it with 1 hp, then mosquito only be able to hit camel
        ###   for 1 leaving only the zombie cricket
        t0 = Team(["cricket", "camel"])
        t1 = Team(["dolphin", "dolphin", "mosquito"])
        t1[2].obj.level = 3
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_blowfish_pingpong(self):
        ref_team = Team(["blowfish"], battle=True)
        ref_team[0].obj._health = 1

        ### Check puffer-fish ping-pong, even though not part of start of
        ### battle it should work if hurt is triggered manually
        t0 = Team(["blowfish"])
        t1 = Team(["blowfish"])
        t0[0].obj.hurt(1)
        b = run_sob(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_bee_sob(self):
        ref_team = Team(["pet-bee"], battle=True)
        t0 = Team(["ant"])
        t0[0].obj.eat(Food("honey"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_badger_sob(self):
        """
        Fairly complex example, where badger has honey, ally fish has one-up,
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

    def test_badger_honey_fly_sob(self):
        """
        Same as above but with fly for ally.
        """
        t0 = Team(["badger", "fish", "fish", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)

    def test_badger_honey_fly_shark_sob(self):
        """
        Same as above but with additional shark for ally
        """
        t0 = Team(["badger", "fish", "fish", "fly", "shark"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        
    def test_badger_hedgehog(self):
        t0 = Team(["badger", "hedgehog"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        
    
    def test_sheep_fly(self):
        pass

    def test_rhino_loop(self):
        pass


# %%
