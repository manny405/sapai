
import sys,inspect
import numpy as np

from data import data
from pets import Pet
from teams import Team,TeamSlot
from store import pet_tier_lookup,pet_tier_lookup_std

"""
This module implements all effects in the game. API description is as follows:

    - Function name must match the effect["kind"] in data.data
    - Function must take in the pet_idx that has triggered the effect to occur 
        where pet_idx=(team_idx,team_pet_idx)
    - Function must take in teams referenced by pet_idx
    - Function takes in triggering entity optionally as te
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


def get_target(pet_idx,teams,get_from=False,te=None):
    """
    Returns the targets for a given effect. Targets are returned as a list of 
    pets. 
    
    """
    p = teams[pet_idx[0]][pet_idx[1]].pet
    effect = p.ability["effect"]
    
    ### Logic switch because data-dictionary is not consistent
    if "target" not in effect:
        if "to" in effect:
            target = effect["to"]
        else:
            raise Exception("Target not found")
    else:
        target = effect["target"]
        
    if get_from:
        if "from" not in effect:
            raise Exception("from not found in effect")
        else:
            target = effect["from"]
    
    if type(target) != dict:
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
        lookup_pet_idx = -1
        lookup = {}
        for iter_idx,temp_idx in enumerate(fidx):
            if temp_idx == pet_idx[1]:
                lookup_pet_idx = temp_idx
            lookup[iter_idx] = {"fidx": temp_idx}
        if lookup_pet_idx < 0:
            raise Exception("Not possible")
        start_idx = len(lookup)
        for iter_idx,temp_idx in enumerate(oidx):
            lookup[start_idx+iter_idx] = {"oidx": temp_idx}
        ret_pets = []
        if lookup_pet_idx+1 in lookup:
            if "fidx" in lookup[lookup_pet_idx+1]:
                temp_idx = lookup[lookup_pet_idx+1]["fidx"]
                ret_pets.append(fteam[temp_idx].pet)
            elif "oidx" in lookup[lookup_pet_idx+1]:
                temp_idx = lookup[lookup_pet_idx+1]["oidx"]
                ret_pets.append(oteam[temp_idx].pet)
        if lookup_pet_idx-1 in lookup:
            if "fidx" in lookup[lookup_pet_idx-1]:
                temp_idx = lookup[lookup_pet_idx-1]["fidx"]
                ret_pets.append(fteam[temp_idx].pet)
            elif "oidx" in lookup[lookup_pet_idx-1]:
                temp_idx = lookup[lookup_pet_idx-1]["oidx"]
                ret_pets.append(oteam[temp_idx].pet)
        return ret_pets
        
    elif kind == "AdjacentFriends":
        lookup_pet_idx = -1
        lookup = {}
        for iter_idx,temp_idx in enumerate(fidx):
            if temp_idx == pet_idx[1]:
                lookup_pet_idx = temp_idx
            lookup[iter_idx] = {"fidx": temp_idx}
        if lookup_pet_idx < 0:
            raise Exception("Not possible")
        ret_pets = []
        if lookup_pet_idx+1 in lookup:
            if "fidx" in lookup[lookup_pet_idx+1]:
                temp_idx = lookup[lookup_pet_idx+1]["fidx"]
                ret_pets.append(fteam[temp_idx].pet)
            else:
                raise Exception()
        if lookup_pet_idx-1 in lookup:
            if "fidx" in lookup[lookup_pet_idx-1]:
                temp_idx = lookup[lookup_pet_idx-1]["fidx"]
                ret_pets.append(fteam[temp_idx].pet)
            else:
                raise Exception()
        return ret_pets
    
    elif kind == "All":
        ret_pets = []
        for temp_idx in fidx:
            ret_pets.append(fteam[temp_idx].pet)
        for temp_idx in oidx:
            ret_pets.append(oteam[temp_idx].pet)
        return ret_pets
        
    elif kind == "DifferentTierAnimals":
        pet_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
        for temp_idx in fidx:
            temp_tier = fteam[temp_idx].pet.tier
            pet_tier_lookup[temp_tier].append(fteam[temp_idx].pet)
        ret_pets = []
        for _,pet_list in pet_tier_lookup.items():
            if len(pet_list) == 0:
                continue
            chosen_pet = np.random.choice(pet_list, (1,))[0]
            ret_pets.append(chosen_pet)
        return ret_pets
    
    elif kind == "EachFriend":
        ret_pets = []
        for temp_idx in fidx:
            ret_pets.append(fteam[temp_idx].pet)
        return ret_pets
    
    elif kind == "EachShopAnimal":
        store = fteam.store
        if store == None:
            return []
        else:
            return store.cpets
        
    elif kind == "FirstEnemy":
        if len(oidx) > 0:
            return [oteam[oidx[0]].pet]
        else:
            return []
    
    elif kind == "FriendAhead":
        chosen_idx = []
        for temp_idx in fidx:
            if temp_idx < pet_idx[1]:
                chosen_idx.append(temp_idx)
        ret_pets = []
        for temp_idx in chosen_idx:
            ret_pets.append(fteam[temp_idx].pet)
            if len(ret_pets) >= n:
                break
        return ret_pets
        
    elif kind == "FriendBehind":
        chosen_idx = []
        for temp_idx in fidx:
            if temp_idx > pet_idx[1]:
                chosen_idx.append(temp_idx)
        ret_pets = []
        for temp_idx in chosen_idx:
            ret_pets.append(fteam[temp_idx].pet)
            if len(ret_pets) >= n:
                break
        return ret_pets
    
    elif kind == "HighestHealthEnemy":
        health_list = []
        for temp_idx in oidx:
            health_list.append(oteam[temp_idx].pet.health)
        if len(health_list) > 0:
            max_idx = np.argmax(health_list)
            ### Dereference max_idx
            return [oteam[oidx[max_idx]].pet]
        else:
            return []
        
    
    elif kind == "LastEnemy":
        return [oteam[np.max(oidx)].pet]
    
    elif kind == "LeftMostFriend":
        max_idx = np.max(fidx)
        return [fteam[max_idx].pet]
        
    elif kind == "Level2And3Friends":
        level_list = []
        for temp_idx in fidx:
            level_list.append(fteam[temp_idx].pet.level)
        if len(level_list) > 0:
            keep_idx = np.where(np.array(level_list) > 1)[0]
            ret_pets = []
            for temp_idx in keep_idx:
                ### Dereference idx
                temp_idx = fidx[temp_idx]
                ret_pets.append(fteam[temp_idx].pet)
            return ret_pets
        else:
            return []
    
    elif kind == "LowestHealthEnemy":
        health_list = []
        for temp_idx in oidx:
            health_list.append(oteam[temp_idx].pet.health)
        if len(health_list) > 0:
            min_idx = np.argmin(health_list)
            ### Dereference max_idx
            return [oteam[oidx[min_idx]].pet]
        else:
            return []
    
    elif kind == "RandomEnemy":
        cidx = []
        if len(oidx) > 0:
            cidx = np.random.choice(oidx, size=(n,), replace=False)
        ret_pets = []
        for temp_idx in cidx:
            ret_pets.append(oteam[temp_idx].pet)
        return ret_pets
    
    elif kind == "RandomFriend":
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
        ret_pets = []
        for temp_idx in cidx:
            ret_pets.append(teams[pet_idx[0]][temp_idx].pet)
        return ret_pets
        
    elif kind == "RightMostFriend":
        return [fteam[fidx[0]].pet]
    
    elif kind == "Self":
        return [teams[pet_idx[0]][pet_idx[1]].pet]

    elif kind == "StrongestFriend":
        stat_list = []
        for temp_idx in fidx:
            temp_stats = fteam[temp_idx].pet.attack + fteam[temp_idx].pet.health
            stat_list.append(temp_stats)
        max_idx = np.argmax(stat_list)
        max_idx = fidx[max_idx]
        return [fteam[max_idx].pet]
    
    elif kind == "TriggeringEntity":
        if te != None:
            return [te]
        else:
            return []
          
    elif kind == "none":
        ### No targets
        return []

    else:
        raise Exception("Target {} impelementation not found".format(kind))
    

def AllOf(pet_idx, teams, te=None):
    p = get_pet(pet_idx, teams)
    original_effect = p.ability["effect"]
    effects = p.ability["effect"]["effects"]
    for temp_effect in effects:
        effect_kind = temp_effect["kind"]
        func = get_effect_function(effect_kind)
        p.ability["effect"] = temp_effect
        func(pet_idx,teams,te=te)
    p.ability["effect"] = original_effect


def ApplyStatus(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    status = pet.ability["effect"]["status"]
    for target_pet in target:
        target_pet.status = status
    return


def DealDamage(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    health_amount = pet.ability["effect"]["amount"]
    if type(health_amount) == dict:
        if "attackDamagePercent" in health_amount:
            health_amount = int(pet.attack*health_amount["attackDamagePercent"]*0.01)
        else:
            raise Exception()
    for target_pet in target:
        target_pet.health -= health_amount
    return


def GainExperience(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    for target_pet in target:
        amount = target_pet.ability["effect"]["amount"]
        level_up = target_pet.gain_experience(amount=amount)
        if level_up:
            if target_pet.ability["trigger"] == "LevelUp":
                func = get_effect_function(target_pet.ability["effect"]["kind"])
                ### Maybe return TeamSlot instead of pet and TeamSlot contains
                ### meta-data on exactly where it comes from? Or just return 
                ### those idx from get_target...
                ### For now, do nothing smart...
                if pet.ability["effect"]["target"]["kind"] != "Self":
                    raise Exception("Not implemented")
                func(pet_idx, teams,te=target_pet)
    return


def GainGold(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    fteam,oteam = get_teams(pet_idx, teams)
    amount = pet.ability["effect"]["amount"]
    player = fteam.player
    if player != None:
        fteam.player.gold += amount
    return


def FoodMultiplier(pet_idx, teams, shop, te=None):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def ModifyStats(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    attack_amount = 0
    health_amount = 0
    if "attackAmount" in pet.ability["effect"]:
        attack_amount = pet.ability["effect"]["attackAmount"]
    if "healthAmount" in pet.ability["effect"]:
        health_amount = pet.ability["effect"]["healthAmount"]
    for target_pet in target:
        target_pet.attack += attack_amount
        target_pet.health += health_amount
        target_pet.attack = min([target_pet.attack,50])
        target_pet.health = min([target_pet.health,50])
    return


def OneOf(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    original_effect = pet.ability["effect"]
    effects = pet.ability["effect"]["effects"]
    chosen_idx = np.random.choice(np.arange(0,len(effects)), size=(1,))[0]
    effect = effects[chosen_idx]
    effect_kind = effect["kind"]
    pet.ability["effect"] = effect
    func = get_effect_function(effect_kind)
    func(pet_idx,teams,te=te)
    pet.ability["effect"] = original_effect
    return


def ReduceHealth(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    per = pet.ability["effect"]["percentage"]*0.01
    for temp_pet in target:
        if temp_pet.health > 0:
            temp_pet.health = int(temp_pet.health*per)
            if temp_pet.health == 0:
                ### Floor health of 1
                temp_pet.health = 1
    return


def RefillShops(pet_idx, teams, shop, te=None):
    pet = get_pet(pet_idx,teams)
    raise Exception()


def RepeatAbility(pet_idx,teams, te=None, shop=None):
    """ 
    Tiger implementation
    
    Find the animal infront of the Tiger and call their ability again. Keep
    in mind that the same effect priority should be given to the animal that's
    infront of the tiger. Maybe should be handled on the effect order stage?
    
    """
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    raise Exception()


def SummonPet(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    fteam,oteam = get_teams(pet_idx,teams)
    spet_name = pet.ability["effect"]["pet"]
    
    if pet.ability["effect"]["team"] == "Friendly":
        target_team = fteam
        ### First move team as far backward as possible
        target_team.move_backward()
    elif pet.ability["effect"]["team"] == "Enemy":
        target_team = oteam
        target_team.move_forward()
    else:
        raise Exception()
    
    ### Check for furthest back open position
    empty_idx = []
    for iter_idx,temp_slot in enumerate(target_team):
        if temp_slot.empty:
            empty_idx.append(iter_idx)
    
    if len(empty_idx) == 0:
        ### Can safely return, cannot summon
        return
    
    target_slot_idx = np.max(empty_idx)
    spet = Pet(spet_name)
    
    if "withAttack" in pet.ability["effect"]:
        spet.attack = pet.ability["effect"]["withAttack"]
    if "withHealth" in pet.ability["effect"]:
        spet.health = pet.ability["effect"]["withHealth"]
    if "withLevel" in pet.ability["effect"]:
        spet.level = pet.ability["effect"]["withLevel"]
    if pet.name == "pet-rooster":
        spet.attack = pet.attack
        
    target_team[target_slot_idx] = TeamSlot(spet)
    ### Move back forward
    target_team.move_forward()
    
    return


def SummonRandomPet(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    fteam,oteam = get_teams(pet_idx,teams)
    tier = pet.ability["effect"]["tier"]
    if fteam.pack == "StandardPack":
        possible = pet_tier_lookup_std[tier]
    elif fteam.pack == "ExpansionPack1":
        possible = pet_tier_lookup[tier]
    else:
        raise Exception()
    chosen = np.random.choice(possible, (1,))[0]
    fteam.move_backward()
    ### Check for furthest back open position
    empty_idx = []
    for iter_idx,temp_slot in enumerate(fteam):
        if temp_slot.empty:
            empty_idx.append(iter_idx)
    if len(empty_idx) == 0:
        ### Can safely return, cannot summon
        return
    target_slot_idx = np.max(empty_idx)
    spet = Pet(chosen)
    if "baseAttack" in pet.ability["effect"]:
        sattack = pet.ability["effect"]["baseAttack"]
    else:
        sattack = data["pets"][spet.name]["baseAttack"]
    if "baseHealth" in pet.ability["effect"]:
        shealth = pet.ability["effect"]["baseHealth"]
    else:
        shealth = data["pets"][spet.name]["baseHealth"]
    spet.attack = sattack
    spet.health = shealth
    fteam[target_slot_idx] = TeamSlot(spet)
    fteam.move_forward()
    return

def Swallow(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    fteam,oteam = get_teams(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    output_level = pet.level
    if output_level == 1:
        level_attack = 0
        level_health = 0
    elif output_level == 2:
        level_attack = 2
        level_health = 2
    elif output_level == 3:
        level_attack = 5
        level_health = 5
    else:
        raise Exception()
    
    if pet.name != "pet-whale":
        raise Exception("Swallow only done by whale")
    
    ### Remove target from team and store this pet as the given level as a 
    ### Summon ability
    for temp_target in target:
        summon_dict = {
        "description": "Swallowed and summon level {} {}".format(temp_target.name, 
                                                                 output_level),
        "trigger": "Faint",
        "triggeredBy": {'kind': 'Self'},
        "effect":{
        'kind': 'SummonPet',
        'pet': temp_target.name,
        'withAttack': data["pets"][temp_target.name]["baseAttack"]+level_attack,
        'withHealth': data["pets"][temp_target.name]["baseHealth"]+level_health,
        'withLevel': output_level,
        'team': 'Friendly'}}
        pet.set_ability(summon_dict)
        fteam.remove(temp_target)
        break
    fteam.move_forward()
    
    return


def TransferAbility(pet_idx,teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    target_from = get_target(pet_idx,teams,get_from=True,te=te)
    pet.set_ability(target_from[0].ability)
    return


def TransferStats(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    target = get_target(pet_idx,teams,te=te)
    target_from = get_target(pet_idx,teams,get_from=True,te=te)
    effect = pet.ability["effect"]
    copy_attack = effect["copyAttack"]
    copy_health = effect["copyHealth"]
    if len(target) == 1:
        if len(target_from) == 1:
            if copy_attack:
                target[0].attack = target_from[0].attack
            if copy_health:
                target[0].health = target_from[0].health
        elif len(target_from) == 0:
            pass
        else:
            raise Exception()
    elif len(target) == 0:
        pass
    else:
        raise Exception()
    return


def none(pet_idx, teams, te=None):
    pet = get_pet(pet_idx,teams)
    return


def get_teams(pet_idx,teams):
    if pet_idx[0] == 0:
        fteam = teams[0]
        oteam = teams[1]
    elif pet_idx[0] == 1:
        fteam = teams[1]
        oteam = teams[0]
    else:
        raise Exception("That's impossible")
    return fteam,oteam


curr = sys.modules[__name__]
mem = inspect.getmembers(curr, inspect.isfunction)
func_dict = {}
for temp_name,func in mem:
    func_dict[temp_name] = func