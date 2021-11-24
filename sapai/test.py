
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from data import data
from pets import Pet
from foods import Food
from store import Store
from teams import Team,TeamSlot
from fight import Fight
            
# %%

f0 = Food()
f1 = Food("honey")
f2 = Food("apple")
f3 = Food("steak")
p0 = Pet()
p1 = Pet("pet-ant")
p2 = Pet("pet-dodo")
p3 = Pet("pet-dragon")
p4 = Pet("pet-dragon")
p4.health += 1
p1.eat(f1)
p1.eat(f2)
p1.eat(f3)
ts = TeamSlot(p1)
t = Team()
print(t)
print(len(t))
print(ts)

# %%

t[0] = p1
t[1] = p2
t[2] = p3
t[4] = p4
print(t)

# %%

f = Fight(t, t)

    
# %%
