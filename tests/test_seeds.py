import unittest
import numpy as np

from sapai import *
from sapai.compress import compress, decompress


class TestSeeds(unittest.TestCase):
    def test_battle_reproducibility(self):
        state = np.random.RandomState(seed=4).get_state()
        state2 = np.random.RandomState(seed=4).get_state()

        winner_set = set()
        for i in range(20):
            t0 = Team(["ant", "ant", "fish"], seed_state=state)
            t1 = Team(["ant", "ant", "fish"], seed_state=state2)
            b = Battle(t0, t1)
            winner = b.battle()
            # Same state should result in draw
            winner_set.add(winner)
        self.assertEqual(len(winner_set), 1)

    def test_battle_reproducibility_after_compress(self):
        state = np.random.RandomState(seed=4).get_state()
        state2 = np.random.RandomState(seed=4).get_state()

        winner_set = set()
        for i in range(20):
            t0 = Team(["ant", "ant", "fish"], seed_state=state)
            t1 = Team(["ant", "ant", "fish"], seed_state=state2)

            t0 = decompress(compress(t0))
            t1 = decompress(compress(t1))

            b = Battle(t0, t1)
            winner = b.battle()
            # Same state should result in draw
            winner_set.add(winner)
        self.assertEqual(len(winner_set), 1)

    def test_shop_reproducibility(self):
        state = np.random.RandomState(seed=20).get_state()
        s = Shop(turn=11, seed_state=state)
        # ref_init_state = s.state

        # Setup solution
        shop_check_list = []
        s = Shop(turn=11, seed_state=state)
        for i in range(10):
            names = []
            for slot in s:
                names.append(slot.obj.name)
            names = tuple(names)
            shop_check_list.append(names)
            s.roll()
        shop_check_list = tuple(shop_check_list)

        # Run check for reproducibility
        for i in range(10):
            s = Shop(turn=11, seed_state=state)
            temp_check_list = []
            for i in range(10):
                names = []
                for slot in s:
                    names.append(slot.obj.name)
                names = tuple(names)
                temp_check_list.append(names)
                s.roll()
            self.assertEqual(tuple(temp_check_list), shop_check_list)

        for i in range(10):
            s = Shop(turn=11, seed_state=state)
            s = decompress(compress(s))
            # self.assertEqual(s.state, ref_init_state)
            temp_check_list = []
            for i in range(10):
                names = []
                for slot in s:
                    names.append(slot.obj.name)
                names = tuple(names)
                temp_check_list.append(names)
                s.roll()
            self.assertEqual(tuple(temp_check_list), shop_check_list)


# from sapai.compress import compress, decompress
# state = np.random.RandomState(seed=20).get_state()
# s = Shop(turn=11, seed_state=state)
# test_s = decompress(compress(s))
