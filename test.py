# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import time
import csv
import os
from datetime import datetime
import sys
import subprocess

# macOSのTkinterバグ回避
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class JarvisSoundTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("MARK FOCUS : SYSTEM v1.2")
        self.root.geometry("380x520")
        self.root.resizable(False, False)
        
        # Jarvis Color Palette
        self.color_bg = "#0A0F14"      
        self.color_accent = "#00F5FF"  
        self.color_alert = "#FF3B30"   
        self.color_text = "#E0E0E0"    
        self.color_sub = "#506070"     
        self.color_input_bg = "#161C22"

        # フォント設定 (日本語対応)
        self.font_main = ("Hiragino Kaku Gothic ProN", 12)
        self.font_bold = ("Hiragino Kaku Gothic ProN", 12, "bold")
        self.font_header = ("SF Pro Display", 9, "bold")

        # --- サウンド設定 ---
        self.snd_click = "/System/Library/Sounds/Tink.aiff"
        self.snd_alarm = "/System/Library/Sounds/Glass.aiff"
        self.snd_start = "/System/Library/Sounds/Pop.aiff"

        self.root.configure(bg=self.color_bg)

        # --- ファイル保存設定 ---
        self.log_dir = os.path.expanduser("~/Documents/MarkFocus")
        self.csv_file = os.path.join(self.log_dir, "study_log.csv")

        self.is_running = False
        self.start_time = 0
        self.target_seconds = 0
        self.notified = False
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _play_sound(self, sound_path):
        try:
            subprocess.Popen(["afplay", sound_path])
        except Exception:
            pass

    def setup_ui(self):
        self.header = tk.Label(self.root, text="▶ SYSTEM ONLINE", 
                               bg=self.color_bg, fg=self.color_accent, 
                               font=self.font_header, anchor="w")
        self.header.pack(fill="x", padx=35, pady=(25, 0))

        tk.Label(self.root, text="OBJECTIVE", bg=self.color_bg, fg=self.color_sub, 
                 font=("SF Pro Display", 8, "bold")).pack(anchor="w", padx=35, pady=(15, 0))
        
        self.task_entry = tk.Entry(self.root, font=("Hiragino Kaku Gothic ProN", 16), 
                                   bg=self.color_input_bg, fg=self.color_text, 
                                   bd=0, insertbackground=self.color_accent, 
                                   highlightthickness=1, highlightbackground=self.color_sub,
                                   highlightcolor=self.color_accent, justify="center")
        self.task_entry.pack(pady=5, ipady=8, fill="x", padx=35)

        self.mode_var = tk.StringVar(value="up")
        mode_frame = tk.Frame(self.root, bg=self.color_bg)
        mode_frame.pack(pady=15)
        
        for m_text, m_val in [("ASCEND", "up"), ("DESCEND", "down")]:
            rb = tk.Radiobutton(mode_frame, text=m_text, variable=self.mode_var, value=m_val, 
                                bg=self.color_bg, fg=self.color_sub, selectcolor=self.color_bg,
                                activeforeground=self.color_accent, font=("SF Pro Display", 9, "bold"), 
                                command=self.on_mode_change, bd=0)
            rb.pack(side="left", padx=15)

        self.target_frame = tk.Frame(self.root, bg=self.color_bg)
        self.target_entry = tk.Entry(self.target_frame, font=("SF Mono", 14), width=5, 
                                     bg=self.color_input_bg, fg=self.color_accent, 
                                     bd=0, justify="center", highlightthickness=1,
                                     highlightbackground=self.color_sub)
        self.target_entry.insert(0, "25")
        tk.Label(self.target_frame, text="MIN", bg=self.color_bg, fg=self.color_sub, font=("SF Pro", 7)).pack(side="right", padx=5)
        self.target_entry.pack(side="right")
        
        self.timer_container = tk.Frame(self.root, bg=self.color_bg, highlightthickness=1, highlightbackground="#203040")
        self.timer_container.pack(pady=10, padx=35, fill="x")

        self.label_display = tk.Label(self.timer_container, text="00:00:00", 
                                      font=("SF Mono", 40), 
                                      bg=self.color_bg, fg=self.color_accent)
        self.label_display.pack(pady=20)

        self.btn_main = tk.Button(self.root, text="INITIATE", command=self.start_timer, 
                                  bg=self.color_accent, fg=self.color_bg, 
                                  font=("SF Pro Display", 12, "bold"), 
                                  relief="flat", width=18, height=2, bd=0)
        self.btn_main.pack(pady=15)

        self.btn_terminate = tk.Button(self.root, text="TERMINATE & ARCHIVE", command=self.stop_timer, 
                                       bg=self.color_bg, fg=self.color_alert, 
                                       font=("SF Pro Display", 11, "bold"), 
                                       relief="flat", highlightthickness=1, 
                                       highlightbackground=self.color_alert, width=18, height=2)
        self.btn_terminate.pack(pady=5)
        self.btn_terminate.pack_forget()

    def on_mode_change(self):
        self._play_sound(self.snd_click)
        if self.mode_var.get() == "down":
            self.target_frame.pack(pady=0)
        else:
            self.target_frame.pack_forget()

    def start_timer(self):
        self._play_sound(self.snd_start)
        if self.mode_var.get() == "down":
            try:
                self.target_seconds = int(self.target_entry.get()) * 60
            except ValueError:
                return
        else:
            self.target_seconds = 0

        self.is_running = True
        self.start_time = time.time()
        self.notified = False
        
        self.btn_main.pack_forget()
        self.btn_terminate.pack(pady=15)
        self.task_entry.config(state="disabled")
        self.header.config(text="▶ MISSION IN PROGRESS", fg=self.color_accent)
        self.update_timer()

    def update_timer(self):
        if self.is_running:
            total_elapsed = time.time() - self.start_time
            mode = self.mode_var.get()
            color = self.color_accent

            if mode == "down":
                if total_elapsed < self.target_seconds:
                    display_sec = self.target_seconds - total_elapsed
                else:
                    display_sec = total_elapsed
                    color = self.color_alert
                    if not self.notified:
                        self.notified = True
                        self._play_sound(self.snd_alarm)
                        self.header.config(text="▶ LIMIT EXCEEDED", fg=self.color_alert)
                        messagebox.showinfo("JARVIS", "Target reached.")
            else:
                display_sec = total_elapsed

            self.label_display.config(text=self.format_time(display_sec), fg=color)
            self.root.after(100, self.update_timer)

    def format_time(self, seconds):
        s = int(seconds)
        return f"{s // 3600:02}:{(s % 3600) // 60:02}:{s % 60:02}"

    def stop_timer(self):
        self._play_sound(self.snd_click)
        # 日本語での確認ダイアログ
        if messagebox.askyesno("TERMINATE", "データを保存して終了しますか？"):
            self.is_running = False
            self.save_to_csv()
            self.reset_ui()

    def save_to_csv(self):
        """データをCSV形式で保存。utf-8-sigを使用しExcel文字化けを防ぐ。"""
        total_duration = int(time.time() - self.start_time)
        task_name = self.task_entry.get().strip() or "未定義タスク"
        now = datetime.now()
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        fieldnames = ["task", "date", "start_at", "duration", "duration_sec", "mode", "timestamp"]
        new_log = {
            "task": task_name,
            "date": now.strftime("%Y-%m-%d"),
            "start_at": now.strftime("%H:%M:%S"),
            "duration": self.format_time(total_duration),
            "duration_sec": total_duration,
            "mode": self.mode_var.get().upper(),
            "timestamp": time.time()
        }

        file_exists = os.path.isfile(self.csv_file)
        try:
            # encoding='utf-8-sig' に変更することでExcelの文字化けを防止
            with open(self.csv_file, "a", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(new_log)
        except Exception as e:
            messagebox.showerror("SAVE ERROR", f"保存エラー: {e}")

    def reset_ui(self):
        self.label_display.config(text="00:00:00", fg=self.color_accent)
        self.btn_terminate.pack_forget()
        self.btn_main.pack(pady=15)
        self.task_entry.config(state="normal")
        self.task_entry.delete(0, tk.END)
        self.header.config(text="▶ SYSTEM ONLINE", fg=self.color_accent)

    def on_closing(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisSoundTimer(root)
    root.mainloop()
