import numpy as np

def diceroll_6():
    """Function for rolling 3 six-sided dice, and summing the second 2."""
    d = np.random.randint(1,7,[3])
    return [d[0],d[1]+d[2]]

def diceroll_20():
    """Function for rolling 20-sided die."""
    return np.random.randint(1,21)