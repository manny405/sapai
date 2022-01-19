
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai import data
from sapai import Pet,Shop,Food
from sapai.teams import Team,TeamSlot
from sapai.compress import compress,decompress


#%%

################################################################################
##### Testing get_target function
################################################################################
%run /Users/ibier/Software/sapai/sapai/effects.py

shop = Shop()
shop.roll()
t0 = Team(["fish", "dragon", "owl", "ant", "badger"], shop=shop)
t1 = Team(["cat", "hippo", "horse", "ant"], shop=shop)
for slot in t0:
    slot.pet.shop = shop
for slot in t1:
    slot.pet.shop = shop
t1[0].pet.health = 7
t0[0].pet.level = 2
t0[1].pet.level = 3
t0[0].pet.health = 8

apet=t0[0].pet
apet_idx=[0,3]
teams=[t0,t1]
te=None
fixed_targets=[]
get_from=False

# print("----------------------------------------")
# test_kind="AdjacentAnimals"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("AdjacentAnimals")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="AdjacentFriends"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("AdjacentFriends")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="All"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("All")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="DifferentTierAnimals"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("DifferentTierAnimals")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))


# print("----------------------------------------")
# test_kind="EachEnemy"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("EachEnemy")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="EachFriend"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("EachFriend")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="EachShopAnimal"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("EachShopAnimal")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="FirstEnemy"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("FirstEnemy")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="FriendAhead"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("FriendAhead")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))


# print("----------------------------------------")
# test_kind="FriendBehind"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("FriendBehind")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="HighestHealthEnemy"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("HighestHealthEnemy")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="LastEnemy"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("LastEnemy")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="LeftMostFriend"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("LeftMostFriend")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))


# print("----------------------------------------")
# test_kind="Level2And3Friends"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("Level2And3Friends")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))


# print("----------------------------------------")
# test_kind="LowestHealthEnemy"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("LowestHealthEnemy")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="RandomEnemy"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("RandomEnemy")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="RandomFriend"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("RandomFriend")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="RightMostFriend"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("RightMostFriend")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="Self"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("Self")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="StrongestFriend"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("StrongestFriend")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="HighestHealthFriend"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("HighestHealthFriend")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="TriggeringEntity"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("TriggeringEntity")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))

# print("----------------------------------------")
# test_kind="none"
# t,p = get_target(apet,apet_idx,teams,te,fixed_targets,get_from,test_kind)
# print("none")
# print("{:10s}{}".format("CHOSEN: ", t))
# print("{:10s}{}".format("POSSIBLE: ", p))


#%%

#%%

################################################################################
##### Testing all functions
################################################################################
%run /Users/ibier/Software/sapai/sapai/effects.py

all_func = [x for x in func_dict.keys()]
pet_func = {}
for pet,fd in data["pets"].items():
    if "level1Ability" not in fd:
        continue
    kind = fd["level1Ability"]["effect"]["kind"]
    if kind not in pet_func:
        pet_func[kind] = []
    pet_func[kind].append(pet)
    

shop = Shop()
shop.roll()
base_team = Team(["fish", "dragon"])
for slot in base_team:
    slot.pet.shop = shop
    slot.pet.team = base_team
tc = compress(base_team)
for func_name in all_func:
    print("###############################################")
    print(func_name)
    if func_name not in pet_func:
        continue
    for pet in pet_func[func_name]:
        temp_team = decompress(tc)
        temp_team.append(pet)
        temp_team[2].pet.shop = shop
        temp_team.append("bison")
        temp_team[3].pet.shop = shop
        temp_enemy_team = decompress(tc)
        func = get_effect_function(temp_team[2])
        apet = temp_team[2].pet
        apet_idx = [0,2]
        teams = [temp_team,temp_enemy_team]
        te = temp_team[2].pet
        te_idx = [0,2]
        fixed_targets=[]
        
        # teams[0].remove(apet)
        if func_name == "RepeatAbility":
            te = temp_team[1].pet
        if func_name == "FoodMultiplier":
            te = Food("pear")
        targets,possible = func(apet,apet_idx,teams,te,te_idx,fixed_targets)
        
        print("-------------------------")
        print("PET", pet)
        print(temp_team)
        print(temp_enemy_team)
        print("TARGETS: ", targets)
        print("POSSIBLE: ",possible)

# %%

################################################################################
###### Tiger Test
################################################################################

from sapai import data
from sapai import Pet,Shop,Food,Team

#%%

t = Team(["spider", "tiger"], fight=True)
print(t)
slot_list = [x for x in t]
for slot in slot_list:
    slot.pet.faint_trigger(slot.pet)
    print(t)

# %%
