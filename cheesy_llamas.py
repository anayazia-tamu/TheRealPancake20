# Program that takes arbitrary x, y data pairs, then calculates linear interpolation / extrapolation for any x

def get_user_data():
    """ Parameters: (none)
        Function asks user to type in an x then a corresponding y. If user types 'q', it exits. The values are added
        into x and y lists. The user is also asked what the dependent variable is.
        Return: x_list (list, x-values), y_list (list, y-values), depend_var (string, user defined dependent var) """

    x_list = []  # [5, 2, 3, 8, 97, 65]                                     # lists created here for testing purposes
    y_list = []  # [1022, 87, 99, 1180, 5, 42]                              # (easier than typing input each time)
    depend_var = input("What will the dependent variable represent?: ")  # 'Cheese consumed by llamas'
    x = input('Please enter the first x-value: ')
    while x != 'q':
        x_list.append(float(x))
        y_list.append(float(input('Please enter the y-value: ')))
        x = input('Please enter next x-value ("q" to quit): ')
    return x_list, y_list, depend_var


def write_input(x_list, y_list, v):
    """ parameters: x (list, contains x-values), y (list, contains y-values), v (str, dependent variable from user).
        Function writes into nailedit.txt file the values, formatted as required in problem statement. """

    # ---- WRITE HEADER AND X-Y VALUES TO EXTERNAL FILE ----
    pass # <-- replace this with your code



def reorder_lists(x_list, y_list):
    """ parameters: x_list (list, contains x-values), y_list (list, contains y-values).
        Function finds min of list, and appends that value to a new list. Takes same indexed value from y-list into
        ordered y-list at the same time.
        return: ord_x (list, ordered x-list), ord_y (list, ordered y-list). """

    # ---- REORDER THE LISTS ----
    ord_x = []
    ord_y = []
    for i in range(len(x_list)):
        min_index = x_list.index(min(x_list))
        ord_x.append(x_list.pop(min_index))
        ord_y.append(y_list.pop(min_index))
    return ord_x, ord_y


def extrapolate(x_list, y_list, x):
    """ parameters: x_list (list, contains x-values), y_list (list, contains y-values), x (float, current x-value).
        Function finds whether this x is above or below the data set, and then extrapolates the y-value. Function
        return: y (float), and string 'extrapolated' """

    if x < x_list[0]:  # extrapolate low
        y = y_list[0] + ((x - x_list[0]) / (x_list[1] - x_list[0])) * (y_list[1] - y_list[0])
    elif x > x_list[-1]:  # extrapolate high
        y = y_list[-2] + (x - x_list[-2]) / (x_list[-1] - x_list[-2]) * (y_list[-1] - y_list[-2])
    return y, 'extrapolated'


def interpolate(xlist, ylist, xvalue):
    """ parameters: x_list (list, contains x-values), y_list (list, contains y-values), x (float, current x-value).
        Function finds which data x values the current x falls between, and then interpolates the y-value.
        return: y (float), and string 'interpolated' """

    for i in range(len(xlist) - 1):
        if xlist[i] <= xvalue <= xlist[i + 1]:
            # lower_x_int = xlist[i]
            # upper_x_int = xlist[i + 1]
            y = ylist[i] + (xvalue - xlist[i]) * (ylist[i + 1] - ylist[i]) / (xlist[i + 1] - xlist[i])
    return y, 'interpolated'


def print_to_screen(x, y, t):
    """ parameters: x (float), y (float), t (string).
        Function prints to screen the x, corresponding y, and whether it was interpolated or extrapolated.
        return: (none) """

    print('For x =', x)
    print(f'The {t} value of y = {y : .1f}')


def print_to_file(x, y, t):
    """ parameters: x (float), y (float), t (string).
        Function writes to file the x, corresponding y, and whether it was interpolated or extrapolated.
        return: (none) """

    # ---- WRITE X-Y VALUES AND ESTIMATION TYPE TO EXTERNAL FILE ----
    pass # <-- replace this with your code


#########################################################################
# ----------------------------- MAIN CODE ----------------------------- #

# ---- Take user inputs
x_data, y_data, variable = get_user_data()

# ---- Write the inputs formatted into correct file
write_input(x_data, y_data, variable)

# ---- Order the values for the estimation
ordered_x, ordered_y = reorder_lists(x_data, y_data)

# ---- Repeatedly take values from user and estimate the y value
x_val = input("Enter an x value ('q' to quit): ")

while x_val != 'q':
    x_val_float = float(x_val)

    # Determine if y-value needs to be extrapolated or interpoled
    if x_val_float < ordered_x[0] or x_val_float > ordered_x[-1]:
        y_val, y_type = extrapolate(ordered_x, ordered_y, x_val_float)
    else:
        y_val, y_type = interpolate(ordered_x, ordered_y, x_val_float)

    # Print x, y and type of estimation to the screen and external file
    print_to_screen(x_val, y_val, y_type)
    print_to_file(x_val_float, y_val, y_type)

    # Update x_val (or quit)
    x_val = input("Enter an x value ('q' to quit): ")

# ---- Be polite
print('Have a great day!')
