"""
Synent Technologies – Python Development Internship
Task 2: Number Guessing Game (GUI)
Author: dev
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math

# ── Palette ──────────────────────────────────────────────────────────────
BG      = "#080818"
PANEL   = "#0e0e24"
CARD    = "#14142e"
GOLD    = "#ffd700"
CYAN    = "#00e5ff"
GREEN   = "#39ff14"
RED     = "#ff3355"
PURPLE  = "#bf5fff"
TEXT    = "#e8e8ff"
SUBTEXT = "#5a5a8a"
# ─────────────────────────────────────────────────────────────────────────

DIFFICULTY = {
    "Easy":   (1, 50,  10),
    "Medium": (1, 100, 7),
    "Hard":   (1, 200, 5),
}


class GuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Synent Number Quest")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self._setup_window()
        self._init_game_state()
        self._build_ui()
        self._animate_title(0)

    def _setup_window(self):
        w, h = 480, 680
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _init_game_state(self):
        self.difficulty = "Medium"
        self.secret = None
        self.attempts = 0
        self.max_attempts = 0
        self.game_active = False
        self.history = []

    def _build_ui(self):
        # ── Animated Header ──────────────────────────────────────
        self.hdr_frame = tk.Frame(self.root, bg=PANEL, pady=18)
        self.hdr_frame.pack(fill="x")

        self.title_lbl = tk.Label(
            self.hdr_frame, text="◈ NUMBER QUEST",
            bg=PANEL, fg=GOLD,
            font=("Courier New", 22, "bold"))
        self.title_lbl.pack()
        tk.Label(self.hdr_frame, text="Synent Technologies  •  Guessing Game",
                 bg=PANEL, fg=SUBTEXT,
                 font=("Courier New", 9)).pack()

        # ── Difficulty ───────────────────────────────────────────
        diff_frame = tk.Frame(self.root, bg=BG, pady=10)
        diff_frame.pack()
        tk.Label(diff_frame, text="DIFFICULTY", bg=BG, fg=SUBTEXT,
                 font=("Courier New", 10, "bold")).pack()
        btn_row = tk.Frame(diff_frame, bg=BG)
        btn_row.pack(pady=6)
        self.diff_var = tk.StringVar(value="Medium")
        colors = {"Easy": GREEN, "Medium": GOLD, "Hard": RED}
        for d in ["Easy", "Medium", "Hard"]:
            rb = tk.Radiobutton(
                btn_row, text=d, variable=self.diff_var, value=d,
                bg=BG, fg=colors[d], selectcolor=CARD,
                activebackground=BG,
                font=("Courier New", 12, "bold"),
                command=self._on_diff_change)
            rb.pack(side="left", padx=14)

        # ── Range Display ────────────────────────────────────────
        self.range_var = tk.StringVar(value="Range: 1 – 100  |  Attempts: 7")
        tk.Label(self.root, textvariable=self.range_var,
                 bg=BG, fg=SUBTEXT,
                 font=("Courier New", 10)).pack(pady=(0, 6))

        # ── Mystery number display ───────────────────────────────
        mystery_frame = tk.Frame(self.root, bg=CARD,
                                 highlightbackground=PURPLE,
                                 highlightthickness=2)
        mystery_frame.pack(padx=30, pady=8, fill="x")
        self.mystery_lbl = tk.Label(
            mystery_frame, text="?",
            bg=CARD, fg=PURPLE,
            font=("Courier New", 72, "bold"))
        self.mystery_lbl.pack(pady=10)

        # ── Hint feedback ────────────────────────────────────────
        self.hint_var = tk.StringVar(value="Press START to begin!")
        self.hint_lbl = tk.Label(
            self.root, textvariable=self.hint_var,
            bg=BG, fg=CYAN,
            font=("Courier New", 15, "bold"), pady=4)
        self.hint_lbl.pack()

        # ── Attempts meter ───────────────────────────────────────
        meter_frame = tk.Frame(self.root, bg=BG)
        meter_frame.pack(fill="x", padx=30, pady=6)
        self.meter_canvas = tk.Canvas(meter_frame, bg=BG, bd=0,
                                      highlightthickness=0,
                                      height=12, width=420)
        self.meter_canvas.pack()
        self.attempts_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.attempts_var,
                 bg=BG, fg=SUBTEXT,
                 font=("Courier New", 10)).pack()

        # ── Input row ────────────────────────────────────────────
        inp_frame = tk.Frame(self.root, bg=PANEL, padx=20, pady=14)
        inp_frame.pack(fill="x", padx=30, pady=8)
        self.guess_entry = tk.Entry(
            inp_frame, bg=CARD, fg=TEXT,
            insertbackground=CYAN,
            font=("Courier New", 20, "bold"),
            bd=0, relief="flat", width=10, justify="center",
            state="disabled"
        )
        self.guess_entry.pack(side="left", padx=(0, 10), ipady=8)
        self.guess_entry.bind("<Return>", lambda e: self._submit_guess())

        self.submit_btn = tk.Button(
            inp_frame, text="GUESS ▶",
            bg=CYAN, fg=BG,
            font=("Courier New", 12, "bold"),
            bd=0, relief="flat", padx=14, pady=8,
            cursor="hand2", state="disabled",
            command=self._submit_guess)
        self.submit_btn.pack(side="left")

        # ── Start / Restart ──────────────────────────────────────
        self.start_btn = tk.Button(
            self.root, text="⚡ START GAME",
            bg=GOLD, fg=BG,
            font=("Courier New", 14, "bold"),
            bd=0, relief="flat", pady=12,
            cursor="hand2",
            command=self._start_game)
        self.start_btn.pack(fill="x", padx=30, pady=8)

        # ── History ──────────────────────────────────────────────
        tk.Label(self.root, text="GUESS HISTORY",
                 bg=BG, fg=SUBTEXT,
                 font=("Courier New", 9, "bold")).pack(anchor="w",
                                                        padx=30)
        self.hist_frame = tk.Frame(self.root, bg=BG)
        self.hist_frame.pack(fill="x", padx=30, pady=4)

    def _on_diff_change(self):
        d = self.diff_var.get()
        lo, hi, mx = DIFFICULTY[d]
        self.range_var.set(f"Range: {lo} – {hi}  |  Attempts: {mx}")

    def _start_game(self):
        d = self.diff_var.get()
        lo, hi, mx = DIFFICULTY[d]
        self.secret = random.randint(lo, hi)
        self.attempts = 0
        self.max_attempts = mx
        self.game_active = True
        self.history = []

        self.mystery_lbl.config(text="?", fg=PURPLE)
        self.hint_var.set(f"Guess a number between {lo} and {hi}!")
        self.hint_lbl.config(fg=CYAN)
        self.guess_entry.config(state="normal")
        self.guess_entry.delete(0, "end")
        self.submit_btn.config(state="normal")
        self.start_btn.config(text="🔄 RESTART", bg=PANEL, fg=GOLD)
        self._update_meter()
        self._clear_history()

    def _submit_guess(self):
        if not self.game_active:
            return
        raw = self.guess_entry.get().strip()
        try:
            guess = int(raw)
        except ValueError:
            self.hint_var.set("⚠ Enter a valid number!")
            self.hint_lbl.config(fg=RED)
            return

        d = self.diff_var.get()
        lo, hi, _ = DIFFICULTY[d]
        if not (lo <= guess <= hi):
            self.hint_var.set(f"⚠ Enter a number between {lo} and {hi}!")
            self.hint_lbl.config(fg=RED)
            return

        self.attempts += 1
        self.guess_entry.delete(0, "end")

        if guess == self.secret:
            self._win()
        elif self.attempts >= self.max_attempts:
            self._lose()
        else:
            remaining = self.max_attempts - self.attempts
            if guess < self.secret:
                diff = self.secret - guess
                heat = "🥶 WAY TOO LOW" if diff > 20 else "⬆ Too Low"
                color = CYAN
            else:
                diff = guess - self.secret
                heat = "🔥 WAY TOO HIGH" if diff > 20 else "⬇ Too High"
                color = RED

            self.hint_var.set(f"{heat}  •  {remaining} attempts left")
            self.hint_lbl.config(fg=color)
            self._add_history(guess, "↑" if guess < self.secret else "↓", color)
            self._update_meter()

    def _win(self):
        self.game_active = False
        self.mystery_lbl.config(text=str(self.secret), fg=GREEN)
        self.hint_var.set(f"🎉 Correct! Found in {self.attempts} attempt(s)!")
        self.hint_lbl.config(fg=GREEN)
        self.guess_entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self._update_meter()
        self._add_history(self.secret, "✓", GREEN)
        self._flash_win()

    def _lose(self):
        self.game_active = False
        self.mystery_lbl.config(text=str(self.secret), fg=RED)
        self.hint_var.set(f"💀 Game Over! The number was {self.secret}")
        self.hint_lbl.config(fg=RED)
        self.guess_entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self._update_meter()

    def _update_meter(self):
        used = self.attempts
        total = self.max_attempts
        ratio = used / total if total else 0
        self.meter_canvas.delete("all")
        self.meter_canvas.create_rectangle(0, 0, 420, 12,
                                           fill="#1a1a2e", outline="")
        color = GREEN if ratio < 0.5 else GOLD if ratio < 0.8 else RED
        self.meter_canvas.create_rectangle(0, 0,
                                           int(420 * ratio), 12,
                                           fill=color, outline="")
        self.attempts_var.set(f"Attempts used: {used} / {total}")

    def _add_history(self, guess, sym, color):
        self.history.insert(0, (guess, sym, color))
        self._clear_history()
        for g, s, c in self.history[:6]:
            row = tk.Frame(self.hist_frame, bg=CARD, padx=8, pady=3)
            row.pack(side="left", padx=4)
            tk.Label(row, text=f"{s} {g}", bg=CARD, fg=c,
                     font=("Courier New", 11, "bold")).pack()

    def _clear_history(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()

    def _animate_title(self, step):
        colors = [GOLD, CYAN, PURPLE, GREEN, RED]
        self.title_lbl.config(fg=colors[step % len(colors)])
        self.root.after(800, self._animate_title, step + 1)

    def _flash_win(self, count=0):
        if count >= 6:
            self.mystery_lbl.config(fg=GREEN)
            return
        col = GREEN if count % 2 == 0 else GOLD
        self.mystery_lbl.config(fg=col)
        self.root.after(200, self._flash_win, count + 1)


if __name__ == "__main__":
    root = tk.Tk()
    app = GuessingGame(root)
    root.mainloop()
