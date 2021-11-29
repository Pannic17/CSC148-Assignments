"""CSC148 Assignment 1 - People and Elevators

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This module contains classes for the two "basic" entities in this simulation:
people and elevators. We have provided basic outlines of these two classes
for you; you are responsible for implementing these two classes so that they
work with the rest of the simulation.

You may NOT change any existing attributes, or the interface for any public
methods we have provided. However, you can (and should) add new attributes,
and of course you'll have to implement the methods we've provided, as well
as add your own methods to complete this assignment.

Finally, note that Person and Elevator each inherit from a kind of sprite found
in sprites.py; this is to enable their instances to be visualized properly.
You may not change sprites.py, but are responsible for reading the documentation
to understand these classes, as well as the abstract methods your classes must
implement.
"""
from __future__ import annotations
from typing import List
from sprites import PersonSprite, ElevatorSprite


class Elevator(ElevatorSprite):
    """An elevator in the elevator simulation.

    Remember to add additional documentation to this class docstring
    as you add new attributes (and representation invariants).

    === Attributes ===
    passengers: A list of the people currently on this elevator

    === Representation invariants ===
    """
    passengers: List[Person]
    floor: int
    capacity: int

    def __init__(self,
                 person: List[Person],
                 capacity: int) -> None:
        self.passengers = person
        self.floor = 1
        self.capacity = capacity
        ElevatorSprite.__init__(self)

    def is_full(self) -> bool:
        """check whether the elevator is full or not"""
        return len(self.passengers) >= self.capacity

    def is_empty(self) -> bool:
        """check whether the elevator is empty or not"""
        return len(self.passengers) == 0

    def fullness(self) -> float:
        """return the fullness of the elevator"""
        return float(len(self.passengers) / self.capacity)


class Person(PersonSprite):
    """A person in the elevator simulation.

    === Attributes ===
    start: the floor this person started on
    target: the floor this person wants to go to
    wait_time: the number of rounds this person has been waiting

    === Representation invariants ===
    start >= 1
    target >= 1
    wait_time >= 0
    """
    start: int
    target: int
    wait_time: int

    def __init__(self) -> None:
        self.start = 1
        self.target = 1
        self.wait_time = 0
        PersonSprite.__init__(self)

    def get_start(self, start: int) -> None:
        """set the start floor"""
        self.start = start

    def get_target(self, target: int) -> None:
        """set the target floor"""
        self.target = target

    def waited(self) -> None:
        """make those people wait"""
        self.wait_time += 1

    def get_anger_level(self) -> int:
        """Return this person's anger level.

        A person's anger level is based on how long they have been waiting
        before reaching their target floor.
            - Level 0: waiting 0-2 rounds
            - Level 1: waiting 3-4 rounds
            - Level 2: waiting 5-6 rounds
            - Level 3: waiting 7-8 rounds
            - Level 4: waiting >= 9 rounds
        """
        # self.waited()
        if self.wait_time == 0:
            return 0
        elif self.wait_time >= 9:
            return 4
        else:
            return (self.wait_time - 1) // 2


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['sprites'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
