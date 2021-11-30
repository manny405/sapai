
#%%

import os,shutil
import numpy as np
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

from sapai.data import data
from sapai.pets import Pet
from sapai.foods import Food
from sapai.store import Store
from sapai.teams import Team,TeamSlot
from sapai.fight import Fight
from sapai.graph import graph_fight


#%%


### Testing variety of fight effects

a = Pet("pet-ant")
b = Pet("pet-badger")
f = Pet("pet-fish")
t = Pet("pet-tiger")
snake = Pet("pet-snake")
k = Pet("pet-kangaroo")
m = Pet("pet-mosquito")
s = Pet("pet-sheep")
w = Pet("pet-whale")
spider = Pet("pet-spider")
r = Pet("pet-rhino")
e = Pet("pet-elephant")
d = Pet("pet-dragon")
d.health += 1

honey = Food("honey")
melon = Food("melon")
chili = Food("chili")
spider.eat(melon)

# %%

#%%

t0 = Team([b,t.copy(),s])
# t0[1].pet.eat(chili)
t1 = Team([s,w,t.copy()])
# t1[2].pet.eat(melon)
f = Fight(t0,t1)
print("WINNER", f.fight())

#%%

g = graph_fight(f, "test")

#%%
 

################################################################################
#### Testing the README commands
################################################################################

#%%

from sapai.pets import Pet
pet = Pet("ant")
print(pet)
pet.attack += 3
print(pet)
print(pet.ability)

# %%

from sapai.pets import Pet
from sapai.teams import Team
ant = Pet("ant")
ox = Pet("ox")
tiger = Pet("tiger")
sheep = Pet("sheep")
team0 = Team([ant,ox,tiger])
team1 = Team([sheep,tiger])
print(team0)
print(team1)
team0.move(2,4)
print(team0)
team0.move_forward()
print(team0)

# %%

### Using the teams created in the last section
from sapai.fight import Fight
fight = Fight(team0,team1)
winner = fight.fight()
print(winner)
    
    
# %%

from sapai.pets import Pet
from sapai.teams import Team
from sapai.fight import Fight
ant = Pet("ant")
ox = Pet("ox")
tiger = Pet("tiger")
sheep = Pet("sheep")
team0 = Team([ant,ox,tiger])
team1 = Team([sheep,tiger])

def timing_test():
    f = Fight(team0,team1)
    winner = f.fight()

%timeit timing_test()      

# %%


from sapai.graph import graph_fight
graph_fight(fight, file_name="Example")

# %%
