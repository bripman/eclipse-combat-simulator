#!/usr/bin/env python3
"""part.py -- Defines the Part class, which is used by the Eclipse
Combat Simulator. Has debugging functionality if called as _main__.
"""

import sys
import os
import time

import db_parser
import user_input

if __name__ != '__main__':
    sys.path.insert(0, os.path.split(__file__)[0])


class Part:
    """The Part class contains all of the attributes associated with a
    modular piece of equipment in the game Eclipse. These parts are
    placed in equipment slots on ships and modify their attributes.
    Note that there is potential for name confusion here since the
    in-game characteristic "hull" is referred to as "armor" in all ECS
    code.
    """
    
    def __init__(self, name='<Empty Slot>', damage=0, nshots=0, power=0,
                 armor=0, shield=0, hit_bonus=0, initiative=0, is_weapon=0,
                 is_missile=0, is_drive=0, is_ancient=0, is_available=1):
        self.name = name
        self.damage = damage # How much damage this does per shot
        self.nshots = nshots # Number of shots per round
        self.power = power # Power supplied (+) or consumed (-)
        self.armor = armor # Armor provided
        self.shield = shield # Shield provided
        self.hit_bonus = hit_bonus # Hit bonus provided
        self.initiative = initiative # Initiative bonus provided
        self.is_weapon = is_weapon
        self.is_missile = is_missile
        self.is_drive = is_drive
        self.is_ancient = is_ancient
        self.is_available = is_available
    
    def __str__(self):
        """Returns a verbose description of the part."""
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
    def get_parts():
        """Returns a dictionary whose keys are part names indexing all
        part objects available to the ECS.
        """
        parts = {}
        part_attributes = Part.get_part_attributes()
        for name in part_attributes.keys():
            new_part = Part(name,
                            part_attributes[name]['damage'],
                            part_attributes[name]['nshots'],
                            part_attributes[name]['power'],
                            part_attributes[name]['armor'],
                            part_attributes[name]['shield'],
                            part_attributes[name]['hit_bonus'],
                            part_attributes[name]['initiative'],
                            part_attributes[name]['is_weapon'],
                            part_attributes[name]['is_missile'],
                            part_attributes[name]['is_drive'],
                            part_attributes[name]['is_ancient'])
            parts[name] = new_part
        return parts

    @staticmethod
    def get_part_attributes():
        """Retrieves information about all available parts from the ECS
        SQLite database and returns it as a dictionary of dictionaries
        where the outer dict keys are part names and the inner dict
        keys are attribute names indexing each part's attribute values.
        """
        parts = {}
        part_table = db_parser.get_table_as_dict('part')
        for row in part_table:
            # Make a new nested dictionary indexed by this part's name
            part_name = row['part_name']
            parts[part_name] = {}
            for key in row.keys():
                if key == 'part_name':
                    pass
                else:
                    parts[part_name][key] = row[key]
        return parts


def select_part(parts, slot_num):
    """Displays a list of parts to the user so that they can select a
    part to equip to a ship. The parts argument must be in the same
    format as the output from the get_parts static method of the part
    class. Returns the name of the selected part as a string.
    """
    available_parts = \
        [key for key in sorted(parts.keys()) if parts[key].is_available]
    print("\nAvailable parts:")
    for i in range(len(available_parts)):
        print("%2i -" %(i + 1), parts[available_parts[i]].name)
        time.sleep(0.01)
    selected_part = user_input.get_int(
            "\nWhich part would you like to equip in slot %i? " % (slot_num),
            True, 1, len(available_parts))
    part_name = parts[available_parts[selected_part - 1]].name
    return part_name


def main():
    """Tests various functions defined in this module."""
    print("\nHello world from part.py!\n")

    all_parts = Part.get_parts()
    for key in all_parts.keys():
        print(all_parts[key].name)
        time.sleep(0.01)
    print("\n^ These are all the parts I can make.")
    print("Total number of parts = %i" % (len(all_parts)))

    print("\nNow let's try selecting a part to equip to a ship.")
    input("Press Enter to continue...")
    parts = Part.get_parts()
    part_name = select_part(parts, 1)
    print("You chose to equip the %s." % (part_name))


if __name__ == '__main__':
    main()