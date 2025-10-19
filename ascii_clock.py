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

time = input("Enter the time: ")
clock_type = int(input("Choose the clock type (12 or 24): "))
preferred_char = (input("Enter your preferred character: "))

#ensures that the preffered character is valid:
while(not (preferred_char in "abcdeghkmnopqrsuvwxyz@$&*= ")):
    preferred_char = (input("Character not permitted! Try again: "))
    
if(clock_type == 12): #reformats number from 24 hours to 12 hours if necesary
    time = time + "AM" if(int(time[0:time.index(":")]) <= 12) else str(int(time[:time.index(":")])-12) + time[-3:] + "PM"
    time = "12" + time[1:] if time[0] == "0" else time
def write(time, c):
    out = ""
    for i in range(5): #builds output string one line at a time
        line = "" 
        for l in time:
            c = l if c in "APM1234567890 :" else c #checks if preffered character was left blank, updates to appropraite number if so
            nums = { #hardcoded print formats of each clock character
                '1': [f" {c} ", f"{c}{c} ", f" {c} ", f" {c} ", f"{c}{c}{c}"], #1
                '2': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}"], #2
                '3': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"], #3
                '4': [f"{c} {c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"  {c}"], #4
                '5': [f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"], #5
                '6': [f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"], #6
                '7': [f"{c}{c}{c}", f"  {c}", f"  {c}", f"  {c}", f"  {c}"], #7
                '8': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"], #8
                '9': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"], #9
                '0': [f"{c}{c}{c}", f"{c} {c}", f"{c} {c}", f"{c} {c}", f"{c}{c}{c}"], #0
                
                'A': [f" A ", f"A A", f"AAA", f"A A", f"A A"], #A
                'P': [f"PPP", f"P P", f"PPP", f"P  ", f"P  "], #P
                'M': [f"M   M", f"MM MM", f"M M M", f"M   M", f"M   M"], #M
                ':': [f" ", f":", f" ", f":", f" "] #:
            }
            line += str(nums[l][i]) + " "
        out += line[:-1] + "\n"
    return out[:-1]

print()
print(write(time, preferred_char))