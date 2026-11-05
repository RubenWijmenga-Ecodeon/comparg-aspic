from typing import Set, List, Union, Any

from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import AbstractArgumentationFramework
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.algorithms.semantics.get_largest_admissible_subset import get_largest_admissible_subset
from py_arg.algorithms.semantics.get_semistable_extensions import get_semistable_extensions


def get_eager_extension(argumentation_framework: AbstractArgumentationFramework) -> List[
    Set[Union[Any]]]:
    """
    Get the eager extension of an argumentation framework: the largest admissible subset of the intersection of all
    semi-stable extensions.

    :param argumentation_framework: The argumentation framework for which we need the eager extension.
    :return: eager extension of the argumentation framework.

    >>> b = Argument('b')
    >>> c = Argument('c')
    >>> d = Argument('d')
    >>> arguments = [b, c, d]
    >>> defeats = [Defeat(b, c), Defeat(c, d), Defeat(d, c)]
    >>> af = AbstractArgumentationFramework('af', arguments, defeats)
    >>> ees = get_eager_extension(af)
    >>> len(ees)
    1
    >>> frozenset({b, d}) in ees
    True
    >>> frozenset({b}) in ees
    False
    """
    intersect_semistable = set.intersection(*(set(semistable_extension) for semistable_extension
                                              in get_semistable_extensions(argumentation_framework)))
    return [get_largest_admissible_subset(argumentation_framework, intersect_semistable)]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
