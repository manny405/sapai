
#%%

from pets import Pet

class Team():
    """
    Defines a team class. 
    
    What should be included here that won't be included in just a list of 
    animals? idk...
    
    Maybe including interaction between animals. For example, Tiger. Are there
    any other interactions?
    
    """
    def __init__(self):
        self.max_slots = 5
        self.team = [TeamSlot() for x in range(self.max_slots)]
        
        
    def move(self, sidx, tidx):
        """ Moves animal from start idx to target idx """
        raise Exception()
    
    
    def __len__(self):
        count = 0
        for temp_slot in self.team:
            if temp_slot.pet.name != "pet-none":
                count += 1
        return count
    
    
    def __getitem__(self, idx):
        return self.team[idx]
    
    
    def __setitem__(self, idx, obj):
        if type(obj).__name__ == "Pet":
            self.team[idx] = TeamSlot(obj)
        elif type(obj).__name__ == "TeamSlot":
            self.team[idx] = obj
        else:
            raise Exception("Tried setting a team slot with type {}"
                .format(type(obj).__name__))
    
    
    def __repr__(self):
        repr_str = ""
        for iter_idx,slot in enumerate(self.team):
            repr_str += "{}: {} \n    ".format(iter_idx, slot)
        return repr_str
        
        
class TeamSlot():
    def __init__(self, obj=None):
        if type(obj).__name__ == "Pet":
            self.pet = obj
        elif type(obj).__name__ == "TeamSlot":
            self.pet = obj.pet
        elif type(obj).__name__ == "NoneType":
            self.pet = Pet()
        else:
            raise Exception("Tried initalizing TeamSlot with type {}"
                    .format(type(obj).__name__))
            
        self.attack = self.pet.attack
        self.health = self.pet.health
        self.status = self.pet.status
    
    def __repr__(self):
        if self.pet.name == "pet-none":
            return "< Slot EMPTY >"
        else:
            pet_repr = self.pet.__repr__()
            pet_repr = pet_repr[2:-2]
            return "< Slot {} >".format(pet_repr)
            
# %%
