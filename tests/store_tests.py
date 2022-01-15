
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team,TeamSlot
from sapai.fight import Fight
from sapai.graph import graph_fight


#%%

%run /Users/ibier/Software/sapai/sapai/store.py

slot = StoreSlot("pet")
slot.item = Pet("ant")
print(slot)
slot.roll()
print(slot)
slot = StoreSlot("food")
slot.item = Food("apple")
print(slot)
slot.roll()
print(slot)
# s = Store()

slot = StoreSlot("levelup")
print(slot)

#%%

%run /Users/ibier/Software/sapai/sapai/store.py
s = Store()
print(s)

s.freeze(0)
print(s)

for i in range(10):
    s.roll()
    print(s)

# %%
