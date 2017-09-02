#!/usr/bin/env python
"""user_input.py -- Contains the GetInput function. Has debugging
functionality if called as __main__."""

def GetInput(prompt, desired_type, bounded=False, low_lim=0, high_lim=1):
    """Receives various criteria and uses them to pester the user for input
    until they give an answer with the desired type and within the specified
    numerical limits (if bounded == True). Supported types are str and int."""
    acceptable_input = False
    while not acceptable_input:
        response = input(prompt)
        if not response:
            print("You've gotta give me SOMETHING!")
            continue
        if desired_type == str:
            try:
                result = str(response)
            except ValueError:
                print("Please enter a string!")
                continue
            acceptable_input = True
        elif desired_type == int:
            try:
                result = int(response)
            except ValueError:
                print("Please enter an integer!")
                continue
            if bounded and (result < low_lim or result > high_lim):
                print("Please enter a number between %i and %i!"\
                      % (low_lim, high_lim))
                continue
            acceptable_input = True
        else:
            raise TypeError('Unsupported input type requested.')
    return result
    
def main():
    """Uses the Get_Input function to pester the user for various types of
    input."""
    print("Hello world from user_input.py!")
    print("Let's try asking the user for some input.")
    test1 = GetInput('Give me a string: ', str)
    test2 = GetInput('Give me an integer: ', int)
    test3 = GetInput('Give me an integer between 0 and 10: ', int, True, 0, 10)
    
if __name__ == '__main__':
    main()