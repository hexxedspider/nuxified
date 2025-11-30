import subprocess
import sys
import time
import os
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, scripts):
        self.scripts = scripts  # list of bot scripts
        self.processes = {}
        self.kill_existing_bots()
        self.start_bots()

    def kill_existing_bots(self):
        try:
            if os.name == 'nt':
                try:
                    result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe', '/fo', 'csv'],
                                          capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:
                            if 'nuxified.py' in line:
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    pid = parts[1].strip('"')
                                    try:
                                        subprocess.run(['taskkill', '/f', '/pid', pid],
                                                     capture_output=True, check=False)
                                    except:
                                        pass
                except:
                    pass
            else:
                try:
                    result = subprocess.run(['pgrep', '-f', 'nuxified.py'],
                                          capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            if pid.strip():
                                try:
                                    os.kill(int(pid), signal.SIGTERM)
                                    time.sleep(0.5)
                                    try:
                                        os.kill(int(pid), signal.SIGKILL)
                                    except (ProcessLookupError, OSError):
                                        pass
                                except (ProcessLookupError, OSError):
                                    pass
                except:
                    pass
        except Exception as e:
            print(f"Warning: Could not kill existing bot instances: {e}")

    def start_bots(self):
        for script in self.scripts:
            self.start_bot(script)

    def start_bot(self, script):
        if script in self.processes:
            self.processes[script].terminate()
            self.processes[script].wait()
        self.processes[script] = subprocess.Popen([sys.executable, script])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            for script in self.scripts:
                self.start_bot(script)

if __name__ == "__main__":
    path = "."
    bot_scripts = ["nuxified.py"]
    event_handler = RestartHandler(bot_scripts)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
        for proc in event_handler.processes.values():
            proc.terminate()
    observer.join()
