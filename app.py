import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import sys
import json
import os
import signal
from config import load_config, save_config

class MLBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💎 Mobile Legends Diamond Bot")
        self.root.geometry("700x500")
        self.bot_process = None
        self.config_data = load_config()

        self.tab_control = ttk.Notebook(root)
        self.bot_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.bot_tab, text="🤖 Bot Control")
        self.tab_control.add(self.settings_tab, text="⚙ Settings")
        self.tab_control.pack(expand=1, fill='both')

        self.create_bot_tab()
        self.create_settings_tab()

    def create_bot_tab(self):
        frame = self.bot_tab
        self.status_label = tk.Label(frame, text="🔴 Bot Status: Stopped", fg="red", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)

        btn_frame = tk.Frame(frame)
        btn_frame.pack()

        self.start_btn = tk.Button(btn_frame, text="▶ Start Bot", command=self.start_bot, width=15, bg="#4CAF50", fg="white")
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = tk.Button(btn_frame, text="⏹ Stop Bot", command=self.stop_bot, width=15, bg="#f44336", fg="white", state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=10)

        self.log_area = ScrolledText(frame, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED)
        self.log_area.pack(pady=10)

    def create_settings_tab(self):
        frame = self.settings_tab

        tk.Label(frame, text="BOT Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.token_entry = tk.Entry(frame, width=60)
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Admin ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.admin_entry = tk.Entry(frame, width=60)
        self.admin_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Payment Info:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.payment_entry = tk.Entry(frame, width=60)
        self.payment_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Order Channel URL:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.channel_entry = tk.Entry(frame, width=60)
        self.channel_entry.grid(row=3, column=1, padx=5, pady=5)

        self.save_btn = tk.Button(frame, text="💾 Save & Restart Bot", bg="#2196F3", fg="white", command=self.save_and_restart)
        self.save_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.load_settings()

    def load_settings(self):
        self.token_entry.insert(0, self.config_data['BOT_TOKEN'])
        self.admin_entry.insert(0, self.config_data['ADMIN_ID'])
        self.payment_entry.insert(0, self.config_data['PAYMENT_INFO'])
        self.channel_entry.insert(0, self.config_data['ORDER_CHANNEL'])

    def save_and_restart(self):
        self.config_data['BOT_TOKEN'] = self.token_entry.get()
        self.config_data['ADMIN_ID'] = int(self.admin_entry.get())
        self.config_data['PAYMENT_INFO'] = self.payment_entry.get()
        self.config_data['ORDER_CHANNEL'] = self.channel_entry.get()
        save_config(self.config_data)
        messagebox.showinfo("Saved", "✅ Config saved successfully. Restarting bot...")
        self.stop_bot()
        self.start_bot()

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def start_bot(self):
        if self.bot_process is None:
            self.log("🚀 Starting bot...")
            self.bot_process = subprocess.Popen([sys.executable, "bot.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.status_label.config(text="🟢 Bot Status: Running", fg="green")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            threading.Thread(target=self.read_output, daemon=True).start()

    def stop_bot(self):
        if self.bot_process:
            self.log("⏹ Stopping bot...")
            self.bot_process.terminate()
            self.bot_process.wait()
            self.bot_process = None
            self.status_label.config(text="🔴 Bot Status: Stopped", fg="red")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def read_output(self):
        try:
            for line in self.bot_process.stdout:
                self.log("📥 " + line.strip())
            for line in self.bot_process.stderr:
                self.log("❗ " + line.strip())
        except:
            pass

    def on_close(self):
        if self.bot_process:
            self.stop_bot()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MLBotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
