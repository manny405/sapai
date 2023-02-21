import numpy as np
from sapai import data
from sapai.battle import Battle
from sapai.effects import (
    RespawnPet,
    SummonPet,
    SummonRandomPet,
    get_effect_function,
    get_target,
)

import sapai.shop
from sapai.shop import Shop, ShopSlot
from sapai.teams import Team, TeamSlot


def storeaction(func):
    def store_action(*args, **kwargs):
        player = args[0]
        action_name = str(func.__name__).split(".")[-1]
        targets = func(*args, **kwargs)
        store_targets = []
        if targets is not None:
            for entry in targets:
                if getattr(entry, "state", False):
                    store_targets.append(entry.state)
        player.action_history.append((action_name, store_targets))

    ### Make sure that the func returned as the same name as input func
    store_action.__name__ = func.__name__

    return store_action


class Player:
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

    def __init__(
        self,
        shop=None,
        team=None,
        lives=10,
        default_gold=10,
        gold=10,
        turn=1,
        lf_winner=None,
        action_history=None,
        pack="StandardPack",
        seed_state=None,
        wins=0,
    ):
        action_history = action_history or []

        self.shop = shop
        self.team = team
        self.lives = lives
        self.default_gold = default_gold
        self.gold = gold
        self.pack = pack
        self.turn = turn
        self.wins = wins

        ### Default Parameters
        self._max_team = 5

        ### Keep track of outcome of last battle for snail
        self.lf_winner = lf_winner

        ### Initialize shop and team if not provided
        if self.shop is None:
            self.shop = Shop(pack=self.pack, seed_state=seed_state)
        if self.team is None:
            self.team = Team(seed_state=seed_state)

        if type(self.shop) == list:
            self.shop = Shop(self.shop, seed_state=seed_state)
        if type(self.team) == list:
            self.team = Team(self.team, seed_state=seed_state)

        ### Connect objects
        self.team.player = self
        for slot in self.team:
            slot._pet.player = self
            slot._pet.shop = self.shop

        for slot in self.shop:
            slot.obj.player = self
            slot.obj.shop = self.shop

        ### This stores the history of actions taken by the given player
        if len(action_history) == 0:
            self.action_history = []
        else:
            self.action_history = list(action_history)

    @storeaction
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

        return ()

    @storeaction
    def buy_pet(self, pet):
        """Buy one pet from the shop"""
        if len(self.team) == self._max_team:
            raise Exception("Attempted to buy Pet on full team")

        if type(pet) == int:
            pet = self.shop[pet]

        if isinstance(pet, ShopSlot):
            pet = pet.obj

        if type(pet).__name__ != "Pet":
            raise Exception(f"Attempted to buy_pet using object {pet}")

        shop_idx = self.shop.index(pet)
        shop_slot = self.shop.slots[shop_idx]
        cost = shop_slot.cost

        if cost > self.gold:
            raise Exception(
                f"Attempted to buy Pet of cost {cost} with only {self.gold} gold"
            )

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

        return (pet,)

    @storeaction
    def buy_food(self, food, team_pet=None):
        """
        Buy and feed one food from the shop

        team_pet is either the purchase target or empty for food effect target

        """
        if type(food) == int:
            food = self.shop[food]
            if food.slot_type != "food":
                raise Exception("Shop slot not food")
        if isinstance(food, ShopSlot):
            food = food.obj
        if type(food).__name__ != "Food":
            raise Exception(f"Attempted to buy_food using object {food}")

        if team_pet is None:
            targets, _ = get_target(food, [0, None], [self.team])
        else:
            if type(team_pet) == int:
                team_pet = self.team[team_pet]
            if isinstance(team_pet, TeamSlot):
                team_pet = team_pet._pet
            if not self.team.check_friend(team_pet):
                raise Exception(f"Attempted to buy food for Pet not on team {team_pet}")
            if type(team_pet).__name__ != "Pet":
                raise Exception(f"Attempted to buy_pet using object {team_pet}")
            targets = [team_pet]

        shop_idx = self.shop.index(food)
        shop_slot = self.shop.slots[shop_idx]
        cost = shop_slot.cost

        if cost > self.gold:
            raise Exception(
                f"Attempted to buy Pet of cost {cost} with only {self.gold} gold"
            )

        ### Before feeding, check for cat
        for slot in self.team:
            if slot._pet.name != "pet-cat":
                continue
            slot._pet.cat_trigger(food)

        ### Make all updates
        self.gold -= cost
        self.shop.buy(food)
        for pet in targets:
            levelup = pet.eat(food)
            ### Check for levelup triggers if appropriate
            if levelup:
                pet.levelup_trigger(pet)
                self.shop.levelup()

            ### After feeding, check for eats_shop_food triggers
            for slot in self.team:
                slot._pet.eats_shop_food_trigger(pet)

        ### After feeding, check for buy_food triggers
        for slot in self.team:
            slot._pet.buy_food_trigger()

        ### Check if any animals fainted because of pill and if any other
        ### animals fainted because of those animals fainting
        pp = Battle.update_pet_priority(self.team, Team())  # no enemy team in shop
        status_list = []
        while True:
            ### Get a list of fainted pets
            fainted_list = []
            for _, pet_idx in pp:
                p = self.team[pet_idx].pet
                if p.name == "pet-none":
                    continue
                if p.health <= 0:
                    fainted_list.append(pet_idx)
                    if p.status != "none":
                        status_list.append([p, pet_idx])

            ### check every fainted pet
            faint_targets_list = []
            for pet_idx in fainted_list:
                fainted_pet = self.team[pet_idx].pet
                ### check for all pets that trigger off this fainted pet (including self)
                for _, te_pet_idx in pp:
                    other_pet = self.team[te_pet_idx].pet
                    te_idx = [0, pet_idx]
                    activated, targets, possible = other_pet.faint_trigger(
                        fainted_pet, te_idx
                    )
                    if activated:
                        faint_targets_list.append(
                            [fainted_pet, pet_idx, activated, targets, possible]
                        )

                ### If no trigger was activated, then the pet was never removed.
                ###   Check to see if it should be removed now.
                if self.team.check_friend(fainted_pet):
                    self.team.remove(fainted_pet)

            ### If pet was summoned, then need to check for summon triggers
            for (
                fainted_pet,
                pet_idx,
                activated,
                targets,
                possible,
            ) in faint_targets_list:
                self.check_summon_triggers(
                    fainted_pet, pet_idx, activated, targets, possible
                )

            ### if pet was hurt, then need to check for hurt triggers
            hurt_list = []
            for _, pet_idx in pp:
                p = self.team[pet_idx].pet
                while p._hurt > 0:
                    hurt_list.append(pet_idx)
                    activated, targets, possible = p.hurt_trigger(Team())

            pp = Battle.update_pet_priority(self.team, Team())

            ### if nothing happend, stop the loop
            if len(fainted_list) == 0 and len(hurt_list) == 0:
                break

        ### Check for status triggers on pet
        for p, pet_idx in status_list:
            self.check_status_triggers(p, pet_idx)

        return (food, targets)

    def check_summon_triggers(self, fainted_pet, pet_idx, activated, targets, possible):
        if not activated:
            return
        func = get_effect_function(fainted_pet)
        if func not in [RespawnPet, SummonPet, SummonRandomPet]:
            return
        for temp_te in targets:
            for temp_slot in self.team:
                temp_pet = temp_slot.pet
                temp_pet.friend_summoned_trigger(temp_te)

    def check_status_triggers(self, fainted_pet, pet_idx):
        if fainted_pet.status not in ["status-honey-bee", "status-extra-life"]:
            return

        ability = data["statuses"][fainted_pet.status]["ability"]
        fainted_pet.set_ability(ability)
        te_idx = [0, pet_idx]
        activated, targets, possible = fainted_pet.faint_trigger(fainted_pet, te_idx)
        self.check_summon_triggers(fainted_pet, pet_idx, activated, targets, possible)

    @storeaction
    def sell(self, pet):
        """Sell one pet on the team"""
        if type(pet) == int:
            pet = self.team[pet]

        if isinstance(pet, TeamSlot):
            pet = pet._pet

        if type(pet).__name__ != "Pet":
            raise Exception(f"Attempted to sell Object {pet}")

        ### Activate sell trigger first
        for slot in self.team:
            slot._pet.sell_trigger(pet)

        if self.team.check_friend(pet):
            self.team.remove(pet)

        ### Add default gold
        self.gold += 1

        return (pet,)

    @storeaction
    def sell_buy(self, team_pet, shop_pet):
        """Sell one team pet and replace it with one shop pet"""
        if type(shop_pet) == int:
            shop_pet = self.shop[shop_pet]
        if type(team_pet) == int:
            team_pet = self.team[team_pet]

        if isinstance(shop_pet, ShopSlot):
            shop_pet = shop_pet.obj
        if isinstance(team_pet, TeamSlot):
            team_pet = team_pet._pet

        if type(shop_pet).__name__ != "Pet":
            raise Exception(f"Attempted sell_buy with Shop item {shop_pet}")
        if type(team_pet).__name__ != "Pet":
            raise Exception(f"Attempted sell_buy with Team Pet {team_pet}")

        ### Activate sell trigger first
        self.sell(team_pet)

        ### Then attempt to buy shop pet
        self.buy_pet(shop_pet)

        return (team_pet, shop_pet)

    def freeze(self, obj):
        """Freeze one pet or food in the shop"""
        if isinstance(obj, ShopSlot):
            obj = obj.obj
            shop_idx = self.shop.index(obj)
        elif type(obj) == int:
            shop_idx = obj
        shop_slot = self.shop.slots[shop_idx]
        shop_slot.freeze()
        return (shop_slot,)

    def unfreeze(self, obj):
        """Unfreeze one pet or food in the shop"""
        if isinstance(obj, ShopSlot):
            obj = obj.obj
            shop_idx = self.shop.index(obj)
        elif type(obj) == int:
            shop_idx = obj
        shop_slot = self.shop.slots[shop_idx]
        shop_slot.unfreeze()
        return (shop_slot,)

    @storeaction
    def roll(self):
        """Roll shop"""
        if self.gold < 1:
            raise Exception("Attempt to roll without gold")
        self.shop.roll()
        self.gold -= 1
        return ()

    @staticmethod
    def combine_pet_stats(pet_to_keep, pet_to_be_merged):
        """Pet 1 is the pet that is kept"""
        c_attack = max(pet_to_keep._attack, pet_to_be_merged._attack) + 1
        c_until_end_of_battle_attack = max(
            pet_to_keep._until_end_of_battle_attack_buff,
            pet_to_be_merged._until_end_of_battle_attack_buff,
        )
        c_health = max(pet_to_keep._health, pet_to_be_merged._health) + 1
        c_until_end_of_battle_health = max(
            pet_to_keep._until_end_of_battle_health_buff,
            pet_to_be_merged._until_end_of_battle_health_buff,
        )
        cstatus = get_combined_status(pet_to_keep, pet_to_be_merged)

        pet_to_keep._attack = c_attack
        pet_to_keep._health = c_health
        pet_to_keep._until_end_of_battle_attack_buff = c_until_end_of_battle_attack
        pet_to_keep._until_end_of_battle_health_buff = c_until_end_of_battle_health
        pet_to_keep.status = cstatus
        levelup = pet_to_keep.gain_experience()

        # Check for levelup triggers if appropriate
        if levelup:
            # Activate the ability of the previous level
            pet_to_keep.level -= 1
            pet_to_keep.levelup_trigger(pet_to_keep)
            pet_to_keep.level += 1

        return levelup

    @storeaction
    def buy_combine(self, shop_pet, team_pet):
        """Combine two pets on purchase"""
        if type(shop_pet) == int:
            shop_pet = self.shop[shop_pet]
        if type(team_pet) == int:
            team_pet = self.team[team_pet]

        if isinstance(shop_pet, ShopSlot):
            shop_pet = shop_pet.obj
        if isinstance(team_pet, TeamSlot):
            team_pet = team_pet._pet

        if type(shop_pet).__name__ != "Pet":
            raise Exception(f"Attempted buy_combined with Shop item {shop_pet}")
        if type(team_pet).__name__ != "Pet":
            raise Exception(f"Attempted buy_combined with Team Pet {team_pet}")
        if team_pet.name != shop_pet.name:
            raise Exception(
                f"Attempted combine for pets {team_pet.name} and {shop_pet.name}"
            )

        shop_idx = self.shop.index(shop_pet)
        shop_slot = self.shop.slots[shop_idx]
        cost = shop_slot.cost

        if cost > self.gold:
            raise Exception(
                f"Attempted to buy Pet of cost {cost} with only {self.gold} gold"
            )

        ### Make all updates
        self.gold -= cost
        self.shop.buy(shop_pet)

        levelup = Player.combine_pet_stats(team_pet, shop_pet)
        if levelup:
            self.shop.levelup()

        ### Check for buy_pet triggers
        for slot in self.team:
            slot._pet.buy_friend_trigger(team_pet)

        return shop_pet, team_pet

    @storeaction
    def combine(self, pet1, pet2):
        """Combine two pets on the team together"""
        if type(pet1) == int:
            pet1 = self.team[pet1]
        if type(pet2) == int:
            pet2 = self.team[pet2]

        if isinstance(pet1, TeamSlot):
            pet1 = pet1._pet
        if isinstance(pet2, TeamSlot):
            pet2 = pet2._pet

        if not self.team.check_friend(pet1):
            raise Exception(f"Attempted combine for Pet not on team {pet1}")
        if not self.team.check_friend(pet2):
            raise Exception(f"Attempted combine for Pet not on team {pet2}")

        if pet1.name != pet2.name:
            raise Exception(f"Attempted combine for pets {pet1.name} and {pet2.name}")

        levelup = Player.combine_pet_stats(pet1, pet2)
        if levelup:
            self.shop.levelup()

        ### Remove pet2 from team
        idx = self.team.index(pet2)
        self.team[idx] = TeamSlot()

        return pet1, pet2

    @storeaction
    def reorder(self, idx):
        """Reorder team"""
        if len(idx) != len(self.team):
            raise Exception("Reorder idx must match team length")
        unique = np.unique(idx)

        if len(unique) != len(self.team):
            raise Exception(f"Cannot input duplicate indices to reorder: {idx}")

        self.team = Team([self.team[x] for x in idx], seed_state=self.team.seed_state)

        return idx

    @storeaction
    def end_turn(self):
        """End turn and move to battle phase"""
        ### Activate eot trigger
        for slot in self.team:
            slot._pet.eot_trigger()
        return None

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
            "action_history": self.action_history,
            "wins": self.wins,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        team = Team.from_state(state["team"])
        shop_type = state["shop"]["type"]
        shop_cls = getattr(sapai.shop, shop_type)
        shop = shop_cls.from_state(state["shop"])
        if "action_history" in state:
            action_history = state["action_history"]
        else:
            action_history = []
        return cls(
            team=team,
            shop=shop,
            lives=state["lives"],
            default_gold=state["default_gold"],
            gold=state["gold"],
            turn=state["turn"],
            lf_winner=state["lf_winner"],
            pack=state["pack"],
            action_history=action_history,
            wins=state["wins"],
        )

    def __repr__(self):
        info_str = f"PACK:  {self.pack}\n"
        info_str += f"TURN:  {self.turn}\n"
        info_str += f"LIVES: {self.lives}\n"
        info_str += f"WINS:  {self.wins}\n"
        info_str += f"GOLD:  {self.gold}\n"
        print_str = "--------------\n"
        print_str += "CURRENT INFO: \n--------------\n" + info_str + "\n"
        print_str += "CURRENT TEAM: \n--------------\n" + self.team.__repr__() + "\n"
        print_str += "CURRENT SHOP: \n--------------\n" + self.shop.__repr__()
        return print_str


def get_combined_status(pet1, pet2):
    """
    Statuses are combined based on the tier that they come from.

    """
    status_tier = {
        0: ["status-weak", "status-poison-attack", "none"],
        1: ["status-honey-bee"],
        2: ["status-bone-attack"],
        3: ["status-garlic-armor"],
        4: ["status-splash-attack"],
        5: [
            "status-coconut-shield",
            "status-melon-armor",
            "status-steak-attack",
            "status-extra-life",
        ],
    }

    status_lookup = {}
    for key, value in status_tier.items():
        for entry in value:
            status_lookup[entry] = key

    ### If there is a tie in tier, then pet1 status is used
    max_idx = np.argmax([status_lookup[pet1.status], status_lookup[pet2.status]])

    return [pet1.status, pet2.status][max_idx]
