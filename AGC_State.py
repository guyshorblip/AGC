import numpy as np
from config import WINDOW_SIZE

class AGCState:
    def __init__(self):
        self.audio_window = np.zeros(WINDOW_SIZE, dtype=np.float32)
        self.window_index = 0
        self.current_gain = 1.0

    def reset(self):
        self.audio_window[:] = 0.0
        self.window_index = 0
        self.current_gain = 1.0
