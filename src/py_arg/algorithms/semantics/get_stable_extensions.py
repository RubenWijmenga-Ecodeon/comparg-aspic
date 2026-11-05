from typing import Set, FrozenSet

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_preferred_extensions import get_preferred_extensions


def get_stable_extensions(argumentation_framework: AbstractArgumentationFramework) -> Set[FrozenSet[Argument]]:
    """
    Get the stable extensions of an argumentation framework: the preferred extensions that defeat every argument outside
    them (every stable extension is preferred).

    :param argumentation_framework: The argumentation framework for which we need the stable extensions.
    :return: stable extension of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> ses = get_stable_extensions(af)
    >>> len(ses)
    1
    >>> frozenset({b, d}) in ses
    True
    >>> frozenset({b}) in ses
    False
    """
    defeated = {argument: set() for argument in argumentation_framework.arguments}
    for defeat in argumentation_framework.defeats:
        defeated[defeat.from_argument].add(defeat.to_argument)
    all_arguments = set(argumentation_framework.arguments)
    return {preferred_extension for preferred_extension in get_preferred_extensions(argumentation_framework)
            if preferred_extension.union(*(defeated[argument] for argument in preferred_extension)) == all_arguments}


if __name__ == "__main__":
    import doctest

    doctest.testmod()
