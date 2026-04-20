# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
import time
import csv
import os
from datetime import datetime
import sys
import subprocess

if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class JarvisSystemV2:
    def __init__(self, root):
        self.root = root
        self.root.title("MARK FOCUS : SYSTEM v2.2")
        self.root.geometry("400x640")
        self.root.resizable(False, False)
        
        # Jarvis Color Palette
        self.color_bg = "#0A0F14"      
        self.color_accent = "#00F5FF"  
        self.color_alert = "#FF3B30"   
        self.color_warning = "#FF9500" # オレンジ（警告/中止用）
        self.color_text = "#E0E0E0"    
        self.color_sub = "#506070"     
        self.color_input_bg = "#12181F"
        self.color_border = "#1A242D"
        self.color_active_btn = "#1A3A4A"

        self.root.configure(bg=self.color_bg)

        # サウンド
        self.snd_click = "/System/Library/Sounds/Tink.aiff"
        self.snd_alarm = "/System/Library/Sounds/Glass.aiff"
        self.snd_start = "/System/Library/Sounds/Pop.aiff"
        self.snd_abort = "/System/Library/Sounds/Basso.aiff" # 中止音

        # ファイル
        self.log_dir = os.path.expanduser("~/Documents/MarkFocus")
        self.csv_file = os.path.join(self.log_dir, "study_log.csv")

        self.is_running = False
        self.start_time = 0
        self.target_seconds = 0
        self.notified = False
        
        self.setup_styles()
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TCombobox", 
                        fieldbackground=self.color_input_bg, 
                        background=self.color_sub, 
                        foreground=self.color_accent,
                        darkcolor=self.color_bg,
                        lightcolor=self.color_sub,
                        arrowcolor=self.color_accent)

    def _play_sound(self, sound_path):
        try:
            subprocess.Popen(["afplay", sound_path])
        except Exception:
            pass

    def setup_ui(self):
        # 1. HEADER
        header_frame = tk.Frame(self.root, bg=self.color_bg)
        header_frame.pack(fill="x", padx=30, pady=(25, 10))
        
        self.header_status = tk.Label(header_frame, text="● SYSTEM ONLINE", 
                                     bg=self.color_bg, fg=self.color_accent, 
                                     font=("SF Pro Display", 10, "bold"))
        self.header_status.pack(side="left")

        # 2. MISSION BRIEFING
        briefing_box = tk.Frame(self.root, bg=self.color_bg, highlightthickness=1, highlightbackground=self.color_border)
        briefing_box.pack(fill="x", padx=30, pady=10, ipady=10)

        tk.Label(briefing_box, text="OBJECTIVE", bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 8, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.task_entry = tk.Entry(briefing_box, font=("Hiragino Kaku Gothic ProN", 13), 
                                   bg=self.color_input_bg, fg=self.color_text, 
                                   bd=0, insertbackground=self.color_accent, 
                                   highlightthickness=1, highlightbackground="#253039",
                                   highlightcolor=self.color_accent, justify="center")
        self.task_entry.pack(pady=(5, 10), padx=15, fill="x", ipady=5)

        tk.Label(briefing_box, text="CLASSIFICATION", bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 8, "bold")).pack(anchor="w", padx=15)
        self.tag_var = tk.StringVar()
        self.tag_combo = ttk.Combobox(briefing_box, textvariable=self.tag_var, 
                                     values=["授業", "課題", "自主学習", "読書", "会議", "プロジェクト"],
                                     font=("Hiragino Kaku Gothic ProN", 11))
        self.tag_combo.pack(pady=(5, 0), padx=15, fill="x")
        self.tag_combo.set("自主学習")

        # 3. OPERATION MODE
        mode_label_frame = tk.Frame(self.root, bg=self.color_bg)
        mode_label_frame.pack(fill="x", padx=30, pady=(15, 0))
        tk.Label(mode_label_frame, text="OPERATION MODE", bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 8, "bold")).pack(side="left")
        self.target_label = tk.Label(mode_label_frame, text="GOAL", bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 8, "bold"))
        self.target_label.pack(side="right")

        param_frame = tk.Frame(self.root, bg=self.color_bg)
        param_frame.pack(fill="x", padx=30, pady=(5, 10))

        self.mode_var = tk.StringVar(value="up")
        self.mode_container = tk.Frame(param_frame, bg=self.color_border, padx=1, pady=1)
        self.mode_container.pack(side="left")

        self.btn_up = tk.Button(self.mode_container, text="COUNT UP", command=lambda: self.set_mode("up"),
                               bg=self.color_active_btn, fg=self.color_accent, font=("SF Pro Display", 9, "bold"),
                               relief="flat", bd=0, width=12, height=1, activebackground=self.color_active_btn)
        self.btn_up.pack(side="left")

        self.btn_down = tk.Button(self.mode_container, text="COUNT DOWN", command=lambda: self.set_mode("down"),
                                 bg=self.color_input_bg, fg=self.color_sub, font=("SF Pro Display", 9, "bold"),
                                 relief="flat", bd=0, width=12, height=1, activebackground=self.color_input_bg)
        self.btn_down.pack(side="left")

        target_container = tk.Frame(param_frame, bg=self.color_input_bg, highlightthickness=1, highlightbackground=self.color_border)
        target_container.pack(side="right")
        self.target_entry = tk.Entry(target_container, font=("SF Mono", 12, "bold"), width=4, 
                                     bg=self.color_input_bg, fg=self.color_accent, bd=0, justify="center")
        self.target_entry.insert(0, "25")
        self.target_entry.pack(side="left", padx=5, pady=5)
        tk.Label(target_container, text="MIN", bg=self.color_input_bg, fg=self.color_sub, font=("SF Pro Display", 7)).pack(side="left", padx=(0, 8))

        # 4. CHRONOMETER
        self.timer_frame = tk.Frame(self.root, bg=self.color_bg, bd=1, highlightthickness=1, highlightbackground=self.color_accent)
        self.timer_frame.pack(pady=20, padx=30, fill="x")

        self.label_display = tk.Label(self.timer_frame, text="00:00:00", 
                                      font=("SF Mono", 48, "bold"), 
                                      bg=self.color_bg, fg=self.color_accent)
        self.label_display.pack(pady=15)

        # 5. ACTIONS
        # 待機中ボタン
        self.btn_main = tk.Button(self.root, text="INITIATE SESSION", command=self.start_timer, 
                                  bg=self.color_accent, fg=self.color_bg, 
                                  font=("SF Pro Display", 12, "bold"), 
                                  relief="flat", height=2, bd=0)
        self.btn_main.pack(fill="x", padx=30, pady=10)

        # 進行中ボタン（コンテナ）
        self.action_frame = tk.Frame(self.root, bg=self.color_bg)
        
        self.btn_abort = tk.Button(self.action_frame, text="ABORT", command=self.abort_session, 
                                   bg=self.color_bg, fg=self.color_alert, 
                                   font=("SF Pro Display", 10, "bold"), 
                                   relief="flat", highlightthickness=1, 
                                   highlightbackground=self.color_alert, width=12, height=2)
        self.btn_abort.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.btn_complete = tk.Button(self.action_frame, text="COMPLETE & ARCHIVE", command=self.complete_session, 
                                     bg=self.color_accent, fg=self.color_bg, 
                                     font=("SF Pro Display", 10, "bold"), 
                                     relief="flat", width=22, height=2)
        self.btn_complete.pack(side="right", padx=(5, 0), expand=True, fill="x")

    def set_mode(self, mode):
        if self.is_running: return
        self._play_sound(self.snd_click)
        self.mode_var.set(mode)
        if mode == "up":
            self.btn_up.config(bg=self.color_active_btn, fg=self.color_accent)
            self.btn_down.config(bg=self.color_input_bg, fg=self.color_sub)
            self.target_label.config(text="GOAL")
        else:
            self.btn_up.config(bg=self.color_input_bg, fg=self.color_sub)
            self.btn_down.config(bg=self.color_active_btn, fg=self.color_accent)
            self.target_label.config(text="LIMIT")

    def start_timer(self):
        try:
            val = int(self.target_entry.get())
            if val <= 0: raise ValueError
            self.target_seconds = val * 60
        except ValueError:
            messagebox.showwarning("ERROR", "無効な時間設定です。")
            return

        self._play_sound(self.snd_start)
        self.is_running = True
        self.start_time = time.time()
        self.notified = False
        
        self.btn_main.pack_forget()
        self.action_frame.pack(fill="x", padx=30, pady=10)
        
        self.task_entry.config(state="disabled")
        self.tag_combo.config(state="disabled")
        self.target_entry.config(state="disabled")
        self.btn_up.config(state="disabled")
        self.btn_down.config(state="disabled")
        self.header_status.config(text="● MISSION IN PROGRESS", fg=self.color_accent)
        
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
                    display_sec = total_elapsed - self.target_seconds
                    color = self.color_alert
                    if not self.notified: self._trigger_alarm("LIMIT EXCEEDED")
            else:
                display_sec = total_elapsed
                if display_sec >= self.target_seconds:
                    color = "#FFD700" 
                    if not self.notified: self._trigger_alarm("GOAL REACHED")

            self.label_display.config(text=self.format_time(display_sec), fg=color)
            self.timer_frame.config(highlightbackground=color)
            self.root.after(100, self.update_timer)

    def _trigger_alarm(self, msg):
        self.notified = True
        self._play_sound(self.snd_alarm)
        self.header_status.config(text=f"● {msg}", fg=self.color_alert)

    def format_time(self, seconds):
        s = int(seconds)
        return f"{s // 3600:02}:{(s % 3600) // 60:02}:{s % 60:02}"

    def complete_session(self):
        """正常終了：保存してリセット"""
        self._play_sound(self.snd_click)
        if messagebox.askyesno("COMPLETE", "セッションを終了し、データを記録しますか？"):
            self.is_running = False
            self.save_to_csv()
            self.header_status.config(text="● MISSION ARCHIVED", fg=self.color_accent)
            self.reset_ui()

    def abort_session(self):
        """中止：保存せずにリセット"""
        self._play_sound(self.snd_abort)
        if messagebox.askretrycancel("WARNING: ABORT MISSION", "作戦を中止しますか？\n(データは保存されません)"):
            self.is_running = False
            self.header_status.config(text="● MISSION ABORTED", fg=self.color_warning)
            self.reset_ui()

    def save_to_csv(self):
        total_duration = int(time.time() - self.start_time)
        task_name = self.task_entry.get().strip() or "UNDEFINED MISSION"
        tag_name = self.tag_var.get().strip() or "NO TAG"
        now = datetime.now()
        
        if not os.path.exists(self.log_dir): os.makedirs(self.log_dir)

        fieldnames = ["task", "tag", "date", "start_at", "duration", "duration_sec", "mode", "timestamp"]
        new_log = {
            "task": task_name, "tag": tag_name, "date": now.strftime("%Y-%m-%d"),
            "start_at": now.strftime("%H:%M:%S"), "duration": self.format_time(total_duration),
            "duration_sec": total_duration, "mode": self.mode_var.get().upper(),
            "timestamp": time.time()
        }

        file_exists = os.path.isfile(self.csv_file)
        try:
            with open(self.csv_file, "a", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists: writer.writeheader()
                writer.writerow(new_log)
        except Exception as e:
            messagebox.showerror("SAVE ERROR", f"保存エラー: {e}")

    def reset_ui(self):
        self.label_display.config(text="00:00:00", fg=self.color_accent)
        self.timer_frame.config(highlightbackground=self.color_accent)
        self.action_frame.pack_forget()
        self.btn_main.pack(fill="x", padx=30, pady=10)
        
        self.task_entry.config(state="normal")
        self.tag_combo.config(state="normal")
        self.target_entry.config(state="normal")
        self.btn_up.config(state="normal")
        self.btn_down.config(state="normal")
        self.task_entry.delete(0, tk.END)

    def on_closing(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisSystemV2(root)
    root.mainloop()
