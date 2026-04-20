# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
import time
import csv
import os
from datetime import datetime
import sys
import subprocess

# --- macOS Matplotlib バグ回避設定 ---
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class JarvisSystemV2:
    def __init__(self, root):
        self.root = root
        self.root.title("MARK FOCUS : SYSTEM v2.9")
        self.root.geometry("400x720")
        self.root.resizable(False, False)
        
        # Color Palette
        self.color_bg = "#0A0F14"      
        self.color_accent = "#00F5FF"  
        self.color_alert = "#FF3B30"   
        self.color_warning = "#FF9500" 
        self.color_text = "#E0E0E0"    
        self.color_sub = "#506070"     
        self.color_input_bg = "#12181F"
        self.color_border = "#1A242D"
        self.color_active_btn = "#1A3A4A"

        self.root.configure(bg=self.color_bg)

        # Sounds
        self.snd_click = "/System/Library/Sounds/Tink.aiff"
        self.snd_alarm = "/System/Library/Sounds/Glass.aiff"
        self.snd_start = "/System/Library/Sounds/Pop.aiff"
        self.snd_abort = "/System/Library/Sounds/Basso.aiff"

        # Files
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
        style.configure("TCombobox", fieldbackground=self.color_input_bg, background=self.color_sub, foreground=self.color_accent, darkcolor=self.color_bg, lightcolor=self.color_sub, arrowcolor=self.color_accent)
        # Treeview Styling
        style.configure("Treeview", background=self.color_input_bg, foreground=self.color_text, fieldbackground=self.color_input_bg, rowheight=30, borderwidth=0, font=("Hiragino Kaku Gothic ProN", 10))
        style.map("Treeview", background=[('selected', self.color_active_btn)], foreground=[('selected', self.color_accent)])
        style.configure("Treeview.Heading", background=self.color_border, foreground=self.color_sub, relief="flat", font=("SF Pro Display", 9, "bold"))

    def _play_sound(self, sound_path):
        try: subprocess.Popen(["afplay", sound_path])
        except: pass

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg=self.color_bg)
        header_frame.pack(fill="x", padx=30, pady=(25, 10))
        self.header_status = tk.Label(header_frame, text="● SYSTEM ONLINE", bg=self.color_bg, fg=self.color_accent, font=("SF Pro Display", 10, "bold"))
        self.header_status.pack(side="left")

        briefing_box = tk.Frame(self.root, bg=self.color_bg, highlightthickness=1, highlightbackground=self.color_border)
        briefing_box.pack(fill="x", padx=30, pady=10, ipady=10)

        tk.Label(briefing_box, text="OBJECTIVE", bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 8, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.task_entry = tk.Entry(briefing_box, font=("Hiragino Kaku Gothic ProN", 13), bg=self.color_input_bg, fg=self.color_text, bd=0, insertbackground=self.color_accent, highlightthickness=1, highlightbackground="#253039", highlightcolor=self.color_accent, justify="center")
        self.task_entry.pack(pady=(5, 10), padx=15, fill="x", ipady=5)

        tk.Label(briefing_box, text="CLASSIFICATION", bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 8, "bold")).pack(anchor="w", padx=15)
        self.tag_var = tk.StringVar()
        # タグを英語に統一
        self.tag_combo = ttk.Combobox(briefing_box, textvariable=self.tag_var, values=["LECTURE", "ASSIGNMENT", "SELF-STUDY", "READING", "MEETING", "PROJECT"], font=("SF Pro Display", 11))
        self.tag_combo.pack(pady=(5, 0), padx=15, fill="x")
        self.tag_combo.set("SELF-STUDY")

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

        self.btn_up = tk.Button(self.mode_container, text="COUNT UP", command=lambda: self.set_mode("up"), bg=self.color_active_btn, fg=self.color_accent, font=("SF Pro Display", 9, "bold"), relief="flat", bd=0, width=12, height=1)
        self.btn_up.pack(side="left")
        self.btn_down = tk.Button(self.mode_container, text="COUNT DOWN", command=lambda: self.set_mode("down"), bg=self.color_input_bg, fg=self.color_sub, font=("SF Pro Display", 9, "bold"), relief="flat", bd=0, width=12, height=1)
        self.btn_down.pack(side="left")

        target_container = tk.Frame(param_frame, bg=self.color_input_bg, highlightthickness=1, highlightbackground=self.color_border)
        target_container.pack(side="right")
        self.target_entry = tk.Entry(target_container, font=("SF Mono", 12, "bold"), width=4, bg=self.color_input_bg, fg=self.color_accent, bd=0, justify="center")
        self.target_entry.insert(0, "25")
        self.target_entry.pack(side="left", padx=5, pady=5)
        tk.Label(target_container, text="MIN", bg=self.color_input_bg, fg=self.color_sub, font=("SF Pro Display", 7)).pack(side="left", padx=(0, 8))

        self.timer_frame = tk.Frame(self.root, bg=self.color_bg, bd=1, highlightthickness=1, highlightbackground=self.color_accent)
        self.timer_frame.pack(pady=20, padx=30, fill="x")
        self.label_display = tk.Label(self.timer_frame, text="00:00:00", font=("SF Mono", 48, "bold"), bg=self.color_bg, fg=self.color_accent)
        self.label_display.pack(pady=15)

        self.btn_main = tk.Button(self.root, text="INITIATE SESSION", command=self.start_timer, bg=self.color_accent, fg=self.color_bg, font=("SF Pro Display", 12, "bold"), relief="flat", height=2, bd=0)
        self.btn_main.pack(fill="x", padx=30, pady=5)

        # Dashboard Button
        self.btn_dashboard = tk.Button(self.root, text="SYSTEM ANALYTICS & LOGS", command=self.open_dashboard, bg=self.color_bg, fg=self.color_sub, font=("SF Pro Display", 9), relief="flat", bd=0)
        self.btn_dashboard.pack(pady=10)

        self.action_frame = tk.Frame(self.root, bg=self.color_bg)
        self.btn_abort = tk.Button(self.action_frame, text="ABORT", command=self.abort_session, bg=self.color_bg, fg=self.color_alert, font=("SF Pro Display", 10, "bold"), relief="flat", highlightthickness=1, highlightbackground=self.color_alert, width=12, height=2)
        self.btn_abort.pack(side="left", padx=(0, 5), expand=True, fill="x")
        self.btn_complete = tk.Button(self.action_frame, text="COMPLETE & ARCHIVE", command=self.complete_session, bg=self.color_accent, fg=self.color_bg, font=("SF Pro Display", 10, "bold"), relief="flat", width=22, height=2)
        self.btn_complete.pack(side="right", padx=(5, 0), expand=True, fill="x")

    def open_dashboard(self):
        self._play_sound(self.snd_click)
        dash_win = tk.Toplevel(self.root)
        JarvisDashboard(dash_win, self.csv_file, self.color_bg, self.color_accent, self.color_sub, self.color_input_bg, self.color_text)

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
            val = int(self.target_entry.get()); self.target_seconds = val * 60
        except: return
        self._play_sound(self.snd_start)
        self.is_running = True; self.start_time = time.time(); self.notified = False
        self.btn_main.pack_forget(); self.btn_dashboard.pack_forget()
        self.action_frame.pack(fill="x", padx=30, pady=10)
        self.task_entry.config(state="disabled"); self.tag_combo.config(state="disabled"); self.target_entry.config(state="disabled")
        self.header_status.config(text="● MISSION IN PROGRESS", fg=self.color_accent)
        self.update_timer()

    def update_timer(self):
        if self.is_running:
            total_elapsed = time.time() - self.start_time
            display_sec = total_elapsed
            color = self.color_accent
            if self.mode_var.get() == "down":
                if total_elapsed < self.target_seconds: display_sec = self.target_seconds - total_elapsed
                else:
                    display_sec = total_elapsed - self.target_seconds; color = self.color_alert
                    if not self.notified: self._trigger_alarm("LIMIT EXCEEDED")
            else:
                if total_elapsed >= self.target_seconds:
                    color = "#FFD700"
                    if not self.notified: self._trigger_alarm("GOAL REACHED")
            self.label_display.config(text=self.format_time(display_sec), fg=color)
            self.timer_frame.config(highlightbackground=color)
            self.root.after(100, self.update_timer)

    def _trigger_alarm(self, msg):
        self.notified = True; self._play_sound(self.snd_alarm)
        self.header_status.config(text=f"● {msg}", fg=self.color_alert)

    def format_time(self, seconds):
        s = int(seconds)
        return f"{s // 3600:02}:{(s % 3600) // 60:02}:{s % 60:02}"

    def complete_session(self):
        if messagebox.askyesno("COMPLETE", "セッションを終了し、データを記録しますか？"):
            self.is_running = False; self.save_to_csv(); self.reset_ui()

    def abort_session(self):
        if messagebox.askretrycancel("WARNING", "作戦を中止しますか？"):
            self.is_running = False; self.reset_ui()

    def save_to_csv(self):
        total_duration = int(time.time() - self.start_time)
        now = datetime.now()
        if not os.path.exists(self.log_dir): os.makedirs(self.log_dir)
        fieldnames = ["task", "tag", "date", "start_at", "duration", "duration_sec", "mode", "timestamp"]
        with open(self.csv_file, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not os.path.isfile(self.csv_file) or os.path.getsize(self.csv_file) == 0: writer.writeheader()
            writer.writerow({
                "task": self.task_entry.get().strip() or "UNDEFINED",
                "tag": self.tag_var.get().strip(),
                "date": now.strftime("%Y-%m-%d"),
                "start_at": now.strftime("%H:%M:%S"),
                "duration": self.format_time(total_duration),
                "duration_sec": total_duration,
                "mode": self.mode_var.get().upper(),
                "timestamp": time.time()
            })

    def reset_ui(self):
        self.label_display.config(text="00:00:00", fg=self.color_accent); self.timer_frame.config(highlightbackground=self.color_accent)
        self.action_frame.pack_forget(); self.btn_main.pack(fill="x", padx=30, pady=5); self.btn_dashboard.pack(pady=10)
        self.task_entry.config(state="normal"); self.tag_combo.config(state="normal"); self.target_entry.config(state="normal")
        self.task_entry.delete(0, tk.END); self.header_status.config(text="● SYSTEM ONLINE", fg=self.color_accent)

    def on_closing(self): self.root.destroy()

# --- DASHBOARD & BEAUTIFUL LOGS ---
class JarvisDashboard:
    def __init__(self, window, csv_file, bg, accent, sub, card, text_color):
        self.window = window
        self.window.title("MARK FOCUS : ANALYTICS & LOGS")
        self.window.geometry("1000x750")
        self.window.configure(bg=bg)
        self.csv_file = csv_file
        self.colors = {"bg": bg, "accent": accent, "sub": sub, "card": card, "text": text_color}
        
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # Navigation
        nav = tk.Frame(self.window, bg=self.colors["bg"])
        nav.pack(fill="x", padx=30, pady=20)
        tk.Label(nav, text="📊 SYSTEM ANALYTICS", font=("SF Pro Display", 18, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(side="left")

        # Tabs (Analytics / Logs)
        tab_control = ttk.Notebook(self.window)
        self.tab_analytics = tk.Frame(tab_control, bg=self.colors["bg"])
        self.tab_logs = tk.Frame(tab_control, bg=self.colors["bg"])
        tab_control.add(self.tab_analytics, text="  ANALYTICS  ")
        tab_control.add(self.tab_logs, text="  SESSION LOGS  ")
        tab_control.pack(expand=1, fill="both", padx=30)

        # --- Analytics Tab Setup ---
        self.setup_analytics_tab()
        
        # --- Logs Tab Setup ---
        self.setup_logs_tab()

    def setup_analytics_tab(self):
        filter_frame = tk.Frame(self.tab_analytics, bg=self.colors["card"], padx=15, pady=10)
        filter_frame.pack(fill="x", pady=10)
        
        tk.Label(filter_frame, text="YEAR FILTER:", bg=self.colors["card"], fg=self.colors["sub"], font=("SF Pro", 8, "bold")).pack(side="left", padx=5)
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var, state="readonly", width=10)
        self.year_combo.pack(side="left", padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        self.kpi_frame = tk.Frame(self.tab_analytics, bg=self.colors["bg"])
        self.kpi_frame.pack(fill="x", pady=10)
        self.graph_frame = tk.Frame(self.tab_analytics, bg=self.colors["bg"])
        self.graph_frame.pack(fill="both", expand=True)

    def setup_logs_tab(self):
        # Beautiful Treeview for Logs
        log_container = tk.Frame(self.tab_logs, bg=self.colors["bg"])
        log_container.pack(fill="both", expand=True, pady=20)

        columns = ("date", "start", "task", "tag", "duration")
        self.tree = ttk.Treeview(log_container, columns=columns, show="headings")
        
        # Headings
        self.tree.heading("date", text="DATE")
        self.tree.heading("start", text="START")
        self.tree.heading("task", text="OBJECTIVE (TASK NAME)")
        self.tree.heading("tag", text="TAG")
        self.tree.heading("duration", text="DURATION")

        # Column Widths
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("start", width=80, anchor="center")
        self.tree.column("task", width=350, anchor="w")
        self.tree.column("tag", width=120, anchor="center")
        self.tree.column("duration", width=100, anchor="center")

        # Scrollbar
        scroller = ttk.Scrollbar(log_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroller.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroller.pack(side="right", fill="y")

    def refresh_data(self):
        if not os.path.exists(self.csv_file): return
        data = []
        with open(self.csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['duration_sec'] = int(row['duration_sec'])
                data.append(row)
        
        # Update Year Combobox
        years = sorted(list(set(r['date'].split('-')[0] for r in data)), reverse=True)
        self.year_combo['values'] = years

        # Filter Data
        sel_year = self.year_var.get()
        filtered = [d for d in data if d['date'].startswith(sel_year)]

        # --- Update Analytics ---
        for w in self.kpi_frame.winfo_children(): w.destroy()
        total_hrs = sum(d['duration_sec'] for d in filtered)/3600
        self.create_kpi(self.kpi_frame, "YEAR TOTAL", f"{total_hrs:.1f} hrs")
        self.create_kpi(self.kpi_frame, "SESSIONS", f"{len(filtered)}")
        
        for w in self.graph_frame.winfo_children(): w.destroy()
        if HAS_MATPLOTLIB and filtered: self.draw_graphs(filtered, sel_year)

        # --- Update Beautiful Logs (Japanese Support) ---
        for item in self.tree.get_children(): self.tree.delete(item)
        # 逆順で表示（新しいものが上）
        for d in reversed(data):
            self.tree.insert("", "end", values=(d['date'], d['start_at'], d['task'], d['tag'], d['duration']))

    def draw_graphs(self, data, year):
        plt.rcParams['text.color'] = self.colors["text"]
        plt.rcParams['axes.labelcolor'] = self.colors["text"]
        plt.rcParams['xtick.color'] = self.colors["sub"]
        plt.rcParams['ytick.color'] = self.colors["sub"]

        fig = plt.figure(figsize=(8, 4), facecolor=self.colors["bg"])
        
        # Monthly Bar
        month_data = {m: 0 for m in range(1, 13)}
        for d in data: month_data[int(d['date'].split('-')[1])] += d['duration_sec']
        
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.bar(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 
                [month_data[m]/3600 for m in range(1, 13)], color=self.colors["accent"], alpha=0.6)
        ax1.set_title(f"MONTHLY HOURS ({year})", fontsize=10, fontweight='bold')
        ax1.set_facecolor(self.colors["bg"])

        # Tags Bar (Strictly English Tags)
        tag_dict = {}
        for d in data: tag_dict[d['tag']] = tag_dict.get(d['tag'], 0) + d['duration_sec']
        
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.bar(list(tag_dict.keys()), [v/60 for v in tag_dict.values()], color="#1A3A4A", edgecolor=self.colors["accent"])
        ax2.set_title("MINS BY CLASSIFICATION", fontsize=10, fontweight='bold')
        ax2.set_facecolor(self.colors["bg"])
        plt.xticks(rotation=45, fontsize=8)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_kpi(self, parent, label, val):
        f = tk.Frame(parent, bg=self.colors["card"], highlightthickness=1, highlightbackground=self.colors["sub"])
        f.pack(side="left", fill="both", expand=True, padx=5, ipady=5)
        tk.Label(f, text=label, bg=self.colors["card"], fg=self.colors["sub"], font=("Arial", 7, "bold")).pack()
        tk.Label(f, text=val, bg=self.colors["card"], fg=self.colors["accent"], font=("Arial", 14, "bold")).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisSystemV2(root)
    root.mainloop()
