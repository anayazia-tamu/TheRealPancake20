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


#Starter Code
def print_puzzle(puzzle):
    ''' Print puzzle as a long division problem. '''
    puzzle = puzzle.split(',')
    for i in range(len(puzzle)):
        if i == 1:
            print(f'{len(puzzle[i].split("|")[1]) * "_": >16}')
        print(f'{puzzle[i]: >16}')
        if i > 1 and i % 2 == 0:
            print(f"{'-'*len(puzzle[i]): >16}")

    
######Starter Code End

def make_number(word, user_guess):
    return int("".join(list(str(user_guess.index(i)) for i in word)))

def make_numbers(puzzle, guess):
    puzzle = puzzle.split(",")
    #RUMORS, RUE, EAR, USA
    #"RUE,EAR | RUMORS,UEII  ,UKTR ,EAR ,KEOS,KAIK,USA"
    return (make_number(puzzle[1][puzzle[1].index("| "):].replace("| ", ""), guess),
        make_number(puzzle[0].replace(" ", ""), guess),
        make_number(puzzle[1][:puzzle[1].index("|")].replace(" ", ""), guess),
        make_number(puzzle[-1].replace(" ", ""), guess))

def get_valid_letters(s):
    return "".join(set(i for i in s if i not in ",| "))

def is_valid_guess(b1, b2) -> bool:
    for num in b1:
        count = 0
        for num2 in b2:
            if num == num2:
                count += 1
        if count > 1:
            break
    x = len(set(i for i in b2)) == 10) and count == 1
    return x


def check_user_guess(dividend, quotient, divisor, remainder) -> bool:
    return (dividend == quotient * divisor + remainder)
    
def main():
    puzzle_input = input("Enter a word arithmetic puzzle: ")
    
    # The lines below demonstrate what the print_puzzle function outputs.
    #puzzle_input = "RUE,EAR | RUMORS,UEII  ,UKTR ,EAR ,KEOS,KAIK,USA"
    # [FAIL] Puzzle: SAG,SOW | GLOSSY,NSAS  ,EGLS ,EOGT ,OTYY,OSSO,OEA, Guess: Invalid guess
    # Some guesses: LONGESTWAY GLOSETYNAW GLASS GGLOSETYNA
    print()
    print_puzzle(puzzle_input)
    print()
    guess_input = input("Enter your guess, for example ABCDEFGHIJ: ")
    if(len(guess_input) != 10):
        print("Your guess should contain exactly 10 unique letters used in the puzzle.")
    elif is_valid_guess(get_valid_letters(puzzle_input), guess_input):
        guessnum = make_numbers(puzzle_input, guess_input)
        if check_user_guess(guessnum[0], guessnum[1], guessnum[2], guessnum[3]):
            print("Good Job!")
        else:
            print("Try again!)
    else:
        print("Try again!")
    

if __name__ == '__main__':
    main()
    #print(is_valid_guess("asdfghjklp", "plkjhgfdsa"))
