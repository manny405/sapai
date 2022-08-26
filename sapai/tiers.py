import numpy as np
from sapai.data import data


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
