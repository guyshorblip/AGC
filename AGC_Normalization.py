import numpy as np
from config import EPSILON

def normalize_audio(audio, target_rms=0.1):
    rms = np.sqrt(np.mean(audio ** 2) + EPSILON)
    audio = audio * (target_rms / rms)
    return np.clip(audio, -1.0, 1.0)
