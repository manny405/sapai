
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team
from sapai.battle import Battle
from sapai.graph import graph_battle
from sapai.agents import DatabaseLookupRanker,CombinatorialAgent

#%%

ranker = DatabaseLookupRanker()

#%%

agent = CombinatorialAgent(ranker=ranker)
cstate = compress(agent.player)
for i in range(100):
    agent.player = decompress(cstate)
    agent.train()
    if i % 10 == 0:
        print(i)
        
# Player.from_state(agent.current_state)
# %lprun -f ranker.run_database _ = agent.train()

# %%

results = []
values = []
total_list = []
for x in ranker.team_database.values():
    values.append(x)
    wins = x["wins"]
    total = x["total"]
    frac = wins/total
    results.append(frac)
    total_list.append(total)
    
max_idx = np.argmax(results)
max_frac = results[max_idx]
min_idx = np.argmin(results)
print(max_frac)
print(values[max_idx])
print(len(ranker.team_database))
print(values[min_idx])
print(total_list)
    
#%%

