time = input("Enter the time: ")
clock_type = int(input("Choose the clock type (12 or 24): "))
preferred_char = (input("Enter your preferred character: "))
    
while(not (preferred_char in "abcdeghkmnopqrsuvwxyz@$&*=")):
    if preferred_char == "":
        break
    else:
        preferred_char = (input("Character not permitted! Try again: "))
    
if(clock_type == 12):
    if "0" == time[0]:
        time = time.replace("0", "12")
    elif not (len(time) == 5):
        time = time[::-1]+"0"
        time = time[::-1]
    if (int(time[0:2]) > 12):
        convert = int(time[0:2])
        convert -= 12
        time = str(convert) + time[2:] + "PM"
    elif(int(time[0:2])<= 12): 
        time += "AM"

def write(time, c):
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
    out = ""
    for i in range(5):
        line = "" 
        for l in time:
            if l == "0" and time.index(l) == 0:
                continue
            elif c == "":
                c = l
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
                c = ""
            if l == time[-1]:
                line += str(nums[l][i])
            else:
                line += str(nums[l][i]) + " "
        if i != 4:
            out += line + "\n"
        else: 
            out += line
    return out

print(write(time, preferred_char))
