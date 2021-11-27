


class Player():
    """
    Defines and implements all of the actions that a player can take. In particular
    each of these actions is directly tied to the actions reinforment learning 
    model can take. 
    
    Can also be programmed in phases similar to Fight
    
    Arguments
    ---------
    
    
    """
    def __init__(self, shop=None, team=None, lives=10, default_gold=10):
        raise Exception()
    
    
    def buy(self, pet):
        """ Buy one pet from the store """
        raise Exception()
    
    
    def sell(self):
        """ Sell one pet on the team """
        raise Exception()
    
    
    def freeze(self, idx):
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
        
        