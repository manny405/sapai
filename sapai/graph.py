# %%

from graphviz import Digraph
from sapai import Pet


def html_table(
    header="",
    entries=None,
    table_attr=None,
    header_font_attr=None,
    header_bg_color="#1C6EA4",
    cell_font_attr=None,
    cell_border=0,
    column_align=None,
    cell_bg_colors=None,
):
    entries = entries or [[]]
    table_attr = table_attr or [("BORDER", "1")]
    header_font_attr = header_font_attr or [("COLOR", "#000000")]
    cell_font_attr = cell_font_attr or []
    column_align = column_align or ["RIGHT", "LEFT"]
    cell_bg_colors = cell_bg_colors or [[]]

    table_attr_str = ""
    for attr, value in table_attr:
        table_attr_str += f""" {attr}="{value}" """
    table_str = f"<<table {table_attr_str}>"

    num_rows = 0
    if len(header) > 0:
        num_rows += 1

    if len(entries) != 0:
        if type(entries[0]) != list:
            raise Exception("Entries argument should be list of lists.")
        else:
            num_rows += len(entries)

    if len(cell_bg_colors) != 0:
        if type(cell_bg_colors[0]) != list:
            raise Exception("Argument cell_bg_colors should be list of lists")
        for iter_idx, temp_entry in enumerate(cell_bg_colors):
            temp_length = len(temp_entry)
            temp_check_length = len(entries[iter_idx])
            if temp_length != 0:
                raise NotImplementedError
            if temp_length != temp_check_length:
                raise Exception("Must supply one cell_bg_color for every entry")

    num_columns = 0
    for entry in entries:
        temp_columns = len(entry)
        num_columns = max(num_columns, temp_columns)

    ### Build string starting with header
    if len(header) > 0:
        temp_str = "<tr> "

        temp_font_attr_str = ""
        for attr, value in header_font_attr:
            temp_font_attr_str += f""" {attr}="{value}" """

        temp_str += f"""<td BGCOLOR="{header_bg_color}" COLSPAN="{num_columns}"><font {temp_font_attr_str}>{header}</font></td>"""
        temp_str += "</tr>"
        table_str += temp_str

    cell_font_attr_str = ""
    for attr, value in cell_font_attr:
        cell_font_attr_str += f""" {attr}="{value}" """

    for entry in entries:
        temp_str = "<tr> "
        for column_idx in range(num_columns):
            if column_idx < len(entry):
                temp_cell_str = entry[column_idx]
            else:
                temp_cell_str = ""
            temp_align = column_align[column_idx % len(column_align)]
            temp_str += f"""<td BORDER="{cell_border}" ALIGN="{temp_align}"><font {cell_font_attr_str}>{temp_cell_str}</font></td>"""
        temp_str += "</tr>"
        table_str += temp_str

    table_str += "</table>>"
    return table_str


def prep_pet_str(pstr):
    if isinstance(pstr, Pet):
        pstr = str(pstr)
    temp_pstr = pstr.replace("<", "")
    temp_pstr = temp_pstr.replace(">", "")
    temp_pstr = temp_pstr.replace(" Slot ", "")
    temp_pstr = temp_pstr.replace("pet-", "")
    # temp_pstr = temp_pstr.replace("EMPTY "," ")
    temp_pstr = temp_pstr.replace("none", "")
    temp_pstr = " ".join(temp_pstr.split())
    temp_pstr_list = temp_pstr.split()
    if len(temp_pstr_list) == 2:
        temp_stats = temp_pstr_list[1]
        replace_index = temp_stats.index("-")
        temp_pstr_list[
            1
        ] = f"{temp_stats[0:replace_index]},{temp_stats[replace_index + 1 :]}"
        temp_pstr = " ".join(temp_pstr_list)
    return temp_pstr


def prep_pet_str_obj(obj):
    """Recursive function to prepare pet string"""
    if type(obj) == str:
        return prep_pet_str(obj)
    elif type(obj) == list:
        ret_obj = []
        for temp_entry in obj:
            ret_obj += [prep_pet_str_obj(temp_entry)]
        return ret_obj
    else:
        raise Exception(type(obj))


def prep_effect(effect_list):
    effect_name = effect_list[0]
    team_idx = effect_list[1][0]
    pet_idx = effect_list[1][1]
    pet_str = prep_pet_str(effect_list[2])
    target_str = prep_pet_str_obj(effect_list[3])
    target_str = " ".join(target_str)
    if len(target_str) == 0:
        target_str = " "
    effect_columns = [
        "Effect",
        "Team",
        "  Pet Index  ",
        "  Activating Pet  ",
        "Targets",
    ]
    return (
        [effect_name, str(team_idx), str(pet_idx), pet_str, target_str],
        effect_columns,
    )


def graph_battle(f, file_name="", verbose=False):
    g = Digraph(graph_attr={"rankdir": "TB", "clusterrank": "local"})
    prev_node = None
    node_idx = 0
    for turn_name, phase_dict in f.battle_history.items():
        if turn_name == "init":
            pstr = prep_pet_str_obj(phase_dict)
            pstr[0] = ["Team 0: "] + pstr[0]
            pstr[1] = ["Team 1: "] + pstr[1]
            temp_table = html_table(
                header="Initial Teams",
                entries=pstr,
                table_attr=[("BORDER", "1")],
                header_font_attr=[("COLOR", "#FFFFFF")],
                header_bg_color="#1C6EA4",
                cell_font_attr=[],
                cell_border=0,
                column_align=[
                    "RIGHT",
                    "CENTER",
                    "CENTER",
                    "CENTER",
                    "CENTER",
                    "CENTER",
                ],
                cell_bg_colors=[[]],
            )
            g.node(
                str(node_idx), style="rounded,invisible", shape="box", label=temp_table
            )
            prev_node = str(node_idx)
            node_idx += 1
            continue

        turn_name = turn_name[0].upper() + turn_name[1:] + " Turn"
        ### Should really do nested tables for start and each attack. That's next.
        for phase_name, phase_entry in phase_dict.items():
            if "phase_move" in phase_name:
                if phase_name == "phase_move_start":
                    header = f"{turn_name} Phase: Move-Team-Start"
                    if not verbose:
                        continue
                elif phase_name == "phase_move_end":
                    header = f"{turn_name} Phase: Move-Team-End"
                pstr = prep_pet_str_obj(phase_entry)
                ### Only interested in final positions
                if len(pstr) > 0:
                    pstr = pstr[-1]
                else:
                    pstr = [[], []]
                pstr[0] = ["Team 0: "] + pstr[0]
                pstr[1] = ["Team 1: "] + pstr[1]
                entries = pstr

            elif "phase_start" == phase_name:
                header = f"{turn_name} Phase: Start Fight"
                entries = []
                for iter_idx, temp_effect_info in enumerate(phase_entry):
                    es, ec = prep_effect(temp_effect_info)
                    if iter_idx == 0:
                        entries.append(ec)
                    entries.append(es)
                if len(entries) == 0:
                    if not verbose:
                        continue
                    entries.append(
                        [
                            "Effect",
                            "Team",
                            "  Pet Index  ",
                            "  Activating Pet  ",
                            "Targets",
                        ]
                    )

            elif "phase_hurt_and_faint" in phase_name:
                header = f"{turn_name} Phase: Hurt and Faint"
                entries = []
                if len(phase_entry) != 0:
                    for iter_idx, temp_effect_info in enumerate(phase_entry):
                        es, ec = prep_effect(temp_effect_info)
                        if iter_idx == 0:
                            entries.append(ec)
                        entries.append(es)
                if len(entries) == 0:
                    if not verbose:
                        continue
                    entries.append(
                        [
                            "Effect",
                            "Team",
                            "  Pet Index  ",
                            "  Activating Pet  ",
                            "Targets",
                        ]
                    )

            elif phase_name in [
                "phase_attack_before",
                "phase_attack_after",
                "phase_attack",
                "phase_knockout",
            ]:
                if phase_name == "phase_attack_before":
                    header = f"{turn_name} Phase: Before Attack"
                elif phase_name == "phase_attack":
                    header = f"{turn_name} Phase: Attack"
                elif phase_name == "phase_attack_after":
                    header = f"{turn_name} Phase: Attack After"
                elif phase_name == "phase_knockout":
                    header = f"{turn_name} Phase: Knockout"
                entries = []
                for temp_effect_info in phase_entry:
                    es, ec = prep_effect(temp_effect_info)
                    if len(entries) == 0:
                        entries.append(ec)
                    entries.append(es)
                if len(entries) == 0:
                    if not verbose:
                        continue
                    entries.append(
                        [
                            "Effect",
                            "Team",
                            "  Pet Index  ",
                            "  Activating Pet  ",
                            "Targets",
                        ]
                    )

            else:
                continue

            temp_table = html_table(
                header=header,
                entries=entries,
                table_attr=[("BORDER", "1")],
                header_font_attr=[("COLOR", "#FFFFFF")],
                header_bg_color="#1C6EA4",
                cell_font_attr=[],
                cell_border=0,
                column_align=["CENTER", "CENTER", "CENTER", "CENTER", "CENTER"],
                cell_bg_colors=[[]],
            )
            g.node(
                str(node_idx), style="rounded,invisible", shape="box", label=temp_table
            )
            g.edge(prev_node, str(node_idx))
            prev_node = str(node_idx)
            node_idx = node_idx + 1

    if len(file_name) > 0:
        g.render(filename=file_name)
    return g


# %%
