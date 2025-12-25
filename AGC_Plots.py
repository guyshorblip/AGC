import numpy as np
import matplotlib
matplotlib.use("Agg")  # <<< CRITICAL: non-GUI backend
import matplotlib.pyplot as plt
import os
import sys
from config import EPSILON


def plot_signals(original, processed, fs, file_path):
    # ===============================
    # Align signals
    # ===============================
    N = min(len(original), len(processed))
    original = original[:N]
    processed = processed[:N]

    t = np.arange(N) / fs
    gain = np.abs(processed) / (np.abs(original) + EPSILON)

    # ===============================
    # Create plot (NO GUI)
    # ===============================
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    axes[0].plot(t, original)
    axes[0].set_title("Original Signal")
    axes[0].grid(True)

    axes[1].plot(t, processed)
    axes[1].set_title("Processed Signal (AGC)")
    axes[1].grid(True)

    axes[2].plot(t, gain)
    axes[2].set_title("AGC Gain Over Time")
    axes[2].set_xlabel("Time [s]")
    axes[2].grid(True)

    fig.tight_layout()

    # ===============================
    # Save
    # ===============================
    plot_path = os.path.splitext(file_path)[0] + "_plots.png"
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)

    # ===============================
    # Open with OS image viewer
    # ===============================
    if sys.platform == "darwin":
        os.system(f"open '{plot_path}'")
    elif sys.platform.startswith("linux"):
        os.system(f"xdg-open '{plot_path}'")
    elif sys.platform == "win32":
        os.startfile(plot_path)
