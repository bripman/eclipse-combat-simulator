#!/usr/bin/env python
"""player_def.py -- Defines the Player class, which is used by the Eclipse
Combat Simulator. Has debugging functionality if called as
__main__."""

import sys
import os
if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])
import ship_def
import hull_def

class Player:
    """The Player class stores all relevant information about a participant
    in an Eclipse fleet battle and defines methods for managing a Player's
    fleet."""
    players = 0 # Used to tag each Player with a unique ID
    
    def __init__(self, name):
        self.id = Player.players
        Player.players += 1
        self.name = name
        self.fleet = []

    def __str__(self):
        """Returns a verbose description of the Player."""
        description = "-------- %s --------" % (self.name)
        description += "\n%s's id: %i" % (self.name, self.id)
        description += "\n%s's fleet contains:" % (self.name)
        ships = {}
        for ship in self.fleet:
            if ship.hull.name not in ships.keys():
                ships[ship.hull.name] = 1
            else:
                ships[ship.hull.name] += 1
        for key in ships.keys():
            description += "\n%i %ss" % (ships[key], key)
        description += "\n(%i ships total)" % (len(self.fleet))
        return description

    def SortFleet(self):
        """Sorts the ships in the Player's fleet by descending kill priority.
        The combat algorithm relies on fleets being sorted in this way."""
        self.fleet = sorted(self.fleet, key=lambda ship: -ship.kill_priority)
    
def main():
    """Tests various functions defined in player_def."""
    print("\nHello world from player_def.py!\n")
    
    print("Let's try making a player.")
    new_player = Player('Ben')
    print(new_player)
    
if __name__ == '__main__':
    main()