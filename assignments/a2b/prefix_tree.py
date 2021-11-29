"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    weight_cal: List[int]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type
        self.weight_cal = [0, 0]

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        length = 0
        if self.is_leaf():
            return 1
        else:
            for subtree in self.subtrees:
                length += subtree.__len__()
        return length

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n' + f'{depth}'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    ############################################################################
    # Task 1 / insert
    ############################################################################
    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """
        Insert the given value into this Autocompleter.
        >>> spt1 = SimplePrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c','a', 'r'])
        >>> spt1.value
        []
        >>> spt1.subtrees[0].value
        ['c']
        >>> spt1.subtrees[0].subtrees[0].value
        ['c', 'a']
        >>> spt1.subtrees[0].subtrees[0].subtrees[0].value
        ['c', 'a', 'r']
        >>> spt1.subtrees[0].subtrees[0].subtrees[0].subtrees[0].value
        'car'
        >>> spt2 = SimplePrefixTree('average')
        >>> spt2.insert('a', 2.0, ['a'])
        >>> spt2.insert('a', 6.0, ['a'])
        >>> spt2.value
        []
        >>> spt2.subtrees[0].value
        ['a']
        >>> spt2.subtrees[0].subtrees[0].value
        'a'
        >>> spt2.weight
        4.0
        >>> spt1.insert('cat', 2.0, ['c', 'a', 't'])
        >>> spt1.insert('danger', 2.0, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> spt1.insert('care', 2.0, ['c', 'a', 'r', 'e'])
        >>> str(spt1)
        []
        >>> spt2.insert('as', 8.0, ['a', 's'])
        >>> str(spt2)
        []
        >>> spt2.insert([1, 2, 3], 6.0, [1, 2, 3])
        >>> spt2.insert('sample test', 6.0, ['sample', 'test'])
        >>> str(spt2)
        []
        """
        num = 0
        self.weight_add(weight)
        self.insert_helper(value, weight, prefix, num)

    def insert_helper(self, value: Any, weight: float,
                      prefix: List[SimplePrefixTree], num: int) -> None:
        """
        Helper Function for /Function insert
        /Recursion
        """
        if prefix[:num] == prefix:
            self.subtrees.append(SimplePrefixTree(self.weight_type))
            self.subtrees[0].value = value
            self.subtrees[0].weight_add(weight)
        else:
            index = get_subtree_index(self.subtrees, prefix[:(num + 1)])
            if index == -1:
                """create new SPT"""
                self.subtrees.append(SimplePrefixTree(self.weight_type))
                self.subtrees[index].value = prefix[:(num + 1)]
                self.subtrees[index].weight_add(weight)
            else:
                """append value in old SPT"""
                self.subtrees[index].value = prefix[:(num + 1)]
                self.subtrees[index].weight_add(weight)
            self.subtrees[index].insert_helper(value, weight, prefix, (num + 1))

    def weight_add(self, weight: float) -> None:
        """
        Helper Function modifies the value of weight
        """
        if self.weight_type == 'sum':
            self.weight += weight
            self.weight_cal[0] += weight
            self.weight_cal[1] += 1
        elif self.weight_type == 'average':
            if self.is_leaf():
                self.weight_cal[0] += weight
                self.weight += weight
            else:
                self.weight_cal[0] += weight
                self.weight_cal[1] += 1
                self.weight = self.weight_cal[0] / self.weight_cal[1]

    ############################################################################
    # Task 2 / autocomplete
    ############################################################################
    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        >>> spt1 = SimplePrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.5, ['c', 'a', 't'])
        >>> spt1.insert('dog', 5.0, ['d', 'o', 'g'])
        >>> spt1.insert('rat', 1.0, ['r', 'a', 't'])
        >>> spt1.insert('care', 3.0, ['c', 'a', 'r', 'e'])
        >>> str(spt1)
        []
        >>> spt1.autocomplete(['c', 'a'])
        [('care', 3.0), ('cat', 2.5), ('car', 2.0)]
        >>> spt1.autocomplete(['c', 'a'], 2)
        [('care', 3.0), ('cat', 2.5)]
        >>> spt2 = SimplePrefixTree('average')
        >>> spt2.insert('a', 2.0, ['a'])
        >>> spt2.insert('as', 4.0, ['a', 's'])
        >>> spt2.insert([1, 2, 3], 6.0, [1, 2, 3])
        >>> spt2.insert([1, 2, 5], 8.0, [1, 2, 5])
        >>> str(spt2)
        []
        >>> spt2.autocomplete([1])
        [([1, 2, 5], 8.0), ([1, 2, 3], 6.0)]
        """
        unsorted = self.autocomplete_helper(prefix)
        if limit is None:
            unsorted.sort(key=lambda tup: tup[1], reverse=True)
            return unsorted
        else:
            return unsorted[:limit]

    def autocomplete_helper(self, prefix: List) -> List[Tuple[Any, float]]:
        """
        Helper function for /Function autocomplete
        /Recursion
        >>> spt1 = SimplePrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.5, ['c', 'a', 't'])
        >>> spt1.insert('dog', 5.0, ['d', 'o', 'g'])
        >>> spt1.insert('rat', 1.0, ['r', 'a', 't'])
        >>> str(spt1)
        []
        >>> spt1.autocomplete_helper(['c', 'a'])
        [('car', 2.0), ('cat', 2.5)]
        >>> spt1.autocomplete_helper(['r'])
        [('rat', 1.0)]
        """
        output = []
        if self.is_leaf():
            matched_tuple = (self.value, self.weight)
            return [matched_tuple]
        else:
            if compare_list(self.value, prefix):
                list_index = sort_trees(self.subtrees)
                for index in list_index:
                    output.extend(self.subtrees[index].autocomplete_helper(prefix))
        return output

    ############################################################################
    # Task 3 / remove
    ############################################################################
    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        >>> spt1 = SimplePrefixTree('sum')
        >>> spt1.insert('car', 1.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.0, ['c', 'a', 't'])
        >>> spt1.insert('dog', 3.0, ['d', 'o', 'g'])
        >>> spt1.insert('rat', 4.0, ['r', 'a', 't'])
        >>> str(spt1)
        []
        >>> spt1.subtrees[0].subtrees[0].weight_cal
        []
        >>> spt1.remove(['c', 'a'])
        >>> str(spt1)
        []
        >>> spt1.remove(['r'])
        >>> str(spt1)
        []
        >>> spt1.remove(['d', 'o'])
        >>> str(spt1)
        []
        """
        if self.is_leaf():
            pass
        elif self.value == prefix:
            self.subtrees = []
            self.weight = 0.0
            self.weight_cal = self.weight_cal[:2] + self.weight_cal[:2]
            self.weight_cal[0] = 0
            self.weight_cal[1] = 0
        else:
            if compare_list(self.value, prefix):
                for subtree in self.subtrees:
                    subtree.remove(prefix)
                    if subtree.is_empty():
                        self.subtrees.remove(subtree)
                        """
                        if (self.weight_cal[1] - subtree.weight_cal[3]) == 0:
                            self.weight = 0.0
                            self.weight_cal += self.weight_cal
                            self.weight_cal[0] = 0
                            self.weight_cal[1] = 0
                        else:
                            self.weight = (self.weight_cal[0] -
                             subtree.weight_cal[2]) /
                              (self.weight_cal[1] -
                               subtree.weight_cal[3])
                            self.weight_cal[0] -= subtree.weight_cal[2]
                            self.weight_cal[1] -= subtree.weight_cal[3]
                            self.weight_cal.append(subtree.weight_cal[2])
                            self.weight_cal.append(subtree.weight_cal[3])
                        """
                        self.weight_minus(subtree)

    def weight_minus(self, subtree: SimplePrefixTree) -> None:
        """
        Helper Function
        """
        if self.weight_type == 'sum':
            self.weight -= subtree.weight_cal[2]
            self.weight_cal[0] = 0
            self.weight_cal.append(subtree.weight_cal[2])
        elif self.weight_type == 'average':
            if (self.weight_cal[1] - subtree.weight_cal[3]) == 0:
                self.weight = 0.0
                self.weight_cal += self.weight_cal
                self.weight_cal[0] = 0
                self.weight_cal[1] = 0
            else:
                self.weight = (self.weight_cal[0] - subtree.weight_cal[2]) / (
                            self.weight_cal[1] - subtree.weight_cal[3])
                self.weight_cal[0] -= subtree.weight_cal[2]
                self.weight_cal[1] -= subtree.weight_cal[3]
                self.weight_cal.append(subtree.weight_cal[2])
                self.weight_cal.append(subtree.weight_cal[3])


################################################################################
# Helper Function /Static
################################################################################
def get_subtree_index(
        subtrees: List[Optional[SimplePrefixTree, CompressedPrefixTree]],
        prefix: List) -> int:
    """
    Helper Function to get the index of certain subtree needed.
    Return -1 only if the prefix list is not in the subtrees
    /Static
    """
    check_list = []
    for subtree in subtrees:
        check_list.append(subtree.value)
    if prefix in check_list:
        return check_list.index(prefix)
    else:
        return -1


def compare_list(list_a: List, list_b: List) -> bool:
    """
    Helper Function of comparing two list and determine their relation ship
    Return true if  list_a contains list_b
                or  list_b contains list_a
                or  they are the same
    /Static
    >>> compare_list([1, 2], [1, 2, 3])
    True
    >>> compare_list([], [1, 2])
    True
    >>> compare_list([1], [3])
    False
    """
    len_a = len(list_a)
    len_b = len(list_b)
    if len_a > len_b:
        return list_a[:len_b] == list_b
    elif len_b > len_a:
        return list_b[:len_a] == list_a
    else:
        return list_a == list_b


def sort_trees(list_trees: List) -> List[int]:
    index = 0
    list_tup = []
    for tree in list_trees:
        index_tup = (index, tree.weight)
        list_tup.append(index_tup)
        index += 1
    list_tup.sort(key=lambda tup: tup[1], reverse=True)
    output = []
    for tups in list_tup:
        output.append(tups[0])
    return output


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    weight_type: str
    weight_cal: List[int]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type
        self.weight_cal = [0, 0]

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        length = 0
        if self.is_leaf():
            return 1
        else:
            for subtree in self.subtrees:
                length += subtree.__len__()
        return length

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def is_internal(self) -> bool:
        """
        >>> spt1 = CompressedPrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c','a', 'r'])
        >>> spt1.is_internal()
        True
        """
        return len(self.subtrees) == 1 and not (self.subtrees[0].is_leaf())

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n' + f'{depth}'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    ############################################################################
    # Task 6-1 / insert
    ############################################################################
    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """
        Insert the given value into this Autocompleter.
        >>> spt1 = CompressedPrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.0, ['c', 'a', 't'])
        >>> str(spt1)
        []
        >>> spt1.insert('cap', 2.0, ['c', 'a', 'p'])
        >>> str(spt1)
        >>> spt1.insert('care', 2.0, ['c', 'a', 'r', 'e'])
        >>> str(spt1)
        []
        >>> spt1.insert('danger', 2.0, ['d', 'a', 'n', 'g', 'e', 'r'])
        >>> str(spt1)
        []
        >>> spt1.insert('dog', 2.0, ['d', 'o', 'g'])
        >>> str(spt1)
        []
        >>> spt1.insert('donation', 2.0, ['d', 'o', 'a', 't', 'i', 'o', 'n'])
        >>> str(spt1)
        []
        >>> spt2 = CompressedPrefixTree('average')
        >>> spt2.insert('a', 2.0, ['a'])
        >>> spt2.insert('a', 6.0, ['a'])
        >>> spt2.insert('as', 4.0, ['a', 's'])
        >>> spt2.insert([1, 2, 3], 6.0, [1, 2, 3])
        >>> spt2.insert('sample test', 15.0, ['sample', 'test'])
        >>> str(spt2)
        []
        """
        num = 0
        self.weight_add(weight)
        self.insert_helper(value, weight, prefix, num)
        for times in range(len(prefix)):
            self.insert_delete(prefix)

    def insert_helper(self, value: Any, weight: float,
                      prefix: List[SimplePrefixTree], num: int) -> None:
        """
        Helper Function for /Function insert
        /Recursion
        """
        if prefix[:num] == prefix:
            self.subtrees.append(CompressedPrefixTree(self.weight_type))
            self.subtrees[0].value = value
            self.subtrees[0].weight_add(weight)
        else:
            index = get_subtree_index(self.subtrees, prefix[:(num + 1)])
            if index == -1:
                # create new CPT
                temp_trees = []
                for subtree in self.subtrees:
                    if subtree.value[:num + 1] == prefix[:num + 1]:
                        temp_trees.append(subtree)
                        self.subtrees.remove(subtree)
                self.subtrees.append(CompressedPrefixTree(self.weight_type))
                self.subtrees[index].value = prefix[:(num + 1)]
                self.subtrees[index].weight_add(weight)
                self.subtrees[index].subtrees.extend(temp_trees)
                for tree in temp_trees:
                    self.subtrees[index].weight += tree.weight
                    self.subtrees[index].weight_cal[0] += tree.weight_cal[0]
                    self.subtrees[index].weight_cal[1] += tree.weight_cal[1]
            else:
                # append value in old CPT
                self.subtrees[index].value = prefix[:(num + 1)]
                self.subtrees[index].weight_add(weight)
            self.subtrees[index].insert_helper(value, weight, prefix, (num + 1))

    def insert_delete(self, prefix: List) -> None:
        if self.is_leaf():
            pass
        else:
            if compare_list(self.value, prefix):
                for subtree in self.subtrees:
                    if subtree.is_internal():
                        temp_tree = subtree.subtrees
                        self.subtrees.remove(subtree)
                        self.subtrees.extend(temp_tree)
                    subtree.insert_delete(prefix)

    def weight_add(self, weight: float) -> None:
        """
        Helper Function modifies the value of weight
        """
        if self.weight_type == 'sum':
            self.weight += weight
            self.weight_cal[0] += weight
            self.weight_cal[1] += 1
        elif self.weight_type == 'average':
            self.weight_cal[0] += weight
            self.weight_cal[1] += 1
            self.weight = self.weight_cal[0] / self.weight_cal[1]

    # Version B/ Failure
        # def insert_helper(self, value: Any, weight: float,
        # prefix: List[CompressedPrefixTree], num: int) -> None:
        """
        Helper Function for /Function insert
        /Recursion
        """
        """
        if prefix[:num] == prefix:
            self.subtrees.append(CompressedPrefixTree(self.weight_type))
            self.subtrees[-1].value = value
            self.subtrees[-1].weight_add(weight)
        else:
            check_list = []
            diff_index = 0
            position_to_remove = 0
            for subtree in self.subtrees:
                check_list.append(subtree.value)
                if get_diff(subtree.value, prefix) != 0:
                    diff_index = 
                        max(get_diff(subtree.value, prefix), diff_index)
                    position_to_remove = check_list.index(subtree.value)
            if diff_index == 0:
                # Create list with leaf
                self.subtrees.append(CompressedPrefixTree(self.weight_type))
                self.subtrees[-1].value = prefix
                self.subtrees[-1].weight_add(weight)
                self.subtrees[-1].insert_helper(
                    value, weight, prefix, len(prefix) + 1)
            else:
                # Create give length list to insert
                if prefix[:diff_index] in check_list:
                    # Check whether there is an existing list
                    exist_index = check_list.index(prefix[:diff_index])
                    self.subtrees[exist_index].value = prefix[:diff_index]
                    self.subtrees[exist_index].weight_add(weight)
                    diff_index -= 1
                    self.subtrees[exist_index].insert_helper(
                        value, weight, prefix, diff_index + 1)
                elif diff_index >= len(self.subtrees[position_to_remove].value):
                    self.subtrees.append(CompressedPrefixTree(self.weight_type))
                    self.subtrees[-1].value = prefix[:num + 1]
                    self.subtrees[-1].weight_add(weight)
                    self.subtrees[-1].insert_helper(
                        value, weight, prefix, num + 1)
                else:
                    temp_subtree = self.subtrees[position_to_remove]
                    self.subtrees.remove(self.subtrees[position_to_remove])
                    self.subtrees.append(CompressedPrefixTree(self.weight_type))
                    self.subtrees[-1].value = prefix[:diff_index]
                    self.subtrees[-1].weight_add(temp_subtree.weight)
                    self.subtrees[-1].subtrees.append(temp_subtree)
                    curr_subtree = CompressedPrefixTree(self.weight_type)
                    curr_subtree.value = prefix[:diff_index + 1]
                    curr_subtree.weight = weight
                    self.subtrees[-1].weight_add(weight)
                    self.subtrees[-1].subtrees.append(curr_subtree)
                    self.subtrees[-1].insert_helper(
                        value, weight, prefix, diff_index + 1)
            # Version A
            index = get_subtree_index(self.subtrees, prefix[:(num + 1)])
            if index == -1:
                # create new SPT
                self.subtrees.append(CompressedPrefixTree(self.weight_type))
                self.subtrees[index].value = prefix
                self.subtrees[index].weight_add(weight)
                self.subtrees[index].insert_helper(value, weight, prefix,
                                                   len(prefix))
            else:
                # append value in old SPT
                self.subtrees[index].value = prefix[:(num + 1)]
                self.subtrees[index].weight_add(weight)
                self.subtrees[index].insert_helper(value, weight, prefix,
                                                   (num + 1))
            """

    ############################################################################
    # Task 6-2 / autocomplete
    ############################################################################
    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        >>> spt1 = CompressedPrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.5, ['c', 'a', 't'])
        >>> spt1.insert('dog', 5.0, ['d', 'o', 'g'])
        >>> spt1.insert('rat', 1.0, ['r', 'a', 't'])
        >>> spt1.insert('care', 3.0, ['c', 'a', 'r', 'e'])
        >>> str(spt1)
        []
        >>> spt1.autocomplete(['c'])
        [('care', 3.0), ('cat', 2.5), ('car', 2.0)]
        >>> spt1.autocomplete(['c', 'a'], 2)
        [('care', 3.0), ('cat', 2.5)]
        >>> spt2 = CompressedPrefixTree('average')
        >>> spt2.insert('a', 2.0, ['a'])
        >>> spt2.insert('as', 4.0, ['a', 's'])
        >>> spt2.insert([1, 2, 3], 6.0, [1, 2, 3])
        >>> spt2.insert([1, 2, 5], 8.0, [1, 2, 5])
        >>> str(spt2)
        []
        >>> spt2.autocomplete([1])
        [([1, 2, 5], 8.0), ([1, 2, 3], 6.0)]
        """
        unsorted = self.autocomplete_helper(prefix)
        if limit is None:
            unsorted.sort(key=lambda tup: tup[1], reverse=True)
            return unsorted
        else:
            return unsorted[:limit]

    def autocomplete_helper(self, prefix: List) -> List[Tuple[Any, float]]:
        """
        Helper function for /Function autocomplete
        /Recursion
        >>> spt1 = CompressedPrefixTree('sum')
        >>> spt1.insert('car', 2.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.5, ['c', 'a', 't'])
        >>> spt1.insert('dog', 5.0, ['d', 'o', 'g'])
        >>> spt1.insert('rat', 1.0, ['r', 'a', 't'])
        >>> str(spt1)
        []
        >>> spt1.autocomplete_helper(['c', 'a'])
        [('car', 2.0), ('cat', 2.5)]
        >>> spt1.autocomplete_helper(['r'])
        [('rat', 1.0)]
        """
        output = []
        if self.is_leaf():
            matched_tuple = (self.value, self.weight)
            return [matched_tuple]
        else:
            if compare_list(self.value, prefix):
                list_index = sort_trees(self.subtrees)
                for index in list_index:
                    output.extend(
                        self.subtrees[index].autocomplete_helper(prefix))
        return output

    ############################################################################
    # Task 6-3 / remove
    ############################################################################
    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        >>> spt1 = CompressedPrefixTree('sum')
        >>> spt1.insert('car', 1.0, ['c', 'a', 'r'])
        >>> spt1.insert('cat', 2.0, ['c', 'a', 't'])
        >>> spt1.insert('dog', 3.0, ['d', 'o', 'g'])
        >>> spt1.insert('rat', 4.0, ['r', 'a', 't'])
        >>> str(spt1)
        []
        >>> spt1.remove(['c', 'a'])
        >>> str(spt1)
        []
        >>> spt1.remove(['r'])
        >>> str(spt1)
        []
        >>> spt1.remove(['d', 'o'])
        >>> str(spt1)
        []
        """
        self.insert(prefix, -1.0, prefix)
        self.remove_helper(prefix)

    def remove_helper(self, prefix: List) -> None:
        if self.is_leaf():
            pass
        elif self.value == prefix:
            self.subtrees = []
            self.weight = 0.0
            self.weight_cal += self.weight_cal
            self.weight_cal[0] = 0
            self.weight_cal[1] = 0
        else:
            if compare_list(self.value, prefix):
                for subtree in self.subtrees:
                    subtree.remove_helper(prefix)
                    if subtree.is_empty():
                        self.subtrees.remove(subtree)
                        """
                        if (self.weight_cal[1] - subtree.weight_cal[3]) == 0:
                            self.weight = 0.0
                            self.weight_cal += self.weight_cal
                            self.weight_cal[0] = 0
                            self.weight_cal[1] = 0
                        else:
                            self.weight = (self.weight_cal[0] -
                             subtree.weight_cal[2]) /
                              (self.weight_cal[1] -
                               subtree.weight_cal[3])
                            self.weight_cal[0] -= subtree.weight_cal[2]
                            self.weight_cal[1] -= subtree.weight_cal[3]
                            self.weight_cal.append(subtree.weight_cal[2])
                            self.weight_cal.append(subtree.weight_cal[3])
                        """
                        self.weight_minus(subtree)

    def weight_minus(self, subtree: CompressedPrefixTree) -> None:
        """
        Helper Function
        """
        if self.weight_type == 'sum':
            self.weight -= subtree.weight_cal[2]
            self.weight_cal[0] -= subtree.weight_cal[2]
            self.weight_cal.append(subtree.weight_cal[2])
        elif self.weight_type == 'average':
            if (self.weight_cal[1] - subtree.weight_cal[3]) == 0:
                self.weight = 0.0
                self.weight_cal += self.weight_cal
                self.weight_cal[0] = 0
                self.weight_cal[1] = 0
            else:
                self.weight = (self.weight_cal[0] - subtree.weight_cal[2]) / (
                        self.weight_cal[1] - subtree.weight_cal[3])
                self.weight_cal[0] -= subtree.weight_cal[2]
                self.weight_cal[1] -= subtree.weight_cal[3]
                self.weight_cal.append(subtree.weight_cal[2])
                self.weight_cal.append(subtree.weight_cal[3])


def get_diff(list_a: List, list_b: List) -> int:
    """
    >>> get_diff(['c', 'a', 't'], ['c', 'a', 'r'])
    2
    >>> get_diff(['c', 'a', 'r'], ['c', 'a', 'r', 'e'])
    3
    """
    len_a = len(list_a)
    len_b = len(list_b)
    _len = min(len_a, len_b)
    for index in range(_len):
        if list_a[index] != list_b[index]:
            return index
    return min(len_a, len_b)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
