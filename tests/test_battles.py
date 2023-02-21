# %%
import unittest

import numpy as np

from sapai import *
from sapai.battle import Battle
from sapai.graph import graph_battle
from sapai.compress import *


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

    def test_cat_battle(self):
        team1 = Team([Pet("fish")])
        team2 = Team([Pet("cat")])

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

    def test_caterpillar_order_high_attack(self):
        cp = Pet("caterpillar")
        cp.level = 3
        cp._attack = 5  # 1 more than dolphin
        cp._health = 7
        t = Team([cp, "dragon"])
        t2 = Team(["dolphin", "dragon"])
        b = Battle(t, t2)
        r = b.battle()
        # print(b.battle_history) # caterpillar evolves first, dolphin snipes butterfly, 1v2 loss
        self.assertEqual(r, 1)

    def test_caterpillar_order_low_attack(self):
        cp = Pet("caterpillar")
        cp.level = 3
        cp._attack = 1
        cp._health = 7
        t = Team([cp, "dragon"])
        t2 = Team(["dolphin", "dragon"])
        b = Battle(t, t2)
        r = b.battle()
        # print(b.battle_history) # dolphin hits caterpillar, caterpillar evolves, copies dragon, win
        self.assertEqual(r, 0)

    def test_dodo(self):
        dodo = Pet("dodo")
        dodo.level = 3
        dodo._attack = 10
        team1 = Team([Pet("leopard"), dodo])

        fish = Pet("fish")
        fish._attack = 5
        fish._health = 20
        team2 = Team([fish])

        test_battle = Battle(team1, team2)
        result = test_battle.battle()

        # dodo adds enough attack for leopard to kill fish
        self.assertEqual(result, 0)

    def test_ant_in_battle(self):
        team1 = Team([Pet("ant"), Pet("fish")])
        team2 = Team([Pet("camel")])

        test_battle = Battle(team1, team2)
        result = test_battle.battle()
        self.assertEqual(result, 0)

    def test_horse_in_battle(self):
        team1 = Team([Pet("cricket"), Pet("horse")])
        team2 = Team([Pet("camel")])

        test_battle = Battle(team1, team2)
        result = test_battle.battle()
        self.assertEqual(test_battle.t0.empty, [0, 1, 2, 3, 4])
        self.assertEqual(test_battle.t1[0].health, 1)

    def test_horse_with_bee_in_battle(self):
        cricket = Pet("cricket")
        cricket.status = "status-honey-bee"
        team1 = Team([cricket, Pet("horse")])
        fish = Pet("fish")
        fish._health = 5
        team2 = Team([fish, Pet("beaver")])

        test_battle = Battle(team1, team2)
        result = test_battle.battle()
        self.assertEqual(result, 2)

    def test_mosquito_in_battle(self):
        team1 = Team([Pet("mosquito")])
        team2 = Team([Pet("pig")])

        test_battle = Battle(team1, team2)
        result = test_battle.battle()
        self.assertEqual(result, 0)

    def test_blowfish_pingpong(self):
        # they hit eachother once, rest of the battle is constant hurt triggers until they both faint
        b1 = Pet("blowfish")
        b1._attack = 1
        b1._health = 50

        b2 = Pet("blowfish")
        b2._attack = 1
        b2._health = 50

        b = Battle(Team([b1]), Team([b2]))
        r = b.battle()
        self.assertTrue(
            "attack 1" not in b.battle_history
        )  # they attack eachother, then keep using hurt_triggers until one of them dies, should never reach a 2nd attack phase

    def test_elephant_blowfish(self):
        # blowfish snipes first fish in 'before-attack' phase of elephant, leaving elephant without a target to attack normally
        # then snipes second fish in next turn's 'before attack'
        state = np.random.RandomState(seed=1).get_state()

        e1 = Pet("elephant")
        e1._attack = 1
        e1._health = 5

        b1 = Pet("blowfish", seed_state=state)
        b1._attack = 1
        b1._health = 5

        f1 = Pet("fish")
        f1._attack = 50
        f1._health = 1
        f1.status = "status-splash-attack"

        f2 = Pet("fish")
        f2._attack = 50
        f2._health = 1
        f2.status = "status-splash-attack"

        b = Battle(Team([e1, b1]), Team([f1, f2]))
        r = b.battle()
        self.assertEqual(r, 0)

    def test_hedgehog_blowfish_camel_hurt_team(self):
        # standard hedgehog blowfish camel teams facing off against eachother
        # lots of hurt triggers going off within one turn
        state1 = np.random.RandomState(seed=2).get_state()
        state2 = np.random.RandomState(seed=2).get_state()

        bf1 = Pet("blowfish", seed_state=state1)
        bf1._attack = 20
        bf1._health = 20
        bf1.level = 3
        bf1.status = "status-garlic-armor"

        c1 = Pet("camel")
        c1._attack = 20
        c1._health = 20
        c1.level = 2
        c1.status = "status-garlic-armor"

        hh1 = Pet("hedgehog")
        hh2 = Pet("hedgehog")

        bf2 = Pet("blowfish", seed_state=state2)
        bf2._attack = 20
        bf2._health = 20
        bf2.level = 3
        bf2.status = "status-garlic-armor"

        c2 = Pet("camel")
        c2._attack = 20
        c2._health = 20
        c2.level = 2
        c2.status = "status-garlic-armor"

        hh3 = Pet("hedgehog")
        hh4 = Pet("hedgehog")

        b = Battle(Team([hh1, hh2, c1, bf1]), Team([hh3, hh4, c2, bf2]))
        r = b.battle()
        self.assertEqual(r, 2)

    def test_hedgehog_vs_honey(self):
        hh1 = Pet("hedgehog")
        hh2 = Pet("hedgehog")
        hh3 = Pet("hedgehog")
        hh4 = Pet("hedgehog")
        hh5 = Pet("hedgehog")
        f1 = Pet("fish")
        f1.status = "status-honey-bee"

        b = Battle(Team([hh1, hh2, hh3, hh4, hh5]), Team([f1]))
        r = b.battle()
        # ability triggers always go before status triggers
        # fish wins since honey bee spawns at the end of the turn, after all faint triggers are completed
        self.assertEqual(r, 1)

    def test_hedgehog_vs_mushroom(self):
        hh1 = Pet("hedgehog")
        hh2 = Pet("hedgehog")
        hh3 = Pet("hedgehog")
        hh4 = Pet("hedgehog")
        hh5 = Pet("hedgehog")
        f1 = Pet("fish")
        f1.status = "status-extra-life"

        b = Battle(Team([hh1, hh2, hh3, hh4, hh5]), Team([f1]))
        r = b.battle()
        # ability triggers always go before status triggers
        # fish wins since mushroom spawns at the end of the turn, after all faint triggers are completed
        self.assertEqual(r, 1)

    def test_mushroom_scorpion(self):
        scorpion = Pet("scorpion")
        scorpion.status = "status-extra-life"
        b = Battle(Team([scorpion]), Team(["dragon"]))
        r = b.battle()
        self.assertEqual(r, 2)  # draw since scorpion respawns with poison.

    def test_badger_draws(self):
        # normal 1v1
        b1 = Pet("badger")
        b2 = Pet("badger")
        b = Battle(Team([b1]), Team([b2]))
        r = b.battle()
        self.assertEqual(r, 2)

        # 1 survives, enemy ability kills
        b1 = Pet("badger")
        b1._health = 6
        b2 = Pet("badger")
        b = Battle(Team([b1]), Team([b2]))
        r = b.battle()
        self.assertEqual(r, 2)

        # normal honey 1v1
        hb1 = Pet("badger")
        hb1.status = "status-honey-bee"
        hb2 = Pet("badger")
        hb2.status = "status-honey-bee"
        b = Battle(Team([hb1]), Team([hb2]))
        r = b.battle()
        self.assertEqual(r, 2)

        # 1 survives, enemy ability kills
        hb1 = Pet("badger")
        hb1.status = "status-honey-bee"
        hb1._health = 6
        hb2 = Pet("badger")
        hb2.status = "status-honey-bee"
        b = Battle(Team([hb1]), Team([hb2]))
        r = b.battle()
        self.assertEqual(r, 2)

        # 1 survives, enemey ability kills, even with less attack priority should NOT be able to hit bee with ability
        hb1 = Pet("badger")
        hb1.status = "status-honey-bee"
        hb1._attack = 4
        hb1._health = 6
        hb2 = Pet("badger")
        hb2.status = "status-honey-bee"
        b = Battle(Team([hb1]), Team([hb2]))
        r = b.battle()
        self.assertEqual(r, 2)

        # badger with less attack can kill zombie-cricket
        b1 = Pet("badger")
        c1 = Pet("cricket")
        c1._attack = 6
        b = Battle(Team([b1]), Team([c1]))
        r = b.battle()
        self.assertEqual(r, 2)

        # badger with higher priority hits nothing with ability, zombie-cricket spanws and bee spawns
        hb1 = Pet("badger")
        hb1.status = "status-honey-bee"
        c1 = Pet("cricket")
        c1._attack = 4
        b = Battle(Team([hb1]), Team([c1]))
        r = b.battle()
        self.assertEqual(r, 2)

    def test_badger_wins(self):
        # bee win
        hb1 = Pet("badger")
        hb1.status = "status-honey-bee"
        b2 = Pet("badger")
        b = Battle(Team([hb1]), Team([b2]))
        r = b.battle()
        self.assertEqual(r, 0)

        # badger with higher priority hits nothing with ability, zombie-cricket spanws and wins
        c1 = Pet("cricket")
        c1._attack = 4
        b1 = Pet("badger")
        b = Battle(Team([c1]), Team([b1]))
        r = b.battle()
        self.assertEqual(r, 0)

        # badger with less attack can kill zombie-cricket, then bee spawns
        hb1 = Pet("badger")
        hb1.status = "status-honey-bee"
        c1 = Pet("cricket")
        c1._attack = 6
        b = Battle(Team([hb1]), Team([c1]))
        r = b.battle()
        self.assertEqual(r, 0)

    def test_rat_summons_at_front(self):
        team1 = Team(["rat", "blowfish"])
        fish = Pet("fish")
        fish._attack = 5
        big_attack_pet = Pet("beaver")
        big_attack_pet._attack = 50
        team2 = Team([fish, big_attack_pet])

        test_battle = Battle(team1, team2)
        result = test_battle.battle()
        self.assertEqual(result, 0)

    def test_peacock(self):
        ### Check that peacock attack is correct after battle

        ### Check peacock attack after elephant for all three levels

        ### Check peacock after headgehog on both teams

        ### Implement later with others
        pass


# %%
