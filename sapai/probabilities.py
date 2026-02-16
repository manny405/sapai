def get_pack_names(data):
    packs = set()
    for group in ("pets", "foods"):
        for entry in data[group].values():
            for pack in entry.get("packs", []):
                packs.add(pack)
    return tuple(packs)


def _turn_numbers(data):
    turns = []
    for key in data["turns"]:
        if not key.startswith("turn-"):
            raise ValueError(f"Invalid turns key '{key}'. Expected format 'turn-N'.")
        turn_token = key.split("-")[-1]
        if not turn_token.isdigit():
            raise ValueError(f"Invalid turn number in key '{key}'. Expected 'turn-N'.")
        turns.append(int(turn_token))
    return sorted(turns)


def _count_shop_entries(data, group, pack, tier_limit):
    count = 0
    for entry in data[group].values():
        if not isinstance(entry.get("tier"), int):
            continue
        if entry["tier"] > tier_limit:
            continue
        if pack not in entry.get("packs", []):
            continue
        count += 1
    return count


def generate_probabilities(data):
    turns = _turn_numbers(data)
    pack_names = get_pack_names(data)
    group_configs = (
        ("pets", "animalShopSlots", "pet"),
        ("foods", "foodShopSlots", "food"),
    )

    shop_counts = {group: {pack: {} for pack in pack_names} for group, _, _ in group_configs}
    for turn in turns:
        tiers_available = data["turns"][f"turn-{turn}"]["tiersAvailable"]
        for group, _, _ in group_configs:
            for pack in pack_names:
                shop_counts[group][pack][turn] = _count_shop_entries(
                    data, group, pack, tiers_available
                )

    for group, slots_key, label in group_configs:
        for entry in data[group].values():
            if not isinstance(entry.get("tier"), int):
                entry["probabilities"] = "none"
                continue

            probabilities = []
            for turn in turns:
                turn_data = data["turns"][f"turn-{turn}"]
                per_slot = {}
                per_shop = {}
                if entry["tier"] <= turn_data["tiersAvailable"]:
                    for pack in pack_names:
                        if pack not in entry.get("packs", []):
                            continue
                        count = shop_counts[group][pack][turn]
                        if count <= 0:
                            raise ValueError(
                                f"Invalid {label} shop count for pack={pack}, turn={turn}, "
                                f"entry={entry.get('id', '<unknown>')}: {count}"
                            )
                        slot_prob = 1 / count
                        per_slot[pack] = slot_prob
                        per_shop[pack] = 1 - (1 - slot_prob) ** turn_data[slots_key]
                if per_slot:
                    probabilities.append(
                        {
                            "kind": "shop",
                            "turn": f"turn-{turn}",
                            "perShop": per_shop,
                            "perSlot": per_slot,
                        }
                    )

            entry["probabilities"] = probabilities or "none"
