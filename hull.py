#!/usr/bin/env python3
"""hull.py -- Defines the Hull class, which is used by the Eclipse
Combat Simulator. Has debugging functionality if called as __main__.
"""

import time

import db_parser
import part


class Hull:
    """The Hull class contains all the basic, immutable characteristics
    of a ship chassis in Eclipse.
    """
    
    def __init__(self, name='Undefined Hull', nmax=0, nslots=0, bonus_power=0, 
                 bonus_initiative=0., needs_drive=1, is_mobile=1,
                 default_parts=[]):
        self.name = name
        self.nmax = nmax # Max number that a player may build
        self.nslots = nslots # Number of slots for equipping parts
        self.bonus_power = bonus_power
        self.bonus_initiative = bonus_initiative
        self.needs_drive = needs_drive
        self.is_mobile = is_mobile
        self.default_parts = default_parts # Default part loadout

    def __str__(self):
        """Returns a verbose description of the hull."""
        description = "-------- %s --------" % (self.name)
        description += "\nnmax = %i" % (self.nmax)
        description += "\nnslots = %i" % (self.nslots)
        description += "\nbonus_power = %i" % (self.bonus_power)
        description += "\nbonus_initiative = %.1f" % (self.bonus_initiative)
        description += "\nneeds_drive = %i" % (self.needs_drive)
        description += "\nis_mobile = %i" % (self.is_mobile)
        description += "\n----- Default Parts -----"
        for i in range(len(self.default_parts)):
            description += "\n%i) %s" % (i + 1, self.default_parts[i].name)
        return description

    @staticmethod
    def get_hulls():
        """Returns a dictionary whose keys are hull names indexing all
        hull objects available to the ECS.
        """
        hulls = {}
        hull_attributes = Hull.get_hull_attributes()
        all_parts = part.Part.get_parts()
        for hull_name in hull_attributes.keys():
            default_parts = []
            for part_name in hull_attributes[hull_name]['loadout']:
                default_parts.append(all_parts[part_name])
            new_hull = Hull(hull_name,
                            hull_attributes[hull_name]['nmax'],
                            hull_attributes[hull_name]['nslots'],
                            hull_attributes[hull_name]['bonus_power'],
                            hull_attributes[hull_name]['bonus_initiative'],
                            hull_attributes[hull_name]['needs_drive'],
                            hull_attributes[hull_name]['is_mobile'],
                            default_parts)
            hulls[hull_name] = new_hull
        return hulls

    @staticmethod
    def get_hull_attributes():
        """Retrieves information about all available hulls from the ECS
        SQLite database and returns it as a dictionary of dictionaries
        where the outer dict keys are hull names and the inner dict
        keys are attribute names indexing each hull's attribute
        values.
        """
        hulls = {}
        hull_table = db_parser.get_table_as_dict('hull')
        hull_loadouts = Hull.get_hull_loadouts()
        for row in hull_table:
            # Make a new nested dictionary indexed by this hull's name
            hull_name = row['hull_name']
            hulls[hull_name] = {}
            for key in row.keys():
                if key == 'hull_name':
                    pass
                else:
                    hulls[hull_name][key] = row[key]
            # Now add this hull's loadout to its dictionary
            hulls[hull_name]['loadout'] = hull_loadouts[hull_name]
        return hulls

    @staticmethod
    def get_hull_loadouts():
        """Retrieves the default loadouts for each hull from the ECS
        SQLite database and returns them as a dictionary where each key
        is a hull name indexing a list of part names.
        """
        loadouts = {}
        loadout_table = db_parser.get_table_as_dict('loadout')
        for row in loadout_table:
            if row['hull_name'] not in loadouts.keys():
                loadouts[row['hull_name']] = []
            loadouts[row['hull_name']].append(row['part_name'])
        return loadouts


def main():
    """Tests various functions defined in this module."""
    print("\nHello world from hull.py\n")

    all_hulls = Hull.get_hulls()
    for key in all_hulls.keys():
        print(all_hulls[key], "\n")
        time.sleep(0.01)
    print("\n^ These are all the hulls I can make.")
    print("Total number of hulls = %i" % (len(all_hulls))) 


if __name__ == '__main__':
    main()