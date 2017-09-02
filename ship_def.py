#!/usr/bin/env python
"""ship_def.py -- Defines the Ship class, which is used by the Eclipse Combat
Simulator. Has debugging functionality if called as __main__."""

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
    
    def __init__(self, hull, parts, player):
        self.id = Ship.ships
        Ship.ships += 1
        self.hull = hull
        self.owner = player
        self.parts = [] # List of all equipped Parts
        self.Build(parts)

    def Build(self, parts):
        """Begins the process of building a Ship. Determines whether or not the
        user wants to construct a custom Ship and then calls the appropriate
        function."""
        default = user_input.GetStrInput(
            "Should we use the default %s parts (y/n)? "
            % (self.hull.name), True, ['y', 'Y', 'n', 'N'])
        if default in ['y', 'Y']:
            # No need to pass parts; hull already contains the default loadout.
            self.BuildDefault()
        else:
            self.BuildCustom(parts)

    def BuildDefault(self):
        """Builds a Ship using the default Parts for that Ship's Hull."""
        self.parts = self.hull.default_parts # No need to make a deep copy here
        self.Integrate()
        verified = self.Verify()
        if not verified:
            # This is really surprising - all default loadouts should be legal.
            # Just crash right out of the program.
            raise RuntimeError('Illegal default ship loadout! ' +
                               'ECS database is configured improperly.')

    def BuildCustom(self, parts):
        """Builds a Ship using a customized set of Parts."""
        while True:
            print("\n%ss have %i slots. Let's equip parts one by one."
                  % (self.hull.name, self.hull.nslots))
            for i in range(self.hull.nslots):
                selected_part = part_def.SelectPart(parts, i + 1)
                self.parts.append(parts[selected_part])
                if parts[selected_part].is_ancient:
                    # We equipped an ancient Part. Since there is only one copy
                    # of each ancient Part, it's no longer available.
                    parts[selected_part].is_available = 0
            print()
            self.Integrate()
            verified = self.Verify()
            if not verified:
                print("Let's try again.")
                input("Press Enter to continue...")
                # Ship was constructed improperly - reset availability of all
                # equipped Parts, reset the list of equipped Parts, and try
                # again.
                for part in self.parts:
                    part.is_available = 1
                self.parts = []
                continue
            else:
                # Ship was constucted properly!
                break

    def Integrate(self):
        """Initializes this Ship's attributes and then integrates the stats from
        all equipped Parts."""
        self.net_damage = 0
        # Total damage this Ship can do per round
        self.net_power = self.hull.bonus_power
        # Power supplied - power consumed
        self.armor = 1
        # All Ships have at least 1 armor 
        self.shield = 0
        # Higher number makes it harder for enemies to hit
        self.hit_bonus = 0
        # Higher number makes it easier to hit enemies
        self.initiative = self.hull.bonus_initiative
        # Initiative determines the order in which Ships attack in combat
        self.has_drive = 0
        # Does the Ship have a drive Part equipped?
        self.has_weapon = 0
        # Does the Ship have a weapon Part equipped?
        self.kill_priority = 0
        # How tempting a target is this Ship in combat?
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

    def Verify(self):
        """Verify that this Ship is shipshape, as it were."""
        # Check that the Ship is legal
        legal = self.VerifyLegality()
        if not legal:
            return False
        # Check that all unusual design decisons were intentional
        weirdness_intentional = self.VerifyDesignDecisions()
        if not weirdness_intentional:
            return False
        # No dealbreakers found!
        return True

    def VerifyLegality(self):
        """Returns True if this Ship is legal within Eclipse's rules.
        Returns False otherwise."""
        legal = True
        # Confirm that power consumed <= power supplied
        if self.net_power < 0:    
            print("***--> Design flaw: power supplied < power consumed.")
            legal = False
        # If the Ship needs a drive, confirm that it has one
        if self.hull.needs_drive and not self.has_drive:
            print("***--> Design flaw: no drive equipped.")
            legal = False
        # Confirm that the Ship doesn't have more empty slots than are in
        # the default loadout. (You can't actually add empty slots to a Ship.)
        empty_slots = sum(part.name == '<Empty Slot>' for part in self.parts)
        empty_slots_allowed = sum(part.name == '<Empty Slot>' \
                                  for part in self.hull.default_parts)
        if empty_slots > empty_slots_allowed:
            print("***--> Design flaw: too many empty slots.")
            legal = False
        return legal

    def VerifyDesignDecisions(self):
        """Returns True if all of this Ship's unsual design decisions were
        intentional. Returns False otherwise."""
        weirdness_intentional = True
        # If the Ship has no weapons, confirm that this was intentional.
        weapon_equipped = False
        for part in self.parts:
            if part.is_weapon:
                weapon_equipped = True
        if not weapon_equipped:
            response = user_input.GetStrInput(
                "This %s design has no weapons. " % (self.hull.name) +
                "Is this intentional? (y/n)? ",
                True, ['y', 'Y', 'n', 'N'])
            if response in ['y', 'Y']:
                pass
            else:
                weirdness_intentional = False
        return weirdness_intentional

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

def main():
    """Tests various functions defined in ship_def."""
    print("\nHello world from ship_def.py!\n")

    print("Let's try making a ship.")
    hulls = hull_def.Hull.GetHulls()
    parts = part_def.Part.GetParts()
    player = player_def.Player('Ben')
    new_ship = Ship(hulls['Interceptor'], parts, player)
    print()
    print(new_ship)
    
if __name__ == '__main__':
    main()