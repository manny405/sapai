"""

Definition and implementation of the reinforment model that will be used to 
expertly learn how to play the game. 

Notes:
    - The capability to add rules to the model should be added. For example, 
        only allowing the model to purchase certain animals. This will allow
        the capability to learn novel and more interesting strategies. 
    - Beginning training model only with tier1 animals for the first few turns
        thereby making it easier to learn good initial behavior
    - Continue with tier2 animals and so on
    
    - Model makes selections based on a mask of possible behaviors that are 
        available. For example, if there's no gold left, then the purchase 
        and roll actions have a mask value of 0 and therefore the action 
        cannot be performed. This will hopefully not be detremental to training. 
        - In addition, biasing the training such that the desired value for these
            is zero may be a better approach.
        
"""
