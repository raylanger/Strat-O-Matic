from dice import diceroll_20

def runner_advancement(chance):
    """Function for executing conditional runner advancement.

    Args:
        chance (int): Number from 1-19 indicating range of successful rolls

    Returns:
        int: Number indicating whether runner was out (0), held (1), or safe (2) 
    """

    #Ask if runner would like to be sent:
    if input('Would you like to send the runner? (%d) ' % chance) == "Y": #If yes
        
        #Roll; print Out, return 0 if out, else print safe, return 1
        res = diceroll_20()
        print(res)
        if res > chance:
            print("Out!")
            return 0
        else:
            print("Safe!")
            return 2
        
    else: #If no
        return 1