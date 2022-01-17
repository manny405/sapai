

#%%

import json,zlib
import sapai


def compress(obj):
    """
    Will compress objects such that they can be stored and searched by a single
    string. This makes storage and quering of teams naively simple.

    """
    state = getattr(obj, "state", False)
    if not state:
        raise Exception("No state found for obj {}".format(obj))
    json_str = json.dumps(state)
    compressed_str = zlib.compress(json_str.encode())
    return compressed_str
    
    
def decompress(compressed_str):
    """
    Decompress the given encoded str into an object
    
    """
    state_str = zlib.decompress(compressed_str).decode()
    state_dict = json.loads(state_str)
    obj_type = state_dict["type"]
    obj_cls = getattr(sapai, obj_type)
    obj = obj_cls.from_state(state_dict)
    return obj





#%%
        