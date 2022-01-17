
import numpy as np

from sapai.shop import Shop
from sapai.teams import Team,TeamSlot


class Player():
    """
    Defines and implements all of the actions that a player can take. In particular
    each of these actions is directly tied to the actions reinforment learning 
    models can take. 
    
    Actions with the shop are based off of Objects and not based off of indices. 
    There is a huge advantage to doing things this way. The index that a Pet/Food 
    is in a shop is arbitrary. Therefore, when actions are based off the Object,
    The ML Agent will not have to learn the index invariances of the shop.
    
    The Player class is allowed to make appropriate changes to the Shop and 
    Team. Therefore, Shops and Teams input into the Player class will not be
    static. The Player class is also responsible for checking all of the 
    relevant Pet triggers when taking any action. 
    
    """
    def __init__(self, 
                 shop=None, 
                 team=None, 
                 lives=10, 
                 default_gold=10,
                 gold=10, 
                 turn=1,
                 lf_winner=None,
                 pack="StandardPack"):
        self.shop = shop
        self.team = team
        self.lives = lives
        self.default_gold = default_gold
        self.gold = gold
        self.pack = pack
        self.turn = turn
        
        ### Default Parameters
        self._max_team = 5
        
        ### Keep track of outcome of last fight for snail
        self.lf_winner = lf_winner
        
        ### Initialize shop and team if not provided
        if self.shop == None:
            self.shop = Shop(pack=self.pack)
        if self.team == None:
            self.team = Team()
        
        if type(self.shop) == list:
            self.shop = Shop(self.shop)
        if type(self.team) == list:
            self.team = Team(self.team)
            
        ### Connect objects
        self.team.player = self
        for slot in self.team:
            slot._pet.player = self
            slot._pet.shop = self.shop
            
    
    def start_turn(self, winner=None):
        ### Update turn count and gold
        self.turn += 1
        self.gold = self.default_gold
        self.lf_winner = winner
        
        ### Roll shop
        self.shop.turn += 1
        self.shop.roll()

        ### Activate start-of-turn triggers after rolling shop
        for slot in self.team:
            slot._pet.sot_trigger()
            
        return
    
    
    def buy_pet(self, pet):
        """ Buy one pet from the shop """
        if len(self.team) == self._max_team:
            raise Exception("Attempted to buy Pet on full team")
        
        if type(pet).__name__ == "ShopSlot":
            pet = pet.item
        
        if type(pet).__name__ != "Pet":
            raise Exception("Attempted to buy_pet using object {}".format(pet))
        
        shop_idx = self.shop.index(pet)
        shop_slot = self.shop.shop_slots[shop_idx]
        cost = shop_slot.cost
        
        if cost > self.gold:
            raise Exception("Attempted to buy Pet of cost {} with only {} gold"
                            .format(cost, self.gold))
        
        ### Connect pet with current Player 
        pet.team = self.team
        pet.player = self
        pet.shop = self.shop

        ### Make all updates 
        self.gold -= cost
        self.team.append(pet)
        self.shop.buy(pet)
        
        ### Check buy_friend triggers after purchase
        for slot in self.team:
            slot._pet.buy_friend_trigger(pet)
            
        ### Check summon triggers after purchse
        for slot in self.team:
            slot._pet.friend_summoned_trigger(pet)
        
        return 
    
    
    def buy_food(self, food, team_pet):
        """ Buy and feed one food from the shop to a pet """
        if type(food).__name__ == "ShopSlot":
            food = food.item
            
        if type(food).__name__ != "Food":
            raise Exception("Attempted to buy_food using object {}".format(food))
        
        if type(team_pet).__name__ == "TeamSlot":
            team_pet = team_pet._pet
            
        if not self.team.check_friend(team_pet):
            raise Exception("Attempted to buy food for Pet not on team {}"
                            .format(temp_pet))
        
        if type(team_pet).__name__ != "Pet":
            raise Exception("Attempted to buy_pet using object {}".format(team_pet))
        
        shop_idx = self.shop.index(food)
        shop_slot = self.shop.shop_slots[shop_idx]
        cost = shop_slot.cost
        
        if cost > self.gold:
            raise Exception("Attempted to buy Pet of cost {} with only {} gold"
                            .format(cost, self.gold))
            
        ### Before feeding, check for cat
        for slot in self.team:
            if slot._pet.name != "pet-cat":
                continue
            slot._pet.cat_trigger(food)
        
        ### Make all updates 
        self.gold -= cost
        levelup = team_pet.eat(food)
        self.shop.buy(food)
        
        ### Check for levelup triggers if appropriate
        if levelup:
            team_pet.levelup_trigger(team_pet)
        
        ### After feeding, check for buy_food triggers
        for slot in self.team:
            slot._pet.buy_food_trigger(food)
            
        ### Check if any animals fainted because of pill and if any other
        ### animals fainted because of those animals fainting
        while True:
            fainted_list = []
            for slot in self.team:
                if slot.empty:
                    continue
                if slot.health <= 0:
                    fainted_list.append(slot._pet)
            for fainted_pet in fainted_list:
                fainted_pet_idx = self.team.index(fainted_pet)+1
                for slot in self.team:
                    slot._pet.faint_trigger(fainted_pet, fainted_pet_idx)
                if self.team.check_friend(fainted_pet):
                    self.team.remove(fainted_pet)
            if len(fainted_list) == 0:
                break
        
        return 
    
    
    def sell(self, pet):
        """ Sell one pet on the team """
        if type(pet).__name__ == "TeamSlot":
            pet = pet._pet
        
        if type(pet).__name__ != "Pet":
            raise Exception("Attempted to sell Object {}".format(pet))
        
        ### Activate sell trigger first
        for slot in self.team:
            slot._pet.sell_trigger(pet)
            
        ### Then delete from team
        del_idx = self.team.index(pet)
        del(self.team.team[del_idx])
        
        ### Add default gold
        self.gold += 1
        
        return
    
    
    def freeze(self, obj):
        """ Freeze one pet or food in the shop """
        if type(obj).__name__ == "ShopSlot":
            obj = obj.item
            shop_idx = self.shop.index(obj)
        elif type(obj) == int:
            shop_idx = obj
        shop_slot = self.shop.shop_slots[shop_idx]
        shop_slot.freeze()
        return
        
    
    def roll(self):
        """ Roll shop """
        if self.gold < 1:
            raise Exception("Attempt to roll without gold")
        self.shop.roll()
        self.gold -= 1
        return
    
    
    def buy_combine(self, shop_pet, team_pet):
        """ Combine two pets on purchase """
        if type(shop_pet).__name__ == "ShopSlot":
            shop_pet = shop_pet.item
        if type(team_pet).__name__ == "TeamSlot":
            team_pet = team_pet._pet
        
        if type(shop_pet).__name__ != "Pet":
            raise Exception("Attempted buy_combined with Shop item {}"
                            .format(shop_pet))
        if type(team_pet).__name__ != "Pet":
            raise Exception("Attempted buy_combined with Team Pet {}"
                            .format(team_pet))
        if team_pet.name != shop_pet.name:
            raise Exception("Attempted combine for pets {} and {}"
                            .format(team_pet.name, shop_pet.name))
        
        shop_idx = self.shop.index(shop_pet)
        shop_slot = self.shop.shop_slots[shop_idx]
        cost = shop_slot.cost
        
        if cost > self.gold:
            raise Exception("Attempted to buy Pet of cost {} with only {} gold"
                            .format(cost, self.gold))
        
        ### Make all updates 
        self.gold -= cost
        self.shop.buy(shop_pet)
        
        ### Perform combine
        cattack = max(shop_pet.attack, team_pet.attack)+1
        chealth = max(shop_pet.health, team_pet.health)+1
        team_pet.attack = cattack
        team_pet.health = chealth
        levelup = team_pet.gain_experience()
        
        ### Check for levelup triggers if appropriate
        if levelup:
            ### Activate the ability of the previous level
            team_pet.level -= 1
            team_pet.levelup_trigger(team_pet)
            team_pet.level += 1
            
        ### Check for buy_pet triggers
        for slot in self.team:
            slot._pet.buy_friend_trigger(team_pet)
    
    
    def combine(self, pet1, pet2):
        """ Combine two pets on the team together """
        if type(pet1).__name__ == "TeamSlot":
            pet1 = pet1._pet
        if type(pet2).__name__ == "TeamSlot":
            pet2 = pet2._pet
        
        if not self.team.check_friend(pet1):
            raise Exception("Attempted combine for Pet not on team {}"
                            .format(pet1))
        if not self.team.check_friend(pet2):
            raise Exception("Attempted combine for Pet not on team {}"
                            .format(pet2))
        
        if pet1.name != pet2.name:
            raise Exception("Attempted combine for pets {} and {}"
                            .format(pet1.name, pet2.name))
        
        ### Perform combine
        cattack = max(pet1.attack, pet2.attack)+1
        chealth = max(pet1.health, pet2.health)+1
        pet1.attack = cattack
        pet1.health = chealth
        levelup = pet1.gain_experience()
        
        ### Check for levelup triggers if appropriate
        if levelup:
            ### Activate the ability of the previous level
            pet1.level -= 1
            pet1.levelup_trigger(pet1)
            pet1.level += 1
        
        ### Remove pet2 from team
        idx = self.team.index(pet2)
        self.team[idx] = TeamSlot()
        return
        
    
    def reorder(self, idx):
        """ Reorder team """
        if len(idx) != len(self.team):
            raise Exception("Reorder idx must match team length")
        unique = np.unique(idx)
        
        if len(unique) != len(self.team):
            raise Exception("Cannot input duplicate indices to reorder: {}"
                            .format(idx))
            
        self.team = [self.team[x] for x in idx]
        return self.team
    
    
    def end_turn(self):
        """ End turn and move to fight phase """
        ### Activate eot trigger
        for slot in self.team:
            slot._pet.eot_trigger()
        
        
    @property
    def state(self):
        state_dict = {
            "type": "Player",
            "team": self.team.state,
            "shop": self.shop.state,
            "lives": self.lives, 
            "default_gold": self.default_gold, 
            "gold": self.gold, 
            "lf_winner": self.lf_winner,
            "pack": self.pack,
            "turn": self.turn, 
        }
        return state_dict
    
    
    @classmethod
    def from_state(cls, state):
        team = Team.from_state(state["team"])
        shop = Shop.from_state(state["shop"])
        return cls(team=team,
                   shop=shop,
                   lives=state["lives"],
                   default_gold=state["default_gold"],
                   gold=state["gold"],
                   turn=state["turn"],
                   lf_winner=state["lf_winner"],
                   pack=state["pack"])
    
    
    def __repr__(self):
        info_str =  "PACK:  {}\n".format(self.pack)
        info_str += "TURN:  {}\n".format(self.turn)
        info_str += "LIVES: {}\n".format(self.lives)
        info_str += "GOLD:  {}\n".format(self.gold)
        print_str = "CURRENT INFO: \n--------------\n"+info_str+"\n"
        print_str += "CURRENT TEAM: \n--------------\n"+self.team.__repr__()+"\n"
        print_str += "CURRENT SHOP: \n--------------\n"+self.shop.__repr__()
        return print_str