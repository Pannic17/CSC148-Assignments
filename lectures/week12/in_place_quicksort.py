"""An implementation of in-place quicksort.

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto
"""
from typing import Any, List, Tuple


################################################################################
# In-place quicksort
################################################################################
def in_place_quicksort(lst: List[int]) -> None:
    """Mutate <lst> so that it is sorted.

    >>> lst = [10, 2, 5, -6, 17, 10]
    >>> in_place_quicksort(lst)
    >>> lst
    [-6, 2, 5, 10, 10, 17]
    """
    _in_place_quicksort(lst, 0, len(lst))


def _in_place_quicksort(lst: List[int], start: int, end: int) -> None:
    """Mutate <lst> so that the range lst[start:end] is sorted.

    The main recursive helper for in_place_quicksort.
    """
    if end - start < 2:
        # Do nothing; lst[start:end] is already sorted
        pass
    else:
        pivot_index = _in_place_partition(lst, start, end)
        _in_place_quicksort(lst, start, pivot_index)
        _in_place_quicksort(lst, pivot_index + 1, end)


def _in_place_partition(lst: List[int], start: int, end: int) -> int:
    """Mutate <lst> so that it is partitioned with pivot lst[0].

    Let pivot = lst[0].
    The elements of <lst> are moved around so that the final list looks like

        [x1, x2, ... x_m, pivot, y1, y2, ... y_n],

    where each of the x's is less than or equal to the pivot,
    and each of the y's is greater than the pivot.

    The *new index of the pivot* is returned.

    Precondition: lst != [].

    >>> lst = [10, 3, 20, 5, -6, 30, 7]
    >>> _in_place_partition(lst, 0, 7)  # Pivot is 10
    4
    >>> lst[4]  # Note that 10 is at index 4
    10
    >>> set(lst[:4]) == {3, 5, -6, 7}
    True
    >>> set(lst[5:]) == {20, 30}
    True
    """
    pivot = lst[start]
    small_i = start + 1
    big_i = end

    while small_i < big_i:
        if lst[small_i] < pivot:
            small_i += 1
        else:
            lst[small_i], lst[big_i - 1] = lst[big_i - 1], lst[small_i]
            big_i -= 1

    # Move the pivot to the right location
    lst[start], lst[small_i - 1] = lst[small_i - 1], lst[start]

    return small_i - 1


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all()
