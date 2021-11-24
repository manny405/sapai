

import numpy as np


class Fight():
    """
    Performs a fight. 
    
    Most important thing here to implement is the action queue including the 
    logic for when actions should be removed from the action queue upon death. 
    
    Note that effects are performed in the order of highest attack to lowest
    attack. If there is a tie, then health values are compared. If there is a 
    tie then a random animal is chosen first. This is tracked by the 
    effect_order which is updated before every turn of the fight. 
    
    Any effect which is in the queue for a given turn is executed, even if the 
    animal dies due to preceeding effect, as the game entails.
    
    """
    def __init__(self, t0, t1):
        """
        Performs the fight between the input teams t1 and t2. 
        
        """
        ### Initialize internal storage
        self.t0 = t0
        self.t1 = t1
        self.team_list = []
        self.effect_order = []
        
        ### Build initial effect queue order
        self.update_effect_order()
        
        ### Perform all effects that occur at the start of the fight
        self.start()
        
        while True:
            ### First update effect order
            self.update_effect_order()
            ### Then attack
            result = self.attack()
            if result == False:
                break
        
        
    def start(self):
        """ Perform all start effects """
        raise Exception("NOT IMPLEMENTED")
    
    
    def attack(self):
        """ 
        Perform and attack and then check for new pet triggers 
        
        Returns whether or not another attack should occur. This depends on 
        if all animals of one team have a health of 0 already. 

        """
        ### Pets in the front of each team attack
        
        
        ### Apply effects related to this attack
        
        
        ### Apply effects related to pet deaths HOWEVER Before or after 
        ### summoning effects based on fainting? Is it only based on attack?
        
        
        ### Check if fight is over
        
        ### End fight
        return False
    
    
    def update_effect_order(self):
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

        ### Basic sorting by max attack
        sort_idx = np.argsort(attack)[::-1]
        attack = np.array([attack[x] for x in sort_idx])
        health = np.array([health[x] for x in sort_idx])
        teams = np.array([teams[x] for x in sort_idx])
        idx = np.array([idx[x] for x in sort_idx])
                
        ### Find attack collisions
        uniquea = np.unique(attack)[::-1]
        for uattack in uniquea:
            ### Get collision idx
            temp_idx = np.where(attack == uattack)[0]
            temp_attack = attack[temp_idx]
            
            ### Initialize final idx for sorting
            temp_sort_idx = np.arange(0,len(temp_idx))
            
            if len(temp_idx) < 2:
                continue
            
            ### Correct attack collisions by adding in health
            temp_health = health[temp_idx]
            temp_stats =  temp_attack + temp_health
            start_idx = 0
            for ustats in np.unique(temp_stats)[::-1]:
                temp_sidx = np.where(temp_stats == ustats)[0]
                temp_sidx = np.random.choice(temp_sidx, size=(len(temp_sidx),), 
                                             replace=False)
                end_idx = start_idx+len(temp_sidx)
                temp_sort_idx[start_idx:end_idx] = temp_sidx
                start_idx = end_idx
            
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
            dereferenced_idx = temp_idx[temp_sort_idx]
            sort_idx[temp_idx] = dereferenced_idx


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
        self.effect_order = []
        for t,i in zip(teams,idx):
            self.effect_order.append((t,i))
              
        
    
    
    

        