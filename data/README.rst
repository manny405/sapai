====
Data
====


This folder contains data that may be helpful for training agents. 

-------
Round 1
-------

The ``Round_1.pt`` contains a dictionary of all possible teams that can be constructed in round 1 of SAP and their relative win-rate against one-another. This file can be loaded into memory using the follow code.

.. code-block:: python
    
    >>> import torch
    >>> results = torch.load("Round_1.pt")
    >>> print(f"Number of Possible Teams: {len(output_dict)}")
    5013
    
The key of the dictionary is a loss-less compression of the Team. The Team can be rebuilt in memory easily using ``sapai.compress.decompress``. For example, if you would like to examine the best possible teams from Round 1, the following code can be used.  

.. code-block:: python
    
    >>> import torch
    >>> import numpy as np
    >>> from sapai.compress import decompress
    >>> results = torch.load("Round_1.pt")
    >>> keys = np.array(list(results.keys()))
    >>> win_rate = np.array(list(results.values()))
    >>> sort_idx = np.argsort(win_rate)[::-1]
    >>> best_win_rate = win_rate[sort_idx[0]]
    >>> best_team = decompress(keys[sort_idx[0]])
    >>> print(f"BEST WIN RATE: {best_win_rate:.3f}")
    0.910
    >>> print(f"BEST TEAM: \n{best_team}")
    BEST TEAM: 
    0: < Slot pet-fish 2-3 none 1-0 > 
        1: < Slot pet-ant 2-1 none 1-0 > 
        2: < Slot pet-cricket 1-2 none 1-0 > 
        3: < Slot EMPTY > 
        4: < Slot EMPTY >
