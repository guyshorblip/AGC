import tkinter as tk

def run_gui(handlers):
    root = tk.Tk()
    root.title("Real-Time AGC")

    tk.Button(
        root,
        text="Select WAV File",
        command=handlers["file"]
    ).pack(pady=5)

    tk.Button(
        root,
        text="Start Recording",
        command=handlers["start"]
    ).pack(pady=5)

    tk.Button(
        root,
        text="Stop Recording",
        command=handlers["stop"]
    ).pack(pady=5)

    root.mainloop()
