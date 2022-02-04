#%%
import unittest

from sapai import *
from sapai.battle import Battle
from sapai.graph import graph_battle


class TestBattles(unittest.TestCase):

    def test_multi_hurt(self):
        t0 = Team(["badger", "camel", "fish"])
        t0[0].pet._health = 1
        t0[0].pet._attack = 1
        t1 = Team(["cricket", "horse", "mosquito", "tiger"])

        b = Battle(t0, t1)
        b.battle()

    def test_multi_faint(self):
        t0 = Team(["badger", "camel", "fish"])
        t0[0].pet._health = 1
        t0[0].pet._attack = 5
        t1 = Team(["cricket", "horse", "mosquito", "tiger"])

        b = Battle(t0, t1)
        b.battle()

    def test_before_and_after_attack(self):
        t0 = Team(["elephant", "snake", "dragon", "fish"])
        t1 = Team(["cricket", "horse", "fly", "tiger"])
        t0[2]._health = 50

        b = Battle(t0, t1)
        b.battle()
        t0 = Team(["elephant", "snake", "dragon", "fish"])
        t1 = Team(["cricket", "horse", "fly", "tiger"])
        t0[2]._health = 50
        print(t0)
        print(t1)

        b = Battle(t0, t1)
        b.battle()

    def test_rhino_test(self):
        t0 = Team(["horse", "horse", "horse", "horse"])
        t1 = Team(["rhino", "tiger"])

        b = Battle(t0, t1)
        b.battle()

    def test_hippo_test(self):
        t0 = Team(["horse", "horse", "horse", "horse"])
        t1 = Team(["hippo", "tiger"])

        b = Battle(t0, t1)
        b.battle()
        
    
    def test_whale_without_swallow_target(self):
        team1 = Team([Pet("fish")])
        team2 = Team([Pet("whale"), Pet("hedgehog"), Pet("fish"), Pet("rabbit")])

        test_battle = Battle(team1, team2)
        test_battle.battle()

    
    def test_multiple_hedgehog(self):
        team1 = Team([Pet("fish"), Pet("hedgehog")])
        team2 = Team([Pet("elephant"), Pet("hedgehog")])

        test_battle = Battle(team1, team2)
        test_battle.battle()

    def test_whale_parrot_swallow(self):
        team1 = Team([Pet("whale"), Pet("parrot")])
        team2 = Team([Pet("fish"), "dragon"])

        player1 = Player(team=team1)
        player2 = Player(team=team2)

        player1.end_turn()
        player2.end_turn()

        test_battle = Battle(player1.team, player2.team)
        test_battle.battle()
# %%
