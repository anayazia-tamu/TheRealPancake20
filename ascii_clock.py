# By submitting this assignment, I agree to the following:
# "Aggies do not lie, cheat, or steal, or tolerate those who do"
# "I have not given or received any unauthorized aid on this assignment."
#
# Names: 
# Sabin Salazar
# Valen Amarasingham
# Anaya Zia
# Devsashank Mugundhan
# Section: 505
# Assignment: Lab 8.17
# Date: 19 October 2025

time = input("Enter the time: ") # initial time input
clock_type = int(input("Choose the clock type (12 or 24): ")) # either military or AM/PM
preferred_char = (input("Enter your preferred character: ")) # character to be used in place of regular number
    

while(not (preferred_char in "abcdeghkmnopqrsuvwxyz@$&*=")):
    # Grab character values until they are in the given string
    # However, if no character is seleced (space), it will be accepted
    if preferred_char == "":
        break
    else:
        preferred_char = (input("Character not permitted! Try again: "))
print() # blank space for zybook
if(clock_type == 12):
    if "0" == time[0]:
        # in the case that only the minutes are given, implying the hours are zero
        # convert the number to 12 to add on from the previous EOD
        time = time.replace("0", "12")
    elif not (len(time) == 5):
        # if the input is a simple, 3-digit time, such as 2:45
        # add a zero to the front for algorithmic purposes
        time = time[::-1]+"0"
        time = time[::-1]
    if (int(time[0:2]) > 12):
        # conversion frommilitary to AM/PM plus string addition
        convert = int(time[0:2])
        convert -= 12
        time = str(convert) + time[2:] + "PM"
    elif(int(time[0:2])<= 12): 
        # conversion not needed, just AM string 
        time += "AM"

def write(time, c):
    # initial dictionary to use under normal conditions
    nums = {
        '1': [f" {c} ", f"{c}{c} ", f" {c} ", f" {c} ", f"{c}{c}{c}"],
        '2': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}"],
        '3': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
        '4': [f"{c} {c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"  {c}"],
        '5': [f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
        '6': [f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"],
        '7': [f"{c}{c}{c}", f"  {c}", f"  {c}", f"  {c}", f"  {c}"],
        '8': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"],
        '9': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
        '0': [f"{c}{c}{c}", f"{c} {c}", f"{c} {c}", f"{c} {c}", f"{c}{c}{c}"],
        
        'A': [f" A ", f"A A", f"AAA", f"A A", f"A A"],
        'P': [f"PPP", f"P P", f"PPP", f"P  ", f"P  "],
        'M': [f"M   M", f"MM MM", f"M M M", f"M   M", f"M   M"],
        ':': [f" ", f":", f" ", f":", f" "]
    }
    # variable to store the entire string to be output
    out = ""
    for i in range(5): # for loop. There are 5 rows of characters meant to be output
        line = ""  # this variable stores the current row's string to be added to the out string
        for l in time: # for loop for every element in the time data
            if l == "0" and time.index(l) == 0:
                # a zero in the tens hour place does not need to be printed, so it can be skipped
                continue
            elif c == "":
                # if the character the user gave is undefined/nothing, then this code will execute
                # the dictionary of values will get redefined over and over again to match the character 
                # in the given string element
                
                c = l # redefine the character to fit the element
                # redefine each key's value to the ewly redefined character
                nums = {
                    '1': [f" {c} ", f"{c}{c} ", f" {c} ", f" {c} ", f"{c}{c}{c}"],
                    '2': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}"],
                    '3': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
                    '4': [f"{c} {c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"  {c}"],
                    '5': [f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
                    '6': [f"{c}  ", f"{c}  ", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"],
                    '7': [f"{c}{c}{c}", f"  {c}", f"  {c}", f"  {c}", f"  {c}"],
                    '8': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"],
                    '9': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
                    '0': [f"{c}{c}{c}", f"{c} {c}", f"{c} {c}", f"{c} {c}", f"{c}{c}{c}"],
                    
                    'A': [f" A ", f"A A", f"AAA", f"A A", f"A A"],
                    'P': [f"PPP", f"P P", f"PPP", f"P  ", f"P  "],
                    'M': [f"M   M", f"MM MM", f"M M M", f"M   M", f"M   M"],
                    ':': [f" ", f":", f" ", f":", f" "]
                }
                c = "" # reset the character value so the condition can evaluate to true next time
            if l == time[-1]:
                # add string with no space if it is the last of the line
                line += str(nums[l][i])
            else:
                # add string with space if it is not the last of the line
                line += str(nums[l][i]) + " "
        if i != 4:
            # add line to the entire string output with new line if not the last line
            out += line + "\n"
        else: 
            # add line to end as is if last line
            out += line
    return out # return the entire string output


print(write(time, preferred_char)) # output the returned string
