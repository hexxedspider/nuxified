import customtkinter as ctk
import os
import subprocess
import sys
from dotenv import load_dotenv, set_key
import threading
import time
import requests
import datetime
import psutil
import platform
import webbrowser
import shutil
from PIL import Image, ImageDraw, ImageFont
import glob
import io

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ObfuscatedEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.real_value = ""
        self.show_char = "*"
        self.timer = None
        self.is_obfuscated = True
        
        self.bind("<Key>", self.on_key)
        self.bind("<BackSpace>", self.on_backspace)
        
    def on_key(self, event):
        if not self.is_obfuscated:
            return
            
        if event.char and event.char.isprintable():
            self.real_value += event.char
            self.configure(show="")
            self.delete(0, "end")
            self.insert(0, self.get_masked_display() + event.char)
            
            if self.timer:
                self.after_cancel(self.timer)
            self.timer = self.after(3000, self.mask_all)
            
            return "break"
            
    def on_backspace(self, event):
        if not self.is_obfuscated:
            return
            
        if self.real_value:
            self.real_value = self.real_value[:-1]
            self.mask_all()
        return "break"
        
    def mask_all(self):
        if not self.is_obfuscated:
            return
            
        self.configure(show=self.show_char)
        self.delete(0, "end")
        self.insert(0, self.real_value)
        
    def get_real(self):
        if not self.is_obfuscated:
            return self.get()
        return self.real_value
        
    def set_real(self, value):
        self.real_value = value
        if self.is_obfuscated:
            self.mask_all()
        else:
            self.delete(0, "end")
            self.insert(0, value)

    def get_masked_display(self):
        return self.show_char * len(self.real_value)

    def set_obfuscation_state(self, enabled):
        if self.is_obfuscated == enabled:
            return
            
        self.is_obfuscated = enabled
        if enabled:
            self.real_value = self.get()
            self.mask_all()
        else:
            self.configure(show="")
            self.delete(0, "end")
            self.insert(0, self.real_value)

class BotLauncher(ctk.CTk):
    def __init__(self):
        self.env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        self.envv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".envv")

        if not os.path.exists(self.env_path) and os.path.exists(self.envv_path):
            try:
                shutil.copy(self.envv_path, self.env_path)
                print(f"created .env from .envv")
            except Exception as e:
                print(f"error creating .env: {e}")

        super().__init__()

        self.title("Nuxified x Nukumoxy444: Nuxified Vision")
        self.geometry("900x600")
        self.resizable(True, True)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        load_dotenv(self.env_path)

        self.create_sidebar()
        self.create_main_area()
        self.viewing_logs = False
        self.show_dashboard()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Nuxified", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_logs = ctk.CTkButton(self.sidebar_frame, text="Live Logs", command=self.show_logs, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.sidebar_button_logs.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_button_terminal = ctk.CTkButton(self.sidebar_frame, text="Terminal", command=self.show_terminal, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.sidebar_button_terminal.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_info = ctk.CTkButton(self.sidebar_frame, text="Info", command=self.open_wiki, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.sidebar_button_info.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=7, column=0, padx=20, pady=20)

    def open_wiki(self):
        webbrowser.open("https://github.com/hexxedspider/nuxified/wiki")

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def clear_main_area(self):
        self.viewing_logs = False
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_area()
        
        title = ctk.CTkLabel(self.main_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        actions_frame = ctk.CTkFrame(self.main_frame)
        actions_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(actions_frame, text="Quick Actions", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)

        self.start_button = ctk.CTkButton(actions_frame, text="Start Bot", command=self.start_bot, fg_color="#333333", hover_color="#555555", height=40)
        self.start_button.pack(padx=15, pady=(0, 15), fill="x")
        
        self.stats_frame = ctk.CTkFrame(self.main_frame)
        self.stats_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.stats_frame, text="Account Stats", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        self.stats_labels = {}
        self.create_stat_label("Account Created", "Loading...")
        self.create_stat_label("Servers", "Loading...")
        self.create_stat_label("CPU Usage", "Loading...")
        self.create_stat_label("RAM Usage", "Loading...")
        self.create_stat_label("Latency", "Loading...")
        self.create_stat_label("Python Version", "Loading...")
        self.create_stat_label("Script Version", "Loading...")

        threading.Thread(target=self.fetch_stats, daemon=True).start()

    def create_stat_label(self, key, value):
        frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(frame, text=f"{key}:", width=150, anchor="w").pack(side="left")
        label = ctk.CTkLabel(frame, text=value, anchor="w")
        label.pack(side="left", fill="x")
        self.stats_labels[key] = label

    def fetch_stats(self):
        try:
            self.update_stat("Python Version", platform.python_version())
            self.update_stat("Script Version", self.get_script_version())
            
            while True:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                self.update_stat("CPU Usage", f"{cpu}%")
                self.update_stat("RAM Usage", f"{ram}%")

                token = os.getenv('nuxified')
                if not token:
                    self.update_stat("Account Created", "No Token")
                    self.update_stat("Servers", "No Token")
                    self.update_stat("Latency", "N/A")
                else:
                    headers = {'Authorization': token, 'Content-Type': 'application/json'}
                    try:
                        start = time.time()
                        r = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
                        latency = (time.time() - start) * 1000
                        self.update_stat("Latency", f"{int(latency)}ms")

                        if r.status_code == 200:
                            data = r.json()
                            created_at = self.get_creation_date(int(data['id']))
                            self.update_stat("Account Created", created_at)
                        else:
                            self.update_stat("Account Created", "Error")

                        r = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers)
                        if r.status_code == 200:
                            guilds = r.json()
                            self.update_stat("Servers", str(len(guilds)))
                        else:
                            self.update_stat("Servers", "Error")
                    except Exception as e:
                        print(f"Error fetching discord stats: {e}")
                
                time.sleep(5) 
        except Exception as e:
            print(f"Error in stats loop: {e}")

    def get_script_version(self):
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuxified.py")
            with open(script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('VERSION ='):
                        return line.split('=')[1].strip().strip('"').strip("'")
            return "Unknown"
        except Exception as e:
            print(f"Error reading version: {e}")
            return "Error"

    def get_creation_date(self, user_id):
        timestamp = ((user_id >> 22) + 1420070400000) / 1000
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def update_stat(self, key, value):
        if key in self.stats_labels:
            try:
                self.stats_labels[key].configure(text=value)
            except:
                pass

    def show_settings(self):
        self.clear_main_area()
        self.entries = {}

        title = ctk.CTkLabel(self.main_frame, text="Configuration", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Environment Variables")
        scroll_frame.pack(fill="both", expand=True)

        self.create_group(scroll_frame, "Bot Configuration", [
            ("Bot Token", "nuxified"),
            ("Allowed User IDs", "allowed")
        ])

        self.create_group(scroll_frame, "API Keys", [
            ("OpenRouter Key", "OpenRouter"),
            ("Steam API Key", "STEAM_API_KEY"),
            ("Spotify Client ID", "spotify_client_id"),
            ("Spotify Client Secret", "spotify_client_secret"),
            ("Xbox API Key", "XBOX_API_KEY")
        ])
        
        self.obfuscation_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(scroll_frame, text="Token Obfuscation", variable=self.obfuscation_var, command=self.toggle_obfuscation).pack(anchor="w", padx=20, pady=10)

        save_btn = ctk.CTkButton(self.main_frame, text="Save Changes", command=self.save_config, height=40, fg_color="#333333", hover_color="#555555")
        save_btn.pack(pady=20, fill="x")
        
        self.load_current_values()

    def create_group(self, parent, title, fields):
        group_frame = ctk.CTkFrame(parent)
        group_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(group_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        for label_text, env_key in fields:
            field_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
            field_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(field_frame, text=label_text, width=120, anchor="w").pack(side="left")
            
            # Obfuscate everything except "allowed" (Allowed User IDs)
            if env_key != "allowed":
                entry = ObfuscatedEntry(field_frame, placeholder_text=f"Enter {env_key}...")
            else:
                entry = ctk.CTkEntry(field_frame, placeholder_text=f"Enter {env_key}...")
                
            entry.pack(side="left", fill="x", expand=True)
            
            self.entries[env_key] = entry

    def toggle_obfuscation(self):
        enabled = self.obfuscation_var.get()
        for entry in self.entries.values():
            if isinstance(entry, ObfuscatedEntry):
                entry.set_obfuscation_state(enabled)

    def load_current_values(self):
        for key, entry in self.entries.items():
            value = os.getenv(key, "")
            if isinstance(entry, ObfuscatedEntry):
                entry.set_real(value)
            else:
                entry.delete(0, "end")
                entry.insert(0, value)

    def save_config(self):
        try:
            if not os.path.exists(self.env_path):
                with open(self.env_path, 'w') as f:
                    pass

            for key, entry in self.entries.items():
                if isinstance(entry, ObfuscatedEntry):
                    value = entry.get_real().strip()
                else:
                    value = entry.get().strip()
                os.environ[key] = value
                set_key(self.env_path, key, value)
            
            self.status_label.configure(text="Status: Config Saved", text_color="#2ecc71")
            self.after(3000, lambda: self.status_label.configure(text="Status: Ready", text_color="gray"))
        except Exception as e:
            self.status_label.configure(text=f"Status: Error Saving", text_color="#e74c3c")
            print(e)

    def start_bot(self):
        try:
            self.status_label.configure(text="Status: Starting...", text_color="#3498db")
            
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuxified.py")
            
            if os.name == 'nt': 
                subprocess.Popen(f'start cmd /k "{python_exe} {script_path}"', shell=True)
            else:
                subprocess.Popen([python_exe, script_path])
                
            self.status_label.configure(text="Status: Running", text_color="#2ecc71")
        except Exception as e:
            self.status_label.configure(text=f"Status: Error Starting", text_color="#e74c3c")
            print(e)

    def show_logs(self):
        self.clear_main_area()
        
        title = ctk.CTkLabel(self.main_frame, text="Live Logs", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        self.log_textbox = ctk.CTkTextbox(self.main_frame, width=800, height=400)
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.configure(state="disabled")
        
        self.viewing_logs = True
        threading.Thread(target=self.update_logs, daemon=True).start()

    def update_logs(self):
        last_size = 0
        current_log_file = None
        
        while self.viewing_logs:
            try:
                if not self.log_textbox.winfo_exists():
                    break
                log_files = glob.glob("logs/logs_*.txt")
                if not log_files:
                    time.sleep(2)
                    continue
                    
                newest_file = max(log_files, key=os.path.getctime)
                
                if newest_file != current_log_file:
                    current_log_file = newest_file
                    last_size = 0
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.delete("1.0", "end")
                    self.log_textbox.configure(state="disabled")
                
                current_size = os.path.getsize(current_log_file)
                if current_size > last_size:
                    with open(current_log_file, "r", encoding="utf-8") as f:
                        f.seek(last_size)
                        new_content = f.read()
                        last_size = current_size
                        
                        self.log_textbox.configure(state="normal")
                        self.log_textbox.insert("end", new_content)
                        self.log_textbox.see("end")
                        self.log_textbox.configure(state="disabled")
                
                time.sleep(1)
            except Exception as e:
                print(f"Error updating logs: {e}")
                time.sleep(2)

    def show_terminal(self):
        self.clear_main_area()
        
        title = ctk.CTkLabel(self.main_frame, text="Terminal", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        self.terminal_output = ctk.CTkTextbox(self.main_frame, width=800, height=350)
        self.terminal_output.pack(fill="both", expand=True, pady=(0, 10))
        self.terminal_output.configure(state="disabled")
        
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x")
        
        ctk.CTkLabel(input_frame, text=">>>").pack(side="left", padx=5)
        
        self.terminal_input = ctk.CTkEntry(input_frame)
        self.terminal_input.pack(side="left", fill="x", expand=True, padx=5)
        self.terminal_input.bind("<Return>", self.execute_terminal_command)
        
        run_btn = ctk.CTkButton(input_frame, text="Run", width=60, command=self.execute_terminal_command)
        run_btn.pack(side="right", padx=5)

    def execute_terminal_command(self, event=None):
        command = self.terminal_input.get()
        self.terminal_input.delete(0, "end")
        
        self.terminal_output.configure(state="normal")
        self.terminal_output.insert("end", f">>> {command}\n")
        
        try:
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            
            try:
                exec(command, globals())
            except Exception as e:
                print(e)
                
            sys.stdout = old_stdout
            output = redirected_output.getvalue()
            
            if output:
                self.terminal_output.insert("end", output + "\n")
        except Exception as e:
            self.terminal_output.insert("end", f"Error: {e}\n")
            
        self.terminal_output.see("end")
        self.terminal_output.configure(state="disabled")

if __name__ == "__main__":
    app = BotLauncher()
    app.mainloop()
