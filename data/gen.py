
#%%
"""
Purpose of this script is to begin data generation in order to train a model
that will provide an estimate of the quality of a given team. 

Quality could be defined as the probability of winning against other teams 
with identical investment, where investment corresponds to levels and food
(health + attack) given to each pet. Tier of the animal does not correspond 
to any notion of quality or investment directly. 

Quality is also the notion of the future capability of the team. For example, a
team that just sold a strong pet to purchase a dragon certainly has a smaller 
amount of stats, but it's quality could have increased due to increased scaling
in future rounds. This type of quality will not be handled here initially. 
That requires training involving full gameplay. However training a model
using the initial quality proposed here will significantly under-value scaling
characters. Unless, their scaling behavior is allowed into team construction...

Training will require some form of pet embedding taking into account the 
pet's stats and equipment. Team embedding takes place through the concatenation
of each pet embedding and then through another network.

All learning should take place through dropout so that the network cannot rely
too much on any single path. 

"""

#%%



#%%

