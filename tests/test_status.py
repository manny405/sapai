#%%
import unittest
import numpy as np

from sapai import *
from sapai.compress import compress, decompress
from sapai.status import *

#%%

MIN = -10
MAX = 100


class TestStatus(unittest.TestCase):
    def test_damage(self):
        p = Pet("fish")
        for i in range(MIN, 0):
            assert p.get_damage(i) == 0
        for i in range(0, MAX):
            assert p.get_damage(i) == i

    def test_garlic_damage(self):
        p = Pet("fish")
        p.eat(Food("garlic"))
        for i in range(MIN, 0):
            assert p.get_damage(i) == 0
        for i in range(1, 3):
            assert p.get_damage(i) == 1
        for i in range(3, MAX):
            assert p.get_damage(i) == (i - 2)

    def test_melon_damage(self):
        p = Pet("fish")
        p.eat(Food("melon"))
        for i in range(MIN, 20):
            assert p.get_damage(i) == 0
        for i in range(21, MAX):
            assert p.get_damage(i) == (i - 20)

    def test_coconut_damage(self):
        p = Pet("fish")
        p.status = "status-coconut-shield"
        for i in range(MIN, MAX):
            assert p.get_damage(i) == 0

    def test_weak(self):
        p = Pet("fish")
        p.status = "status-weak"
        for i in range(MIN, 1):
            assert p.get_damage(i) == 0
        for i in range(1, MAX):
            assert p.get_damage(i) == i + 3


#%%
