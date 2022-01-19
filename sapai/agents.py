

import os,json
from sapai import Player
from sapai.fight import Fight
from sapai.compress import compress,decompress

### Pets with a random component
###   Random component in the future should just be handled in an exact way
###   whereby all possible outcomes are evaluated just once. This would 
###   significantly speed up training. 
random_buy_pets = {"pet-otter"}
random_sell_pets = {"pet-beaver"}
random_pill_pets = {"pet-ant"}
random_fight_pets = {"pet-mosquito"}

class CombinatorialAgent():
    """
    The CombinatorialAgent is built to resemble the way that a human player will
    make decisions. However, the CombinatorialAgent will consider all possible 
    combinations of decisions in order arrive at the best possible outcome. 
    
    The limitation of this method is the depth with which decisions are
    searched and how decisions are ranked. 
    
    """
    def __init__(self, 
                 shop=None, 
                 team=None, 
                 lives=10, 
                 default_gold=10,
                 gold=10, 
                 turn=1,
                 lf_winner=None,
                 max_turns=1, 
                 pack="StandardPack",
                 ranker=None,
                 ):
        self.max_turns = max_turns
        
        if pack not in ["StandardPack", "ExpansionPack1"]:
            raise Exception("Pack must be StandardPack or ExpansionPack1")
        
        self.player = Player(shop=shop, 
                             team=team, 
                             lives=lives, 
                             default_gold=default_gold,
                             gold=gold, 
                             turn=turn,
                             lf_winner=lf_winner,
                             pack=pack)
        
        self.ranker = ranker
        
    
    def train(self):
        ### Start turn
        self.player.start_turn()
        self.player.buy_pet(self.player.shop[0])
        self.player.buy_pet(self.player.shop[0])
        self.player.buy_pet(self.player.shop[0])
        
        # self.player.start_turn()
        # self.player.buy_pet(self.player.shop[0])
        # self.player.buy_pet(self.player.shop[0])
        
        self.player.end_turn()
        rank = self.ranker(self.player.team)
        

class DatabaseLookupRanker():
    """
    Will provide a rank to a given team based on its performance on a database
    of teams. 
    
    """
    def __init__(self, 
                 path="",
                 turn=1,
                 randn=100,
                ):
        self.path = path
        self.turn = turn
        self.randn = randn
        
        if os.path.exists(path):
            with open(path, "r") as f:
                self.database = json.loads(f)
        else:
            self.database = {}

        self.team_database = {}
        for key,value in self.database:
            self.team_database[key] = {"team": decompress(key),
                                       "wins": int(len(self.database)*value),
                                       "total": len(self.database)-1}
    
    
    def __call__(self, team):
        c = compress(team)
        if c in self.database:
            return self.database[c]
        else:
            return self.run_against_database(team)
    
    
    def run_against_database(self, team):
        #### Add team to database
        team_key = compress(team)
        if team_key not in self.team_database:
            self.team_database[team_key] = {"team": team, 
                                            "wins": 0,
                                            "total": 0}
        
        for key,value in self.team_database.items():
            # print(team, value["team"])
            self.t0 = team
            self.t1 = value["team"]
            
            f = Fight(team,value["team"])
            winner = f.fight()
        
            winner_key = [[team_key],[key],[]][winner]
            for temp_key in winner_key:
                self.team_database[temp_key]["wins"] += 1
            for temp_key in [team_key,key]:
                self.team_database[temp_key]["total"] += 1
                
        for key,value in self.team_database.items():
            wins = self.team_database[key]["wins"]
            total = self.team_database[key]["total"]
            self.database[key] = wins/total
        
        wins = self.team_database[team_key]["wins"]
        total = self.team_database[team_key]["total"]
        return wins/total
        

    def test_against_database(self, team):
        wins = 0
        total = 0
        for key,value in self.team_database.items():
            # print(team, value["team"])
            f = Fight(team,value["team"])
            winner = f.fight()
            if winner == 0:
                wins += 1
            total += 1
        return wins,total