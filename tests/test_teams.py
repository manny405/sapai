# %%
import unittest
import numpy as np

from sapai import *
from sapai.compress import compress, decompress

MIN = -5
MAX = 20
pet_names = list(data["pets"].keys())


class TestLists(unittest.TestCase):
    def test_team(self):
        l = Team([Pet(pet_names[x]) for x in range(3)])


# %%

# test = TestLists()
# test.test_remove()

# %%
