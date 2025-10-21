def print_puzzle(puzzle):
    ''' Print puzzle as a long division problem. '''
    puzzle = puzzle.split(',')
    for i in range(len(puzzle)):
        if i == 1:
            print(f'{len(puzzle[i].split("|")[1]) * "_": >16}')
        print(f'{puzzle[i]: >16}')
        if i > 1 and i % 2 == 0:
            print(f"{'-'*len(puzzle[i]): >16}")
            
def make_number(word, guess):
    number = num1+ num2
    return int(number)

def make_numbers(num1, num2):
    return (number1, number2, number3, number4)
    
def main():
    # The lines below demonstrate what the print_puzzle function outputs.
    puzzle = "RUE,EAR | RUMORS,UEII  ,UKTR ,EAR ,KEOS,KAIK,USA"
    print()
    print_puzzle(puzzle)

def get_valid_letters(s):
    

def is_valid_guess(b1, b2) -> bool:
    return all(i in b1 for i in b2) and (len(b1) == len(b2)) and (len(b2) == 10)


def check_user_guess(dividend, quotient, divisor, remainder) -> bool:
    return (dividend == (quotient * divisor) + remainder)
    

     




if __name__ == '__main__':
    main()
    



