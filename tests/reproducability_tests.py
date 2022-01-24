
#%%

import os,shutil,json
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")
    
from sapai.compress import compress,decompress
from sapai import Team
from sapai.graph import graph_battle
from sapai.battle import Battle
from sapai.shop import Shop

%load_ext line_profiler

#%%

################################################################################
####### Testing battle reproducibility
################################################################################
state = np.random.RandomState(seed=4).get_state()
state2 = np.random.RandomState(seed=4).get_state()

#### Random result
winner_list = []
for i in range(20):
    t0 = Team(["ant","ant", "fish"])
    t1 = Team(["ant","ant","fish"])
    b = Battle(t0, t1)
    winner = b.battle()
    # Same state should result in draw
    winner_list.append(winner)
print("RAND: {}".format(np.unique(winner_list, return_counts=True)))
    
#### Deterministic result
winner_list = []
for i in range(20):
    t0 = Team(["ant","ant","fish"],seed_state=state)
    t1 = Team(["ant","ant","fish"],seed_state=state2)
    b = Battle(t0, t1)
    winner = b.battle()
    # Same state should result in draw
    winner_list.append(winner)
print("SEED: {}".format(np.unique(winner_list, return_counts=True)))


### Ensure deterministic results after compress and decompress teams
winner_list = []
for i in range(20):
    t0 = Team(["ant","ant","fish"],seed_state=state)
    t1 = Team(["ant","ant","fish"],seed_state=state2)
    
    t0 = decompress(compress(t0))
    t1 = decompress(compress(t1))

    b = Battle(t0, t1)
    winner = b.battle()
    # Same state should result in draw
    winner_list.append(winner)
print("TEST COMPRESSION: {}".format(np.unique(winner_list, return_counts=True)))
    
#%%

################################################################################
####### Testing Shop reproducibility
################################################################################
state = np.random.RandomState(seed=20).get_state()
s = Shop(turn=11,seed_state=state)

#s.freeze(0)
#print(s)

#### Setup solution
shop_check_list = []
s = Shop(turn=11,seed_state=state)
for i in range(10):
    names = []
    for slot in s:
        names.append(slot.item.name)
    names = tuple(names)
    shop_check_list.append(names)
    s.roll()
shop_check_list = tuple(shop_check_list)

#### Run check for reproducibility
for i in range(10):
    s = Shop(turn=11,seed_state=state)
    temp_check_list = []
    for i in range(10):
        names = []
        for slot in s:
            names.append(slot.item.name)
        names = tuple(names)
        temp_check_list.append(names)
        s.roll()
    if tuple(temp_check_list) != shop_check_list:
        raise Exception("Shop did not match")
    
### Ensure that runs are reproducible after compression and decompression
for i in range(10):
    s = Shop(turn=11,seed_state=state)
    s = decompress(compress(s))
    temp_check_list = []
    for i in range(10):
        names = []
        for slot in s:
            names.append(slot.item.name)
        names = tuple(names)
        temp_check_list.append(names)
        s.roll()
    if tuple(temp_check_list) != shop_check_list:
        raise Exception("Shop did not match")

# %%
