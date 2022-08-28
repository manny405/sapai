from sapai.data import data


def apply_(value):
    return max([value, 0])


def apply_garlic_armor(value):
    if value > 0:
        return max([value - 2, 1])
    else:
        return 0


def apply_melon_armor(value):
    return max([value - 20, 0])


def apply_coconut_shield(value):
    return 0


def apply_bone_attack(value):
    if value > 0:
        return value + 4
    else:
        return 0


def apply_steak_attack(value):
    if value > 0:
        return value + 20
    else:
        return 0


def apply_weak(value):
    if value > 0:
        return value + 3
    else:
        return 0


def apply_poison_attack(value):
    if value > 0:
        return 1000
    else:
        return 0


def apply_splash_attack(value):
    return apply_(value)


def apply_honey_bee(pet, team):
    raise Exception("Not implemented")


def apply_extra_life(pet, team):
    raise Exception("Not implemented")


def apply_faint_status_trigger(faint_trigger_fn):
    def faint_status_trigger(self, trigger, te_idx, oteam):
        activated, targets, possible = faint_trigger_fn(self, trigger, te_idx, oteam)

        ### If pet itself has not fainted, status is not activated
        if trigger != self:
            return activated, targets, possible

        ### Check status
        if self.status in ["status-honey-bee", "status-extra-life"]:
            ### It's not good that this has to be moved outside of this function
            ###   because that's ugly way to do it. But if it works for now then
            ###   can clean up later with good testing suite.
            # original_ability = self.ability
            # ability = data["statuses"][self.status]["ability"]
            # self.set_ability(ability)
            # status_activated, status_targets, status_possible = faint_trigger_fn(
            #     self, trigger, te_idx, oteam
            # )
            # return (
            #     status_activated,
            #     targets + status_targets,
            #     possible + status_possible,
            # )
            ### Return that this pet has a status that needs to be activated
            ###   after fainting
            return activated, targets, possible, True
        else:
            return activated, targets, possible, False

    return faint_status_trigger


apply_null_dict = {
    "none": apply_,
    "status-bone-attack": apply_,
    "status-coconut-shield": apply_,
    "status-extra-life": apply_,
    "status-garlic-armor": apply_,
    "status-honey-bee": apply_,
    "status-melon-armor": apply_,
    "status-poison-attack": apply_,
    "status-splash-attack": apply_,
    "status-steak-attack": apply_,
    "status-weak": apply_,
}

apply_damage_dict = {
    "none": apply_,
    "status-bone-attack": apply_,
    "status-coconut-shield": apply_coconut_shield,
    "status-extra-life": apply_,
    "status-garlic-armor": apply_garlic_armor,
    "status-honey-bee": apply_,
    "status-melon-armor": apply_melon_armor,
    "status-poison-attack": apply_,
    "status-splash-attack": apply_,
    "status-steak-attack": apply_,
    "status-weak": apply_weak,
}

apply_attack_dict = {
    "none": apply_,
    "status-bone-attack": apply_bone_attack,
    "status-coconut-shield": apply_,
    "status-extra-life": apply_,
    "status-garlic-armor": apply_,
    "status-honey-bee": apply_,
    "status-melon-armor": apply_,
    "status-poison-attack": apply_poison_attack,
    "status-splash-attack": apply_splash_attack,
    "status-steak-attack": apply_steak_attack,
    "status-weak": apply_,
}

apply_faint_dict = {
    "none": apply_,
    "status-bone-attack": apply_,
    "status-coconut-shield": apply_,
    "status-extra-life": apply_extra_life,
    "status-garlic-armor": apply_,
    "status-honey-bee": apply_honey_bee,
    "status-melon-armor": apply_,
    "status-poison-attack": apply_,
    "status-splash-attack": apply_,
    "status-steak-attack": apply_,
    "status-weak": apply_,
}

apply_once = {
    "status-coconut-shield",
    "status-melon-armor",
    "status-steak-attack",
}
