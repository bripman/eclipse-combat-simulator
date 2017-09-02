#!/usr/bin/env python
"""ship_def.py -- Defines the Ship class, which is used by the Eclipse Combat
Simulator. Also contains the BuildShip and BuildDefaultShip functions and has
debugging functionality if called as __main__."""

import sys
import os
import random
if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])
import part_def
import hull_def
import user_input
import player_def

class Ship:
    """The Ship class represents the common blueprint for all Ships of a given
    Hull type in a player's fleet. The class defines methods for integrating the
    stats on all equipped Parts, verifying a Ship's legality within the game's
    rules, and rolling attacks with the ship's weapons. Note that there is
    potential for name confusion here since the in-game characteristic "hull"
    is referred to as "armor" in all ECS code."""
    ships = 0 # Used to tag each Ship with a unique ID
    
    def __init__(self, hull, player):
        self.id = Ship.ships
        Ship.ships += 1
        self.hull = hull
        self.owner = player
        self.parts = [] # List of all equipped Parts
        self.net_damage = 0 # Total damage this Ship can do per round
        self.net_power = hull.bonus_power # Power supplied minus power consumed
        self.armor = 1 # All Ships have at least 1 armor 
        self.shield = 0 # Higher number makes it harder for enemies to hit
        self.hit_bonus = 0 # Higher number makes it easier to hit enemies
        self.initiative = hull.bonus_initiative
        # Initiative determines order in which Ships attack in combat
        self.has_drive = 0 # Does the Ship have a drive Part equipped?
        self.has_weapon = 0 # Does the Ship have a weapon Part equipped?
        self.kill_priority = 0 # How tempting a target is it for enemy Ships?

    def __str__(self):
        """Returns a verbose description of the Ship."""
        description = "---- %s ----\n(owned by %s)" \
            % (self.hull.name, self.owner.name)
        description += "\n----------------------"
        description += "\nEquipped parts:"
        for part in self.parts:
            description += '\n' + part.name
        description += "\n----------------------"
        description += "\nnet_damage = %i" % (self.net_damage)
        description += "\nnet_power = %i" % (self.net_power)
        description += "\narmor = %i" % (self.armor)
        description += "\nshield = %i" % (self.shield)
        description += "\nhit_bonus = %i" % (self.hit_bonus)
        description += "\ninitiative = %.1f" % (self.initiative)
        description += "\nkill_priority = %.3f" % (self.kill_priority)
        description += "\nid = %i" % (self.id)
        return description

    def IntegrateShip(self):
        """Integrates the stats from all equipped Parts and initializes
        some of the Ship's attributes."""
        for part in self.parts:
            self.net_damage += part.damage * part.nshots
            self.net_power += part.power
            self.armor += part.armor
            self.shield += part.shield
            self.hit_bonus += part.hit_bonus
            self.initiative += part.initiative
            if part.is_drive:
                self.has_drive = 1
            if part.is_weapon:
                self.has_weapon = 1
        # Set kill_priority to the Ship's expected damage output per round
        self.kill_priority = self.net_damage * (1 + self.hit_bonus) / 6.0
        # Then reduce it by a factor proportional to the Ship's toughness
        self.kill_priority /= self.armor * (4 + self.shield) / 6.0

    def VerifyLegality(self):
        """Checks the legality of an assembled Ship. Ships need to have
        total power >= 0 (i.e. at least as much power supply as consumption)
        and most Ships require a drive. Ships also cannot have more empty slots
        than the default loadout for their Hull."""
        legal_ship = True
        if self.net_power < 0:
            # Power consumed by Parts > power supplied by Parts
            print("Design flaw: power supplied < power consumed.")
            legal_ship = False
        if self.hull.needs_drive and not self.has_drive:
            # The Ship's Hull requires a drive Part but it doesn't have one
            print("Design flaw: no drive equipped.")
            legal_ship = False
        # Now we must confirm that the ship doesn't have more empty slots than
        # are in the default loadout.
        empty_slots = sum(part.name == '<Empty_Slot>' for part in self.parts)
        empty_slots_allowed = sum(part.name == '<Empty_Slot>' \
                                  for part in self.hull.default_parts)
        if empty_slots > empty_slots_allowed:
            print("Design flaw: too many empty slots.")
            legal_ship = False
        return legal_ship

    def RollAttacks(self):
        """Returns a list of tuples where each tuple represents one of the
        Ship's attacks. The structure of each tuple is: (to-hit roll (1d6), 
        to-hit bonus, damage). The to-hit roll and to-hit bonus must be reported
        separately because a roll of 1 always misses and a 6 always hits."""
        attacks = []
        for part in self.parts:
            if part.is_weapon:
                for i in range(part.nshots):
                    attacks += \
                        (random.randint(1, 6), self.hit_bonus, part.damage)
        if attacks == []:
            # To avoid certain potential pitfalls, if we're about to return an
            # empty attacks list, just return a missed shot instead.
            attacks += (1, 0, 0)
        return attacks
    
    @staticmethod
    def BuildShip(hull, parts, player):
        """Accepts a Hull and a Player as input and walks the user through the
        process of building a Ship for that Player with the specified Hull.
        Returns the completed Ship."""
        while True:
            default = user_input.GetInput(
                "Should we use the default %s parts (y/n)? " % (hull.name), str)
            if default not in ['y', 'n']:
                continue
            else:
                break
        if default == 'y':
            new_ship = Ship.BuildDefaultShip(hull, player)
        else:
            new_ship = Ship.BuildCustomShip(hull, parts, player)
        return new_ship

    @staticmethod
    def BuildDefaultShip(hull, player):
        """Accepts a Hull and a Player owner as input and builds a Ship using
        the default Parts for that Hull. Returns the completed Ship."""
        new_ship = Ship(hull, player)
        new_ship.parts = hull.default_parts # No need to make a deep copy here
        new_ship.IntegrateShip()
        legal_ship = new_ship.VerifyLegality()
        if not legal_ship:
            # This is surprising - all default loadouts should be legal
            raise RuntimeError('Illegal default ship loadout! '
                               'ECS database is configured improperly.')
        return new_ship

    @staticmethod
    def BuildCustomShip(hull, parts, player):
        """Accepts a Hull, a dictionary of Part names and Parts, and a Player
        as input and builds a custom Ship with a user-defined Part loadout for
        the specified Player. Returns the completed Ship."""
        while True:
            print("\n%ss have %i slots. Let's equip parts one by one."
                  % (hull.name, hull.nslots))
            new_ship = Ship(hull, player)
            for i in range(hull.nslots):
                selected_part = part_def.SelectPart(parts, i + 1)
                new_ship.parts.append(parts[selected_part])
                if parts[selected_part].is_ancient:
                    parts[selected_part].is_available = 0
            print()
            new_ship.IntegrateShip()
            legal_ship = new_ship.VerifyLegality()
            if not legal_ship:
                print("Let's try again.\n")
                # Ship was constructed improperly - reset availability of all
                # equipped parts and try again
                for part in new_ship.parts:
                    part.is_available = 1
                continue
            else:
                # Ship was constucted properly!
                break
        return new_ship

def main():
    """Tests various functions defined in ship_def."""
    print("\nHello world from ship_def.py!\n")

    print("Let's try making a ship.")
    hulls = hull_def.Hull.GetHulls()
    parts = part_def.Part.GetParts()
    player = player_def.Player('Ben')
    new_ship = Ship.BuildShip(hulls['Interceptor'], parts, player)
    print(new_ship)
    
if __name__ == '__main__':
    main()