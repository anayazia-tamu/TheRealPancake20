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
# Assignment: Lab 2.8
# Date: 27 August 2025

# init_dist 
# fin_dist = 
# fin_time = 45
# init_time = 10

import math

def lin_inter(time):
    return (((23029-2029)/(55-10))*(time-10) + 2029) % (2 * math.pi * 6745)

print("Part 1:")
print(f"For t = 25 minutes, the position p = {lin_inter(25)} kilometers")

print("Part 2:")
print(f"For t = 300 minutes, the position p = {lin_inter(300)} kilometers")

