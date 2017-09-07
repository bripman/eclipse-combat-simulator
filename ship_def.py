#!/usr/bin/env python3
"""ship_def.py -- Defines the Ship class, which is used by the Eclipse Combat
Simulator. Has debugging functionality if called as __main__."""

import sys
import os
import random

import part_def
import hull_def
import user_input
import player_def

if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])


class Ship:
    """The Ship class represents a ship in Eclipse. Note that there is
    potential for name confusion here since the in-game characteristic "hull"
    is referred to as "armor" in all ECS code."""
    ships = 0 # Used to tag each ship with a unique ID
    
    def __init__(self, hull, parts, player, dupe=False, dupe_parts=[]):
        self.id = Ship.ships
        Ship.ships += 1
        self.hull = hull
        self.owner = player
        self.parts = []
        self.missiles_fired = 0 # Has the ship fired its missiles already?
        if not dupe:
            # We are constructing the prototype all ships of this hull
            # type for this player
            self.Build(parts)
        else:
            # We are duplicating a prototype to fill out this player's
            # fleet.
            self.BuildDupe(dupe_parts)

    def Build(self, parts):
        """Begins the process of building a ship. Determines whether or not the
        user wants to construct a custom ship and then calls the appropriate
        function."""
        default = user_input.GetStr(
            "Should we use the default %s parts (y/n)? "
            % (self.hull.name), True, ['y', 'Y', 'n', 'N'])
        if default in ['y', 'Y']:
            # No need to pass parts; hull already contains the default loadout.
            self.BuildDefault()
        else:
            self.BuildCustom(parts)

    def BuildDefault(self):
        """Builds a ship using the default parts for that ship's hull."""
        self.parts = self.hull.default_parts
        self.Integrate()
        verified = self.Verify()
        if not verified:
            # This is really surprising - all default loadouts should be legal.
            # Just crash right out of the program.
            raise RuntimeError("Illegal default ship loadout! " +
                               "ECS database is configured improperly.")

    def BuildCustom(self, parts):
        """Builds a ship using a customized set of parts."""
        while True:
            print("\n%ss have %i slots. Let's equip parts one by one."
                  % (self.hull.name, self.hull.nslots))
            for i in range(self.hull.nslots):
                selected_part = part_def.SelectPart(parts, i + 1)
                self.parts.append(parts[selected_part])
                if parts[selected_part].is_ancient:
                    # We equipped an ancient part. Since there is only one copy
                    # of each ancient part, it's no longer available.
                    parts[selected_part].is_available = 0
            print()
            self.Integrate()
            verified = self.Verify()
            if not verified:
                print("Let's try again.")
                input("Press Enter to continue...")
                # Ship was constructed improperly - reset availability of all
                # equipped parts, reset the list of equipped parts, and try
                # again.
                for part in self.parts:
                    part.is_available = 1
                self.parts = []
                continue
            else:
                # Ship was constucted properly!
                break

    def BuildDupe(self, dupe_parts):
        """Builds a duplicate ship with a predefined parts list."""
        self.parts = dupe_parts
        # We will assume that this design verifies
        self.Integrate()

    def Integrate(self):
        """Initializes most of this ship's stats and then integrates the
        stats from all equipped parts."""
        # Initialize
        self.net_damage = 0
        self.net_power = self.hull.bonus_power
        self.armor = 1
        self.shield = 0
        self.hit_bonus = 0
        self.initiative = self.hull.bonus_initiative
        if self.owner.is_defending:
            # The defending player goes first when initiative is tied. Simplest
            # way to implement that is with a fractional bump.
            self.initiative += 0.5
        self.has_drive = 0
        self.has_weapon = 0
        # Integrate
        for part in self.parts:
            self.net_power += part.power
            self.armor += part.armor
            self.shield += part.shield
            self.hit_bonus += part.hit_bonus
            self.initiative += part.initiative
            if part.is_drive:
                self.has_drive = 1
            if part.is_weapon:
                if not part.is_missile:
                    self.has_weapon = 1
                    self.net_damage += part.damage * part.nshots
                else:
                    if self.missiles_fired:
                        pass
                    else:
                        self.has_weapon = 1
                        self.net_damage += part.damage * part.nshots

        self.CalcKillPriority()

    def CalcKillPriority(self):
        """Sets this ship's kill_priority stat, which measures how tempting
        a target it is in combat."""
        # Set kill_priority to the ship's expected damage output per round
        self.kill_priority = self.net_damage * (1 + self.hit_bonus) / 6.0
        # Then reduce it by a factor proportional to the ship's toughness
        self.kill_priority /= self.armor

    def Verify(self):
        """Verify that this ship is shipshape, as it were."""
        # Check that the ship is legal
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
        """Returns True if this ship is legal within Eclipse's rules.
        Returns False otherwise."""
        legal = True
        # Confirm that power consumed <= power supplied
        if self.net_power < 0:    
            print("***--> Design flaw: power supplied < power consumed.")
            legal = False
        # If the ship needs a drive, confirm that it has one
        if self.hull.needs_drive and not self.has_drive:
            print("***--> Design flaw: no drive equipped.")
            legal = False
        # Confirm that the ship doesn't have more empty slots than are in
        # the default loadout. (You can't actually add empty slots to a ship.)
        empty_slots = sum(part.name == '<Empty Slot>' for part in self.parts)
        empty_slots_allowed = sum(part.name == '<Empty Slot>'
                                  for part in self.hull.default_parts)
        if empty_slots > empty_slots_allowed:
            print("***--> Design flaw: too many empty slots.")
            legal = False
        return legal

    def VerifyDesignDecisions(self):
        """Returns True if all of this ship's unsual design decisions were
        intentional. Returns False otherwise."""
        weirdness_intentional = True
        # If the ship has no weapons, confirm that this was intentional.
        weapon_equipped = False
        for part in self.parts:
            if part.is_weapon:
                weapon_equipped = True
        if not weapon_equipped:
            response = user_input.GetStr(
                "This %s design has no weapons. " % (self.hull.name) +
                "Is this intentional? (y/n)? ",
                True, ['y', 'Y', 'n', 'N'])
            if response in ['y', 'Y']:
                weirdness_intentional = True
            else:
                weirdness_intentional = False
        return weirdness_intentional

    def __str__(self):
        """Returns a verbose description of the ship."""
        description = ("---- %s ----\n(owned by %s)"
                       % (self.hull.name, self.owner.name))
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

    def RollMissileAttacks(self):
        """Rolls this ship's missile attacks and rechecks its has_weapon status
        Returns a list of tuples where each tuple represents one of the ship's
        attacks. The structure of each tuple is: (to-hit roll (1d6), to-hit
        bonus, damage)."""
        if not self.has_weapon:
            return None
        attacks = []
        for part in self.parts:
            if part.is_weapon and part.is_missile:
                for i in range(part.nshots):
                    attacks.append(
                        (random.randint(1, 6), self.hit_bonus, part.damage))
        # Once missiles have fired, they are exhausted. Set this ship's
        # missiles_fired attribute and reintegrate it.
        self.missiles_fired = 1
        self.Integrate()
        return attacks

    def RollConventionalAttacks(self):
        """Rolls this ship's conventional (i.e. non-missile) attacks. Returns a
        list of tuples where each tuple represents one of the ship's attacks.
        The structure of each tuple is: (to-hit roll (1d6), to-hit bonus,
        damage)."""
        if not self.has_weapon:
            return None
        attacks = []
        for part in self.parts:
            if part.is_weapon and not part.is_missile:
                for i in range(part.nshots):
                    attacks.append(
                        (random.randint(1, 6), self.hit_bonus, part.damage))
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

    input("\nPress Enter to continue...\n")

    print("Let's try rolling some attacks for that ship!")
    attacks = new_ship.RollMissileAttacks()
    print("Missile attacks: ", attacks)
    attacks = new_ship.RollConventionalAttacks()
    print("Conventional attacks: ", attacks)


if __name__ == '__main__':
    main()