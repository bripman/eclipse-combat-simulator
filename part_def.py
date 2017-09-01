#!/usr/bin/env python
"""part_def.py -- Defines the Part class, which is used by the 
Eclipse Combat Simulator. Has debugging functionality if called as
_main__."""

import sys
import os
if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])
import db_parser
import user_input
import time

class Part:
    """The Part class contains all of the attributes associated with a
    modular piece of equipment in the game Eclipse. These Parts are placed
    in slots on Ships and modify their attributes. Note that there is potential
    for name confusion here since the in-game characteristic "hull" is referred
    to as "armor" in all ECS code."""
    
    def __init__(self, name='<Empty Slot>', damage=0, nshots=0, power=0,
                 armor=0, shield=0, hit_bonus=0, initiative=0, is_weapon=0,
                 is_missile=0, is_drive=0, is_ancient=0, is_available=1):
        self.name = name
        self.damage = damage # How much damage this does
        self.nshots = nshots # Number of shots per round
        self.power = power # How much power this supplies (+) or consumes (-)
        self.armor = armor # How much armor this provides
        self.shield = shield # Shield bonus provided
        self.hit_bonus = hit_bonus # Hit bonus provided
        self.initiative = initiative # Initiative bonus provided
        self.is_weapon = is_weapon # Is this a weapon?
        self.is_missile = is_missile # Is this a missile launcher?
        self.is_drive = is_drive # Is this a drive?
        self.is_ancient = is_ancient # Is this an ancient Part?
        self.is_available = is_available # Some Parts have a finite supply
    
    def __str__(self):
        """Returns a verbose description of the Part."""
        description = "-- %s --" % (self.name)
        description += "\ndamage = %i" % (self.damage)
        description += "\nnshots = %i" % (self.nshots)
        description += "\npower = %i" % (self.power)
        description += "\narmor = %i" % (self.armor)
        description += "\nshield = %i" % (self.shield)
        description += "\nhit_bonus = %i" % (self.hit_bonus)
        description += "\ninitiative = %i" % (self.initiative)
        description += "\nis_weapon = %i" % (self.is_weapon)
        description += "\nis_missile = %i" % (self.is_missile)
        description += "\nis_drive = %i" % (self.is_drive)
        description += "\nis_ancient = %i" % (self.is_ancient)
        description += "\nis_available = %i" % (self.is_available)
        return description

    @staticmethod
    def GetPartsFromDB():
        """Returns a dictionary whose keys are Part names indexing Part objects
        representing the available Ship parts in the board game Eclipse. Part
        info is obtained from an SQLite database."""
        parts = {}
        part_data = db_parser.GetParts()
        for name in part_data.keys():
            new_part = Part(name,
                            part_data[name]['damage'],
                            part_data[name]['nshots'],
                            part_data[name]['power'],
                            part_data[name]['armor'],
                            part_data[name]['shield'],
                            part_data[name]['hit_bonus'],
                            part_data[name]['initiative'],
                            part_data[name]['is_weapon'],
                            part_data[name]['is_missile'],
                            part_data[name]['is_drive'],
                            part_data[name]['is_ancient'])
            parts[name] = new_part
        return parts

def SelectPart(parts, slot_num):
    """Used to display a list of Parts to the user so that they can select
    a Part to equip to a Ship. The parts argument is in the same format as the
    output from the GetPartsFromDB static method of the Part class. Returns the
    name of the selected Part as a string."""
    available_parts = \
        [key for key in sorted(parts.keys()) if parts[key].is_available]
    print("\nAvailable parts:")
    for i in range(len(available_parts)):
        print("%2i -" %(i + 1), parts[available_parts[i]].name)
        time.sleep(0.01)
    selected_part = user_input.GetInput(
            "Which part would you like to equip in slot %i? " % (slot_num),
            int, True, 1, len(available_parts))
    part_name = parts[available_parts[selected_part - 1]].name
    return part_name

def main():
    """Gives the GetParts function a spin and shows the results."""
    print("\nHello world from part_def.py!\n")

    all_parts = Part.GetPartsFromDB()
    for key in all_parts.keys():
        print(all_parts[key], "\n")
    print("^ These are all the parts I can make.")
    print("Total number of parts = %i" % (len(all_parts)))

    input("\nPress Enter to continue...\n")

    print("Now let's try selecting a part to equip to a ship.")
    parts = Part.GetPartsFromDB()
    part_name = SelectPart(parts, 1)
    print("You chose to equip the %s." % (part_name))

if __name__ == '__main__':
    main()