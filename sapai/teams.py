# %%
import numpy

from sapai.pets import Pet
from sapai.lists import Slot, SAPList
from numpy import int32, int64


class Team(SAPList):
    """
    Defines a team class.

    What should be included here that won't be included in just a list of
    animals? idk...

    Maybe including interaction between animals. For example, Tiger. Are there
    any other interactions?

    """

    def __init__(
        self,
        slots=None,
        battle=False,
        shop=None,
        player=None,
        pack="StandardPack",
        seed_state=None,
    ):
        slots = slots or []

        super().__init__(slots, 5, slot_class=TeamSlot)
        self._battle = battle
        self.seed_state = seed_state
        self.slots = [TeamSlot(seed_state=self.seed_state) for _ in range(self.nslots)]
        for iter_idx, obj in enumerate(slots):
            self[iter_idx] = obj
            self[iter_idx]._pet.team = self
        self.player = player
        self.shop = shop
        self.pack = "StandardPack"

    def move(self, sidx, tidx):
        """Moves animal from start idx to target idx"""
        target = self[tidx]
        if not target.empty:
            raise Exception("Attempted move to a populated position")
        ### Move
        self[tidx] = self[sidx]
        ### Dereference original position
        self[sidx] = TeamSlot(seed_state=self.seed_state)

    def move_forward(self, start_idx=0, end_idx=10):
        """
        Adjust the location of the pets in the team, moving them to the furthest
        possible forward location using a recursive function. The arg idx may
        be provided to indicate the first index that is allowed to move
        forward.

        """
        empty_idx = []
        filled_idx = []
        for iter_idx, slot in enumerate(self):
            if slot.empty:
                empty_idx.append(iter_idx)
            else:
                filled_idx.append(iter_idx)
        if len(empty_idx) > 0:
            ### Only need to consider the first empty position
            empty_idx = empty_idx[0]

            ### Find first pet that can fill this empty position
            found = False
            for temp_idx in filled_idx:
                if temp_idx < start_idx:
                    continue
                if temp_idx >= end_idx:
                    continue
                if empty_idx < temp_idx:
                    found = True
                    ### Move pet
                    self.move(temp_idx, empty_idx)
                    break

            ### If a pet was moved, call recurisvely
            if found:
                self.move_forward(start_idx, end_idx)

        return

    def move_backward(self, **kwargs):
        """
        Adjust the location of the pets in the team, moving them to the furthest
        possible backward location using a recursive function.

        This is useful for summoning purposes

        """
        empty_idx = []
        filled_idx = []
        for iter_idx, slot in enumerate(self):
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
                    self.move(start_idx, empty_idx)
                    break

            ### If a pet was moved, call recurisvely
            if found:
                self.move_backward()

        return

    def remove(self, obj):
        if type(obj) == int:
            self.slots[obj] = TeamSlot(seed_state=self.seed_state)
        elif isinstance(obj, TeamSlot):
            found = False
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception(f"Remove {obj} not found")
            self.slots[found_idx] = TeamSlot(seed_state=self.seed_state)
        elif isinstance(obj, Pet):
            found = False
            for iter_idx, temp_slot in enumerate(self.slots):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception(f"Remove {obj} not found")
            self.slots[found_idx] = TeamSlot(seed_state=self.seed_state)
        else:
            raise Exception(f"Object of type {type(obj)} not recognized")

    def check_friend(self, obj):
        if isinstance(obj, TeamSlot):
            found = False
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot == obj:
                    found = True
            return found
        elif isinstance(obj, Pet):
            found = False
            for iter_idx, temp_slot in enumerate(self.slots):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found = True
            return found
        else:
            raise Exception(f"Object of type {type(obj)} not recognized")

    def get_idx(self, obj):
        if isinstance(obj, TeamSlot):
            found = False
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception(f"get_idx {obj} not found")
            return found_idx
        elif isinstance(obj, Pet):
            found = False
            for iter_idx, temp_slot in enumerate(self.slots):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception(f"get_idx {obj} not found")
            return found_idx
        elif type(obj) == int:
            return obj
        elif isinstance(obj, int64):
            ### For numpy int
            return obj
        elif isinstance(obj, int32):
            ### For numpy int
            return obj
        else:
            raise Exception(f"Object of type {type(obj)} not recognized")

    def index(self, obj):
        return self.get_idx(obj)

    def get_fidx(self):
        ### Get possible indices for each team
        fidx = []
        for iter_idx, temp_slot in enumerate(self):
            if not temp_slot.empty:
                ### Skiped if health is less than 0
                if temp_slot.pet.health > 0:
                    fidx.append(iter_idx)
        return fidx

    def get_ahead(self, obj, n=1):
        pet_idx = self.get_idx(obj)
        fidx = []
        for iter_idx, temp_slot in enumerate(self):
            if not temp_slot.empty:
                fidx.append(iter_idx)
        chosen_idx = []
        for temp_idx in fidx:
            if temp_idx < pet_idx:
                chosen_idx.append(temp_idx)
        ret_pets = []
        for temp_idx in chosen_idx[::-1]:
            ret_pets.append(self[temp_idx].pet)
            if len(ret_pets) >= n:
                break
        return ret_pets

    def get_behind(self, obj, n=1):
        pet_idx = self.get_idx(obj)
        fidx = []
        for iter_idx, temp_slot in enumerate(self):
            if not temp_slot.empty:
                fidx.append(iter_idx)
        chosen = []
        for temp_idx in fidx:
            if temp_idx > pet_idx:
                chosen.append(self.slots[temp_idx])
        return chosen[0:n]

    def get_empty(self):
        empty_idx = []
        for iter_idx, temp_slot in enumerate(self):
            if temp_slot.empty:
                empty_idx.append(iter_idx)
        return empty_idx

    def append(self, obj):
        obj = TeamSlot(obj, seed_state=self.seed_state)
        n = len(self)
        if n == len(self.slots):
            raise Exception("Attempted to append to a full team")
        empty_idx = self.get_empty()
        if len(empty_idx) == 0:
            raise Exception("This should not be possible")
        self.slots[empty_idx[0]] = obj

    def check_lvl3(self):
        for slot in self.slots:
            if slot.empty:
                continue
            if slot.pet.level == 3:
                return True
        return False

    @property
    def battle(self):
        return self._battle

    def __iter__(self):
        yield from self.slots

    def __len__(self):
        count = 0
        for temp_slot in self.slots:
            if not temp_slot.empty:
                count += 1
        return count

    def __getitem__(self, idx):
        return self.slots[idx]

    def __setitem__(self, idx, obj):
        if isinstance(obj, Pet):
            self.slots[idx] = TeamSlot(obj, seed_state=self.seed_state)
        elif isinstance(obj, TeamSlot):
            self.slots[idx] = obj
        elif type(obj) == str or type(obj) == numpy.str_:
            self.slots[idx] = TeamSlot(obj, seed_state=self.seed_state)
        else:
            raise Exception(f"Tried setting a team slot with type {type(obj).__name__}")

    def __repr__(self):
        repr_str = ""
        for iter_idx, slot in enumerate(self.slots):
            repr_str += f"{iter_idx}: {slot} \n    "
        return repr_str

    def copy(self):
        return Team(
            [x.copy() for x in self],
            self.battle,
            self.player,
            seed_state=self.seed_state,
        )

    @property
    def state(self):
        ### seed_state doesn't need to be stored for Team because the seed_state
        ###   is stored by pets
        state_dict = {
            "type": "Team",
            "battle": self.battle,
            "team": [x.state for x in self.slots],
            "pack": self.pack,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        team = [TeamSlot.from_state(x) for x in state["team"]]
        return cls(
            slots=team,
            battle=state["battle"],
            shop=None,
            player=None,
            pack=state["pack"],
        )


class TeamSlot(Slot):
    def __init__(self, obj=None, seed_state=None):
        super().__init__()
        self.seed_state = seed_state
        if isinstance(obj, Pet):
            self.obj = obj
        elif isinstance(obj, TeamSlot):
            self.obj = obj.pet
        elif obj is None:
            self.obj = Pet(seed_state=self.seed_state)
        elif type(obj) == str or type(obj) == numpy.str_:
            self.obj = Pet(obj, seed_state=self.seed_state)
        else:
            raise Exception(
                f"Tried initalizing TeamSlot with type {type(obj).__name__}"
            )

    @property
    def _pet(self):
        return self._obj

    @property
    def pet(self):
        return self.obj

    @property
    def empty(self):
        return self.obj.name == "pet-none"

    @property
    def attack(self):
        return self.obj.attack

    @property
    def health(self):
        return self.obj.health

    @property
    def ability(self):
        return self.obj.ability

    @property
    def level(self):
        return self.obj.level

    def __repr__(self):
        if self.obj.name == "pet-none":
            return "< Slot EMPTY >"
        else:
            pet_repr = str(self.obj)
            pet_repr = pet_repr[2:-2]
            return f"< Slot {pet_repr} >"

    def copy(self):
        return TeamSlot(self.obj.copy(), seed_state=self.seed_state)

    @property
    def state(self):
        ### seed_state doesn't need to be stored for TeamSlot because the
        ###   seed_state is stored by pets
        state_dict = {
            "type": "TeamSlot",
            "pet": self.obj.state,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        pet = Pet.from_state(state["pet"])
        return cls(pet)


# %%
