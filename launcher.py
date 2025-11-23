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

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BotLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nuxified Launcher")
        self.geometry("900x600")
        self.resizable(True, True)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        load_dotenv(self.env_path)

        self.create_sidebar()
        self.create_main_area()
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

        self.sidebar_button_info = ctk.CTkButton(self.sidebar_frame, text="Info", command=self.open_wiki, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.sidebar_button_info.grid(row=4, column=0, padx=20, pady=10, sticky="s")
        
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=20, pady=20)

    def open_wiki(self):
        webbrowser.open("https://github.com/hexxedspider/nuxified/wiki")

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def clear_main_area(self):
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
            entry = ctk.CTkEntry(field_frame, placeholder_text=f"Enter {env_key}...")
            entry.pack(side="left", fill="x", expand=True)
            
            self.entries[env_key] = entry

    def load_current_values(self):
        for key, entry in self.entries.items():
            value = os.getenv(key, "")
            entry.delete(0, "end")
            entry.insert(0, value)

    def save_config(self):
        try:
            if not os.path.exists(self.env_path):
                with open(self.env_path, 'w') as f:
                    pass

            for key, entry in self.entries.items():
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

if __name__ == "__main__":
    app = BotLauncher()
    app.mainloop()
