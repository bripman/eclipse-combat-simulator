#!/usr/bin/env python3
"""scoreboard.py -- Defines the Scoreboard class, which is used by the
Eclipse Combat Simulator. Has debugging functionality if called as
__main__.
"""

import sys
import os


if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])


class Scoreboard:
    """Stores the results of ECS combat simulations and has methods for
    updating and displaying those results.
    """

    def __init__(self, defender, attacker):
        """Initialize the scoreboard with an attacking player and a
        defending player.
        """
        self.defender = defender
        self.def_wins = 0
        self.def_ships_remaining = {}
        for a_ship in defender.fleet:
            if a_ship.hull.name not in self.def_ships_remaining.keys():
                self.def_ships_remaining[a_ship.hull.name] = []
        # Each key in def_ships_remaining is the name of a hull class
        # in the defender's fleet and indexes a list that stores the
        # number of ships of that class remaining for each of the
        # defender's victories.
        self.attacker = attacker
        self.atk_wins = 0
        self.atk_ships_remaining = {}
        for a_ship in attacker.fleet:
            if a_ship.hull.name not in self.atk_ships_remaining.keys():
                self.atk_ships_remaining[a_ship.hull.name] = []
        # See above comments on def_ships_remaining
        self.stalemates = 0

    def __str__(self):
        """Return the scoreboard as a string formatted for printing."""
        nsims_completed = self.def_wins + self.atk_wins + self.stalemates
        description = ""
        if nsims_completed == 0:
            description = "\nNo simulations have been run yet!"
        else:
            description += "\nHere are the simulation results:"
            description += ("\n\n%s won %i times (%.2f%% probability)"
                % (self.defender.name, self.def_wins,
                100. * self.def_wins / nsims_completed))
            if self.def_wins > 0:
                description += ("\n%s's average surviving victorious fleet:"
                    % (self.defender.name))
                for key in self.def_ships_remaining.keys():
                    description += ("\n-------- %.1f %ss"
                        % (sum(self.def_ships_remaining[key])
                        / len(self.def_ships_remaining[key]), key))
            description += ("\n\n%s won %i times (%.2f%% probability)"
                % (self.attacker.name, self.atk_wins,
                100. * self.atk_wins / nsims_completed))
            if self.atk_wins > 0:
                description += ("\n%s's average surviving victorious fleet:"
                    % (self.attacker.name))
                for key in self.atk_ships_remaining.keys():
                    description += ("\n-------- %.1f %ss"
                        % (sum(self.atk_ships_remaining[key])
                        / len(self.atk_ships_remaining[key]), key))
            if self.stalemates > 0:
                description += \
                    ("\nThere were %i stalemates (%.2f%% probability)"
                    % (self.stalemates,
                    100. * self.stalemates / nsims_completed))
        return description

    def record_victory(self, winner):
        """Record results of a combat sim where one player was
        victorious, e.g. destroyed all of the opponent's ships.
        """
        if winner.id == self.defender.id:
            self.def_wins += 1
            for key in self.def_ships_remaining.keys():
                self.def_ships_remaining[key].append(
                    sum(1 for a_ship in winner.fleet if
                        a_ship.hull.name == key))
        else:
            self.atk_wins += 1
            for key in self.atk_ships_remaining.keys():
                self.atk_ships_remaining[key].append(
                    sum(1 for a_ship in winner.fleet if
                        a_ship.hull.name == key))

    def record_stalemate(self):
        """Record results of a combat sim that ended in a stalemate."""
        self.stalemates += 1


def main():
    """Tests various functions defined in this module."""
    print("\nHello world from scoreboard.py!\n")


if __name__ == '__main__':
    main()