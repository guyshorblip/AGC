def main():
    import tkinter as tk
    from tkinter import filedialog, messagebox
    import os
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
    import matplotlib.pyplot as plt
    import queue
    import threading
    import sys

    # ===============================
    # Configuration
    # ===============================
    fs = 44100
    agc_factor = 0.8
    EPSILON = 1e-10
    window_duration = 0.01
    window_size = int(fs * window_duration)

    # ===============================
    # AGC State
    # ===============================
    audio_window = np.zeros(window_size, dtype=np.float32)
    window_index = 0
    current_gain = 1.0

    def reset_agc():
        nonlocal audio_window, window_index, current_gain
        audio_window[:] = 0.0
        window_index = 0
        current_gain = 1.0

    # ===============================
    # Recording State
    # ===============================
    recording = False
    audio_queue = queue.Queue()
    original_audio_buffer = []
    processed_audio_buffer = []

    # ===============================
    # DSP Functions
    # ===============================
    def normalize_audio(audio, target_rms=0.1):
        rms = np.sqrt(np.mean(audio ** 2) + EPSILON)
        audio = audio * (target_rms / rms)
        return np.clip(audio, -1.0, 1.0)

    def real_time_agc(audio):
        nonlocal audio_window, window_index, current_gain

        output = np.zeros_like(audio)
        smoothing = 0.1

        for i in range(len(audio)):
            audio_window[window_index] = audio[i]
            window_index = (window_index + 1) % window_size

            max_amp = np.max(np.abs(audio_window)) + EPSILON
            target_gain = min(1.0 / max_amp * agc_factor, 10.0)

            current_gain = smoothing * target_gain + (1 - smoothing) * current_gain
            output[i] = audio[i] * current_gain

        return np.clip(output, -1.0, 1.0)

    # ===============================
    # Plotting
    # ===============================
    def plot_signals(original, processed, fs_local, file_path):
        t_orig = np.arange(len(original)) / fs_local
        t_proc = np.arange(len(processed)) / fs_local

        N = min(len(original), len(processed))
        gain = np.abs(processed[:N]) / (np.abs(original[:N]) + EPSILON)
        t_gain = np.arange(N) / fs_local

        plt.figure(figsize=(14, 10))

        plt.subplot(3, 1, 1)
        plt.plot(t_orig, original)
        plt.title("Original Signal (Normalized, Display ±5)")
        plt.ylim(-5, 5)
        plt.grid(True)
        plt.axhline(1, color='gray', linestyle='--', alpha=0.5)
        plt.axhline(-1, color='gray', linestyle='--', alpha=0.5)

        plt.subplot(3, 1, 2)
        plt.plot(t_proc, processed)
        plt.title("Processed Signal (AGC Applied, Display ±5)")
        plt.ylim(-5, 5)
        plt.grid(True)
        plt.axhline(1, color='gray', linestyle='--', alpha=0.5)
        plt.axhline(-1, color='gray', linestyle='--', alpha=0.5)

        plt.subplot(3, 1, 3)
        plt.plot(t_gain, gain)
        plt.title("AGC Gain Over Time")
        plt.ylim(0, 10)
        plt.xlabel("Time [s]")
        plt.grid(True)

        plt.tight_layout()
        plot_path = os.path.splitext(file_path)[0] + "_plots.png"
        plt.savefig(plot_path)
        plt.close()

        try:
            if sys.platform == "darwin":
                os.system(f"open '{plot_path}'")
            elif sys.platform == "win32":
                os.startfile(plot_path)
        except Exception:
            pass

    # ===============================
    # FILE PROCESSING (NEW)
    # ===============================
    def process_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")]
        )
        if not file_path:
            return

        reset_agc()

        audio, fs_local = sf.read(file_path, dtype='float32')
        if audio.ndim > 1:
            audio = audio[:, 0]

        audio = normalize_audio(audio)
        processed = real_time_agc(audio)

        processed_path = os.path.splitext(file_path)[0] + "_processed.wav"
        sf.write(processed_path, processed, fs_local)

        plot_signals(audio, processed, fs_local, processed_path)
        messagebox.showinfo("Done", "File processed successfully")

    # ===============================
    # Recording
    # ===============================
    def audio_callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        audio_queue.put(indata[:, 0].copy())
        original_audio_buffer.append(indata[:, 0].copy())

    def record_audio():
        reset_agc()
        with sd.InputStream(samplerate=fs, channels=1, callback=audio_callback):
            while recording:
                sd.sleep(20)

    def process_real_time_audio():
        with sd.OutputStream(samplerate=fs, channels=1) as out:
            while recording or not audio_queue.empty():
                try:
                    chunk = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                chunk = normalize_audio(chunk)
                processed = real_time_agc(chunk)
                processed_audio_buffer.append(processed)
                out.write(processed.reshape(-1, 1))

    def start_recording():
        nonlocal recording
        recording = True
        original_audio_buffer.clear()
        processed_audio_buffer.clear()

        threading.Thread(target=record_audio, daemon=True).start()
        threading.Thread(target=process_real_time_audio, daemon=True).start()

    def stop_recording():
        nonlocal recording
        recording = False

        if not original_audio_buffer or not processed_audio_buffer:
            messagebox.showwarning(
                "No Data",
                "Please record at least 1–2 seconds of audio."
            )
            return

        recorded = np.concatenate(original_audio_buffer)
        processed = np.concatenate(processed_audio_buffer)

        save_file = filedialog.asksaveasfilename(defaultextension=".wav")
        if save_file:
            sf.write(save_file, recorded, fs)
            sf.write(save_file.replace(".wav", "_processed.wav"), processed, fs)
            plot_signals(recorded, processed, fs, save_file)

    # ===============================
    # GUI
    # ===============================
    root = tk.Tk()
    root.title("Real-Time AGC")

    tk.Button(root, text="Select WAV File", command=process_file).pack(pady=5)
    tk.Button(root, text="Start Recording", command=start_recording).pack(pady=5)
    tk.Button(root, text="Stop Recording", command=stop_recording).pack(pady=5)

    root.mainloop()



if __name__ == "__main__":
    main()
