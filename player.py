import json

#Obtain data for players
with open("players.json", mode="r", encoding="utf-8") as read_file:
    player_data = json.load(read_file)

#Class for batters
class batter(): 
    def __init__(self, name = None):
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
        
#Class for pitchers
class pitcher():
    def __init__(self, name = None):
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
        
