
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
# from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team,TeamSlot
from sapai.battle import Battle
from sapai.graph import graph_battle
from sapai.shop import Shop
from sapai.player import Player
from sapai.effects import get_target,get_effect_function


def get_print_str(pets):
    n = []
    trigger_list = []
    triggerby_list = []
    effect_kind_list = []
    effect_target_kind_list = []
    for iter_idx,pet in enumerate(pets):
        n.append(iter_idx)
        trigger_list.append(pet.ability["trigger"])
        triggerby_list.append(pet.ability["triggeredBy"]["kind"])
        effect_kind_list.append(pet.ability["effect"]["kind"])
        if "target" in pet.ability["effect"]:
            effect_target_kind_list.append(pet.ability["effect"]["target"]["kind"])
        else:
            effect_target_kind_list.append("NONE")

    str_fmt = "{:3s}{:15s}{:15s}{:15s}{:20s}{:20s}\n"
    print_str = str_fmt.format("N", "Pet", "Trigger", "TriggerBy", "EffectKind", "EffectTarget")
    print_str += "-------------------------------------------------------------------------------\n"
    for iter_idx in range(len(test_pet_names)):
        print_str += str_fmt.format(
                                str(n[iter_idx]),
                                test_pet_names[iter_idx],
                                trigger_list[iter_idx],
                                triggerby_list[iter_idx],
                                effect_kind_list[iter_idx],
                                effect_target_kind_list[iter_idx])
    
    return print_str

# t = Team([Pet("fish"), Pet("dragon"), Pet("cat"), Pet("sheep")])
#%%

################################################################################
##### Testing all start-of-turn pets
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_pet_names = ["dromedary", "swan", "caterpillar", "squirrel"]
pets = [Pet(x, shop=Shop(), team=Team(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.sot_trigger()
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)


# %%

################################################################################
##### Testing all sell_trigger pets
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_team = Team([Pet("dragon"), Pet("cat"), Pet("horse")])

test_pet_names = ["beaver", "duck", "pig", "shrimp", "owl"]
pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

### Sell Self
test_bool_list = [True, True, True, False, True]
for iter_idx,pet in enumerate(pets):
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.sell_trigger(pet)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)
    

### Sell other
pets = [Pet(x, shop=Shop(), team=test_team.copy()) for x in test_pet_names]
test_bool_list = [False, False, False, True, False]
for iter_idx,pet in enumerate(pets):
    activated_bool,targets,possible = pet.sell_trigger(pet.team[0].pet)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))

# %%

################################################################################
##### Testing all buy_food_trigger pets
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_team = Team([Pet("dragon"), Pet("cat")])

test_pet_names = ["beetle", "ladybug", "tabby-cat", "rabbit", "worm", "seal", 
                    "sauropod"]
pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

### Buy food for self
for pet in pets:
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.buy_food_trigger(pet)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

### Buy food for other
test_bool_list = [False, True, False, True, False, False, True]
# n = 3
# test_bool_list = test_bool_list[n:]
# pets = pets[n:]
for iter_idx,pet in enumerate(pets):
    activated_bool,targets,possible = pet.buy_food_trigger(pet.team[0].pet)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))
    

# %%

################################################################################
##### Testing all buy_friend_trigger pets
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

test_pet_names = ["otter", "crab", "snail", "buffalo", "chicken", "cow", 
                    "goat", "dragon"]
pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

### Buy friend as self
test_bool_list = [True, True, True, False, False, True, False, False]
for iter_idx,pet in enumerate(pets):
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.buy_friend_trigger(pet)
    if activated_bool != test_bool_list[iter_idx]:
        if pet.name == "pet-snail":
            continue
        raise Exception("Incorrect activation for pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

### Buy other friend tier1
test_bool_list = [False, False, False, True, True, False, True, True]
# n = 7
# test_bool_list = test_bool_list[n:]
# pets = pets[n:]
for iter_idx,pet in enumerate(pets):
    activated_bool,targets,possible = pet.buy_friend_trigger(pet.team[0].pet)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))
    
### Buy other friend not tier1
test_bool_list = [False, False, False, True, False, False, True, False]
for iter_idx,pet in enumerate(pets):
    activated_bool,targets,possible = pet.buy_friend_trigger(pet.team[1].pet)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))

# %%


################################################################################
##### Testing all friend_summoned_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

test_pet_names = ["horse", "dog", "lobster", "turkey"]
pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.friend_summoned_trigger(pet.team[0].pet)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)


# %%


################################################################################
##### Testing all levelup_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])

test_pet_names = ["fish", "octopus"]
pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.levelup_trigger(pet.team[0].pet)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

# %%


################################################################################
##### Testing all eot_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")])
test_team[0].pet.level = 3
player = Player()

test_pet_names = [
            "bluebird", "hatching-chick", "giraffe", "puppy", "tropical-fish", 
             "bison", "llama", "penguin", "parrot", "monkey", "poodle", 
             "tyrannosaurus"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=player) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.eot_trigger(pet.team[0].pet)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)
    
# %%


################################################################################
##### Testing all faint_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py
from sapai.compress import compress,decompress

test_team = Team([Pet("fish")], battle=True)
cteam = compress(test_team)
test_pet_names = ["ant", "cricket", "flamingo", "hedgehog", "spider", "badger", 
             "ox", "sheep", "turtle", "deer", "rooster", "microbe", 
             "eagle", "shark", "fly", "mammoth"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

### Self faint
test_bool_list = [True, True, True, True, True, 
                  True, False, True, True, True,
                  True, True, True, False, False, 
                  True]
for iter_idx,pet in enumerate(pets):
    pet.team.append(Pet("tiger"))
    trigger = decompress(cteam)
    print("###################################################################")
    print(pet)
    print(pet.player)
    te_idx = [0,pet.team.index(pet)]
    activated_bool,targets,possible = pet.faint_trigger(pet,te_idx)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)
    
### Friend ahead faints
pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
test_bool_list = [False, False, False, False, False, 
                  False, True, False, False, False,
                  False, False, False, True, True, 
                  False]
for iter_idx,pet in enumerate(pets):
    pet.team.append(Pet("tiger"))
    
    print("###################################################################")
    print(pet)
    print(pet.player)
    
    friend_ahead = pet.team.get_ahead(pet)[0]
    te_idx = [0,pet.team.index(friend_ahead)]
    activated_bool,targets,possible = pet.faint_trigger(friend_ahead,te_idx)
    if activated_bool != test_bool_list[iter_idx]:
        raise Exception("Incorrect activation for pet {}".format(pet))
    
    print(targets)
    print(possible)
    print(pet.player)

# %%

################################################################################
##### Testing all start-of-battle triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py
from sapai.compress import compress,decompress

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")], battle=True)
cteam = compress(test_team)
player = Player()

test_pet_names = ["mosquito", "bat", "whale", "dolphin", "skunk", "crocodile", 
                    "leopard"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    pet.team.append(Pet("tiger"))
    trigger = decompress(cteam)
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.sob_trigger(trigger)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

# %%


################################################################################
##### Testing all before_attack_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py
from sapai.compress import compress,decompress

test_team = Team([Pet("fish"), Pet("dragon"), Pet("cat")], battle=True)
cteam = compress(test_team)
player = Player()

test_pet_names = ["elephant", "boar", "octopus"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
pets[-1].level = 3
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    pet.team.append(Pet("tiger"))
    trigger = decompress(cteam)
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.before_attack_trigger(trigger)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)


# %%

################################################################################
##### Testing all after_attack_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py
from sapai.compress import compress,decompress

test_team = Team([Pet("fish")], battle=True)
cteam = compress(test_team)
player = Player()

test_pet_names = ["kangaroo","snake"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
pets[-1].level = 3
print_str = get_print_str(pets)
print(print_str)


for pet in pets:
    pet.team.append(Pet("tiger"))
    trigger = decompress(cteam)
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.after_attack_trigger(trigger)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

#%%

################################################################################
##### Testing all hurt_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py
from sapai.compress import compress,decompress

test_team = Team([Pet("fish")], battle=True)
cteam = compress(test_team)
player = Player()

test_pet_names = ["peacock", "blowfish", "camel", "gorilla"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    pet.team.append(Pet("tiger"))
    trigger = decompress(cteam)
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.hurt_trigger(trigger)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

# %%

################################################################################
##### Testing all knockout_trigger triggers
################################################################################

%run /Users/ibier/Software/sapai/sapai/pets.py
from sapai.compress import compress,decompress

test_team = Team([Pet("fish")], battle=True)
cteam = compress(test_team)
player = Player()

test_pet_names = ["hippo", "rhino"]

pets = [Pet(x, shop=Shop(), team=test_team.copy(), player=Player()) for x in test_pet_names]
print_str = get_print_str(pets)
print(print_str)

for pet in pets:
    pet.team.append(Pet("tiger"))
    trigger = decompress(cteam)
    print("###################################################################")
    print(pet)
    print(pet.player)
    activated_bool,targets,possible = pet.knockout_trigger(trigger)
    if activated_bool == False:
        raise Exception("Non-activated pet {}".format(pet))
    print(targets)
    print(possible)
    print(pet.player)

    
# %%

# %%
