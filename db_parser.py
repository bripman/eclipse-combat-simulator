#!/usr/bin/env python3
"""db_parser.py -- Contains various functions used to query the ECS database.
Has debugging functionality if called as __main__."""

import sqlite3
import time

def QueryDB(table_name, db_name, query):
    """Executes an SQLite database query. Currently insecure against injection
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
    """Sanitizes a string, making it suitable for use as input for SQLite
    commands."""
    clean_string = ''
    try:
        string = str(string)
        clean_string = ''.join(char for char in string if char.isalnum())
    except:
        print("*** An exception occured in CleanString! ***")
    return clean_string

def GetTableAttrs(table_name, db_name='ecs.sqlite3'):
    """Returns a list of all attribute names for entities in a table in the ECS
    database."""
    query = 'PRAGMA table_info(%s)' % (table_name)
    pragma_output = QueryDB(table_name, db_name, query)
    attr_names = [pragma[1] for pragma in pragma_output]
    return attr_names

def GetTableContents(table_name, db_name='ecs.sqlite3'):
    """Retrieves the contents of a table in the ECS database."""
    query = 'SELECT * FROM %s' % (table_name)
    table_contents = QueryDB(table_name, db_name, query)
    return table_contents

def GetTableAsDict(table_name):
    """Retrieves the contents of a table in the ECS database and returns it as a
    list of dictionaries. Each dictionary in this list represents a row of data
    and has the table's attribute names as keys indexing attribute values."""
    items = []
    keys = GetTableAttrs(table_name)
    item_table = GetTableContents(table_name)
    for item in item_table:
        items.append(dict(zip(keys, item)))
    return items

def GetHullLoadouts():
    """Retrieves the default loadouts for each Hull in the ECS database and
    returns them as a dictionary where each key is a Hull name and indexes a
    list of Part names."""
    loadouts = {}
    loadout_table = GetTableAsDict('loadout')
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
    hull_table = GetTableAsDict('hull')
    loadouts = GetHullLoadouts()
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

def main():
    """Tests various functions defined in db_parser."""
    print("\nHello world from db_parser.py!\n")

    attribute_names = GetTableAttrs('hull')
    for item in attribute_names:
        print(item)
        time.sleep(0.01)
    print("\n^ Here are all of the attributes in the hull table.")

    input("Press Enter to continue...\n")
    table_contents = GetTableContents('loadout')
    for item in table_contents:
        print(item)
        time.sleep(0.01)
    print("\n^ Here is the raw content of the loadout table.")

    input("Press Enter to continue...\n")
    hulls = GetTableAsDict('hull')
    for item in hulls:
        print(item)
        time.sleep(0.01)
    print("\n^ Here is the formatted content of the hull table.")

if __name__ == '__main__':
    main()