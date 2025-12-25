import queue
import threading
import sounddevice as sd

from config import FS
from AGC_Normalization import normalize_audio
from AGC_Algorithm import real_time_agc


def start_realtime(agc_state, stop_flag, original_buffer, processed_buffer):
    """
    Real-time audio engine:
    - Records audio from microphone
    - Applies AGC in real time
    - Plays processed audio
    - Stores original and processed streams
    """

    audio_queue = queue.Queue(maxsize=20)

    # ===============================
    # Audio input callback (RT safe)
    # ===============================
    def audio_callback(indata, frames, time, status):
        if status:
            print(status)

        try:
            chunk = indata[:, 0].copy()
            audio_queue.put_nowait(chunk)
            original_buffer.append(chunk)
        except queue.Full:
            # Drop frame instead of blocking RT thread
            pass

    # ===============================
    # Recording thread
    # ===============================
    def record_thread():
        with sd.InputStream(
            samplerate=FS,
            channels=1,
            callback=audio_callback,
            blocksize=0  # let backend decide
        ):
            while not stop_flag["stop"]:
                sd.sleep(20)

    # ===============================
    # Processing + playback thread
    # ===============================
    def process_thread():
        with sd.OutputStream(
            samplerate=FS,
            channels=1
        ) as out:
            while not stop_flag["stop"] or not audio_queue.empty():
                try:
                    chunk = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                chunk = normalize_audio(chunk)
                processed = real_time_agc(chunk, agc_state)

                processed_buffer.append(processed)
                out.write(processed.reshape(-1, 1))

    # ===============================
    # Start threads
    # ===============================
    threading.Thread(
        target=record_thread,
        daemon=True
    ).start()

    threading.Thread(
        target=process_thread,
        daemon=True
    ).start()
