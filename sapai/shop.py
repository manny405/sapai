

#%%

from random import seed
import numpy as np
from sapai.data import data
from sapai.foods import Food
from sapai.pets import Pet
import sapai.foods
import sapai.pets

#%%

################################################################################
#### Building optimized datastructures for construction shop states
################################################################################

pet_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
pet_tier_lookup_std = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in data["pets"].items():
    if type(value["tier"]) == int:
        pet_tier_lookup[value["tier"]].append(key)
        if "StandardPack" in value["packs"]:
            pet_tier_lookup_std[value["tier"]].append(key)
pet_tier_avail_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in pet_tier_lookup.items():
    for temp_key,temp_value in pet_tier_avail_lookup.items():
        if temp_key >= key:
            temp_value += value
            
food_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in data["foods"].items():
    if type(value["tier"]) == int:
        food_tier_lookup[value["tier"]].append(key)
food_tier_avail_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6:[]}
for key,value in food_tier_lookup.items():
    for temp_key,temp_value in food_tier_avail_lookup.items():
        if temp_key >= key:
            temp_value += value
            
turn_prob_pets_std = {}
turn_prob_pets_exp = {}
for i in np.arange(0,12):
    turn_prob_pets_std[i] = {}
    turn_prob_pets_exp[i] = {}
for key,value in data["pets"].items():
    if "probabilities" not in value:
        continue
    if data["pets"][key]["probabilities"] == "none":
        continue
    for temp_dict in data["pets"][key]["probabilities"]:
        temp_turn = int(temp_dict["turn"].split("-")[-1])
        if "StandardPack" in temp_dict["perSlot"]:
            temp_std = temp_dict["perSlot"]["StandardPack"]
            turn_prob_pets_std[temp_turn][key] = temp_std
        if "ExpansionPack1" in temp_dict["perSlot"]:
            temp_exp = temp_dict["perSlot"]["ExpansionPack1"]
            turn_prob_pets_exp[temp_turn][key] = temp_exp
        else:
            ### Assumption, if expansion info not provided, use standard info
            temp_exp = temp_std
            turn_prob_pets_exp[temp_turn][key] = temp_exp
        
turn_prob_foods_std = {}
turn_prob_foods_exp = {}
for i in np.arange(0,12):
    turn_prob_foods_std[i] = {}
    turn_prob_foods_exp[i] = {}
for key,value in data["foods"].items():
    if "probabilities" not in value:
        continue
    if data["foods"][key]["probabilities"] == "none":
        continue
    for temp_dict in data["foods"][key]["probabilities"]:
        if temp_dict == "none":
            continue
        temp_turn = int(temp_dict["turn"].split("-")[-1])
        if "StandardPack" in temp_dict["perSlot"]:
            temp_std = temp_dict["perSlot"]["StandardPack"]
            turn_prob_foods_std[temp_turn][key] = temp_std
        if "ExpansionPack1" in temp_dict["perSlot"]:
            temp_exp = temp_dict["perSlot"]["ExpansionPack1"]
            turn_prob_foods_exp[temp_turn][key] = temp_exp
        else:
            ### Assumption, if expansion info not provided, use standard info
            temp_exp = temp_std
            turn_prob_foods_exp[temp_turn][key] = temp_exp

#%%

#%%

class Shop():
    def __init__(self, 
                 shop_slots=[], 
                 turn=1, 
                 can=0,
                 pack="StandardPack",
                 seed_state=None):
        self.rs = np.random.RandomState()
        self.seed_state = seed_state
        if seed_state != None:
            self.rs.set_state(self.seed_state)
        self.turn = turn
        self.pack = pack
        self.tier_avail = 0
        self.leveup_tier = 0
        self.shop_slots = []
        self.pp = []                    ### Probability of pet 
        self.fp = []                    ### Probability of food
        self.fslots = 0
        self.pslots = 0
        self.max_slots = 7
        self.can = can                  ### Keep track of can stats
        
        if pack == "StandardPack":
            self.turn_prob_pets = turn_prob_pets_std
            self.turn_prob_foods = turn_prob_foods_std
        elif pack == "ExpansionPack1":
            self.turn_prob_pets = turn_prob_pets_exp
            self.turn_prob_foods = turn_prob_foods_exp
        else:
            raise Exception("Pack {} not valid".format(pack))
        
        self.update_shop_rules()
        if len(shop_slots) > 0:
            self.shop_slots = [
                ShopSlot(x,pack=self.pack,turn=self.turn,seed_state=self.seed_state) for x in shop_slots]
            
    
    def buy(self, obj):
        """ Only thing that buy does is to remove the item from the shop list """
        if type(obj) == int:
            idx = obj
        else:
            idx = -1
            for iter_idx,slot in enumerate(self.shop_slots):
                if slot.item == obj:
                    idx = iter_idx
                    break
        
        if idx < 0:
            raise Exception("Unrecognized Shop Object {}".format(obj))
        
        del(self.shop_slots[idx])
        
    
    def index(self, obj):
        if type(obj).__name__ == "ShopSlot":
            obj = obj.item
        idx = -1
        for iter_idx,slot in enumerate(self.shop_slots):
            if slot.item == obj:
                idx = iter_idx
                break
        if idx < 0:
            raise Exception("Unrecognized Shop Object {}".format(obj))
        return idx
        
    
    @property
    def pets(self):
        pet_slots = []
        for slot in self.shop_slots:
            if slot.slot_type == "pet":
                pet_slots.append(slot.item)
            elif slot.slot_type == "levelup":
                pet_slots.append(slot.item)
            else:
                pass
        return pet_slots
    
    
    @property
    def foods(self):
        food_slots = []
        for slot in self.shop_slots:
            if slot.slot_type == "food":
                food_slots.append(slot.item)
        return food_slots
    
    
    def roll(self, team=[]):
        """ Randomizes shop and returns list of available entries """
        self.check_rules()
        
        for slot in self.shop_slots:
            # New RandomState per roll or else every slot will roll the same pet/food
            slot.rs = np.random.RandomState()
            slot.rs.set_state(self.seed_state)   
            slot.roll() 
            self.seed_state = slot.seed_state
            ### Add health and attack from previously purchased cans
            if slot.frozen == False:
                if slot.slot_type == "pet":
                    slot.item._attack += self.can
                    slot.item._health += self.can
        
        for team_slot in team:
            team_slot._pet.shop_ability(shop=self,trigger="roll")

    
    def freeze(self, idx):
        """
        Freeze a shop index 
        
        """
        if idx >= len(self.shop_slots):
            ### Just do nothing if attempting to freeze outside the range of 
            ###   the current shop
            return
        self.shop_slots[idx].freeze()
    
    
    def unfreeze(self, idx):
        """
        Unfreeze shop index
        
        """
        if idx > len(self.shop_slots):
            ### Just do nothing if attempting to unfreeze outside the range of 
            ###   the current shop
            return
        self.shop_slots[idx].unfreeze()
        
    
    def levelup(self):
        """ 
        Called when a pet is leveled-up by the player to update the shop state
        with a new pet
        
        """
        new_slot = ShopSlot("levelup",pack=self.pack,turn=self.turn)
        self.append(new_slot)
        
    
    def update_shop_rules(self, turn=-1):
        if turn < 0:
            turn = self.turn
        
        ### Turn 11 is max shopd info
        if turn > 11:
            turn = 11
            
        rules = get_shop_rules(turn)
        self.pslots = rules[0]
        self.fslots = rules[1]
        self.tier_avail = rules[2]
        self.levelup_tier = rules[3]
        self.avail_pets = rules[4]
        self.avail_foods = rules[5]
        self.pp = rules[6]
        self.fp = rules[7]
        
        ### Setup the shop slots
        new_shop_slots_pet = []
        new_shop_slots_food = []
        for slot in self.shop_slots:
            if slot.slot_type == "pet":
                new_shop_slots_pet.append(slot)
            elif slot.slot_type == "food":
                new_shop_slots_food.append(slot)
            else:
                raise Exception()
            
        add_pets = self.pslots - len(new_shop_slots_pet)
        for i in range(add_pets):
            new_shop_slots_pet.append(
                ShopSlot("pet",pack=self.pack,turn=self.turn, seed_state=self.seed_state))
        
        add_foods = self.fslots - len(new_shop_slots_food)
        for i in range(add_foods):
            new_shop_slots_food.append(
                ShopSlot("food",pack=self.pack,turn=self.turn, seed_state=self.seed_state))
        
        self.shop_slots = new_shop_slots_pet+new_shop_slots_food
        
        ### Roll all slots upon update of rules
        self.roll()
    
    
    def next_turn(self):
        ### Update turn counter
        self.turn += 1
        
        ### Update rules of the shop to generate a shop state
        self.update_shop_rules()
        
        return self.roll()
    
    
    def check_rules(self):
        """
        Used to ensure that rules of the current shop are satisfied before
        beforming a roll. This is because slots may be added when an animal 
        on the team levels-up.
        """
        keep_idx = []
        pslots = []
        fslots = []
        
        ### Look for frozen slots first
        for iter_idx,slot in enumerate(self.shop_slots):
            if slot.frozen == True:
                keep_idx.append(iter_idx)
                if slot.slot_type == "pet":
                    pslots.append(iter_idx)
                elif slot.slot_type == "levelup":
                    pslots.append(iter_idx)
                elif slot.slot_type == "food":
                    fslots.append(iter_idx)
        
        ### Then add other slots only if it has not yet exceeded the rules
        for iter_idx,slot in enumerate(self.shop_slots):
            if slot.frozen == True:
                ### Skip frozen slots because they have already been added
                continue
            if slot.slot_type == "pet":
                if len(pslots) < self.pslots:
                    keep_idx.append(iter_idx)
                    pslots.append(iter_idx)
            if slot.slot_type == "food":
                if len(fslots) < self.fslots:
                    keep_idx.append(iter_idx)
                    fslots.append(iter_idx)

        if len(pslots) < self.pslots:
            add_slots = min(self.pslots - len(pslots), 
                            self.max_slots - len(keep_idx))
            for idx in range(add_slots):
                self.shop_slots.append(
                    ShopSlot("pet", turn=self.turn, pack=self.pack, seed_state=self.seed_state))
                keep_idx.append(len(self.shop_slots)-1)
        if len(fslots) < self.fslots:
            add_slots = min(self.fslots - len(fslots), 
                            self.max_slots - len(keep_idx))
            for idx in range(add_slots):
                self.shop_slots.append(
                    ShopSlot("food", turn=self.turn, pack=self.pack, seed_state=self.seed_state))
                keep_idx.append(len(self.shop_slots)-1)
        
        keep_slots = [self.shop_slots[x] for x in keep_idx]
        self.shop_slots = keep_slots
        
        ### Order shop slots
        keep_idx = []
        pslots = []
        fslots = []
        for iter_idx,slot in enumerate(self.shop_slots):
            if slot.slot_type == "pet":
                pslots.append(iter_idx)
            elif slot.slot_type == "leveup":
                pslots.append(iter_idx)
        for iter_idx,slot in enumerate(self.shop_slots):
            if slot.slot_type == "food":
                fslots.append(iter_idx)
        keep_idx = pslots+fslots
        keep_slots = [self.shop_slots[x] for x in keep_idx]
        self.shop_slots = keep_slots
        

    def __len__(self):
        return len(self.shop_slots)
    
    
    def __getitem__(self, idx):
        return self.shop_slots[idx]
    
    
    def __setitem__(self, idx, obj):
        """
        __setitem__ should never be used
        
        """
        raise Exception("Cannot set item in shop directly")

    
    def append(self, obj):
        """
        Append should be used when adding an animal from a levelup
        """
        if len(self.shop_slots) >= self.max_slots:
            ### Max slots already reached so cannot be added
            return
        
        add_slot = ShopSlot(obj, pack=self.pack, turn=self.turn, seed_state=self.seed_state)
        pslots = []
        fslots = []
        for iter_idx,slot in enumerate(self.shop_slots):
            if slot.slot_type == "pet":
                pslots.append(slot)
            if slot.slot_type == "food":
                fslots.append(slot)
        
        new_slots = []
        new_slots += [x for x in pslots]
        new_slots += [add_slot]
        new_slots += [x for x in fslots]
        
        self.shop_slots = new_slots
        
        
    @property
    def state(self):
        state_dict = {
            "type": "Shop",
            "shop_slots": [x.state for x in self.shop_slots],
            "turn": self.turn,
            "can": self.can,
            "pack": self.pack,
            "seed_state": self.seed_state,
        }
        return state_dict
    
    
    @classmethod
    def from_state(cls, state):
        return cls(
            shop_slots=[ShopSlot.from_state(x) for x in state["shop_slots"]],
            turn=state["turn"],
            can=state["can"],
            pack=state["pack"],
            seed_state = state["seed_state"])
    
    
    def __repr__(self):
        repr_str = ""
        for iter_idx,slot in enumerate(self.shop_slots):
            repr_str += "{}: {} \n    ".format(iter_idx, slot)
        return repr_str


class ShopLearn(Shop):
    """
    Shop behavior designed for learning algorithms. In this shop, all Pets and 
    Foods are presented for a given tier. In this way, the all possible can 
    be considered and becaues the API is considered with a regular shop, the
    agent can automatically be executed with normal random shop behavior. 
    Only disadvantage is that rolling behavior can not be learned by this method
    until transitioning to normal random shop behavior.
    
    Rolling behavior is emulated. For example, on the first round, if 3 pets
    are bought, then all pets in the shop are removed requiring that a roll
    takes place before another pet can be bought. Without this requirement,
    teams that could never be built in the real game are possible by buying 
    and selling more than 3 pets without rolling a single time. 
    
    """
    def __init__(self,*args,**kwargs):
        self.npet_bought = 0
        self.nfood_bought = 0
        self.nmax_levelup = 0
        self.nlevelup_bought = 0
        self.shop_names = {}
        super().__init__(*args,**kwargs)
        self.max_slots = int(1e6)
    
    
    def roll(self):
        ### Reset npet_bought and nfood_bough upon rolling
        self.npet_bought = 0
        self.nfood_bought = 0
        self.nlevelup_bought = 0
        
        ### Return the number of pets that can be bought from the next tier
        ###   to zero
        self.nmax_levelup = 0
        
        ### Rebuild ShopLearn
        self.update_shop_rules()


    def buy(self, obj):
        """ 
        Buy has slightly different behavior than normal. After buying a pet, 
        it is never removed. However, all levelup slots are removed. What this
        does is that Pets from a higher tier that is available from a combining
        to levelup can only be considered or bought a single time. This provides
        very good emulation of realistic game behavior during the shopping 
        phase. 
        
        """
        ### Desired object is ShopSlot in this case
        if type(obj).__name__ == "ShopSlot":
            pass
        elif type(obj) == int:
            obj = self.shop_slots[obj]
        else:
            idx = -1
            for iter_idx,slot in enumerate(self.shop_slots):
                if slot.item == obj:
                    idx = iter_idx
                    obj = slot
                    break
            if idx < 0:
                raise Exception("Unrecognized Shop Object {}".format(obj))
        
        if obj.slot_type == "pet":
            self.npet_bought += 1
        elif obj.slot_type == "food":
            self.nfood_bought += 1
        elif obj.slot_type == "levelup":
            self.nlevelup_bought += 1
        else:
            raise Exception("Unrecognized ShopSlot {}".format(obj))
            
        ### Rebuild ShopLearn to remove all levelup ShopSlots
        self.update_shop_rules()
            
        
    
    def update_shop_rules(self, turn=-1):
        """
        Rebuilds ShopLearn using all Pets and Foods available for the givne turn
        
        """
        if turn < 0:
            turn = self.turn
        
        ### Turn 11 is max shopd info
        if turn > 11:
            turn = 11
            
        rules = get_shop_rules(turn)
        self.pslots = rules[0]
        self.fslots = rules[1]
        self.tier_avail = rules[2]
        self.levelup_tier = rules[3]
        self.avail_pets = rules[4]
        self.avail_foods = rules[5]
        self.pp = len(self.avail_pets)
        self.fp = len(self.avail_foods)
        
        ### Setup the shop slots
        self.shop_names = {}
        self.shop_slots = []
        new_shop_slots_pet = []
        new_shop_slots_food = []
        new_shop_slots_levelup = []
        
        ### Check if Pet purchase limit or Food purchase limit has been reached
        if self.npet_bought < self.pslots:
            for pet in self.avail_pets:
                new_shop_slots_pet.append(
                    ShopSlot(pet,pack=self.pack,turn=self.turn, seed_state=self.seed_state))
                self.shop_names[pet] = True
        if self.nfood_bought < self.fslots:
            for food in self.avail_foods:
                new_shop_slots_food.append(
                    ShopSlot(food,pack=self.pack,turn=self.turn, seed_state=self.seed_state))
                self.shop_names[food] = True
        if self.nlevelup_bought < self.nmax_levelup:
            if self.pack == "StandardPack":
                levelup_avail_pets = pet_tier_lookup_std[self.levelup_tier]
            else:
                levelup_avail_pets = pet_tier_lookup[self.levelup_tier]
            for pet in levelup_avail_pets:
                if pet not in self.shop_names:
                    temp_slot = ShopSlot(slot_type="levelup",
                                        pack=self.pack,
                                        turn=self.turn, seed_state=self.seed_state)
                    temp_slot.item = Pet(pet,seed_state=self.seed_state)
                    new_shop_slots_levelup.append(temp_slot)
                    self.shop_names[pet] = True
        
        self.shop_slots = new_shop_slots_pet+\
                          new_shop_slots_levelup+\
                          new_shop_slots_food
            
        
    def levelup(self):
        ### Add 1 to the number of levelup pets that can be bought
        self.nmax_levelup += 1
        ### Rebuild shop
        self.update_shop_rules()
                
    
    def check_rules(self):
        raise Exception("ShopLearn does not use check_rules")
    
    
    @property
    def state(self):
        state_dict = {
            "type": "ShopLearn",
            "shop_slots": [x.state for x in self.shop_slots],
            "turn": self.turn,
            "can": self.can,
            "pack": self.pack,
            "seed_state":self.seed_state
        }
        return state_dict
    
    
    @classmethod
    def from_state(cls, state):
        return cls(
            shop_slots=[ShopSlot.from_state(x) for x in state["shop_slots"]],
            turn=state["turn"],
            can=state["can"],
            pack=state["pack"],
            seed_state = state["seed_state"])
                


class ShopSlot():
    """
    Class for a slot in the shop
    
    """
    def __init__(self, 
                 obj=None, 
                 slot_type="pet", 
                 frozen=False,
                 turn=1, 
                 cost=3,
                 pack="StandardPack",
                 seed_state=None):
        self.seed_state = seed_state
        self.rs = np.random.RandomState()
        if seed_state != None:
            self.rs.set_state(self.seed_state)
       
        self.slot_type = slot_type
        self.turn = turn
        self.pack = pack
        self.frozen = frozen
        self.cost = cost
        
        if slot_type not in ["pet", "food", "levelup"]:
            raise Exception("Unrecognized slot type {}".format(self.slot_type))
        
        if obj != None and type(obj) != str:
            if type(obj).__name__ == "Pet":
                self.slot_type = "pet"
                self.item = obj
            elif type(obj).__name__ == "Food":
                self.slot_type = "food"
                self.item = obj
            elif type(obj).__name__ == "ShopSlot":
                self.slot_type = obj.slot_type
                self.turn = obj.turn
                self.pack = obj.pack
                self.frozen = obj.frozen
                self.cost = obj.cost
                self.item = obj.item.copy()
        else:
            if type(obj) == str:
                if obj not in ["pet", "food", "levelup"]:
                    if obj in data["pets"]:
                        name = obj
                        self.slot_type = "pet"  
                    elif obj in data["foods"]       :
                        name = obj
                        self.slot_type = "food"
                    elif "pet-{}".format(obj) in data["pets"]:
                        name = obj
                        self.slot_type = "pet"
                    elif "food-{}".format(obj) in data["foods"]:
                        name = obj
                        self.slot_type = "food"
                    else:
                        raise Exception("Unrecognized ShopSlot Object {}"
                                        .format(obj))
                else:
                    self.slot_type = obj
                    name = "none"
                
            if self.slot_type == "pet":
                self.item = Pet(name,seed_state=self.seed_state)
            elif self.slot_type == "food":
                self.item = Food(name,seed_state=self.seed_state)
            elif self.slot_type == "levelup":
                self.roll_levelup()
            
    
    def __repr__(self):
        if self.frozen:
            fstr = "frozen"
        else:
            fstr = "not-frozen"
        if self.slot_type == "pet":
            if self.item.name == "pet-none":
                return "< ShopSlot-{} {} EMPTY >".format(
                    self.slot_type, fstr)
            else:
                pet_repr = str(self.item)
                pet_repr = pet_repr[2:-2]
                return "< ShopSlot-{} {} {}-gold {} >".format(
                    self.slot_type, fstr, self.cost, pet_repr)
        else:
            if self.item.name == "food-none":
                return "< ShopSlot-{} {} EMPTY >".format(
                    self.slot_type, fstr)
            else:
                food_repr = str(self.item)
                food_repr = food_repr[2:-2]
                return "< ShopSlot-{} {} {}-gold {} >".format(
                    self.slot_type, fstr, self.cost, food_repr)
    
    def freeze(self):
        """
        Freeze current slot such that shop rolls don't update the ShopSlot
        """
        self.frozen = True
    
    
    def unfreeze(self):
        self.frozen = False
    
    
    def roll(self, avail=[], prob=[]):
        if self.frozen:
            return
        if self.slot_type == "levelup":
            ### If roll is called on a levelup slot, then it should change to 
            ###   a typical pet slot type. Deletion of levelup slots is handled
            ###   by the Shop.check_rules method when appropriate. 
            self.slot_type = "pet"
        
        if len(avail) == 0:
            rules = get_shop_rules(self.turn, pack=self.pack)
            if self.slot_type == "pet":
                avail = rules[4]
                prob = rules[6]
            elif self.slot_type == "food":
                avail = rules[5]
                prob = rules[7]
            else:
                raise Exception()
            
        choice = self.rs.choice(avail, 
                                    size=(1,),
                                    replace=True, 
                                    p=prob)[0]
        self.seed_state = self.rs.get_state()
        if self.slot_type == "pet":
            self.item = Pet(choice, seed_state=self.seed_state)
        elif self.slot_type == "food":
            self.item = Food(choice, seed_state=self.seed_state)
            if self.item.name == "food-sleeping-pill":
                ### Hard-coded for pill because of limitations of data json
                self.cost = 1
        else:
            raise Exception()
        
        
    
    def roll_levelup(self):
        rules = get_shop_rules(self.turn, pack=self.pack)
        levelup_tier = rules[3]
        if self.pack == "StandardPack":
            avail_pets = pet_tier_lookup_std[levelup_tier]
        else:
            avail_pets = pet_tier_lookup[levelup_tier]
        pet_choice = self.rs.choice(avail_pets, 
                                        size=(1,),
                                        replace=True)[0]
        self.seed_state = self.rs.get_state()
        self.item = Pet(pet_choice,seed_state=self.seed_state)
        
        
    @property
    def state(self):
        state_dict = {
            "type": "ShopSlot",
            "slot_type": self.slot_type,
            "item": self.item.state,
            "turn": self.turn,
            "pack": self.pack,
            "cost": self.cost, 
            "frozen": self.frozen,
            "seed_state": self.seed_state
        }
        return state_dict
    
    
    @classmethod
    def from_state(cls, state):
        slot_type = state["slot_type"]
        obj_state = state["item"]
        if state["item"]["type"] == "Pet":
            item_cls = getattr(sapai.pets, "Pet")
        elif state["item"]["type"] == "Food":
            item_cls = getattr(sapai.foods, "Food")
        else:
            raise Exception("Unrecognized item state")
        obj = item_cls.from_state(state["item"])
        turn = state["turn"]
        pack = state["pack"]
        cost = state["cost"]
        frozen = state["frozen"]
        seed_state = state["seed_state"]
        obj.rs = np.random.RandomState()
        if seed_state != None:
            obj.rs.set_state(state["item"]["seed_state"])
        return cls(obj=obj, 
                   slot_type=slot_type,
                   frozen=frozen,
                   turn=turn,
                   cost=cost,
                   pack=pack,
                   seed_state=seed_state)
        

def get_shop_rules(turn, pack="StandardPack"):
    if pack == "StandardPack":
        turn_prob_pets = turn_prob_pets_std
        turn_prob_foods = turn_prob_foods_std
    elif pack == "ExpansionPack1":
        turn_prob_pets = turn_prob_pets_exp
        turn_prob_foods = turn_prob_foods_exp
    else:
        raise Exception("Pack {} not valid".format(pack))
    
    if turn <= 0:
        raise Exception("Input turn must be greater than 0")
    
    ### Turn 11 is max shop info
    if turn > 11:
        turn = 11
        
    td = data["turns"]["turn-{}".format(turn)]
    fslots = td["foodShopSlots"]
    pslots = td["animalShopSlots"]
    tier_avail = td["tiersAvailable"]
    levelup_tier = td["levelUpTier"]
    temp_avail_pets = pet_tier_avail_lookup[tier_avail]
    temp_avail_foods = food_tier_avail_lookup[tier_avail]
    
    temp_prob_pets = turn_prob_pets[turn]
    pp = []
    avail_pets = []
    for temp_pet in temp_avail_pets:
        if temp_pet not in temp_prob_pets:
            continue
        pp.append(temp_prob_pets[temp_pet])
        avail_pets.append(temp_pet)
    
    temp_prob_foods = turn_prob_foods[turn]
    fp = []
    avail_foods = []
    for temp_food in temp_avail_foods:
        if temp_food not in temp_prob_foods:
            continue
        fp.append(temp_prob_foods[temp_food])
        avail_foods.append(temp_food)
        
    ### Ensure that the probabilities sum to 1...
    pp = np.array(pp) 
    pp = pp / np.sum(pp)
    
    fp = np.array(fp) 
    fp = fp / np.sum(fp)
    
    return pslots,fslots,tier_avail,levelup_tier,avail_pets,avail_foods,pp,fp


# %%
