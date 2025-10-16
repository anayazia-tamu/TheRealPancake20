time = input("Enter the time: ")
clock_type = int(input("Choose the clock type (12 or 24): "))
preferred_char = (input("Enter your preffered character:"))

while(not (preferred_char in "abcdeghkmnopqrsuvwxyz@$&*=")):
    preferred_char = (input("Character not permitted! Try again: "))
    
if(clock_type == 12):
    if(len(time) == 5 and not(time[0:2] == "12")):
        convert = int(time[0:2])
        convert -= 12
        time = str(convert) + time[2:] + "AM"
    elif(time[0:2]== "12"): 
        time += "AM"
    else: 
        time += "PM"









def write(time, c):
    nums = {
        '1': [f" {c} ", f"{c}{c} ", f" {c} ", f" {c} ", f"{c}{c}{c}"],
        '2': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}"],
        '3': [f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
        '4': [f"{c} {c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f"  {c}"],
        '5': [f"{c}{c}{c}", f"{c}  ", f"{c}{c}{c}", f"  {c}", f"{c}{c}{c}"],
        '6': [f"{c}  ", f"{c}  ", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"],
        '7': [f"{c}{c}{c}", f"  {c}", f"  {c}", f"  {c}", f"  {c}"],
        '8': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}"],
        '9': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"  {c}", f" {c}"],
        '0': [f"{c}{c}{c}", f"{c} {c}", f"{c} {c}", f"{c} {c}", f"{c}{c}{c}"],
        
        'A': [f" {c} ", f"{c} {c}", f"{c}{c}{c}", f"{c} {c}", f"{c} {c}"],
        'P': [f"{c}{c}{c}", f"{c} {c}", f"{c}{c}{c}", f"{c}  ", f"{c}  "],
        'M': [f"{c}   {c}", f"{c}{c} {c}{c}", f"{c} {c} {c}", f"{c}   {c}", f"{c}   {c}"],
        ':': [f" ", f":", f" ", f":", f" "]
    }
    out = ""
    for i in range(5):
        line = "" 
        for l in time:
            line += str(nums[l][i]) + " "
        out += line + "\n"
    return out


print(write(time, preferred_char))