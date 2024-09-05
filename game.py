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
    
     
    def __init__(self, bat_team=0, runners=None, score=None, outs=0, inning = None,
                 positions=None, lineups=None, lineup_pos=None, IF_pos = None, hold = None):
        self.batting_team = bat_team #0 for away, 1 for home
        self.runners = runners if runners is not None else [None, None, None] #Baserunners
        self.score = score if score is not None else [0, 0] #Score
        self.outs = outs #outs
        self.inning = inning if inning is not None else 1 #Inning
        self.positions = positions if positions is not None else [[None, None, None, None, None, None, None, None, None, None], 
                                                                  [None, None, None, None, None, None, None, None, None, None]] #Positions (0 is DH)
        
        for i in range(10):
            for j in [0,1]:
                if type(self.positions[j][i]) is str:
                    try: self.positions[j][i] = batter(self.positions[j][i])
                    except ValueError: self.positions[j][i] = pitcher(self.positions[j][i])
                        
        self.lineup = [[self.positions[0][i] for i in lineups[0]], 
                       [self.positions[1][i] for i in lineups[1]]] if lineups is not None else [[self.positions[0][i] for i in [0,2,3,4,5,6,7,8,9]], 
                                                                                                [self.positions[1][i] for i in [0,2,3,4,5,6,7,8,9]]] #Lineup, given by position
        
        self.lineup_pos = lineup_pos if lineup_pos is not None else [0, 0] #Current batter position in each lineup
        self.pitcher = self.positions[1 - self.batting_team][1] #Current pitcher
        self.batter = self.lineup[self.batting_team][self.lineup_pos[self.batting_team]] #Current batter
        self.IF_pos = IF_pos if IF_pos is not None else 0 #Infield position (0 for normal, 1 for corners in, 2 for infield in)
        self.hold = hold if hold is not None else [False if i is not None else None for i in self.runners]
        
        self.plays = {"K": self.K, "BB": self.BB, "HBP": self.BB, 
                              "HR": self.HR, "S": self.S, "D": self.D, "T": self.T,
                              "FB": self.FB, "GB": self.GB, 'lomax': self.lomax, "LO": self.LO, "PO": self.PO, "FO": self.FO, 
                              "X": self.X,"E": self.E, "WP": self.WP, "PB": self.PB}

    def update_pitcher_batter(self):
        
        self.pitcher = self.positions[1-self.batting_team][1]
        self.batter = self.lineup[self.batting_team][self.lineup_pos[self.batting_team]]
    
    def display(self):
        bbox_fielder = {'boxstyle': 'round','alpha': 0.8, 'pad' : 0.2, 'ec' : 'k', 'fc' : 'w'}
        bbox_runner = {'boxstyle': 'round','alpha': 0.8, 'pad' : 0.2, 'ec' : 'r', 'fc' : 'w'}
        fig = plt.figure(figsize = [8,8])
        ax = fig.add_subplot()

        ax.set_title("%d-%d" % (self.score[0],self.score[1]), fontsize = 14)
        ax.text(0.02,0.98, "%s%d\n%d Outs" % ("T" if self.batting_team == 0 else "B", self.inning,self.outs), ha = 'left', va = 'top', transform = ax.transAxes, fontsize = 14)

        img = np.asarray(Image.open('diamonddiagram.jpg'))
        ax.imshow(img, origin = 'lower')
        x_home = np.linspace(270,302,100)
        def corner(x, center, upper = False):
            xl = x[0]
            xm = x[-1]
            if upper:
                return [i - xl + center[1] if i <= center[0] else -i + xm + center[1] for i in x]
            else:
                return [-i + xl + center[1] if i <= center[0] else i - xm + center[1] for i in x]
        y_home1 = corner(x_home, [286,28])
        y_home2 = 45

        x_1b = np.linspace(411,447)
        y_1b1 = corner(x_1b,[429.5,174])
        y_1b2 = corner(x_1b,[429.5,174], upper = True)

        x_3b = np.linspace(125,160)
        y_3b1 = corner(x_3b,[142.5,174])
        y_3b2 = corner(x_3b,[142.5,174], upper = True)

        x_2b = np.linspace(267.5,303.5,100)
        y_2b1 = corner(x_2b,[285.5,320])
        y_2b2 = corner(x_2b,[285.5,320], upper = True)

        ax.fill_between(x_home,y_home1,y_home2,ec = 'k',fc = 'w')
        
        if self.runners[0] is not None:
            ax.fill_between(x_1b,y_1b1,y_1b2, ec = 'k', fc = 'k')
            ax.text(0.8,0.33,self.runners[0].name,ha = 'center',va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        else:
            ax.fill_between(x_1b,y_1b1,y_1b2, ec = 'k', fc = 'w')

        if self.runners[1] is not None:
            ax.fill_between(x_2b,y_2b1,y_2b2, ec = 'k', fc = 'k')
            ax.text(0.5,0.65,self.runners[1].name,ha = 'center',va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        else:
            ax.fill_between(x_2b,y_2b1,y_2b2, ec = 'k', fc = 'w')

        if self.runners[2] is not None:
            ax.fill_between(x_3b,y_3b1,y_3b2, ec = 'k', fc = 'k')
            ax.text(0.2,0.33,self.runners[2].name,ha = 'center',va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        else:
            ax.fill_between(x_3b,y_3b1,y_3b2, ec = 'k', fc = 'w')
        ax.set_ylim(-10,509)
        ax.set_xlim(0,570)

        ax.text(0.5,0.38,self.positions[1-self.batting_team][1].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.5,0.03,self.positions[1-self.batting_team][2].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.75,0.42,self.positions[1-self.batting_team][3].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.65,0.55,self.positions[1-self.batting_team][4].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.35,0.55,self.positions[1-self.batting_team][6].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.25,0.42,self.positions[1-self.batting_team][5].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.2,0.68,self.positions[1-self.batting_team][7].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.5,0.85,self.positions[1-self.batting_team][8].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        ax.text(0.8,0.68,self.positions[1-self.batting_team][9].name,ha = 'center', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_fielder)
        if self.batter.hand == 'R' or (self.batter.hand == 'S' and self.pitcher.hand == 'L'):
            ax.text(0.47,0.1,self.batter.name, ha = 'right', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        else:
            ax.text(0.53,0.1,self.batter.name, ha = 'left', va = 'center', fontsize = 10,transform = ax.transAxes, bbox = bbox_runner)
        plt.show()
    
    def S(self, typ):
        "Function for updating game state for all variety of singles."
        if typ == '*': #Single, 1 base advance
            runs = [i.name for i in self.runners[2:] if i is not None]
            self.score[self.batting_team] += len(runs) #Increase score if runner on third
            
            #Move all runners up 1
            self.runners[2] = self.runners[1]
            self.runners[1] = self.runners[0]
            self.runners[0] = self.batter
            
        elif typ == '**': #Single, 2 base advance
            runs = [i.name for i in self.runners[1:] if i is not None]
            #Increase score by number of batters on second and third
            self.score[self.batting_team] += len(runs) #Increase score by number of runners on number of runners on second and third        
            
            #Move runners up 2
            self.runners[2] = self.runners[0]
            self.runners[1] = None
            self.runners[0] = self.batter
            
        else: #Single, to specific positions

            #If runner on second, he may choose to score
            if self.runners[1] is not None:
                
                #Parameters for determing safe/out chance
                speed = self.runners[1].run
                arm = self.positions[1-self.batting_team][typ].field[typ][2]
                outs2 = self.outs == 2

                #Chance of bering safe
                chance = min([20,max([1,speed + arm + 2*outs2])])
                #Run runner_advancement for runner on second, to fielder single was hit to
                res = runner_advancement(chance)
                
                if res == 0: #If out, remove runner from second then execute single, 2 base advance
                    self.outs += 1
                    self.runners[1] = None
                    runs = self.S('**')[0]
                elif res == 2: #If safe, single, 2 base advance
                    runs = self.S('**')[0]
                else: #If held, single, 1-base advance
                    runs = self.S('*')[0]

            #If no runner on second, and runner on first, he may choose to go to third
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
                
                if res == 0:#If out, remove runner from second then execute single, 2 base advance
                    self.outs += 1
                    self.runners[0] = None
                    self.S('**')
                elif res == 2:#If safe, single, 2 base advance
                    runs = self.S('**')[0]
                else:#If held, single, 1-base advance
                    runs = self.S('*')[0]

            else: #If no runners on first or second, single, 1 base advance
                runs = self.S('*')[0]
        return runs, True, [], []

    def D(self, typ):
        """Function for updating game state for all variety of singles."""
        
        if typ == '**': #2-base double
            runs = [i.name for i in self.runners[1:] if i is not None]

            #Increase score by number of runners on second and third
            self.score[self.batting_team] += len(runs) #Increase score by number of runners on number of runners on second and third
            
            #Move runners up 2
            self.runners[2] = self.runners[0]
            self.runners[1] = self.batter
            self.runners[0] = None
            
        elif typ == '***':
            runs = [i.name for i in self.runners if i is not None]
            #Increase score by number of runners on second and third
            self.score[self.batting_team] += len(runs) #Increase score by number of runners on number of runners on bases
            
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
                #Run runner_advancement for runner on second, to fielder single was hit to
                res = runner_advancement(chance)
                
                if res == 0:
                    self.outs += 1
                    self.runners[2] = None
                    runs = self.D('**')[0]
                    
                if res == 2:
                    runs = self.D('***')[0]
            else:
                runs = self.D('**')[0]
        return runs, True, [], []

    def T(self):
        """Function for updating game state for a triple"""
        runs = [i.name for i in self.runners if i is not None]
        self.score[self.batting_team] += len(runs)
        self.runners[2] = self.batter
        self.runners[1] = None
        self.runners[0] = None

        return runs, True, [], []

    # def HRN(self):
    #     """Function for updating game state for a homerun-N"""
        
    #     #Homerun if batter power is N, else single, 2-base advance
    #     if self.batter.batting[self.pitcher.hand]['pow'] == "N":
    #         runs = self.HR(self)[0]
    #         return runs, True, True
    #     else:
    #         runs = self.S(self, '**')[0]
    #         return runs, False, True

    
    def HR(self):
        """Function for updating game state for a homerun"""
        runs = [self.batter.name] + [i.name for i in self.runners if i is not None]
        #Score all runners and batter, remove all runners
        self.score[self.batting_team] += len(runs)
        self.runners = [None,None,None]
        
        return runs, True, [], []
    
    def FB(self,pos,typ):
        """Function for updating game state for a flyball of all types"""
        self.outs += 1 #Increase outs by 1
        runs = []
        typ2 = ''
        if self.outs < 3: #If inning continues
                
            if 'A' in typ: #All runners advance
                runs = [self.runners[2].name] if self.runners[2] is not None else []
                self.score[self.batting_team] += len(runs) #Score runner on third
                typ2 = 'sac' if bool(len(runs)) else ''

                #Move runners up 1
                self.runners[2] = self.runners[1]
                self.runners[1] = self.runners[0]
                self.runners[0] = None
                
            elif 'B' in typ: #Runner on third advances
                if "?" in typ: #For questionable fly ball
                    if self.runners[2] is not None: #Runner on third may advance
                        speed = self.runners[2].run #Run speed
                        arm = self.positions[1-self.batting_team][pos].field[pos][2] #Fielder arm
                        
                        chance = min([20,max([1,speed + arm + 2])]) #Chance of success
                        res = runner_advancement(chance) #Calculate results
                        if res == 0: #Runner out
                            self.outs += 1
                            self.runners[2] = None
                            typ2 = 'dp'
                        elif res == 2: #Runner scores
                            self.score[self.batting_team] += 1
                            runs = [self.runners[2].name]
                            self.runners[2] = None
                            typ2 = 'sac'
                        

                else: #Deep fly ball
                    #Runner on third scores
                    runs = [self.runners[2].name] if self.runners[2] is not None else []
                    self.score[self.batting_team] += len(runs)
                    typ2 = 'sac' if bool(len(runs)) else ''
                    self.runners[2] = None
                    
                    #Runner on second may advance if FB to right
                    if self.runners[1] is not None and pos == 9:
                        speed = self.runners[1].run #speed
                        arm = self.positions[1-self.batting_team][pos].field[pos][2] #fielder arm
                        
                        chance = min([20,max([1,speed + arm + 2])]) #Success chance
                        if input('Would you like to send the runner? (%d) ' % chance) == "Y":
            
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
        """Function for updating game state on groundballs of all types"""
        
        # #If + in type and infield in, change to single, 2 base advance
        # if '+' in typ and self.IF_pos == 2:
        #     runs = self.S(self,'**')[0]
        #     return runs, True
        
        #Increase outs by 1
        self.outs += 1
        runs = []
        if self.outs < 3: #If inning continues
            if 'A' in typ: #Double play
                if self.runners[0] is not None: #Double play
                    self.outs += 1 #Increase outs by 1
                    if self.outs < 3:#If inning continues
                        runs = [self.runners[2].name] if self.runners[2] is not None else []
                        self.score[self.batting_team] += len(runs)
                        self.runners[2] = self.runners[1]
                        self.runners[1] = None
                        self.runners[0] = None
                    return runs, False, ['dp'], [pos,'dp']
                return runs, False, [''], [pos, '']
            
            elif 'B' in typ: #Force play
                if self.runners[0] is not None:
                    runs = [self.runners[2].name] if self.runners[2] is not None else []
                    self.score[self.batting_team] += len(runs)
                    self.runners[2] = self.runners[1]
                    self.runners[1] = None
                    self.runners[0] = self.batter
                    return runs, True, ['fc'], [pos,'fc'] 
                return runs, True, [''], [pos, '']
            
            elif 'C' in typ: #Runners advance
                runs = [self.runners[2].name] if self.runners[2] is not None else []
                self.score[self.batting_team] += len(runs)
                self.runners[2] = self.runners[1]
                self.runners[1] = self.runners[0]
                self.runners[0] = None
                return runs, True, [''], [pos, '']
        return runs, True, [''], [pos, '']

    def LO(self,pos):
        """Function for updating game state on lineout"""
        self.outs += 1
        return [], True, [], [pos]
    def PO(self, pos):
        """Function for updating game state on popout"""
        self.outs += 1
        return [], True, [], [pos]
        
    def FO(self, pos):
        """Function for updating game state on popout"""
        self.outs += 1
        return [], True, [], [pos]
                    
    def lomax(self,pos):
        """Function for updating game state on lineout into as many outs as possible"""
        self.outs += 1
        bases = []
        if self.outs < 3:
            if self.runners[2] is not None: 
                self.outs += 1
                bases.append(2)
                self.runners[2] = None
            if self.outs < 3:
                if self.runners[1] is not None: 
                    self.outs += 1
                    bases.append(1)
                    self.runners[1] = None
                if self.outs < 3:
                    if self.runners[0] is not None: 
                        self.outs += 1
                        bases.append(0)
                        self.runners[0] = None

        return [], True, [1 + len(bases)], [pos,bases]

    def K(self):
        """Function for updating game state on strikeout"""
        self.outs += 1
        return [], True, [], []

    def BB(self):
        """Function for updating game state on walk"""
        runs = [self.runners[2].name] if self.runners[2] is not None else []
        self.score[self.batting_team] += len(runs)
        self.runners[2] = self.runners[1] if (self.runners[1] is not None) and (self.runners[0] is not None) else self.runners[2]
        self.runners[1] = self.runners[0] if self.runners[0] is not None else self.runners[1]
        self.runners[0] = self.batter
        return runs, True, [], []
        
    def WP(self):
        """Function for updating game state on wild pitch"""
        runs = [self.runners[2].name] if self.runners[2] is not None else []
        self.score[self.batting_team] += len(runs)
        self.score[self.batting_team] += self.runners[2] is not None
        self.runners = [None, self.runners[0],self.runners[1]]
        return runs, False

    def PB(self):
        """Function for updating game state on passed ball"""
        runs = [self.runners[2].name] if self.runners[2] is not None else []
        self.score[self.batting_team] += len(runs)
        self.score[self.batting_team] += self.runners[2] is not None
        self.runners = [None, self.runners[0],self.runners[1]]
        return runs, False
        
    def X(self,pos):
        """Function for updating game state on fielder play"""
        
        #Determine player ball was hit to
        player = self.positions[1-self.batting_team][pos]
        print(player.name)
        #Determine player rating
        rating = player.field[pos][0]
        print(rating)
        #Determine Roll
        roll = diceroll_20()
        print(roll)
        
        #Get result
        result = fieldingchart[pos][rating][roll-1]
        if result == 'E': #If result is E, more rolls necessary
            E_n = player.field[pos][1]
            print(E_n)
            roll2 = diceroll_6()
            print(roll2)
            result = fieldingchart[pos]['E'][E_n][roll2[1]-2]
            if type(result) is list:
                result = result[1] if roll2 <= result[0] else result[2]
        
        #Execute result
        result = re.split('[_]', result)
        for i in range(len(result)):
            try:
                result[i] = int(result[i])
            except (TypeError,IndexError, ValueError): pass
    #     print(result)
        
        # if pos == 2:
        #     if result[0] in ['WP', 'PB']:
        #         runs_0 = self.plays[result[0]](self)
        #         result = result[1:]

        # runs_1 = self.plays[result[0]](self, *result[1:])[0]
        # return result, [runs_0,runs_1]
        return result

    def E(self, base, pos):
        "Function for updating game state on error"
        if base == 3:
            runs = self.T()[0]
        elif base == 2:
            runs = self.D('**')[0]
        else:
            runs = self.S('*')[0]

        return runs,False, [], [pos, base]
        

class box_score():
    def __init__(self, positions, lineups):
        self.positions = positions if positions is not None else [[None, None, None, None, None, None, None, None, None, None], 
                                                                  [None, None, None, None, None, None, None, None, None, None]] #Positions (0 is DH)
        
        for i in range(10):
            for j in [0,1]:
                if type(self.positions[j][i]) is str:
                    try: self.positions[j][i] = batter(self.positions[j][i])
                    except ValueError: self.positions[j][i] = pitcher(self.positions[j][i])
                        
        self.lineup = [[self.positions[0][i] for i in lineups[0]], 
                       [self.positions[1][i] for i in lineups[1]]] if lineups is not None else [[self.positions[0][i] for i in [0,2,3,4,5,6,7,8,9]], 
                                                                                              [self.positions[1][i] for i in [0,2,3,4,5,6,7,8,9]]] #Lineup, given by position
        
        self.pos_keys = {0: "DH", 1:"P", 2:"C", 3:"1B", 4:"2B", 5:"3B", 6:"SS", 7:"LF", 8:"CF", 9:"RF"}
        self.hitters = {0: {'%s'%(positions[0][i].name) : [self.pos_keys[i],0,0,0,0,0,0,0] for i in lineups[0]},
                        1: {'%s'%(positions[1][i].name) : [self.pos_keys[i],0,0,0,0,0,0,0] for i in lineups[1]}}
        self.pitchers = {0: {'%s'%(positions[0][1].name): [0.,0,0,0,0,0]},
                         1: {'%s'%(positions[1][1].name): [0.,0,0,0,0,0]}}
        
        self.plays = {"K": self.K, "BB": self.BB, "HBP": self.BB, 
                              "HR": self.HR, "S": self.S, "D": self.D, "T": self.T,
                              "FB": self.FB, "GB": self.GB, 'lomax': self.lomax, "LO": self.LO, "PO": self.PO, "FO": self.FO, 
                              "E": self.E}
    def display(self):
        print('Away:')
        
        print(tabulate(pd.DataFrame(data = self.hitters[0].values(),columns = ['Pos','AB','R','H','RBI','HR','BB','K'],index = self.hitters[0].keys()),
                                        headers = 'keys', tablefmt = 'fancy_grid'))
        print(tabulate(pd.DataFrame(data = self.pitchers[0].values(), columns = ['IP', 'H', 'R', 'BB', 'K', 'HR'], index = self.pitchers[0].keys()),
                                        headers = 'keys', tablefmt = 'fancy_grid'))

        print('Home:')
        print(tabulate(pd.DataFrame(data = self.hitters[1].values(),columns = ['Pos','AB','R','H','RBI','HR','BB','K'],index = self.hitters[1].keys()),
                                        headers = 'keys', tablefmt = 'fancy_grid'))
        print(tabulate(pd.DataFrame(data = self.pitchers[1].values(), columns = ['IP', 'H', 'R', 'BB', 'K', 'HR'], index = self.pitchers[1].keys()),
                                        headers = 'keys', tablefmt = 'fancy_grid'))

    def batter_runs(self, batting_team, batter, runs, RBI):
        for i in runs:
            self.hitters[batting_team][i][2] += 1
        if RBI:
            self.hitters[batting_team][batter][4] += len(runs)

    def pitcher_runs(self, batting_team, pitcher, runs, earned = True):
        self.pitchers[1-batting_team][pitcher][2] += len(runs)

    def K(self, batting_team, batter, pitcher):
        self.hitters[batting_team][batter][1] += 1
        self.hitters[batting_team][batter][-1] += 1
        self.pitchers[1-batting_team][pitcher][-2] += 1
        self.pitchers[1-batting_team][pitcher][0] += 1/3
    
    def BB(self, batting_team, batter, pitcher):
        self.hitters[batting_team][batter][-2] += 1
        self.pitchers[1-batting_team][pitcher][3] += 1

    def HR(self, batting_team, batter, pitcher):
        self.hitters[batting_team][batter][1] += 1
        self.hitters[batting_team][batter][3] += 1
        self.hitters[batting_team][batter][5] += 1
        self.pitchers[1-batting_team][pitcher][1] += 1
        self.pitchers[1-batting_team][pitcher][-1] += 1
    
    def S(self, batting_team,batter,pitcher):
        self.hitters[batting_team][batter][1] += 1
        self.hitters[batting_team][batter][3] += 1
        self.pitchers[1-batting_team][pitcher][1] += 1
    
    def D(self, batting_team,batter,pitcher):
        self.S(batting_team,batter,pitcher)
    
    def T(self, batting_team,batter,pitcher):
        self.S(batting_team,batter,pitcher)
    
    def FB(self, batting_team,batter,pitcher, typ):
        if typ != 'sac':
            self.hitters[batting_team][batter][1] += 1
        self.pitchers[1-batting_team][pitcher][0] += (1 + (typ == 'dp'))/3

    def GB(self, batting_team,batter,pitcher, typ):
        self.hitters[batting_team][batter][1] += 1
        self.pitchers[1-batting_team][pitcher][0] += (1+(typ=='dp'))/3

    def lomax(self,batting_team, batter,pitcher,outs):
        self.hitters[batting_team][batter][1] += 1
        self.pitchers[1-batting_team][pitcher][0] += outs/3

    def LO(self,batting_team,batter,pitcher):
        self.hitters[batting_team][batter][1] += 1
        self.pitchers[1-batting_team][pitcher][0] += 1/3

    def FO(self,batting_team,batter,pitcher):
        self.LO(batting_team,batter,pitcher)

    def PO(self,batting_team,batter,pitcher):
        self.LO(batting_team,batter,pitcher)
    
    def E(self,batting_team,batter,pitcher):
        self.hitters[batting_team][batter][1] += 1
       
class scorecard():
    def __init__(self,positions,lineups):
        self.positions = positions if positions is not None else [[None, None, None, None, None, None, None, None, None, None], 
                                                                  [None, None, None, None, None, None, None, None, None, None]] #Positions (0 is DH)
        
        for i in range(10):
            for j in [0,1]:
                if type(self.positions[j][i]) is str:
                    try: self.positions[j][i] = batter(self.positions[j][i])
                    except ValueError: self.positions[j][i] = pitcher(self.positions[j][i])
                        
        self.lineup = [[self.positions[0][i] for i in lineups[0]], 
                       [self.positions[1][i] for i in lineups[1]]] if lineups is not None else [[self.positions[0][i] for i in [0,2,3,4,5,6,7,8,9]], 
                                                                                              [self.positions[1][i] for i in [0,2,3,4,5,6,7,8,9]]] #Lineup, given by position
        
        self.pos_keys = {0: "DH", 1:"P", 2:"C", 3:"1B", 4:"2B", 5:"3B", 6:"SS", 7:"LF", 8:"CF", 9:"RF"}
        self.empty = '       '
        self.hitters = {0: {"%s" % (self.lineup[0][i].name): [self.pos_keys[lineups[0][i]]] + [self.empty for j in range(9)] for i in range(9)},
                        1: {"%s" % (self.lineup[1][i].name): [self.pos_keys[lineups[1][i]]] + [self.empty for j in range(9)] for i in range(9)}}
        
        self.plays = {"K": self.K, "BB": self.BB, "HBP": self.BB, 
                              "HR": self.HR, "S": self.S, "D": self.D, "T": self.T,
                              "FB": self.FB, "GB": self.GB, 'lomax': self.lomax, "LO": self.LO, "PO": self.PO, "FO": self.FO, 
                              "E": self.E}
    
    def display(self):
        print('Away:')
        print(tabulate(pd.DataFrame(data = self.hitters[0].values(),columns = ['Pos'] + list(range(1,10)),index = self.hitters[0].keys()), 
                                   headers = 'keys', tablefmt = 'fancy_grid'))
        
        print('Home:')
        print(tabulate(pd.DataFrame(data = self.hitters[1].values(),columns = ['Pos'] + list(range(1,10)),index = self.hitters[1].keys()), 
                                   headers = 'keys', tablefmt = 'fancy_grid'))
    
    def K(self, batter, inning, batting_team):
        self.result(batter,inning,batting_team, '    K  ')

    def BB(self, batter, inning, batting_team):
        self.result(batter,inning,batting_team, '   BB  ')

    def S(self, batter, inning, batting_team):
        self.result(batter,inning,batting_team, u'    \u2014  ')

    def D(self, batter, inning, batting_team):
        self.result(batter,inning,batting_team, u'    \u2550  ')

    def T(self, batter, inning, batting_team):
        self.result(batter,inning,batting_team, u'    \u2261  ')

    def HR(self, batter, inning, batting_team):
        self.result(batter,inning,batting_team, u'   HR  ')

    def FB(self, batter, inning, batting_team, pos, typ):
        if typ == 'sac':
            self.result(batter,inning,batting_team, u'  SF%d ' % pos)
        elif typ == 'dp':
            self.result(batter,inning,batting_team, u'  %d-2 ' % pos)
        else:
            self.result(batter,inning,batting_team, u'    %d ' % pos)

    def GB(self, batter, inning, batting_team, pos, typ):
        if typ == 'dp':
            if pos in [1,2,3,4]:
                self.result(batter,inning,batting_team, u' %d-6-3 ' % pos)
            else:
                self.result(batter,inning,batting_team, u' %d-4-3 ' % pos)
        elif typ == 'fc':
            if pos in [1,2,3,4]:
                self.result(batter,inning,batting_team, u'   %d-6 ' % pos)
            else:
                self.result(batter,inning,batting_team, u'   %d-4 ' % pos) 
        else:
            self.result(batter,inning,batting_team, u'   %d-3 ' % pos) 
    
    def lomax(self, batter, inning, batting_team, pos, bases):
        outcome = ' %d' % pos
        if 2 in bases:
            outcome += '-5'
        if 1 in bases:
            if outcome[-1] in [3,4]:
                outcome += '-6'
            else:
                outcome += '-4'
        if 0 in bases:
            outcome += '-3'
        
        outcome += ' '
        outcome = ' '*(7-len(outcome)) + outcome
        self.result(batter,inning,batting_team, outcome)

    def LO(self, batter, inning, batting_team,pos):
        self.result(batter,inning,batting_team, '   LO%d ' % pos)

    def PO(self, batter, inning, batting_team,pos):
        self.result(batter,inning,batting_team, '   PO%d ' % pos)

    def FO(self, batter, inning, batting_team,pos):
        self.result(batter,inning,batting_team, '   FO%d ' % pos)

    def E(self, batter,inning, batting_team, pos, N):
        self.result(batter,inning,batting_team, ' E%d(%d) ' % (pos,N))

    def result(self,batter,inning,batting_team,outcome):
        if self.hitters[batting_team][batter][inning] == self.empty:
            self.hitters[batting_team][batter][inning] = outcome
        elif self.hitters[batting_team][batter][inning] is str:
            self.hitters[batting_team,batter][inning] = [self.hitters[batting_team,batter][inning], outcome]
        else:
            self.hitters[batting_team,batter][inning] += [outcome]
        

class scoreboard():
    def __init__(self,teams = None):
        self.teams = teams if teams is not None else ['Away','Home']
        self.score = {0: {i: '' for i in range(1,10)},
                      1: {i: '' for i in range(1,10)}}
        
        self.score[0]['R'] = 0
        self.score[1]['R'] = 0
        self.score[0]['H'] = 0
        self.score[1]['H'] = 0
        self.score[0]['E'] = 0
        self.score[1]['E'] = 0
        
        self.plays = {"GB": self.N, "FB": self.N, "PO": self.N, "FO": self.N, "lomax": self.N, "LO": self.N, "BB": self.N, "K": self.N,
                   "S": self.H, "D": self.H, "T": self.H, "HR": self.H, "E": self.E}
        
    def display(self):
        df = pd.DataFrame(index = self.teams, data = [self.score[0].values(),self.score[1].values()], columns = self.score[0].keys())
        print(tabulate(df, headers = 'keys', tablefmt = 'fancy_grid'))
        
    def runs(self,r,inning, batting_team):
        
        self.score[batting_team][inning] += len(r)
        self.score[batting_team]['R'] += len(r)

    def inning_start(self, inning, batting_team):
        self.score[batting_team][inning] = 0
    
    def N(self, inning, batting_team): pass
    
    def H(self, inning, batting_team): 
        self.score[batting_team]['H'] += 1
        
    def E(self, inning, batting_team): 
        self.score[1-batting_team]['E'] += 1

class game():
    def __init__(self,teams = None,positions = None,lineups = None):
        self.GS = game_state(positions = positions, lineups = lineups)
        self.BS = box_score(positions=positions,lineups = lineups)
        self.SC = scorecard(positions=positions, lineups = lineups)
        self.SB = scoreboard(teams)
        self.SB.inning_start(self.GS.inning,self.GS.batting_team)
        self.result = None
        
    def PA(self):
        self.GS.display()
        B = self.GS.batter
        P = self.GS.pitcher
        input("Roll?")
        roll = diceroll_6()
        print(roll)
        if roll[0] < 4:
            result = B.batting[P.hand][roll[0]][roll[1]-2]
        else:
            if B.hand == 'S':
                result = P.pitching['L' if P.hand == 'R' else 'R'][roll[0]][roll[1]-2]
            else:
                result = P.pitching[B.hand][roll[0]][roll[1]-2]

        
        try:
            result = re.split('[_]', result)
        except TypeError:
            print(result)
            roll2 = diceroll_20()
            print(roll2)
            if roll2 <= result[0]:
                result = re.split('[_]', result[1])
            else:
                result = re.split('[_]', result[2])
    #     print(result)
        if result[-1] == '~':
            if P.tired: 
                result = ['S','**']
            else:
                result = result[:-1]
    #     print(result)
        for i in range(len(result)):
            try:
                result[i] = int(result[i])
            except (IndexError,TypeError, ValueError): pass
    #     print(result)
        if result[0] == 'X':
            print(result)
            result = self.GS.plays[result[0]](*result[1:])

        if result[0] in ['PB', 'WP']:
            print(result[0])
            runs_0 = self.GS.plays[result[0]]()
            result = result[1:]
        
        print(result)
        if result[0] == 'HRN':
            if B.batting[P.hand]['pow'] == "N":
                result = ['HR']
            else:
                result = ['S', '**']
            print(result)
        
        try:
            if '+' in result[-1] and self.GS.IF_pos == 2:
                result = ['S', '**']
                print(result)
        except:
            pass

        runs, RBI, BS_arg, SC_arg = self.GS.plays[result[0]](*result[1:])

        print(runs, RBI, BS_arg, SC_arg)
        self.BS.batter_runs(self.GS.batting_team,B.name,runs,RBI)
        self.BS.pitcher_runs(self.GS.batting_team,P.name,runs)
        self.SB.runs(runs,self.GS.inning, self.GS.batting_team)
    
        self.BS.plays[result[0]](self.GS.batting_team,B.name,P.name,*BS_arg)
        self.SB.plays[result[0]](self.GS.inning,self.GS.batting_team)
        self.SC.plays[result[0]](B.name, self.GS.inning, self.GS.batting_team,*SC_arg)

        self.GS.lineup_pos[self.GS.batting_team] = (self.GS.lineup_pos[self.GS.batting_team] + 1) % 9

        if self.GS.inning >= 9 and self.GS.batting_team == 1 and self.GS.score[1] > self.GS.score[0]:
            if self.GS.batting_team == 1 and self.GS.score[1] > self.GS.score[0]:
                print('Walk Off Win!')
                self.result = 1
        if self.GS.outs == 3:
            if self.GS.inning >= 9:
                if self.GS.batting_team == 0 and self.GS.score[1] > self.GS.score[0]:
                    print('Home team wins!')
                    self.result = 1
                elif self.GS.batting_team == 1 and self.GS.score[0] > self.GS.score[1]:
                    print('Away team wins!')
                    self.result = 0
            if result is None:
                self.GS.outs = 0
                self.GS.inning += self.GS.batting_team
                self.GS.batting_team = 1-self.GS.batting_team
                self.GS.runners = [None,None,None]
                game.SB.inning_start(self.GS.inning,self.GS.batting_team)

        self.GS.update_pitcher_batter()
        return result
    
    def game(self):
        while self.result is None:
            self.PA()