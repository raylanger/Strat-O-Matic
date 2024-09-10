import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from player import pitcher, batter
import pandas as pd
from dice import diceroll_6, diceroll_20
import re 
from running import runner_advancement
from fielding import fieldingchart
from tabulate import tabulate

#Class for the state of the current game - players, score, outs, etc.
class game_state():
    """Class which contains info describing the current state of a baseball game. 
    
    Attributes:
        self.score (list of int, default [0,0]): List of 2 int giving away and home team score, repsectively.
        self.inning (int, default 1): Current inning.
        self.outs (int, default 0): Current outs.
        batting_team (bool, default False): Current batting team. False is Away, True is Home.
        batter (batter, default None): Current batter. Must be of class batter defined in player.py.
        pitcher (pitcher, default None): Current pitcher. Must be of class pitcher defined in player.py.
        positions (list of batter and pitcher, default all None): List of shape (2,10) describing positions for each team. Elements must be of the class pitcher or batter defined in player.py. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH).
        runners (list of batter, default [None,None,None]): List of 3 batters describing the occupation of each base. None is used for an empty base.
        lineup (list of batter): List of batter of shape (2,9) giving lineups for each team. Input lineup may be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot. Default is in increasing order of position number (e.g. DH, C, 1B, etc.)
        lineup_pos (list of int, default [0,0]): list of 2 int describing current spot in the order of each lineup.
        IF_pos (int, default 0): int describing infield position. 0 for normal, 1 for corners in, 2 for infield in.
        hold (bool, default False): Whether or not runners are being held.
        plays (dict): A dictionary connecting play strings to their corresponding functions.
    """
     
    def __init__(self, bat_team=0, runners=None, score=None, outs=0, inning = None,
                 positions=None, lineups=None, lineup_pos=None, IF_pos = None, hold = None):
        """Initialization function for game_state class.

        Arguments:
            bat_team (bool, default False): Current batting team. False or 0 for Away, True or 1 for Home.
            runners (list of None or batter, default [None,None,None]): A list of 3 elements indicating occupation of each base. None is used when the base is empty. The runner is given by the batter class.
            score (list int, default [0,0]): A list of two int specifying away and home score, respectively.
            outs (int, default 0): Current number of outs.
            inning (int, default 1): Current inning.
            positions (list of player): A list of shape (2,10) indicating the players at each position for each team. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH). Provided list may include batter/pitcher classes or str of player names.
            lineups (list of int): List of batter of shape (2,9) giving lineups for each team. May be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot.
            lineup_pos (list of int, default [0,0]): list of 2 int describing current spot in the order of each lineup.
            IF_pos (int, default 0): int describing infield position. 0 for normal, 1 for corners in, 2 for infield in.
            hold (bool, default False): Whether or not runners are being held.
        """

        self.batting_team = bat_team #0 for away, 1 for home
        self.runners = runners if runners is not None else [None, None, None] #Baserunners
        self.score = score if score is not None else [0, 0] #Score
        self.outs = outs #outs
        self.inning = inning if inning is not None else 1 #Inning
        self.positions = positions if positions is not None else [[None, None, None, None, None, None, None, None, None, None], 
                                                                  [None, None, None, None, None, None, None, None, None, None]] #Positions (0 is DH)
        
        #Convert strings in positions to batter or pitcher class
        for j in [0,1]:
            for i in range(10):
                if type(self.positions[j][i]) is str:
                    if i == 1: self.positions[j][i] = pitcher(self.positions[j][i])
                    else: self.positions[j][i] = batter(self.positions[j][i])

                #Ensure no non-player elements were provided.
                assert isinstance(self.positions[j][i], pitcher) or isinstance(self.positions[j][i], batter)
        
        #Set lineup
        if lineups is not None:
            try: #If lineup was provided by position number
                self.lineup = [[self.positions[0][i] for i in lineups[0]], 
                       [self.positions[1][i] for i in lineups[1]]]
            except TypeError: #If lineup was provided 
                self.lineup = lineups

                #Ensure all players are of batter class and are listed in positions
                for i in [0,1]:
                    for j in range(10):
                        assert isinstance(lineups[i][j], batter)
                        assert lineups[i][j] in positions[i]
        else: #Default
            self.lineup = [[self.positions[0][i] for i in [0,2,3,4,5,6,7,8,9]],
                           [self.positions[1][i] for i in [0,2,3,4,5,6,7,8,9]]] 
        
        
        self.lineup_pos = lineup_pos if lineup_pos is not None else [0, 0] #Current batter position in each lineup
        self.pitcher = self.positions[1 - self.batting_team][1] #Current pitcher
        self.batter = self.lineup[self.batting_team][self.lineup_pos[self.batting_team]] #Current batter
        self.IF_pos = IF_pos if IF_pos is not None else 0 #Infield position (0 for normal, 1 for corners in, 2 for infield in)
        self.hold = hold if hold is not None else False #Holding runners

        self.plays = {"K": self.K, "BB": self.BB, "HBP": self.BB, 
                              "HR": self.HR, "S": self.S, "D": self.D, "T": self.T,
                              "FB": self.FB, "GB": self.GB, 'lomax': self.lomax, "LO": self.LO, "PO": self.PO, "FO": self.FO, 
                              "X": self.X,"E": self.E, "WP": self.WP, "PB": self.PB}

    def update_pitcher_batter(self):
        """Updates pitcher and batter to those based on current batting team, position list and lineup position.
        """
        self.pitcher = self.positions[1-self.batting_team][1] #Set pitcher
        self.batter = self.lineup[self.batting_team][self.lineup_pos[self.batting_team]] #Set batter
    
    def display(self):
        """A function for displaying the current game state."""

        #Define dictionaries containing information about the box styles used to list fielder and runner names.
        bbox_fielder = {'boxstyle': 'round','alpha': 0.8, 'pad' : 0.2, 'ec' : 'k', 'fc' : 'w'}
        bbox_runner = {'boxstyle': 'round','alpha': 0.8, 'pad' : 0.2, 'ec' : 'r', 'fc' : 'w'}

        #Create figure and axis
        fig = plt.figure(figsize = [8,8])
        ax = fig.add_subplot()

        #Set title as the score
        ax.set_title("%d-%d" % (self.score[0],self.score[1]), fontsize = 14)

        #Put inning and outs in top left.
        ax.text(0.02,0.98, "%s%d\n%d Outs" % ("T" if self.batting_team == 0 else "B", self.inning,self.outs), ha = 'left', va = 'top', transform = ax.transAxes, fontsize = 14)

        #Plot image of baseball diamond
        img = np.asarray(Image.open('diamonddiagram.jpg'))
        ax.imshow(img)
        ax.axis('off')

        #If runners occupt bases, colour base black and write runner name
        if self.runners[0] is not None:
            ax.add_patch(matplotlib.patches.Polygon([[0.7210526315789474,0.35452793834296725],
                                [0.7535087719298246,0.31888246628131023],
                                [0.7842105263157895,0.35452793834296725],
                                [0.7535087719298246,0.3901734104046243]], fc = 'k', transform = ax.transAxes))
            ax.text(0.8,0.33,self.runners[0].name,ha = 'center',va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)


        if self.runners[1] is not None:
            ax.add_patch(matplotlib.patches.Polygon([[0.46842105263157896,0.6358381502890174],
                                [0.5008771929824561,0.6001926782273603],
                                [0.5333333333333333,0.6358381502890174],
                                [0.5008771929824561,0.6714836223506744]], fc = 'k', transform = ax.transAxes))
            ax.text(0.5,0.65,self.runners[1].name,ha = 'center',va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)

        if self.runners[2] is not None:
            ax.add_patch(matplotlib.patches.Polygon([[0.21929824561403508,0.35452793834296725],
                                [0.25,0.31888246628131023],
                                [0.2807017543859649,0.35452793834296725],
                                [0.25,0.3901734104046243]], fc = 'k', transform = ax.transAxes))
            ax.text(0.2,0.33,self.runners[2].name,ha = 'center',va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)

        #Write all fielder names in respective positions
        ax.text(0.5,0.38,self.positions[1-self.batting_team][1].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.5,0.03,self.positions[1-self.batting_team][2].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.75,0.42,self.positions[1-self.batting_team][3].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.65,0.55,self.positions[1-self.batting_team][4].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.35,0.55,self.positions[1-self.batting_team][6].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.25,0.42,self.positions[1-self.batting_team][5].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.2,0.68,self.positions[1-self.batting_team][7].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.5,0.85,self.positions[1-self.batting_team][8].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.8,0.68,self.positions[1-self.batting_team][9].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        
        #Write batter name on proper side of plate
        if self.batter.hand == 'R' or (self.batter.hand == 'S' and self.pitcher.hand == 'L'):
            ax.text(0.47,0.1,self.batter.name, ha = 'right', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        else:
            ax.text(0.53,0.1,self.batter.name, ha = 'left', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        plt.show()
    
    def S(self, typ):
        """Updates game state for all variety of singles.

        Args:
            typ (int or str): Describes the type of single for runner advancement purposes. Number of '*' indicates guaranteed base advancement, and an int denotes position for conditional advancement.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments ('out' if runner thrown out)
            list: Additional score card arguments (Always empty)
        """

        BS_arg = ['']
        if typ == '*': #Single, 1 base advance

            #Runs score only if runner on third
            runs = [i.name for i in self.runners[2:] if i is not None] 
            self.score[self.batting_team] += len(runs)
            
            #Move all runners up 1
            self.runners[2] = self.runners[1]
            self.runners[1] = self.runners[0]
            self.runners[0] = self.batter
            
        elif typ == '**': #Single, 2 base advance
            
            #Increase score by number of batters on second and third
            runs = [i.name for i in self.runners[1:] if i is not None]
            self.score[self.batting_team] += len(runs) 

            #Move runners up 2
            self.runners[2] = self.runners[0]
            self.runners[1] = None
            self.runners[0] = self.batter
            
        else: #Single, to specific positions

            #If runner on second: runner may choose to score
            if self.runners[1] is not None:
                
                #Parameters for determing safe/out chance
                speed = self.runners[1].run
                arm = self.positions[1-self.batting_team][typ].field[typ][2]
                outs2 = self.outs == 2

                #Chance of bering safe
                chance = min([20,max([1,speed + arm + 2*outs2])])

                #Run runner_advancement
                res = runner_advancement(chance)
                
                if res == 0: #If out: remove runner from second then single, 2-base advance
                    self.outs += 1
                    self.runners[1] = None
                    runs = self.S('**')[0]
                    BS_arg = ['out']

                elif res == 2: #If safe: single, 2-base advance
                    runs = self.S('**')[0]
                else: #If held: single, 1-base advance
                    runs = self.S('*')[0]

            #If no runner on second, and runner on first: runner may choose to go to third
            elif self.runners[0] is not None:
                
                #Parameters for determing safe/out chance
                speed = self.runners[0].run
                arm = self.positions[1-self.batting_team][typ].field[typ][2]
                outs2 = self.outs == 2
                extra = 2*(typ-8)
                
                #Chance of bering safe
                chance = min([20,max([1,speed + arm + 2*outs2 + extra])])
                
                #Run runner advancement for runner on first going to third, to fielder it was hit to
                res = runner_advancement(chance)
                
                if res == 0: #If out: remove runner from first then single, 2-base advance
                    self.outs += 1
                    self.runners[0] = None
                    self.S('**')
                    BS_arg = ['out']
                elif res == 2:#If safe: single, 2-base advance
                    runs = self.S('**')[0]
                else:#If held: single, 1-base advance
                    runs = self.S('*')[0]

            else: #If no runners on first or second: single, 1-base advance
                runs = self.S('*')[0]

        return runs, True, BS_arg, []

    def D(self, typ):
        """Updates game state for all variety of doubles.

        Args:
            typ (int or str): Describes the type of single for runner advancement purposes. Number of '*' indicates guaranteed base advancement, and an int denotes position for conditional advancement.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments ('out' if runner thrown out)
            list: Additional score card arguments (Always empty)
        """
        
        if typ == '**': #2-base double
            
            #Runners on second and third score
            runs = [i.name for i in self.runners[1:] if i is not None]
            self.score[self.batting_team] += len(runs) 

            #Move runners up 2
            self.runners[2] = self.runners[0]
            self.runners[1] = self.batter
            self.runners[0] = None
            
        elif typ == '***':
            #All runners score
            runs = [i.name for i in self.runners if i is not None]
            self.score[self.batting_team] += len(runs) 
            
            #Empty bases, put batter on second
            self.runners[2] = None
            self.runners[1] = self.batter
            self.runners[0] = None
        
        else:

            #Runner_advancement for runner on first
            if self.runners[0] is not None:
                
                #Parameters for determing safe/out chance
                speed = self.runners[0].run
                arm = self.positions[1-self.batting_team][typ].field[typ][2]
                outs2 = self.outs == 2

                #Chance of bering safe
                chance = min([20,max([1,speed + arm + 2*outs2])])

                #Run runner_advancement
                res = runner_advancement(chance)
                
                if res == 0: #If out: remove runner from first, then double, 2-base advance
                    self.outs += 1
                    self.runners[2] = None
                    runs = self.D('**')[0]
                    BS_arg = ['out']
                if res == 2: #If safe: double, 3-base advance
                    runs = self.D('***')[0]

            else: #If no runner on first: double, 2-base advance
                runs = self.D('**')[0]

        return runs, True, BS_arg, []

    def T(self):
        """Updates game state for a triple.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always empty)
        """
        #All runners score
        runs = [i.name for i in self.runners if i is not None]
        self.score[self.batting_team] += len(runs)

        #Empty bases, batter on third
        self.runners[2] = self.batter
        self.runners[1] = None
        self.runners[0] = None

        return runs, True, [], []
    
    def HR(self):
        """Updates game state for a home run.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always empty)
        """
        #Score all runners and batter
        runs = [self.batter.name] + [i.name for i in self.runners if i is not None]
        self.score[self.batting_team] += len(runs)

        #Empty bases
        self.runners = [None,None,None]
        
        return runs, True, [], []
    
    def FB(self,pos,typ):
        """Updates game state for all types of flyballs.

        Args:
            pos (int): position flyball was hit to
            typ (str): One of 'A', 'B', 'B?', or 'C'

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (maybe 'sac' for sacrifice or 'dp' for double play)
            list: Additional score card arguments (position and maybe 'sac' for sacrifice or 'dp' for double play)
        """

        #Increase outs by 1
        self.outs += 1 

        #Set default runs and typ2
        runs = []
        typ2 = '' #Modifier for tracking dp and sf

        if self.outs < 3: #If inning continues
                
            if 'A' in typ: #All runners advance

                #Runner on third scores
                runs = [self.runners[2].name] if self.runners[2] is not None else []
                self.score[self.batting_team] += len(runs) 
                
                #Set typ2 modifier to sac if runner scored
                typ2 = 'sac' if bool(len(runs)) else ''

                #Move runners up 1
                self.runners[2] = self.runners[1]
                self.runners[1] = self.runners[0]
                self.runners[0] = None
                
            elif 'B' in typ: #Runner on third advances
                if "?" in typ: #For questionable fly ball
                    if self.runners[2] is not None: #Runner on third may advance

                        #Parameters for determing safe/out chance
                        speed = self.runners[2].run 
                        arm = self.positions[1-self.batting_team][pos].field[pos][2]
                        
                        #Chance of success
                        chance = min([20,max([1,speed + arm + 2])])

                        #Run runner_advancement
                        res = runner_advancement(chance)

                        if res == 0: #If out: Set as 'dp'
                            self.outs += 1
                            self.runners[2] = None
                            typ2 = 'dp'
                        elif res == 2: #If scores: Set as 'sac'
                            self.score[self.batting_team] += 1
                            runs = [self.runners[2].name]
                            self.runners[2] = None
                            typ2 = 'sac'
                        

                else: #Guaranteed sacrifice

                    #Runner on third scores
                    runs = [self.runners[2].name] if self.runners[2] is not None else []
                    self.score[self.batting_team] += len(runs)

                    #Set modifier to 'sac' if runner scored
                    typ2 = 'sac' if bool(len(runs)) else ''

                    self.runners[2] = None
                    
                    #Runner on second may advance if FB to right
                    if self.runners[1] is not None and pos == 9:

                        #Parameters for determing safe/out chance
                        speed = self.runners[1].run #speed
                        arm = self.positions[1-self.batting_team][pos].field[pos][2] #fielder arm
                        
                        #Chance of success
                        chance = min([20,max([1,speed + arm + 2])])

                        #Abnormal runner_advancement: Runner only out on exactly 20
                        if input('Would you like to send the runner? (%d) ' % chance) == "Y":
            
                            #Roll dice
                            res = diceroll_20() #Dice roll
                            print(res)
                            if res <= chance: #Safe if less than chance
                                print("Safe!")
                                self.runners[2] = self.runners[1]
                                self.runners[1] = None
                            elif res == 20: #Out if 20
                                print("Out!")
                                self.outs += 1
                                self.runners[1] = None
                            else: #Else holds
                                print('Runner holds')
        
        return runs, True, [typ2], [pos,typ2]

    def GB(self, pos, typ):
        """Updates game state for all types of groundballs.

        Args:
            pos (int): position groundball was hit to
            typ (str): One of 'A', 'A+', 'B', or 'C'

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (False if dp)
            list: Additional box score arguments (maybe 'dp' for double play or 'fc' for fielder choice)
            list: Additional score card arguments (position and maybe 'dp' for double play or 'fc' for fielder choice)
        """
        
        #Increase outs by 1
        self.outs += 1

        #Set default runs
        runs = []

        if self.outs < 3: #If inning continues
            if 'A' in typ: #Double play
                if self.runners[0] is not None: #Double play
                    self.outs += 1 #Increase outs by 1
                    if self.outs < 3:#If inning continues

                        #Runner on third scores
                        runs = [self.runners[2].name] if self.runners[2] is not None else []
                        self.score[self.batting_team] += len(runs)

                        #Runner on second advances to third. Other runners out
                        self.runners[2] = self.runners[1]
                        self.runners[1] = None
                        self.runners[0] = None

                    #Runs are not RBIs 
                    return runs, False, ['dp'], [pos,'dp']
                
                return runs, False, [''], [pos, '']
            
            elif 'B' in typ: #Force play

                if self.runners[0] is not None: #Runner on first is out, other runners advance (otherwise, all runners hold)
                    
                    #Runner on third scores
                    runs = [self.runners[2].name] if self.runners[2] is not None else []
                    self.score[self.batting_team] += len(runs)

                    #Runner on second moves to third, runner on first is batter
                    self.runners[2] = self.runners[1]
                    self.runners[1] = None
                    self.runners[0] = self.batter

                    return runs, True, ['fc'], [pos,'fc'] 
                
                return runs, True, [''], [pos, '']
            
            elif 'C' in typ: #Runners advance

                #Runner on third scores
                runs = [self.runners[2].name] if self.runners[2] is not None else []
                self.score[self.batting_team] += len(runs)

                #Move all runners up 1
                self.runners[2] = self.runners[1]
                self.runners[1] = self.runners[0]
                self.runners[0] = None
                return runs, True, [''], [pos, '']
        return runs, True, [''], [pos, '']

    def LO(self,pos):
        """Updates game state for a lineout.

        Returns:
            list: runners who scored (Always empty)
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always pos)
        """
        self.outs += 1
        return [], True, [], [pos]
    
    def PO(self, pos):
        """Updates game state for a popout.

        Returns:
            list: runners who scored (Always empty)
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always pos)
        """
        self.outs += 1
        return [], True, [], [pos]
        
    def FO(self, pos):
        """Updates game state for a foulout.

        Returns:
            list: runners who scored (Always empty)
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always pos)
        """
        self.outs += 1
        return [], True, [], [pos]
                    
    def lomax(self,pos):
        """Updates game state for a lineout into as many outs as possible.

        Returns:
            list: runners who scored (Always empty)
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (number of outs)
            list: Additional score card arguments (pos and bases where outs made)
        """
        #Out for catching
        self.outs += 1

        #Initialize tracker for outs on basepaths
        bases = []
        if self.outs < 3: #If inning continues
            if self.runners[2] is not None: #If runner on third out: Add 2 to list of bases
                self.outs += 1 
                bases.append(2) 
                self.runners[2] = None
            if self.outs < 3: #If inning continues
                if self.runners[1] is not None: #If runner on second out: Add 1 to list of bases
                    self.outs += 1
                    bases.append(1)
                    self.runners[1] = None
                if self.outs < 3: #If inning continues
                    if self.runners[0] is not None: #If runner on first out: Add 0 to list of bases
                        self.outs += 1
                        bases.append(0)
                        self.runners[0] = None

        return [], True, [1 + len(bases)], [pos,bases]

    def K(self):
        """Updates game state for a strikeout.

        Returns:
            list: runners who scored (Always empty)
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always empty)
        """
        self.outs += 1
        return [], True, [], []

    def BB(self):
        """Updates game state for a walk.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always True)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always empty)
        """
        #Runner on third scores if bases loaded
        runs = [self.runners[2].name] if all([i is not None for i in self.runners]) else []
        self.score[self.batting_team] += len(runs)

        #Move runners up if all bases loaded behind them
        self.runners[2] = self.runners[1] if all([i is not None for i in self.runners[:2]]) else self.runners[2]
        self.runners[1] = self.runners[0] if self.runners[0] is not None else self.runners[1]
        self.runners[0] = self.batter
        return runs, True, [], []
        
    def WP(self):
        """Updates game state for a wild pitch.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always False)
        """
        #Runner on third scores
        runs = [self.runners[2].name] if self.runners[2] is not None else []
        self.score[self.batting_team] += len(runs)

        #Move all runners up one
        self.runners = [None, self.runners[0],self.runners[1]]
        return runs, False

    def PB(self):
        """Updates game state for a wild pitch.

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always False)
        """
        #Runner on third scores
        runs = [self.runners[2].name] if self.runners[2] is not None else []
        self.score[self.batting_team] += len(runs)

        #Move all runners up one
        self.runners = [None, self.runners[0],self.runners[1]]
        return runs, False
        
    def X(self,pos):
        """Function for determining outcome of X chance.

        Args:
            pos (int): position that ball was hit to.

        Returns:
            list: outcome plus any additional arguments needed to describe the outcome
        """
        
        #Determine player ball was hit to
        player = self.positions[1-self.batting_team][pos]
        print(player.name)

        #Determine fielding rating
        rating = player.field[pos][0]
        print(rating)

        #Determine Roll
        roll = diceroll_20()
        print(roll)
        
        #Get result
        result = fieldingchart[pos][rating][roll-1]
        if result == 'E': #If result is E, more rolls necessary

            #Determine error rating
            E_n = player.field[pos][1]
            print(E_n)

            #Roll two six-sided dice
            roll2 = diceroll_6()
            print(roll2)

            #Get result
            result = fieldingchart[pos]['E'][E_n][roll2[1]-2]
            if type(result) is list: #Some results require a roll of another six-sided die
                result = result[1] if roll2[0] <= result[0] else result[2] 
        
        #Split result into outcome plus arguments
        result = re.split('[_]', result)
        for i in range(len(result)):
            try:
                result[i] = int(result[i])
            except (TypeError,IndexError, ValueError): pass

        return result

    def E(self, base, pos):
        """Function for updating game state on error

        Args:
            base (int): number of base to advance due to error
            pos (int): position error was hit to

        Returns:
            list: runners who scored
            bool: Controls whether runs scored count as RBI (Always False)
            list: Additional box score arguments (Always empty)
            list: Additional score card arguments (Always position and number of bases)
        """

        #Execute equivalent hits for each base error
        if base == 3:
            runs = self.T()[0]
        elif base == 2:
            runs = self.D('**')[0]
        else:
            runs = self.S('*')[0]

        return runs,False, [], [pos, base]
        

class box_score():
    """Class for the box score of a game. 
    
    Attributes:
        positions (list of batter and pitcher, default all None): List of shape (2,10) describing positions for each team. Elements must be of the class pitcher or batter defined in player.py. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH).
        lineup (list of batter): List of batter of shape (2,9) giving lineups for each team. Input lineup may be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot. Default is in increasing order of position number (e.g. DH, C, 1B, etc.)
        pos_keys (dict): Connects integers from 0-9 to corresponding positions (0 for DH)
        hitters (dict): Dictionary containing the box score stats for each hitter on each team. For each hitter, information is stored in a list of length 8: [Pos,AB,R,H,RBI,HR,BB,K]
        pitchers (dict): Dictionary containing the box score stats for each pitcher on each team. For each pitcher, information is stored in a list of length 6: [IP,H,R,BB,K,HR]
        plays (dict): A dictionary connecting play strings to their corresponding functions.
    """
    def __init__(self, positions, lineups):
        """Initialization function for box_score class.

        Args:
            positions (list of player): A list of shape (2,10) indicating the players at each position for each team. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH). Provided list may include batter/pitcher classes or str of player names.
            lineups (list of int): List of batter of shape (2,9) giving lineups for each team. May be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot.
        """

        #Players at each position by index (0 is DH)
        self.positions = positions if positions is not None else [[None, None, None, None, None, None, None, None, None, None], 
                                                                  [None, None, None, None, None, None, None, None, None, None]] #Positions (0 is DH)
        
        
        #Convert strings in positions to batter or pitcher class
        for j in [0,1]:
            for i in range(10):
                if type(self.positions[j][i]) is str:
                    if i == 1: self.positions[j][i] = pitcher(self.positions[j][i])
                    else: self.positions[j][i] = batter(self.positions[j][i])

                #Ensure no non-player elements were provided.
                assert isinstance(self.positions[j][i], pitcher) or isinstance(self.positions[j][i], batter)

        #Set lineup
        if lineups is not None:
            try: #If lineup was provided by position number
                self.lineup = [[self.positions[0][i] for i in lineups[0]], 
                               [self.positions[1][i] for i in lineups[1]]]
            
            except TypeError: #If lineup was provided 
                self.lineup = lineups

                #Ensure all players are of batter class and are listed in positions
                for i in [0,1]:
                    for j in range(10):
                        assert isinstance(lineups[i][j], batter)
                        assert lineups[i][j] in positions[i]
        
        else: #Default
            self.lineup = [[self.positions[0][i] for i in [0,2,3,4,5,6,7,8,9]],
                           [self.positions[1][i] for i in [0,2,3,4,5,6,7,8,9]]]                 
        
        #Dictionary converting position numbers to position labels
        self.pos_keys = {0: "DH", 1:"P", 2:"C", 3:"1B", 4:"2B", 5:"3B", 6:"SS", 7:"LF", 8:"CF", 9:"RF"}

        #Dictionary containing hitting info (0: Away, 1: Home)
        self.hitters = {0: {'%s'%(positions[0][i].name) : [self.pos_keys[i],0,0,0,0,0,0,0] for i in lineups[0]},
                        1: {'%s'%(positions[1][i].name) : [self.pos_keys[i],0,0,0,0,0,0,0] for i in lineups[1]}}
        
        #Dictionary containing pitching info (0: Away, 1: Home)
        self.pitchers = {0: {'%s'%(positions[0][1].name): [0.,0,0,0,0,0]},
                         1: {'%s'%(positions[1][1].name): [0.,0,0,0,0,0]}}
        
        #Dictionary assigning positions to functions
        self.plays = {"K": self.K, "BB": self.BB, "HBP": self.BB, 
                              "HR": self.HR, "S": self.S, "D": self.D, "T": self.T,
                              "FB": self.FB, "GB": self.GB, 'lomax': self.lomax, "LO": self.LO, "PO": self.PO, "FO": self.FO, 
                              "E": self.E}
        
    def display(self, batter = True, pitcher = True, home = True, away = True):
        """Displays box score.

        Arguments:
            batter (bool, optional, default True): Whether or not to show batter info.
            pitcher (bool, optional, default True): Whether or not to show pitcher info.
            home (bool, optional, default True): Whether or not to show home team info.
            away (bool, optional, default True): Whether or not to show away team info.
        """

        if away:
            #Print tabulated statistics for away players
            print('Away:')
            
            if batter:
                print(tabulate(pd.DataFrame(data = self.hitters[0].values(),columns = ['Pos','AB','R','H','RBI','HR','BB','K'],index = self.hitters[0].keys()),
                                            headers = 'keys', tablefmt = 'fancy_grid'))
            if pitcher:
                print(tabulate(pd.DataFrame(data = self.pitchers[0].values(), columns = ['IP', 'H', 'R', 'BB', 'K', 'HR'], index = self.pitchers[0].keys()),
                                            headers = 'keys', tablefmt = 'fancy_grid'))
        
        if home:
            #Print tabulated statistics for away players
            print('Home:')
            if batter:
                print(tabulate(pd.DataFrame(data = self.hitters[1].values(),columns = ['Pos','AB','R','H','RBI','HR','BB','K'],index = self.hitters[1].keys()),
                                                headers = 'keys', tablefmt = 'fancy_grid'))
            if pitcher:
                print(tabulate(pd.DataFrame(data = self.pitchers[1].values(), columns = ['IP', 'H', 'R', 'BB', 'K', 'HR'], index = self.pitchers[1].keys()),
                                                headers = 'keys', tablefmt = 'fancy_grid'))

    def batter_runs(self, batting_team, batter, runs, RBI):
        """Function for updating batting box score when runs score

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Batter at plate when runs scored
            runs (list of str): Runners who scored
            RBI (bool): Whether runs count as RBI for batter or not.
        """

        #Add 1 to runs column for each runner scored
        for i in runs:
            self.hitters[batting_team][i][2] += 1
        
        #Add no. of runs scored to RBI column, if they count
        if RBI:
            self.hitters[batting_team][batter][4] += len(runs)

    def pitcher_runs(self, batting_team, pitcher, runs, earned = True):
        """Function for updating pitching box score when runs score

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            pitcher (str): Current pitcher
            runs (list of str): Runners who scored
            earned (bool, optional): Whether or not runs are earned. Current not operational
        """

        #Add no. of runs scored to runs column
        self.pitchers[1-batting_team][pitcher][2] += len(runs)

    def K(self, batting_team, batter, pitcher):
        """Updates box score on strikeout.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """
        #Increase batter AB, K by 1
        self.hitters[batting_team][batter][1] += 1
        self.hitters[batting_team][batter][-1] += 1

        #Increase pitcher K by 1, IP by 1/3
        self.pitchers[1-batting_team][pitcher][-2] += 1
        self.pitchers[1-batting_team][pitcher][0] += 1/3
    
    def BB(self, batting_team, batter, pitcher):
        """Updates box score on a walk.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """

        #Increase pitcher and hitter BB by 1
        self.hitters[batting_team][batter][-2] += 1
        self.pitchers[1-batting_team][pitcher][3] += 1

    def HR(self, batting_team, batter, pitcher):
        """Updates box score on a homerun.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """

        #Update batter AB, H, HR by 1
        self.hitters[batting_team][batter][1] += 1
        self.hitters[batting_team][batter][3] += 1
        self.hitters[batting_team][batter][5] += 1

        #Update pitcher H, HR by 1
        self.pitchers[1-batting_team][pitcher][1] += 1
        self.pitchers[1-batting_team][pitcher][-1] += 1
    
    def S(self, batting_team,batter,pitcher, out):
        """Updates box score on a single.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
            out (str): 'out' if runner has been thrown out
        """

        #Increase batter AB and H by 1
        self.hitters[batting_team][batter][1] += 1
        self.hitters[batting_team][batter][3] += 1

        #Increase pitcher H by 1
        self.pitchers[1-batting_team][pitcher][1] += 1

        if out == 'out':
            self.pitchers[1-batting_team][pitcher][0] += 1/3
    
    def D(self, batting_team,batter,pitcher, out):
        """Updates box score on a double.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
            out (str): 'out' if runner has been thrown out
        """

        #Same effect on box score as single
        self.S(batting_team,batter,pitcher, out)
    
    def T(self, batting_team,batter,pitcher):
        """Updates box score on a triple.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """

        #Same effect on box score as single
        self.S(batting_team,batter,pitcher)
    
    def FB(self, batting_team,batter,pitcher, typ):
        """Updates box score on a fly ball.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
            typ (str): Modifier for flyball (either dp for double play or sac for sacrifice)
        """

        #Increase batter AB by 1 if flyball was not a sacrifice
        if typ != 'sac':
            self.hitters[batting_team][batter][1] += 1

        #Increase pitcher IP by (no. of outs)/3
        self.pitchers[1-batting_team][pitcher][0] += (1 + (typ == 'dp'))/3

    def GB(self, batting_team,batter,pitcher, typ):
        """Updates box score on a ground ball.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
            typ (str): Modifier for groundball (either dp for double play or fc for fielders choice)
        """

        #Increase batter AB by 1
        self.hitters[batting_team][batter][1] += 1

        #Increase pitcher IP by (no. of outs)/3
        self.pitchers[1-batting_team][pitcher][0] += (1+(typ=='dp'))/3

    def lomax(self,batting_team, batter,pitcher,outs):
        """Updates box score on lineout into as many outs as possible.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
            outs (int): Number of outs made
        """

        #Increase batter AB by 1
        self.hitters[batting_team][batter][1] += 1

        #Increase pitcher IP by (no. of outs)/3
        self.pitchers[1-batting_team][pitcher][0] += outs/3

    def LO(self,batting_team,batter,pitcher):
        """Updates box score on lineout.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """

        #Increase hitter AB by 1
        self.hitters[batting_team][batter][1] += 1

        #Increase pitcher IP by 1/3
        self.pitchers[1-batting_team][pitcher][0] += 1/3

    def FO(self,batting_team,batter,pitcher):
        """Updates box score on flyout.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """
        #Same effect on box score as lineout
        self.LO(batting_team,batter,pitcher)

    def PO(self,batting_team,batter,pitcher):
        """Updates box score on popout.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """
        #Same effect on box score as lineout
        self.LO(batting_team,batter,pitcher)
    
    def E(self,batting_team,batter,pitcher):
        """Updates box score on error.

        Args:
            batting_team (int): Team batting (0 for away, 1 for home)
            batter (str): Current batter
            pitcher (str): Current pitcher
        """
        #Update batter AB by 1
        self.hitters[batting_team][batter][1] += 1
       
class scorecard():
    """Class for the scorecard of a game. 
    
    Attributes:
        positions (list of batter and pitcher, default all None): List of shape (2,10) describing positions for each team. Elements must be of the class pitcher or batter defined in player.py. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH).
        lineup (list of batter): List of batter of shape (2,9) giving lineups for each team. Input lineup may be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot. Default is in increasing order of position number (e.g. DH, C, 1B, etc.)
        pos_keys (dict): Connects integers from 0-9 to corresponding positions (0 for DH)
        empty (str, default '       '): string used for empty box score. 
        hitters (dict): Dictionary containing the score card information for each hitter on each team. 
        plays (dict): A dictionary connecting play strings to their corresponding functions.
    """
    def __init__(self,positions,lineups):
        """Initialization function for box_score class.

        Args:
            positions (list of player): A list of shape (2,10) indicating the players at each position for each team. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH). Provided list may include batter/pitcher classes or str of player names.
            lineups (list of int): List of batter of shape (2,9) giving lineups for each team. May be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot.
        """

        #Players at each position by index (0 is DH)
        self.positions = positions if positions is not None else [[None, None, None, None, None, None, None, None, None, None], 
                                                                  [None, None, None, None, None, None, None, None, None, None]] #Positions (0 is DH)
        
        
        #Convert strings in positions to batter or pitcher class
        for j in [0,1]:
            for i in range(10):
                if type(self.positions[j][i]) is str:
                    if i == 1: self.positions[j][i] = pitcher(self.positions[j][i])
                    else: self.positions[j][i] = batter(self.positions[j][i])

                #Ensure no non-player elements were provided.
                assert isinstance(self.positions[j][i], pitcher) or isinstance(self.positions[j][i], batter)

        #Set lineup
        if lineups is not None:
            try: #If lineup was provided by position number
                self.lineup = [[self.positions[0][i] for i in lineups[0]], 
                               [self.positions[1][i] for i in lineups[1]]]
            
            except TypeError: #If lineup was provided 
                self.lineup = lineups

                #Ensure all players are of batter class and are listed in positions
                for i in [0,1]:
                    for j in range(10):
                        assert isinstance(lineups[i][j], batter)
                        assert lineups[i][j] in positions[i]
        
        else: #Default
            self.lineup = [[self.positions[0][i] for i in [0,2,3,4,5,6,7,8,9]],
                           [self.positions[1][i] for i in [0,2,3,4,5,6,7,8,9]]]
            
        #Dictionary connecting numbers 0-9 to corresponding position labels
        self.pos_keys = {0: "DH", 1:"P", 2:"C", 3:"1B", 4:"2B", 5:"3B", 6:"SS", 7:"LF", 8:"CF", 9:"RF"}

        #Empty string
        self.empty = '       '

        #Scorecard information for hitters (0: Away, 1: Home)
        self.hitters = {0: {"%s" % (self.lineup[0][i].name): [self.pos_keys[lineups[0][i]]] + [self.empty for j in range(9)] for i in range(9)},
                        1: {"%s" % (self.lineup[1][i].name): [self.pos_keys[lineups[1][i]]] + [self.empty for j in range(9)] for i in range(9)}}
        
        #Dictionary connecting plays to corresponding functions
        self.plays = {"K": self.K, "BB": self.BB, "HBP": self.BB, 
                              "HR": self.HR, "S": self.S, "D": self.D, "T": self.T,
                              "FB": self.FB, "GB": self.GB, 'lomax': self.lomax, "LO": self.LO, "PO": self.PO, "FO": self.FO, 
                              "E": self.E}
    
    def display(self, away = True, home = True):
        """Displays score card.

        Args:
            away (bool, optional, default True): Whether or not to show away team.
            home (bool, optional, default True): Whether or not to show home team.
        """

        if away:
            #Display away hitters
            print('Away:')
            print(tabulate(pd.DataFrame(data = self.hitters[0].values(),columns = ['Pos'] + list(range(1,10)),index = self.hitters[0].keys()), 
                                    headers = 'keys', tablefmt = 'fancy_grid'))
        
        if home:
            #Display home hitters
            print('Home:')
            print(tabulate(pd.DataFrame(data = self.hitters[1].values(),columns = ['Pos'] + list(range(1,10)),index = self.hitters[1].keys()), 
                                    headers = 'keys', tablefmt = 'fancy_grid'))
    
    def result(self,batter,inning,batting_team,outcome):
        """Function for updating scorecard with general result

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
            outcome (str): String describing outcome of given plate appearance.
        """

        #If first PA of inning, set corresponding element to outcome
        if self.hitters[batting_team][batter][inning] == self.empty:
            self.hitters[batting_team][batter][inning] = outcome

        #If second PA of inning, set corresponding element to list of len 2 with both outcomes
        elif self.hitters[batting_team][batter][inning] is str:
            self.hitters[batting_team,batter][inning] = [self.hitters[batting_team,batter][inning], outcome]
        
        #If third or higher PA of inning, append outcome to list.
        else:
            self.hitters[batting_team,batter][inning] += [outcome]
    
    def K(self, batter, inning, batting_team):
        """Function for updating score card after strikeout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, '    K  ')

    def BB(self, batter, inning, batting_team):
        """Function for updating score card after walk.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, '   BB  ')

    def S(self, batter, inning, batting_team):
        """Function for updating score card after strikeout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, u'    \u2014  ')#Single dash

    def D(self, batter, inning, batting_team):
        """Function for updating score card after strikeout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, u'    \u2550  ')#Double dash

    def T(self, batter, inning, batting_team):
        """Function for updating score card after strikeout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, u'    \u2261  ')#Triple dash

    def HR(self, batter, inning, batting_team):
        """Function for updating score card after strikeout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, u'   HR  ')

    def FB(self, batter, inning, batting_team, pos, typ):
        """Function for updating score card after flyball.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
            pos (int): position flyball was hit to
            typ (str): Flyball modifier (dp for double play, sac for sac fly)
        """

        if typ == 'sac':
            self.result(batter,inning,batting_team, u'  SF%d ' % pos)
        elif typ == 'dp':
            self.result(batter,inning,batting_team, u'  %d-2 ' % pos)
        else:
            self.result(batter,inning,batting_team, u'    %d ' % pos)

    def GB(self, batter, inning, batting_team, pos, typ):
        """Function for updating score card after groundball.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
            pos (int): position groundball was hit to
            typ (str): groundball modifier (dp for double play, fc for fielders choice)
        """
        if typ == 'dp':
            if pos in [1,2,3,4]: #If GB hit to pitcher, catcher, 1b, 2b: shortstop takes second
                self.result(batter,inning,batting_team, u' %d-6-3 ' % pos)
            else: #Otherwise: 2B takes second
                self.result(batter,inning,batting_team, u' %d-4-3 ' % pos)
        elif typ == 'fc':
            if pos in [1,2,3,4]: #If GB hit to pitcher, catcher, 1b, 2b: shortstop takes second
                self.result(batter,inning,batting_team, u'   %d-6 ' % pos)
            else: #Otherwise: 2B takes second
                self.result(batter,inning,batting_team, u'   %d-4 ' % pos) 
        else:
            self.result(batter,inning,batting_team, u'   %d-3 ' % pos) 
    
    def lomax(self, batter, inning, batting_team, pos, bases):
        """Function for updating score card after lineout into as many outs as possible.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
            pos (int): position lineout was hit to
            bases (int): bases where additional outs were made.
        """

        #Base outcome includes position lineout was hit to
        outcome = ' %d' % pos

        #Throw ball around to bases as necessary
        if 2 in bases:
            outcome += '-5'
        if 1 in bases:
            if pos in [3,4]:
                outcome += '-6'
            else:
                outcome += '-4'
        if 0 in bases:
            outcome += '-3'
        
        #Make sure outcome is length 7
        outcome += ' '
        outcome = ' '*(7-len(outcome)) + outcome
        self.result(batter,inning,batting_team, outcome)

    def LO(self, batter, inning, batting_team,pos):
        """Function for updating score card after lineout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, '   LO%d ' % pos)

    def PO(self, batter, inning, batting_team,pos):
        """Function for updating score card after popout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, '   PO%d ' % pos)

    def FO(self, batter, inning, batting_team,pos):
        """Function for updating score card after foulout.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
        """
        self.result(batter,inning,batting_team, '   FO%d ' % pos)

    def E(self, batter,inning, batting_team, pos, N):
        """Function for updating score card after error.

        Args:
            batter (str): Current batter
            inning (int): Current inning
            batting_team (int): Current batting team. 0 for away, 1 for home.
            pos (int): position error was hit to
            N (int): number of bases given up by error
        """
        self.result(batter,inning,batting_team, ' E%d(%d) ' % (pos,N))

class scoreboard():
    """Class for the scoreboard of a game. 
    
    Attributes:
        teams (list of str, default ['Away', 'Home']): List of length two containing participating teams.
        score (dict of lists): Dict containing scores in each inning + runs, hits, errors for each team.
        plays (dict): A dictionary connecting play strings to their corresponding functions.
    """
    def __init__(self,teams = None):
        """Initialization function for scoreboard.

        Args:
            teams (list of str, default ['Away', 'Home']): List of length two containing participating teams.
        """

        #Set teams
        self.teams = teams if teams is not None else ['Away','Home']

        #Initializae scoreboard
        self.score = {0: {i: '' for i in range(1,10)},
                      1: {i: '' for i in range(1,10)}}
        
        self.score[0]['R'] = 0
        self.score[1]['R'] = 0
        self.score[0]['H'] = 0
        self.score[1]['H'] = 0
        self.score[0]['E'] = 0
        self.score[1]['E'] = 0
        
        #Set plays
        self.plays = {"GB": self.N, "FB": self.N, "PO": self.N, "FO": self.N, "lomax": self.N, "LO": self.N, "BB": self.N, "K": self.N,
                   "S": self.H, "D": self.H, "T": self.H, "HR": self.H, "E": self.E}
        
    def display(self):
        """Function for displaying scoreboard.
        """

        df = pd.DataFrame(index = self.teams, data = [self.score[0].values(),self.score[1].values()], columns = self.score[0].keys())
        print(tabulate(df, headers = 'keys', tablefmt = 'fancy_grid'))
        
    def runs(self,r,inning, batting_team):
        """Function for updating scoreboard on run scoring.

        Args:
            r (list of str): runners who scored 
            inning (int): current inning
            batting_team (int): batting team. 0 for away, 1 for home
        """
        #Add score to inning and to total runs scored.
        self.score[batting_team][inning] += len(r)
        self.score[batting_team]['R'] += len(r)

    def inning_start(self, inning, batting_team):
        """Function for beginning new inning.

        Args:
            inning (int): current inning
            batting_team (int): batting team. 0 for away, 1 for home
        """
        #Set runs scored in inning to 0
        self.score[batting_team][inning] = 0
    
    def N(self, inning, batting_team): 
        """Function for updating scoreboard when nothing happens.

        Args:
            inning (int): current inning
            batting_team (int): batting team. 0 for away, 1 for home
        """
        pass
    
    def H(self, inning, batting_team):
        """Function for updating scoreboard on a hit.

        Args:
            inning (int): current inning
            batting_team (int): batting team. 0 for away, 1 for home
        """

        #Increase H column by 1
        self.score[batting_team]['H'] += 1
        
    def E(self, inning, batting_team): 
        """Function for updating scoreboard on an error.

        Args:
            inning (int): current inning
            batting_team (int): batting team. 0 for away, 1 for home
        """

        #Increase E column by 1
        self.score[1-batting_team]['E'] += 1

class game():
    """Class for containing everything about a game (game state, box score, scorecard, scoreboard)

    Attributes:
        GS (game_state): current game_state
        BS (box_score): current box_score
        SC (scorecard): current scorecard
        SB (scoreboard): current scoreboard
        result (int or None, default None): result of game (0 for away win, 1 for home win). None represents unfinished
    """
    def __init__(self,teams = None,positions = None,lineups = None):
        """Initialization function for game class.

        Args:
            teams (list of str, default ['Away', 'Home']): Name of teams competing.
            positions (list of player): A list of shape (2,10) indicating the players at each position for each team. The first list of 10 is for the away team, and the second list of 10 is for the home team. Within each list of 10, the index i indicates the player at position i (0 for DH). Provided list may include batter/pitcher classes or str of player names.
            lineups (list of int): List of batter of shape (2,9) giving lineups for each team. May be either a (2,9) list of batter, or a (2,9) list of int describing the position played by each lineup spot.
        """

        #Initialize game state, box score, and scorecard with corresponding positions and lineups
        self.GS = game_state(positions = positions, lineups = lineups)
        self.BS = box_score(positions=positions,lineups = lineups)
        self.SC = scorecard(positions=positions, lineups = lineups)

        #Initialize scoreboard with teams, start first inning
        self.SB = scoreboard(teams)
        self.SB.inning_start(self.GS.inning,self.GS.batting_team)

        #Initialize result to None
        self.result = None
        
    def PA(self):
        """Function for executing a plate appearance and updating game state, box score, scoreboard and scorecard.
        """

        #Display game state
        self.GS.display()

        #Get current pitcher and batter
        B = self.GS.batter
        P = self.GS.pitcher
        
        #Ask for roll
        input("Roll?")

        #Roll dice
        roll = diceroll_6()
        print(roll)

        #Get result of roll
        if roll[0] < 4:
            result = B.batting[P.hand][roll[0]][roll[1]-2]
        else:
            if B.hand == 'S':
                result = P.pitching['L' if P.hand == 'R' else 'R'][roll[0]][roll[1]-2]
            else:
                result = P.pitching[B.hand][roll[0]][roll[1]-2]

        #Try to split result by _
        try:
            result = re.split('[_]', result)

        except TypeError: #If element is a list, need to roll D20
            print(result)

            #Roll dice
            roll2 = diceroll_20()
            print(roll2)

            #Take result given by diceroll
            if roll2 <= result[0]:
                result = re.split('[_]', result[1])
            else:
                result = re.split('[_]', result[2])

        #If result ends in ~ and pitcher is tired. Convert result to S**
        if result[-1] == '~':
            if P.tired: 
                result = ['S','**']
            else:
                result = result[:-1]

        #Convert all numbers in result to ints
        for i in range(len(result)):
            try:
                result[i] = int(result[i])
            except (IndexError,TypeError, ValueError): pass

        #If result is X, execute GS.X function to determine result
        if result[0] == 'X':
            print(result)
            result = self.GS.plays[result[0]](*result[1:])

        #If result is PB or WP, execute GS function and 
        if result[0] in ['PB', 'WP']:
            print(result[0])
            runs_0 = self.GS.plays[result[0]]()[0]
            result = result[1:]
            if len(runs_0) > 0:
                self.BS.batter_runs(self.GS.batting_team,B.name,runs_0,False)
                self.BS.pitcher_runs(self.GS.batting_team,P.name,runs_0)
                self.SB.runs(runs,self.GS.inning, self.GS.batting_team)

        #If result is HRN, change to S** if batter power weak
        if result[0] == 'HRN':
            if B.batting[P.hand]['pow'] == "N":
                result = ['HR']
            else:
                result = ['S', '**']
        
        #If + in result and infield in, change to S**
        try:
            if '+' in result[-1] and self.GS.IF_pos == 2:
                result = ['S', '**']
        except:
            pass

        #Exceute play
        print(result)
        runs, RBI, BS_arg, SC_arg = self.GS.plays[result[0]](*result[1:])

        #Update box score and scoreboard with runs scored
        print(runs, RBI, BS_arg, SC_arg)
        self.BS.batter_runs(self.GS.batting_team,B.name,runs,RBI)
        self.BS.pitcher_runs(self.GS.batting_team,P.name,runs)
        self.SB.runs(runs,self.GS.inning, self.GS.batting_team)
    
        #Update box score, and scoreboard and scorecard with play
        self.BS.plays[result[0]](self.GS.batting_team,B.name,P.name,*BS_arg)
        self.SB.plays[result[0]](self.GS.inning,self.GS.batting_team)
        self.SC.plays[result[0]](B.name, self.GS.inning, self.GS.batting_team,*SC_arg)

        #Update lineup position
        self.GS.lineup_pos[self.GS.batting_team] = (self.GS.lineup_pos[self.GS.batting_team] + 1) % 9

        #If there are 3 outs
        if self.GS.outs == 3:

            #If the inning is 9 or more, check if a team has won
            if self.GS.inning >= 9:

                #If the away team was up, and home team winning, home team wins
                if self.GS.batting_team == 0 and self.GS.score[1] > self.GS.score[0]:
                    print('Home team wins!')
                    self.result = 1

                #If the home team was up, and away team winning, away team wins
                elif self.GS.batting_team == 1 and self.GS.score[0] > self.GS.score[1]:
                    print('Away team wins!')
                    self.result = 0

            if self.result is None: #If game proceeds

                #Set outs to 0
                self.GS.outs = 0

                #Increase inning if home team was up
                self.GS.inning += self.GS.batting_team

                #Change batting team
                self.GS.batting_team = 1-self.GS.batting_team

                #Empty bases
                self.GS.runners = [None,None,None]

                #Start inning
                self.SB.inning_start(self.GS.inning,self.GS.batting_team)

        #If home team batting, and inning >= 9, check for walk-off win
        elif self.GS.inning >= 9 and self.GS.batting_team == 1 and self.GS.score[1] > self.GS.score[0]:
            if self.GS.batting_team == 1 and self.GS.score[1] > self.GS.score[0]:
                print('Walk Off Win!')
                self.result = 1

        #Update pitcher and batter
        self.GS.update_pitcher_batter()
    
    def game(self):
        """Function for executing entire game.
        """

        #Execute PA until game is over.
        while self.result is None:
            self.PA()