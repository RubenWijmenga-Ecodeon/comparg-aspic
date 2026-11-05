from enum import Enum
from typing import Set, Dict, FrozenSet, List

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat


# Labelling-based search after Algorithm 1 from Nofal, Samer, Katie Atkinson, and Paul E. Dunne. "Algorithms for
# decision problems in argument systems under preferred semantics." Artificial Intelligence 207 (2014): 23-51. The search
# labels arguments IN or UNDEC one by one and abandons a branch as soon as it can no longer become admissible.


class AdmissibleLabel(Enum):
    IN = 1  # Arguments *might* be in an admissible set
    OUT = 2  # Argument is defeated by an IN argument
    BLANK = 3  # Default label for all arguments, indicating that the argument is still unprocessed.
    MUST_OUT = 4  # Argument defeats IN argument
    UNDEC = 5  # Argument may not be included in an admissible set because not defended by any IN argument.


def get_admissible_sets(argumentation_framework: AbstractArgumentationFramework) -> Set[FrozenSet[Argument]]:
    """
    Get the admissible sets of an argumentation framework.

    :param argumentation_framework: The argumentation framework for which we need the admissible sets.
    :return: admissible sets of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> ads = get_admissible_sets(af)
    >>> len(ads)
    4
    >>> frozenset({b, d}) in ads
    True
    >>> frozenset({c}) in ads
    False
    """
    arguments = sorted(argumentation_framework.arguments)
    defeaters = {argument: set() for argument in arguments}
    defeated = {argument: set() for argument in arguments}
    for defeat in argumentation_framework.defeats:
        defeaters[defeat.to_argument].add(defeat.from_argument)
        defeated[defeat.from_argument].add(defeat.to_argument)

    # A self-defeating argument is never in a conflict-free set.
    labelling = {argument: AdmissibleLabel.UNDEC if argument in defeaters[argument] else AdmissibleLabel.BLANK
                 for argument in arguments}
    admissible_sets: Set[FrozenSet[Argument]] = set()
    _search_admissible_sets(arguments, labelling, defeaters, defeated, admissible_sets)
    return admissible_sets


def _search_admissible_sets(arguments: List[Argument],
                            labelling: Dict[Argument, AdmissibleLabel],
                            defeaters: Dict[Argument, Set[Argument]],
                            defeated: Dict[Argument, Set[Argument]],
                            admissible_sets: Set[FrozenSet[Argument]]):
    # Dead end: an argument that must be defeated by the IN set, but no unprocessed argument can defeat it any more.
    if any(labelling[argument] == AdmissibleLabel.MUST_OUT and
           not any(labelling[defeater] == AdmissibleLabel.BLANK for defeater in defeaters[argument])
           for argument in arguments):
        return

    blank_arguments = [argument for argument in arguments if labelling[argument] == AdmissibleLabel.BLANK]
    if not blank_arguments:
        admissible_sets.add(frozenset(argument for argument in arguments
                                      if labelling[argument] == AdmissibleLabel.IN))
        return

    # Prefer an argument that defeats a MUST_OUT argument: the IN set needs it for its defence.
    chosen = next((argument for argument in blank_arguments
                   if any(labelling[defeated_argument] == AdmissibleLabel.MUST_OUT
                          for defeated_argument in defeated[argument])),
                  blank_arguments[0])
    _search_admissible_sets(arguments, _in_trans(labelling, chosen, defeaters, defeated),
                            defeaters, defeated, admissible_sets)
    _search_admissible_sets(arguments, _undec_trans(labelling, chosen),
                            defeaters, defeated, admissible_sets)


def _in_trans(labelling: Dict[Argument, AdmissibleLabel], argument: Argument,
              defeaters: Dict[Argument, Set[Argument]],
              defeated: Dict[Argument, Set[Argument]]) -> Dict[Argument, AdmissibleLabel]:
    new_labelling = labelling.copy()
    new_labelling[argument] = AdmissibleLabel.IN
    for defeated_argument in defeated[argument]:
        new_labelling[defeated_argument] = AdmissibleLabel.OUT
    for defeater in defeaters[argument]:
        if new_labelling[defeater] != AdmissibleLabel.OUT:
            new_labelling[defeater] = AdmissibleLabel.MUST_OUT
    return new_labelling


def _undec_trans(labelling: Dict[Argument, AdmissibleLabel], argument: Argument) -> \
        Dict[Argument, AdmissibleLabel]:
    new_labelling = labelling.copy()
    new_labelling[argument] = AdmissibleLabel.UNDEC
    return new_labelling


if __name__ == "__main__":
    import doctest

    doctest.testmod()
