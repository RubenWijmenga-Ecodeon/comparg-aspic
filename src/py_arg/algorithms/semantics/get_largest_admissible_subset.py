from typing import Set, Iterable

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument


def get_largest_admissible_subset(argumentation_framework: AbstractArgumentationFramework,
                                  candidate: Iterable[Argument]) -> Set[Argument]:
    """
    Get the largest admissible subset of a conflict-free set of arguments, by repeatedly removing the arguments that the
    remaining set does not defend. An admissible subset keeps defending all its members, so it is never removed; the
    result therefore contains every admissible subset of the candidate.

    :param argumentation_framework: The argumentation framework the arguments belong to.
    :param candidate: A conflict-free set of arguments, such as the intersection of the preferred extensions.
    :return: The largest admissible subset of the candidate.
    """
    defeaters = {argument: set() for argument in argumentation_framework.arguments}
    for defeat in argumentation_framework.defeats:
        defeaters[defeat.to_argument].add(defeat.from_argument)

    remaining = set(candidate)
    while True:
        defeated_by_remaining = {defeated for defeated, its_defeaters in defeaters.items()
                                 if its_defeaters & remaining}
        undefended = {argument for argument in remaining if not defeaters[argument] <= defeated_by_remaining}
        if not undefended:
            return remaining
        remaining -= undefended
