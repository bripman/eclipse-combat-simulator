#!/usr/bin/env python
"""db_parser.py -- Contains various functions used to query the ECS database.
Has debugging functionality if called as __main__."""

import sqlite3

def QueryDB(table_name, db_name, query):
    """Executes an SQLITE database query. Currently insecure against injection
    attacks a la https://xkcd.com/327/ since the query parameter can't be
    properly sanitized."""
    table_name = CleanString(table_name)
    output = []
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('%s' % (query))
        output = c.fetchall()
    except:
        print("*** An exception occured in QueryDB! ***")
    finally:
        conn.close()
    return output

def CleanString(string):
    """Sanitizes a string, making it suitable for use as input for sqlite3
    commands."""
    clean_string = ''
    try:
        string = str(string)
        clean_string = ''.join(char for char in string if char.isalnum())
    except:
        print("*** An exception occured in CleanString! ***")
    return clean_string

def GetTableAttrs(table_name, db_name='ecs.sqlite3'):
    """Returns a list of all attribute names for entities in a user-specified
    table in the ECS database."""
    query = 'PRAGMA table_info(%s)' % (table_name)
    pragma_output = QueryDB(table_name, db_name, query)
    attr_names = [pragma[1] for pragma in pragma_output]
    return attr_names

def GetTableContents(table_name, db_name='ecs.sqlite3'):
    """Retrieves all attributes for all entities in a user-specified table in
    the ECS database."""
    query = 'SELECT * FROM %s' % (table_name)
    table_contents = QueryDB(table_name, db_name, query)
    return table_contents

def GetFormattedTable(table_name):
    """Retrieves a table of data from the ECS database and returns it as list of
    dictionaries. Each dictionary has the table's attribute names as keys
    indexing attribute values."""
    items = []
    keys = GetTableAttrs(table_name)
    item_table = GetTableContents(table_name)
    for item in item_table:
        items.append(dict(zip(keys, item)))
    return items

def GetLoadouts():
    """Retrieves the default loadouts for each Hull in the ECS database and
    returns them as a dictionary where each key is a Hull name and indexes a
    list of Part names."""
    loadouts = {}
    loadout_table = GetFormattedTable('loadout')
    for item in loadout_table:
        if item['hull_name'] not in loadouts.keys():
            loadouts[item['hull_name']] = []
        loadouts[item['hull_name']].append(item['part_name'])
    return loadouts

def GetHulls():
    """Retrieves information about all Hulls in the ECS database and returns it
    as a dictionary of dictionaries where the outer dict keys index different
    Hulls and the inner dict keys index each Hull's characteristics."""
    hulls = {}
    hull_table = GetFormattedTable('hull')
    loadouts = GetLoadouts()
    for hull in hull_table:
        # Make a new nested dictionary indexed by this hull's name
        name = hull['hull_name']
        hulls[name] = {}
        for key in hull.keys():
            if key == 'hull_name':
                pass
            else:
                hulls[name][key] = hull[key]
        # Now add this hull's loadout to its dictionary
        hulls[name]['loadout'] = loadouts[name]
    return hulls

def GetParts():
    """Retrieves information about all Parts in the ECS database and returns it
    as a dictionary of dictionaries where the outer dict keys index different
    Parts and the inner dict keys index each Part's characteristics."""
    parts = {}
    part_table = GetFormattedTable('part')
    for part in part_table:
        # Make a new nested dictionary indexed by this part's name
        name = part['part_name']
        parts[name] = {}
        for key in part.keys():
            if key == 'part_name':
                pass
            else:
                parts[name][key] = part[key]
    return parts

def main():
    """Tests all of the functions defined in db_parser.py."""
    print("\nHello world from db_parser.py!\n")

    print("Here are all of the attributes in the hull table:")
    attribute_names = GetTableAttrs('hull')
    for item in attribute_names:
        print(item)

    input("\nPress Enter to continue...\n")

    print("Here is the raw content of the loadout table:")
    table_contents = GetTableContents('loadout')
    for item in table_contents:
        print(item)

    input("\nPress Enter to continue...\n")

    print("Here is the formatted content of the hull table:")
    hulls = GetFormattedTable('hull')
    for item in hulls:
        print(item)

    input("\nPress Enter to continue...\n")

    print("Here are the Hull loadouts:")
    loadouts = GetLoadouts()
    for key in loadouts.keys():
        print('%s: ' % (key), loadouts[key])

    input("\nPress Enter to continue...\n")

    print("Results of the GetHulls function:")
    hulls = GetHulls()
    for key in hulls.keys():
        print("%s: " % (key), hulls[key])

    input("\nPress Enter to continue...\n")

    print("Results of the GetParts function:")
    parts = GetParts()
    for key in parts.keys():
        print("%s: " % (key), parts[key])

    print()

if __name__ == '__main__':
    main()