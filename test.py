import tkinter as tk
from tkinter import messagebox
import time
import csv
import os
from datetime import datetime


class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S Focus Log")
        self.root.geometry("420x520")
        self.root.configure(bg="#0B0F14")

        self.is_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.csv_file = "study_log.csv"

        # JARVIS color palette
        self.bg = "#0B0F14"
        self.panel = "#111826"
        self.cyan = "#00E5FF"
        self.red = "#FF3B30"
        self.white = "#E6F1FF"
        self.muted = "#8AA0B6"

        self.font_main = ("Helvetica", 14)
        self.font_timer = ("Helvetica", 44, "bold")

        # Title
        tk.Label(
            root,
            text="STUDY MODULE",
            bg=self.bg,
            fg=self.cyan,
            font=("Helvetica", 14, "bold"),
        ).pack(pady=(25, 10))

        # Task label
        tk.Label(
            root,
            text="Current Objective",
            bg=self.bg,
            fg=self.muted,
            font=self.font_main,
        ).pack(pady=(10, 5))

        # Entry
        self.task_entry = tk.Entry(
            root,
            font=self.font_main,
            justify="center",
            bg=self.panel,
            fg=self.white,
            insertbackground=self.cyan,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.cyan,
            highlightcolor=self.cyan,
        )
        self.task_entry.pack(pady=10, ipady=10, fill="x", padx=40)

        # Timer display
        self.label_display = tk.Label(
            root, text="00:00:00", font=self.font_timer, bg=self.bg, fg=self.cyan
        )
        self.label_display.pack(pady=40)

        # Start button
        self.btn_start = tk.Button(
            root,
            text="INITIATE",
            command=self.start_timer,
            bg=self.cyan,
            fg="#0B0F14",
            font=self.font_main,
            relief="flat",
            activebackground="#00BBD4",
            activeforeground="#0B0F14",
            width=18,
        )
        self.btn_start.pack(pady=8)

        # Stop button
        self.btn_stop = tk.Button(
            root,
            text="TERMINATE & SAVE",
            command=self.stop_timer,
            bg=self.red,
            fg="white",
            font=self.font_main,
            relief="flat",
            activebackground="#CC2F28",
            activeforeground="white",
            width=18,
        )
        self.btn_stop.pack(pady=8)
        self.btn_stop.pack_forget()

    def update_timer(self):
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
            self.label_display.config(text=self.format_time(self.elapsed_time))
            self.root.after(100, self.update_timer)

    def format_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"

    def start_timer(self):
        self.is_running = True
        self.start_time = time.time() - self.elapsed_time

        self.btn_start.pack_forget()
        self.btn_stop.pack(pady=8)

        self.task_entry.config(state="disabled")

        self.update_timer()

    def stop_timer(self):
        if messagebox.askyesno("Confirm", "Terminate session and save log?"):
            self.is_running = False
            self.save_to_csv()
            self.reset_timer()

    def save_to_csv(self):
        task_name = self.task_entry.get().strip() or "Untitled Task"
        now = datetime.now()

        date_str = now.strftime("%Y-%m-%d")
        start_time_str = now.strftime("%H:%M:%S")
        duration_str = self.format_time(self.elapsed_time)

        file_exists = os.path.isfile(self.csv_file)

        with open(self.csv_file, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Task", "Start Time", "Duration"])
            writer.writerow([date_str, task_name, start_time_str, duration_str])

    def reset_timer(self):
        self.elapsed_time = 0
        self.label_display.config(text="00:00:00")

        self.btn_stop.pack_forget()
        self.btn_start.pack(pady=8)

        self.task_entry.config(state="normal")
        self.task_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()
