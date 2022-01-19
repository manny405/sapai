
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team
from sapai.graph import graph_battle

%load_ext line_profiler

#%%

%run /Users/ibier/Software/sapai/sapai/battle.py 

t0 = Team(["ant", "ant", "horse"])

t1 = Team(["cricket", "horse", "mosquito", "tiger"])

print(t0)
print(t1)

f = Battle(t0, t1)
f.battle()
graph_battle(f)

# %%

print(t0)
print(t1)

# %%
