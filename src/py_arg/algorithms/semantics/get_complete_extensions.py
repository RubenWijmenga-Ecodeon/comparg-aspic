from enum import Enum
from typing import Set, Dict, FrozenSet, List

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_grounded_extension import get_grounded_extension


# Labelling-based search after Algorithm 1 from Nofal, Samer, Katie Atkinson, and Paul E. Dunne. "Algorithms for
# decision problems in argument systems under preferred semantics." Artificial Intelligence 207 (2014): 23-51. A complete
# extension is an admissible set containing every argument it defends; the search labels arguments IN or UNDEC one by one
# and prunes branches that can no longer become admissible or have left out an argument the IN set defends. Without that
# pruning the search visits every labelling, which does not finish for frameworks of a few dozen arguments.


class CompleteExtensionLabel(Enum):
    IN = 1  # Arguments *might* be in a complete extension
    OUT = 2  # Argument is defeated by an IN argument
    BLANK = 3  # Default label for all arguments, indicating that the argument is still unprocessed.
    MUST_OUT = 4  # Argument defeats IN argument
    UNDEC = 5  # Argument may not be included in a complete extension because not defended by any IN argument.


def get_complete_extensions(argumentation_framework: AbstractArgumentationFramework) -> Set[FrozenSet[Argument]]:
    """
    Get the complete extensions of an argumentation framework.

    :param argumentation_framework: The argumentation framework for which we need the complete extensions.
    :return: complete extensions of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> ces = get_complete_extensions(af)
    >>> len(ces)
    1
    >>> frozenset({b, d}) in ces
    True
    >>> frozenset({b}) in ces
    False
    """
    arguments = sorted(argumentation_framework.arguments)
    defeaters = {argument: set() for argument in arguments}
    defeated = {argument: set() for argument in arguments}
    for defeat in argumentation_framework.defeats:
        defeaters[defeat.to_argument].add(defeat.from_argument)
        defeated[defeat.from_argument].add(defeat.to_argument)

    labelling = {argument: CompleteExtensionLabel.BLANK for argument in arguments}
    # A self-defeating argument is never in a conflict-free set.
    for argument in arguments:
        if argument in defeaters[argument]:
            labelling[argument] = CompleteExtensionLabel.UNDEC
    # Every complete extension contains the grounded extension, so it can be labelled IN before searching.
    for argument in get_grounded_extension(argumentation_framework):
        labelling = _in_trans(labelling, argument, defeaters, defeated)

    complete_extensions: Set[FrozenSet[Argument]] = set()
    _search_complete_extensions(arguments, labelling, defeaters, defeated, complete_extensions)
    return complete_extensions


def _search_complete_extensions(arguments: List[Argument],
                                labelling: Dict[Argument, CompleteExtensionLabel],
                                defeaters: Dict[Argument, Set[Argument]],
                                defeated: Dict[Argument, Set[Argument]],
                                complete_extensions: Set[FrozenSet[Argument]]):
    # Dead end: an argument that must be defeated by the IN set, but no unprocessed argument can defeat it any more.
    if any(labelling[argument] == CompleteExtensionLabel.MUST_OUT and
           not any(labelling[defeater] == CompleteExtensionLabel.BLANK for defeater in defeaters[argument])
           for argument in arguments):
        return

    # Dead end: an UNDEC argument whose defeaters are all OUT is defended by the IN set, so it should have been IN.
    if any(labelling[argument] == CompleteExtensionLabel.UNDEC and
           all(labelling[defeater] == CompleteExtensionLabel.OUT for defeater in defeaters[argument])
           for argument in arguments):
        return

    blank_arguments = [argument for argument in arguments if labelling[argument] == CompleteExtensionLabel.BLANK]
    if not blank_arguments:
        # Only IN, OUT and UNDEC arguments are left, and the checks above make the IN set admissible and complete.
        complete_extensions.add(frozenset(argument for argument in arguments
                                          if labelling[argument] == CompleteExtensionLabel.IN))
        return

    # An argument whose defeaters are all OUT is defended by the IN set, so it can only be IN.
    defended = next((argument for argument in blank_arguments
                     if all(labelling[defeater] == CompleteExtensionLabel.OUT for defeater in defeaters[argument])),
                    None)
    if defended is not None:
        _search_complete_extensions(arguments, _in_trans(labelling, defended, defeaters, defeated),
                                    defeaters, defeated, complete_extensions)
        return

    # Prefer an argument that defeats a MUST_OUT argument: the IN set needs it for its defence.
    chosen = next((argument for argument in blank_arguments
                   if any(labelling[defeated_argument] == CompleteExtensionLabel.MUST_OUT
                          for defeated_argument in defeated[argument])),
                  blank_arguments[0])
    _search_complete_extensions(arguments, _in_trans(labelling, chosen, defeaters, defeated),
                                defeaters, defeated, complete_extensions)
    _search_complete_extensions(arguments, _undec_trans(labelling, chosen),
                                defeaters, defeated, complete_extensions)


def _in_trans(labelling: Dict[Argument, CompleteExtensionLabel], argument: Argument,
              defeaters: Dict[Argument, Set[Argument]],
              defeated: Dict[Argument, Set[Argument]]) -> Dict[Argument, CompleteExtensionLabel]:
    new_labelling = labelling.copy()
    new_labelling[argument] = CompleteExtensionLabel.IN
    for defeated_argument in defeated[argument]:
        new_labelling[defeated_argument] = CompleteExtensionLabel.OUT
    for defeater in defeaters[argument]:
        if new_labelling[defeater] != CompleteExtensionLabel.OUT:
            new_labelling[defeater] = CompleteExtensionLabel.MUST_OUT
    return new_labelling


def _undec_trans(labelling: Dict[Argument, CompleteExtensionLabel], argument: Argument) -> \
        Dict[Argument, CompleteExtensionLabel]:
    new_labelling = labelling.copy()
    new_labelling[argument] = CompleteExtensionLabel.UNDEC
    return new_labelling


if __name__ == "__main__":
    import doctest

    doctest.testmod()
