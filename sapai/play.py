# %%


class Play:
    """
    Input the player list and mode that the game should be played in. This class
    Defines the actions of an overall game including shopping, battles, and
    lives of the player.

    Tournament mode will be the most basic mode for learning purposes. This just
    constructs a tournament of players where each turn the losing is removed
    from the tournament. This type of game will optimize only the most ideal
    play.

    Arena mode will mimic the way the game seems to be played. In this, after
    each match, players will be pooled based on thier record. Only players with
    similar records may play one another. Once a player reaches 0 lives, their
    play will end.

    Versus mode will mimic the versus game-mode including the way that the game
    adds clones of characters to the game.

    """

    def __init__(self, players=None, mode="tournament"):
        players = players or []

        raise NotImplementedError


# %%
