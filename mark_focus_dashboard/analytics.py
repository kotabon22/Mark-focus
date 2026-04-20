# -*- coding: utf-8 -*-
import os
import sys

# --- macOSのバージョン誤認バグを回避する設定 ---
import matplotlib
matplotlib.use('TkAgg') # 強制的にTkinter用バックエンドを使用
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class JarvisDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("MARK FOCUS : ANALYTICS SYSTEM")
        self.root.geometry("1000x750")
        
        # Jarvis Color Palette
        self.color_bg = "#0A0F14"
        self.color_accent = "#00F5FF"
        self.color_sub = "#506070"
        self.color_card = "#12181F"
        self.color_text = "#E0E0E0"
        self.color_active_btn = "#1A3A4A"

        self.root.configure(bg=self.color_bg)

        # パス設定
        self.log_dir = os.path.expanduser("~/Documents/MarkFocus")
        self.csv_file = os.path.join(self.log_dir, "study_log.csv")

        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        # --- HEADER ---
        header = tk.Frame(self.root, bg=self.color_bg)
        header.pack(fill="x", padx=30, pady=20)
        
        tk.Label(header, text="📊 ANALYTICS DASHBOARD", font=("Hiragino Kaku Gothic ProN", 18, "bold"),
                 bg=self.color_bg, fg=self.color_accent).pack(side="left")
        
        tk.Button(header, text="REFRESH SYSTEM", command=self.refresh_data,
                  bg=self.color_active_btn, fg=self.color_accent, 
                  relief="flat", font=("Hiragino Kaku Gothic ProN", 9)).pack(side="right")

        # --- FILTER BAR ---
        filter_frame = tk.Frame(self.root, bg=self.color_card, padx=20, pady=15)
        filter_frame.pack(fill="x", padx=30, pady=10)

        tk.Label(filter_frame, text="TAG:", bg=self.color_card, fg=self.color_sub, font=("Arial", 8, "bold")).grid(row=0, column=0, padx=5)
        self.tag_var = tk.StringVar(value="ALL")
        self.tag_combo = ttk.Combobox(filter_frame, textvariable=self.tag_var, state="readonly", width=15)
        self.tag_combo.grid(row=0, column=1, padx=10)
        self.tag_combo.bind("<<ComboboxSelected>>", lambda e: self.update_display())

        tk.Label(filter_frame, text="SEARCH:", bg=self.color_card, fg=self.color_sub, font=("Arial", 8, "bold")).grid(row=0, column=2, padx=5)
        self.search_entry = tk.Entry(filter_frame, bg=self.color_bg, fg=self.color_text, insertbackground=self.color_accent, bd=0, width=25)
        self.search_entry.grid(row=0, column=3, padx=10, ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_display())

        # --- KPI CARDS ---
        kpi_frame = tk.Frame(self.root, bg=self.color_bg)
        kpi_frame.pack(fill="x", padx=30, pady=10)

        self.kpi_total = self.create_kpi_card(kpi_frame, "TOTAL STUDY TIME", "0.0 hrs")
        self.kpi_count = self.create_kpi_card(kpi_frame, "SESSIONS", "0")
        self.kpi_avg = self.create_kpi_card(kpi_frame, "AVG SESSION", "0 min")

        # --- GRAPH AREA ---
        self.graph_frame = tk.Frame(self.root, bg=self.color_bg)
        self.graph_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def create_kpi_card(self, parent, label, value):
        card = tk.Frame(parent, bg=self.color_card, highlightthickness=1, highlightbackground=self.color_sub)
        card.pack(side="left", fill="both", expand=True, padx=5, ipady=10)
        
        tk.Label(card, text=label, bg=self.color_card, fg=self.color_sub, font=("Arial", 8, "bold")).pack(pady=(10,0))
        val_label = tk.Label(card, text=value, bg=self.color_card, fg=self.color_accent, font=("Arial", 18, "bold"))
        val_label.pack(pady=5)
        return val_label

    def refresh_data(self):
        if not os.path.exists(self.csv_file):
            return

        try:
            self.df = pd.read_csv(self.csv_file, encoding='utf-8-sig')
            self.df['date'] = pd.to_datetime(self.df['date'])
            tags = ["ALL"] + sorted(self.df['tag'].dropna().unique().tolist())
            self.tag_combo['values'] = tags
            self.update_display()
        except Exception as e:
            print(f"Error loading data: {e}")

    def update_display(self):
        if not hasattr(self, 'df'): return
        
        f_df = self.df.copy()
        if self.tag_var.get() != "ALL":
            f_df = f_df[f_df['tag'] == self.tag_var.get()]
        
        search = self.search_entry.get().strip()
        if search:
            f_df = f_df[f_df['task'].astype(str).str.contains(search, case=False)]

        total_sec = f_df['duration_sec'].sum()
        self.kpi_total.config(text=f"{total_sec / 3600:.1f} hrs")
        self.kpi_count.config(text=f"{len(f_df)}")
        avg_min = (total_sec / len(f_df) / 60) if len(f_df) > 0 else 0
        self.kpi_avg.config(text=f"{avg_min:.1f} min")

        self.draw_graphs(f_df)

    def draw_graphs(self, data):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if data.empty: return

        # スタイル適用
        plt.rcParams['text.color'] = self.color_text
        plt.rcParams['axes.labelcolor'] = self.color_text
        plt.rcParams['xtick.color'] = self.color_sub
        plt.rcParams['ytick.color'] = self.color_sub

        fig = plt.figure(figsize=(10, 4), facecolor=self.color_bg)
        
        # 日別
        ax1 = fig.add_subplot(1, 2, 1)
        daily = data.groupby('date')['duration_sec'].sum() / 3600
        ax1.plot(daily.index, daily.values, color=self.color_accent, marker='o', linewidth=2)
        ax1.set_title("DAILY ACTIVITY (HOURS)", fontsize=10)
        ax1.set_facecolor(self.color_bg)

        # タグ別
        ax2 = fig.add_subplot(1, 2, 2)
        tag_dist = data.groupby('tag')['duration_sec'].sum() / 60
        tag_dist.plot(kind='bar', ax=ax2, color=self.color_active_btn, edgecolor=self.color_accent)
        ax2.set_title("TIME BY TAG (MINUTES)", fontsize=10)
        ax2.set_facecolor(self.color_bg)
        plt.xticks(rotation=45)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisDashboard(root)
    root.mainloop()
