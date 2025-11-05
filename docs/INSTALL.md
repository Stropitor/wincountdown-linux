# Installation & Testing Guide

Quick guide for installing and testing wincountdown on Linux.

## Quick Start (Testing Without Installation)

```bash
# Make executable
chmod +x wincountdown.py

# Test basic countdown
./wincountdown.py 10s

# Test with help
./wincountdown.py --help

# Test clock mode
./wincountdown.py --clock
```

## Installation Methods

### Method 1: System-wide Installation (Recommended)

```bash
# Install using pip
sudo pip install .

# Or using setup.py
sudo python setup.py install

# Now available as system command
wincountdown 5m
```

### Method 2: User Installation (No sudo required)

```bash
# Install to user directory
pip install --user .

# Make sure ~/.local/bin is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Now available as command
wincountdown 5m
```

### Method 3: Symlink (Development)

```bash
# Create symlink to /usr/local/bin
sudo ln -s "$(pwd)/wincountdown.py" /usr/local/bin/wincountdown

# Or to ~/.local/bin (no sudo)
mkdir -p ~/.local/bin
ln -s "$(pwd)/wincountdown.py" ~/.local/bin/wincountdown
```

### Method 4: Arch Linux Package (Local Build)

```bash
# Build package locally
makepkg -si

# This will:
# 1. Build the package
# 2. Install it via pacman
# 3. Track it in package manager
```

## Post-Installation Testing

### 1. Basic Functionality

```bash
# 10 second countdown
wincountdown 10s

# Should display large ASCII numbers counting down
# Should beep when finished (if beep package installed)
```

### 2. Check Config Creation

```bash
# Run once to create config
wincountdown 5s

# Check config was created
ls -la ~/.config/wincountdown/config.json
cat ~/.config/wincountdown/config.json
```

### 3. Test Audio Alerts

```bash
# With beep package installed
wincountdown 5s -f 1000 -b 3 -d 500

# Without beep (should fallback to terminal bell)
# Temporarily move beep: sudo mv /usr/bin/beep /usr/bin/beep.bak
wincountdown 5s
# Restore: sudo mv /usr/bin/beep.bak /usr/bin/beep
```

### 4. Test Clock Mode

```bash
# Display current time
wincountdown --clock

# Press Ctrl+C to exit
```

### 5. Test Loop Mode

```bash
# Auto-restart countdown
wincountdown 5s -l

# Press Ctrl+C to exit
```

### 6. Test Debug Mode

```bash
# Enable debug logging
wincountdown 10s --debug

# Check log file
cat ~/.cache/wincountdown/debug.log
```

## Install Optional Dependencies

### Audio Alerts (beep package)

```bash
# Arch Linux
sudo pacman -S beep

# Debian/Ubuntu
sudo apt install beep

# Fedora
sudo dnf install beep

# Note: May require additional permissions configuration
```

### Beep Permissions (if needed)

If beep doesn't work, you may need to:

```bash
# Add your user to audio group
sudo usermod -a -G audio $USER

# Or configure sudoers for beep
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/beep" | sudo tee /etc/sudoers.d/beep

# Logout and login for group changes to take effect
```

## Uninstallation

### If installed via pip

```bash
# System-wide
sudo pip uninstall wincountdown

# User installation
pip uninstall wincountdown
```

### If installed via setup.py

```bash
# Find installation location
pip show wincountdown

# Uninstall
sudo pip uninstall wincountdown
```

### If installed via pacman (Arch)

```bash
sudo pacman -R wincountdown
```

### If installed via symlink

```bash
# Remove symlink
sudo rm /usr/local/bin/wincountdown
# or
rm ~/.local/bin/wincountdown
```

### Remove configuration files

```bash
# Remove config and cache
rm -rf ~/.config/wincountdown
rm -rf ~/.cache/wincountdown
```

## Troubleshooting

### Command not found

```bash
# Check if installed
which wincountdown

# Check PATH includes installation directory
echo $PATH

# For user installation, ensure ~/.local/bin in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### ImportError or ModuleNotFoundError

```bash
# Check Python version (requires 3.6+)
python3 --version

# Verify installation
pip show wincountdown
```

### Beep doesn't work

```bash
# Check beep is installed
which beep

# Test beep directly
beep -f 800 -l 500

# If permission error, check user groups
groups $USER

# Should include 'audio' group
```

### Config file not created

```bash
# Check permissions
ls -la ~/.config/

# Manually create directory
mkdir -p ~/.config/wincountdown

# Run program again
wincountdown 5s
```

### Display issues (no ANSI colors/cursor hiding)

```bash
# Check terminal supports ANSI
echo -e "\033[31mRed Text\033[0m"

# Try different terminal emulator
# Most modern terminals support ANSI:
# - gnome-terminal
# - konsole
# - xterm
# - alacritty
# - kitty
```

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/wincountdown-linux.git
cd wincountdown-linux

# Make executable
chmod +x wincountdown.py

# Run directly (no installation)
./wincountdown.py 10s

# Edit code
vim wincountdown.py

# Test changes immediately
./wincountdown.py 5s
```

## Building AUR Package

```bash
# Install base-devel
sudo pacman -S base-devel

# Build package
makepkg -si

# Clean build files
makepkg -c

# Generate .SRCINFO (after editing PKGBUILD)
makepkg --printsrcinfo > .SRCINFO
```

## Next Steps

1. Customize config file: `~/.config/wincountdown/config.json`
2. Set default beep sounds, loop mode, etc.
3. Customize ASCII art digits
4. Create shell aliases for common countdowns:
   ```bash
   alias pomo='wincountdown 25m -l'
   alias break='wincountdown 5m'
   ```

## Getting Help

```bash
# Show help
wincountdown --help

# Enable debug mode for troubleshooting
wincountdown 10s --debug
cat ~/.cache/wincountdown/debug.log
```
