# %%
import numpy as np
from sapai.data import data
from sapai.effects import get_effect_function, RespawnPet, SummonPet, SummonRandomPet
from sapai.tiers import pet_tier_lookup
from sapai.rand import MockRandomState
from sapai import status

# %%


class Pet:
    """
    Pet class defines all properties and triggers for Pets during gameplay

    """

    def __init__(
        self, name="pet-none", shop=None, team=None, player=None, seed_state=None
    ):
        if len(name) != 0:
            if not name.startswith("pet-"):
                name = f"pet-{name}"
        self.seed_state = seed_state
        if self.seed_state is not None:
            self.rs = np.random.RandomState()
            self.rs.set_state(self.seed_state)
        else:
            ### Otherwise, set use
            self.rs = MockRandomState()

        self.eaten = False
        self.shop = shop
        self.team = team
        self.player = player

        ### Used only for goat
        self.ability_counter = 0

        self.name = name
        if name not in data["pets"]:
            raise Exception(f"Pet {name} not found")
        fd = data["pets"][name]
        self.fd = fd
        self.override_ability = False
        self.override_ability_dict = {}
        self.tier = data["pets"][name]["tier"]

        ### Overall stats that should be brought into a battle
        self._attack = fd["baseAttack"]
        self._health = fd["baseHealth"]

        # For tracking buffs that only last until the end of battle
        self._until_end_of_battle_attack_buff = 0
        self._until_end_of_battle_health_buff = 0
        self._hurt = 0
        self.status = "none"
        if "status" in self.fd:
            self.status = self.fd["status"]

        self.level = 1
        self.experience = 0

        #### Add pet to team if not already present
        if self.team is not None:
            if self._attack != "none":
                if self not in team:
                    team.append(self)

            if self.team.shop is None:
                if self.shop is not None:
                    self.team.shop = self.shop

        ### Make sure everything has been initialized together
        if player is not None:
            if self.team is not None:
                player.team = self.team
            if self.shop is not None:
                player.shop = self.shop

    @property
    def attack(self):
        if self._attack == "none":
            return self._attack
        return min(
            status.apply_attack_dict[self.status](
                self._attack + self._until_end_of_battle_attack_buff
            ),
            50,
        )

    @property
    def health(self):
        if self._health == "none":
            return self._health
        return min(self._health + self._until_end_of_battle_health_buff, 50)

    @property
    def ability(self):
        if self.override_ability:
            return self.override_ability_dict
        if f"level{self.level}Ability" in self.fd:
            return self.fd[f"level{self.level}Ability"]
        else:
            return empty_ability

    def get_damage(self, value):
        return status.apply_damage_dict[self.status](value)

    def hurt(self, value):
        self._health -= value
        self._hurt += 1

    def set_ability(self, ability_dict):
        self.override_ability = True
        self.override_ability_dict = ability_dict
        return

    def eat(self, food):
        """Returns bool of whether pet levelups"""
        if food.apply_until_end_of_battle:
            self._until_end_of_battle_attack_buff += food.attack
            self._until_end_of_battle_health_buff += food.health
        else:
            self._attack += food.attack
            self._health += food.health

        if food.status != "none":
            self.status = food.status

        if food.name == "food-chocolate":
            return self.gain_experience()
        elif food.name == "food-sleeping-pill":
            self._health = -1000
        elif food.name == "food-canned-food":
            food.shop.shop_attack += food.attack
            food.shop.shop_health += food.health
        return False

    def init_battle(self):
        self.fhealth = int(self.health)
        self.fattack = int(self.attack)

    def combine(self, pet):
        raise Exception("Combine this pet with another pet")

    def gain_experience(self, amount=1):
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
            ["dromedary", "swan", "caterpillar", "squirrel", "hatching-chick lvl3"]
        """

        # Reset temporary attack and health buffs
        self._until_end_of_battle_attack_buff = 0
        self._until_end_of_battle_health_buff = 0

        ### Reset ability_counter for goat at sot_trigger
        self.ability_counter = 0

        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "StartOfTurn":
            return activated, targets, possible

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], trigger)

        activated = True
        return activated, targets, possible

    def cat_trigger(self, trigger=None):
        """
        Apply pet's shop ability to the given shop when shop is rolled

        Pets:
            ["cat"]
        """
        activated = False
        targets = []
        possible = []
        ### Hard coded because for some reason the cat trigger is hurt but it
        ###   should be roll
        if self.name not in ["pet-cat"]:
            return activated, targets, possible

        if type(trigger).__name__ != "Food":
            raise Exception("Must input purchased food as trigger for cat")

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], trigger)

        activated = True
        return activated, targets, possible

    def sell_trigger(self, trigger=None):
        """
        Apply pet's sell ability when a friend (or self) is self

        Pets:
            ["beaver", "duck", "pig", "shrimp", "owl"]
        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "Sell":
            return activated, targets, possible

        if type(trigger).__name__ != "Pet":
            raise Exception("Sell must be triggered by a Pet")

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        ### Remove the triggering pet before activating function because sell
        ###   has been called on this pet
        if self.team.check_friend(trigger):
            self.team.remove(trigger)

        ### Check if self has been sold is important
        if self.ability["triggeredBy"]["kind"] == "Self":
            if trigger != self:
                return activated, targets, possible

        ### Check if not selling self is important, only for shrimp
        if self.ability["triggeredBy"]["kind"] == "EachFriend":
            if trigger == self:
                return activated, targets, possible

        targets, possible = func(self, [0, pet_idx], [self.team], trigger)

        activated = True
        return activated, targets, possible

    def eats_shop_food_trigger(self, trigger=None):
        """
        Apply pet's ability when food is eaten

        Pets:
            ["beetle", "tabby-cat", "rabbit", "worm", "seal"]

        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "EatsShopFood":
            return activated, targets, possible

        if type(trigger).__name__ != "Pet":
            raise Exception("Buy food must input pet that ate as trigger")

        ### Check if food has been bought for self is important
        if self.ability["triggeredBy"]["kind"] == "Self":
            if trigger != self:
                return activated, targets, possible

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], trigger)

        activated = True
        return activated, targets, possible

    def buy_food_trigger(self, trigger=None):
        """
        Apply pet's ability when food is bought

        Pets:
            ["ladybug", "sauropod"]

        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "BuyFood":
            return activated, targets, possible

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], trigger)

        activated = True
        return activated, targets, possible

    def buy_friend_trigger(self, trigger=None):
        """
        Apply pet's ability when a friend (or self) is bought

        Pets:
            ["otter", "crab", "snail", "buffalo", "chicken", "cow",
             "goat", "dragon", ]
        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] not in ["Buy", "BuyAfterLoss", "BuyTier1Animal"]:
            return activated, targets, possible

        if type(trigger).__name__ != "Pet":
            raise Exception("Buy food must input food target as triggered")

        ### Behavior for bought self and friend
        if self.ability["trigger"] == "Buy":
            if self.ability["triggeredBy"]["kind"] == "Self":
                if trigger != self:
                    return activated, targets, possible
            elif self.ability["triggeredBy"]["kind"] == "Player":
                ### Behavior for kind=self and kind=player is actually the
                ###   same and any distinction is unnecessary
                if trigger != self:
                    return activated, targets, possible
            elif self.ability["triggeredBy"]["kind"] == "EachFriend":
                ### If trigger is EachFriend, then the trigger cannot actually
                ###   be self
                if trigger == self:
                    return activated, targets, possible
            else:
                raise Exception(f"Ability unrecognized for {self}")

        ### Behavior for BuyTier1Animal
        if self.ability["trigger"] == "BuyTier1Animal":
            if trigger.name not in pet_tier_lookup[1]:
                return activated, targets, possible

        ### Behavior for BuyAfterLoss
        if self.ability["trigger"] == "BuyAfterLoss":
            if self.player is None:
                return activated, targets, possible
            if self.player.lf_winner != False:
                return activated, targets, possible

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], trigger)

        activated = True
        return activated, targets, possible

    def friend_summoned_trigger(self, trigger=None):
        """
        Apply pet's ability when a friend is summoned

        Pets:
            ["horse", "dog", "lobster", "turkey"]
        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "Summoned":
            return activated, targets, possible

        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")

        if trigger == self:
            ### Do not activate for summoning self
            return activated, targets, possible

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = tiger_func(
            func, False, self, [0, pet_idx], [self.team], trigger
        )

        activated = True
        return activated, targets, possible

    def levelup_trigger(self, trigger=None):
        """
        Apply pet's ability when a friend (or self) level-up

        Pets:
            ["fish", "octopus"]
        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "LevelUp":
            return activated, targets, possible

        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], te=trigger)

        activated = True
        return activated, targets, possible

    def eot_trigger(self, trigger=None):
        """
        Apply pet's end-of-turn ability

        Pets:
            ["bluebird", "hatching-chick", "giraffe", "puppy", "tropical-fish",
             "bison", "llama", "penguin", "parrot", "monkey", "poodle",
             "tyrannosaurus"]
        """
        activated = False
        targets = []
        possible = []
        if not self.ability["trigger"].startswith("EndOfTurn"):
            return activated, targets, possible

        ### Check gold for puppy and tyrannosaurus
        if self.ability["trigger"] == "EndOfTurnWith3PlusGold":
            if self.player is not None:
                if self.player.gold >= 3:
                    pass
                else:
                    return activated, targets, possible
            else:
                return activated, targets, possible
        ### Check for bison
        elif self.ability["trigger"] == "EndOfTurnWithLvl3Friend":
            if self.team is not None:
                if not self.team.check_lvl3():
                    return activated, targets, possible
            else:
                return activated, targets, possible
        ### Check for llama
        elif self.ability["trigger"] == "EndOfTurnWith4OrLessAnimals":
            if self.team is not None:
                if len(self.team) > 4:
                    return activated, targets, possible
            else:
                return activated, targets, possible
        else:
            if self.ability["trigger"] != "EndOfTurn":
                raise Exception(f"Unrecognized trigger {self.ability['trigger']}")

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = func(self, [0, pet_idx], [self.team], te=trigger)

        activated = True
        return activated, targets, possible

    def faint_trigger(self, trigger=None, te_idx=None, oteam=None):
        """
        Apply pet's ability associated with a friend (or self) fainting

        Pets:
            ["ant", "cricket", "flamingo", "hedgehog", "spider", "badger",
             "ox", "sheep", "turtle", "deer", "rooster", "microbe",
             "eagle", "shark", "fly", "mammoth"]
        """
        te_idx = te_idx or []

        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "Faint":
            return activated, targets, possible

        if type(trigger).__name__ != "Pet":
            raise Exception("Trigger must be a Pet")

        if len(te_idx) == 0:
            raise Exception("Index of triggering entity must be input")

        if self.ability["triggeredBy"]["kind"] == "Self":
            if trigger != self:
                return activated, targets, possible
        elif self.ability["triggeredBy"]["kind"] == "FriendAhead":
            pet_ahead = self.team.get_ahead(self, n=1)
            if len(pet_ahead) == 0:
                return activated, targets, possible
            pet_ahead = pet_ahead[0]
            if trigger != pet_ahead:
                return activated, targets, possible
        elif self.ability["triggeredBy"]["kind"] == "EachFriend":
            if trigger == self:
                ### Only time this doesn't activate is if it self triggered
                return activated, targets, possible
        else:
            pass

        ### Check for Fly
        if self.name == "pet-fly":
            if trigger.name == "pet-zombie-fly":
                ### Do not activate if another zombie-fly faints
                return activated, targets, possible

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        if self.team.check_friend(self):
            pet_idx = self.team.get_idx(self)
        else:
            pet_idx = te_idx

        if oteam is not None:
            teams = [self.team, oteam]
        else:
            teams = [self.team]

        if func in [RespawnPet, SummonPet, SummonRandomPet]:
            ### API for SummonPet is slightly different
            targets, possible = tiger_func(
                func, True, self, [0, pet_idx], teams, trigger, te_idx
            )
        else:
            targets, possible = tiger_func(
                func, True, self, [0, pet_idx], teams, trigger
            )

        activated = True
        return activated, targets, possible

    def sob_trigger(self, trigger):
        """
        Start of a battle trigger. Input trigger is the opponent's Team.

        Pets:
            ["mosquito", "bat", "whale", "dolphin", "skunk", "crocodile",
            "leopard", "caterpillar lvl3"]

        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "StartOfBattle":
            return activated, targets, possible

        if type(trigger).__name__ != "Team":
            raise Exception("Trigger must be a Team")

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = tiger_func(
            func, False, self, [0, pet_idx], [self.team, trigger], trigger
        )

        activated = True
        return activated, targets, possible

    def before_attack_trigger(self, trigger):
        """
        Apply pet's ability before attacking. Input trigger is the
        opponent's Team.

        Pets:
            ["elephant", "boar", "octopus"]
        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "BeforeAttack":
            return activated, targets, possible

        if type(trigger).__name__ != "Team":
            raise Exception("Trigger must be a Team")

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = tiger_func(
            func, False, self, [0, pet_idx], [self.team, trigger], trigger
        )

        activated = True
        return activated, targets, possible

    def after_attack_trigger(self, trigger):
        """
        Apply pet's ability after attacking. Input trigger is the
        opponent's Team.

        Pets:
            ["kangaroo","snake"]

        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "AfterAttack":
            return activated, targets, possible

        if type(trigger).__name__ != "Team":
            raise Exception("Trigger must be a Team")

        if self.ability["triggeredBy"]["kind"] != "FriendAhead":
            raise Exception(
                "Only triggeredBy FriendAhead implemented for after_attack_trigger"
            )

        ### Check that self is behind the front friend which should have just
        ###   attacked
        slot_ahead = self.team.get_ahead(self, n=1)
        if len(slot_ahead) == 0:
            return activated, targets, possible
        if self.team.index(slot_ahead[0]) != 0:
            return activated, targets, possible

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        ### Otherwise, the pet ahead is the pet the just attacked and the
        ###   ability after attack should be activated
        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = tiger_func(
            func, False, self, [0, pet_idx], [self.team, trigger], trigger
        )

        activated = True
        return activated, targets, possible

    def hurt_trigger(self, trigger):
        """
        Apply pet's ability after being hurt attacking. Input trigger is the
        opponent's Team. Only activate hurt trigger if the pet has health above
        0.

        There is no way to test if hurt_trigger should be activated within this
        function. Therefore, only call hurt trigger where appropriate during
        battle and shop phase.

        Pets:
            ["peacock", "blowfish", "camel", "gorilla"]

        """
        activated = False
        targets = []
        possible = []
        if self._hurt == 0:
            raise Exception("Called hurt trigger on pet that was not hurt")
        else:
            self._hurt -= 1

        if self.ability["trigger"] != "Hurt":
            return activated, targets, possible

        if type(trigger).__name__ != "Team":
            raise Exception("Trigger must be a Team")

        if self.ability["triggeredBy"]["kind"] == "Self":
            pass
        else:
            raise Exception("Only Self trigger available for hurt_trigger")

        ### Cannot call if health is less than zero because fainted
        if self._health <= 0:
            return activated, targets, possible

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = tiger_func(
            func, False, self, [0, pet_idx], [self.team, trigger], trigger
        )

        activated = True
        return activated, targets, possible

    def knockout_trigger(self, trigger):
        """
        Apply pet's ability after knockout on opponent. Input trigger is the
        opponent's Team. Only activate trigger if the pet has health above 0.

        There is no way to test if knockout_trigger should be activated within
        this function. Therefore, only call knockout_trigger where appropriate
        during the battle phase.

        Pets:
            ["hippo", "rhino"]
        """
        activated = False
        targets = []
        possible = []
        if self.ability["trigger"] != "KnockOut":
            return activated, targets, possible

        if type(trigger).__name__ != "Team":
            raise Exception("Trigger must be a Team")

        ### Cannot call if health is less than zero because fainted
        if self._health <= 0:
            return activated, targets, possible

        if "maxTriggers" in self.ability:
            if self.ability_counter >= self.ability["maxTriggers"]:
                return activated, targets, possible
            else:
                self.ability_counter += 1

        func = get_effect_function(self)
        pet_idx = self.team.get_idx(self)
        targets, possible = tiger_func(
            func, False, self, [0, pet_idx], [self.team, trigger], trigger
        )

        activated = True
        return activated, targets, possible

    def __repr__(self):
        return f"< {self.name} {self.attack}-{self.health} {self.status} {self.level}-{self.experience} >"

    def copy(self):
        copy_pet = Pet(self.name, self.shop, seed_state=self.seed_state)
        for key, value in self.__dict__.items():
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

        #### Ensure that state can be JSON serialized
        if getattr(self, "rs", False):
            if isinstance(self.rs, MockRandomState):
                seed_state = None
            else:
                seed_state = list(self.rs.get_state())
                seed_state[1] = seed_state[1].tolist()
        else:
            seed_state = None

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
            "attack": self._attack,
            "health": self._health,
            "until_end_of_battle_attack_buff": self._until_end_of_battle_attack_buff,
            "until_end_of_battle_health_buff": self._until_end_of_battle_health_buff,
            "status": self.status,
            "level": self.level,
            "experience": self.experience,
            "seed_state": seed_state,
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
        pet._attack = state["attack"]
        pet._health = state["health"]
        pet._until_end_of_battle_attack_buff = state["until_end_of_battle_attack_buff"]
        pet._until_end_of_battle_health_buff = state["until_end_of_battle_health_buff"]
        pet.status = state["status"]
        pet.level = state["level"]
        pet.experience = state["experience"]

        ### Supply seed_state in state dict should be optional
        if "seed_state" in state:
            if state["seed_state"] is not None:
                pet.seed_state = state["seed_state"]
                pet.rs = np.random.RandomState()
                pet.rs.set_state(pet.seed_state)

        return pet


def tiger_func(func, te_fainted, *args):
    ### Check behind for tiger
    apet = args[0]
    if apet.team is None:
        ### Just run function
        targets, possible = func(*args)
        return targets, possible

    ### If checked on Bee status, then not repeated because this is a status
    ###   and not an ability
    if "pet" in apet.ability["effect"]:
        if apet.ability["effect"]["pet"] == "pet-bee":
            targets, possible = func(*args)
            return targets, possible
    ### Mushroom
    if "kind" in apet.ability["effect"]:
        if apet.ability["effect"]["kind"] == "RespawnPet":
            targets, possible = func(*args)
            return targets, possible

    ### Get pet behind apet before running function
    pet_behind = apet.team.get_behind(apet, n=1)

    ### If the triggering entity is supposed to have fainted, remove it now
    if te_fainted:
        if apet.team.check_friend(args[3]):
            apet.team.remove(args[3])

    ### Run function
    targets, possible = func(*args)

    ### If not in a battle, then tiger doesnt trigger
    if not apet.team.battle:
        return targets, possible

    ### If there's no pet behind, then return
    if len(pet_behind) == 0:
        return targets, possible

    ### Check if tiger is behind
    pet_behind = pet_behind[0].pet
    if pet_behind.name != "pet-tiger":
        return targets, possible
    if pet_behind.health <= 0:
        ### If tiger died and has been removed don't run function again
        if not apet.team.check_friend(pet_behind):
            return targets, possible

    ### Reset activiting pet's original ability because that's what should
    ###  be duplicated. This is important for Whale.
    if not te_fainted:
        apet.override_ability = False
    if len(args) == 5:
        te_idx = [0, args[4][1] + len(targets)]
        ### Run function again
        temp_targets, temp_possible = func(args[0], args[1], args[2], args[3], te_idx)
    else:
        temp_targets, temp_possible = func(*args)

    return [targets] + [temp_targets], [possible] + [temp_possible]


empty_ability = {
    "description": "none",
    "trigger": "none",
    "triggeredBy": {"kind": "none", "n": "none"},
    "effect": {
        "kind": "none",
        "attackAmount": "none",
        "healthAmount": "none",
        "target": {"kind": "none", "n": "none", "includingFuture": "none"},
        "untilEndOfBattle": "none",
        "pet": "none",
        "withAttack": "none",
        "withHealth": "none",
        "team": "none",
        "amount": "none",
        "status": "none",
        "to": {"kind": "none", "n": "none"},
        "copyAttack": "none",
        "copyHealth": "none",
        "from": {"kind": "none", "n": "none"},
        "effects": "none",
        "tier": "none",
        "baseAttack": "none",
        "baseHealth": "none",
        "percentage": "none",
        "shop": "none",
        "food": "none",
        "level": "none",
    },
    "maxTriggers": "none",
}

# %%
