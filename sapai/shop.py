# %%

from functools import partial
import numpy as np

from sapai.data import data
from sapai.lists import Slot, SAPList
from sapai.foods import Food
from sapai.pets import Pet
import sapai.foods
import sapai.pets
from sapai.rand import MockRandomState

# %%

################################################################################
#### Building optimized datastructures for construction shop states
################################################################################

pet_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
pet_tier_lookup_std = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
for key, value in data["pets"].items():
    if type(value["tier"]) == int:
        pet_tier_lookup[value["tier"]].append(key)
        if "StandardPack" in value["packs"]:
            pet_tier_lookup_std[value["tier"]].append(key)
pet_tier_avail_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
for key, value in pet_tier_lookup.items():
    for temp_key, temp_value in pet_tier_avail_lookup.items():
        if temp_key >= key:
            temp_value += value

food_tier_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
for key, value in data["foods"].items():
    if type(value["tier"]) == int:
        food_tier_lookup[value["tier"]].append(key)
food_tier_avail_lookup = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
for key, value in food_tier_lookup.items():
    for temp_key, temp_value in food_tier_avail_lookup.items():
        if temp_key >= key:
            temp_value += value

turn_prob_pets_std = {}
turn_prob_pets_exp = {}
for i in np.arange(0, 12):
    turn_prob_pets_std[i] = {}
    turn_prob_pets_exp[i] = {}
for key, value in data["pets"].items():
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
for i in np.arange(0, 12):
    turn_prob_foods_std[i] = {}
    turn_prob_foods_exp[i] = {}
for key, value in data["foods"].items():
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

# %%

# %%


class Shop(SAPList):
    def __init__(
        self,
        slots=None,
        turn=1,
        shop_attack=0,
        shop_health=0,
        pack="StandardPack",
        seed_state=None,
        fixed_rules=None,
    ):
        slots = slots or []

        #### Setting up random state
        self.seed_state = seed_state
        if self.seed_state is not None:
            self.rs = np.random.RandomState()
            self.rs.set_state(self.seed_state)
        else:
            self.rs = MockRandomState()

        self.max_slots = 7
        self.turn = turn
        self.pack = pack
        self.shop_attack = shop_attack  ### Keep track of can/chicken stats
        self.shop_health = shop_health  ### Keep track of can/chicken stats
        slot_class = partial(
            ShopSlot, pack=self.pack, turn=self.turn, seed_state=self.seed_state
        )

        if pack == "StandardPack":
            self.turn_prob_pets = turn_prob_pets_std
            self.turn_prob_foods = turn_prob_foods_std
        elif pack == "ExpansionPack1":
            self.turn_prob_pets = turn_prob_pets_exp
            self.turn_prob_foods = turn_prob_foods_exp
        else:
            raise Exception(f"Pack {pack} not valid")

        ### Initialize shop based on input turn or input slots
        rules = get_shop_rules(self.turn)
        if len(slots) == 0:
            self.pslots = rules[0]  ### Number pet slots for shop tier
            self.fslots = rules[1]  ### Number food slots for shop tiers
            if fixed_rules is None:
                self.fixed_rules = False
                nslots = self.pslots + self.fslots
            else:
                self.fixed_rules = fixed_rules
                nslots = 0
        else:
            temp_slots = []
            for slot in slots:
                if not isinstance(slot, Slot):
                    temp_slots.append(slot_class(slot))
                else:
                    temp_slots.append(slot)
            slots = temp_slots
            slot_types = [x.slot_type for x in slots]
            self.pslots = slot_types.count("pet")
            self.fslots = slot_types.count("food")
            if fixed_rules is None:
                self.fixed_rules = True
            else:
                self.fixed_rules = fixed_rules
            nslots = len(slots)
        self.tier_avail = rules[2]  ### Pet tier available
        self.levelup_tier = rules[3]  ### Level-up tier available
        self.avail_pets = rules[4]  ### Available pets for pet slots
        self.avail_foods = rules[5]  ### Avaliable foods for food slots
        self.pp = rules[6]  ### Probability of rolling each pet
        self.fp = rules[7]  ### Probability of rolling eaach food

        super().__init__(slots, nslots=nslots, slot_class=slot_class)
        if not self.fixed_rules:
            self.update_shop_rules(roll_only_empty=True)

    def buy(self, obj):
        """Only thing that buy does is to remove the item from the shop list"""
        if type(obj) == int:
            idx = obj
        else:
            idx = -1
            for iter_idx, slot in enumerate(self.slots):
                if slot.obj == obj:
                    idx = iter_idx
                    break

        if idx < 0:
            raise Exception(f"Unrecognized Shop Object {obj}")

        del self.slots[idx]

    def index(self, obj):
        if isinstance(obj, ShopSlot):
            obj = obj.obj
        idx = -1
        for iter_idx, slot in enumerate(self.slots):
            if slot.obj == obj:
                idx = iter_idx
                break
        if idx < 0:
            raise Exception(f"Unrecognized Shop Object {obj}")
        return idx

    @property
    def pets(self):
        pet_slots = []
        for slot in self.slots:
            if slot.slot_type == "pet":
                pet_slots.append(slot.obj)
            elif slot.slot_type == "levelup":
                pet_slots.append(slot.obj)
            else:
                pass
        return pet_slots

    @property
    def foods(self):
        food_slots = []
        for slot in self.slots:
            if slot.slot_type == "food":
                food_slots.append(slot.obj)
        return food_slots

    def roll(self, team=None, roll_only_empty=False):
        """Randomizes shop and returns list of available entries"""
        team = team or []

        self.check_rules()

        for slot in self.slots:
            # New RandomState per roll or else every slot will roll the same pet/food
            if roll_only_empty:
                if slot.empty:
                    if type(slot.rs).__name__ != "MockRandomState":
                        slot.rs = np.random.RandomState()
                        slot.rs.set_state(self.seed_state)
                    slot.roll()
                    self.seed_state = slot.seed_state
            else:
                # if type(slot.rs).__name__ != "MockRandomState":
                #     slot.rs = np.random.RandomState()
                #     slot.rs.set_state(self.seed_state)
                slot.roll()
                self.seed_state = slot.seed_state
            ### Add health and attack from previously purchased cans
            if not slot.frozen:
                if slot.slot_type == "pet":
                    slot.obj._attack += self.shop_attack
                    slot.obj._health += self.shop_health
                if slot.slot_type == "food":
                    slot.cost = slot.obj.cost

        for team_slot in team:
            team_slot._pet.shop_ability(shop=self, trigger="roll")

    def freeze(self, idx):
        """
        Freeze a shop index

        """
        if idx >= len(self.slots):
            ### Just do nothing if attempting to freeze outside the range of
            ###   the current shop
            return
        self.slots[idx].freeze()

    def unfreeze(self, idx):
        """
        Unfreeze shop index

        """
        if idx > len(self.slots):
            ### Just do nothing if attempting to unfreeze outside the range of
            ###   the current shop
            return
        self.slots[idx].unfreeze()

    def levelup(self):
        """
        Called when a pet is leveled-up by the player to update the shop state
        with a new pet

        """
        new_slot = ShopSlot("levelup", pack=self.pack, turn=self.turn)
        self.append(new_slot)

    def update_shop_rules(self, turn=-1, roll_only_empty=False):
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
        new_slots_pet = []
        new_slots_food = []
        for slot in self.slots:
            if slot.slot_type == "pet":
                new_slots_pet.append(slot)
            elif slot.slot_type == "food":
                new_slots_food.append(slot)
            else:
                pass

        add_pets = self.pslots - len(new_slots_pet)
        for i in range(add_pets):
            new_slots_pet.append(
                ShopSlot(
                    "pet", pack=self.pack, turn=self.turn, seed_state=self.seed_state
                )
            )

        add_foods = self.fslots - len(new_slots_food)
        for i in range(add_foods):
            new_slots_food.append(
                ShopSlot(
                    "food", pack=self.pack, turn=self.turn, seed_state=self.seed_state
                )
            )

        self.nslot = self.pslots + self.fslots
        self.slots = new_slots_pet + new_slots_food

        ### Roll all slots upon update of rules
        self.roll(roll_only_empty=roll_only_empty)

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
        for iter_idx, slot in enumerate(self.slots):
            if slot.frozen:
                keep_idx.append(iter_idx)
                if slot.slot_type == "pet":
                    pslots.append(iter_idx)
                elif slot.slot_type == "levelup":
                    pslots.append(iter_idx)
                elif slot.slot_type == "food":
                    fslots.append(iter_idx)

        ### Then add other slots only if it has not yet exceeded the rules
        for iter_idx, slot in enumerate(self.slots):
            if slot.frozen:
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
            add_slots = min(self.pslots - len(pslots), self.nslots - len(keep_idx))
            for idx in range(add_slots):
                self.slots.append(
                    ShopSlot(
                        "pet",
                        turn=self.turn,
                        pack=self.pack,
                        seed_state=self.seed_state,
                    )
                )
                keep_idx.append(len(self.slots) - 1)
        if len(fslots) < self.fslots:
            add_slots = min(self.fslots - len(fslots), self.nslots - len(keep_idx))
            for idx in range(add_slots):
                self.slots.append(
                    ShopSlot(
                        "food",
                        turn=self.turn,
                        pack=self.pack,
                        seed_state=self.seed_state,
                    )
                )
                keep_idx.append(len(self.slots) - 1)

        keep_slots = [self.slots[x] for x in keep_idx]
        self.slots = keep_slots

        ### Order shop slots
        pslots = []
        fslots = []
        for iter_idx, slot in enumerate(self.slots):
            if slot.slot_type == "pet":
                pslots.append(iter_idx)
            elif slot.slot_type == "leveup":
                pslots.append(iter_idx)
        for iter_idx, slot in enumerate(self.slots):
            if slot.slot_type == "food":
                fslots.append(iter_idx)
        keep_idx = pslots + fslots
        keep_slots = [self.slots[x] for x in keep_idx]
        self.slots = keep_slots

    def __len__(self):
        return len(self.slots)

    def __getitem__(self, idx):
        return self.slots[idx]

    def __setitem__(self, idx, obj):
        """
        __setitem__ should never be used

        """
        raise Exception("Cannot set item in shop directly")

    def append(self, obj):
        """
        Append should be used when adding an animal from a levelup
        """
        if len(self.slots) >= self.max_slots:
            ### Max slots already reached so cannot be added
            return

        add_slot = ShopSlot(
            obj, pack=self.pack, turn=self.turn, seed_state=self.seed_state
        )
        pslots = []
        fslots = []
        for iter_idx, slot in enumerate(self.slots):
            if slot.slot_type == "pet":
                pslots.append(slot)
            if slot.slot_type == "food":
                fslots.append(slot)

        new_slots = []
        new_slots += [x for x in pslots]
        new_slots += [add_slot]
        new_slots += [x for x in fslots]

        self.nslots = len(new_slots)
        self.slots = new_slots

    @property
    def state(self):
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
            "type": "Shop",
            "slots": [x.state for x in self.slots],
            "turn": self.turn,
            "shop_attack": self.shop_attack,
            "shop_health": self.shop_health,
            "pack": self.pack,
            "seed_state": seed_state,
            "fixed_rules": self.fixed_rules,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        ### Supply seed_state in state dict should be optional
        if "seed_state" in state:
            seed_state = state["seed_state"]
        else:
            seed_state = None
        return cls(
            slots=[ShopSlot.from_state(x) for x in state["slots"]],
            turn=state["turn"],
            shop_attack=state["shop_attack"],
            shop_health=state["shop_health"],
            pack=state["pack"],
            seed_state=seed_state,
            fixed_rules=state["fixed_rules"],
        )

    def __repr__(self):
        repr_str = ""
        for iter_idx, slot in enumerate(self.slots):
            repr_str += f"{iter_idx}: {slot} \n    "
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

    def __init__(self, *args, **kwargs):
        self.npet_bought = 0
        self.nfood_bought = 0
        self.nmax_levelup = 0
        self.nlevelup_bought = 0
        self.shop_names = {}
        super().__init__(*args, **kwargs)
        self.nslots = len(self.avail_pets) + len(self.avail_foods)

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
        if isinstance(obj, ShopSlot):
            pass
        elif type(obj) == int:
            obj = self.slots[obj]
        else:
            idx = -1
            for iter_idx, slot in enumerate(self.slots):
                if slot.obj == obj:
                    idx = iter_idx
                    obj = slot
                    break
            if idx < 0:
                raise Exception(f"Unrecognized Shop Object {obj}")

        if obj.slot_type == "pet":
            self.npet_bought += 1
        elif obj.slot_type == "food":
            self.nfood_bought += 1
        elif obj.slot_type == "levelup":
            self.nlevelup_bought += 1
        else:
            raise Exception(f"Unrecognized ShopSlot {obj}")

        ### Rebuild ShopLearn to remove all levelup ShopSlots
        self.update_shop_rules()

    def update_shop_rules(self, turn=-1, roll_only_empty=True):
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
        self.slots = []
        new_slots_pet = []
        new_slots_food = []
        new_slots_levelup = []

        ### Check if Pet purchase limit or Food purchase limit has been reached
        if self.npet_bought < self.pslots:
            for pet in self.avail_pets:
                new_slots_pet.append(
                    ShopSlot(
                        pet, pack=self.pack, turn=self.turn, seed_state=self.seed_state
                    )
                )
                self.shop_names[pet] = True
        if self.nfood_bought < self.fslots:
            for food in self.avail_foods:
                new_slots_food.append(
                    ShopSlot(
                        food, pack=self.pack, turn=self.turn, seed_state=self.seed_state
                    )
                )
                self.shop_names[food] = True
        if self.nlevelup_bought < self.nmax_levelup:
            if self.pack == "StandardPack":
                levelup_avail_pets = pet_tier_lookup_std[self.levelup_tier]
            else:
                levelup_avail_pets = pet_tier_lookup[self.levelup_tier]
            for pet in levelup_avail_pets:
                if pet not in self.shop_names:
                    temp_slot = ShopSlot(
                        slot_type="levelup",
                        pack=self.pack,
                        turn=self.turn,
                        seed_state=self.seed_state,
                    )
                    temp_slot.obj = Pet(pet, seed_state=self.seed_state)
                    new_slots_levelup.append(temp_slot)
                    self.shop_names[pet] = True

        self.slots = new_slots_pet + new_slots_levelup + new_slots_food

    def levelup(self):
        ### Add 1 to the number of levelup pets that can be bought
        self.nmax_levelup += 1
        ### Rebuild shop
        self.update_shop_rules()

    def check_rules(self):
        raise Exception("ShopLearn does not use check_rules")

    @property
    def state(self):
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
            "type": "ShopLearn",
            "slots": [x.state for x in self.slots],
            "turn": self.turn,
            "shop_attack": self.shop_attack,
            "shop_health": self.shop_health,
            "pack": self.pack,
            "seed_state": seed_state,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        ### Supply seed_state in state dict should be optional
        if "seed_state" in state:
            seed_state = state["seed_state"]
        else:
            seed_state = None
        return cls(
            slots=[ShopSlot.from_state(x) for x in state["slots"]],
            turn=state["turn"],
            shop_attack=state["shop_attack"],
            shop_health=state["shop_health"],
            pack=state["pack"],
            seed_state=seed_state,
        )


class ShopSlotNoneItem:
    def __init__(self, seed_state=None):
        self.player = None
        self.name = "none"
        self.seed_state = seed_state
        self.obj = None
        if self.seed_state is not None:
            self.rs = np.random.RandomState()
            self.rs.set_state(self.seed_state)
        else:
            ### Otherwise, set use
            self.rs = MockRandomState()

    @property
    def state(self):
        if getattr(self, "rs", False):
            if isinstance(self.rs, MockRandomState):
                seed_state = None
            else:
                seed_state = list(self.rs.get_state())
                seed_state[1] = seed_state[1].tolist()
        else:
            seed_state = None
        return {"type": "ShopSlotNoneItem", "seed_state": seed_state}

    @classmethod
    def from_state(cls, state):
        if "seed_state" in state:
            return cls(state["seed_state"])
        else:
            return cls()

    def copy(self):
        return self


class ShopSlot(Slot):
    """
    Class for a slot in the shop

    """

    def __init__(
        self,
        obj=None,
        slot_type="none",
        frozen=False,
        turn=1,
        cost=3,
        pack="StandardPack",
        seed_state=None,
    ):
        self.seed_state = seed_state
        if self.seed_state is not None:
            self.rs = np.random.RandomState()
            self.rs.set_state(self.seed_state)
        else:
            ### Otherwise, set use
            self.rs = MockRandomState()

        self.slot_type = slot_type
        self.turn = turn
        self.pack = pack
        self.frozen = frozen
        self.cost = cost
        self.obj = ShopSlotNoneItem(seed_state=self.seed_state)

        if slot_type not in ["pet", "food", "levelup", "none"]:
            raise Exception(f"Unrecognized slot type {self.slot_type}")

        if obj is not None and type(obj) != str:
            if isinstance(obj, Pet):
                self.slot_type = "pet"
                self.obj = obj
            elif isinstance(obj, Food):
                self.slot_type = "food"
                self.obj = obj
                self.cost = obj.cost
            elif isinstance(obj, ShopSlot):
                self.slot_type = obj.slot_type
                self.turn = obj.turn
                self.pack = obj.pack
                self.frozen = obj.frozen
                self.cost = obj.cost
                if self.slot_type == "food":
                    self.cost = obj.obj.cost
                self.obj = obj.obj
        else:
            if type(obj) == str:
                if obj not in ["pet", "food", "levelup"]:
                    if obj in data["pets"]:
                        name = obj
                        self.slot_type = "pet"
                    elif obj in data["foods"]:
                        name = obj
                        self.slot_type = "food"
                    elif f"pet-{obj}" in data["pets"]:
                        name = obj
                        self.slot_type = "pet"
                    elif f"food-{obj}" in data["foods"]:
                        name = obj
                        self.slot_type = "food"
                    else:
                        raise Exception(f"Unrecognized ShopSlot Object {obj}")
                else:
                    self.slot_type = obj
                    name = "none"
            else:
                self.slot_type = "none"
                name = "none"

            if self.slot_type == "pet":
                self.obj = Pet(name, seed_state=self.seed_state)
            elif self.slot_type == "food":
                self.obj = Food(name, seed_state=self.seed_state)
                self.cost = self.obj.cost
            elif self.slot_type == "levelup":
                self.roll_levelup()
            elif self.slot_type == "none":
                self.obj = ShopSlotNoneItem(seed_state=self.seed_state)

    def __repr__(self):
        if self.frozen:
            fstr = "frozen"
        else:
            fstr = "not-frozen"
        if self.slot_type == "pet" or self.slot_type == "levelup":
            if self.obj.name == "pet-none":
                return f"< ShopSlot-{self.slot_type} {fstr} EMPTY >"
            else:
                pet_repr = str(self.obj)
                pet_repr = pet_repr[2:-2]
                return (
                    f"< ShopSlot-{self.slot_type} {fstr} {self.cost}-gold {pet_repr} >"
                )
        elif self.slot_type == "food":
            if self.obj.name == "food-none":
                return f"< ShopSlot-{self.slot_type} {fstr} EMPTY >"
            else:
                food_repr = str(self.obj)
                food_repr = food_repr[2:-2]
                return (
                    f"< ShopSlot-{self.slot_type} {fstr} {self.cost}-gold {food_repr} >"
                )
        elif self.slot_type == "none":
            return f"< ShopSlot-{None} {fstr} EMPTY >"
        else:
            raise Exception(f"Invalid ShopSlot type {self.slot_type}")

    @property
    def empty(self):
        """
        Returns if the given slot is empty
        """
        return self.obj.name in ["pet-none", "food-none", "none"]

    def freeze(self):
        """
        Freeze current slot such that shop rolls don't update the ShopSlot
        """
        if self.slot_type == "none":
            raise Exception("Cannot freeze an empty shop slot")
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    def roll(self, avail=None, prob=None):
        avail = avail or []
        prob = prob or []

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
                avail = ["none"]
                prob = [1]

        choice = self.rs.choice(avail, size=(1,), replace=True, p=prob)[0]
        self.seed_state = self.rs.get_state()
        if self.slot_type == "pet":
            self.obj = Pet(choice, seed_state=self.seed_state)
        elif self.slot_type == "food":
            self.obj = Food(choice, seed_state=self.seed_state)
        elif self.slot_type == "none":
            self.obj = ShopSlotNoneItem(seed_state=self.seed_state)

    def roll_levelup(self):
        rules = get_shop_rules(self.turn, pack=self.pack)
        levelup_tier = rules[3]
        if self.pack == "StandardPack":
            avail_pets = pet_tier_lookup_std[levelup_tier]
        else:
            avail_pets = pet_tier_lookup[levelup_tier]
        pet_choice = self.rs.choice(avail_pets, size=(1,), replace=True)[0]
        self.seed_state = self.rs.get_state()
        self.obj = Pet(pet_choice, seed_state=self.seed_state)

    @property
    def state(self):
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
            "type": "ShopSlot",
            "slot_type": self.slot_type,
            "obj": self.obj.state,
            "turn": self.turn,
            "pack": self.pack,
            "cost": self.cost,
            "frozen": self.frozen,
            "seed_state": seed_state,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        slot_type = state["slot_type"]
        if state["obj"]["type"] == "Pet":
            item_cls = getattr(sapai.pets, "Pet")
        elif state["obj"]["type"] == "Food":
            item_cls = getattr(sapai.foods, "Food")
        elif state["obj"]["type"] == "ShopSlotNoneItem":
            item_cls = ShopSlotNoneItem
        else:
            raise Exception("Unrecognized item state")
        obj = item_cls.from_state(state["obj"])
        turn = state["turn"]
        pack = state["pack"]
        cost = state["cost"]
        frozen = state["frozen"]
        ### Supply seed_state in state dict should be optional
        if "seed_state" in state:
            seed_state = state["seed_state"]
        else:
            seed_state = None

        ### This should no longer be possible
        # obj.rs = np.random.RandomState()
        # if seed_state is not None:
        #     obj.rs.set_state(state["item"]["seed_state"])

        return cls(
            obj=obj,
            slot_type=slot_type,
            frozen=frozen,
            turn=turn,
            cost=cost,
            pack=pack,
            seed_state=seed_state,
        )


def get_shop_rules(turn, pack="StandardPack"):
    if pack == "StandardPack":
        turn_prob_pets = turn_prob_pets_std
        turn_prob_foods = turn_prob_foods_std
    elif pack == "ExpansionPack1":
        turn_prob_pets = turn_prob_pets_exp
        turn_prob_foods = turn_prob_foods_exp
    else:
        raise Exception(f"Pack {pack} not valid")

    if turn <= 0:
        raise Exception("Input turn must be greater than 0")

    ### Turn 11 is max shop info
    if turn > 11:
        turn = 11

    td = data["turns"][f"turn-{turn}"]
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

    return pslots, fslots, tier_avail, levelup_tier, avail_pets, avail_foods, pp, fp


# %%
