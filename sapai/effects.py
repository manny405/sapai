
import sys,inspect
import itertools
import numpy as np

from sapai.data import data
from sapai.tiers import pet_tier_lookup,pet_tier_lookup_std
from sapai.foods import Food


"""
This module implements all effects in the game. API description is as follows:

    Arguments
    ---------
    apet: Pet
        Activating Pet. Must include the attached shop or player when necessary.
    apet_idx: list
        List of two indices for the [team_list_idx, team_idx] from which the 
        activating pet was called from
    teams: list
        List of Team objects. Either one or two teams. 
    te: Pet
        Triggering pet. If a pet has trigger the action. For example, if a horse
        is on the team and then an animal is summoned. The summoned animal would
        be the triggering pet. 
    te_idx: list
        List of two indices for the [team_list_idx, team_idx] from which the 
        triggering entity exists. This is only used for SummonPet in the case
        of a Fly summoning in the position of the fainted pet, which is the 
        triggering entity. In all other cases, te_idx should not be used as it
        is unnecessary. 
    fixed_targets: list of pets
        If a fixed target is desired for the effect. For common use, this is not
        required. It is useful in the case that certain outcomees are being 
        tested. It is also useful in the case that all outcomes due to 
        randomness are exactly exactly considered rather than having to rely on bootstrapped probabilities. This leads to significantly improved 
        efficiency for training by database purposes. 

    Returns
    -------
    targets: list
        List of pets that have been targeted by the effect of the ability
    possible: list of lists
        List of lists of all possible targets that could also be targeted. 
        If there is an element of randomness in the outcome, all possible 
        targets, and potentially all possible combinations of targets, is also
        returned. 

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


def get_pet(pet_idx,teams,fainted_pet=None,te=None):
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
    if te != None:
        pet = te
    return pet
 

def get_teams(pet_idx,teams):
    if len(teams) == 1:
        return teams[0],[]
    if pet_idx[0] == 0:
        fteam = teams[0]
        oteam = teams[1]
    elif pet_idx[0] == 1:
        fteam = teams[1]
        oteam = teams[0]
    else:
        raise Exception("That's impossible")
    return fteam,oteam


def get_target(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[],get_from=False,
               test_kind=""):
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
    p = apet
    effect = p.ability["effect"]
    
    if len(teams) == 1:
        teams = [teams[0], []]
    
    ### Logic switch because data-dictionary is not consistent
    if "target" not in effect:
        if "to" in effect:
            target = effect["to"]
        else:
            print(apet,apet_idx,teams,te,fixed_targets,get_from)
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
    else:
        n = 1
        
    if len(test_kind) != 0:
        kind = test_kind
    
    if apet_idx[0] == 0:
        fteam = teams[0]
        oteam = teams[1]
    elif apet_idx[0] == 1:
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
        all_pets = []
        fpet_slot_idx = []
        ### First add opponent backward 
        for temp_slot in oteam[::-1]:
            all_pets.append(temp_slot)
        ### Then friendly
        for temp_slot in fteam:
            fpet_slot_idx.append(len(all_pets))
            all_pets.append(temp_slot)
        apet_in_all = fpet_slot_idx[apet_idx[1]]
        if (apet_in_all-1) > 0:
            left_slot = all_pets[apet_in_all-1]
        else:
            left_slot = None
        
        if (apet_in_all+1) < len(all_pets):
            right_slot = all_pets[apet_in_all+1]
        else:
            right_slot = None

        ret_pets = []
        for temp_slot in [left_slot,right_slot]:
            if temp_slot == None:
                continue
            if temp_slot.empty:
                continue
            else:
                ret_pets.append(temp_slot.pet)
        return ret_pets,[ret_pets]
    
    elif kind == "AdjacentFriends":
        all_pets = []
        fpet_slot_idx = []
        for temp_slot in fteam:
            fpet_slot_idx.append(len(all_pets))
            all_pets.append(temp_slot)
        apet_in_all = fpet_slot_idx[apet_idx[1]]
        if (apet_in_all-1) > 0:
            left_slot = all_pets[apet_in_all-1]
        else:
            left_slot = None
        
        if (apet_in_all+1) < len(all_pets):
            right_slot = all_pets[apet_in_all+1]
        else:
            right_slot = None
            
        ret_pets = []
        for temp_slot in [left_slot,right_slot]:
            if temp_slot == None:
                continue
            if temp_slot.empty:
                continue
            else:
                ret_pets.append(temp_slot.pet)
        return ret_pets,[ret_pets]
    
    elif kind == "All":
        ret_pets = []
        for temp_idx in fidx:
            ret_pets.append(fteam[temp_idx].pet)
        for temp_idx in oidx:
            ret_pets.append(oteam[temp_idx].pet)
        return ret_pets,[ret_pets]
        
    elif kind == "DifferentTierAnimals":
        pet_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
        for temp_idx in fidx:
            temp_tier = fteam[temp_idx].pet.tier
            pet_tier_lookup[temp_tier].append(temp_idx)
        
        ### Build lookup of all possible pets
        idx_list = []
        for key,value in pet_tier_lookup.items():
            if len(value) > 0:
                idx_list.append(value)
        grid = np.meshgrid(*idx_list)
        ravel_grid = [x.ravel()  for x in grid]
        all_idx = np.array(ravel_grid).T
        all_possible = []
        for temp_idx in all_idx:
            temp_chosen = [fteam[x].pet for x in temp_idx]
            all_possible.append(temp_chosen)
        
        ### Choose one to return for current 
        choice_idx_range = np.arange(0,len(all_possible))
        choice_idx = np.random.choice(choice_idx_range, (1,))[0]
        ret_pets = all_possible[choice_idx]
        return ret_pets,all_possible
    
    elif kind == "EachEnemy":
        ret_pets = []
        for temp_idx in oidx:
            ret_pets.append(oteam[temp_idx].pet)
        return ret_pets,[ret_pets]
    
    elif kind == "EachFriend":
        ret_pets = []
        for temp_idx in fidx:
            ret_pets.append(fteam[temp_idx].pet)
        return ret_pets,[ret_pets]
    
    elif kind == "EachShopAnimal":
        shop = p.shop
        if shop == None:
            return [],[]
        else:
            return shop.pets,[shop.pets]
        
    elif kind == "FirstEnemy":
        if len(oidx) > 0:
            return [oteam[oidx[0]].pet],[[oteam[oidx[0]].pet]]
        else:
            return [],[]
    
    elif kind == "FriendAhead":
        chosen_idx = []
        for temp_idx in fidx:
            if temp_idx < apet_idx[1]:
                chosen_idx.append(temp_idx)
        ret_pets = []
        for temp_idx in chosen_idx[::-1]:
            ret_pets.append(fteam[temp_idx].pet)
            if len(ret_pets) >= n:
                break
        return ret_pets,[ret_pets]
        
    elif kind == "FriendBehind":
        chosen_idx = []
        for temp_idx in fidx:
            if temp_idx > apet_idx[1]:
                chosen_idx.append(temp_idx)
        ret_pets = []
        for temp_idx in chosen_idx:
            ret_pets.append(fteam[temp_idx].pet)
            if len(ret_pets) >= n:
                break
        return ret_pets,[ret_pets]
    
    elif kind == "HighestHealthEnemy":
        health_list = []
        for temp_idx in oidx:
            health_list.append(oteam[temp_idx].pet.health)
        if len(health_list) > 0:
            max_health = np.max(health_list)
            choice_idx_range = np.where(np.array(health_list) == max_health)[0]
            choice_idx = np.random.choice(choice_idx_range, (1,), replace=False)[0]
            all_possible = [[oteam[oidx[x]].pet] for x in choice_idx_range]
            ### Dereference max_idx
            return [oteam[oidx[choice_idx]].pet],all_possible
        else:
            return [],[]
        
    elif kind == "LastEnemy":
        if len(oidx) > 0:
            return [oteam[np.max(oidx)].pet],[[oteam[np.max(oidx)].pet]]
        else:
            return [],[]
    
    elif kind == "LeftMostFriend":
        max_idx = np.max(fidx)
        return [fteam[max_idx].pet],[[fteam[max_idx].pet]]
        
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
            return ret_pets,[ret_pets]
        else:
            return [],[]
    
    elif kind == "LowestHealthEnemy":
        health_list = []
        for temp_idx in oidx:
            health_list.append(oteam[temp_idx].pet.health)
        if len(health_list) > 0:
            min_health = np.min(health_list)
            choice_idx_range = np.where(np.array(health_list) == min_health)[0]
            choice_idx = np.random.choice(choice_idx_range, (1,), replace=False)[0]
            all_possible = [[oteam[oidx[x]].pet] for x in choice_idx_range]
            ### Dereference max_idx
            return [oteam[oidx[choice_idx]].pet],all_possible
        else:
            return [],[]
    
    elif kind == "RandomEnemy":
        ret_pets = []
        all_possible = []
        if len(oidx) > 0:
            if len(oidx) < n:
                n = len(oidx)
            all_idx = [x for x in itertools.combinations(oidx,n)]
            all_possible = []
            for temp_idx in all_idx:
                temp_chosen = [oteam[oidx[x]].pet for x in temp_idx]
                all_possible.append(temp_chosen)
            crange = np.arange(0,len(all_possible))
            cidx = np.random.choice(crange,(1,),replace=False)[0]
            ret_pets = all_possible[cidx]
        return ret_pets,all_possible
    
    elif kind == "RandomFriend":
        ret_pets = []
        all_possible = []
        if len(fidx) > 0:
            if len(fidx) < n:
                n = len(fidx)
            all_idx = [x for x in itertools.combinations(fidx,n)]
            all_possible = []
            for temp_idx in all_idx:
                temp_chosen = [fteam[fidx[x]].pet for x in temp_idx]
                all_possible.append(temp_chosen)
            crange = np.arange(0,len(all_possible))
            cidx = np.random.choice(crange,(1,),replace=False)[0]
            ret_pets = all_possible[cidx]
        return ret_pets,all_possible
        
    elif kind == "RightMostFriend":
        return [fteam[fidx[0]].pet],[[fteam[fidx[0]].pet]]
    
    elif kind == "Self":
        return [apet],[[apet]]

    elif kind == "StrongestFriend":
        stat_list = []
        for temp_idx in fidx:
            temp_stats = fteam[temp_idx].pet.attack + fteam[temp_idx].pet.health
            stat_list.append(temp_stats)
        stat_list = np.array(stat_list)
        max_stats = np.max(stat_list)
        max_idx = np.where(stat_list == max_stats)[0]
        all_possible = []
        for temp_idx in max_idx:
            all_possible.append(fteam[temp_idx].pet)
        choice = np.random.choice(max_idx,(1,),replace=False)[0]
        ret_pets = [fteam[choice].pet]
        return ret_pets,all_possible

    elif kind == "HighestHealthFriend":
        health_list = []
        for temp_idx in fidx:
            health_list.append(fteam[temp_idx].pet.health)
        max_health = np.max(health_list)
        max_idx = np.where(health_list == max_health)[0]
        all_possible = []
        for temp_idx in max_idx:
            all_possible.append(fteam[temp_idx].pet)
        choice = np.random.choice(max_idx,(1,),replace=False)[0]
        ret_pets = [fteam[choice].pet]
        return ret_pets,all_possible

    
    elif kind == "TriggeringEntity":
        if te != None:
            return [te],[te]
        else:
            return [],[]
          
    elif kind == "none":
        ### No targets
        return [],[]

    else:
        raise Exception("Target {} impelementation not found".format(kind))
    

def AllOf(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """ AllOf will return list of lists """
    original_effect = apet.ability["effect"]
    effects = apet.ability["effect"]["effects"]
    target = []
    possible_targets = []
    for iter_idx,temp_effect in enumerate(effects):
        effect_kind = temp_effect["kind"]
        func = get_effect_function(effect_kind)
        apet.ability["effect"] = temp_effect
        temp_target,temp_possible = func(
            apet,apet_idx,teams,te,fixed_targets)
        target.append(temp_target)
        possible_targets.append(temp_possible)
    apet.ability["effect"] = original_effect
    return target,possible_targets


def ApplyStatus(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    status = apet.ability["effect"]["status"]
    for target_pet in target:
        target_pet.status = status
    return target,possible


def DealDamage(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    health_amount = apet.ability["effect"]["amount"]
    if type(health_amount) == dict:
        if "attackDamagePercent" in health_amount:
            health_amount = int(apet.attack*health_amount["attackDamagePercent"]*0.01)
        else:
            raise Exception()
    for target_pet in target:
        target_pet.health -= health_amount
    return target,possible


def GainExperience(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    for target_pet in target:
        amount = target_pet.ability["effect"]["amount"]
        level_up = target_pet.gain_experience(amount=amount)
        if level_up:
            target_pet.levelup_trigger(target_pet)
    return target,possible


def GainGold(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    amount = apet.ability["effect"]["amount"]
    player = apet.player
    if player != None:
        apet.player.gold += amount
    return player,[player]


def Evolve(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    fteam,oteam = get_teams(apet_idx, teams)
    target = [apet]
    spet = apet.ability["effect"]["into"]
    fteam.remove(apet)
    fteam[apet_idx[1]] = spet
    kind = spet.ability["effect"]["kind"]
    func = get_effect_function(kind)
    target = func(apet_idx,teams,te=spet)
    return target,possible


def FoodMultiplier(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    if te == None:
        raise Exception("Must input purchased food to FoodMultiplier")
    
    mult = int(apet.ability["effect"]["amount"])
    food_list = [te]
    for food in food_list:
        ### Multiplier is not strict multiplier of current value, but additive
        ###   multiplier of base attack and health
        if food.attack == food.base_attack:
            ### If first time that additive multiplier applied, then account
            ###   for an extra x that already exists 
            mult = mult - 1
        food.attack += food.base_attack*mult
        food.health += food.base_health*mult
    return food_list,[food_list]


def ModifyStats(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    # print("CALLED ModifyStats")
    # print("----------------")
    # print(pet_idx)
    # print(teams)
    # print(fainted_pet)
    # print(te)
    
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    
    attack_amount = 0
    health_amount = 0
    if "attackAmount" in apet.ability["effect"]:
        attack_amount = apet.ability["effect"]["attackAmount"]
    if "healthAmount" in apet.ability["effect"]:
        health_amount = apet.ability["effect"]["healthAmount"]
    for target_pet in target:
        target_pet.attack += attack_amount
        target_pet.health += health_amount
        target_pet.attack = min([target_pet.attack,50])
        target_pet.health = min([target_pet.health,50])
    
    return target,possible


def OneOf(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """ 
    Dog is only one with OneOf anyways
    However, OneOf current not returning possible correctly because I haven't
      decided exactly how possible will be used...
    """
    # if len(fixed_targets) == 0:
    #     target,possible = get_target(apet, apet_idx, teams, te=te)
    # else:
    #     target = fixed_targets
    #     possible = [fixed_targets]
    
    target = [apet]
    possible = [[apet]]
    original_effect = apet.ability["effect"]
    effects = apet.ability["effect"]["effects"]
    chosen_idx = np.random.choice(np.arange(0,len(effects)), size=(1,))[0]
    effect = effects[chosen_idx]
    effect_kind = effect["kind"]
    apet.ability["effect"] = effect
    func = get_effect_function(effect_kind)
    target = func(apet, apet_idx, teams, te, fixed_targets)[0]
    apet.ability["effect"] = original_effect
    return target,possible


def ReduceHealth(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    per = apet.ability["effect"]["percentage"]*0.01
    for temp_pet in target:
        if temp_pet.health > 0:
            temp_pet.health = int(temp_pet.health*per)
            if temp_pet.health == 0:
                ### Floor health of 1
                temp_pet.health = 1
    return target,possible


def RefillShops(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """
    Only Cow has refill shop in newest patch anyways...
    
    """
    if apet.name != "pet-cow":
        raise Exception("Only cow implemented for RefillShops")
    shop = apet.shop
    level = apet.level
    targets = []
    for slot in shop:
        if slot.slot_type == "food":
            temp_food = Food("milk")
            temp_food.attack *= level
            temp_food.health *= level
            slot.item = temp_food
            targets.append(slot)
    return targets,[targets]


def RepeatAbility(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """ 
    Tiger implementation. 
    
    """
    ### First, modify te by the level of the tiger
    original_level = te.level
    te.level = apet.level
    
    ### Get te ability
    func = get_effect_function(te)
    
    ### Call will te as apet
    if len(fixed_targets) == 0:
        targets,possible = func(te, apet_idx, teams, te=None, fixed_targets=[])
    else:
        ### Use fixed_targets if the repeated function is supposed to target
        ### exactly the same pets again
        targets,possible = func(te, apet_idx, teams, te=fixed_targets)
    
    te.level = original_level
    return targets,possible


def SummonPet(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """
    
    """
    # print("CALLED SUMMON")
    # print("----------------")
    # print(pet_idx)
    # print(teams)
    # print(fainted_pet)
    # print(te)
    
    fteam,oteam = get_teams(apet_idx,teams)
    spet_name = apet.ability["effect"]["pet"]
    team = apet.ability["effect"]["team"]
    summon_idx = te_idx
    
    if len(fixed_targets) > 0:
        raise Exception("Not implemented")
    
    if team == "Friendly":
        target_team = fteam
        ### First move team as far backward as possible
        target_team.move_backward()
        ### Then move all animals forward that are infront of the target pet
        end_idx = summon_idx[1]+2
        target_team.move_forward(start_idx=0, end_idx=end_idx)
    elif team == "Enemy":
        target_team = oteam
        target_team.move_forward()
    else:
        raise Exception(apet.ability["effect"]["team"])
    
    n = 1
    if apet.name == "pet-sheep":
        n = 2
    elif apet.name == "pet-rooster":
        n = apet.level
    
    target = []
    for _ in range(n):
        ### Check for furthest back open position
        empty_idx = []
        for iter_idx,temp_slot in enumerate(target_team):
            if temp_slot.empty:
                empty_idx.append(iter_idx)
        if len(empty_idx) == 0:
            ### Can safely return, cannot summon
            return target,[target]
                
        target_slot_idx = np.max(empty_idx)
        target_team[target_slot_idx] = spet_name
        spet = target_team[target_slot_idx].pet
        
        if "withAttack" in apet.ability["effect"]:
            spet.attack = apet.ability["effect"]["withAttack"]
        if "withHealth" in apet.ability["effect"]:
            spet.health = apet.ability["effect"]["withHealth"]
        if "withLevel" in apet.ability["effect"]:
            spet.level = apet.ability["effect"]["withLevel"]
        if apet.name == "pet-rooster":
            spet.attack = int(apet.attack*0.5)
        
        target.append(spet)
        
    ### Move back forward
    target_team.move_forward()
    
    return target,[target]


def SummonRandomPet(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """
    
    """
    fteam,oteam = get_teams(apet_idx,teams)
    summon_idx = te_idx
    
    if len(fixed_targets) > 0:
        chosen = fixed_targets[0]
        if len(fixed_targets) > 1:
            raise Exception(
                "Only 1 fixed_targets input allowed for SummonRandomPet")
    else:
        tier = apet.ability["effect"]["tier"]
        if fteam.pack == "StandardPack":
            possible = pet_tier_lookup_std[tier]
        elif fteam.pack == "ExpansionPack1":
            possible = pet_tier_lookup[tier]
        else:
            raise Exception()
        chosen = np.random.choice(possible, (1,))[0]
    
    
    
    #### Perform team movement to ensure that the pet is summoned in the 
    #### correct position
    ### First move team as far backward as possible
    fteam.move_backward()
    ### Then move all animals forward that are infront of the target pet
    end_idx = summon_idx[1]+2
    fteam.move_forward(start_idx=0, end_idx=end_idx)
    
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
    if "baseAttack" in apet.ability["effect"]:
        sattack = apet.ability["effect"]["baseAttack"]
    else:
        sattack = data["pets"][spet.name]["baseAttack"]
    if "baseHealth" in apet.ability["effect"]:
        shealth = apet.ability["effect"]["baseHealth"]
    else:
        shealth = data["pets"][spet.name]["baseHealth"]
        
    spet.attack = sattack
    spet.health = shealth
    fteam.move_forward()
    return [spet],[[x] for x in possible]

def Swallow(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    fteam,oteam = get_teams(apet_idx,teams)
    if len(fixed_targets) == 0:
        target,possible = get_target(apet, apet_idx, teams, te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
        
    if len(target) == 0:
        return target
    output_level = apet.level
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
    
    if apet.name != "pet-whale":
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
        apet.set_ability(summon_dict)
        faint_idx = fteam.get_idx(temp_target)
        temp_target.health = -1
    
    fteam.move_forward()
    return target,possible


def TransferAbility(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    fteam,oteam = get_teams(apet_idx,teams)
    if len(fixed_targets) == 0:
        target,possible = get_target(apet,apet_idx,teams,te=te,get_from=True)
    else:
        target = fixed_targets
        possible = [fixed_targets]
    
    if len(target) > 0:
        apet.set_ability(target[0].ability)
        
    return target,possible


def TransferStats(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    fteam,oteam = get_teams(apet_idx,teams)
    if len(fixed_targets) == 0:
        target,possible = get_target(apet,apet_idx,teams,te=te)
    else:
        target = fixed_targets
        possible = [fixed_targets]
        
    effect = apet.ability["effect"]
    copy_attack = effect["copyAttack"]
    copy_health = effect["copyHealth"]
    percentage = 1
    if "percentage" in effect["to"]:
        percentage = effect["to"]["percentage"]*0.01
    from_self = effect["from"]["kind"] == True
    
    for entry in target:
        if from_self:
            #### dodo is only from_self and it is additive, not copy, unlike
            #### what the database says
            if copy_attack:
                entry.attack += max(int(apet.attack*percentage),1)
            if copy_health:
                raise Exception("This should not be possible")
        else:
            temp_from = get_target(apet,apet_idx,teams,te=te,get_from=True)
            ### Randomness not needed as outcome will be the same for all pets
            ###   that have this ability
            temp_from = temp_from[0][0]
            if copy_attack:
                apet.attack = temp_from.attack
            if copy_health:
                apet.health = temp_from.health
    
    return target,possible


def DiscountFood(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    shop = apet.shop
    if shop == None:
        raise Exception("No shop found to discount food")
    amount = apet.ability["effect"]["amount"]
    targets = []
    for slot in shop:
        if slot.slot_type == "food":
            slot.cost = max((slot.cost - amount), 0)
            targets.append(slot)
    return targets,[targets]


def GainAbility(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    """ 
    Only Octopus has GainAbility. Also, within programming framework, 
    GainAbility is not necessary because the ability is automatically 
    updated with levelup. 
    """
    return [apet],[[apet]]


def none(apet,apet_idx,teams,te=None,te_idx=[],fixed_targets=[]):
    return [],[]


curr = sys.modules[__name__]
mem = inspect.getmembers(curr, inspect.isfunction)
func_dict = {}
for temp_name,func in mem:
    func_dict[temp_name] = func