import numpy as np

def diceroll_6():
    """Function for rolling 3 six-sided dice, and summing the second 2.

    Returns:
        list of int: list of two int. first element is result of single six-sided die, second element is sum of roll of two other six-sided die.
    """
    d = np.random.randint(1,7,[3])
    return [d[0],d[1]+d[2]]

def diceroll_20():
    """Function for rolling 20-sided die.

    Returns:
        int: Result of die roll.
    """
    return np.random.randint(1,21)