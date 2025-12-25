# ===============================
# Audio Configuration
# ===============================
FS = 44100
CHANNELS = 1

# ===============================
# AGC Parameters
# ===============================
AGC_FACTOR = 0.8
TARGET_RMS = 0.1
EPSILON = 1e-10
MAX_GAIN = 10.0
SMOOTHING_ALPHA = 0.1

# ===============================
# Window Parameters
# ===============================
WINDOW_DURATION = 0.01  # seconds
WINDOW_SIZE = int(FS * WINDOW_DURATION)

# ===============================
# Plotting
# ===============================
PLOT_DISPLAY_LIMIT = 5

# ===============================
# General
# ===============================
DEBUG = False
