import numpy as np
from config import (
    AGC_FACTOR,
    EPSILON,
    WINDOW_SIZE,
    MAX_GAIN,
    SMOOTHING_ALPHA
)

def real_time_agc(audio, agc_state):
    output = np.zeros_like(audio)

    for i, sample in enumerate(audio):
        # Update circular window
        agc_state.audio_window[agc_state.window_index] = sample
        agc_state.window_index = (
            agc_state.window_index + 1
        ) % WINDOW_SIZE

        # Compute gain
        max_amp = np.max(np.abs(agc_state.audio_window)) + EPSILON
        target_gain = min(
            (1.0 / max_amp) * AGC_FACTOR,
            MAX_GAIN
        )

        # Smooth gain
        agc_state.current_gain = (
            SMOOTHING_ALPHA * target_gain
            + (1.0 - SMOOTHING_ALPHA) * agc_state.current_gain
        )

        # Apply gain
        output[i] = sample * agc_state.current_gain

    return np.clip(output, -1.0, 1.0)
