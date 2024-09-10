import json
import matplotlib.pyplot as plt
import numpy as np
import re

def string_converter_1(string):
    """Converts play string to human readable equivalent.
    
    Args:
        string (str): String to be converted.
        
    Returns:
        str: Human readable string.
    """

    #Split outcome into consituents
    elements = re.split('[_]', string)

    #Initialize result
    result = ''

    #Dictionary for position keys
    pos_keys = {'0': "DH", '1':"P", '2':"C", '3':"1B", '4':"2B", "5":"3B", '6':"SS", '7':"LF", '8':"CF", '9':"RF"}

    if elements[0] == 'K': #Strikeout
        result += 'strikeout'
        kwargs = {} #kwargs control fontweight
    elif elements[0] == 'BB': #Walk
        result += 'WALK'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'HBP': #Hit by pitch
        result += 'HBP'
        kwargs = {'fontweight': 'bold'} 
    elif elements[0] == 'HR': #Homerun
        result += 'HOMERUN'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'HRN': #Normal homerun
        result += 'N-HOMERUN'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'S': #Single
        result += 'SINGLE'
        kwargs = {'fontweight': 'bold'}
        try: #For conditional advancement
            int(elements[1])
            result += '(%s)' % pos_keys[elements[1]]
        except ValueError: #For guaranteed advancement
            result += '%s' % elements[1]
    elif elements[0] == 'D': #Double
        result += 'DOUBLE'
        kwargs = {'fontweight': 'bold'}
        try: #For conditional advancement
            int(elements[1])
            result += '(%s)' % pos_keys[elements[1]]
        except ValueError: #For guaranteed advancement
            result += '%s' % elements[1]
    elif elements[0] == 'T': #Triple
        result += 'TRIPLE'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'FB': #Flyball
        result += 'fly (%s) %s' % (pos_keys[elements[1]].lower(), elements[2])
        kwargs = {}
    elif elements[0] == 'GB': #Groundball
        result += 'gb (%s) %s' % (pos_keys[elements[1]].lower(), elements[2])
        kwargs = {}
    elif elements[0] == 'lomax': #Lomax
        result += 'lomax (%s)' % pos_keys[elements[1]]
        kwargs = {}
    elif elements[0] == 'FO': #Foulout
        result += 'foulout (%s)' % pos_keys[elements[1]]
        kwargs = {}
    elif elements[0] == 'LO': #Lineout
        result += 'lineout (%s)' % pos_keys[elements[1]]
        kwargs = {}
    elif elements[0] == 'PO': #Popout
        result += 'popout (%s)' % pos_keys[elements[1]]
        kwargs = {}
    elif elements[0] == 'X': #Fielding Chart
        if elements[1] == '2': #Catcher
            result += "CATCH"
        elif elements[1] in ['1','3','4','5','6']: #Infielders
            result += 'GB (%s)' % pos_keys[elements[1]].lower()
        elif elements[1] in ['7','8','9']: #Outfielders
            result += 'FLY (%s)'  % pos_keys[elements[1]].lower()
        result += ' X'
        kwargs = {}
    
    if elements[-1] == '~': #If pitcher tired
        result += u' \u25CF'

    return result,kwargs

def string_converter_2(string):
    """Converts play string to human readable equivalent.
    
    Args:
        string (str): String to be converted.
        
    Returns:
        str: Human readable string.
    """

    #Split outcome into consituents
    elements = re.split('[_]', string)

    #Initialize result
    result = ''

    #Dictionary for position keys
    pos_keys = {'0': "DH", '1':"P", '2':"C", '3':"1B", '4':"2B", "5":"3B", '6':"SS", '7':"LF", '8':"CF", '9':"RF"}

    if elements[0] == 'HR': #Homerun
        result += 'HR'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'HRN': #Normal homerun
        result += 'N-HR'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'S': #Single
        result += 'SI'
        kwargs = {'fontweight': 'bold'}
        try: #For conditional advancement
            int(elements[1])
            result += '(%s)' % pos_keys[elements[1]]
        except ValueError: #For guaranteed advancement
            result += '%s' % elements[1]
    elif elements[0] == 'D': #Double
        result += 'DO'
        kwargs = {'fontweight': 'bold'}
        try: #For conditional advancement
            int(elements[1])
            result += '(%s)' % pos_keys[elements[1]]
        except ValueError: #For guaranteed advancement
            result += '%s' % elements[1]
    elif elements[0] == 'T': #Triple
        result += 'TR'
        kwargs = {'fontweight': 'bold'}
    elif elements[0] == 'FB': #Flyball
        result += 'fly (%s) %s' % (pos_keys[elements[1]].lower(), elements[2])
        kwargs = {}
    elif elements[0] == 'GB': #Groundball
        result += 'gb (%s) %s' % (pos_keys[elements[1]].lower(), elements[2])
        kwargs = {}
    elif elements[0] == 'FO': #Foulout
        result += 'fo (%s)' % pos_keys[elements[1]]
        kwargs = {}
    elif elements[0] == 'LO': #Lineout
        result += 'lo (%s)' % pos_keys[elements[1]]
        kwargs = {}
    elif elements[0] == 'PO': #Popout
        result += 'po (%s)' % pos_keys[elements[1]]
        kwargs = {}

    return result,kwargs

#Obtain data for players
with open("players.json", mode="r", encoding="utf-8") as read_file:
    player_data = json.load(read_file)

#Class for batters
class batter(): 
    """Class containing data on batter cards

    Attributes:
        name: Name of the player
        type: Type of player (Batter)
        hand: Handedness of the batter
        run: Running speed of the batter
        bunt: Bunting ability of the batter
        HnR: Hit-n-Run ability of the batter
        steal: Stealing ability of the batter
        field: Fielding data of the batter
        batting: Batting data of the batter
    """
    def __init__(self, name = None):
        """Initializes the batter class.

        Args:
            name (str): Name of batter.

        Raises:
            ValueError: If player is not a batter.
        """
        self.name = name if name is not None else None #Name
        
        dic = player_data[self.name]
        self.type = dic['type'] #Batter or pitcher
        if self.type != 'B':
            raise ValueError("This is not a batter card")
        self.hand = dic['hand'] #Handedness
        self.run = dic['run'] #Running Speed
        self.bunt = dic['bunt'] #Bunting Ability
        self.HnR = dic['HnR'] #Hit-n-Run ability
        self.steal = dic['steal'] #Stealing ability
        self.field = {int(k): v for k, v in dic['fielding'].items()} #Fielding data
        self.batting = {'L': {int(k) if k != "pow" else k: v for k, v in dic["batting"]["L"].items()},
                        'R': {int(k) if k != "pow" else k: v for k, v in dic["batting"]["R"].items()}} #Batting Data
    
    def display(self):
        """Function for depicting batter cards.
        """
        #Create figure, axis
        fig = plt.figure(figsize = np.array([6,2.875])*1.25)
        ax = fig.add_subplot()

        #Have axis extend over whole figure
        ax.set_position([0,0,1,1])
        ax.set_xlim(0,1)
        ax.set_ylim(0,1)

        #Remove axis ticks
        ax.tick_params(left = False, right = False , labelleft = False , 
                labelbottom = False, bottom = False) 

        #Add handedness | name
        ax.text(0.02,0.94,self.hand, ha = 'left', transform = ax.transAxes, fontsize = 12, fontweight = 'bold')
        ax.axvline(0.04, ymin = 0.88, ymax = 0.97, c = 'k', lw = 1)
        ax.text(0.05,0.94,self.name.upper(), ha = 'left', transform = ax.transAxes, fontsize = 12, fontweight = 'bold')
        
        #Create dictionary for positional keys
        pos_keys = {0: "DH", 1:"P", 2:"C", 3:"1B", 4:"2B", 5:"3B", 6:"SS", 7:"LF", 8:"CF", 9:"RF"}

        #Initialize field string
        field_string = ''

        #Iterate over positions
        for e,pos in enumerate(self.field.keys()):

            #Add separator
            if e > 0:
                field_string += '/'

            if pos == 2: #catcher
                field_string += 'c-'
                field_string += str(self.field[pos][0]) #Rating
                field_string += '(+%d)' % self.field[pos][2] if self.field[pos][2] > 0 else '(%d)' % self.field[pos][2]   #Arm
                field_string += ' e%d' % self.field[pos][1] #Error number
                field_string += ', T1-%d' % self.field[pos][3] if self.field[pos][3] > 0 else ', T1' #Throwing errors
                field_string += '(pb-%d)' % self.field[pos][4] #Passed balls
            if pos in [3,4,5,6]: #Infielders
                field_string += pos_keys[pos].lower() + '-'
                field_string += str(self.field[pos][0]) #Rating
                field_string += ' e%d' % self.field[pos][1] #Error number
            elif pos in [7,8,9]: #Outfielders
                field_string += pos_keys[pos].lower() + '-'
                field_string += str(self.field[pos][0]) #Rating
                field_string += '(+%d)' % self.field[pos][2] if self.field[pos][2] > 0 else '(%d)' % self.field[pos][2] #Arm
                field_string += ' e%d' % self.field[pos][1] #Error number

        #Add field string
        ax.text(0.07,0.89,field_string, ha = 'left', transform = ax.transAxes, fontsize = 9)

        #Initialize steal string
        steal_string = 'stealing- '

        steal_string += '(%s)' % self.steal[0] #Rating
        steal_string += '   '

        #* Indicates good jump for no hold
        if self.steal[1]: steal_string += '*'

        #Dice rolls for good jump
        if len(self.steal[2]) != 0:
            for e,i in enumerate(self.steal[2]): #Iterate through rolls
                if e == 0: #Initialize start end
                    start = i
                    end = i
                else: #If not first roll
                    if i == end + 1: #Continue string if numbers consecutive
                        end = i
                    else: #If not consecutive
                        if start == end: #If single number
                            steal_string += '%d,' % start
                        elif end == (start + 1): #If two numbers
                            steal_string += '%d,%d,' % (start,end)
                        else: #If more than two numbers
                            steal_string += '%d-%d,' % (start,end)
                        
                        #Restart string
                        start = i   
                        end = i
            
            #Final string
            if start == end:
                steal_string += '%d,' % start
            elif end == (start + 1):
                steal_string += '%d,%d,' % (start,end)
            else:
                steal_string += '%d-%d,' % (start,end)

            steal_string = steal_string[:-1] #Remove last comma

        #If no rolls
        else:
            steal_string += '-'

        #Separator
        steal_string += '/'

        #Pickoff dice rolls
        if len(self.steal[3]) != 0:
            #Iterate through rolls
            for e,i in enumerate(self.steal[3]):
                if e == 0: #Initialize start end
                    start = i
                    end = i
                else: #If not first roll
                    if i == end + 1: #Continue string if numbers consecutive
                        end = i
                    else: #If not consecutive
                        if start == end: #If single number
                            steal_string += '%d,' % start
                        elif end == (start + 1): #If two numbers
                            steal_string += '%d,%d,' % (start,end)
                        else: #If more than two numbers
                            steal_string += '%d-%d,' % (start,end)

                        #Restart string
                        start = i   
                        end = i

            #Final string
            if start == end:
                steal_string += '%d,' % start
            elif end == (start + 1):
                steal_string += '%d,%d,' % (start,end)
            else:
                steal_string += '%d-%d,' % (start,end)
            
            #Remove last comma
            steal_string = steal_string[:-1]

        #If no rolls
        else:
            steal_string += '-'

        #Success rate
        steal_string += ' (%d-%d)' % (self.steal[4][0],self.steal[4][1]) 

        #Add steal string
        ax.text(0.35,0.94,steal_string, ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Add bunt and hit & run
        ax.text(0.7,0.94, 'bunting-%s' % self.bunt, ha = 'left', transform = ax.transAxes, fontsize = 10)
        ax.text(0.99,0.94, 'hit & run-%s' % self.HnR, ha = 'right', transform = ax.transAxes, fontsize = 10)

        #Add running speed
        ax.text(0.99,0.9, 'running 1-%d' % self.run, ha = 'right', transform = ax.transAxes, fontsize = 10)

        #Add batting data background
        ax.fill_between([0.01,0.5],0.84,0.88, color = 'dodgerblue')
        ax.fill_between([0.5,0.99],0.84,0.88, color = 'orangered')
        ax.fill_between([0.01,0.5],0.01,0.84, color = 'aliceblue')
        ax.fill_between([0.5,0.99],0.01,0.84, color = 'mistyrose')

        #Add batting data columns
        ax.axhline(0.88,xmin = 0.01,xmax = 0.99, c= 'k', lw = 1)
        ax.axhline(0.84,xmin = 0.01,xmax = 0.99, c= 'k', lw = 1)
        ax.axhline(0.80,xmin = 0.01,xmax = 0.99, c= 'k', lw = 1)
        ax.axvline(0.5, ymin = 0.05, ymax = 0.87, c = 'k', lw = 3)
        ax.axvline(1*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)
        ax.axvline(2*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)
        ax.axvline(4*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)
        ax.axvline(5*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)

        #Add column labels
        ax.text(0.5*.49/3+0.01, 0.815, '1', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(1.5*.49/3+0.01, 0.815, '2', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(2.5*.49/3+0.01, 0.815, '3', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(3.5*.49/3+0.01, 0.815, '1', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(4.5*.49/3+0.01, 0.815, '2', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(5.5*.49/3+0.01, 0.815, '3', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')

        #Add section labels
        ax.text( 0.25, 0.858, 'AGAINST LEFT-HANDED PITCHERS', ha = 'center', va = 'center',fontsize = 6)
        ax.text( 0.75, 0.858, 'AGAINST RIGHT-HANDED PITCHERS', ha = 'center', va = 'center',fontsize = 6)

        #Add batting data
        for e_hand,hand in enumerate(self.batting.keys()): #Iterate through pitcher handedness
            for e_roll,roll in enumerate(self.batting[hand].keys()): #Iterate through dice rolls
                if roll != 'pow': #Discount power metric
                    e_roll -= 1
                    counter = 0 #Counter for vertical spacing
                    for e_outcome,outcome in enumerate(self.batting[hand][roll]): #Iterate through outcomes
                        if isinstance(outcome,list): #If outcome is list

                            #Convert first outcome to string; print
                            string1,kwargs1 = string_converter_2(outcome[1])
                            ax.text(0.02+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, str(e_outcome + 2)+ '-'+string1,kwargs1,va = 'top', ha = 'left', transform = ax.transAxes, fontsize = 9)
                            
                            #Print rolls for first outcome
                            if outcome[0] == 1:
                                ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, 1,kwargs1,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                            else:
                                ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, '1-%d'%outcome[0],kwargs1,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                            counter += 1

                            #Convert second outcome to string; print
                            string2,kwargs2 = string_converter_2(outcome[2])
                            ax.text(0.02+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, '   '+string2,kwargs2,va = 'top', ha = 'left', transform = ax.transAxes, fontsize = 9)
                            
                            #Print rolls for second outcome
                            if outcome[0] == 19:
                                ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, 20,kwargs2,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                            else:
                                ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, '%d-20'%(outcome[0]+1),kwargs2,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                            counter += 1

                        else: #If outcome is not list
                            #Convert outcome to string; print
                            string,kwargs = string_converter_1(outcome)
                            ax.text(0.02+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, str(e_outcome + 2)+ '-'+string,kwargs,va = 'top', ha = 'left', transform = ax.transAxes, fontsize = 9)
                            counter += 1

#Class for pitchers
class pitcher():
    """Class containing data on pitcher cards.

    Attributes:
        name: Name of the player
        type: Type of player (Pitcher)
        hand: Handedness of the pitcher
        hold: Holding ability of the pitcher
        balk: Balking rate of the pitcher
        wp: Wild pitch rate of the pitcher
        field: Fielding data of the pitcher
        bunt: Bunting ability of the pitcher
        endurance_S: Starter endurance of the pitcher
        endurance_R: Relief endurance of the pitcher
        tired: Tired status of the pitcher
        pitching: Pitching data of the pitcher
    """
    def __init__(self, name = None):
        """Initializes the pitcher class.

        Args:
            name (str): Name of pitcher.

        Raises:
            ValueError: If player is not pitcher.
        """
        self.name = name if name is not None else None #Name
        
        dic = player_data[self.name]
        self.type = dic['type'] #Batter or Pitcher
        if self.type != 'P':
            raise ValueError("This is not a pitcher card")
            
        self.hand = dic['hand']#Handedness
        self.hold = dic['hold']#Holding ability
        self.balk = dic['balk']#Balking rate
        self.wp = dic['wp']#Wild pitch rate
        self.field = {int(k): v for k, v in dic['field'].items()} #Fielding data
        self.bunt = dic['bunt'] #Bunting ability
        self.endurance_S = dic['endurance_S'] #Starter endurance
        self.endurance_R = dic['endurance_R'] #Relief endurance
        self.tired = False #Tired status
        self.pitching = {'L': {int(k) if k != "pow" else k: v for k, v in dic["pitching"]["L"].items()},
                        'R': {int(k) if k != "pow" else k: v for k, v in dic["pitching"]["R"].items()}} #Pitching
        
    def display(self):
        """Function for depicting pitcher cards.
        """

        #Create figure, axis
        fig = plt.figure(figsize = np.array([6,2.875])*1.25)
        ax = fig.add_subplot()

        #Have axis extend over whole figure
        ax.set_position([0,0,1,1])
        ax.set_xlim(0,1)
        ax.set_ylim(0,1)
        
        #Remove axis ticks
        ax.tick_params(left = False, right = False , labelleft = False , 
                labelbottom = False, bottom = False) 

        #Name
        ax.text(0.02,0.9,self.name.upper(), ha = 'left', transform = ax.transAxes, fontsize = 12, fontweight = 'bold')
        
        #Balk and wild pitch rates
        ax.text(0.35,0.95,'bk- '+ str(self.balk), ha = 'left', transform = ax.transAxes, fontsize = 10)
        ax.text(0.44,0.95,'wp- '+ str(self.wp), ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Handedness
        ax.text(0.35,0.90,'throws %s' % ('LEFT' if self.hand == 'L' else 'RIGHT'), ha = 'left', transform = ax.transAxes, fontsize = 10, fontweight = 'bold')
        
        #Error number
        ax.text(0.54,0.95, 'e%d' % self.field[1][1], ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Hold ability
        ax.text(0.54,0.9, 'hold %d' % self.hold, ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Bunting
        ax.text(0.65,0.9, 'bunting-%s' % self.bunt, ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Fielding data
        ax.text(0.7,0.95, 'pitcher-%d'%self.field[1][0], ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Starter endurance
        if self.endurance_S != 'N/A':
            ax.text(0.85,0.95, 'starter-(%d)'%self.endurance_S, ha = 'left', transform = ax.transAxes, fontsize = 10)
        else:
            ax.text(0.85,0.95, 'starter-(N/A)', ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Relief endurance
        if self.endurance_R != 'N/A':
            ax.text(0.85,0.9, 'reliever-(%d)/%d'%(self.endurance_R[0],self.endurance_R[1]), ha = 'left', transform = ax.transAxes, fontsize = 10)
        else:
            ax.text(0.85,0.9, 'reliver-(N/A)', ha = 'left', transform = ax.transAxes, fontsize = 10)

        #Add pitching data background
        ax.fill_between([0.01,0.5],0.84,0.88, color = 'dodgerblue')
        ax.fill_between([0.5,0.99],0.84,0.88, color = 'orangered')
        ax.fill_between([0.01,0.5],0.01,0.84, color = 'aliceblue')
        ax.fill_between([0.5,0.99],0.01,0.84, color = 'mistyrose')

        #Add pitching data columns
        ax.axhline(0.88,xmin = 0.01,xmax = 0.99, c= 'k', lw = 1)
        ax.axhline(0.84,xmin = 0.01,xmax = 0.99, c= 'k', lw = 1)
        ax.axhline(0.80,xmin = 0.01,xmax = 0.99, c= 'k', lw = 1)
        ax.axvline(0.5, ymin = 0.05, ymax = 0.87, c = 'k', lw = 3)
        ax.axvline(1*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)
        ax.axvline(2*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)
        ax.axvline(4*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)
        ax.axvline(5*.49/3+0.01, ymin = 0.05, ymax = 0.84, c = 'k', lw = 1)

        #Add column labels
        ax.text(0.5*.49/3+0.01, 0.815, '4', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(1.5*.49/3+0.01, 0.815, '5', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(2.5*.49/3+0.01, 0.815, '6', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(3.5*.49/3+0.01, 0.815, '4', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(4.5*.49/3+0.01, 0.815, '5', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')
        ax.text(5.5*.49/3+0.01, 0.815, '6', ha = 'center', va = 'center', fontsize = 7, fontweight = 'light')

        #Add section labels
        ax.text( 0.25, 0.858, 'AGAINST LEFT-HANDED BATTERS', ha = 'center', va = 'center',fontsize = 6)
        ax.text( 0.75, 0.858, 'AGAINST RIGHT-HANDED BATTERS', ha = 'center', va = 'center',fontsize = 6)

        #Add pitching data
        for e_hand,hand in enumerate(self.pitching.keys()): #Iterate through handedness
            for e_roll,roll in enumerate(self.pitching[hand].keys()): #Iterate through dice rolls
                counter = 0
                for e_outcome,outcome in enumerate(self.pitching[hand][roll]): #Iterate through outcomes
                    if isinstance(outcome,list): #If outcome is list

                        #Convert first outcome to string; print
                        string1,kwargs1 = string_converter_2(outcome[1])
                        ax.text(0.02+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, str(e_outcome + 2)+ '-'+string1,kwargs1,va = 'top', ha = 'left', transform = ax.transAxes, fontsize = 9)
                        
                        #Print rolls for first outcome
                        if outcome[0] == 1:
                            ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, 1,kwargs1,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                        else:
                            ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, '1-%d'%outcome[0],kwargs1,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                        counter += 1

                        #Convert second outcome to string; print
                        string2,kwargs2 = string_converter_2(outcome[2])
                        ax.text(0.02+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, '   '+string2,kwargs2,va = 'top', ha = 'left', transform = ax.transAxes, fontsize = 9)
                        
                        #Print rolls for second outcome
                        if outcome[0] == 19:
                            ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, 20,kwargs2,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                        else:
                            ax.text(0.17+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, '%d-20'%(outcome[0]+1),kwargs2,va = 'top', ha = 'right', transform = ax.transAxes, fontsize = 9)
                        counter += 1

                    else: #If outcome is not list

                        #Convert outcome to string; print
                        string,kwargs = string_converter_1(outcome)
                        ax.text(0.02+(3*e_hand+e_roll)*0.49/3,0.78-counter*0.05, str(e_outcome + 2)+ '-'+string,kwargs,va = 'top', ha = 'left', transform = ax.transAxes, fontsize = 9)
                        counter += 1


        