"""CSC148 Assignment 1 - Simulation

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This contains the main Simulation class that is actually responsible for
creating and running the simulation. You'll also find the function `sample_run`
here at the bottom of the file, which you can use as a starting point to run
your simulation on a small configuration.

Note that we have provided a fairly comprehensive list of attributes for
Simulation already. You may add your own *private* attributes, but should not
remove any of the existing attributes.
"""
# You may import more things from these modules (e.g., additional types from
# typing), but you may not import from any other modules.
from typing import Dict, List, Any

import algorithms
from algorithms import Direction
from entities import Person, Elevator
from visualizer import Visualizer


###############################################################################
# Helper Function
###############################################################################
def return_direction(direction: Direction) -> int:
    """
    helper function return int to calculate according to the direction given
    """
    if direction == Direction.UP:
        return 1
    elif direction == Direction.STAY:
        return 0
    elif direction == Direction.DOWN:
        return -1
    else:
        # This never runs!
        assert False
        return 'Debug'


###############################################################################
# Main
###############################################################################
class Simulation:
    """The main simulation class.

    === Attributes ===
    arrival_generator: the algorithm used to generate new arrivals.
    elevators: a list of the elevators in the simulation
    moving_algorithm: the algorithm used to decide how to move elevators
    num_floors: the number of floors
    visualizer: the Pygame visualizer used to visualize this simulation
    waiting: a dictionary of people waiting for an elevator
             (keys are floor numbers, values are the list of waiting people)
    round_stat: a dictionary of str record the stats
    waiting_people: a list of person record the current people in the elevator
                    and on the floor who are waiting for arrival
    people_time: a list of int record the arrived waiting times
    """
    arrival_generator: algorithms.ArrivalGenerator
    elevators: List[Elevator]
    moving_algorithm: algorithms.MovingAlgorithm
    num_floors: int
    visualizer: Visualizer
    waiting: Dict[int, List[Person]]
    round_stat: {str: int}
    waiting_people: List[Person]
    people_time: List[int]

    def __init__(self,
                 config: Dict[str, Any]) -> None:
        """Initialize a new simulation using the given configuration."""

        # Initialize the visualizer.
        # Note that this should be called *after* the other attributes
        # have been initialized.
        self.elevators = []
        index = 0
        while index < (config['num_elevators']):
            empty = []
            self.elevators.append(Elevator(empty, config['elevator_capacity']))

            index += 1
        self.num_floors = config['num_floors']
        self.visualizer = Visualizer(self.elevators,  # should be self.elevators
                                     self.num_floors,   # should self.num_floors
                                     config['visualize'])
        self.waiting = {}
        self.round_stat = {
            'num_iterations': 0,
            'total_people': 0,
            'people_completed': 0,
            'max_time': 0,
            'min_time': 0,
            'avg_time': 0
        }
        self.waiting_people = []
        self.people_time = []
        self.moving_algorithm = config['moving_algorithm']
        self.arrival_generator = config['arrival_generator']

    ############################################################################
    # Handle rounds of simulation.
    ############################################################################
    def run(self, num_rounds: int) -> Dict[str, Any]:
        """Run the simulation for the given number of rounds.

        Return a set of statistics for this simulation run, as specified in the
        assignment handout.

        Precondition: num_rounds >= 1.

        Note: each run of the simulation starts from the same initial state
        (no people, all elevators are empty and start at floor 1).
        """
        self.round_stat['min_time'] = num_rounds + 1
        for i in range(num_rounds):
            self.round_stat['num_iterations'] = i + 1

            self.visualizer.render_header(i)

            # Stage 1: generate new arrivals
            self._generate_arrivals(i)

            # Stage 2: leave elevators
            self._handle_leaving()

            # Stage 3: board elevators
            self._handle_boarding()

            # Stage 4: move the elevators using the moving algorithm
            self._move_elevators()

            # Pause for 1 second
            self.visualizer.wait(1)

            for index in range(len(self.waiting_people)):
                self.waiting_people[index].waited()

        self.round_stat['avg_time'] = self.average_time()

        return self._calculate_stats()

    def _generate_arrivals(self, round_num: int) -> None:
        """Generate and visualize new arrivals."""
        round_generate = self.arrival_generator.generate(round_num)
        for item in round_generate:
            if item in self.waiting:
                for person in round_generate[item]:
                    self.waiting[item].append(person)
                    self.round_stat['total_people'] += 1
                    self.waiting_people.append(person)
            else:
                self.waiting[item] = round_generate[item]
                for person in round_generate[item]:
                    self.round_stat['total_people'] += 1
                    self.waiting_people.append(person)
        self.visualizer.show_arrivals(self.waiting)

    def _handle_leaving(self) -> None:
        """Handle people leaving elevators."""
        index = -1
        for elevator in self.elevators:
            index += 1
            for person in elevator.passengers:
                if elevator.floor == person.target:
                    self.elevators[index].passengers.remove(person)
                    self.round_stat['people_completed'] += 1
                    self.max_min(person.wait_time)
                    self.people_time.append(person.wait_time)
                    self.waiting_people.remove(person)
                    self.visualizer.show_disembarking(person, elevator)

    def _handle_boarding(self) -> None:
        index = -1
        for elevator in self.elevators:
            index += 1
            if elevator.floor in self.waiting:
                for person in self.waiting[elevator.floor]:
                    if not elevator.is_full():
                        self.elevators[index].passengers.append(person)
                        self.waiting[elevator.floor].remove(person)
                        """Handle boarding of people and visualize."""
                        self.visualizer.show_boarding(person, elevator)

    def _move_elevators(self) -> None:
        """Move the elevators in this simulation.

        Use this simulation's moving algorithm to move the elevators.
        """
        movement = self.moving_algorithm.move_elevators(self.elevators,
                                                        self.waiting,
                                                        self.num_floors)
        index = 0
        while index < len(self.elevators):
            self.elevators[index].floor += return_direction(movement[index])
            index += 1
        self.visualizer.show_elevator_moves(self.elevators, movement)

    ############################################################################
    # Statistics calculations
    ############################################################################
    def max_min(self, person_time: int) -> None:
        """Comparing the max or min time"""
        if person_time > self.round_stat['max_time']:
            self.round_stat['max_time'] = person_time
        if person_time < self.round_stat['min_time']:
            self.round_stat['min_time'] = person_time

    def average_time(self) -> int:
        """Calculate the average time"""
        total = 0
        for item in self.people_time:
            total += item
        if len(self.people_time) == 0:
            return 0
        else:
            return total / len(self.people_time)

    def _calculate_stats(self) -> Dict[str, int]:
        """Report the statistics for the current run of this simulation.
        """
        return self.round_stat


def sample_run() -> Dict[str, int]:
    """Run a sample simulation, and return the simulation statistics."""
    config = {
        'num_floors': 6,
        'num_elevators': 6,
        'elevator_capacity': 3,
        'num_people_per_round': None,
        # Random arrival generator with 6 max floors and 2 arrivals per round.
        'arrival_generator': algorithms.RandomArrivals(6, None),
        'moving_algorithm': algorithms.RandomAlgorithm(),
        'visualize': True
    }

    sim = Simulation(config)
    stats = sim.run(15)
    return stats


if __name__ == '__main__':
    # Uncomment this line to run our sample simulation (and print the
    # statistics generated by the simulation).
    print(sample_run())

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['entities', 'visualizer', 'algorithms', 'time'],
        'max-nested-blocks': 4,
        'max-attributes': 12,
        'disable': ['R0201']
    })
