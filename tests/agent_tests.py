
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team,Player
from sapai.shop import ShopLearn
from sapai.battle import Battle
from sapai.graph import graph_battle
from sapai.agents import DatabaseLookupRanker,CombinatorialSearch,PairwiseBattles

#%%

################################################################################
##### Test default initialization
################################################################################
cs = CombinatorialSearch()
dlr = DatabaseLookupRanker()
pb = PairwiseBattles()

#%%

################################################################################
##### Testing CombinatorialSearch methods
################################################################################

turn=1
player = Player(team=["ant", "fish", "beaver", "cricket", "horse"],
                shop=ShopLearn(turn=turn),
                turn=turn)
cs = CombinatorialSearch()
avail_actions = cs.avail_actions(player)

for temp_action in avail_actions:
    if len(temp_action) == 0:
        temp_name = "None"
    else:
        temp_name = temp_action[0].__name__
        
    if len(temp_action) > 1:
        temp_inputs = temp_action[1:]
    else:
        temp_inputs = []
        
    print(temp_name, temp_inputs)

# %%

################################################################################
##### Testing simple CombinatorialSearch
################################################################################
%run /Users/ibier/Software/sapai/sapai/agents.py

turn=1
player = Player(shop=ShopLearn(turn=turn),
                turn=turn)
player.gold = 6
cs = CombinatorialSearch()
player_list,team_dict = cs.search(player)

# %load_ext line_profiler
# %lprun -f cs.build_player_list cs.search(player)

# %%
