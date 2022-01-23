
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team
from sapai.graph import graph_battle
from sapai.battle import Battle

%load_ext line_profiler

#%%

################################################################################
####### Testing battle reproducibility
################################################################################
state = np.random.RandomState(seed = 4).get_state()
state2 = np.random.RandomState(seed = 4).get_state()

for i in range(20):
    t0 = Team(["ant","ant", "fish"],seed_state = state)
    t1 = Team(["ant","ant","fish"],seed_state = state2)

    b = Battle(t0, t1)
    winner = b.battle()
    # Same state should result in draw
    print(winner)
