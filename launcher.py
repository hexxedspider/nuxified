import customtkinter as ctk
import os
import subprocess
import sys
import threading
import time
import requests
import datetime
import psutil
import platform
import webbrowser
import shutil
import glob
import io
import json
import concurrent.futures
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv, set_key

try:
    import pystray
    from pystray import MenuItem as item
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("pystray not installed - system tray disabled. Run: pip install pystray")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#0a0a0f",
    "bg_card": "#12121a", 
    "accent_purple": "#6d28d9",
    "accent_cyan": "#0e7490",
    "success": "#15803d",
    "warning": "#b45309",
    "error": "#b91c1c",
    "text": "#e4e4e7",
    "text_muted": "#71717a"
}

class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, message, toast_type="info", duration=2000, y_offset=20):
        super().__init__(master, corner_radius=10, bg_color="transparent")
        
        self.master_ref = master
        self.dismissed = False
        
        colors = {
            "info": COLORS["accent_cyan"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"]
        }
        
        self.configure(fg_color=colors.get(toast_type, COLORS["accent_cyan"]))
        
        self.label = ctk.CTkLabel(
            self, 
            text=message, 
            text_color="white",
            font=ctk.CTkFont(size=13),
            wraplength=280
        )
        self.label.pack(padx=10, pady=10)
        
        self.update_idletasks()
        
        self.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=y_offset)
        
        self.after(duration, self.dismiss)
    
    def dismiss(self):
        if self.dismissed:
            return
        self.dismissed = True
        try:
            if hasattr(self.master_ref, 'active_toasts') and self in self.master_ref.active_toasts:
                self.master_ref.active_toasts.remove(self)
            self.destroy()
        except:
            pass


class LoadingScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.title("")
        self.overrideredirect(True) 
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = 640
        height = 400
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(fg_color=COLORS["bg_dark"])
        
        self.banner_label = None
        banner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "nuxified_banner.png")
        
        if os.path.exists(banner_path):
            try:
                img = Image.open(banner_path)
                img = img.resize((600, 300), Image.Resampling.LANCZOS)
                self.banner_image = ctk.CTkImage(light_image=img, dark_image=img, size=(600, 300))
                self.banner_label = ctk.CTkLabel(self, image=self.banner_image, text="")
                self.banner_label.pack(pady=(20, 10))
            except Exception as e:
                print(f"Error loading banner: {e}")
        
        if not self.banner_label:
            self.title_label = ctk.CTkLabel(
                self, 
                text="Nuxified", 
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color=COLORS["accent_purple"]
            )
            self.title_label.pack(pady=(80, 20))
        
        self.status_label = ctk.CTkLabel(
            self, 
            text="Loading...", 
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_muted"]
        )
        self.status_label.pack(pady=10)
        
        self.progress = ctk.CTkProgressBar(self, width=400, height=4)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        self.lift()
        self.attributes('-topmost', True)
    
    def update_status(self, text, progress=None):
        try:
            self.status_label.configure(text=text)
            if progress is not None:
                self.progress.set(progress)
            self.update()
        except:
            pass

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
        self.project_dir = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(self.env_path) and os.path.exists(self.envv_path):
            try:
                shutil.copy(self.envv_path, self.env_path)
                print(f"created .env from .envv")
            except Exception as e:
                print(f"error creating .env: {e}")

        super().__init__()

        self.title("Nuxified x Nukumoxy444: Nuxified Vision")
        self.geometry("950x650")
        self.resizable(True, True)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        load_dotenv(self.env_path)
        
        self.bot_process = None
        self.bot_pids = []
        
        self.accounts = self.load_accounts()
        self.current_account = "nuxified"
        
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        self.tray_icon = None
        self.tray_thread = None
        
        self.active_toasts = []

        self.loading_screen = LoadingScreen(self)
        self.loading_screen.update_status("Initializing...", 0.1)
        self.update()
        
        self.loading_screen.update_status("Creating interface...", 0.3)
        self.create_sidebar()
        self.create_main_area()
        
        self.loading_screen.update_status("Loading configuration...", 0.5)
        self.viewing_logs = False
        self.log_filter_text = ""
        self.stats_running = False
        
        self.loading_screen.update_status("Setting up system tray...", 0.7)
        if TRAY_AVAILABLE:
            self.setup_tray_icon()
        
        self.loading_screen.update_status("Checking for updates...", 0.9)
        self.show_dashboard()
        
        self.after(500, self.check_for_updates_on_startup)
        
        self.loading_screen.update_status("Ready!", 1.0)
        self.after(800, self.loading_screen.destroy)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_toast(self, message, toast_type="info", duration=4000):
        self.active_toasts = [t for t in self.active_toasts if not t.dismissed and t.winfo_exists()]
        
        y_offset = 20 + (len(self.active_toasts) * 55)
        
        toast = ToastNotification(self, message, toast_type, duration, y_offset)
        self.active_toasts.append(toast)

    def load_accounts(self):
        accounts = {}
        load_dotenv(self.env_path)
        
        primary = os.getenv('nuxified', '')
        if primary:
            accounts['nuxified'] = {'token': primary, 'name': 'Primary Account'}
        
        for i in range(2, 11):
            key = f'nuxified_{i}'
            token = os.getenv(key, '')
            if token:
                accounts[key] = {'token': token, 'name': f'Account {i}'}
        
        return accounts

    def save_accounts(self):
        for key, data in self.accounts.items():
            set_key(self.env_path, key, data['token'])

    def setup_tray_icon(self):
        if not TRAY_AVAILABLE:
            return
            
        try:
            icon_path = os.path.join(self.project_dir, "assets", "nuxified_icon.png")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
            else:
                icon_image = Image.new('RGB', (64, 64), color=COLORS["accent_purple"])
            
            menu = pystray.Menu(
                item('Show', self.show_from_tray, default=True),
                item('Start Bot', self.start_bot_from_tray),
                item('Stop Bot', self.stop_bot_from_tray),
                pystray.Menu.SEPARATOR,
                item('Exit', self.quit_app)
            )
            
            self.tray_icon = pystray.Icon("Nuxified", icon_image, "Nuxified Launcher", menu)
            
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()
        except Exception as e:
            print(f"Error setting up tray icon: {e}")

    def show_from_tray(self, icon=None, item=None):
        self.after(0, self.deiconify)
        self.after(0, self.lift)

    def start_bot_from_tray(self, icon=None, item=None):
        self.after(0, self.start_bot)

    def stop_bot_from_tray(self, icon=None, item=None):
        self.after(0, self.stop_bot)

    def quit_app(self, icon=None, item=None):
        self.stop_bot()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    def on_closing(self):
        if TRAY_AVAILABLE and self.tray_icon:
            self.withdraw()
            self.show_toast("Minimized to tray", "info", 2000)
        else:
            self.quit_app()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLORS["bg_card"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Nuxified", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["accent_purple"]
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        button_style = {
            "fg_color": "transparent", 
            "border_width": 2, 
            "text_color": COLORS["text"],
            "border_color": COLORS["accent_purple"],
            "hover_color": COLORS["accent_purple"]
        }

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard, **button_style)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings, **button_style)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_logs = ctk.CTkButton(self.sidebar_frame, text="Live Logs", command=self.show_logs, **button_style)
        self.sidebar_button_logs.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_button_terminal = ctk.CTkButton(self.sidebar_frame, text="Terminal", command=self.show_terminal, **button_style)
        self.sidebar_button_terminal.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_info = ctk.CTkButton(self.sidebar_frame, text="Info", command=self.open_wiki, **button_style)
        self.sidebar_button_info.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", text_color=COLORS["text_muted"])
        self.status_label.grid(row=7, column=0, padx=20, pady=20)

    def open_wiki(self):
        webbrowser.open("https://github.com/hexxedspider/nuxified/wiki")

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def clear_main_area(self):
        self.viewing_logs = False
        self.stats_running = False
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_area()
        
        title = ctk.CTkLabel(self.main_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        actions_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"])
        actions_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(actions_frame, text="Quick Actions", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)
        account_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        account_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(account_frame, text="Account:").pack(side="left", padx=(0, 10))
        
        account_names = list(self.accounts.keys()) if self.accounts else ["nuxified"]
        self.account_dropdown = ctk.CTkComboBox(
            account_frame, 
            values=account_names,
            command=self.on_account_change,
            width=200
        )
        self.account_dropdown.set(self.current_account)
        self.account_dropdown.pack(side="left")

        button_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.start_button = ctk.CTkButton(
            button_frame, 
            text="Start Bot", 
            command=self.start_bot, 
            fg_color=COLORS["success"], 
            hover_color="#0f5c2e",
            height=40,
            width=150
        )
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ctk.CTkButton(
            button_frame, 
            text="Stop Bot", 
            command=self.stop_bot, 
            fg_color=COLORS["error"], 
            hover_color="#dc2626",
            height=40,
            width=150
        )
        self.stop_button.pack(side="left")
        
        self.update_bot_buttons()

        links_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"])
        links_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(links_frame, text="Quick Links", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        links_button_frame = ctk.CTkFrame(links_frame, fg_color="transparent")
        links_button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            links_button_frame, 
            text="Discord", 
            command=lambda: webbrowser.open("https://discord.com/app"),
            fg_color=COLORS["accent_purple"],
            width=120
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            links_button_frame, 
            text="Logs Folder", 
            command=lambda: self.open_folder("logs"),
            fg_color=COLORS["accent_cyan"],
            width=120
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            links_button_frame, 
            text="Nuxified Folder", 
            command=lambda: self.open_folder("project"),
            fg_color=COLORS["accent_cyan"],
            width=130
        ).pack(side="left")
        
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_card"])
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
        self.create_stat_label("Bot Status", "Loading...")

        threading.Thread(target=self.fetch_stats_async, daemon=True).start()

    def open_folder(self, folder_type):
        if folder_type == "logs":
            path = os.path.join(self.project_dir, "logs")
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        else:
            path = self.project_dir
        
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', path])

    def on_account_change(self, selected):
        self.current_account = selected
        self.show_toast(f"Switched to {selected}", "info", 2000)

    def update_bot_buttons(self):
        if self.is_bot_running():
            self.start_button.configure(state="disabled", fg_color=COLORS["text_muted"])
            self.stop_button.configure(state="normal", fg_color=COLORS["error"])
            self.status_label.configure(text="Status: Running", text_color=COLORS["success"])
        else:
            self.start_button.configure(state="normal", fg_color=COLORS["success"])
            self.stop_button.configure(state="disabled", fg_color=COLORS["text_muted"])
            self.status_label.configure(text="Status: Stopped", text_color=COLORS["text_muted"])

    def is_bot_running(self):
        if self.bot_process:
            return self.bot_process.poll() is None
        return False

    def create_stat_label(self, key, value):
        frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkLabel(frame, text=f"{key}:", width=150, anchor="w", text_color=COLORS["text_muted"]).pack(side="left")
        label = ctk.CTkLabel(frame, text=value, anchor="w")
        label.pack(side="left", fill="x")
        self.stats_labels[key] = label

    def fetch_stats_async(self):
        self.stats_running = True
        try:
            self.update_stat("Python Version", platform.python_version())
            self.update_stat("Script Version", self.get_script_version())
            
            while self.stats_running:
                if not self.stats_running:
                    break
                    
                try:
                    cpu = psutil.cpu_percent(interval=0)
                    ram = psutil.virtual_memory().percent
                    self.update_stat("CPU Usage", f"{cpu}%")
                    self.update_stat("RAM Usage", f"{ram}%")
                except:
                    pass
                
                try:
                    if self.is_bot_running():
                        self.update_stat("Bot Status", "[ON] Running")
                    else:
                        self.update_stat("Bot Status", "[OFF] Stopped")
                except:
                    pass

                if not self.stats_running:
                    break
                    
                token = os.getenv(self.current_account) or os.getenv('nuxified')
                if not token:
                    self.update_stat("Account Created", "No Token")
                    self.update_stat("Servers", "No Token")
                    self.update_stat("Latency", "N/A")
                else:
                    try:
                        discord_stats = self.fetch_discord_stats(token)
                        if self.stats_running:
                            self.update_stat("Account Created", discord_stats.get("created", "-"))
                            self.update_stat("Servers", discord_stats.get("servers", "-"))
                            self.update_stat("Latency", discord_stats.get("latency", "-"))
                    except Exception as e:
                        if self.stats_running:
                            self.update_stat("Account Created", "-")
                            self.update_stat("Servers", "-")
                            self.update_stat("Latency", "-")
                
                for _ in range(10):
                    if not self.stats_running:
                        break
                    time.sleep(0.5)
        except Exception as e:
            print(f"Error in stats loop: {e}")

    def fetch_discord_stats(self, token):
        stats = {"created": "-", "servers": "-", "latency": "-"}
        
        if not token or len(token) < 10:
            return stats
            
        headers = {'Authorization': token, 'Content-Type': 'application/json'}
        
        try:
            start = time.time()
            r = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=8)
            latency = (time.time() - start) * 1000
            stats["latency"] = f"{int(latency)}ms"
            
            if r.status_code == 200:
                data = r.json()
                created_at = self.get_creation_date(int(data['id']))
                stats["created"] = created_at
            elif r.status_code == 401:
                stats["created"] = "Invalid Token"
                stats["servers"] = "Invalid Token"
                return stats
            else:
                stats["created"] = f"Error ({r.status_code})"
        except requests.exceptions.Timeout:
            stats["latency"] = "Timeout"
            stats["created"] = "Timeout"
        except requests.exceptions.RequestException as e:
            stats["created"] = "Network Error"
        except Exception as e:
            stats["created"] = "-"
        
        try:
            r = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers, timeout=8)
            if r.status_code == 200:
                guilds = r.json()
                if isinstance(guilds, list):
                    stats["servers"] = str(len(guilds))
                else:
                    stats["servers"] = "-"
            elif r.status_code == 401:
                stats["servers"] = "Invalid Token"
            else:
                stats["servers"] = f"Error ({r.status_code})"
        except requests.exceptions.Timeout:
            stats["servers"] = "Timeout"
        except requests.exceptions.RequestException:
            stats["servers"] = "Network Error"
        except Exception:
            stats["servers"] = "-"
        
        return stats

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

    def check_for_updates_on_startup(self):
        def check():
            try:
                url = "https://api.github.com/repos/hexxedspider/nuxified/releases/latest"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    latest_tag = data.get('tag_name', '').lstrip('v')
                    current_ver = self.get_script_version().lstrip('v')
                    
                    try:
                        latest_parts = [int(x) for x in latest_tag.split('.')]
                        current_parts = [int(x) for x in current_ver.split('.')]
                        
                        while len(latest_parts) < 3: latest_parts.append(0)
                        while len(current_parts) < 3: current_parts.append(0)
                        
                        if current_parts > latest_parts:
                            self.after(0, lambda: self.show_toast(f"v{current_ver} (unreleased build)", "warning", 5000))
                        elif current_parts < latest_parts:
                            self.after(0, lambda: self.show_toast(f"Update available: v{latest_tag}", "info", 6000))
                        else:
                            self.after(0, lambda: self.show_toast(f"v{current_ver} - Up to date!", "success", 4000))
                    except ValueError:
                        self.after(0, lambda: self.show_toast(f"v{current_ver}", "info", 3000))
            except Exception as e:
                print(f"Update check error: {e}")
        
        threading.Thread(target=check, daemon=True).start()

    def show_settings(self):
        self.clear_main_area()
        self.entries = {}

        title = ctk.CTkLabel(self.main_frame, text="Configuration", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Environment Variables", fg_color=COLORS["bg_card"])
        scroll_frame.pack(fill="both", expand=True)

        self.create_group(scroll_frame, "Bot Configuration", [
            ("Bot Token", "nuxified"),
            ("Allowed User IDs", "allowed")
        ])

        self.create_group(scroll_frame, "Additional Accounts", [
            ("Account 2 Token", "nuxified_2"),
            ("Account 3 Token", "nuxified_3"),
            ("Account 4 Token", "nuxified_4"),
        ])

        self.create_group(scroll_frame, "API Keys", [
            ("OpenRouter Key", "OpenRouter"),
            ("Steam API Key", "STEAM_API_KEY"),
            ("Spotify Client ID", "spotify_client_id"),
            ("Spotify Client Secret", "spotify_client_secret"),
            ("Xbox API Key", "XBOX_API_KEY")
        ])
        
        self.obfuscation_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(scroll_frame, text="Obfuscation", variable=self.obfuscation_var, command=self.toggle_obfuscation).pack(anchor="w", padx=20, pady=10)

        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        save_btn = ctk.CTkButton(buttons_frame, text="Save Changes", command=self.save_config, height=40, fg_color=COLORS["success"], hover_color="#16a34a")
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        test_btn = ctk.CTkButton(buttons_frame, text="Test Token", command=self.test_token, height=40, fg_color=COLORS["accent_cyan"], hover_color="#0891b2")
        test_btn.pack(side="left", padx=(0, 10))
        
        backup_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        backup_frame.pack(fill="x", pady=5)
        
        backup_btn = ctk.CTkButton(backup_frame, text="Backup .env", command=self.backup_env, height=35, fg_color=COLORS["accent_purple"])
        backup_btn.pack(side="left", padx=(0, 10))
        
        restore_btn = ctk.CTkButton(backup_frame, text="Restore .env", command=self.restore_env, height=35, fg_color=COLORS["accent_purple"])
        restore_btn.pack(side="left")
        
        self.load_current_values()

    def test_token(self):
        token = None
        if 'nuxified' in self.entries:
            entry = self.entries['nuxified']
            token = entry.get_real() if isinstance(entry, ObfuscatedEntry) else entry.get()
        
        if not token:
            token = os.getenv('nuxified')
        
        if not token:
            self.show_toast("No token to test", "warning")
            return
        
        def test():
            try:
                headers = {'Authorization': token, 'Content-Type': 'application/json'}
                r = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=5)
                
                if r.status_code == 200:
                    data = r.json()
                    username = data.get('username', 'Unknown')
                    self.after(0, lambda: self.show_toast(f"Token valid: {username}", "success", 4000))
                elif r.status_code == 401:
                    self.after(0, lambda: self.show_toast("Token invalid or expired", "error", 4000))
                else:
                    self.after(0, lambda: self.show_toast(f"Token test failed: {r.status_code}", "warning", 4000))
            except Exception as e:
                self.after(0, lambda: self.show_toast(f"Test error: {str(e)[:30]}", "error", 4000))
        
        threading.Thread(target=test, daemon=True).start()
        self.show_toast("Testing token...", "info", 2000)

    def backup_env(self):
        if not os.path.exists(self.env_path):
            self.show_toast("No .env file to backup", "warning")
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.project_dir, f".env_backup_{timestamp}")
        
        try:
            shutil.copy(self.env_path, backup_path)
            self.show_toast(f"Backup saved: .env_backup_{timestamp}", "success", 4000)
        except Exception as e:
            self.show_toast(f"Backup failed: {e}", "error")

    def restore_env(self):
        filepath = filedialog.askopenfilename(
            initialdir=self.project_dir,
            title="Select .env backup",
            filetypes=[("Env files", ".env*"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                shutil.copy(filepath, self.env_path)
                load_dotenv(self.env_path, override=True)
                self.accounts = self.load_accounts()
                self.show_toast("Configuration restored!", "success")
                self.show_settings()
            except Exception as e:
                self.show_toast(f"Restore failed: {e}", "error")

    def create_group(self, parent, title, fields):
        group_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_dark"])
        group_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(group_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        for label_text, env_key in fields:
            field_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
            field_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(field_frame, text=label_text, width=150, anchor="w").pack(side="left")
            
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
        load_dotenv(self.env_path, override=True)
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
            
            self.accounts = self.load_accounts()
            self.status_label.configure(text="Status: Config Saved", text_color=COLORS["success"])
            self.show_toast("Configuration saved!", "success")
            self.after(3000, lambda: self.status_label.configure(text="Status: Ready", text_color=COLORS["text_muted"]))
        except Exception as e:
            self.status_label.configure(text=f"Status: Error Saving", text_color=COLORS["error"])
            self.show_toast(f"Save error: {e}", "error")
            print(e)

    def start_bot(self):
        if self.is_bot_running():
            self.show_toast("Bot is already running", "warning")
            return
            
        try:
            self.status_label.configure(text="Status: Starting...", text_color=COLORS["accent_cyan"])
            
            python_exe = sys.executable
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuxified.py")
            
            env = os.environ.copy()
            if self.current_account != "nuxified" and self.current_account in self.accounts:
                env['nuxified'] = self.accounts[self.current_account]['token']
            
            if os.name == 'nt': 
                self.bot_process = subprocess.Popen(
                    [python_exe, script_path],
                    env=env,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                self.bot_process = subprocess.Popen([python_exe, script_path], env=env)
                
            self.status_label.configure(text="Status: Running", text_color=COLORS["success"])
            self.show_toast("Bot started!", "success")
            self.update_bot_buttons()
            
            threading.Thread(target=self.monitor_bot_process, daemon=True).start()
            
        except Exception as e:
            self.status_label.configure(text=f"Status: Error Starting", text_color=COLORS["error"])
            self.show_toast(f"Start error: {e}", "error")
            print(e)

    def stop_bot(self):
        if not self.is_bot_running():
            self.show_toast("No bot running", "warning")
            return
        
        try:
            if self.bot_process:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
                self.bot_process = None
            
            self.status_label.configure(text="Status: Stopped", text_color=COLORS["text_muted"])
            self.show_toast("Bot stopped", "info")
            self.update_bot_buttons()
        except Exception as e:
            try:
                self.bot_process.kill()
                self.bot_process = None
            except:
                pass
            self.show_toast(f"Stop error: {e}", "error")

    def monitor_bot_process(self):
        if self.bot_process:
            self.bot_process.wait()
            self.after(0, self.on_bot_exit)

    def on_bot_exit(self):
        self.bot_process = None
        self.update_bot_buttons()
        self.show_toast("Bot process ended", "info")

    def show_logs(self):
        self.clear_main_area()
        
        title = ctk.CTkLabel(self.main_frame, text="Live Logs", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 10))
        
        filter_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=(0, 10))
        
        self.log_filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search logs...", width=200)
        self.log_filter_entry.pack(side="left", padx=(0, 10))
        self.log_filter_entry.bind("<KeyRelease>", self.on_log_filter_change)
        
        self.log_level_var = ctk.StringVar(value="ALL")
        ctk.CTkLabel(filter_frame, text="Level:").pack(side="left", padx=(20, 10))
        
        levels = ["ALL", "MSG", "BOT", "DEL"]
        self.log_level_dropdown = ctk.CTkComboBox(filter_frame, values=levels, variable=self.log_level_var, command=self.on_log_level_change, width=100)
        self.log_level_dropdown.pack(side="left")
        
        export_btn = ctk.CTkButton(filter_frame, text="Export Logs", command=self.export_logs, fg_color=COLORS["accent_purple"], width=100)
        export_btn.pack(side="right")
        
        self.log_textbox = ctk.CTkTextbox(self.main_frame, width=800, height=400, fg_color=COLORS["bg_card"])
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.configure(state="disabled")
        
        self.viewing_logs = True
        self.log_filter_text = ""
        self.log_level_filter = "ALL"
        self.full_log_content = ""
        
        threading.Thread(target=self.update_logs, daemon=True).start()

    def on_log_filter_change(self, event=None):
        self.log_filter_text = self.log_filter_entry.get().lower()
        self.apply_log_filters()

    def on_log_level_change(self, level):
        self.log_level_filter = level
        self.apply_log_filters()

    def apply_log_filters(self):
        if not hasattr(self, 'full_log_content'):
            return
        
        lines = self.full_log_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if self.log_level_filter != "ALL":
                if f"[{self.log_level_filter}]" not in line:
                    continue
            
            if self.log_filter_text and self.log_filter_text not in line.lower():
                continue
            
            filtered_lines.append(line)
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("end", '\n'.join(filtered_lines))
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def export_logs(self):
        filepath = filedialog.asksaveasfilename(
            initialdir=os.path.join(self.project_dir, "logs"),
            title="Save Logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"logs_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filepath:
            try:
                content = self.log_textbox.get("1.0", "end")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.show_toast(f"Logs exported!", "success")
            except Exception as e:
                self.show_toast(f"Export failed: {e}", "error")

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
                    self.full_log_content = ""
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.delete("1.0", "end")
                    self.log_textbox.configure(state="disabled")
                
                current_size = os.path.getsize(current_log_file)
                if current_size > last_size:
                    with open(current_log_file, "r", encoding="utf-8") as f:
                        f.seek(last_size)
                        new_content = f.read()
                        last_size = current_size
                        
                        self.full_log_content += new_content
                        self.apply_log_filters()
                
                time.sleep(1)
            except Exception as e:
                print(f"Error updating logs: {e}")
                time.sleep(2)

    def show_terminal(self):
        self.clear_main_area()
        
        title = ctk.CTkLabel(self.main_frame, text="Terminal", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        self.terminal_output = ctk.CTkTextbox(self.main_frame, width=800, height=350, fg_color=COLORS["bg_card"])
        self.terminal_output.pack(fill="both", expand=True, pady=(0, 10))
        self.terminal_output.configure(state="disabled")
        
        input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        ctk.CTkLabel(input_frame, text=">>>", text_color=COLORS["accent_cyan"]).pack(side="left", padx=5)
        
        self.terminal_input = ctk.CTkEntry(input_frame)
        self.terminal_input.pack(side="left", fill="x", expand=True, padx=5)
        self.terminal_input.bind("<Return>", self.execute_terminal_command)
        
        run_btn = ctk.CTkButton(input_frame, text="Run", width=60, command=self.execute_terminal_command, fg_color=COLORS["accent_purple"])
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
