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
# Assignment: Your Stony Past
# Date: 29 September 2025


board = [[' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']]

for y in range(1, 10):
    row = []
    for x in range(10):
        if(x!=0):
            row.append(".")
        else:
            row.append(y)
    board.append(row)

black = True


go = True
while(go):
    for row in board:
        for square in row:
            print(square, end=' ')
        print()
    go = input("continue or stop? ").lower() != "stop"
    if(not go):
        break

    print(("Player 2: ", "Player 1: ")[black])
    y = int(float(input("Which row?(1-9): ")))
    x = ord(input("Which col?(A-I): ").lower())-96 #ACII value

    
    if(x > 0 and x < 10 and y > 0 and y < 10 and board[y][x] == "."):
        board[y][x] = (chr(9679), chr(9675))[black] #places stone
        black = not black #dominican ppl be like
    else:
        print("Location is invalid. Please enter a new location.")
