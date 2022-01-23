
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team
from sapai.battle import Battle
from sapai.graph import graph_battle

# %load_ext line_profiler

#%%

################################################################################
####### Testing multi-hurt 
################################################################################
# %run /Users/ibier/Software/sapai/sapai/battle.py 

t0 = Team(["badger", "camel", "fish"])
t0[0].pet._health = 1
t0[0].pet._attack = 1 
t1 = Team(["cricket", "horse", "mosquito", "tiger"])

print(t0)
print(t1)

b = Battle(t0, t1)
b.battle()
graph_battle(b)

# %%

################################################################################
####### Testing multi-faint
################################################################################
# %run /Users/ibier/Software/sapai/sapai/battle.py 

t0 = Team(["badger", "camel", "fish"])
t0[0].pet._health = 1
t0[0].pet._attack = 5
t1 = Team(["cricket", "horse", "mosquito", "tiger"])

print(t0)
print(t1)

b = Battle(t0, t1)
b.battle()
graph_battle(b)

# %%


################################################################################
####### Testing before and after attack
################################################################################
# %run /Users/ibier/Software/sapai/sapai/battle.py 

t0 = Team(["elephant", "snake", "dragon", "fish"])
t1 = Team(["cricket", "horse", "fly", "tiger"])
t0[2]._health = 50
print(t0)
print(t1)

b = Battle(t0, t1)
b.battle()
graph_battle(b)

# %%

################################################################################
####### Rhino test
################################################################################
# %run /Users/ibier/Software/sapai/sapai/battle.py 

t0 = Team(["horse", "horse", "horse", "horse"])
t1 = Team(["rhino", "tiger"])
print(t0)
print(t1)

b = Battle(t0, t1)
b.battle()
graph_battle(b)

# %%


################################################################################
####### Hippo test
################################################################################
# %run /Users/ibier/Software/sapai/sapai/battle.py 

t0 = Team(["horse", "horse", "horse", "horse"])
t1 = Team(["hippo", "tiger"])
print(t0)
print(t1)

b = Battle(t0, t1)
b.battle()
graph_battle(b)

# %%

# %%

# %%
