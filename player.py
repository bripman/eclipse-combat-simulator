#!/usr/bin/env python3
"""player.py -- Defines the Player class, which is used by the Eclipse
Combat Simulator. Has debugging functionality if called as __main__.
"""

import sys
import os

import ship
import hull
import user_input

if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])


class Player:
    """The Player class stores all relevant information about a player
    in an Eclipse fleet battle and defines methods for managing their
    fleet.
    """

    players = 0 # Used to tag each player with a unique ID

    def __init__(self):
        Player.players += 1
        self.id = Player.players
        self.name = user_input.get_str("Please enter player %i's name: "
                                       % (self.id))
        self.fleet = []
        self.is_defending = 0

    def __str__(self):
        """Returns a verbose description of the player."""
        description = "-------- %s --------" % (self.name)
        if self.is_defending:
            description = "\n-- (%s is defending) --" % (self.name)
        description += "\n%s's id: %i" % (self.name, self.id)
        description += "\n%s's fleet contains:" % (self.name)
        ships = {}
        for a_ship in self.fleet:
            if a_ship.hull.name not in ships.keys():
                ships[a_ship.hull.name] = 1
            else:
                ships[a_ship.hull.name] += 1
        for key in ships.keys():
            description += "\n%i %ss" % (ships[key], key)
        description += "\n(%i ships total)" % (len(self.fleet))
        return description

    def sort_fleet(self):
        """Sort the player's fleet by descending kill_priority. The
        combat algorithm currently relies on this, which is a bit
        kludgey.
        """
        self.fleet = \
            sorted(self.fleet, key=lambda a_ship: -a_ship.kill_priority)


def main():
    """Tests various functions defined in this module."""
    print("\nHello world from player.py!\n")
    
    print("Let's try making a player.")
    new_player = Player('Ben')
    print(new_player)


if __name__ == '__main__':
    main()