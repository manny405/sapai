

#%%
from data import data


#%%

class Pet():
    def __init__(self, name="", shop=None):
        """
        Food class definition the types of interactions that food undergoes
        
        """
        if len(name) != 0:
            if not name.startswith("pet-"):
                name = "pet-{}".format(name)
            
        self.eaten = False
        self.shop = shop
        
        ### Overall stats that should be brought into a battle
        self.attack = 0
        self.health = 0
        self.level = 0
        self.status = "none"
        self.ability = {}
        self.fd = {}
        
        ### For keeping track during an actual battle
        self.fhealth = 0
        self.fattack = 0        
            
        if len(name) == 0:
            self.name = "pet-none"
            
        else:
            self.name = name
            if name not in data["pets"]:
                raise Exception("Pet {} not found".format(name))
            fd = data["pets"][name]
            self.fd = fd
            
            self.attack = fd["baseAttack"]
            self.health = fd["baseHealth"]
            self.status = "none"
            if "level1Ability" in fd:
                self.ability = fd["level1Ability"]
            else:
                self.ability = {}
            
            if shop != None:
                can = shop.can
                self.attack += can
                self.health += can
    
    
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
    
        
    def __repr__(self):
        return "< {} {}-{} {} >".format(
            self.name, self.attack, self.health, self.status)
# %%
