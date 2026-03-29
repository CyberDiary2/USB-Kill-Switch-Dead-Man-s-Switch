# USB Kill Switch 🔒

A lightweight security tool for Linux laptops that automatically shuts down your system when a monitored USB device (like a magnetic breakaway cable) disconnects.

## How It Works

1. Plug a USB device into your laptop and attach it to a pocket loop via magnetic cable
2. Select the device in the GUI and start monitoring
3. If the cable breaks away (laptop stolen, you move away, etc.), your laptop shuts down immediately
4. Since your drive is encrypted, your data stays protected

## Installation

### Prerequisites
```bash
# Install Python 3 and tkinter (usually pre-installed on most Linux distros)
sudo apt install python3 python3-tk  # Ubuntu/Debian
sudo dnf install python3 python3-tkinter  # Fedora
sudo pacman -S python tk  # Arch
```

### Setup
1. Download `usb_killswitch.py`
2. Make it executable:
   ```bash
   chmod +x usb_killswitch.py
   ```

3. **IMPORTANT**: Configure sudo to allow shutdown without password:
   ```bash
   sudo visudo
   ```
   Add this line at the end (replace YOUR_USERNAME):
   ```
   YOUR_USERNAME ALL=(ALL) NOPASSWD: /sbin/shutdown
   ```
   Save and exit (Ctrl+X, then Y, then Enter)

## Usage

### Starting the App
```bash
python3 usb_killswitch.py
```

Or double-click the file if your file manager supports it.

### Using the GUI

1. **Click "Refresh Device List"** - Shows all connected USB devices
2. **Select your USB device** - Pick the one you'll use as the kill switch (usually your magnetic cable/USB stick)
3. **Click "START MONITORING"** - Monitoring is now ACTIVE
4. **To stop**: Click "STOP" button

### Important Notes

- **When monitoring is active**, disconnecting the USB device will IMMEDIATELY shut down your laptop
- Test it first in a safe environment!
- The device selection is saved, so you don't need to select it every time
- Keep the app running in the background (minimize it, don't close)

## Advanced: Auto-Start on Boot

To run the kill switch automatically when you log in:

### Option 1: Desktop File (Easiest)
Create `~/.config/autostart/usb-killswitch.desktop`:
```ini
[Desktop Entry]
Type=Application
Name=USB Kill Switch
Exec=python3 /full/path/to/usb_killswitch.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

### Option 2: Systemd Service (More Advanced)
Create `/etc/systemd/system/usb-killswitch.service`:
```ini
[Unit]
Description=USB Kill Switch Monitor
After=graphical.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/bin/python3 /full/path/to/usb_killswitch.py
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable it:
```bash
sudo systemctl enable usb-killswitch.service
sudo systemctl start usb-killswitch.service
```

## How to Test Safely

1. Save all your work and close important apps
2. Start monitoring your USB device
3. Gently disconnect the USB device
4. Your laptop should shut down immediately
5. Reboot and verify everything works

## Troubleshooting

**"Permission denied" when shutting down?**
- Make sure you configured sudo correctly (see Setup step 3)

**Device not detected?**
- Click "Refresh Device List"
- Try unplugging and replugging the USB device
- Run `lsusb` in terminal to verify the device is detected

**Kill switch not working?**
- Verify monitoring is active (status shows "ACTIVE 🔴")
- Test with `lsusb` - when you unplug, device should disappear

## Technical Details

- **Language**: Python 3
- **GUI**: Tkinter (built-in, no extra dependencies)
- **System calls**: lsusb for device detection, sudo shutdown for system shutdown
- **Resource usage**: Minimal (~10-20MB RAM, negligible CPU)
- **Check interval**: 0.5 seconds (fast response time)

## Security Considerations

 **Good for:**
- Physical theft protection (laptop grab-and-run)
- Quick data protection in emergency
- Leaving laptop unattended in public spaces

 **Not protection against:**
- Skilled attackers with time (they can boot from USB, remove drive, etc.)
- Network attacks
- Malware already on the system

**Remember**: This is ONE layer of security. Keep your drive encrypted, use strong passwords, and keep your system updated!

## License

Free to use, modify, and distribute. Use at your own risk.
-andrew@cyberdiary.net

If you found this useful and would like to buy me a slice of pizza:
BTC: bc1qm8x8ksce54ueqdvft8tp3pnh0npu5a6p8ql8mk
ETH: 0xed1681351E6C2F5342Fc9eF53ac58081C65808db
---

**Tip**: Use a distinctive USB stick or device that you won't accidentally unplug!
