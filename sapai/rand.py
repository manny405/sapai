import numpy as np


class MockRandomState:
    """
    Numpy RandomState is actually extremely slow, requiring about 300 microseconds
    for any operation involving state. Therefore, when reproducibility is not
    necessary, this class should be used to immensly improve efficiency.

    Tests were run for Player:
        %timeit _ = Player.from_state(pstate)
        # ORIGINAL: 26.8 ms ± 788 µs per loop
        # MockRandomState: 1.15 ms ± 107 µs per loop
    Use of MockRandomState improved the performance by 10x. This is very important.

    """

    def __init__(self):
        pass

    def set_state(self):
        """Doesn't do anything"""
        return None

    def get_state(self):
        return None

    def choice(self, *args, **kwargs):
        return np.random.choice(*args, **kwargs)
