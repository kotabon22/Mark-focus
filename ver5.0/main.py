# -*- coding: utf-8 -*-
import time
import sys
import csv
import os
from datetime import datetime
import tkinter as tk

# --- SETTINGS ---
LOG_DIR = os.path.expanduser("~/Documents/MarkFocus")
LOG_FILE = os.path.join(LOG_DIR, "study_log.csv")
TASK_FILE = os.path.join(LOG_DIR, "task_queue.csv")

# Jarvis Colors (Terminal)
CYAN = "\033[36m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"

TAGS = ["CLASS", "ASSIGNMENT", "LAB", "RESEARCH", "SELF-STUDY", "MEETING", "PROJECT"]

class MiniHUD:
    """浮遊する小窓タイマー"""
    def __init__(self, target_sec):
        self.root = tk.Tk()
        self.root.title("CORE")
        self.root.geometry("180x60+50+50") # 左上に出現
        self.root.overrideredirect(True) # 枠なし
        self.root.attributes("-topmost", True) # 常に最前面
        self.root.configure(bg="#0A0F14", highlightthickness=1, highlightbackground="#00F5FF")
        
        self.lbl = tk.Label(self.root, text="00:00:00", bg="#0A0F14", fg="#00F5FF", font=("Courier", 24, "bold"))
        self.lbl.pack(expand=True)
        
        # ドラッグ移動可能にする
        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._drag_motion)

    def _start_drag(self, e):
        self.x = e.x
        self.y = e.y

    def _drag_motion(self, e):
        x = self.root.winfo_x() - self.x + e.x
        y = self.root.winfo_y() - self.y + e.y
        self.root.geometry(f"+{x}+{y}")

    def update(self, time_str, is_over):
        color = "#FF3B30" if is_over else "#00F5FF"
        self.lbl.config(text=time_str, fg=color)
        self.root.update()

    def close(self):
        self.root.destroy()

def setup_env():
    if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

def load_tasks():
    if not os.path.exists(TASK_FILE): return []
    with open(TASK_FILE, "r", encoding="utf-8-sig") as f:
        return [row for row in csv.reader(f) if row]

def save_tasks(tasks):
    with open(TASK_FILE, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(tasks)

def run_timer(objective, tag, target_min):
    target_sec = target_min * 60
    start_time = time.time()
    start_at = datetime.now().strftime("%H:%M:%S")
    
    # 小窓の生成
    hud = MiniHUD(target_sec)
    
    print(f"\n{GREEN}● MISSION INITIATED{RESET}")
    print(f"OBJECTIVE: {BOLD}{objective}{RESET}")
    print(f"{YELLOW}Press Ctrl+C in this terminal to FINISH{RESET}\n")

    try:
        while True:
            elapsed = time.time() - start_time
            is_over = elapsed >= target_sec
            
            sec = target_sec - elapsed if not is_over else elapsed - target_sec
            color = CYAN if not is_over else RED
            
            mins, secs = divmod(int(sec), 60)
            hours, mins = divmod(mins, 60)
            t_str = f"{hours:02}:{mins:02}:{secs:02}"

            # ターミナル更新
            sys.stdout.write(f"\r {color}{BOLD}[ {t_str} ]{RESET} | {objective}    ")
            sys.stdout.flush()
            
            # 小窓更新
            hud.update(t_str, is_over)
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        hud.close()
        return handle_end(objective, tag, start_time, start_at)

def handle_end(objective, tag, start_time, start_at):
    print(f"\n\n{YELLOW}{BOLD}=== MISSION CONTROL ==={RESET}")
    print(f" {GREEN}[c]{RESET} Archive  {RED}[a]{RESET} Abort  {CYAN}[r]{RESET} Resume")
    while True:
        cmd = input("Choice: ").lower()
        if cmd == 'c':
            save_log(objective, tag, start_time, start_at)
            return True
        elif cmd == 'a':
            return False
        elif cmd == 'r':
            # 再開（実際には再帰的にタイマーを呼ぶ）
            # 本来は累積時間を渡すべきですが簡易化のためリスタート
            return run_timer(objective, tag, 1) # 再開処理は必要に応じて調整

def save_log(objective, tag, start_time, start_at):
    dur_sec = int(time.time() - start_time)
    mins, secs = divmod(dur_sec, 60)
    hours, mins = divmod(mins, 60)
    t_str = f"{hours:02}:{mins:02}:{secs:02}"

    with open(LOG_FILE, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["task", "tag", "date", "start_at", "duration", "duration_sec", "mode", "timestamp"])
        if os.path.getsize(LOG_FILE) == 0: writer.writeheader()
        writer.writerow({"task": objective, "tag": tag, "date": datetime.now().strftime("%Y-%m-%d"), "start_at": start_at, "duration": t_str, "duration_sec": dur_sec, "mode": "CLI+HUD", "timestamp": time.time()})
    print(f"{GREEN}✔ ARCHIVED: {t_str}{RESET}")
    time.sleep(1)

def main_menu():
    while True:
        os.system('clear')
        tasks = load_tasks()
        print(f"{CYAN}{BOLD}=== MARK FOCUS : COMMAND CENTER ==={RESET}")
        for i, t in enumerate(tasks, 1):
            print(f" {BOLD}{i:02}:{RESET} {t[2]:<20} {YELLOW}[{t[1]}] {CYAN}{t[0]}m{RESET}")
        print("-" * 40)
        print(f" {GREEN}[s ID]{RESET} Start  {CYAN}[a]{RESET} Add  {RED}[r ID]{RESET} Remove  {DIM}[q]{RESET} Quit")
        
        try:
            line = input(f"\n{BOLD}>>{RESET} ").lower().split()
            if not line: continue
            cmd = line[0]
            if cmd == 's':
                idx = int(line[1])-1 if len(line)>1 else 0
                t = tasks.pop(idx)
                if run_timer(t[2], t[1], int(t[0])): tasks.append(t)
                else: tasks.insert(idx, t)
                save_tasks(tasks)
            elif cmd == 'a':
                name = input("Name: ")
                print(f"Tags: {', '.join(TAGS)}")
                tag = input("Tag: ") or "SELF-STUDY"
                tasks.append([input("Min: ") or "25", tag.upper(), name])
                save_tasks(tasks)
            elif cmd == 'r':
                tasks.pop(int(line[1])-1); save_tasks(tasks)
            elif cmd == 'q': break
        except: pass

if __name__ == "__main__":
    setup_env()
    main_menu()
