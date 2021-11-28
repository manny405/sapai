
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
    def __init__(self, obj_list=[], fight=False, store=None, player=None, 
                 pack="StandardPack"):
        self._fight = fight
        self.max_slots = 5
        self.team = [TeamSlot() for x in range(self.max_slots)]
        for iter_idx,obj in enumerate(obj_list):
            self[iter_idx] = obj
        self.player = player
        self.store = store
        self.pack = "StandardPack"
    
    
    def move(self, sidx, tidx):
        """ Moves animal from start idx to target idx """
        target = self[tidx]
        if not target.empty:
            raise Exception("Attempted move to a populated position")
        ### Move
        self[tidx] = self[sidx]
        ### Dereference original position
        self[sidx] = TeamSlot()
            
    
    def move_forward(self, start_idx=0, end_idx=10):
        """
        Adjust the location of the pets in the team, moving them to the furthest 
        possible forward location using a recursive function. The arg idx may
        be provided to indicate the first index that is allowed to move 
        forward. 
        
        """
        empty_idx = []
        filled_idx = []
        for iter_idx,slot in enumerate(self):
            if slot.empty:
                empty_idx.append(iter_idx)
            else:
                filled_idx.append(iter_idx)
        if len(empty_idx) > 0:
            ### Only need to consider the first emtpy position 
            empty_idx = empty_idx[0]
            
            ### Find first pet that can fill this emtpy position
            found = False
            for temp_idx in filled_idx:
                if temp_idx < start_idx:
                    continue
                if temp_idx >= end_idx:
                    continue
                if empty_idx < temp_idx:
                    found = True
                    ### Move pet
                    self.move(temp_idx,empty_idx)
                    break
            
            ### If a pet was moved, call recurisvely
            if found:
                self.move_forward(start_idx,end_idx)
        
        return
    
    
    def move_backward(self):
        """
        Adjust the location of the pets in the team, moving them to the furthest 
        possible backward location using a recursive function. 

        This is useful for summoning purposes
        
        """
        empty_idx = []
        filled_idx = []
        for iter_idx,slot in enumerate(self):
            if slot.empty:
                empty_idx.append(iter_idx)
            else:
                filled_idx.append(iter_idx)
        if len(empty_idx) > 0:
            ### Only need to consider the last empty position 
            empty_idx = empty_idx[-1]
            
            ### Find first pet that can fill this empty position
            found = False
            for start_idx in filled_idx[::-1]:
                if empty_idx > start_idx:
                    found = True
                    ### Move pet
                    self.move(start_idx,empty_idx)
                    break
            
            ### If a pet was moved, call recurisvely
            if found:
                self.move_backward()
        
        return
    
    
    def remove(self, obj):
        if type(obj) == int:
            self.team[obj] = TeamSlot()
        elif type(obj).__name__ == "TeamSlot":
            found = False
            for iter_idx,temp_slot in enumerate(self.team):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("Remove {} not found".format(obj))
            self.team[found_idx] = TeamSlot()
        elif type(obj).__name__ == "Pet":
            found = False
            for iter_idx,temp_slot in enumerate(self.team):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("Remove {} not found".format(obj))
            self.team[found_idx] = TeamSlot()
        else:
            raise Exception("Object of type {} not recognized".format(type(obj)))
        
    
    def get_idx(self, obj):
        if type(obj).__name__ == "TeamSlot":
            found = False
            for iter_idx,temp_slot in enumerate(self.team):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("Remove {} not found".format(obj))
            return found_idx
        elif type(obj).__name__ == "Pet":
            found = False
            for iter_idx,temp_slot in enumerate(self.team):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("Remove {} not found".format(obj))
            return found_idx
        else:
            raise Exception("Object of type {} not recognized".format(type(obj)))
    
    def remove_fainted(self):
        if not self.fight:
            raise Exception("Cannot use method remove_fainted outside of a fight")
        
    
    @property
    def fight(self):
        return self._fight
    
    
    def __len__(self):
        count = 0
        for temp_slot in self.team:
            if not temp_slot.emtpy:
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
    
    
    def copy(self):
        return Team([x.copy() for x in self], self.fight, self.player)
    
        
class TeamSlot():
    def __init__(self, obj=None):
        if type(obj).__name__ == "Pet":
            self._pet = obj
        elif type(obj).__name__ == "TeamSlot":
            self._pet = obj.pet
        elif type(obj).__name__ == "NoneType":
            self._pet = Pet()
        else:
            raise Exception("Tried initalizing TeamSlot with type {}"
                    .format(type(obj).__name__))
        
    @property
    def pet(self):
        return self._pet
    
    @property
    def empty(self):
        return self._pet.name == "pet-none"

    @property
    def attack(self):
        return self._pet.attack
    
    @property
    def health(self):
        return self._pet.health
    
    
    def __repr__(self):
        if self._pet.name == "pet-none":
            return "< Slot EMPTY >"
        else:
            pet_repr = str(self._pet)
            pet_repr = pet_repr[2:-2]
            return "< Slot {} >".format(pet_repr)

    
    def copy(self):
        return TeamSlot(self._pet.copy())
            
            
# %%
