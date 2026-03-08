import unittest

from sapai.data import data
from sapai.probabilities import get_pack_names


class TestProbabilitiesGeneration(unittest.TestCase):
    packs = get_pack_names(data)
    groups = (("pets", "animalShopSlots"), ("foods", "foodShopSlots"))

    def _count_shop(self, group, pack, turn):
        tier_limit = data["turns"][f"turn-{turn}"]["tiersAvailable"]
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

    def test_non_shop_entries_use_none_probabilities(self):
        for group, _ in self.groups:
            for entry in data[group].values():
                if isinstance(entry.get("tier"), int):
                    continue
                self.assertEqual(entry.get("probabilities"), "none")

    def test_shop_probabilities_match_generated_counts(self):
        for group, slots_key in self.groups:
            for entry in data[group].values():
                probs = entry.get("probabilities")
                if probs == "none":
                    continue
                for prob in probs:
                    self.assertEqual(prob["kind"], "shop")
                    turn = int(prob["turn"].split("-")[-1])
                    slots = data["turns"][f"turn-{turn}"][slots_key]
                    for pack, per_slot in prob["perSlot"].items():
                        expected_slot = 1 / self._count_shop(group, pack, turn)
                        self.assertAlmostEqual(per_slot, expected_slot)
                        expected_shop = 1 - (1 - expected_slot) ** slots
                        self.assertAlmostEqual(prob["perShop"][pack], expected_shop)

    def test_probabilities_have_known_pack_keys(self):
        for group, _ in self.groups:
            for entry in data[group].values():
                probs = entry.get("probabilities")
                if probs == "none":
                    continue
                for prob in probs:
                    for pack in prob.get("perSlot", {}):
                        self.assertIn(pack, self.packs)
                    for pack in prob.get("perShop", {}):
                        self.assertIn(pack, self.packs)
