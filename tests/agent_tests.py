
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team
from sapai.fight import Fight
from sapai.graph import graph_fight

%load_ext line_profiler

#%%

%run /Users/ibier/Software/sapai/sapai/agents.py

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

print(ranker.test_against_database(values[min_frac]["team"]))

#%%


# %%

# t0 = Team(["cricket"])
# t1 = Team(["horse"])
# t0 = values[max_idx]["team"]
# t1 = values[min_idx]["team"]
t0 = ranker.t0
t1 = ranker.t1
f = Fight(t0,t1)
winner = f.fight()
graph_fight(f, "test")

# %%
