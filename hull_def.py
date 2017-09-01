#!/usr/bin/env python
"""hull_def.py -- Defines the Hull class, which is used by the Eclipse
Combat Simulator. Has debugging functionality if called as __main__."""

import db_parser
import part_def

class Hull:
    """The Hull class contains all the basic, immutable characteristics
    of a Ship type in Eclipse."""
    
    def __init__(self, name='Undefined Hull', nmax=0, nslots=0, bonus_power=0, 
                 bonus_initiative=0., needs_drive=1, is_mobile=1,
                 default_parts=[]):
        self.name = name # Name of this Hull type
        self.nmax = nmax # Max number that a player may build
        self.nslots = nslots # Number of module slots
        self.bonus_power = bonus_power # Bonus power supply
        self.bonus_initiative = bonus_initiative # Bonus initiative
        self.needs_drive = needs_drive # Is a drive Module required?
        self.is_mobile = is_mobile # Is it mobile?
        self.default_parts = default_parts # List of default Parts for this Hull

    def __str__(self):
        """Returns a verbose description of the Hull."""
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
    def GetHullsFromDB():
        """Returns a list of Hull objects representing the available Ship
        types in the board game Eclipse. Hull info is obtained from an
        SQLite database."""
        hulls = {}
        all_hulls = db_parser.GetHulls()
        all_parts = part_def.Part.GetPartsFromDB()
        for hull_name in all_hulls.keys():
            default_parts = []
            for part_name in all_hulls[hull_name]['loadout']:
                default_parts.append(all_parts[part_name])
            new_hull = Hull(hull_name,
                            all_hulls[hull_name]['nmax'],
                            all_hulls[hull_name]['nslots'],
                            all_hulls[hull_name]['bonus_power'],
                            all_hulls[hull_name]['bonus_initiative'],
                            all_hulls[hull_name]['needs_drive'],
                            all_hulls[hull_name]['is_mobile'],
                            default_parts)
            hulls[hull_name] = new_hull
        return hulls

def main():
    """Gives the GetHullsFromDB function a spin and shows the results."""
    print("\nHello world from hull_def.py\n")

    hulls = Hull.GetHullsFromDB()
    for name in hulls.keys():
        print(hulls[name], "\n")
    print("^ These are all the hulls I can make.")
    print("Total number of hulls = %i" % (len(hulls))) 
    
if __name__ == '__main__':
    main()