import copy
import numpy as np

from sapai.data import data
from sapai.pets import Pet
from sapai.teams import Team
from sapai.effects import (
    get_effect_function,
    get_pet,
    get_teams,
    RespawnPet,
    SummonPet,
    SummonRandomPet,
)
from sapai import status


class Battle:
    """
    Performs a battle.

    Most important thing here to implement is the action queue including the
    logic for when actions should be removed from the action queue upon death.

    Note that effects are performed in the order of highest attack to lowest
    attack. If there is a tie, then health values are compared. If there is a
    tie then a random animal is chosen first. This is tracked by the
    pet_priority which is updated before every turn of the battle.

    Any effect which is in the queue for a given turn is executed, even if the
    animal dies due to preceeding effect, as the game entails.

    A Battle goes as follows:
        1. execute start-of-turn abilities according to pet priority
        2. perform hurt and faint abilities according to pet priority
                2.1 Execute 2 until there are no new fainted animals
        3. before-attack abilities according to pet priority
        4. perform fainted pet abilities via pet priority
                4.1 Execute 4 until there are no new fainted animals
        5. attack phase
            5.0 perform before_attack abilities
            5.1. perform hurt and fainted abilities according to pet priority
                   5.1.1 Execute 5.1 until there are no new fainted animals
            5.2 perform attack damage
            5.3 perform after attack abilities
            5.4 perform hurt and fainted abilities according to pet priority
                   5.4.1 Execute 5.4 until there are no new fainted animals
            5.5. check if knock-out abilities should be performed
                    5.5.1 if knock-out ability activated jump to 5.5
            5.6. if battle has not ended, jump to 5.0

    """

    def __init__(self, t0, t1):
        """
        Performs the battle between the input teams t1 and t2.

        """
        ### Make copy each team to cary out the battle so that the original
        ### pets are not modified in any way after the battle
        self.t0 = t0.copy()
        self.t0._battle = True
        self.t1 = t1.copy()
        self.t1._battle = True

        ### Internal storage
        self.pet_priority = []
        self.battle_history = {}
        self.battle_iter = 0

        ### Build initial effect queue order
        self.pet_priority = self.update_pet_priority(self.t0, self.t1)

    def battle(self):
        ### Perform all effects that occur at the start of the battle
        self.start()
        while True:
            result = self.attack()
            if result == False:
                break

        ### Check winner and return 0 for t0 win, 1 for t1 win, 2 for draw
        return self.check_battle_result()

    def start(self):
        """
        Perform all start of battle effects

        """
        ### First move the teams forward
        t0 = self.t0
        t1 = self.t1
        teams = [t0, t1]

        ### Phase of start
        phase_dict = {
            "init": [[str(x) for x in t0], [str(x) for x in t1]],
            "start": {
                "phase_move_start": [],
                "phase_start": [],
                "phase_move_end": [],
            },
        }

        for temp_phase in phase_dict["start"]:
            battle_phase(
                self, temp_phase, teams, self.pet_priority, phase_dict["start"]
            )

            self.battle_history.update(phase_dict)

            ### If animals have moved or fainted then effect order must be updated
            if temp_phase.startswith("phase_move"):
                self.pet_priority = self.update_pet_priority(t0, t1)

    def attack(self):
        """
        Perform and attack and then check for new pet triggers

        Returns whether or not another attack should occur. This depends on
        if all animals of one team have a health of 0 already.

        Order of operations for an attack are:
            - Apply BeforeAttack triggers
            - Pets in the front of each team attack
            - Apply AfterAttack & Hurt triggers
            - Apply Faint triggers that are not summons
            - Apply Faint triggers that are summons & Summoned triggers
            - Check if battle is over

        """
        ### First update effect order
        self.pet_priority = self.update_pet_priority(self.t0, self.t1)
        ### Set all pet's hurt values back to 0
        for slot in self.t0:
            slot.pet.reset_hurt()
        for slot in self.t1:
            slot.pet.reset_hurt()

        t0 = self.t0
        t1 = self.t1

        attack_str = "attack {}".format(self.battle_iter)
        phase_dict = {
            attack_str: {
                "phase_move_start": [],
                "phase_attack_before": [],
                "phase_attack": [],
                "phase_attack_after": [],
                "phase_move_end": [],
            }
        }
        self.battle_iter += 1

        ### Check exit condition, if one team has no animals, return False
        if len(t0.filled) == 0:
            return False
        if len(t1.filled) == 0:
            return False
        return True

    def check_battle_result(self):
        t0 = self.t0
        t1 = self.t1
        found0 = False
        for temp_slot in t0:
            if not temp_slot.empty:
                if temp_slot.pet.health > 0:
                    found0 = True
                    break
        found1 = False
        for temp_slot in t1:
            if not temp_slot.empty:
                if temp_slot.pet.health > 0:
                    found1 = True
                    break
        if found0 and found1:
            ### Fight not over
            return -1
        if found0:
            ### t0 won
            return 0
        if found1:
            ### t1 won
            return 1
        ### Must have been draw
        return 2

    @staticmethod
    def update_pet_priority(t0, t1):
        """

        Prepares the order that the animals effects should be considered in

        Note that effects are performed in the order of highest attack to lowest
        attack. If there is a tie, then health values are compared. If there is
        a tie then a random animal is chosen first.

        """
        ### Build all data types to determine effect order
        pets = [x for x in t0] + [x for x in t1]
        attack = [x.attack for x in t0] + [x.attack for x in t1]
        health = [x.health for x in t0] + [x.health for x in t1]
        teams = [0 for x in t0] + [1 for x in t1]
        idx = [x for x in range(5)] + [x for x in range(5)]

        for iter_idx, value in enumerate(attack):
            if value == "none":
                attack[iter_idx] = 0
                health[iter_idx] = 0

        ### Basic sorting by max attack
        sort_idx = np.arange(0, len(attack))
        attack = np.array(attack)
        health = np.array(attack)
        teams = np.array(teams)
        idx = np.array(idx)

        ### Find attack collisions
        uniquea = np.unique(attack)[::-1]
        start_idx = 0
        for uattack in uniquea:
            ### Get collision idx
            temp_idx = np.where(attack == uattack)[0]
            temp_attack = attack[temp_idx]

            ### Initialize final idx for sorting
            temp_sort_idx = np.arange(0, len(temp_idx))

            if len(temp_idx) < 2:
                end_idx = start_idx + len(temp_idx)
                sort_idx[start_idx:end_idx] = temp_idx
                start_idx = end_idx
                continue

            ### Correct attack collisions by adding in health
            temp_health = health[temp_idx]
            temp_stats = temp_attack + temp_health
            temp_start_idx = 0
            for ustats in np.unique(temp_stats)[::-1]:
                temp_sidx = np.where(temp_stats == ustats)[0]
                temp_sidx = np.random.choice(
                    temp_sidx, size=(len(temp_sidx),), replace=False
                )
                temp_end_idx = temp_start_idx + len(temp_sidx)
                temp_sort_idx[temp_start_idx:temp_end_idx] = temp_sidx
                temp_start_idx = temp_end_idx

            ### Double check algorithm
            sorted_attack = [temp_attack[x] for x in temp_sort_idx]
            sorted_health = [temp_health[x] for x in temp_sort_idx]
            for iter_idx, tempa in enumerate(sorted_attack[1:-1]):
                iter_idx += 1
                if tempa < sorted_attack[iter_idx]:
                    raise Exception("That's impossible. Sorting issue.")
            for iter_idx, temph in enumerate(sorted_health[1:-1]):
                iter_idx += 1
                if temph < sorted_health[iter_idx]:
                    raise Exception("That's impossible. Sorting issue.")

            ### Dereference temp_sort_idx and store in sort_idx
            end_idx = start_idx + len(temp_idx)
            sort_idx[start_idx:end_idx] = temp_idx
            start_idx = end_idx

        ### Finish sorting by max attack
        attack = np.array([attack[x] for x in sort_idx])
        health = np.array([health[x] for x in sort_idx])
        teams = np.array([teams[x] for x in sort_idx])
        idx = np.array([idx[x] for x in sort_idx])

        ### Double check sorting algorithm
        for iter_idx, tempa in enumerate(attack[1:-1]):
            iter_idx += 2
            if tempa < attack[iter_idx]:
                raise Exception("That's impossible. Sorting issue.")

        ### Build final queue
        pet_priority = []
        pet_priority_pets = []
        for t, i in zip(teams, idx):
            if [t0, t1][t][i].empty == True:
                continue
            pet_priority.append((t, i))

        return pet_priority


class RBattle(Battle):
    """
    This class will calculate all possible outcomes of a SAP battle considering
    all paths of random behavior. The advantage is that probabilities of winning
    are evaluated exactly rather than requiring bootstrapped probabilities.

    Disadvantage is that it is possible that huge number of paths must be
    evaluated to determine exact probabilities. Protection against (could) be
    implemented in two ways:
        1. Determining that paths lead to nomial identical results and can
            merge back together improving calculation efficiency
        2. Define a maximum path size and if the number paths detected is larger
            then probabilities are bootstrapped.

    """

    def __init__(self, t0, t1, max_paths=1000):
        """
        Performs the battle between the input teams t1 and t2.

        """
        ### Make copy each team to cary out the battle so that the original
        ### pets are not modified in any way after the battle
        self.t0 = t0.copy()
        self.t0._battle = True
        self.t1 = t1.copy()
        self.t1._battle = True

        ### Internal storage
        self.battle_list = []

        ### Build initial effect queue order
        self.pet_priority = self.update_pet_priority(self.t0, self.t1)

        raise Exception("Not implemented")


def battle_phase(battle_obj, phase, teams, pet_priority, phase_dict):
    """
    Definition for performing all effects and actions throughout the battle.
    Implemented as function instead of class method to save an extra
    indentation.
    s
    """
    ### Parse inputs and collect info
    pp = pet_priority

    ##### Trigger logic for starting battle
    if phase.startswith("phase_move"):
        start_order = [[str(x) for x in teams[0]], [str(x) for x in teams[1]]]
        teams[0].move_forward()
        teams[1].move_forward()
        end_order = [[str(x) for x in teams[0]], [str(x) for x in teams[1]]]
        phase_dict[phase] = [start_order, end_order]

    elif phase == "phase_start":
        battle_phase_start(battle_obj, phase, teams, pet_priority, phase_dict)

    ##### Trigger logic for an attack
    elif phase == "phase_attack_before":
        battle_phase_attack_before(battle_obj, phase, teams, pet_priority, phase_dict)

    elif phase == "phase_attack":
        ### Check if fainted and performed fainted triggers
        battle_phase_attack(battle_obj, phase, teams, pet_priority, phase_dict)

    elif phase == "phase_attack_after":
        battle_phase_attack_after(battle_obj, phase, teams, pet_priority, phase_dict)

    else:
        raise Exception("Phase {} not found".format(phase))


def battle_phase_start(battle_obj, phase, teams, pet_priority, phase_dict):
    phase_list = phase_dict["phase_start"]
    pp = pet_priority
    for team_idx, pet_idx in pp:
        p = teams[team_idx][pet_idx].pet
        fteam, oteam = get_teams([team_idx, pet_idx], teams)
        activated, targets, possible = p.sob_trigger(oteam)
        append_phase_list(
            phase_list, p, team_idx, pet_idx, activated, targets, possible
        )

    check_self_summoned_triggers(teams, pet_priority, phase_dict)

    return phase_list


def check_summon_triggers(
    phase_list, p, team_idx, pet_idx, fteam, activated, targets, possible
):
    if activated == False:
        return 0

    func = get_effect_function(p)
    if func not in [RespawnPet, SummonPet, SummonRandomPet]:
        return 0

    if "team" in p.ability["effect"]:
        team = p.ability["effect"]["team"]
        if team == "Enemy":
            return 0

    ### Otherwise, summon triggers need to be checked for each Pet in targets
    if len(targets) > 0:
        if type(targets[0]) == list:
            temp_all_targets = []
            for entry in targets:
                temp_all_targets += entry
            targets = temp_all_targets

    for temp_te in targets:
        for temp_slot in fteam:
            temp_pet = temp_slot.pet
            tempa, tempt, tempp = temp_pet.friend_summoned_trigger(temp_te)
            append_phase_list(
                phase_list, temp_pet, team_idx, pet_idx, tempa, tempt, tempp
            )

    return len(targets)


def check_self_summoned_triggers(teams, pet_priority, phase_dict):
    """
    Currently only butterfly

    """

    phase_list = phase_dict["phase_start"]
    pp = pet_priority
    for team_idx, pet_idx in pp:
        p = teams[team_idx][pet_idx].pet
        if p.health <= 0:
            continue
        if p.ability["trigger"] != "Summoned":
            continue
        if p.ability["triggeredBy"]["kind"] != "Self":
            continue

        func = get_effect_function(p)
        target = func(p, [0, pet_idx], teams, te=p)
        append_phase_list(phase_list, p, team_idx, pet_idx, True, target, [target])


def check_status_triggers(phase_list, p, team_idx, pet_idx, teams):
    if p.status not in ["status-honey-bee", "status-extra-life"]:
        return

    ability = data["statuses"][p.status]["ability"]
    p.set_ability(ability)
    te_idx = [team_idx, pet_idx]
    activated, targets, possible = p.faint_trigger(p, te_idx)
    append_phase_list(phase_list, p, team_idx, pet_idx, activated, targets, possible)
    check_summon_triggers(
        phase_list, p, team_idx, pet_idx, teams[team_idx], activated, targets, possible
    )


def battle_phase_attack(battle_obj, phase, teams, pet_priority, phase_dict):
    phase_list = phase_dict["phase_attack"]
    aidx, nidx = get_attack_idx(phase, teams, pet_priority, phase_dict)
    if len(aidx) != 2:
        ### Must be two animals available for attacking to continue with battle
        return phase_list

    p0 = teams[0][aidx[0][1]].pet
    p1 = teams[1][aidx[1][1]].pet

    #### Implement food
    p0a, p1a = get_attack(p0, p1)

    teams[0][aidx[0][1]].pet.hurt(p1a)
    teams[1][aidx[1][1]].pet.hurt(p0a)
    phase_list.append(["Attack", (aidx[0]), str(p0), [str(p1)]])

    ### Keep track of knockouts for rhino and hippo by:
    ###   (attacking_pet, team_idx)
    knockout_list = []
    if teams[0][aidx[0][1]].pet.health <= 0:
        knockout_list.append((p1, 1))
    if teams[1][aidx[1][1]].pet.health <= 0:
        knockout_list.append((p0, 0))

    ### Implement chili
    if p0.status == "status-splash-attack":
        original_attack = p0._attack
        original_tmp_attack = p0._until_end_of_battle_attack_buff
        original_status = p0.status
        p0._attack = 5
        p0._until_end_of_battle_attack_buff = 0
        if len(nidx[1]) != 0:
            pn1 = teams[1][nidx[1][1]].pet
            p0a, p1a = get_attack(p0, pn1)
            pn1.hurt(p0a)
            phase_list.append(["splash", (aidx[0]), (str(p0)), [str(pn1)]])

            if pn1.health <= 0:
                knockout_list.append((p0, 0))

        p0.status = original_status
        p0._attack = original_attack
        p0._until_end_of_battle_attack_buff = original_tmp_attack

    if p1.status == "status-splash-attack":
        original_attack = p1._attack
        original_tmp_attack = p1._until_end_of_battle_attack_buff
        original_status = p1.status
        p1._attack = 5
        p1._until_end_of_battle_attack_buff = 0
        if len(nidx[0]) != 0:
            pn0 = teams[0][nidx[0][1]].pet
            p0a, p1a = get_attack(pn0, p1)
            pn0.hurt(p1a)
            phase_list.append(["splash", (aidx[1]), (str(p1)), [str(pn0)]])

            if pn0.health <= 0:
                knockout_list.append((p1, 1))

        p1.status = original_status
        p1._attack = original_attack
        p1._until_end_of_battle_attack_buff = original_tmp_attack

    ### Add knockout list to the end of phase_list. This is later removed
    ###   in the knockout phase
    phase_list.append(knockout_list)

    return phase_dict


def get_attack(p0, p1):
    attack_list = [p1.get_damage(p0.attack), p0.get_damage(p1.attack)]
    return attack_list


def battle_phase_attack_before(battle_obj, phase, teams, pet_priority, phase_dict):
    phase_list = phase_dict["phase_attack_before"]
    aidx, nidx = get_attack_idx(phase, teams, pet_priority, phase_dict)
    pp = pet_priority
    if len(aidx) != 2:
        ### Must be two animals available for attacking to continue with battle
        return phase_list
    for team_idx, pet_idx in pp:
        if aidx[team_idx][1] != pet_idx:
            ### Effects are only activated for the attacking pet
            continue
        p = teams[team_idx][pet_idx].pet
        fteam, oteam = get_teams([team_idx, pet_idx], teams)
        activated, targets, possible = p.before_attack_trigger(oteam)
        append_phase_list(
            phase_list, p, team_idx, pet_idx, activated, targets, possible
        )

    return phase_dict


def get_attack_idx(phase, teams, pet_priority, phase_dict):
    """
    Helper function to get the current animals participating in the attack.
    These are defined as the first animals in each team that have a health above
    zero.
    """
    ### Only check for the first target
    ### Ff there is no target it means the target fainted in the 'before_attack' phase
    if not teams[0][0].empty and teams[0][0].pet.health > 0:
        t0_idx = 0
    else:
        t0_idx = -1

    if not teams[1][0].empty and teams[1][0].pet.health > 0:
        t1_idx = 0
    else:
        t1_idx = -1

    ret_idx = []
    if t0_idx > -1:
        ret_idx.append((0, t0_idx))
    if t1_idx > -1:
        ret_idx.append((1, t1_idx))

    ### Getting next idx at the same time
    t0_next_idx = -1
    for iter_idx, temp_slot in enumerate(teams[0]):
        if not temp_slot.empty:
            if temp_slot.pet.health > 0:
                if t0_idx == iter_idx:
                    continue
                t0_next_idx = iter_idx
                break
    t1_next_idx = -1
    for iter_idx, temp_slot in enumerate(teams[1]):
        if not temp_slot.empty:
            if temp_slot.pet.health > 0:
                if t1_idx == iter_idx:
                    continue
                t1_next_idx = iter_idx
                break
    ret_next_idx = []
    if t0_next_idx > -1:
        ret_next_idx.append((0, t0_next_idx))
    else:
        ret_next_idx.append(())
    if t1_next_idx > -1:
        ret_next_idx.append((1, t1_next_idx))
    else:
        ret_next_idx.append(())

    return ret_idx, ret_next_idx


def battle_phase_attack_after(battle_obj, phase, teams, pet_priority, phase_dict):
    phase_list = phase_dict[phase]
    pp = pet_priority

    ### Can get the two animals that just previously attacked from the
    ###   phase_dict
    attack_history = phase_dict["phase_attack"]
    if len(attack_history) == 0:
        return phase_dict

    t0_pidx = attack_history[0][1][0]
    t1_pidx = attack_history[0][1][1]

    return phase_dict


def run_looping_effect_queue(
    trigger, trigger_args, battle_obj, phase, teams, pet_priority, phase_dict
):
    """
    Loop hurt & faint triggers until the effect queue is empty. This is,
    for example, for pufferfish to ping-pong with one-another. Summons are
    deferred until all other effects have been activated, which is the game's
    behavior. Level 3 catapillar's start of battle is Evolve, which is not
    the same as Summon, and therefore is not deferred.

    Queue has entries: (pet, team_idx, pet_idx, trigger_method, trigger_args)

    Should turn this into decorator once working

    Arguments
    ---------
    trigger: str
        Name of the initial trigger for the loop
    trigger_args_kw: list of str
        List of args to include for current trigger

    """
    print("\n")

    def loop_effect_queue(effect_queue, summon_queue):
        summon_queue_added = []
        while True:
            ### Question: Does pet_priority need to be re-evaluated in this loop?
            ###   Should match what actual game does.
            ### For now, putting it in here
            pp = battle_obj.update_pet_priority(teams[0], teams[1])
            knockout_queue = []
            summoned_list = []
            faint_list = []

            ### First empty the current effect queue
            for _ in range(len(effect_queue)):
                p, team_idx, pet_idx, trigger_method, effect_args = effect_queue.pop(0)
                print(
                    "-" * 80 + "\n", p, team_idx, pet_idx, trigger_method, effect_args
                )
                activated, targets, possible = trigger_method(*effect_args)
                append_phase_list(
                    phase_list, p, team_idx, pet_idx, activated, targets, possible
                )

                ### Store any pet that scored a knockout with its effect
                for temp_target in targets:
                    if temp_target.health <= 0:
                        knockout_queue.append(p)

                ### Store summoned pets
                if get_effect_function(p) in [RespawnPet, SummonPet, SummonRandomPet]:
                    summoned_list += targets

                ### Store pets that just performed a faint trigger
                if trigger_method.__name__ == "faint_status_trigger":
                    ### If called with trigger self, then pet must have fainted
                    if p == effect_args[0]:
                        faint_list += [(p, [team_idx, pet_idx])]

            ### Then check for additional triggers to add to the queue by the
            ###   pet priority
            pp = battle_obj.update_pet_priority(teams[0], teams[1])
            for team_idx, pet_idx in pp:
                p = teams[team_idx][pet_idx].pet
                fteam, oteam = get_teams([team_idx, pet_idx], teams)

                if p.health <= 0:
                    trigger_method = getattr(p, "faint_trigger")
                    func = get_effect_function(p)
                    ### Check if faint effect should be put in summon queue or
                    ###   activated immediately
                    if func in [RespawnPet, SummonPet, SummonRandomPet]:
                        ### Don't add summon ability if already in summon_queue
                        if p not in summon_queue_added:
                            print("ADDING TO SUMMON QUEUE", summon_queue_added)
                            summon_queue.append(
                                (
                                    p,
                                    team_idx,
                                    pet_idx,
                                    trigger_method,
                                    [p, [team_idx, pet_idx], oteam],
                                )
                            )
                            summon_queue_added.append(p)
                    else:
                        effect_queue.append(
                            (
                                p,
                                team_idx,
                                pet_idx,
                                trigger_method,
                                [p, [team_idx, pet_idx], oteam],
                            )
                        )
                    ### If fainted, cannot activate any more effects
                    continue
                elif p._hurt > 0:
                    trigger_method = getattr(p, "hurt_trigger")
                    effect_queue.append(
                        (
                            p,
                            team_idx,
                            pet_idx,
                            trigger_method,
                            [
                                oteam,
                            ],
                        )
                    )
                else:
                    pass

                ### Deal with pets that scored a knockout when emptying effect queue
                ###   in the previous loop
                if p in knockout_queue:
                    trigger_method = getattr(p, "knockout_trigger")
                    effect_queue.append(
                        (
                            p,
                            team_idx,
                            pet_idx,
                            trigger_method,
                            [
                                oteam,
                            ],
                        )
                    )

                ### Activating effect to pets that were summoned
                for summoned_pet in summoned_list:
                    if summoned_pet.team == p.team:
                        trigger_method = getattr(p, "friend_summoned_trigger")
                    else:
                        trigger_method = getattr(p, "enemy_summoned_trigger")
                    effect_queue.append(
                        (
                            p,
                            team_idx,
                            pet_idx,
                            trigger_method,
                            [
                                summoned_pet,
                            ],
                        )
                    )

                ### Activating effects triggered by fainted pets
                for fainted_pet, te_idx in faint_list:
                    trigger_method = getattr(p, "faint_trigger")
                    if p.ability["trigger"] == "Faint" and ["triggeredBy"] == "EachFriend":
                        if p.ability["effect"]["kind"] == "SummonPet":
                            ### If summon due to pet dying, then put into the 
                            ###   summon queue
                            summon_queue.append(
                                (
                                    p,
                                    team_idx,
                                    pet_idx,
                                    trigger_method,
                                    [
                                        fainted_pet,
                                        te_idx,
                                        oteam,
                                    ],
                                )
                            )
                        else:
                            ### Otherwise, add to effect queue for activation
                            ###   right away
                            effect_queue.append(
                                (
                                    p,
                                    team_idx,
                                    pet_idx,
                                    trigger_method,
                                    [
                                        fainted_pet,
                                        te_idx,
                                        oteam,
                                    ],
                                )
                            )

            ### Break if no more effects to trigger
            if len(effect_queue) == 0:
                break

        return summon_queue

    ### Build initial effect queue for the current trigger
    phase_list = phase_dict[phase]
    effect_queue = []
    knockout_queue = []
    summon_queue = []

    pp = pet_priority
    for team_idx, pet_idx in pp:
        p = teams[team_idx][pet_idx].pet
        fteam, oteam = get_teams([team_idx, pet_idx], teams)
        trigger_method = getattr(p, trigger)
        temp_trigger_kw_dict = {"oteam": oteam}
        temp_trigger_args = [temp_trigger_kw_dict[x] for x in trigger_args]
        effect_queue.append((p, team_idx, pet_idx, trigger_method, (temp_trigger_args)))

    ### Run loop for effect queue
    print("\n###################### STARTING EFFECT LOOP")
    summon_queue = loop_effect_queue(effect_queue, summon_queue)
    ### Then run summon queue through looping effect queue
    print("\n###################### STARTING SUMMON LOOP")
    print(len(summon_queue))
    _ = loop_effect_queue(summon_queue, [])
    assert len(_) == 0

    ### Done
    return


def append_phase_list(phase_list, p, team_idx, pet_idx, activated, targets, possible):
    if activated:
        tiger = False
        if len(targets) > 0:
            if type(targets[0]) == list:
                tiger = True
        func = get_effect_function(p)

        if not tiger:
            phase_list.append(
                (
                    func.__name__,
                    (team_idx, pet_idx),
                    (p.__repr__()),
                    [str(x) for x in targets],
                )
            )
        else:
            for temp_target in targets:
                phase_list.append(
                    (
                        func.__name__,
                        (team_idx, pet_idx),
                        (p.__repr__()),
                        [str(x) for x in temp_target],
                    )
                )
