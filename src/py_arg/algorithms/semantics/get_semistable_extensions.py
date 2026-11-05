from typing import Set, FrozenSet

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_complete_extensions import get_complete_extensions


def get_semistable_extensions(argumentation_framework: AbstractArgumentationFramework) -> Set[FrozenSet[Argument]]:
    """
    Get the semi-stable extensions of an argumentation framework: the complete extensions whose range (the extension
    plus the arguments it defeats) is maximal with respect to set inclusion.

    :param argumentation_framework: The argumentation framework for which we need the semi-stable extensions.
    :return: semi-stable extension of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> sses = get_semistable_extensions(af)
    >>> len(sses)
    1
    >>> frozenset({b, d}) in sses
    True
    >>> frozenset({b}) in sses
    False
    """
    defeated = {argument: set() for argument in argumentation_framework.arguments}
    for defeat in argumentation_framework.defeats:
        defeated[defeat.from_argument].add(defeat.to_argument)
    ranges = {complete_extension: complete_extension.union(*(defeated[argument] for argument in complete_extension))
              for complete_extension in get_complete_extensions(argumentation_framework)}
    return {complete_extension for complete_extension, extension_range in ranges.items()
            if not any(extension_range < other_range for other_range in ranges.values())}


if __name__ == "__main__":
    import doctest

    doctest.testmod()
