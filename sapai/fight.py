

import numpy as np

from teams import Team


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
        self.t1 = c1.copy()
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
            self.pet_effect_order()
            ### Then attack
            result = self.attack(fight_iter)
            fight_iter += 1
            if result == False:
                break
        
        ### Check winner and return 0 for t0 win, 1 for t1 win, 2 for draw
        
        
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
            self.phase_dict = phase_dict
            
            ### If animals have moved or fainted then effect order must be updated
            if temp_phase.startswith("phase_move"):
                self.update_pet_effect_order()
        
        self.fight_history.update(phase_dict)
    
    
    def attack(self, fight_iter):
        """ 
        Perform and attack and then check for new pet triggers 
        
        Returns whether or not another attack should occur. This depends on 
        if all animals of one team have a health of 0 already. 

        """
        t0 = self.t0
        t1 = self.t1
        
        attack_str = "attack_{}".format(fight_iter)
        phase_dict = {
            attack_str: {
            "phase_move": [[str(t0), str(t1)]],
            "phase_attack_before": [],
            "phase_attack": [],
            "phase_after_attack": [],
            "phase_faint": [],
            "phase_summon": [],
            "phase_move": []}}
        
        t0.move_forward()
        t1.move_forward()
        phase_dict[attack_str]["phase_move"].append([str(t0), str(t1)])

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
        
        ### Pets in the front of each team attack
        
        
        ### Apply effects related to this attack
        
        
        ### Apply effects related to pet deaths HOWEVER Before or after 
        ### summoning effects based on fainting? Is it only based on attack?
        
        
        ### Check if fight is over
        
        self.fight_history.update(phase_dict)
        
        ### End fight
        return False

    
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
            print(uattack)
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
            
        
        ### TODO: CHECK FOR TIGER and give tiger priority correct order
        
        
        ### Build final queue
        self.pet_effect_order = []
        for t,i in zip(teams,idx):
            self.pet_effect_order.append((t,i))
            
    
    def fightviz(self):
        """
        Draw graph visualizing what occured in the fight from the fight history
        
        """
        raise Exception()
    
    
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
        start_order = [str(teams[0]), str(teams[1])]
        teams[0].move_forward()
        teams[1].move_forward()
        end_order = [str(teams[0]), str(teams[1])]
        phase_dict[phase] = [start_order, end_order]
        
    elif phase == "phase_start":
        fight_phase_start(phase,teams,pet_effect_order,phase_dict)
    
    ##### Trigger logic for an attack
    elif phase == "phase_attack_before":
        raise Exception()
    
    elif phase == "phase_attack":
        ### Check if fainted and performed fainted triggers
        raise Exception()

    elif phase == "phase_attack_after":
        raise Exception()

    elif phase == "phase_faint":
        raise Exception()

    elif phase == "phase_summon":
        raise Exception()
    

def fight_phase_start(phase,teams,pet_effect_order,phase_dict):
    pao = pet_effect_order
    for team_idx,pet_idx in pao:
        p = teams[team_idx][pet_idx].pet
        print(p)
        pt = p.ability["trigger"]
        
        if pt != "StartOfBattle":
            ### Nothing to do
            continue   
        
        effect = p.ability["effect"]
        kind = effect["kind"]
        raise Exception()