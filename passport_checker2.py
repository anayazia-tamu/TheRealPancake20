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
# Assignment: Lab 11.9
# Date: 5 November 2025

import re

file = input("Enter the name of the file: ")

f = open(file, "r+")
r = open("valid_passports2.txt", "w")
required = ["iyr", "eyr", "hgt", "hcl", "ecl", "pid", "cid"]
eyes = ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]
valid_pass = [line for line in f.read().split("\n\n") if all(part in line for part in ["iyr", "eyr", "hgt", "hcl", "ecl", "pid", "cid"])]

valid_real = []
passw = valid_pass[0]
for passw in valid_pass:
    valid = True
    iyr = int(passw[passw.index("iyr")+4: passw.index("iyr")+9])
    valid = iyr <= 2025 and iyr >= 2015 and valid    

    eyr = int(passw[passw.index("eyr")+4: passw.index("eyr")+9])
    valid = eyr <= 2035 and eyr >= 2025 and valid

    m = re.search(r"\d+(in|cm)", passw[passw.index("hgt")+4: -1])
    hgt = int(m.group(0)[:-2]) if m else -1
    valid = ((hgt>=59 and hgt <=76) or (hgt >=150 and hgt <= 193)) and valid

    hcl = passw[passw.index("hcl")+4: passw.index("hcl")+11]
    valid = re.match(r"^#\w{6}$", hcl) and valid

    ecl = passw[passw.index("ecl")+4: passw.index("ecl")+7]
    valid = ecl in eyes and valid

    pid = passw[passw.index("pid")+4: passw.index("pid")+13]
    valid = pid.isnumeric() and valid

    cid = int(passw[passw.index("cid")+4: passw.index("cid")+8])
    valid = cid > 99 and cid < 1000 and  valid
    
    if valid:
        r.write(f"{passw}\n\n")
        valid_real.append(passw)

print(f"There are {len(valid_real)} valid passports")
f.close()
r.close()
