import random
from typing import Any, Callable, List
from timeit import timeit

import matplotlib.pyplot as plt

from sorting import mergesort, quicksort, insertion_sort


SIZES = [1000, 2000, 3000, 4000, 8000, 16000]
NUM_TRIALS = 5


def profile_alg(sizes: List[int], alg: Callable[[List], Any],
                shuffle: bool = True) -> List[int]:
    """Return a list of times for the algorithm."""
    times = []
    for size in sizes:
        for _ in range(NUM_TRIALS):
            lst = list(range(size))
            if shuffle:
                random.shuffle(lst)

            time = timeit('alg(lst)', number=1, globals=locals())
            times.append(time)
    return times


if __name__ == '__main__':
    import sys
    sys.setrecursionlimit(20000)

    mergesort_times = profile_alg(SIZES, mergesort, shuffle=True)
    quicksort_times = profile_alg(SIZES, quicksort, shuffle=True)
    insertion_sort_times = profile_alg(SIZES, insertion_sort, shuffle=True)

    all_times = [x for x in SIZES for _ in range(NUM_TRIALS)]
    plt.plot(all_times, mergesort_times, 'ro', label='mergesort')
    plt.plot(all_times, quicksort_times, 'bo', label='quicksort')
    plt.plot(all_times, insertion_sort_times, 'go', label='insertion sort')

    # We calculate the x- and y-axis ranges based on the datasets.
    plt.axis([0, max(SIZES) + 100, 0,
              1.05 * max(mergesort_times + quicksort_times + insertion_sort_times)])
    plt.legend()
    plt.show()
