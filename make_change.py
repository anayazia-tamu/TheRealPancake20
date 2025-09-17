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
# Assignment: Lab 4.16
# Date: 08 September 2025

import math

# insert readable code
pay = 100*float(input("How much did you pay? "))
cost = 100*float(input("How much did it cost? "))
change = (pay-cost)
quarts = change // 25
change -= 25 * quarts
dimes = change // 10
change -= 10 * dimes
nicks = change // 5
change -= 5*nicks
pennies = int(change)


print(f"You received ${(pay-cost)/100:.2f} in change. That is...")
if(quarts > 0):
    if(quarts == 1):
        print(f"{int(quarts)} quarter")
    else:
        print(f"{int(quarts)} quarters")
if(dimes > 0):
    if(dimes == 1):
        print(f"{int(dimes)} dime")
    else:
        print(f"{int(dimes)} dimes")
if(nicks > 0):
    if(nicks == 1):
        print(f"{int(nicks)} nickel")
    else:
        print(f"{int(nicks)} nickels")
if(pennies > 0):
    if(pennies == 1):
        print(f"{int(pennies)} penny")
    else:
        print(f"{int(pennies)} pennies")

