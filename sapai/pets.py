

#%%
from sapai.data import data


#%%

class Pet():
    def __init__(self, name="pet-none", shop=None):
        """
        Food class definition the types of interactions that food undergoes
        
        """
        if len(name) != 0:
            if not name.startswith("pet-"):
                name = "pet-{}".format(name)
            
        self.eaten = False
        self.shop = shop
            
        self.name = name
        if name not in data["pets"]:
            raise Exception("Pet {} not found".format(name))
        fd = data["pets"][name]
        self.fd = fd
        self.override_ability = False
        self.override_ability_dict = {}
        self.tier = data["pets"][name]["tier"]
        
        ### Overall stats that should be brought into a battle
        self.attack = fd["baseAttack"]
        self.health = fd["baseHealth"]
        self.status = "none"
        
        self.level = 1
        self.experience = 0
        
        if shop != None:
            can = shop.can
            if self.attack != "none":
                self.attack += can
                self.health += can
                
    
    @property
    def ability(self):
        if self.override_ability:
            return self.override_ability_dict
        if "level{}Ability".format(self.level) in self.fd:
            return self.fd["level{}Ability".format(self.level)]
        else:
            return empty_ability
    
    
    def set_ability(self, ability_dict):
        self.override_ability = True
        self.override_ability_dict = ability_dict
        return 

    
    def eat(self, food):
        self.attack += food.attack
        self.health += food.health
        if food.status != "none":
            self.status = food.status
                
                
    def init_fight(self):
        self.fhealth = int(self.health)
        self.fattack = int(self.attack)
        
    
    def combine(self, pet):
        raise Exception("Combine this pet with another pet")
    
    
    def gain_experience(self,amount=1):
        """
        After experience is gained, always need to check if an effect has been
        triggered
        
        """
        self.experience += amount
        level_up = False
        if self.level == 1:
            if self.experience >= 2:
                self.level += 1
                self.experience -= 2
                ### Call recursive incase multiple level-ups occuring
                self.gain_experience(0)
                level_up = True
        elif self.level == 2:
            if self.experience >= 3:
                self.level += 1
                self.experience -= 3
                self.gain_experience(0)
                level_up = True
        elif self.level == 3:
            pass
        else:
            raise Exception("Invalid level found")
        return level_up
        
        
    def __repr__(self):
        return "< {} {}-{} {} >".format(
            self.name, self.attack, self.health, self.status)
        
        
    def copy(self):
        copy_pet = Pet(self.name, self.shop)
        for key,value in self.__dict__.items():
            ### Although this approach will copy the internal dictionaries by 
            ###   reference rather than copy by value, these dictionaries will 
            ###   never be modified anyways. 
            ### All integers and strings are copied by value automatically with
            ###   Python, therefore, this achieves the correct behavior
            copy_pet.__dict__[key] = value
        return copy_pet
        
        
        
        
# %%



empty_ability = {'description': 'none',
 'trigger': 'none',
 'triggeredBy': {'kind': 'none', 'n': 'none'},
 'effect': {'kind': 'none',
  'attackAmount': 'none',
  'healthAmount': 'none',
  'target': {'kind': 'none', 'n': 'none', 'includingFuture': 'none'},
  'untilEndOfBattle': 'none',
  'pet': 'none',
  'withAttack': 'none',
  'withHealth': 'none',
  'team': 'none',
  'amount': 'none',
  'status': 'none',
  'to': {'kind': 'none', 'n': 'none'},
  'copyAttack': 'none',
  'copyHealth': 'none',
  'from': {'kind': 'none', 'n': 'none'},
  'effects': 'none',
  'tier': 'none',
  'baseAttack': 'none',
  'baseHealth': 'none',
  'percentage': 'none',
  'shop': 'none',
  'food': 'none',
  'level': 'none'},
 'maxTriggers': 'none'}