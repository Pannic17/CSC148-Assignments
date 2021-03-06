"""CSC148 Assignment 2: Autocomplete engines

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
import csv
from typing import Any, Dict, List, Optional, Tuple

from melody import Melody
from prefix_tree import SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines (Task 4)
################################################################################
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one alphanumeric character, it is inserted into the
        Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given a weight of one.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight (because of how Autocompleter.insert works).
        >>> lae = LetterAutocompleteEngine({'file': 'data/sample_test.txt', 'autocompleter': 'compressed', 'weight_type': 'sum'})
        >>> str(lae.autocompleter)
        []
        """
        # We've opened the file for you here. You should iterate over the
        # lines of the file and process them according to the description in
        # this method's docstring.
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        elif config['autocompleter'] == 'compressed':
            self.autocompleter = CompressedPrefixTree(config['weight_type'])
        file = []
        with open(config['file'], encoding='utf8') as f:
            for line in f:
                temp_1 = line.strip()
                temp_2 = temp_1.rstrip()
                temp_3 = temp_2.lower()
                file.append(temp_3)
        for line in file:
            prefix = []
            for char in line:
                if char.isalnum() or char.isspace():
                    prefix.append(char)
            index = 0
            for char in line:
                if not char.isalnum:
                    line = line[:index] + line[index + 1:]
                index += 1
            self.autocompleter.insert(line, 1, prefix)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        pre_list = []
        for char in prefix:
            pre_list.append(char)
        return self.autocompleter.autocomplete(pre_list, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        pre_list = []
        for char in prefix:
            pre_list.append(char)
        self.autocompleter.remove(pre_list)


class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has two entries:
            - the first entry is a string
            - the second entry is the a number representing the weight of that
              string

        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given THE WEIGHT SPECIFIED ON THE
        LINE FROM THE CSV FILE. (Updated Nov 19)
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        elif config['autocompleter'] == 'compressed':
            self.autocompleter = CompressedPrefixTree(config['weight_type'])
        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                """
                index = 0
                temp_1 = ''
                for char in line[0]:
                    if char.isalnum:
                        temp_1 += char
                    index += 1
                temp_2 = temp_1.lower()
                """
                temp_1 = ''
                prefix = split(line[0])
                for letter in prefix:
                    temp_1 += (letter + ' ')
                temp_2 = temp_1.rstrip()
                temp_3 = temp_2.lower()
                if len(line) > 0:
                    self.autocompleter.insert(temp_3, float(line[1]), prefix)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        pre_list = prefix.split()
        return self.autocompleter.autocomplete(pre_list, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        pre_list = prefix.split()
        self.autocompleter.remove(pre_list)


################################################################################
# Melody-based Autocomplete Engines (Task 5)
################################################################################
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    # === Private Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs (as in Assignment 1)
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.

            HOWEVER, there may be blank entries (stored as an empty string '');
            as soon as you encounter a blank entry, stop processing this line
            and move onto the next line the CSV file.

        Each melody is be inserted into the Autocompleter with a weight of 1.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        elif config['autocompleter'] == 'compressed':
            pass
        with open(config['file']) as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                melo = melody_init(line)
                prefix = get_interval(melo.notes)
                self.autocompleter.insert(melo, 1, prefix)

    def autocomplete(self, prefix: List[int],
                     limit: Optional[int] = None) -> List[Tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """
        return self.autocompleter.autocomplete(prefix, limit)

    def remove(self, prefix: List[int]) -> None:
        """Remove all melodies that match the given interval sequence.
        """
        self.remove(prefix)


###############################################################################
# Helper Function /Static
###############################################################################
def split(string: str) -> List[str]:
    """
    Split the lines and return proper List of str
    >>> a = 'What the hell is that!'
    >>> split(a)
    ['what', 'the', 'hell', 'is', 'that']
    """
    output = string.split()
    index = 0
    for item in output:
        if item.isalnum():
            output[index] = output[index].lower()
        else:
            filtered = list(filter(str.isalnum, item))
            empty = ''
            temp = empty.join(filtered)
            output[index] = temp
            output[index] = output[index].lower()
        index += 1
    return output


def melody_init(line: List[str]) -> Melody:
    """
    >>> m = ['fernando', '45', '500']
    >>> output = melody_init(m)
    >>> output.name
    'fernando'
    >>> output.notes
    [(45, 500)]
    """
    notes = []
    index = 1
    length = len(line)
    while index < length and line[index].isnumeric():
        note = (int(line[index]), int(line[index + 1]))
        notes.append(note)
        index += 2
    return Melody(line[0], notes)


def get_interval(notes: List[Tuple[int, int]]) -> List[int]:
    """
    Helper Function / to get the interval
    """
    output = []
    for index in range(1, len(notes)):
        output.append((notes[index][0] - notes[index - 1][0]))
    return output


###############################################################################
# Sample runs
###############################################################################
def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine."""
    engine = LetterAutocompleteEngine({
        # NOTE: you should also try 'data/google_no_swears.txt' for the file.
        'file': 'data/lotr.txt',
        'autocompleter': 'compressed',
        'weight_type': 'sum'
    })
    return engine.autocomplete('frodo d', 20)


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine."""
    engine = SentenceAutocompleteEngine({
        'file': 'data/google_searches.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    return engine.autocomplete('how to', 20)


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine."""
    engine = MelodyAutocompleteEngine({
        'file': 'data/random_melodies_c_scale.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    melodies = engine.autocomplete([2, 2], 20)
    for melody, _ in melodies:
        melody.play()


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['csv', 'prefix_tree', 'melody']
    })

    # This is used to increase the recursion limit so that your sample runs
    # work even for fairly tall simple prefix trees.
    # import sys
    # sys.setrecursionlimit(5000)

    # print(sample_letter_autocomplete())
    # print(sample_sentence_autocomplete())
    # sample_melody_autocomplete()
    """
    with open('data/lotr.txt', encoding='utf8') as f:
        max_len = 0
        for line in f.readlines():
            line = line.rstrip()
            prefix = []
            line_len = len(line)
            max_len = max(line_len,max_len)
            for char in line:
                if char.isalnum():
                    char.lower()
                    prefix.append(char)
                elif char.isspace():
                    prefix.append(char)
                else:
                    line = line.replace(char, '')

        print(max_len)
    """
