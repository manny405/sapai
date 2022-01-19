
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
from sapai.shop import Shop, ShopSlot
from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team,TeamSlot
from sapai.fight import Fight
from sapai.graph import graph_fight


#%%


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
# s = Store()

slot = ShopSlot("levelup")
print(slot)

#%%

s = Shop()
print(s)
s.freeze(0)
print(s)
s.roll()
print(s)
s.roll()
print(s)
s.roll()
print(s)

#for i in range(10):
#    s.roll()
#    print(s)

# %%
