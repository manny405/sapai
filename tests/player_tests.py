
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team,TeamSlot
from sapai.shop import Shop
from sapai.fight import Fight
from sapai.graph import graph_fight

#%%

%run /Users/ibier/Software/sapai/sapai/player.py

# player = Player(pack="StandardPack")
player = Player(pack="ExpansionPack1")
print(player)

#%%

# %%
