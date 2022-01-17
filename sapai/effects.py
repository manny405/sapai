
import sys,inspect
import numpy as np

from sapai.data import data
from sapai.tiers import pet_tier_lookup,pet_tier_lookup_std
from sapai.foods import Food

#### Removing these to avoid circular imports
# from sapai.pets import Pet
# from sapai.teams import Team,TeamSlot

"""
This module implements all effects in the game. API description is as follows:

    - Function name must match the effect["kind"] in data.data
    - Function must take in the pet_idx that has triggered the effect to occur 
        where pet_idx=(team_idx,team_pet_idx)
    - Function must take in teams referenced by pet_idx
    - Functions may take in fainted_pet as optional input when the effect was
        triggered by a unit that already fained. The pet_idx provided should be 
        the position that the fainted unit was from. 
    - Function takes in triggering entity optionally as te
    - Functions that require the shop to interact must have required shop input
    - Function may modify the teams freely
    - Function must return the pets that were targeted for the effect as a list
    - Returns nothing as further analysis of the outcome of the effect should 
        be determined by other function

"""

def get_effect_function(effect_kind):
    if type(effect_kind).__name__ == "Pet":
        effect_kind = effect_kind.ability["effect"]["kind"]
    elif type(effect_kind).__name__ == "TeamSlot":
        effect_kind = effect_kind.pet.ability["effect"]["kind"]
    elif type(effect_kind) == str:
        pass
    else:
        raise Exception("Unrecognized input {}".format(effect_kind))
    if effect_kind not in func_dict:
        raise Exception("Input effect_kind {} not found in {}"
            .format(effect_kind, list(func_dict.keys())))
    return func_dict[effect_kind]


def get_pet(pet_idx,teams,fainted_pet=None):
    """ Helper function with error catching """
    team_idx = pet_idx[0]
    team_pet_idx = pet_idx[1]
    if len(teams) > 2:
        raise Exception("Cannot input more than 2 teams")
    if team_idx >= len(teams):
        raise Exception("Team idx greater than provided number of teams")
    if team_pet_idx >= 5:
        raise Exception("Team pet idx greater than 5")
    if fainted_pet == None:
        pet = teams[team_idx][team_pet_idx].pet
    else:
        pet = fainted_pet
    return pet
 

def get_teams(pet_idx,teams):
    if len(teams) == 1:
        teams = [teams[0], []]
    if pet_idx[0] == 0:
        fteam = teams[0]
        oteam = teams[1]
    elif pet_idx[0] == 1:
        fteam = teams[1]
        oteam = teams[0]
    else:
        raise Exception("That's impossible")
    return fteam,oteam


def get_target(pet_idx,teams,fainted_pet=None,get_from=False,te=None):
    """
    Returns the targets for a given effect. Targets are returned as a list of 
    pets. 
    
    Arguments
    ---------
    pet_idx: list
        List of two indices that provide the team index and the pet index 
        that has requested to obtain target pets
    teams: list
        List of two teams
    fainted_pet: Pet
        If the target has been requested due to fainting, the fainted pet should
        be input.
    get_from: bool
        For correting some database inconsistencies
    te: Pet
        Triggering entity
    """
    p = get_pet(pet_idx,teams,fainted_pet)
    effect = p.ability["effect"]
    
    if len(teams) == 1:
        teams = [teams[0], []]
    
    ### Logic switch because data-dictionary is not consistent
    if "target" not in effect:
        if "to" in effect:
            target = effect["to"]
        else:
            print(p,effect)
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
            ### Skiped if health is less than 0
            if temp_slot.pet.health > 0:
                fidx.append(iter_idx)
    oidx = []
    for iter_idx,temp_slot in enumerate(oteam):
        if not temp_slot.empty:
            ### Skiped if health is less than 0
            if temp_slot.pet.health > 0:
                oidx.append(iter_idx)
    
    if kind == "AdjacentAnimals":
        lookup_pet_idx = -1
        lookup = {}
        iter_idx = 0
        ### First add opponent indices backward 
        for temp_idx in oidx[::-1]:
            lookup[iter_idx] = {"oidx": temp_idx}
            iter_idx += 1
        ### Then add friendly indices
        for temp_idx in fidx:
            if temp_idx > pet_idx[1]:
                if lookup_pet_idx < 0:
                    ### Handle case that pet has fainted already
                    lookup_pet_idx = iter_idx
                    lookup[iter_idx] = {"fidx": pet_idx[1]}
                    iter_idx += 1
                    lookup[iter_idx] = {"fidx": temp_idx}
                    iter_idx += 1
                    continue
            elif temp_idx == pet_idx[1]:
                lookup_pet_idx = temp_idx
            lookup[iter_idx] = {"fidx": temp_idx}
            iter_idx += 1
        if lookup_pet_idx < 0:
            raise Exception("Not possible")
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
    
    elif kind == "EachEnemy":
        ret_pets = []
        for temp_idx in oidx:
            ret_pets.append(oteam[temp_idx].pet)
        return ret_pets
    
    elif kind == "EachFriend":
        ret_pets = []
        for temp_idx in fidx:
            ret_pets.append(fteam[temp_idx].pet)
        return ret_pets
    
    elif kind == "EachShopAnimal":
        shop = fteam.shop
        if shop == None:
            return []
        else:
            return shop.pets
        
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
        for temp_idx in chosen_idx[::-1]:
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
            if len(oidx) < n:
                n = len(oidx)
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

    elif kind == "HighestHealthFriend":
        health_list = []
        for temp_idx in fidx:
            health_list.append(fteam[temp_idx].pet.health)
        max_idx = np.argmax(health_list)
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
    

def AllOf(pet_idx, teams, fainted_pet=None, te=None):
    p = get_pet(pet_idx,teams,fainted_pet)
    original_effect = p.ability["effect"]
    effects = p.ability["effect"]["effects"]
    target = []
    for temp_effect in effects:
        effect_kind = temp_effect["kind"]
        func = get_effect_function(effect_kind)
        p.ability["effect"] = temp_effect
        target += func(pet_idx,teams,te=te)
    p.ability["effect"] = original_effect
    return target


def ApplyStatus(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    status = pet.ability["effect"]["status"]
    for target_pet in target:
        target_pet.status = status
    return target


def DealDamage(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    health_amount = pet.ability["effect"]["amount"]
    if type(health_amount) == dict:
        if "attackDamagePercent" in health_amount:
            health_amount = int(pet.attack*health_amount["attackDamagePercent"]*0.01)
        else:
            raise Exception()
    for target_pet in target:
        target_pet.health -= health_amount
    return target


def GainExperience(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
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
    return target


def GainGold(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    fteam,oteam = get_teams(pet_idx, teams)
    amount = pet.ability["effect"]["amount"]
    player = fteam.player
    if player != None:
        fteam.player.gold += amount
    return player


def Evolve(pet_idx,teams,fainted_pet=None,te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    fteam,oteam = get_teams(pet_idx, teams)
    target = [pet]
    spet = pet.ability["effect"]["into"]
    fteam.remove(pet)
    fteam[pet_idx[1]] = spet
    kind = spet.ability["effect"]["kind"]
    func = get_effect_function(kind)
    target = func(pet_idx,teams,te=spet)
    return target


def FoodMultiplier(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    if pet.shop == None:
        return []
    
    mult = int(pet.ability["effect"]["amount"])
    food_list = pet.shop.foods
    for food in food_list:
        ### Multiplier is not strict multiplier of current value, but additive
        ###   multiplier of base attack and health
        if food.attack == food.base_attack:
            ### If first time that additive multiplier applied, then account
            ###   for an extra x that already exists 
            mult = mult - 1
        food.attack += food.base_attack*mult
        food.health += food.base_health*mult
        
    return food


def ModifyStats(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
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
    return target


def OneOf(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    original_effect = pet.ability["effect"]
    effects = pet.ability["effect"]["effects"]
    chosen_idx = np.random.choice(np.arange(0,len(effects)), size=(1,))[0]
    effect = effects[chosen_idx]
    effect_kind = effect["kind"]
    pet.ability["effect"] = effect
    func = get_effect_function(effect_kind)
    target = func(pet_idx,teams,te=te)
    pet.ability["effect"] = original_effect
    return target


def ReduceHealth(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    per = pet.ability["effect"]["percentage"]*0.01
    for temp_pet in target:
        if temp_pet.health > 0:
            temp_pet.health = int(temp_pet.health*per)
            if temp_pet.health == 0:
                ### Floor health of 1
                temp_pet.health = 1
    return target


def RefillShops(pet_idx, teams, fainted_pet=None, te=None):
    """
    Only Cow has refill shop in newest patch anyways...
    
    """
    pet = get_pet(pet_idx,teams,fainted_pet)
    if pet.name != "pet-cow":
        raise Exception("Only cow implemented for RefillShops")
    shop = pet.shop
    level = pet.level
    targets = []
    for slot in shop:
        if slot.slot_type == "food":
            temp_food = Food("milk")
            temp_food.attack *= level
            temp_food.health *= level
            slot.item = temp_food
            targets.append(slot)
    return targets


def RepeatAbility(pet_idx,teams, fainted_pet=None, te=None, shop=None):
    """ 
    Tiger implementation
    
    Find the animal infront of the Tiger and call their ability again. Keep
    in mind that the same effect priority should be given to the animal that's
    infront of the tiger. Maybe should be handled on the effect order stage?
    
    """
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    raise Exception()
    return target


def SummonPet(pet_idx, teams, fainted_pet=None, te=None):
    """
    te is tiger if calling from tiger or for next alive 
    """
    pet = get_pet(pet_idx,teams,fainted_pet)       
    fteam,oteam = get_teams(pet_idx,teams)
        
    spet_name = pet.ability["effect"]["pet"]
    if pet.ability["effect"]["team"] == "Friendly":
        target_team = fteam
        if fainted_pet != None:
            if te == None:
                ### Added fainted pet back in
                fteam[pet_idx[1]] = fainted_pet
        ### First move team as far backward as possible
        target_team.move_backward()
        ### Then move all animals forward that are infront of the target pet
        if te == None:
            end_idx = target_team.get_idx(pet)
        else:
            end_idx = target_team.get_idx(te)
        target_team.move_forward(start_idx=0, end_idx=end_idx)
        if fainted_pet != None:
            if te == None:
                ### Remove fainted pet
                temp_idx = target_team.get_idx(pet)
                target_team.remove(temp_idx)
    elif pet.ability["effect"]["team"] == "Enemy":
        target_team = oteam
        target_team.move_forward()
    else:
        raise Exception(pet.ability["effect"]["team"])
    
    n = 1
    if pet.name == "pet-sheep":
        n = 2
    elif pet.name == "pet-rooster":
        n = pet.level
    
    target = []
    for _ in range(n):
        ### Check for furthest back open position
        empty_idx = []
        for iter_idx,temp_slot in enumerate(target_team):
            if temp_slot.empty:
                empty_idx.append(iter_idx)
        if len(empty_idx) == 0:
            ### Can safely return, cannot summon
            return target
                
        target_slot_idx = np.max(empty_idx)
        target_team[target_slot_idx] = spet_name
        spet = target_team[target_slot_idx].pet
        
        if "withAttack" in pet.ability["effect"]:
            spet.attack = pet.ability["effect"]["withAttack"]
        if "withHealth" in pet.ability["effect"]:
            spet.health = pet.ability["effect"]["withHealth"]
        if "withLevel" in pet.ability["effect"]:
            spet.level = pet.ability["effect"]["withLevel"]
        if pet.name == "pet-rooster":
            spet.attack = pet.attack
        
        target.append(spet)
        
    ### Move back forward
    target_team.move_forward()
    
    return target


def SummonRandomPet(pet_idx, teams, fainted_pet=None, te=None):
    """
    te is tiger if calling from tiger or for next alive 
    """
    pet = get_pet(pet_idx,teams,fainted_pet)
    fteam,oteam = get_teams(pet_idx,teams)
    tier = pet.ability["effect"]["tier"]
    if fteam.pack == "StandardPack":
        possible = pet_tier_lookup_std[tier]
    elif fteam.pack == "ExpansionPack1":
        possible = pet_tier_lookup[tier]
    else:
        raise Exception()
    chosen = np.random.choice(possible, (1,))[0]
    
    #### Perform team movement to ensure that the pet is summoned in the 
    #### correct position
    if fainted_pet != None:
        if te == None:
            ### Added fainted pet back in
            fteam[pet_idx[1]] = fainted_pet
    ### First move team as far backward as possible
    fteam.move_backward()
    ### Then move all animals forward that are infront of the target pet
    if te == None:
        end_idx = fteam.get_idx(pet)
    else:
        end_idx = fteam.get_idx(te)
    fteam.move_forward(start_idx=0, end_idx=end_idx)
    if fainted_pet != None:
        if te == None:
            ### Remove fainted pet
            temp_idx = fteam.get_idx(pet)
            fteam.remove(temp_idx)
    
    ### Check for furthest back open position
    empty_idx = []
    for iter_idx,temp_slot in enumerate(fteam):
        if temp_slot.empty:
            empty_idx.append(iter_idx)
    if len(empty_idx) == 0:
        ### Can safely return, cannot summon
        return []
            
    target_slot_idx = np.max(empty_idx)
    fteam[target_slot_idx] = str(chosen)
    spet = fteam[target_slot_idx].pet
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
    fteam.move_forward()
    return [spet]

def Swallow(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    fteam,oteam = get_teams(pet_idx,teams)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    if len(target) == 0:
        return target
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
    
    ### Remove target from team and shop this pet as the given level as a 
    ### Summon ability
    faint_target = []
    for temp_target in target:
        if data["pets"][temp_target.name]["baseAttack"] != "?":
            base_attack = data["pets"][temp_target.name]["baseAttack"]
        else:
            base_attack = temp_target.attack
        if data["pets"][temp_target.name]["baseHealth"] != "?":
            base_health = data["pets"][temp_target.name]["baseHealth"]
        else:
            base_health = temp_target.health
            
        summon_dict = {
        "description": "Swallowed and summon level {} {}".format(temp_target.name, 
                                                                 output_level),
        "trigger": "Faint",
        "triggeredBy": {'kind': 'Self'},
        "effect":{
        'kind': 'SummonPet',
        'pet': temp_target.name,
        'withAttack': base_attack+level_attack,
        'withHealth': base_attack+level_health,
        'withLevel': output_level,
        'team': 'Friendly'}}
        pet.set_ability(summon_dict)
        faint_idx = fteam.get_idx(temp_target)
        temp_target.health = -1
        
        #### NO! Fainting should be handled outside this function during the 
        #### phase_faint
        # fteam.remove(temp_target)
        # ### Check temp_target for Faint Trigger
        # if temp_target.ability["trigger"] == "Faint":
        #     faint_kind = temp_target.ability["effect"]["kind"]
        #     faint_func = get_effect_function(faint_kind)
        #     faint_target = faint_func((pet_idx[0],faint_idx),teams,fainted_pet=temp_target)
            
        # break
    
    fteam.move_forward()
    # target += faint_target
    
    return target


def TransferAbility(pet_idx,teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    target_from = get_target(pet_idx,teams,get_from=True,te=te)
    pet.set_ability(target_from[0].ability)
    return target


def TransferStats(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    target = get_target(pet_idx,teams,fainted_pet=fainted_pet,te=te)
    target_from = get_target(pet_idx,teams,get_from=True,te=te)
    effect = pet.ability["effect"]
    copy_attack = effect["copyAttack"]
    copy_health = effect["copyHealth"]
    n = 1
    if pet.name == "pet-dodo":
        n = pet.level
    if len(target) == 1:
        if len(target_from) == 1:
            if copy_attack:
                if pet.name == "pet-dodo":
                    ### This needs to be checked because their definition is 
                    ### conflicting as towards if it should be equal or sum
                    target[0].attack += target_from[0].attack*n
                else:
                    target[0].attack = target_from[0].attack*n
                
                target[0].attack = min([target[0].attack,50])
            if copy_health:
                target[0].health = target_from[0].health*n
                target[0].health = min([target[0].health,50])
        elif len(target_from) == 0:
            pass
        else:
            raise Exception()
    elif len(target) == 0:
        pass
    else:
        raise Exception()
    return target


def DiscountFood(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    shop = pet.shop
    if shop == None:
        raise Exception("No shop found to discount food")
    amount = pet.ability["effect"]["amount"]
    targets = []
    for slot in shop:
        if slot.slot_type == "food":
            slot.cost = max((slot.cost - amount), 0)
            targets.append(slot)
    return targets


def none(pet_idx, teams, fainted_pet=None, te=None):
    pet = get_pet(pet_idx,teams,fainted_pet)
    return []


curr = sys.modules[__name__]
mem = inspect.getmembers(curr, inspect.isfunction)
func_dict = {}
for temp_name,func in mem:
    func_dict[temp_name] = func