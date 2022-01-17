

#%%
from sapai.data import data


#%%

class Food():
    def __init__(self, name="food-none", shop=None, team=[]):
        """
        Food class definition the types of interactions that food undergoes
        
        """
        if len(name) != 0:
            if not name.startswith("food-"):
                name = "food-{}".format(name)
            
        self.eaten = False
        self.shop = shop
        self.owned_pets = []
        
        self.attack = 0
        self.health = 0
        self.base_attack = 0
        self.base_health = 0
        self.status = "none"
        self.effect = "none"
        self.fd = {}
            
        self.name = name
        if name not in data["foods"]:
            raise Exception("Food {} not found".format(name))
        fd = data["foods"][name]["ability"]
        self.fd = fd
        
        self.attack = 0
        self.health = 0
        self.effect = fd["effect"]["kind"]
        if "attackAmount" in fd["effect"]:
            self.attack = fd["effect"]["attackAmount"]
            self.base_attack = fd["effect"]["attackAmount"]
        if "healthAmount" in fd["effect"]:
            self.health = fd["effect"]["healthAmount"]
            self.base_health = fd["effect"]["healthAmount"]
        if "status" in fd["effect"]:
            self.status = fd["effect"]["status"]
                
        for temp_pet in self.owned_pets:
            raise Exception("ADD IN PET MODIFICATIONS TO FOOD")
    
    
    def apply(self, pet=None):
        """
        Serve the food object to the input pet 
        """
        if self.eaten == True:
            raise Exception("This should not be possible")
        
        if self.name == "food-canned-food":
            self.shop.can += self.attack
            return
            
        pet.attack += self.attack
        pet.health += self.health

        if self.effect == "ModifyStats":
            ### Done
            return pet
        elif self.effect == "ApplyStatus":
            pet.status = self.status
            
    
    def copy(self):
        copy_food = Food(self.name, self.shop)
        for key,value in self.__dict__.items():
            ### Although this approach will copy the internal dictionaries by 
            ###   reference rather than copy by value, these dictionaries will 
            ###   never be modified anyways. 
            ### All integers and strings are copied by value automatically with
            ###   Python, therefore, this achieves the correct behavior
            copy_food.__dict__[key] = value
        return copy_food
    
        
    def __repr__(self):
        return "< {} {}-{} {} >".format(
            self.name, self.attack, self.health, self.status)

        
# %%
