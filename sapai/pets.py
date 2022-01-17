

#%%

from sapai.data import data
from sapai.effects import get_effect_function
from sapai.tiers import pet_tier_lookup,pet_tier_lookup_std

#%%

class Pet():
    def __init__(self, name="pet-none", shop=None, team=None, player=None):
        """
        Food class definition the types of interactions that food undergoes
        
        """
        if len(name) != 0:
            if not name.startswith("pet-"):
                name = "pet-{}".format(name)
            
        self.eaten = False
        self.shop = shop
        self.team = team
        self.player = player
        
        ### Used only for goat
        self.ability_counter = 0
            
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
        if "status" in self.fd:
            self.status = self.fd["status"]
        
        self.level = 1
        self.experience = 0
        
        #### Add pet to team if not already present
        if self.team != None:
            if self.attack != "none":
                if self not in team:
                    team.append(self)

            if self.team.shop == None:
                if self.shop != None:
                    self.team.shop = self.shop
                
    
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
    
    
    def sot_trigger(self, trigger=None):
        """
        Apply pet's start of turn ability
        
        Pets: 
            ["dromedary", "swan", "caterpillar", "squirrel"]
        """
        ### Reset ability_counter for goat at sot_trigger
        self.ability_counter = 0
        
        activated = False
        if self.ability["trigger"] != "StartOfTurn":
            return activated
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team])
        
        activated = True 
        return activated
    
    
    def cat_trigger(self, trigger=None):
        """
        Apply pet's shop ability to the given shop when shop is rolled
        
        Pets: 
            ["cat"]
        """
        activated = False
        ### Hard coded because for some reason the cat trigger is hurt but it 
        ###   should be roll
        if self.name not in ["pet-cat"]:
            return activated
        
        if type(trigger).__name__ != "Food":
            raise Exception("Must input purchased food as trigger for cat")

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True 
        return activated
    
    
    def sell_trigger(self, trigger=None):
        """
        Apply pet's sell ability when a friend (or self) is self
        
        Pets: 
            ["beaver", "duck", "pig", "shrimp", "owl"]
        """
        activated = False
        if self.ability["trigger"] != "Sell":
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Sell must be triggered by a Pet")
        
        ### Check if self has been sold is important
        if self.ability["triggeredBy"]["kind"] == "Self":
            if trigger != self:
                return activated
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team])
        
        activated = True 
        return activated
    
    
    
    def buy_food_trigger(self, trigger=None):
        """
        Apply pet's ability when food is bought
        
        Pets: 
            ["beetle", "ladybug", "tabby-cat", "rabbit", "worm", "seal", 
             "sauropod"]
        
        """
        activated = False
        if self.ability["trigger"] not in ["EatsShopFood", "BuyFood"]:
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Buy food must input food target as triggered")
        
        ### Check if food has been bought for self is important
        if self.ability["trigger"] == "EatsShopFood":
            if trigger != self:
                return activated

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True 
        return activated
    
    
    def buy_friend_trigger(self, trigger=None):
        """
        Apply pet's ability when a friend (or self) is bought
        
        Pets: 
            ["otter", "crab", "snail", "buffalo", "chicken", "cow", 
             "goat", "dragon", ]
        """
        activated = False
        if self.ability["trigger"] not in ["Buy", "BuyAfterLoss", "BuyTier1Animal"]:
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Buy food must input food target as triggered")
        
        ### Behavior for bought self and friend
        if self.ability["trigger"] == "Buy":
            if self.ability["triggeredBy"]["kind"] == "Self":
                if trigger != self:
                    return activated
            elif self.ability["triggeredBy"]["kind"] == "Player":
                ### Behavior for kind=self and kind=player is actually the 
                ###   same and any distinction is unnecessary
                if trigger != self:
                    return activated
            elif self.ability["triggeredBy"]["kind"] == "EachFriend":
                ### If trigger is EachFriend, then the trigger cannot actually
                ###   be self
                if trigger == self:
                    return activated
            else:
                raise Exception("Ability unrecognized for {}".format(self))
        
        ### Behavior for BuyTier1Animal
        if self.ability["trigger"] == "BuyTier1Animal":
            if trigger.name not in pet_tier_lookup[1]:
                return activated
        
        ### Behavior for BuyAfterLoss
        if self.ability["trigger"] == "BuyAfterLoss":
            if self.player == None:
                return activated
            if self.player.lf_winner != False:
                return activated
            
        ### Specific check for goat
        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated
            else:
                self.ability_counter += 1
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True 
        return activated
    
    
    def friend_summoned_trigger(self, trigger=None):
        """
        Apply pet's ability when a friend (or self) is summoned
        
        Pets: 
            ["horse", "dog", "lobster", "turkey"]
        """
        activated = False
        if self.ability["trigger"] != "Summoned":
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True
        return activated
        
    
    
    def levelup_trigger(self, trigger=None):
        """
        Apply pet's ability when a friend (or self) level-up

        Pets: 
            ["fish", "octopus"]
        """
        activated = False
        if self.ability["trigger"] != "LevelUp":
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True
        return activated
        
    
    def eot_trigger(self, trigger=None):
        """
        Apply pet's end-of-turn ability
        
        Pets: 
            ["bluebird", "hatching-chick", "giraffe", "puppy", "tropical-fish", 
             "bison", "llama", "penguin", "parrot", "monkey", "poodle", 
             "tyrannosaurus"]
        """
        activated = False
        if not self.ability["trigger"].startswith("EndOfTurn"):
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")
        
        ### Check gold for puppy and tyrannosaurus
        if self.ability["trigger"] == "EndOfTurnWith3PlusGold":
            if self.player != None:
                if self.player.gold >= 3:
                    pass
                else:
                    return activated
            else:
                return activated
        ### Check for bison
        elif self.ability["trigger"] == "EndOfTurnWithLvl3Friend":
            if self.team != None:
                if not self.team.check_lvl3():
                    return activated
            else:
                return activated
        ### Check for llama
        elif self.ability["trigger"] == "EndOfTurnWith4OrLessAnimals":
            if self.team != None:
                if len(self.team) > 4:
                    return activated
            else:
                return activated
        else:
            if self.ability["trigger"] != "EndOfTurn":
                raise Exception("Unrecognized trigger {}"
                                .format(self.ability["trigger"]))
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True
        return activated
    
    
    def faint_trigger(self, trigger=None):
        """
        Apply pet's ability associated with a friend (or self) fainting
        
        Pets:
            ["ant", "cricket", "flamingo", "hedgehog", "spider", "badger", 
             "ox", "sheep", "turtle", "deer", "rooster", "microbe", 
             "eagle", "shark", "fly", "mammoth"]
        """
        activated = False
        if self.ability["trigger"] != "Faint":
            return activated
        
        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")

        if self.ability["triggeredBy"]["kind"] == "Self":
            if trigger != self:
                return activated
        elif self.ability["triggeredBy"]["kind"] == "FriendAhead":
            pet_ahead = self.team.get_friendahead(self, n=1)[0]
            if trigger != pet_ahead:
                return activated
        elif self.ability["triggeredBy"]["kind"] == "EachFriend":
            if trigger == self:
                ### Only time this doesn't activate is if it self triggered
                return activated
        else:
            pass
        
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        func([0,pet_idx], [self.team], te=trigger)
        
        activated = True
        return activated
    
        
    def __repr__(self):
        return "< {} {}-{} {} {}-{} >".format(
            self.name, 
            self.attack, self.health, 
            self.status, 
            self.level, self.experience)
        
        
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
    
    @property
    def state(self):
        #### Cannot get state for attached objects such as shop, team, or player
        ####   as this will lead to circular logic. Therefore, state should be
        ####   saved at the Player level if all info is desired. 
        state_dict = {
            "type": "Pet",
            "name": self.name,
            "eaten": False,
            "shop": {},
            "team": {},
            "player": {},
            "ability_counter": self.ability_counter,
            "override_ability": self.override_ability,
            "override_ability_dict": self.override_ability_dict,
            "attack": self.attack,
            "health": self.health,
            "status": self.status,
            "level": self.level,
            "experience": self.experience
        }
        
        return state_dict
        
    
    @classmethod
    def from_state(cls, state):
        name = state["name"]
        
        ### Initialize and reset defaults by hand
        pet = cls(name)
        pet.store = None
        pet.team = None
        pet.player = None

        ### Set internal from state 
        pet.ability_counter = state["ability_counter"]
        pet.override_ability = state["override_ability"]
        pet.override_ability_dict = state["override_ability_dict"]
        pet.attack = state["attack"]
        pet.health = state["health"]
        pet.status = state["status"]
        pet.level = state["level"]
        pet.experience = state["experience"]
        
        return pet
        
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