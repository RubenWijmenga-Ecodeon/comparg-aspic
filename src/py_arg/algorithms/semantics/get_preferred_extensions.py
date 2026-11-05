from enum import Enum
from typing import Set, Dict, FrozenSet, List

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_grounded_extension import get_grounded_extension


# Labelling-based search after Nofal, Samer, Katie Atkinson, and Paul E. Dunne. "Algorithms for decision problems in
# argument systems under preferred semantics." Artificial Intelligence 207 (2014): 23-51. A preferred extension is a
# maximal admissible set; the search labels arguments IN or UNDEC one by one and prunes branches that can no longer
# become admissible or can only lead to a subset of a preferred extension already found. Without that pruning the
# search visits every labelling, which does not finish for frameworks of a few dozen arguments.


class PreferredExtensionLabel(Enum):
    IN = 1              # Arguments *might* be in a preferred extension
    OUT = 2             # Argument is defeated by an IN argument
    BLANK = 3           # Default label for all arguments, indicating that the argument is still unprocessed.
    MUST_OUT = 4        # Argument defeats IN argument
    UNDEC = 5           # Argument may not be included in a preferred extension because not defended by any IN argument.


def get_preferred_extensions(argumentation_framework: AbstractArgumentationFramework) -> Set[FrozenSet[Argument]]:
    """
    Get the preferred extensions of an argumentation framework.

    :param argumentation_framework: The argumentation framework for which we need the preferred extensions.
    :return: Preferred extension of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> pes = get_preferred_extensions(af)
    >>> len(pes)
    1
    >>> frozenset({b, d}) in pes
    True
    >>> frozenset({b}) in pes
    False
    """
    arguments = sorted(argumentation_framework.arguments)
    defeaters = {argument: set() for argument in arguments}
    defeated = {argument: set() for argument in arguments}
    for defeat in argumentation_framework.defeats:
        defeaters[defeat.to_argument].add(defeat.from_argument)
        defeated[defeat.from_argument].add(defeat.to_argument)

    labelling = {argument: PreferredExtensionLabel.BLANK for argument in arguments}
    # A self-defeating argument is never in a conflict-free set.
    for argument in arguments:
        if argument in defeaters[argument]:
            labelling[argument] = PreferredExtensionLabel.UNDEC
    # Every preferred extension contains the grounded extension, so it can be labelled IN before searching.
    for argument in get_grounded_extension(argumentation_framework):
        labelling = _in_trans(labelling, argument, defeaters, defeated)

    preferred_extensions: List[FrozenSet[Argument]] = []
    _search_preferred_extensions(arguments, labelling, defeaters, defeated, preferred_extensions)
    return set(preferred_extensions)


def _search_preferred_extensions(arguments: List[Argument],
                                 labelling: Dict[Argument, PreferredExtensionLabel],
                                 defeaters: Dict[Argument, Set[Argument]],
                                 defeated: Dict[Argument, Set[Argument]],
                                 preferred_extensions: List[FrozenSet[Argument]]):
    # Dead end: an argument that must be defeated by the IN set, but no unprocessed argument can defeat it any more.
    if any(labelling[argument] == PreferredExtensionLabel.MUST_OUT and
           not any(labelling[defeater] == PreferredExtensionLabel.BLANK for defeater in defeaters[argument])
           for argument in arguments):
        return

    # Dead end: everything this branch can still label IN lies within a preferred extension found earlier.
    reachable = frozenset(argument for argument in arguments
                          if labelling[argument] in (PreferredExtensionLabel.IN, PreferredExtensionLabel.BLANK))
    if any(reachable <= preferred_extension for preferred_extension in preferred_extensions):
        return

    blank_arguments = [argument for argument in arguments if labelling[argument] == PreferredExtensionLabel.BLANK]
    if not blank_arguments:
        # No BLANK and (by the first check) no MUST_OUT arguments left: the IN arguments form an admissible set that is
        # not contained in any earlier find, so it replaces the earlier finds it contains.
        candidate = frozenset(argument for argument in arguments if labelling[argument] == PreferredExtensionLabel.IN)
        preferred_extensions[:] = [preferred_extension for preferred_extension in preferred_extensions
                                   if not preferred_extension < candidate]
        preferred_extensions.append(candidate)
        return

    # Prefer an argument that defeats a MUST_OUT argument: the IN set needs it for its defence.
    chosen = next((argument for argument in blank_arguments
                   if any(labelling[defeated_argument] == PreferredExtensionLabel.MUST_OUT
                          for defeated_argument in defeated[argument])),
                  blank_arguments[0])
    _search_preferred_extensions(arguments, _in_trans(labelling, chosen, defeaters, defeated),
                                 defeaters, defeated, preferred_extensions)
    _search_preferred_extensions(arguments, _undec_trans(labelling, chosen),
                                 defeaters, defeated, preferred_extensions)


def _in_trans(labelling: Dict[Argument, PreferredExtensionLabel], argument: Argument,
              defeaters: Dict[Argument, Set[Argument]],
              defeated: Dict[Argument, Set[Argument]]) -> Dict[Argument, PreferredExtensionLabel]:
    new_labelling = labelling.copy()
    new_labelling[argument] = PreferredExtensionLabel.IN
    for defeated_argument in defeated[argument]:
        new_labelling[defeated_argument] = PreferredExtensionLabel.OUT
    for defeater in defeaters[argument]:
        if new_labelling[defeater] != PreferredExtensionLabel.OUT:
            new_labelling[defeater] = PreferredExtensionLabel.MUST_OUT
    return new_labelling


def _undec_trans(labelling: Dict[Argument, PreferredExtensionLabel], argument: Argument) -> \
        Dict[Argument, PreferredExtensionLabel]:
    new_labelling = labelling.copy()
    new_labelling[argument] = PreferredExtensionLabel.UNDEC
    return new_labelling


if __name__ == "__main__":
    import doctest

    doctest.testmod()
