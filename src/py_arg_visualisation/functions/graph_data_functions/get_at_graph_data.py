from typing import List, Dict

from py_arg.aspic_classes.argumentation_theory import ArgumentationTheory
from py_arg.aspic_classes.instantiated_argument import InstantiatedArgument
from py_arg.aspic_classes.strict_rule import StrictRule
from py_arg_visualisation.functions.graph_data_functions.get_color import get_color
from py_arg_visualisation.functions.ordering_functions.get_ordering_by_specification \
    import get_ordering_by_specification


def get_rule_name_label(argument: InstantiatedArgument) -> str:
    """
    Calculate a compact label for an argument: the names of the rules it applies (bottom-up) and its conclusion.
    Premise-based arguments keep their premise as label. Strict rules have numeric ids, so they are prefixed with s.

    :param argument: The argument that needs a label.
    """
    if argument.top_rule is None:
        return argument.short_name

    rule_names = []

    def collect_rule_names(sub_argument: InstantiatedArgument):
        for direct_sub_argument in sorted(sub_argument.direct_sub_arguments, key=lambda arg: arg.name):
            collect_rule_names(direct_sub_argument)
        if sub_argument.top_rule is not None:
            rule = sub_argument.top_rule
            rule_name = 's' + str(rule.id) if isinstance(rule, StrictRule) else str(rule.id)
            if rule_name not in rule_names:
                rule_names.append(rule_name)

    collect_rule_names(argument)
    return ', '.join(rule_names) + ': ' + str(argument.conclusion)


def get_argumentation_theory_graph_data(argumentation_theory: ArgumentationTheory, ordering_specification: str,
                                        selected_arguments: Dict[str, List[str]],
                                        color_blind_mode: bool):
    """
    Calculate the data needed for the graphical representation of the argumentation theory and ordering

    :param argumentation_theory: The argumentation_theory that needs to be visualized.
    :param ordering_specification: The chosen ordering, combining both last/weakest link and democratic/elitist.
    :param selected_arguments: Arguments to be marked with a different color (e.g. because they are in some extension)
    :param color_blind_mode: Is the color-blind mode on?
    """
    if selected_arguments and 'blue' in selected_arguments:
        blue = selected_arguments['blue']
    else:
        blue = []
    if selected_arguments and 'green' in selected_arguments:
        green = selected_arguments['green']
    else:
        green = []
    if selected_arguments and 'yellow' in selected_arguments:
        yellow = selected_arguments['yellow']
    else:
        yellow = []
    if selected_arguments and 'red' in selected_arguments:
        red = selected_arguments['red']
    else:
        red = []

    argument_long_str_to_id = {}
    data_nodes = []
    for argument_id, argument in enumerate(argumentation_theory.all_arguments):
        readable_id = 'A' + str(argument_id + 1)
        argument_long_str_to_id[argument.name] = readable_id
        if argument.name in blue:
            color = get_color('blue', color_blind_mode)
        elif argument.name in green:
            color = get_color('green', color_blind_mode)
        elif argument.name in yellow:
            color = get_color('yellow', color_blind_mode)
        elif argument.name in red:
            color = get_color('red', color_blind_mode)
        else:
            color = get_color('gray', color_blind_mode)
        data_nodes.append({'id': readable_id, 'label': get_rule_name_label(argument), 'color': color})

    ordering = get_ordering_by_specification(argumentation_theory, ordering_specification)
    data_edges = []
    for defeat in argumentation_theory.recompute_all_defeats(ordering):
        argument_a_id = argument_long_str_to_id[defeat.from_argument.name]
        argument_b_id = argument_long_str_to_id[defeat.to_argument.name]

        data_edges.append({'id': str(argument_a_id) + '-' + str(argument_b_id),
                           'from': argument_a_id, 'to': argument_b_id, 'arrows': 'to'})

    data = {'nodes': data_nodes, 'edges': data_edges}
    return data
