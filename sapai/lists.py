class SAPList:
    """
    Implements required methods and behaviors for lists of slots for SAP

    """

    def __init__(self, items=[], nslots=None):
        self._slots = []
        for item in items:
            self._slots.append(Slot(item))
        if nslots == None:
            self._nslots = nslots

    def __len__(self):
        """
        Returns the number of filled slots in the slotlist
        """
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

    @property
    def nslots(self):
        """
        Number of slots in the slotlist
        """
        return self._nslots

    @property
    def slots(self):
        return self._slots

    @property
    def left(self):
        return self._slots[0]

    @property
    def right(self):
        return self._slots[-1]

    @property
    def emtpy(self):
        """
        Return the indices of empty slots
        """

    @property
    def state(self):
        """
        Return the state defining the current slotlist
        """

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

    def move_right(self, i=0):
        """
        Move all entries in SlotList after index i to the right
        """

    def move_left(self, i=-1):
        """
        Move all entires in SlotList after index i to the left
        """

    def remove(self, obj):
        """
        Remove slot or item from SlotList
        """

    def index(self, obj):
        """
        Return the index of an input slot or item
        """

    def behind(self, obj, n=1):
        """
        Return the n slots behind the given object
        """

    def front(self, obj, n=1):
        """
        Return the n slots infront of the given object
        """

    def append(self, obj):
        """
        Appent to slotlist, default behavior is not to allow this operation
        """
        raise Exception(f"Append is not allowed for {self.__name__}")

    @classmethod
    def from_state(cls, state):
        """
        Build a SlotList from the given state dictionary
        """


class Slot:
    """
    Implements basic behavior of a slot in a list in SAP

    """

    def __init__(self, item=None):
        self._item = item

    @property
    def item(self):
        return self._item

    @property
    def empty(self):
        """
        Returns if the given slot is empty
        """


class EmptySlot(Slot):
    """
    Special class for an emtpy slot
    """
