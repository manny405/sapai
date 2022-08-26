import unittest

from sapai.shop import *
from sapai.agents import *


class TestAgents(unittest.TestCase):
    def test_CombinatorialSearch(self):
        turn = 1
        player = Player(
            team=["ant", "fish", "beaver", "cricket", "horse"],
            shop=ShopLearn(turn=turn),
            turn=turn,
        )
        cs = CombinatorialSearch()
        avail_actions = cs.avail_actions(player)

        for temp_action in avail_actions:
            if len(temp_action) == 0:
                temp_name = "None"
            else:
                temp_name = temp_action[0].__name__

            if len(temp_action) > 1:
                temp_inputs = temp_action[1:]
            else:
                temp_inputs = []

    def test_simple_CombinatorialSearch(self):
        turn = 1
        player = Player(shop=ShopLearn(turn=turn), turn=turn)
        player.gold = 10
        cs = CombinatorialSearch(max_actions=3)
        player_list, team_dict = cs.search(player)
