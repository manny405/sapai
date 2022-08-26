#%%
import numpy

from sapai.pets import Pet
from sapai.lists import Slot, SAPList


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
        slots=[],
        battle=False,
        shop=None,
        player=None,
        pack="StandardPack",
        seed_state=None,
    ):
        super().__init__(slots, 5, slot_class=TeamSlot)
        self._battle = battle
        self.seed_state = seed_state
        self.team = [TeamSlot(seed_state=self.seed_state) for x in range(self.nslots)]
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

    def move_backward(self):
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
            self.team[obj] = TeamSlot(seed_state=self.seed_state)
        elif type(obj).__name__ == "TeamSlot":
            found = False
            for iter_idx, temp_slot in enumerate(self.team):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("Remove {} not found".format(obj))
            self.team[found_idx] = TeamSlot(seed_state=self.seed_state)
        elif type(obj).__name__ == "Pet":
            found = False
            for iter_idx, temp_slot in enumerate(self.team):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("Remove {} not found".format(obj))
            self.team[found_idx] = TeamSlot(seed_state=self.seed_state)
        else:
            raise Exception("Object of type {} not recognized".format(type(obj)))

    def check_friend(self, obj):
        if type(obj).__name__ == "TeamSlot":
            found = False
            for iter_idx, temp_slot in enumerate(self.team):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            return found
        elif type(obj).__name__ == "Pet":
            found = False
            for iter_idx, temp_slot in enumerate(self.team):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            return found
        else:
            raise Exception("Object of type {} not recognized".format(type(obj)))

    def get_idx(self, obj):
        if type(obj).__name__ == "TeamSlot":
            found = False
            for iter_idx, temp_slot in enumerate(self.team):
                if temp_slot == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("get_idx {} not found".format(obj))
            return found_idx
        elif type(obj).__name__ == "Pet":
            found = False
            for iter_idx, temp_slot in enumerate(self.team):
                temp_pet = temp_slot.pet
                if temp_pet == obj:
                    found_idx = iter_idx
                    found = True
            if not found:
                raise Exception("get_idx {} not found".format(obj))
            return found_idx
        elif type(obj) == int:
            return obj
        elif type(obj).__name__ == "int64":
            ### For numpy int
            return obj
        elif type(obj).__name__ == "int32":
            ### For numpy int
            return obj
        else:
            raise Exception("Object of type {} not recognized".format(type(obj)))

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
                chosen.append(self.team[temp_idx])
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
        if n == len(self.team):
            raise Exception("Attempted to append to a full team")
        empty_idx = self.get_empty()
        if len(empty_idx) == 0:
            raise Exception("This should not be possible")
        self.team[empty_idx[0]] = obj

    def check_lvl3(self):
        for slot in self.team:
            if slot.empty:
                continue
            if slot.pet.level == 3:
                return True
        return False

    @property
    def battle(self):
        return self._battle

    def __iter__(self):
        yield from self.team

    def __len__(self):
        count = 0
        for temp_slot in self.team:
            if not temp_slot.empty:
                count += 1
        return count

    def __getitem__(self, idx):
        return self.team[idx]

    def __setitem__(self, idx, obj):
        if type(obj).__name__ == "Pet":
            self.team[idx] = TeamSlot(obj, seed_state=self.seed_state)
        elif type(obj).__name__ == "TeamSlot":
            self.team[idx] = obj
        elif type(obj) == str or type(obj) == numpy.str_:
            self.team[idx] = TeamSlot(obj, seed_state=self.seed_state)
        else:
            raise Exception(
                "Tried setting a team slot with type {}".format(type(obj).__name__)
            )

    def __repr__(self):
        repr_str = ""
        for iter_idx, slot in enumerate(self.team):
            repr_str += "{}: {} \n    ".format(iter_idx, slot)
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
            "team": [x.state for x in self.team],
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
        self.seed_state = seed_state
        if type(obj).__name__ == "Pet":
            self.obj = obj
        elif type(obj).__name__ == "TeamSlot":
            self.obj = obj.pet
        elif type(obj).__name__ == "NoneType":
            self.obj = Pet(seed_state=self.seed_state)
        elif type(obj) == str or type(obj) == numpy.str_:
            self.obj = Pet(obj, seed_state=self.seed_state)
        else:
            raise Exception(
                "Tried initalizing TeamSlot with type {}".format(type(obj).__name__)
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
            return "< Slot {} >".format(pet_repr)

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
