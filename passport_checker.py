
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


file = input("Enter the name of the file: ")

f = open(file, "r+")
r = open("valid_passports.txt", "w")
required = ["iyr", "eyr", "hgt", "hcl", "ecl", "pid", "cid"]
passlist = f.read().split("\n\n")
valid = []

for passw in passlist: 
    if all(field in passw for field in required):
        r.write(f"{passw}\n\n")
        valid.append(passw)

print(f"There are {len(valid)} valid passports")
#r.write("\n\n".join([line for line in f.read().split("\n\n") if all(part in line for part in ["iyr", "eyr", "hgt", "hcl", "ecl", "pid", "cid"])]))
f.close()
r.close()




# valens bs 
