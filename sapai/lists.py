from functools import partial
from collections.abc import Iterable
import numpy as np


class Slot:
    """
    Implements basic behavior of a slot in a SAPList

    """

    def __init__(self, obj=None):
        if isinstance(obj, Slot):
            obj = obj.obj
        self.obj = obj

    def __repr__(self):
        if self.obj is None:
            name = "EMPTY"
        elif self.obj.name == "pet-none" or self.obj.name == "food-none":
            name = "EMPTY"
        else:
            name = str(self._obj)[2:-2]
        return f"< Slot {name} >"

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, obj):
        if obj is not None:
            if isinstance(obj, type(self)):
                obj = obj.obj
            if (
                not hasattr(obj, "state")
                or not hasattr(obj, "from_state")
                or not hasattr(obj, "name")
            ):
                raise Exception(
                    f"Input object {obj} must have a name, a state method, and a from_state method"
                )
        self._obj = obj

    @property
    def empty(self):
        """
        Returns if the given slot is empty
        """
        return self._obj is None

    @obj.deleter
    def obj(self):
        del self.obj
        self._obj = None

    @property
    def state(self):
        ### seed_state doesn't need to be stored for TeamSlot because the
        ###   seed_state is stored by pets
        state_dict = {
            "type": "Slot",
        }
        if not self.empty:
            state_dict["obj"] = self.obj.state
        return state_dict

    @classmethod
    def from_state(cls, state):
        from sapai.compress import state2obj

        if "obj" in state:
            obj = state2obj(state["obj"])
        return cls(obj)


class SAPList:
    """
    Implements required methods and behaviors for lists of slots for SAP

    """

    def __init__(self, slots=None, nslots=None, slot_class=Slot):
        slots = slots or []

        self.slot_class = slot_class
        self._slots = []
        self._nslots = None
        self.slots = slots
        if nslots is not None:
            self.nslots = nslots

    def __len__(self):
        """
        Returns the number of filled slots
        """
        return len(self.slots)

    def __iter__(self):
        yield from self.slots

    def __getitem__(self, idx):
        return self.slots[idx]

    def __setitem__(self, idx, obj):
        if isinstance(obj, Iterable):
            for i, temp_idx in enumerate(idx):
                self._slots[temp_idx] = Slot(obj[i])
        elif isinstance(idx, (int, np.integer)):
            self._slots[idx] = Slot(obj)
        else:
            raise Exception(f"Index provided must be int, given {type(idx)}")

    def __repr__(self):
        repr_str = ""
        for iter_idx, slot in enumerate(self.slots):
            repr_str += f"{iter_idx}: {slot} \n    "
        return repr_str

    @property
    def slots(self):
        return self._slots

    @slots.setter
    def slots(self, objs):
        if isinstance(self.slot_class, partial):
            test_type = self.slot_class.func
        else:
            test_type = self.slot_class
        if isinstance(objs, Iterable):
            temp_slots = []
            for obj in objs:
                if not isinstance(obj, test_type):
                    temp_slots.append(self.slot_class(obj))
                else:
                    temp_slots.append(obj)
            self._slots = temp_slots
        else:
            temp_slots = []
            if not isinstance(objs, test_type):
                temp_slots.append(self.slot_class(objs))
            else:
                temp_slots.append(objs)
            self._slots = temp_slots
        if self.nslots is not None:
            self.nslots = self._nslots

    @property
    def nslots(self):
        """
        Number of slots in the slotlist
        """
        return self._nslots

    @nslots.setter
    def nslots(self, length):
        """
        Sets nslots and confirms the number of Slots in _slots
        """
        self._nslots = length
        if self._nslots is None:
            return
        if not isinstance(length, (int, np.integer)):
            raise Exception(f"SAPList nslots must be int, given {type(length)}")
        if length < 0:
            raise Exception(f"SAPList nslots must be 0 or greater, given {length}")
        self._nslots = int(self._nslots)
        if len(self._slots) < self.nslots:
            [
                self._slots.append(self.slot_class())
                for _ in range(self.nslots - len(self._slots))
            ]
        elif len(self._slots) > self.nslots:
            self._slots = self._slots[: self.nslots]

    @property
    def left(self):
        return self._slots[0]

    @property
    def right(self):
        return self._slots[-1]

    @property
    def leftmost(self):
        """
        Returns leftmost slot that is not empty
        """
        ret = None
        idx = None
        for i, slot in enumerate(self):
            if slot.empty:
                continue
            ret = slot
            idx = i
            break
        return ret, idx

    @property
    def rightmost(self):
        """
        Returns rightmost slot that is not empty
        """
        ret = None
        for i, slot in enumerate(self[::-1]):
            if slot.empty:
                continue
            ret = slot
            idx = len(self) - 1 - i
            break
        return ret, idx

    @property
    def empty(self):
        """
        Return the indices of empty slots
        """
        idx = []
        for i, temp_slot in enumerate(self.slots):
            if temp_slot.empty:
                idx.append(i)
        return idx

    @property
    def filled(self):
        """
        Return the indices of non-empty slots
        """
        idx = []
        for i, temp_slot in enumerate(self.slots):
            if not temp_slot.empty:
                idx.append(i)
        return idx

    def get_left(self, n=1):
        """
        Return the n left-most slots
        """
        return self._slots[:n]

    def get_right(self, n=1):
        """
        Return the n right-most slots
        """
        return self._slots[::-1][:n]

    def move(self, sidx, tidx):
        """
        Move object from start idx to target idx
        """
        target = self[tidx]
        if not target.empty:
            raise Exception("Attempted move to a populated position")
        self[tidx] = self[sidx]
        ### Dereference original position
        self[sidx] = self.slot_class()

    def move_right(self):
        """
        Move all entries in SlotList after index i to the right
        """
        self.move_backward()

    def move_left(self, sidx=0, eidx=-1):
        """
        Move all entires in SlotList after index i to the left
        """
        self.move_forward(sidx, eidx)

    def move_forward(self, sidx=0, eidx=-1):
        """
        Adjust the location of the pets in the team, moving them as far forward
        as sidx from eidx using a recursive function.

        """
        if eidx == -1:
            eidx = len(self)
        if sidx >= eidx:
            raise Exception(f"End idx {sidx} must be greater than start idx {eidx}")

        empty_idx = [x for x in self.empty if x >= sidx and x <= eidx]
        filled_idx = [x for x in self.filled if x > sidx and x <= eidx]

        if len(empty_idx) > 0:
            ### Only need to consider the first empty position
            empty_idx = empty_idx[0]

            ### Find first pet that can fill this empty position
            found = False
            for temp_idx in filled_idx:
                if empty_idx < temp_idx:
                    found = True
                    ### Move pet
                    self.move(temp_idx, empty_idx)
                    break

            ### If a pet was moved, call recurisvely
            if found:
                self.move_forward(sidx, eidx)

        return

    def move_backward(self, sidx=0, eidx=-1):
        """
        Adjust the location of the pets in the team, moving them to the furthest
        possible backward location using a recursive function.

        """
        if eidx == -1:
            eidx = len(self)
        if sidx >= eidx:
            raise Exception(f"End idx {sidx} must be greater than start idx {eidx}")

        empty_idx = [x for x in self.empty if x > sidx and x <= eidx]
        filled_idx = [x for x in self.filled if x >= sidx and x <= eidx]

        if len(empty_idx) > 0:
            ### Only need to consider the last empty position
            empty_idx = empty_idx[-1]

            ### Find first pet that can fill this empty position
            found = False
            for temp_idx in filled_idx[::-1]:
                if empty_idx > temp_idx:
                    found = True
                    ### Move pet
                    self.move(temp_idx, empty_idx)
                    break

            ### If a pet was moved, call recurisvely
            if found:
                self.move_backward(sidx, eidx)

        return

    def get_index(self, obj):
        """
        Return the index of an input slot or item
        """
        found_idx = None
        if isinstance(obj, Slot):
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot == obj:
                    found_idx = iter_idx
        else:
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot.obj == obj:
                    found_idx = iter_idx
        return found_idx

    def remove(self, obj):
        """
        Remove by slot, item, or index from SAPList
        """
        found = False
        if isinstance(obj, (int, np.integer)):
            self.slots[obj] = self.slot_class()
            found = True
        elif isinstance(obj, Slot):
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot == obj:
                    self.slots[iter_idx] = self.slot_class()
                    found = True
                    break
        else:
            for iter_idx, temp_slot in enumerate(self.slots):
                if temp_slot.obj == obj:
                    self.slots[iter_idx] = self.slot_class()
                    found = True
                    break

        if not found:
            raise Exception(f"Object {obj} not found in SAPList {self}")

    def get_behind(self, obj, n=1):
        """
        Return the n slots behind the given object
        """
        if isinstance(obj, (int, np.integer)):
            idx = obj
        else:
            idx = self.get_index(obj)

        return self.slots[idx + 1 : idx + n + 1]

    def get_infront(self, obj, n=1):
        """
        Return the n slots infront of the given object
        """
        if isinstance(obj, (int, np.integer)):
            idx = obj
        else:
            idx = self.get_index(obj)

        start_idx = max(idx - n, 0)
        end_idx = idx
        return self.slots[start_idx:end_idx][::-1]

    def append(self, obj):
        """
        Adds object to first open slot
        """
        if len(self.empty) > 0:
            self.slots[self.empty[0]] = Slot(obj)
        else:
            raise Exception("Attempted to append to full SAPList")

    @property
    def state(self):
        """
        Return the state defining the current slotlist
        """
        state_dict = {
            "type": "SAPList",
            "nslots": self.nslots,
            "slots": [x.state for x in self.slots],
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        """
        Build a SlotList from the given state dictionary
        """
        from sapai.compress import state2obj

        slots = [state2obj(x) for x in state["slots"]]
        return cls(slots, nslots=state["nslots"])
