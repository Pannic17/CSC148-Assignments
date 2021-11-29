"""CSC148 Assignment 1 - Algorithms

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains two sets of algorithms: ones for generating new arrivals to
the simulation, and ones for making decisions about how elevators should move.

As with other files, you may not change any of the public behaviour (attributes,
methods) given in the starter code, but you can definitely add new attributes
and methods to complete your work here.

See the 'Arrival generation algorithms' and 'Elevator moving algorithsm'
sections of the assignment handout for a complete description of each algorithm
you are expected to implement in this file.
"""
import csv
from enum import Enum
import random
from typing import Dict, List, Optional

from entities import Person, Elevator


###############################################################################
# Arrival generation algorithms
###############################################################################
class ArrivalGenerator:
    """An algorithm for specifying arrivals at each round of the simulation.

    === Attributes ===
    max_floor: The maximum floor number for the building.
               Generated people should not have a starting or target floor
               beyond this floor.
    num_people: The number of people to generate, or None if this is left
                up to the algorithm itself.

    === Representation Invariants ===
    max_floor >= 2
    num_people is None or num_people >= 0
    """
    max_floor: int
    num_people: Optional[int]

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        """Initialize a new ArrivalGenerator.

        Preconditions:
            max_floor >= 2
            num_people is None or num_people >= 0
        """
        self.max_floor = max_floor
        self.num_people = num_people

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        """Return the new arrivals for the simulation at the given round.

        The returned dictionary maps floor number to the people who
        arrived starting at that floor.

        You can choose whether to include floors where no people arrived.
        """
        raise NotImplementedError


class RandomArrivals(ArrivalGenerator):
    """Generate a fixed number of random people each round.

    Generate 0 people if self.num_people is None.

    For our testing purposes, this class *must* have the same initializer header
    as ArrivalGenerator. So if you choose to to override the initializer, make
    sure to keep the header the same!

    Hint: look up the 'sample' function from random.
    """

    def __init__(self, max_floor: int, num_people: Optional[int]) -> None:
        if num_people is None:
            ArrivalGenerator.__init__(self, max_floor, 0)
        elif isinstance(num_people, int):
            ArrivalGenerator.__init__(self, max_floor, num_people)

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        generated = {}
        for _ in range(self.num_people):
            start = random.randint(1, self.max_floor)
            target = start
            while target == start:
                target = random.randint(1, self.max_floor)
            person = Person()
            person.get_start(start)
            person.get_target(target)
            if start in generated:
                generated[start].append(person)
            else:
                generated[start] = [person]
        return generated


class FileArrivals(ArrivalGenerator):
    """Generate arrivals from a CSV file.
    initial: the lines read from CSV file
    spawn_round: the round people spawn,
    the first parameter of each row of CSV file
    """
    initial: Dict[str, List[str]]

    def __init__(self, max_floor: int, filename: str) -> None:
        """Initialize a new FileArrivals algorithm from the given file.

        The num_people attribute of every FileArrivals instance is set to None,
        since the number of arrivals depends on the given file.

        Precondition:
            <filename> refers to a valid CSV file, following the specified
            format and restrictions from the assignment handout.
        """
        ArrivalGenerator.__init__(self, max_floor, None)

        # We've provided some of the "reading from csv files" boilerplate code
        # for you to help you get started.
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            self.initial = {}
            for line in reader:
                # TODO: complete this. <line> is a list of strings corresponding
                # to one line of the original file.
                # You'll need to convert the strings to ints and then process
                # and store them.
                for index in range(1, len(line)):
                    line[index] = int(line[index])
                self.initial[line[0]] = line[1:]

    def generate(self, round_num: int) -> Dict[int, List[Person]]:
        generated = {}
        if str(round_num) in self.initial:
            list_of_csv = self.initial[str(round_num)]
            for index in range(1, len(list_of_csv), 2):
                start = int(list_of_csv[index - 1])
                target = int(list_of_csv[index])
                person = Person()
                person.get_start(start)
                person.get_target(target)
                if start in generated:
                    generated[start].append(person)
                else:
                    generated[start] = [person]
        else:
            generated[round_num] = []
        return generated


###############################################################################
# Direction
###############################################################################
class Direction(Enum):
    """
    The following defines the possible directions an elevator can move.
    This is output by the simulation's algorithms.

    The possible values you'll use in your Python code are:
        Direction.UP, Direction.DOWN, Direction.STAY
    """
    UP = 1
    STAY = 0
    DOWN = -1


###############################################################################
# Helper Function
###############################################################################
def get_direction(int_direction: int) -> Direction:
    """
    helper function to covert int into Direction
    """
    if int_direction == 1:
        return Direction.UP
    elif int_direction == 0:
        return Direction.STAY
    elif int_direction == -1:
        return Direction.DOWN
    else:
        # This never runs!
        assert False
        return 'Debug'


def lowest_waiting(waiting: Dict[int, List[Person]], max_floor: int) -> int:
    """return the lowest floor with person waiting"""
    low = max_floor + 1
    for floor in waiting:
        if len(waiting[floor]) != 0 and floor < low:
            low = floor
    if low != (max_floor + 1):
        return low
    else:
        return 0


def closest_waiting(waiting: Dict[int, List[Person]],
                    max_floor: int,
                    current_floor: int) -> int:
    """return the closest floor with person waiting"""
    gap = max_floor + 1
    close = 0
    for floor in waiting:
        if len(waiting[floor]) != 0 and abs(floor - current_floor) < gap:
            gap = abs(floor - current_floor)
            close = floor
    return close


def nearest(passenger: List[Person],
            max_floor: int,
            current_floor: int) -> int:
    """return the nearest floor with person waiting"""
    gap = max_floor + 1
    near = 0
    for person in passenger:
        if abs(person.target - current_floor) < gap:
            gap = abs(person.target - current_floor)
            near = person.target
    return near


def check_direction(target_floor: int, current_floor: int) -> Direction:
    """check the direction of elevator"""
    if target_floor in [current_floor, 0]:
        return Direction.STAY
    elif target_floor > current_floor:
        return Direction.UP
    elif target_floor < current_floor:
        return Direction.DOWN
    else:
        # This never runs!
        assert False
        return 'Debug'


###############################################################################
# Elevator moving algorithms
###############################################################################
class MovingAlgorithm:
    """An algorithm to make decisions for moving an elevator at each round.
    """
    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        """Return a list of directions for each elevator to move to.

        As input, this method receives the list of elevators in the simulation,
        a dictionary mapping floor number to a list of people waiting on
        that floor, and the maximum floor number in the simulation.

        Note that each returned direction should be valid:
            - An elevator at Floor 1 cannot move down.
            - An elevator at the top floor cannot move up.
        """
        raise NotImplementedError


class RandomAlgorithm(MovingAlgorithm):
    """A moving algorithm that picks a random direction for each elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        list_directions = []
        for elevator in elevators:
            int_direction = 2
            while (elevator.floor + int_direction) > max_floor or \
                    (elevator.floor + int_direction) < 1 or \
                    int_direction == 2:
                int_direction = random.randint(-1, 1)
            list_directions.append(get_direction(int_direction))
        return list_directions


class PushyPassenger(MovingAlgorithm):
    """A moving algorithm that preferences the first passenger on each elevator.

    If the elevator is empty, it moves towards the *lowest* floor that has at
    least one person waiting, or stays still if there are no people waiting.
    If the elevator isn't empty, it moves towards the target floor of the
    *first* passenger who boarded the elevator.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        list_directions = []
        for elevator in elevators:
            if elevator.is_empty():
                target_floor = lowest_waiting(waiting, max_floor)
                list_directions.append(
                    check_direction(target_floor, elevator.floor))
            else:
                for person in elevator.passengers:
                    list_directions.append(
                        check_direction(person.target, elevator.floor))
        return list_directions


class ShortSighted(MovingAlgorithm):
    """A moving algorithm that preferences the closest possible choice.

    If the elevator is empty, it moves towards the *closest* floor that has at
    least one person waiting, or stays still if there are no people waiting.

    If the elevator isn't empty, it moves towards the closest target floor of
    all passengers who are on the elevator.

    In this case, the order in which people boarded does *not* matter.
    """

    def move_elevators(self,
                       elevators: List[Elevator],
                       waiting: Dict[int, List[Person]],
                       max_floor: int) -> List[Direction]:
        list_directions = []
        for elevator in elevators:
            if elevator.is_empty():
                target_floor = closest_waiting(waiting,
                                               max_floor,
                                               elevator.floor)
                list_directions.append(
                    check_direction(target_floor, elevator.floor))
            else:
                target_floor = nearest(elevator.passengers,
                                       max_floor,
                                       elevator.floor)
                list_directions.append(
                    check_direction(target_floor, elevator.floor))
        return list_directions


if __name__ == '__main__':
    # Don't forget to check your work regularly with python_ta!
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['__init__'],
        'extra-imports': ['entities', 'random', 'csv', 'enum'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
