"""Profile BST operations

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains some code for running some timing experiments on
binary search trees.
"""
import random
import sys
from timeit import timeit
import matplotlib.pyplot as plt

from bst import BinarySearchTree


if __name__ == '__main__':
    sys.setrecursionlimit(10000)

    SIZES = [200, 400, 800, 1600, 3200]
    NUM_TRIALS = 100

    all_sizes = []
    sorted_times = []

    for size in SIZES:
        bst = BinarySearchTree(None)
        for i in range(size):
            bst.insert(i)
        # print(bst.height())

        item = size  # Try this with different items!
        time = timeit('bst.__contains__(item)', number=NUM_TRIALS,
                      globals=globals())
        all_sizes.append(size)
        sorted_times.append(time)

    all_sizes2 = []
    random_times = []
    for size in SIZES:
        random_list = list(range(size))
        random.shuffle(random_list)
        bst = BinarySearchTree(None)
        for i in random_list:
            bst.insert(i)
        # print(bst.height())

        item = size  # Try this with different items!
        time = timeit('bst.__contains__(item)', number=NUM_TRIALS,
                      globals=globals())
        all_sizes2.append(size)
        random_times.append(time)

    plt.plot(all_sizes, sorted_times, 'ro',
             all_sizes2, random_times, 'bo')
    plt.axis([0, max(SIZES) + 200, 0, 0.5])
    plt.show()
