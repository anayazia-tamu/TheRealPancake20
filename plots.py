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
# Assignment: Lab 9.19
# Date: 22 Ocotober 2025

import matplotlib.pyplot as plt
import math

t_data = [0, 0.45, 1.1, 1.75, 2.25, 2.7]
y_data = [0, 0.23, 0.4, 0.18, 0.07, 0.01]
x_values = []
x_1 = []
y_1 = []
y_2 = []

# f1 = t*2**(-1*t**2)
# f2 = (t**4)**(-1*t**2)

for i in range(51):
    t = 3*i/51
    f1 = (t**2)*math.exp(-1*t**2)
    f2 = (t**4)*math.exp(-1*t**2)
    x_values.append(t)
    y_1.append(f1)
    y_2.append(f2)

#first plot    
plt.subplot(2, 1, 1)
plt.plot(x_values, y_1, '-', color='red')
plt.plot(x_values, y_2, '-', color = 'blue')
plt.plot(t_data, y_data, 'ko') 
plt.title('Data and two curves vs time')
plt.xlabel('time (s)')
plt.ylabel('y')
plt.xlim(0, 3)
plt.ylim(0, 1)

#second plot

plt.subplot(2, 1, 2)
plt.plot(t_data, y_data, '^-', color = 'orange')
plt.plot(x_values, y_1, '-', color='blue')
plt.xlabel('time (s)')
plt.ylabel('y')
plt.xlim(1, 2)
plt.ylim(0, 0.5)

plt.show()
    
