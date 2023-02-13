# %%
import numpy as np

from sapai.data import data
from sapai.rand import MockRandomState

# %%


class Food:
    def __init__(self, name="food-none", shop=None, seed_state=None):
        """
        Food class definition the types of interactions that food undergoes

        """
        if len(name) != 0:
            if not name.startswith("food-"):
                name = f"food-{name}"

        self.eaten = False
        self.shop = shop

        self.seed_state = seed_state
        if self.seed_state is not None:
            self.rs = np.random.RandomState()
            self.rs.set_state(self.seed_state)
        else:
            ### Otherwise, set use
            self.rs = MockRandomState()

        self.attack = 0
        self.health = 0
        self.base_attack = 0
        self.base_health = 0
        self.apply_until_end_of_battle = False
        self.status = "none"
        self.effect = "none"
        self.fd = {}

        self.name = name
        if name not in data["foods"]:
            raise Exception(f"Food {name} not found")

        self.cost = 3
        item = data["foods"][name]
        if "cost" in item:
            self.cost = item["cost"]

        fd = item["ability"]
        self.fd = fd

        self.attack = 0
        self.health = 0
        self.effect = fd["effect"]
        if "attackAmount" in fd["effect"]:
            self.attack = fd["effect"]["attackAmount"]
            self.base_attack = fd["effect"]["attackAmount"]
        if "healthAmount" in fd["effect"]:
            self.health = fd["effect"]["healthAmount"]
            self.base_health = fd["effect"]["healthAmount"]
        if "status" in fd["effect"]:
            self.status = fd["effect"]["status"]
        if (
            "untilEndOfBattle" in fd["effect"]
            and fd["effect"]["untilEndOfBattle"] is True
        ):
            self.apply_until_end_of_battle = True

    def copy(self):
        copy_food = Food(self.name, self.shop)
        for key, value in self.__dict__.items():
            ### Although this approach will copy the internal dictionaries by
            ###   reference rather than copy by value, these dictionaries will
            ###   never be modified anyways.
            ### All integers and strings are copied by value automatically with
            ###   Python, therefore, this achieves the correct behavior
            copy_food.__dict__[key] = value
        return copy_food

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
            "type": "Food",
            "name": self.name,
            "eaten": self.eaten,
            "attack": self.attack,
            "health": self.health,
            "apply_until_end_of_battle": self.apply_until_end_of_battle,
            "seed_state": seed_state,
        }
        return state_dict

    @classmethod
    def from_state(cls, state):
        food = cls(name=state["name"])
        food.attack = state["attack"]
        food.health = state["health"]
        food.eaten = state["eaten"]
        food.apply_until_end_of_battle = state["apply_until_end_of_battle"]
        ### Supply seed_state in state dict should be optional
        if "seed_state" in state:
            if state["seed_state"] is not None:
                food.seed_state = state["seed_state"]
                food.rs = np.random.RandomState()
                food.rs.set_state(state["seed_state"])
        return food

    def __repr__(self):
        return f"< {self.name} {self.attack}-{self.health} {self.status} >"


# %%
