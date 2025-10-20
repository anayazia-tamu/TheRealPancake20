'''
get time from user input
get preffered clock type from input (12 or 24)
get preffered character from user input

checks to see if preffered character is valid, repeatedly prompts user until so

reformats time from 24 to 12 hour format if user selected 12 hour clock

defines the write function, which returns a string of the paramater as ascii art
    loop that runs five times, once per line of output
        a loop runs once per character in the time inputed
            a dictionary contains a pair of each valid character and a list of five lines used to construct that character
            a line is constructed, getting each line segment from the characters in order
        the completed line is added to the output
    the completed output is returned

prints the completed output from the write function


'''