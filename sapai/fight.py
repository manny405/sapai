
import copy
import numpy as np

from pets import Pet
from teams import Team
from effects import get_effect_function,get_pet,get_teams


class Fight():
    """
    Performs a fight. 
    
    Most important thing here to implement is the action queue including the 
    logic for when actions should be removed from the action queue upon death. 
    
    Note that effects are performed in the order of highest attack to lowest
    attack. If there is a tie, then health values are compared. If there is a 
    tie then a random animal is chosen first. This is tracked by the 
    pet_effect_order which is updated before every turn of the fight. 
    
    Any effect which is in the queue for a given turn is executed, even if the 
    animal dies due to preceeding effect, as the game entails.
    
    """
    def __init__(self, t0, t1):
        """
        Performs the fight between the input teams t1 and t2. 
        
        """
        ### Make copy each team to cary out the fight so that the original
        ### pets are not modified in any way after the fight
        self.t0 = t0.copy()
        self.t0._fight = True
        self.t1 = t1.copy()
        self.t1._fight = True
        
        ### Internal storage
        self.pet_effect_order = []
        self.fight_history = {}
        
        ### Build initial effect queue order
        self.update_pet_effect_order()
    
    
    def fight(self):
        ### Perform all effects that occur at the start of the fight
        self.start()
        
        fight_iter = 0
        while True:
            ### First update effect order
            self.update_pet_effect_order()
            ### Then attack
            result = self.attack(fight_iter)
            fight_iter += 1
            if result == False:
                break
        
        ### Check winner and return 0 for t0 win, 1 for t1 win, 2 for draw
        return self.check_fight_result()
        
    def start(self):
        """ 
        Perform all start of fight effects 
        
        """
        ### First move the teams forward
        t0 = self.t0            
        t1 = self.t1
        
        ### Go through effect order list and perform effects
        teams = [t0, t1]
        phase_dict = {
                      "init": [[str(x) for x in t0], [str(x) for x in t1]],
                      "start": {
                      "phase_move_start": [],
                      "phase_start": [],
                      "phase_faint": [],
                      "phase_summon": [],
                      "phase_move_end": []}}
        
        for temp_phase in phase_dict["start"]:
            fight_phase(temp_phase, 
                        teams, 
                        self.pet_effect_order,
                        phase_dict["start"])
            
            self.fight_history.update(phase_dict)
            
            ### If animals have moved or fainted then effect order must be updated
            if temp_phase.startswith("phase_move"):
                self.update_pet_effect_order()
        
    
    def attack(self, fight_iter):
        """ 
        Perform and attack and then check for new pet triggers 
        
        Returns whether or not another attack should occur. This depends on 
        if all animals of one team have a health of 0 already. 
        
        Order of operations for an attack are:
            - Pets in the front of each team attack
            - Apply effects related to this attack
            - Apply effects related to pet deaths 
            - Summon phase
            - Check if fight is over
            
        """
        t0 = self.t0
        t1 = self.t1
        
        attack_str = "attack {}".format(fight_iter)
        phase_dict = {
            attack_str: {
            "phase_move_start": [],
            "phase_attack_before": [],
            "phase_attack": [],
            "phase_faint": [],
            "phase_summon": [],
            "phase_attack_after": [],
            "phase_faint_2": [],
            "phase_move_end": []}}
        
        
        ### Check exit condition, if one team has no animals, return False
        found0 = False
        for temp_slot in t0:
            if not temp_slot.empty:
                found0 = True
                break
        found1 = False
        for temp_slot in t1:
            if not temp_slot.empty:
                found1 = True
                break
        if found0 == False:
            return False
        if found1 == False:
            return False
        
        teams = [t0, t1]
        for temp_phase in phase_dict[attack_str]:
            fight_phase(temp_phase, 
                        teams, 
                        self.pet_effect_order,
                        phase_dict[attack_str])

            self.fight_history.update(phase_dict)

        ### Check if fight is over
        status = self.check_fight_result()
        if status < 0:
            return True
        else:
            ### End fight
            return False

    
    def check_fight_result(self):
        t0 = self.t0
        t1 = self.t1
        found0 = False
        for temp_slot in t0:
            if not temp_slot.empty:
                if temp_slot.pet.health > 0:
                    found0 = True
                    break
        found1 = False
        for temp_slot in t1:
            if not temp_slot.empty:
                if temp_slot.pet.health > 0:
                    found1 = True
                    break
        if found0 and found1:
            ### Fight not over
            return -1
        if found0:
            ### t0 won
            return 0
        if found1:
            ### t1 won
            return 1
        ### Must have been draw
        return 2
    
    
    def update_pet_effect_order(self):
        """ 
        
        Prepares the order that the animals effects should be considered in
        
        Note that effects are performed in the order of highest attack to lowest
        attack. If there is a tie, then health values are compared. If there is  
        a tie then a random animal is chosen first. 
        
        """
        ### Build all data types to determine effect order
        pets = [x for x in self.t0] + [x for x in self.t1]
        attack = [x.attack for x in self.t0] + [x.attack for x in self.t1]
        health = [x.health for x in self.t0] + [x.health for x in self.t1]
        teams = [0 for x in self.t0] + [1 for x in self.t1]
        idx = [x for x in range(5)] + [x for x in range(5)]
        
        for iter_idx,value in enumerate(attack):
            if value == "none":
                attack[iter_idx] = 0
                health[iter_idx] = 0

        ### Basic sorting by max attack
        # sort_idx = np.argsort(attack)[::-1]
        # attack = np.array([attack[x] for x in sort_idx])
        # health = np.array([health[x] for x in sort_idx])
        # teams = np.array([teams[x] for x in sort_idx])
        # idx = np.array([idx[x] for x in sort_idx])
        sort_idx = np.arange(0,len(attack))
        attack = np.array(attack)
        health = np.array(attack)
        teams = np.array(teams)
        idx = np.array(idx)
                
        ### Find attack collisions
        uniquea = np.unique(attack)[::-1]
        start_idx = 0
        for uattack in uniquea:
            ### Get collision idx
            temp_idx = np.where(attack == uattack)[0]
            temp_attack = attack[temp_idx]
            
            ### Initialize final idx for sorting
            temp_sort_idx = np.arange(0,len(temp_idx))
            
            if len(temp_idx) < 2:
                end_idx = start_idx + len(temp_idx)
                sort_idx[start_idx:end_idx] = temp_idx
                start_idx = end_idx
                continue
            
            ### Correct attack collisions by adding in health
            temp_health = health[temp_idx]
            temp_stats =  temp_attack + temp_health
            temp_start_idx = 0
            for ustats in np.unique(temp_stats)[::-1]:
                temp_sidx = np.where(temp_stats == ustats)[0]
                temp_sidx = np.random.choice(temp_sidx, size=(len(temp_sidx),), 
                                             replace=False)
                temp_end_idx = temp_start_idx+len(temp_sidx)
                temp_sort_idx[temp_start_idx:temp_end_idx] = temp_sidx
                temp_start_idx = temp_end_idx
            
            ### Double check algorithm
            sorted_attack = [temp_attack[x] for x in temp_sort_idx]
            sorted_health = [temp_health[x] for x in temp_sort_idx]
            for iter_idx,tempa in enumerate(sorted_attack[1:-1]):
                iter_idx += 1
                if tempa < sorted_attack[iter_idx]:
                    raise Exception("That's impossible. Sorting issue.")
            for iter_idx,temph in enumerate(sorted_health[1:-1]):
                iter_idx += 1
                if temph < sorted_health[iter_idx]:
                    raise Exception("That's impossible. Sorting issue.")
            
            ### Dereference temp_sort_idx and store in sort_idx
            end_idx = start_idx + len(temp_idx)
            sort_idx[start_idx:end_idx] = temp_idx
            start_idx = end_idx

        ### Finish sorting by max attack
        attack = np.array([attack[x] for x in sort_idx])
        health = np.array([health[x] for x in sort_idx])
        teams = np.array([teams[x] for x in sort_idx])
        idx = np.array([idx[x] for x in sort_idx])

        ### Double check sorting algorithm
        for iter_idx,tempa in enumerate(attack[1:-1]):
            iter_idx += 2
            if tempa < attack[iter_idx]:
                raise Exception("That's impossible. Sorting issue.") 
        
        ### Build final queue
        self.pet_effect_order = []
        for t,i in zip(teams,idx):
            self.pet_effect_order.append((t,i))
            
    
    
def fight_phase(phase,  
                teams,
                pet_effect_order,
                phase_dict):
    """
    Definition for performing all effects and actions throughout the fight. 
    Implemented as function instead of class method to save an extra 
    indentation... Also, this function is certainly a bit ugly right now. 
    There are better ways to implement this switching behavior. However, this 
    certainly works and other forms of implementing it would just be aesthetic
    improvements. 
    
    After evey major phase, phase_faint should be checked
    
    Possible phases of a fight:
        phase_move_start
        phase_start
        phase_attack_before
        phase_attack
        phase_attack_after
        phase_faint
        phase_summon
        phase_move_end
    
    Possible pet triggers for this function:
        StartOfBattle
        Summoned
        Faint
        BeforeAttack
        Hurt
        AfterAttack
        CastsAbility (Tiger)
        KnockOut
    
    Possible pet triggers not for this function:
        Sell
        EatsShopFood
        EndOfTurn
        BuyFood
        Buy
        LevelUp
        BuyAfterLoss
        BuyTier1Animal
        EndOfTurnWith2PlusGold
        EndOfTurnWith3PlusGold
        EndOfTurnWith4OrLessAnimals
        EndOfTurnWithLvl3Friend
        StartOfTurn
        
    triggers = []
    for key,value in data["pets"].items():
        if "level1Ability" in value:
            if "trigger" in value["level1Ability"]:
                if value["level1Ability"]["trigger"] == "CastsAbility":
                    print(key)
                triggers.append(value["level1Ability"]["trigger"])
        
    """
    ### Parse inputs and collect info
    pao = pet_effect_order
    
    ##### Trigger logic for starting battle
    if phase.startswith("phase_move"):
        start_order = [[str(x) for x in teams[0]], [str(x) for x in teams[1]]]
        teams[0].move_forward()
        teams[1].move_forward()
        end_order = [[str(x) for x in teams[0]], [str(x) for x in teams[1]]]
        phase_dict[phase] = [start_order, end_order]
        
    elif phase == "phase_start":
        fight_phase_start(phase,teams,pet_effect_order,phase_dict)
    
    ##### Trigger logic for an attack
    elif phase == "phase_attack_before":
        fight_phase_attack_before(phase,teams,pet_effect_order,phase_dict)
    
    elif phase == "phase_attack":
        ### Check if fainted and performed fainted triggers
        fight_phase_attack(phase,teams,pet_effect_order,phase_dict)

    elif phase == "phase_attack_after":
        fight_phase_attack_after(phase,teams,pet_effect_order,phase_dict)

    elif "phase_faint" in phase:
        fight_phase_faint(phase,teams,pet_effect_order,phase_dict)

    elif phase == "phase_summon":
        fight_phase_summon(phase,teams,pet_effect_order,phase_dict)
        
    else:
        raise Exception("Phase {} not found".format(phase))



def get_attack_idx(phase,teams,pet_effect_order,phase_dict):
    """
    Helper function to get the current animals participating in the attack. 
    These are defined as the first animals in each team that have a health above
    zero. 
    """
    t0_idx = -1
    for iter_idx,temp_slot in enumerate(teams[0]):
        if not temp_slot.empty:
            if temp_slot.pet.health > 0:
                t0_idx = iter_idx
                break
    t1_idx = -1
    for iter_idx,temp_slot in enumerate(teams[1]):
        if not temp_slot.empty:
            if temp_slot.pet.health > 0:
                t1_idx = iter_idx
                break
    ret_idx = []
    if t0_idx > -1:
        ret_idx.append((0,t0_idx))
    if t1_idx > -1:
        ret_idx.append((1,t1_idx))
        
    ### Getting next idx at the same time
    t0_next_idx = -1
    for iter_idx,temp_slot in enumerate(teams[0]):
        if not temp_slot.empty:
            if temp_slot.pet.health > 0:
                if t0_idx == iter_idx:
                    continue
                t0_next_idx = iter_idx
                break
    t1_next_idx = -1
    for iter_idx,temp_slot in enumerate(teams[1]):
        if not temp_slot.empty:
            if temp_slot.pet.health > 0:
                if t1_idx == iter_idx:
                    continue
                t1_next_idx = iter_idx
                break
    ret_next_idx = []
    if t0_next_idx > -1:
        ret_next_idx.append((0,t0_next_idx))
    else:
        ret_next_idx.append(())
    if t1_next_idx > -1:
        ret_next_idx.append((1,t1_next_idx))
    else:
        ret_next_idx.append(())
            
    return ret_idx,ret_next_idx


def fight_phase_attack_after(phase,teams,pet_effect_order,phase_dict):
    ### SPECIFIC IMPLEMENTATION JUST TO HANDLE RHINO 
    phase_list = phase_dict["phase_attack_after"]
    attacks = phase_dict["phase_attack"]
    if len(attacks) == 0:
        return phase_dict
    
    p0 = attacks[0][2][0]
    p1 = attacks[0][3][0]
    
    if p0.ability["trigger"] == "KnockOut":
        if p0.health <= 0:
            ### Rhino doesn't trigger if it fainted
            pass
        elif p1.health <= 0:
            kind = p0.ability["effect"]["kind"]
            func = get_effect_function(kind)
            pet_idx = teams[0].get_idx(p0)
            while True:
                targets = func((0,pet_idx),teams)
                phase_list.append((
                    func.__name__,
                    (0,pet_idx),
                    (str(p0)),
                    [str(x) for x in targets]))
                if targets[0].health < 0:
                    continue
                friend_ahead_check(
                    (0,pet_idx), 
                    teams, 
                    func,
                    "CastsAbility", 
                    phase_list,
                    activate=True)
                if len(targets) == 0:
                    break
                if targets[0].health > 0:
                    break
    
    if p1.ability["trigger"] == "KnockOut":
        if p1.health <= 0:
            ### Rhino doesn't trigger if it fainted
            pass
        elif p0.health <= 0:
            kind = p0.ability["effect"]["kind"]
            func = get_effect_function(kind)
            pet_idx = teams[1].get_idx(p1)
            while True:
                targets = func((1,pet_idx),teams)
                phase_list.append((
                    func.__name__,
                    (1,pet_idx),
                    (str(p1)),
                    [str(x) for x in targets]))
                if targets[0].health < 0:
                    continue
                friend_ahead_check(
                    (0,pet_idx), 
                    teams, 
                    func,
                    "CastsAbility",
                    phase_list,
                    activate=True)
                if len(targets) == 0:
                    break
                if targets[0].health > 0:
                    break
    
    attacks[0][2] = (str(attacks[0][2][0]))
    attacks[0][3][0] = str(attacks[0][3][0])
    
    return phase_dict

def get_attack(p0,p1):
    """ Ugly but works """
    attack_list = [int(p0.attack), int(p1.attack)]
    if p0.status == "status-garlic-armor":
        attack_list[1] -= 2
        attack_list[1] = max([attack_list[1], 1])
    if p1.status ==  "status-garlic-armor":
        attack_list[0] -= 2
        attack_list[0] = max([attack_list[0], 0])
    if p0.status == "status-melon-armor":
        attack_list[1] -= 20
        attack_list[1] = max([attack_list[1], 0])
        p0.status = "none"
    if p1.status == "status-melon-armor":
        attack_list[0] -= 20
        attack_list[0] = max([attack_list[0], 0])
        p1.status = "none"
    if p0.status == "status-bone-attack":
        attack_list[0] = attack_list[0]+5
    if p1.status == "status-bone-attack":
        attack_list[1] = attack_list[1]+5
    if p0.status == "status-steak-attack":
        attack_list[0] = attack_list[0]+20
        p0.status = "none"
    if p1.status == "status-steak-attack":
        attack_list[1] = attack_list[1]+20
        p0.status = "none"
    return attack_list
        

def fight_phase_attack(phase,teams,pet_effect_order,phase_dict):
    phase_list = phase_dict["phase_attack"]
    aidx,nidx = get_attack_idx(phase,teams,pet_effect_order,phase_dict)
    if len(aidx) != 2:
        ### Must be two animals available for attacking to continue with fight
        return phase_list
    
    p0 = teams[0][aidx[0][1]].pet
    p1 = teams[1][aidx[1][1]].pet
    
    #### Implement food
    p0a,p1a = get_attack(p0,p1)
    
    teams[0][aidx[0][1]].pet.health -= p1a
    teams[1][aidx[1][1]].pet.health -= p0a
    phase_list.append([
            "Attack",
            (aidx[0]),
            [p0],
            [p1]])
    
    ### Implement chili
    if p0.status == "status-splash-attack":
        original_attack = p0.attack
        original_status = p0.status
        p0.attack = 5
        if len(nidx[1]) != 0:
            pn1 = teams[1][nidx[1][1]].pet
            p0a,p1a = get_attack(p0,pn1)
            pn1.health -= p0a
            phase_list.append([
                "splash",
                (aidx[0]),
                (str(p0)),
                [str(pn1)]])
        p0.status = original_status
        p0.attack = original_attack
        
    if p1.status == "status-splash-attack":
        original_attack = p1.attack
        original_status = p1.status
        p1.attack = 5
        if len(nidx[0]) != 0:
            pn0 = teams[0][nidx[0][1]].pet
            p0a,p1a = get_attack(pn0,p1)
            pn0.health -= p1a
            phase_list.append([
                "splash",
                (aidx[1]),
                (str(p0)),
                [str(pn0)]])
        p1.status = original_status
        p1.attack = original_attack
    
    #### Check for effects from attack of pet infront
    friend_ahead_check(
        aidx[0], 
        teams, 
        "Attack", 
        "AfterAttack", 
        phase_list,
        activate=True)
    friend_ahead_check(
        aidx[1], 
        teams, 
        "Attack", 
        "AfterAttack", 
        phase_list,
        activate=True)
    
    return phase_dict


def fight_phase_attack_before(phase,teams,pet_effect_order,phase_dict):
    phase_list = phase_dict["phase_attack_before"]
    aidx,nidx = get_attack_idx(phase,teams,pet_effect_order,phase_dict)
    pao = pet_effect_order
    if len(aidx) != 2:
        ### Must be two animals available for attacking to continue with fight
        return phase_list
    for team_idx,pet_idx in pao:
        if aidx[team_idx][1] != pet_idx:
            ### Effects are only activated for the attacking pet
            continue
        
        p = teams[team_idx][pet_idx].pet
        pt = p.ability["trigger"]
        
        if pt != "BeforeAttack":
            ### Nothing to do
            continue   
        
        effect = p.ability["effect"]
        kind = effect["kind"]
        pet_str = str(p)
        func = get_effect_function(kind)
        targets = func((team_idx,pet_idx),teams)
        phase_list.append((
            func.__name__,
            (team_idx,pet_idx),
            (pet_str),
            [str(x) for x in targets]))
        
        ### Before friend_ahead_check, need to re-obtin the correct pet_idx
        pet_idx = teams[team_idx].get_idx(p)
        friend_ahead_check(
            (team_idx,pet_idx), teams, func, "CastsAbility", phase_list)
    return phase_dict



def fight_phase_summon(phase,teams,pet_effect_order,phase_dict):
    phase_list = phase_dict["phase_summon"]
    faint_dict = phase_dict["phase_faint"][0]
    ### Check fainted for animals to summon. Note that the order here will be 
    ### slightly off compared to the real game. However, no animals have effects
    ### when they are summoned. Therefore, there's no issue. 
    ### Also, check honey status at this stage
    for _,entry in faint_dict.items():
        next_pet_list = []
        for entry_idx,faint_info in enumerate(entry):
            if faint_info[0] == "SummonAfterFaint":
                temp_pet = faint_info[2][0]
                temp_idx = faint_info[1]
                kind = temp_pet.ability["effect"]["kind"]
                func = get_effect_function(kind)
                
                ### Checking for tiger beforhand is only way. Spaghetti code...
                next_pet = friend_ahead_check(
                    temp_idx, teams, func, 
                    "CastsAbility", 
                    phase_list,
                    fainted_pet=temp_pet,
                    activate=False)
                
                if next_pet in next_pet_list:
                    ### Cannot be in next_pet_list twice, therefore, must belong
                    ### to the last instance in which it's found as the next_pet
                    next_pet_list = [[]] + next_pet_list
                else:
                    next_pet_list.append(next_pet)
            else:
                next_pet_list.append([])
        
        for entry_idx,faint_info in enumerate(entry):
            if faint_info[0] == "SummonAfterFaint":
                temp_pet = faint_info[2][0]
                next_alive = faint_info[2][1]
                temp_idx = faint_info[1]
                kind = temp_pet.ability["effect"]["kind"]
                func = get_effect_function(kind)
                all_targets = []
                if next_alive == None:
                    # ### Must be placed at the end
                    # final_idx = -1
                    # for iter_idx,temp_slot in enumerate(teams[temp_idx[0]]):
                    #     if not temp_slot.empty:
                    #         if temp_slot.pet.name != "pet-dirty-rat":
                    #             final_idx = max([final_idx,iter_idx])
                    # if final_idx < 0:
                    #     temp_idx = (faint_info[1][0], 4)
                    # else:
                    #     next_alive = teams[faint_info[1][0]][final_idx]
                    pass
                
                ### Checking for tiger beforhand is only way. Spaghetti code...
                next_pet = next_pet_list[entry_idx]
                original_ability = copy.deepcopy(temp_pet.override_ability_dict)
                targets = func(temp_idx,teams,fainted_pet=temp_pet,te=next_alive)
                all_targets += targets
                
                ### Reset entry of faint_info
                entry[entry_idx] = (
                    faint_info[0],
                    faint_info[1],
                    str(temp_pet),
                    faint_info[3]
                )
                
                ### Add info to summon
                phase_list.append((
                    func.__name__,
                    temp_idx,
                    (str(temp_pet)),
                    [str(x) for x in targets]))
                
                if type(next_pet).__name__ == "Pet":
                    ### Next pet must be Tiger
                    next_pet_idx = teams[faint_info[1][0]].get_idx(next_pet)
                    ### Reset ability
                    if len(original_ability) != 0:
                        temp_pet.set_ability(original_ability)
                    kind = temp_pet.ability["effect"]["kind"]
                    func = get_effect_function(kind)
                    ### Call function again using the position of the tiger
                    targets = func((faint_info[1][0],next_pet_idx),
                                   teams,fainted_pet=temp_pet,te=next_pet)
                    final_idx = teams[faint_info[1][0]].get_idx(next_pet)
                    phase_list.append((
                        func.__name__,
                        (temp_idx[0],final_idx),
                        (str(next_pet)),
                        [str(x) for x in targets]))
                    all_targets += targets
                    
                ### Honey implementation
                if temp_pet.status == "status-honey-bee":
                    ### Get first index of summoned animals
                    fteam = teams[faint_info[1][0]]
                    fteam.move_backward()
                    all_idx = []
                    for temp_summoned_pet in all_targets:
                        all_idx.append(fteam.get_idx(temp_summoned_pet))
                    min_idx = np.min(all_idx)
                    fteam.move_forward(start_idx=0,end_idx=min_idx)
                    for slot_idx,temp_slot in enumerate(fteam):
                        if temp_slot.empty:
                            bee = Pet("pet-bee")
                            fteam[slot_idx] = bee
                            fteam.move_forward()
                            final_idx = fteam.get_idx(bee)
                            phase_list.append((
                                "Honey",
                                (temp_idx[0],final_idx),
                                (str(temp_pet)),
                                [str(bee)]))
                            break
                    
                    
                    

def fight_phase_faint(phase,teams,pet_effect_order,phase_dict):
    phase_list = phase_dict["phase_faint"]
    fainted = {"t0": [], "t1": []}
    for team_idx,temp_team in enumerate(teams):
        for iter_idx,temp_slot in enumerate(temp_team):
            if temp_slot.empty:
                continue
            if temp_slot.pet.health <= 0:
                pet_str = str(temp_slot.pet)
                temp_team.remove(temp_slot)
                next_alive = None
                for next_iter_idx,next_temp_slot in enumerate(temp_team[iter_idx+1:]):
                    if not next_temp_slot.empty:
                        if next_temp_slot.pet.health > 0:
                            next_alive = next_temp_slot.pet
                            break
                ### Need to check for fainted effect
                fainted_trigger = temp_slot.pet.ability["trigger"]
                trigger_by = temp_slot.pet.ability["triggeredBy"]["kind"]
                kind = temp_slot.pet.ability["effect"]["kind"]
                if fainted_trigger == "Faint" and \
                    kind in ["SummonPet", "SummonRandomPet"]:
                        ### Will be handled in the phase_summon
                        func_name = "SummonAfterFaint"
                        targets = []
                        ### Store pet in pet_idx for summon phase
                        pet_str = (temp_slot.pet, next_alive)
                elif fainted_trigger == "Faint" and trigger_by == "Self":
                    func = get_effect_function(kind)
                    func_name = func.__name__
                    targets = func((team_idx,iter_idx),teams)
                else:
                    func_name = "None"
                    targets = []
                
                fainted["t{}".format(team_idx)].append((
                    func_name,
                    (team_idx,iter_idx),
                    (pet_str),
                    [str(x) for x in targets]))
                
                ### Check if next alive has trigger
                if next_alive == None:
                    continue
                next_trigger = next_alive.ability["trigger"]
                next_triggered_by = next_alive.ability["triggeredBy"]["kind"]
                next_kind = next_alive.ability["effect"]["kind"]
                next_idx = temp_team.get_idx(next_alive)
                next_str = str(next_alive)
                print(next_alive, next_trigger, next_triggered_by)
                if next_trigger == "Faint" and \
                    next_triggered_by == "FriendAhead":
                        next_func = get_effect_function(next_kind)
                        next_func_name = next_func.__name__
                        next_targets = next_func((team_idx,next_idx),teams)
                        fainted["t{}".format(team_idx)].append((
                            next_func.__name__,
                            (team_idx,next_idx),
                            (next_str),
                            [str(x) for x in next_targets]))
                        
                        ### Check animal behind for Tiger
                        friend_ahead_check(
                            (team_idx,next_idx), 
                            teams, 
                            next_func, 
                            "CastsAbility", 
                            fainted["t{}".format(team_idx)])
    
    phase_list.append(fainted)
    return phase_dict
    

def fight_phase_start(phase,teams,pet_effect_order,phase_dict):
    phase_list = phase_dict["phase_start"]
    pao = pet_effect_order
    for team_idx,pet_idx in pao:
        p = teams[team_idx][pet_idx].pet
        pt = p.ability["trigger"]
        
        if pt != "StartOfBattle":
            ### Nothing to do
            continue   
        
        effect = p.ability["effect"]
        kind = effect["kind"]
        pet_str = str(p)
        func = get_effect_function(kind)
        targets = func((team_idx,pet_idx),teams)
        phase_list.append((
            func.__name__,
            (team_idx,pet_idx),
            (pet_str),
            [str(x) for x in targets]))
        
        ### Before friend_ahead_check, need to re-obtin the correct pet_idx
        pet_idx = teams[team_idx].get_idx(p)
        friend_ahead_check(
            (team_idx,pet_idx), teams, func, "CastsAbility", phase_list)
        
    ### Done programming start!
    return phase_list
        
        
def friend_ahead_check(pet_idx,teams,effect_func,trigger,phase_list,
                       fainted_pet=None,activate=True):
    """
    Check for tiger behind and double the function
    
    Tiger check should really be a "FriendAhead" check. This will also be 
    important for snake. 
    
    Trigger can be:
        CastsAbility
        AfterAttack

    """
    p = get_pet(pet_idx,teams,fainted_pet)
    if pet_idx[1]+1 >= 5:
        ### Cannot have tiger behind
        return 
    fteam,oteam = get_teams(pet_idx,teams)
    
    ### Get possible indices for each team
    fidx = []
    for iter_idx,temp_slot in enumerate(fteam):
        if iter_idx == pet_idx[1]:
            fidx.append(iter_idx)
            continue
        if not temp_slot.empty:
            fidx.append(iter_idx)
    targets = []
    relative_idx = fidx.index(pet_idx[1])
    if len(fidx) > relative_idx+1:
        next_idx = fidx[relative_idx+1]
        next_pet_idx = (pet_idx[0], next_idx)
        next_pet = fteam[next_idx].pet
        if next_pet.ability["triggeredBy"]["kind"] != "FriendAhead":
            return targets
        
        ### First check trigger
        if next_pet.ability["trigger"] != trigger:
            return targets

        next_kind = next_pet.ability["effect"]["kind"]
        if next_kind == "RepeatAbility":
            if not activate:
                return next_pet
            
            ### Hard-code tiger...
            ### Check for ability override which may have occured, for example
            ###   for a whale
            if p.override_ability:
                ### Reset override_ability
                p.override_ability = False
            
            targets = effect_func(pet_idx,teams)
            phase_list.append((
                effect_func.__name__,
                pet_idx,
                (str(next_pet)),
                [str(x) for x in targets]))
        else:
            next_func = get_effect_function(next_kind)
            pet_str = str(next_pet)
            targets = next_func(next_pet_idx,teams)
            phase_list.append((
                next_func.__name__,
                next_pet_idx,
                (pet_str),
                [str(x) for x in targets]))
            
            ### Check for tiger behind this animal with recursive call
            friend_ahead_check(
                next_pet_idx,
                teams,
                next_func,
                "CastsAbility",
                phase_list,
                fainted_pet=None,
                activate=True)
    
    if not activate:
        return None
    else:
        return targets
    