
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team,TeamSlot
from sapai.battle import Battle
from sapai.graph import graph_battle


#%%

%run /Users/ibier/Software/sapai/sapai/shop.py

slot = ShopSlot("pet")
slot.item = Pet("ant")
print(slot)
slot.roll()
print(slot)
slot = ShopSlot("food")
slot.item = Food("apple")
print(slot)
slot.roll()
print(slot)
# s = Shop()

slot = ShopSlot("levelup")
print(slot)

#%%

%run /Users/ibier/Software/sapai/sapai/shop.py
s = Shop(turn=11)
print(s)

s.freeze(0)
print(s)

for i in range(10):
    s.roll()
    print(s)

# %%
