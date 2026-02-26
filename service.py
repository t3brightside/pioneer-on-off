#!/usr/bin/env python3
import time
import serial
import subprocess
import sys
import os

# --- Configuration ---
PORT = '/dev/ttyACM0'
BAUD = 9600
IDLE_THRESHOLD = 1200  # 20 minutes in seconds
CHECK_INTERVAL = 1   # Poll audio every 10 seconds
STATE_FILE = os.path.expanduser("~/.amp_state")

class AmpController:
    def __init__(self):
        self.amp_is_on = False
        self.last_active_time = time.time()
        self.last_log_time = 0
        self.was_playing = False
        self.load_state()

    def load_state(self):
        """Load state from disk on startup to survive computer reboots."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = f.read().strip().split(',')
                    self.amp_is_on = (data[0] == 'True')
                    self.last_active_time = float(data[1])
                print(f"📋 Recovered state: Amp is {'ON' if self.amp_is_on else 'OFF'}")
            except Exception as e:
                print(f"⚠️ State file corrupt ({e}). Starting fresh (Amp OFF).")

    def save_state(self):
        """Save current state to disk with an OS sync to survive power loss."""
        try:
            with open(STATE_FILE, 'w') as f:
                f.write(f"{self.amp_is_on},{self.last_active_time}")
                f.flush()
                os.fsync(f.fileno()) # Forces Linux to write to physical disk immediately
        except Exception as e:
            print(f"❌ Could not save state: {e}")

    def is_audio_playing(self):
        """Checks ALSA hardware status for running streams."""
        try:
            status = subprocess.check_output("grep -r 'RUNNING' /proc/asound/card*/pcm*/sub*/status || true", shell=True)
            return b"RUNNING" in status
        except Exception:
            return False

    def toggle_amp(self, target_on, force=False):
        """Sends the serial command. Uses 'force' for manual CLI overrides."""
        if self.amp_is_on == target_on and not force:
            return # Already in the correct state

        try:
            with serial.Serial(PORT, BAUD, timeout=1) as ser:
                time.sleep(2) # Wait for Arduino to initialize
                ser.write(b'1')
                time.sleep(0.2)
                ser.write(b'1')
                
                self.amp_is_on = target_on
                self.save_state()
                print(f"\n[{time.strftime('%H:%M:%S')}] 🔌 Port Toggled. Target State: {'ON' if target_on else 'OFF'}")
        except Exception as e:
            print(f"\n[{time.strftime('%H:%M:%S')}] ❌ Serial Error: {e}")

    def run_daemon(self):
        print(f"🚀 Daemon Mode: Tracking state via {STATE_FILE}")
        print(f"⏳ Idle limit set to {IDLE_THRESHOLD // 60} minutes.")
        
        while True:
            playing = self.is_audio_playing()
            now = time.time()

            if playing:
                self.last_active_time = now
                if not self.amp_is_on:
                    print(f"[{time.strftime('%H:%M:%S')}] 🎵 Audio detected! Powering up.", flush=True)
                    self.toggle_amp(True)
                
                # If audio just started, log it and save the state
                if not self.was_playing:
                    print(f"[{time.strftime('%H:%M:%S')}] ▶️ Audio playback active. Idle timer paused.", flush=True)
                    self.save_state()
                    self.was_playing = True
            else:
                # If audio just stopped, log it and record the exact time
                if self.was_playing:
                    print(f"[{time.strftime('%H:%M:%S')}] ⏸️ Audio stopped. Starting countdown...", flush=True)
                    self.save_state()
                    self.was_playing = False

                if self.amp_is_on:
                    idle_seconds = now - self.last_active_time
                    remaining = max(0, IDLE_THRESHOLD - idle_seconds)
                    
                    # Log countdown every 60 seconds
                    if now - self.last_log_time >= 60:
                        mins, secs = divmod(int(remaining), 60)
                        print(f"⏳ No audio. Sleep countdown: {mins:02d}m {secs:02d}s...", flush=True)
                        self.last_log_time = now

                    if idle_seconds > IDLE_THRESHOLD:
                        print(f"[{time.strftime('%H:%M:%S')}] 🌙 Threshold reached. Powering down.", flush=True)
                        self.toggle_amp(False)

            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    controller = AmpController()

    # Handle command-line flags
    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()
        if flag in ['--on', '-on']:
            print("Force turning ON...")
            controller.toggle_amp(True, force=True)
        elif flag in ['--off', '-off']:
            print("Force turning OFF...")
            controller.toggle_amp(False, force=True)
        elif flag in ['--status', '-s']:
            playing = "YES" if controller.is_audio_playing() else "NO"
            idle_time = int(time.time() - controller.last_active_time)
            print(f"--- Amp Status ---")
            print(f"State File   : {STATE_FILE}")
            print(f"Amp Power    : {'ON' if controller.amp_is_on else 'OFF'}")
            print(f"Audio Playing: {playing}")
            if controller.amp_is_on and not controller.is_audio_playing():
                rem = max(0, IDLE_THRESHOLD - idle_time)
                print(f"Time to Sleep: {rem // 60}m {rem % 60}s")
        else:
            print("Usage: python3 amp_daemon.py [--on | --off | --status]")
    else:
        # Run the continuous loop
        try:
            controller.run_daemon()
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped by user.")
            sys.exit(0)