
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.store import Store
from sapai.teams import Team,TeamSlot
from sapai.fight import Fight
from sapai.graph import graph_fight

#%%

################################################################################
##### Testing Pet state implementation
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

p = Pet("ant")
p.level = 3
state = p.state
test = Pet.from_state(state)
print(p, test)

#%%

################################################################################
##### Testing Food state implementation
################################################################################

%run /Users/ibier/Software/sapai/sapai/foods.py

f = Food("melon")
state = f.state
test = Food.from_state(state)
print(f, test)

# %%

################################################################################
##### Testing Team state implementation
################################################################################

%run /Users/ibier/Software/sapai/sapai/teams.py

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])
test_team[0].pet.level = 3
state = test_team.state
state_team = Team.from_state(state)

# %%

################################################################################
##### Testing Shop state implementation
################################################################################

%run /Users/ibier/Software/sapai/sapai/shop.py

sl = ShopSlot("pet")
sl.roll()
print(sl)
state = sl.state
test = ShopSlot.from_state(state)
print(test)

s = Shop()
state = s.state
state_shop = Shop.from_state(state)
print(s)
print(state_shop)

#%%

################################################################################
##### Testing Player state implementation
################################################################################

%run /Users/ibier/Software/sapai/sapai/player.py

p = Player(team=Team(["ant", "fish", "dragon"]))
state = p.state
state_p = Player.from_state(state)
print(p)
print(state_p)

# %%

################################################################################
##### Testing compression
################################################################################

%run /Users/ibier/Software/sapai/sapai/compress.py

test = compress(s)
test_shop = decompress(test)

test = compress(p)
test_player = decompress(test)
print(test_player)

# %%
