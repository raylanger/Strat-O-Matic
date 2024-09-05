from dice import diceroll_20

def runner_advancement(chance):
    #Ask manager if runner should go
    if input('Would you like to send the runner? (%d) ' % chance) == "Y":
        
        #Roll; print Out, return 0 if out, else print safe, return 1
        res = diceroll_20()
        print(res)
        if res > chance:
            print("Out!")
            return 0
        else:
            print("Safe!")
            return 2
        
    #Hold if manager chooses
    else:
        return 1