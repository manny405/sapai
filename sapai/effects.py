
import sys,inspect
import numpy as np
from data import data

"""
This module implements all effects in the game. API description is as follows:

    - Function name must match the effect["kind"] in data.data
    - Function must take in the pet_idx that has triggered the effect to occur 
        where pet_idx=(team_idx,team_pet_idx)
    - Function must take in teams referenced by pet_idx
    - Functions that require the shop to interact must have required shop input
    - Function may modify the teams freely
    - Returns nothing as further analysis of the outcome of the effect should 
        be determined by other function

"""

def get_effect_function(effect_kind):
    if effect_kind not in func_dict:
        raise Exception("Input effect_kind {} not found in {}"
            .format(effect_kind, list(func_dict.keys())))
    return func_dict[effect_kind]


def get_pet(pet_idx,teams):
    """ Helper function with error catching """
    team_idx = pet_idx[0]
    team_pet_idx = pet_idx[1]
    if len(teams) > 2:
        raise Exception("Cannot input more than 2 teams")
    if team_idx >= len(teams):
        raise Exception("Team idx greater than provided number of teams")
    if team_pet_idx >= 5:
        raise Exception("Team pet idx greater than 5")
    return teams[team_idx][team_pet_idx].pet


def get_target(pet_idx,teams):
    """
    Returns the targets for a given effect. Targets are returned as a list of 
    pet_idx. 
    
    """
    p = teams[pet_idx[0]][pet_idx[1]].pet
    effect = p.ability["effect"]
    if "target" not in effect:
        raise Exception("No target found")
    target = effect["target"]
    if type(target) != dict:
        print(target)
        raise Exception("This should not be possible")
    kind = target["kind"]
    if "n" in target:
        n = target["n"]
    
    if pet_idx[0] == 0:
        fteam = teams[0]
        oteam = teams[1]
    elif pet_idx[0] == 1:
        fteam = teams[1]
        oteam = teams[0]
    else:
        raise Exception("That's impossible")
    
    ### Get possible indices for each team
    fidx = []
    for iter_idx,temp_slot in enumerate(fteam):
        if not temp_slot.empty:
            fidx.append(iter_idx)
    oidx = []
    for iter_idx,temp_slot in enumerate(oteam):
        if not temp_slot.empty:
            oidx.append(iter_idx)
    
    if kind == "AdjacentAnimals":
        raise Exception()
    if kind == "AdjacentFriends":
        raise Exception()
    if kind == "All":
        raise Exception()
    if kind == "DifferentTierAnimals":
        raise Exception()
    if kind == "EachFriend":
        raise Exception()
    if kind == "EachShopAnimal":
        raise Exception()
    if kind == "FirstEnemy":
        raise Exception()
    if kind == "FriendAhead":
        raise Exception()
    if kind == "FriendBehind":
        raise Exception()
    if kind == "HighestHealthEnemy":
        raise Exception()
    if kind == "LastEnemy":
        raise Exception()
    if kind == "LeftMostFriend":
        raise Exception()
    if kind == "Level2And3Friends":
        raise Exception()
    if kind == "LowestHealthEnemy":
        raise Exception()
    if kind == "RandomEnemy":
        raise Exception()
    
    if kind == "RandomFriend":
        pidx = []
        for temp_idx in fidx:
            if temp_idx != pet_idx[1]:
                pidx.append(temp_idx)
        if n <= len(pidx):
            cidx = np.random.choice(pidx, size=(n,), replace=False)
        elif len(pidx) > 0:
            cidx = np.random.choice(pidx, size=(len(pidx),), replace=False)
        elif len(pidx) == 0:
            cidx = []
        else:
            raise Exception("That's impossible")
        ret_idx = []
        for temp_idx in cidx:
            ret_idx.append((pet_idx[0], temp_idx))
        return ret_idx
        
    if kind == "RightMostFriend":
        raise Exception()
    if kind == "Self":
        raise Exception()
    if kind == "TriggeringEntity":
        raise Exception()
    if kind == "none":
        ### No targets
        return []
    

def AllOf(pet_idx, teams):
    p = get_pet(pet_idx, teams)
    effects = p.ability["effect"]["effects"]
    for temp_effect in effects:
        effect_kind = temp_effect["kind"]
        func = get_effect_function(effect_kind)
        func(pet_idx,teams)


def ApplyStatus(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def DealDamage(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def GainExperience(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def GainGold(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def FoodMultiplier(pet_idx, teams, shop):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def ModifyStats(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams)
    attack_amount = 0
    health_amount = 0
    if "attackAmount" in pet.ability["effect"]:
        attack_amount = pet.ability["effect"]["attackAmount"]
    if "healthAmount" in pet.ability["effect"]:
        health_amount = pet.ability["effect"]["healthAmount"]
    for target_pet_idx in target:
        temp_pet = teams[target_pet_idx[0]][target_pet_idx[1]].pet
        temp_pet.attack += attack_amount
        temp_pet.health += attack_amount
    return


def OneOf(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def ReduceHealth(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def RefillShops(pet_idx,teams,shop):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def RepeatAbility(pet_idx,teams,shop=None):
    """ 
    Tiger implementation
    
    Find the animal infront of the Tiger and call their ability again. Keep
    in mind that the same effect priority should be given to the animal that's
    infront of the tiger. Maybe should be handled on the effect order stage?
    
    """
    pet = get_pet(pet_idx,teams)
    raise Exception()


def SummonPet(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def SummonRandomPet(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def Swallow(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def TransferAbility(pet_idx,teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def TransferStats(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def none(pet_idx, teams):
    pet = get_pet(pet_idx,teams)
    return


curr = sys.modules[__name__]
mem = inspect.getmembers(curr, inspect.isfunction)
func_dict = {}
for temp_name,func in mem:
    func_dict[temp_name] = func