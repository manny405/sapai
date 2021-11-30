=====
sapai
=====

``sapai`` is a Super Auto Pets engine built with reinforcement learning training and other related AI models in mind. You may see more of my published work in machine learning on `ResearchGate <https://www.researchgate.net/publication/347653898_Machine_Learned_Model_for_Solid_Form_Volume_Estimation_Based_on_Packing-Accessible_Surface_and_Molecular_Topological_Fragments>`_ or `ACS <https://pubs.acs.org/doi/full/10.1021/acs.jpca.0c06791>`_.

.. figure:: doc/static/workflow.png
    :height: 380
    :width: 404
    :align: center
    
    
.. contents::
    :local:
    
------------
Installation
------------

To start installing and using ``mcse``, it's highly recommended to start from an Anaconda distribution of Python, which can be downloaded for free here_. 

.. _here: https://www.anaconda.com/products/individual

Then download the library from Github. A ``zip`` file can be downloaded using the green download code button. Alternatively, this repository can be obtained using the following command from the command-line. 

.. code-block:: bash
    
    git clone https://github.com/manny405/sapai.git

After navigating to the ``sapai`` directory, installation is completed with the following command. 

.. code-block:: bash

    python setup.py install
    
    
---------------------------
Introduction: Code Examples
---------------------------

The following code exampes will be run through the Python shell. To start a Python shell session, open up your preferred command-line program, such as Terminal or Powershell, then type and enter ``python``.

###############
Creating a Pet
###############

.. code-block:: python
    
    >>> from sapai.pets import Pet
    >>> pet = Pet("ant")
    >>> print(pet)
    ### Printing pet is given in the form of < PetName Attack-Health Status > 
    < pet-ant 2-1 none >
    >>> pet.attack += 3
    >>> print(pet)
    < pet-ant 5-1 none >
    >>> print(pet.ability)
    ### Organization of pet abilities provided by super-auto-pets-db project
    {'description': 'Faint: Give a random friend +2/+1',
     'trigger': 'Faint',
     'triggeredBy': {'kind': 'Self'},
     'effect': {'kind': 'ModifyStats',
      'attackAmount': 2,
      'healthAmount': 1,
      'target': {'kind': 'RandomFriend', 'n': 1},
      'untilEndOfBattle': False}}
      
      
###############
Creating a Team
###############

.. code-block:: python
    
    >>> from sapai.pets import Pet
    >>> from sapai.teams import Team
    >>> ant = Pet("ant")
    >>> ox = Pet("ox")
    >>> tiger = Pet("tiger")
    >>> sheep = Pet("sheep")
    >>> team0 = Team([ant,ox,tiger])
    >>> team1 = Team([sheep,tiger])
    >>> print(team0)
    0: < Slot pet-ant 2-1 none > 
      1: < Slot pet-ox 1-4 none > 
      2: < Slot pet-tiger 4-3 none > 
      3: < Slot EMPTY > 
      4: < Slot EMPTY > 
   >>> print(team1)
   0: < Slot pet-sheep 2-2 none > 
     1: < Slot pet-tiger 4-3 none > 
     2: < Slot EMPTY > 
     3: < Slot EMPTY > 
     4: < Slot EMPTY >
   >>> team0.move(1,4)
   >>> print(team0)
   0: < Slot pet-ant 2-1 none > 
     1: < Slot pet-ox 1-4 none > 
     2: < Slot EMPTY > 
     3: < Slot EMPTY > 
     4: < Slot pet-tiger 4-3 none > 
   >>> team0.move_forward()
   >>> print(team0)
   0: < Slot pet-ant 2-1 none > 
     1: < Slot pet-ox 1-4 none > 
     2: < Slot pet-tiger 4-3 none > 
     3: < Slot EMPTY > 
     4: < Slot EMPTY >
    
######
Fights
######

.. code-block:: python
    
    ### Using the teams created in the last section
    >>> from sapai.fight import Fight
    >>> fight = Fight(team0,team1)
    >>> winner = fight.fight()
    >>> print(winner)
    2
    ### Possible fight outputs:
    ### 0 = Team0 Wins
    ### 1 = Team1 Wins
    ### 2 = Draw

The implementation of fights is efficient. Using IPython magic, this can be tested using the following IPython method:

.. code-block:: python

      from sapai.pets import Pet
      from sapai.teams import Team
      from sapai.fight import Fight
      ant = Pet("ant")
      ox = Pet("ox")
      tiger = Pet("tiger")
      sheep = Pet("sheep")
      team0 = Team([ant,ox,tiger.copy()])
      team1 = Team([sheep,tiger.copy()])
      
      def timing_test():
          f = Fight(team0,team1)
          winner = f.fight()
      
      %timeit timing_test()      
      ### On 2019 Macbook Pro:
      ###   1.75 ms ± 145 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
      ###   More than 500 fights per second on a single core
      
      
All fight history is stored for every phase, effect, and attack that occured during the fight. This fight history can be graphed and visualized. The full graph for the fight is shown below. 

  >>> from sapai.graph import graph_fight
  >>> graph_fight(fight, file_name="Example")


.. figure:: doc/static/fight_graph_full.png
    :height: 1333
    :width: 500
    :align: center

------
Status
------

Ongoing

1. The engine is still a work in progress. Notes are included for next steps. 

2. Player needs to be implemented with all possible player actions that can be taken. 

3. Play needs to be implemented with AI player organization through multiple different types of competitions. 

4. Model implementation is largely untouched. 

