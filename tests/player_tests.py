
#%%

import os,shutil,zlib
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team,TeamSlot
from sapai.shop import Shop
from sapai.battle import Battle
from sapai.graph import graph_battle

#%%

%run /Users/ibier/Software/sapai/sapai/player.py

pack = "StandardPack"
# pack="ExpansionPack1"

##############################################
##### Buying 3 animals 
##############################################
# player = Player(pack=pack)
# print(player)
# player.buy_pet(player.shop[0])
# player.buy_pet(player.shop[0])
# player.buy_pet(player.shop[0])
# print(player)

##############################################
##### Buying 2 animals and 1 food
##############################################
# player = Player(pack=pack)
# print(player)
# player.buy_pet(player.shop[0])
# player.buy_pet(player.shop[0])
# player.buy_food(player.shop[-1], 
#                 player.team[0])
# player.sell(player.team[0])
# print(player)

##############################################
##### Checking freeze behavior
##############################################
# player = Player(pack=pack)
# player.freeze(0)
# print(player)
# player.shop.roll()
# print(player)


##############################################
#### Checking buy_combine behavior
##############################################
# player = Player(shop=["ant", "fish", "fish", "apple"], 
#                 team=["fish", "ant"], 
#                 pack=pack)
# print(player)
# player.buy_combine(player.shop[1], player.team[0])
# print(player)
# player.buy_combine(player.shop[1], player.team[0])
# print(player)

# player = Player(shop=["ant", "octopus", "octopus", "apple"], 
#                 team=["octopus", "ant"], 
#                 pack=pack)
# print(player)
# player.buy_combine(player.shop[1], player.team[0])
# print(player)
# player.buy_combine(player.shop[1], player.team[0])
# print(player)

##############################################
#### Checking combine behavior
##############################################
# player = Player(shop=["ant", "fish", "fish", "apple"], 
#                 team=["fish", "fish", "fish", "horse"], 
#                 pack=pack)
# print(player)
# player.combine(player.team[0], player.team[1])
# player.combine(player.team[0], player.team[2])
# print(player)

##############################################
#### Checking Cat behavior
##############################################
# player = Player(shop=["ant", "fish", "fish", "pear"], 
#                 team=["fish", "cat"], 
#                 pack=pack)
# print(player)
# player.buy_food(player.shop[-1],player.team[0])
# print(player)

##############################################
#### Checking start of turn behavior
##############################################
# player = Player(shop=["ant", "fish", "fish", "pear"], 
#                 team=["dromedary", "swan", "caterpillar", "squirrel"], 
#                 pack=pack)
# player.team[0]._pet.level = 2
# print(player)
# player.start_turn()
# print(player)


##############################################
#### Checking end-of-turn behavior
##############################################
# ["bluebird", "hatching-chick", "giraffe", "puppy", "tropical-fish", 
# "bison", "llama", "penguin", "parrot", "monkey", "poodle", 
# "tyrannosaurus"]

# player = Player(shop=["ant", "fish", "fish", "pear"], 
#                 team=["bluebird", "hatching-chick", "giraffe", "puppy"], 
#                 pack=pack)
# print(player)
# player.end_turn()
# print(player)

# player = Player(shop=["ant", "fish", "fish", "pear"], 
#                 team=["bison", "tropical-fish", "penguin", "llama"],
#                 pack=pack)
# player.team[0]._pet.level=3
# print(player)
# player.end_turn()
# print(player)

# player = Player(shop=["ant", "fish", "fish", "pear"], 
#                 team=["parrot", "monkey", "poodle", "tyrannosaurus"],
#                 pack=pack)
# print(player)
# player.end_turn()
# print(player)


##############################################
#### Checking pill behavior
##############################################
["ant", "cricket", "flamingo", "hedgehog", "spider", "badger", 
 "ox", "sheep", "turtle", "deer", "rooster", "microbe", 
 "eagle", "shark", "fly", "mammoth"]

player = Player(shop=["ant", "fish", "fish", "food-sleeping-pill"], 
                team=["rooster", "ant", "cricket", "sheep"], 
                pack=pack)
print(player)
player.buy_food(player.shop[-1], player.team[1])
print(player)

## Check multi-faints
player = Player(shop=["ant", "fish", "fish", "food-sleeping-pill"], 
                team=["hedgehog", "ant", "ox", "sheep", "dragon"], 
                pack=pack)
# player.team[0]._pet.level=1
print(player)
player.buy_food(player.shop[-1], player.team[0])
print(player)

### Check deer, microbe, and shark
player = Player(shop=["ant", "fish", "fish", "food-sleeping-pill"], 
                team=["deer", "microbe", "eagle", "shark"], 
                pack=pack)
# player.team[0]._pet.level=1
print(player)
player.buy_food(player.shop[-1], player.team[2])
print(player)

### Check deer, badger, fly, sheep
player = Player(shop=["ant", "fish", "fish", "food-sleeping-pill"], 
                team=["deer", "badger", "sheep", "fly"], 
                pack=pack)
# player.team[0]._pet.level=1
print(player)
player.buy_food(player.shop[-1], player.team[1])
print(player)

#%%

#%%

#%%
 

# %%
