#!/usr/bin/env python3
"""db_parser.py -- Contains various functions used to query the ECS
database. Has debugging functionality if called as __main__.
"""

import sqlite3
import time


def query_db(table_name, query, db_name="game_data.sqlite3"):
    """Executes an SQLite database query. Currently insecure against
    injection attacks a la https://xkcd.com/327/ since the query
    parameter can't be properly sanitized.
    """
    table_name = clean_string(table_name)
    output = []
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('%s' % (query))
        output = c.fetchall()
    except:
        print("*** An exception occured in query_db! ***")
    finally:
        conn.close()
    return output


def clean_string(string):
    """Sanitizes a string, making it suitable for use as input for
    SQLite commands.
    """
    clean_string = ''
    try:
        string = str(string)
        clean_string = ''.join(char for char in string if char.isalnum())
    except:
        print("*** An exception occured in clean_string! ***")
    return clean_string


def get_table_attrs(table_name):
    """Returns a list of all attribute names for entities in a table in
    the ECS database.
    """
    query = 'PRAGMA table_info(%s)' % (table_name)
    pragma_output = query_db(table_name, query)
    attr_names = [pragma[1] for pragma in pragma_output]
    return attr_names


def get_table_contents(table_name):
    """Retrieves the contents of a table in the ECS database."""
    query = 'SELECT * FROM %s' % (table_name)
    table_contents = query_db(table_name, query)
    return table_contents


def get_table_as_dict(table_name):
    """Retrieves the contents of a table in the ECS database and
    returns it as a list of dictionaries. Each dictionary in this list
    represents a row of data and has the table's attribute names as
    keys indexing attribute values.
    """
    items = []
    keys = get_table_attrs(table_name)
    item_table = get_table_contents(table_name)
    for item in item_table:
        items.append(dict(zip(keys, item)))
    return items


def main():
    """Tests various functions defined in db_parser."""
    print("\nHello world from db_parser.py!\n")

    attribute_names = get_table_attrs('hull')
    for item in attribute_names:
        print(item)
        time.sleep(0.01)
    print("\n^ Here are all of the attributes in the hull table.")

    input("Press Enter to continue...\n")
    table_contents = get_table_contents('loadout')
    for item in table_contents:
        print(item)
        time.sleep(0.01)
    print("\n^ Here is the raw content of the loadout table.")

    input("Press Enter to continue...\n")
    hulls = get_table_as_dict('hull')
    for item in hulls:
        print(item)
        time.sleep(0.01)
    print("\n^ Here is the formatted content of the hull table.")


if __name__ == '__main__':
    main()