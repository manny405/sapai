
from sapai.shop import Shop
from sapai.teams import Team


class Player():
    """
    Defines and implements all of the actions that a player can take. In particular
    each of these actions is directly tied to the actions reinforment learning 
    model can take. 
    
    
    Arguments
    ---------
    
    
    """
    def __init__(self, shop=None, team=None, lives=10, default_gold=10, 
                 pack="StandardPack"):
        self.shop = shop
        self.team = team
        self.lives = lives
        self.default_gold = default_gold
        self.gold = default_gold
        self.pack = pack
        
        ### Keep track of outcome of last fight for snail
        self.lf_winner = None
        
        ### Initialize shop and team if not provided
        if self.shop == None:
            self.shop = Shop(pack=self.pack)
        if self.team == None:
            self.team = Team()
    
    
    def buy(self, pet):
        """ Buy one pet from the store """
        raise Exception()
    
    
    def sell(self, pet):
        """ Sell one pet on the team """
        raise Exception()
    
    
    def freeze(self, pet):
        """ Freeze one pet in shop """
        raise Exception()
    
    
    def roll(self):
        """ Roll shop """
        raise Exception()
    
    
    def buy_combine(self):
        """ Combine two pets on purchase """
        raise Exception()
    
    
    def combine(self):
        """ Combine two pets together """
        raise Exception()
    
    
    def move(self):
        """ Move pet to a different team slot """
        raise Exception()
    
    
    def end(self):
        """ End turn and move to fight phase """
        raise Exception()
        
    
    def __repr__(self):
        print_str = "CURRENT TEAM: \n--------------\n"+self.team.__repr__()+"\n"
        print_str += "CURRENT SHOP: \n--------------\n"+self.shop.__repr__()
        return print_str