# %%

import json, zlib
import sapai


def compress(obj, minimal=False):
    """
    Will compress objects such that they can be stored and searched by a single
    string. This makes storage and quering of teams naively simple.

    """
    state = getattr(obj, "state", False)
    if not state:
        raise Exception(f"No state method found for obj {obj}")
    if minimal:
        state = minimal_state(obj)
    json_str = json.dumps(state)
    compressed_str = zlib.compress(json_str.encode())
    return compressed_str


def decompress(compressed_str):
    """
    Decompress the given encoded str into an object

    """
    state_str = zlib.decompress(compressed_str).decode()
    state_dict = json.loads(state_str)
    return state2obj(state_dict)


def state2obj(state):
    obj_type = state["type"]
    obj_cls = getattr(sapai, obj_type)
    obj = obj_cls.from_state(state)
    return obj


def sapai_hash(obj):
    """
    Fast method for hashing the object

    """
    state = getattr(obj, "state", False)
    if not state:
        raise Exception(f"No state found for obj {obj}")
    raise Exception("I can't find faster way to do this... But it would be very nice.")


def minimal_state(obj):
    """
    Including the seed_state from food/pets and including the action history from
    player creates a 10 times increase in the compressed byte size. In many
    situations it is advantageous to create a minimal state for only the team
    stats and current shop pets. This will save memory/storage and improve
    computational efficiency.

    """
    state = obj.state

    def minimal_pet_state(state):
        if "seed_state" in state:
            del state["seed_state"]

    def minimal_team_state(state):
        for teamslot_state in state["team"]:
            minimal_pet_state(teamslot_state["pet"])

    def minimal_shop_state(state):
        if "seed_state" in state:
            del state["seed_state"]
        for shopslot_state in state["slots"]:
            if "seed_state" in shopslot_state:
                del shopslot_state["seed_state"]
            minimal_pet_state(shopslot_state["obj"])

    def minimal_player_state(state):
        if "seed_state" in state:
            del state["seed_state"]
        if "action_history" in state:
            del state["action_history"]
        minimal_team_state(state["team"])
        minimal_shop_state(state["shop"])

    if state["type"] == "Pet":
        minimal_pet_state(state)
    elif state["type"] == "Food":
        minimal_pet_state(state)
    elif state["type"] == "Team":
        minimal_team_state(state)
    elif state["type"] == "Shop":
        minimal_shop_state(state)
    elif state["type"] == "Player":
        minimal_player_state(state)
    else:
        raise Exception(f"Unrecognized state type {state['type']}")

    return state


# %%
