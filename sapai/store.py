

#%%

import numpy as np
from data import data
from foods import Food
from pets import Pet

#%%

################################################################################
#### Building optimized datastructures for construction shop states
################################################################################

pet_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
pet_tier_lookup_std = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in data["pets"].items():
    if type(value["tier"]) == int:
        pet_tier_lookup[value["tier"]].append(key)
        if "StandardPack" in value["packs"]:
            pet_tier_lookup_std[value["tier"]].append(key)
pet_tier_avail_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in pet_tier_lookup.items():
    for temp_key,temp_value in pet_tier_avail_lookup.items():
        if temp_key >= key:
            temp_value += value
            
food_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in data["foods"].items():
    if type(value["tier"]) == int:
        food_tier_lookup[value["tier"]].append(key)
food_tier_avail_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in food_tier_lookup.items():
    for temp_key,temp_value in food_tier_avail_lookup.items():
        if temp_key >= key:
            temp_value += value
            
turn_prob_pets_std = {}
turn_prob_pets_exp = {}
for i in np.arange(0,12):
    turn_prob_pets_std[i] = {}
    turn_prob_pets_exp[i] = {}
for key,value in data["pets"].items():
    if "probabilities" not in value:
        continue
    if data["pets"][key]["probabilities"] == "none":
        continue
    for temp_dict in data["pets"][key]["probabilities"]:
        temp_turn = int(temp_dict["turn"].split("-")[-1])
        if "StandardPack" in temp_dict["perSlot"]:
            temp_std = temp_dict["perSlot"]["StandardPack"]
            turn_prob_pets_std[temp_turn][key] = temp_std
        if "ExpansionPack1" in temp_dict["perSlot"]:
            temp_exp = temp_dict["perSlot"]["ExpansionPack1"]
            turn_prob_pets_exp[temp_turn][key] = temp_exp
        else:
            ### Assumption, if expansion info not provided, use standard info
            temp_exp = temp_std
            turn_prob_pets_exp[temp_turn][key] = temp_exp
        
turn_prob_foods_std = {}
turn_prob_foods_exp = {}
for i in np.arange(0,12):
    turn_prob_foods_std[i] = {}
    turn_prob_foods_exp[i] = {}
for key,value in data["foods"].items():
    if "probabilities" not in value:
        continue
    if data["foods"][key]["probabilities"] == "none":
        continue
    for temp_dict in data["foods"][key]["probabilities"]:
        if temp_dict == "none":
            continue
        temp_turn = int(temp_dict["turn"].split("-")[-1])
        if "StandardPack" in temp_dict["perSlot"]:
            temp_std = temp_dict["perSlot"]["StandardPack"]
            turn_prob_foods_std[temp_turn][key] = temp_std
        if "ExpansionPack1" in temp_dict["perSlot"]:
            temp_exp = temp_dict["perSlot"]["ExpansionPack1"]
            turn_prob_foods_exp[temp_turn][key] = temp_exp
        else:
            ### Assumption, if expansion info not provided, use standard info
            temp_exp = temp_std
            turn_prob_foods_exp[temp_turn][key] = temp_exp

#%%

#%%

class Store():
    def __init__(self, turn=0, pack="StandardPack"):
        self.turn = turn
        self.tier_avail = 0
        self.leveup_tier = 0
        self.avail_pets = []
        self.avail_foods = []
        self.pp = []                    ### Probability of pet 
        self.fp = []                    ### Probability of food
        self.fslots = 0
        self.pslots = 0
        self.max_slots = 7
        self.cpets = []                 ### Current pets in shop
        self.cfood = []                 ### Current foods in shop
        self.can = 0                    ### Keep track of can stats
        
        if pack == "StandardPack":
            self.turn_prob_pets = turn_prob_pets_std
            self.turn_prob_foods = turn_prob_foods_std
        elif pack == "ExpansionPack1":
            self.turn_prob_pets = turn_prob_pets_exp
            self.turn_prob_foods = turn_prob_foods_exp
        else:
            raise Exception("Pack {} not valid".format(pack))
        
    
    def roll(self, team=None):
        """ Randomizes shop and returns list of available entries """
        
        if len(self.avail_pets) > 0:
            pets = np.random.choice(self.avail_pets, 
                                    size=(self.pslots),
                                    replace=True, 
                                    p=self.pp)
        else:
            pets = []
        
        if len(self.avail_foods) > 0:
            foods = np.random.choice(self.avail_foods, 
                                    size=(self.fslots),
                                    replace=True, 
                                    p=self.fp)
        else:
            foods = []
        
        ### What should be done here is that instances of pet and food classes
        ### should be initialized here 
        self.cpets = [Pet(x, self) for x in pets]
        self.cfoods = [Food(x, self, team) for x in foods]
        
        return self.cpets+self.cfoods
    

    
    def freeze(self, idx):
        """
        Freeze a shop index 
        
        """
        raise Exception()
    
    
    def levelup(self):
        """ 
        Called when a pet is leveled-up by the player to update the shop state
        with a new pet
        
        """
        raise Exception("Not implemented")

    
    def update_shop_rules(self, turn=-1):
        if turn < 0:
            turn = self.turn
        
        ### Turn 11 is max stored info
        if turn > 11:
            turn = 11
            
        td = data["turns"]["turn-{}".format(turn)]
        self.fslots = td["foodShopSlots"]
        self.pslots = td["animalShopSlots"]
        self.tier_avail = td["tiersAvailable"]
        self.levelup_tier = td["levelUpTier"]
        temp_avail_pets = pet_tier_avail_lookup[self.tier_avail]
        temp_avail_foods = food_tier_avail_lookup[self.tier_avail]
        
        temp_prob_pets = self.turn_prob_pets[turn]
        self.pp = []
        self.avail_pets = []
        for temp_pet in temp_avail_pets:
            if temp_pet not in temp_prob_pets:
                continue
            self.pp.append(temp_prob_pets[temp_pet])
            self.avail_pets.append(temp_pet)
        
        temp_prob_foods = self.turn_prob_foods[turn]
        self.fp = []
        self.avail_foods = []
        for temp_food in temp_avail_foods:
            if temp_food not in temp_prob_foods:
                continue
            self.fp.append(temp_prob_foods[temp_food])
            self.avail_foods.append(temp_food)
            
        ### Ensure that the probabilities sum to 1...
        self.pp = np.array(self.pp) 
        self.pp = self.pp / np.sum(self.pp)
        
        self.fp = np.array(self.fp) 
        self.fp = self.fp / np.sum(self.fp)
        
    
    def next_turn(self):
        ### Update turn counter
        self.turn += 1
        
        ### Update rules of the shop to generate a shop state
        self.update_shop_rules()
        
        return self.roll()
    
    
    
        
# %%

# %%
