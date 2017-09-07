#!/usr/bin/env python3
"""user_input.py -- Contains the GetInput function. Has debugging
functionality if called as __main__."""


def GetInput(prompt, desired_type):
    """Uses the supplied prompt to pester the user until they give input of
    the desired type."""
    acceptable_input = False
    while not acceptable_input:
        response = input(prompt)
        if not response:
            print("You've gotta give me SOMETHING!")
            continue
        if desired_type == str:
            try:
                response = str(response)
            except ValueError:
                print("Please enter a string!")
                continue
            acceptable_input = True
        elif desired_type == int:
            try:
                response = int(response)
            except ValueError:
                print("Please enter an integer!")
                continue
            acceptable_input = True
        else:
            raise TypeError('Unsupported input type requested.')
    return response


def GetStr(prompt, constrained=False, acceptable_strings=[]):
    """Uses the supplied prompt to pester the user until they yield a string.
    If the constrained arg is True, only accepts input that is contained within
    the acceptable_strings list."""
    acceptable_input = False
    while not acceptable_input:
        response = GetInput(prompt, str)
        if constrained and response not in acceptable_strings:
            print("That is not an acceptable answer.")
        else:
            acceptable_input = True
    return response


def GetInt(prompt, constrained=False, low_lim=0, high_lim=1):
    """Uses the supplied prompt to pester the user until they yield an integer.
    If the constrained arg is True, only accepts input that is >= low_lim and
    <= high_lim."""
    acceptable_input = False
    while not acceptable_input:
        response = GetInput(prompt, int)
        if constrained and (response < low_lim or response > high_lim):
            print("That is not an acceptable answer.")
        else:
            acceptable_input = True
    return response


def main():
    """Tests various functions defined in user_input."""
    print("\nHello world from user_input.py!\n")

    print("Let's try asking the user for some input.")
    str_input1 = GetStr('Give me any string: ')
    str_input2 = GetStr('Give me a decision (y or n): ', True, ['y', 'n'])
    int_input1 = GetInt('Give me any integer: ')
    int_input2 = GetInt('Give me a number between 1 and 10: ',
                             True, 1, 10)


if __name__ == '__main__':
    main()