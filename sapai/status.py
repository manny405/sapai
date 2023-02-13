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
    raise NotImplementedError


def apply_extra_life(pet, team):
    raise NotImplementedError


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
