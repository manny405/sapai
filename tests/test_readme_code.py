import unittest

from sapai import *


class TestReadMeCode(unittest.TestCase):
    def test_pet_creation(self):
        pet = Pet("ant")
        pet._attack += 3
        pet.gain_experience()

    def test_team_move(self):
        team0 = Team(["ant", "ox", "tiger"])
        team1 = Team(["sheep", "tiger"])
        team0.move(1, 4)
        team0.move_forward()

    def test_running_battle(self):
        team0 = Team(["ant", "ox", "tiger"])
        team1 = Team(["sheep", "tiger"])
        battle = Battle(team0, team1)
        winner = battle.battle()
        print(winner)
