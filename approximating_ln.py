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
# Assignment: Lab 5.16
# Date: 22 September 2025


import math
x = float(input("Enter a value for x: "))
while((x <= 0 or x > 2)):
    x = float(input("Out of range! Try again: "))
tol = float(input("Enter the tolerance: "))
val = x - 1          
n = 2
next = (((x-1) ** n) / n) * (-1, 1)[n%2]
while (abs(next)>=tol):
    #print(val)
    val += next
    n += 1
    next = (((x-1) ** n) / n) * (-1, 1)[n%2]

diff = abs(math.log(x) - val)
print(f"ln({x}) is approximately {val}")
print(f"ln({x}) is exactly {math.log(x)}")
print(f"The difference is {diff}")
