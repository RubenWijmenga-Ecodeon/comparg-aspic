from typing import Set, List, Any

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_largest_admissible_subset import get_largest_admissible_subset
from py_arg.algorithms.semantics.get_preferred_extensions import get_preferred_extensions


def get_ideal_extension(argumentation_framework: AbstractArgumentationFramework) -> List[Set[Any]]:
    """
    Get the ideal extension of an argumentation framework: the largest admissible subset of the intersection of all
    preferred extensions.

    :param argumentation_framework: The argumentation framework for which we need the ideal extension.
    :return: ideal extension of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> idl = get_ideal_extension(af)
    >>> len(idl)
    1
    >>> frozenset({b, d}) in idl
    True
    >>> frozenset({b}) in idl
    False
    """
    intersect_preferred = set.intersection(*(set(preferred_extension) for preferred_extension
                                             in get_preferred_extensions(argumentation_framework)))
    return [get_largest_admissible_subset(argumentation_framework, intersect_preferred)]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
