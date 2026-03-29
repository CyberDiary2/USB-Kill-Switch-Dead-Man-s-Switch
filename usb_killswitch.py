#!/usr/bin/env python3
"""
USB Kill Switch - Shuts down laptop when USB device disconnects
Lightweight security tool for Linux systems with encrypted drives
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
import json
from pathlib import Path

class USBKillSwitch:
    def __init__(self):
        self.config_file = Path.home() / '.usb_killswitch_config.json'
        self.monitoring = False
        self.monitor_thread = None
        self.device_id = None
        self.check_interval = 0.5  # Check every 0.5 seconds
        
        self.load_config()
        
    def load_config(self):
        """Load saved configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.device_id = config.get('device_id')
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'device_id': self.device_id}, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_usb_devices(self):
        """Get list of connected USB devices"""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            devices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Extract device ID (format: Bus XXX Device XXX: ID XXXX:XXXX)
                    parts = line.split('ID ')
                    if len(parts) > 1:
                        device_id = parts[1].split()[0]
                        device_name = ' '.join(parts[1].split()[1:])
                        devices.append((device_id, f"{device_id} - {device_name}"))
            return devices
        except Exception as e:
            print(f"Error getting USB devices: {e}")
            return []
    
    def is_device_connected(self):
        """Check if the monitored device is still connected"""
        if not self.device_id:
            return True
        
        devices = self.get_usb_devices()
        for dev_id, _ in devices:
            if dev_id == self.device_id:
                return True
        return False
    
    def shutdown_system(self):
        """Shutdown the system immediately"""
        try:
            # Try immediate shutdown (requires sudo privileges)
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=False)
        except Exception as e:
            print(f"Error shutting down: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print(f"Monitoring started for device: {self.device_id}")
        
        # Wait a moment for initial connection to stabilize
        time.sleep(1)
        
        while self.monitoring:
            if not self.is_device_connected():
                print("DEVICE DISCONNECTED - SHUTTING DOWN!")
                self.shutdown_system()
                break
            time.sleep(self.check_interval)
    
    def start_monitoring(self):
        """Start monitoring the USB device"""
        if not self.device_id:
            return False, "No device selected"
        
        if self.monitoring:
            return False, "Already monitoring"
        
        if not self.is_device_connected():
            return False, "Device not connected"
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        return True, "Monitoring started"
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        return "Monitoring stopped"


class KillSwitchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Kill Switch")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.killswitch = USBKillSwitch()
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        """Create the GUI"""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🔒 USB Kill Switch",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Device selection
        device_label = tk.Label(
            content_frame,
            text="Select USB Device to Monitor:",
            font=("Arial", 11, "bold"),
            bg="white"
        )
        device_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.device_combo = ttk.Combobox(content_frame, state="readonly", width=60)
        self.device_combo.pack(fill=tk.X, pady=(0, 10))
        
        refresh_btn = tk.Button(
            content_frame,
            text="🔄 Refresh Device List",
            command=self.refresh_devices,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        refresh_btn.pack(pady=(0, 20))
        
        # Status
        self.status_label = tk.Label(
            content_frame,
            text="Status: Inactive",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#95a5a6"
        )
        self.status_label.pack(pady=10)
        
        # Control buttons
        button_frame = tk.Frame(content_frame, bg="white")
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ START MONITORING",
            command=self.start_monitoring,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ STOP",
            command=self.stop_monitoring,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            width=20,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Info
        info_text = (
            "⚠️ WARNING: When monitoring is active, disconnecting\n"
            "the selected USB device will IMMEDIATELY shut down\n"
            "your laptop. Make sure your device is secure!"
        )
        info_label = tk.Label(
            content_frame,
            text=info_text,
            font=("Arial", 9),
            bg="#fff3cd",
            fg="#856404",
            padx=10,
            pady=10,
            justify=tk.LEFT
        )
        info_label.pack(fill=tk.X, pady=(10, 0))
        
        # Initial device load
        self.refresh_devices()
    
    def refresh_devices(self):
        """Refresh the list of USB devices"""
        devices = self.killswitch.get_usb_devices()
        device_list = [desc for _, desc in devices]
        self.device_combo['values'] = device_list
        
        # Select previously saved device if available
        if self.killswitch.device_id:
            for i, (dev_id, desc) in enumerate(devices):
                if dev_id == self.killswitch.device_id:
                    self.device_combo.current(i)
                    break
        elif device_list:
            self.device_combo.current(0)
    
    def start_monitoring(self):
        """Start monitoring"""
        if not self.device_combo.get():
            messagebox.showerror("Error", "Please select a USB device first")
            return
        
        # Get selected device ID
        selected = self.device_combo.get()
        device_id = selected.split(' - ')[0]
        self.killswitch.device_id = device_id
        self.killswitch.save_config()
        
        success, message = self.killswitch.start_monitoring()
        
        if success:
            self.status_label.config(text="Status: ACTIVE 🔴", fg="#27ae60")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.device_combo.config(state=tk.DISABLED)
            messagebox.showinfo("Started", "Kill switch is now active!\n\nDisconnecting the USB device will shut down your laptop.")
        else:
            messagebox.showerror("Error", message)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.killswitch.stop_monitoring()
        self.status_label.config(text="Status: Inactive", fg="#95a5a6")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.device_combo.config(state=tk.READONLY)
        messagebox.showinfo("Stopped", "Monitoring has been stopped")
    
    def update_status(self):
        """Update status display"""
        if self.killswitch.monitoring:
            if not self.killswitch.is_device_connected():
                self.status_label.config(text="Status: DEVICE DISCONNECTED!", fg="#e74c3c")
        self.root.after(1000, self.update_status)


def main():
    # Check if running on Linux
    if os.name != 'posix':
        print("This tool is designed for Linux systems only.")
        return
    
    root = tk.Tk()
    app = KillSwitchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
