from AGC_GUI import run_gui
from AGC_State import AGCState
from AGC_Algorithm import real_time_agc
from AGC_Normalization import normalize_audio
from AGC_Plots import plot_signals
from AGC_RealTime import start_realtime
from config import FS

import soundfile as sf
from tkinter import filedialog, messagebox
import numpy as np
import os
import time


def main():
    # ===============================
    # State & buffers
    # ===============================
    agc_state = AGCState()
    stop_flag = {"stop": False}

    original_buffer = []
    processed_buffer = []

    # ===============================
    # GUI callbacks
    # ===============================
    def process_file():
        path = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")]
        )
        if not path:
            return

        agc_state.reset()

        audio, fs = sf.read(path, dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]

        audio = normalize_audio(audio)
        processed = real_time_agc(audio, agc_state)

        out_path = os.path.splitext(path)[0] + "_processed.wav"
        sf.write(out_path, processed, fs)

        plot_signals(audio, processed, fs, out_path)
        messagebox.showinfo("Done", "File processed successfully")

    def start_recording():
        agc_state.reset()
        stop_flag["stop"] = False

        original_buffer.clear()
        processed_buffer.clear()

        start_realtime(
            agc_state,
            stop_flag,
            original_buffer,
            processed_buffer
        )

    def stop_recording():
        # Signal threads to stop
        stop_flag["stop"] = True

        # Let audio threads flush remaining buffers
        time.sleep(0.4)

        if not original_buffer or not processed_buffer:
            messagebox.showwarning(
                "No Data",
                "No audio was recorded."
            )
            return

        # Finalize buffers
        recorded = np.concatenate(original_buffer)
        processed = np.concatenate(processed_buffer)

        # Ask user where to save
        save_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )

        if not save_path:
            return

        # Write files
        sf.write(save_path, recorded, FS)
        sf.write(
            save_path.replace(".wav", "_processed.wav"),
            processed,
            FS
        )

        # Plot results
        plot_signals(recorded, processed, FS, save_path)

    # ===============================
    # Start GUI
    # ===============================
    handlers = {
        "file": process_file,
        "start": start_recording,
        "stop": stop_recording
    }

    run_gui(handlers)


if __name__ == "__main__":
    main()
