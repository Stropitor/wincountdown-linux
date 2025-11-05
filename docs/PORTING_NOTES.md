# Porting Notes: Windows to Linux

This document outlines all changes made to port wincountdown from Windows to Linux.

## Summary of Changes

### 1. Import Statements

**Before:**
```python
import ctypes
import winsound
from ctypes import wintypes
```

**After:**
```python
import subprocess
from pathlib import Path
```

### 2. Terminal/Console Control

**Before:** Windows Console API using `ctypes.windll.kernel32`
```python
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("bVisible", wintypes.BOOL)]

class ConsoleManager:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.h_console = self.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
```

**After:** ANSI escape codes (universal terminal standard)
```python
ANSI_HIDE_CURSOR = '\033[?25l'
ANSI_SHOW_CURSOR = '\033[?25h'
ANSI_CLEAR_SCREEN = '\033[2J\033[H'

def ansi_move_cursor(x, y):
    return f'\033[{y+1};{x+1}H'

class ConsoleManager:
    def hide_cursor(self):
        print(ANSI_HIDE_CURSOR, end='', flush=True)
```

### 3. Audio System

**Before:** `winsound.Beep(frequency, duration)`
```python
winsound.Beep(freq, duration)
```

**After:** Linux `beep` command with fallback to terminal bell
```python
subprocess.run(['beep', '-f', str(freq), '-l', str(duration)],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# Fallback: print('\a')
```

### 4. Screen Clearing

**Before:** `os.system('cls')`

**After:** `os.system('clear')`

### 5. Configuration File Paths (XDG Base Directory Specification)

**Before:** Config files in script directory
```python
def __init__(self, script_dir):
    self.config_file = os.path.join(script_dir, "wincountdown-config.json")
    self.debug_log_file = os.path.join(script_dir, "wincountdown-debug.log")
```

**After:** XDG-compliant directories
```python
def __init__(self, script_dir=None):
    config_dir = Path.home() / '.config' / 'wincountdown'
    cache_dir = Path.home() / '.cache' / 'wincountdown'

    config_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    self.config_file = str(config_dir / 'config.json')
    self.debug_log_file = str(cache_dir / 'debug.log')
```

### 6. File Locations

| Purpose | Windows Location | Linux Location (XDG) |
|---------|-----------------|---------------------|
| Config | `.\wincountdown-config.json` | `~/.config/wincountdown/config.json` |
| Debug Log | `.\wincountdown-debug.log` | `~/.cache/wincountdown/debug.log` |

## New Files Created

### 1. setup.py
Python packaging file for installation via pip or setuptools.

**Key features:**
- Entry point: `wincountdown` command
- Python 3.6+ required
- No external dependencies (only stdlib)

### 2. PKGBUILD
Arch Linux package build file for AUR distribution.

**Key features:**
- Architecture: `any` (pure Python)
- Required dependency: `python`
- Optional dependency: `beep` (for audio alerts)
- Installs to standard system locations

### 3. .SRCINFO
AUR metadata file (generated from PKGBUILD).

### 4. README.md (Updated)
Comprehensive documentation including:
- Installation instructions (AUR, pip, manual)
- Usage examples
- Configuration guide
- FAQ section
- XDG directory information

## Technical Compatibility Notes

### ANSI Escape Codes vs Windows Console API

**Pros:**
- ANSI codes work on all modern terminals (Linux, macOS, modern Windows)
- No external dependencies
- Standard approach

**Cons:**
- Requires terminal that supports ANSI escape sequences
- Not compatible with very old terminals (unlikely to be an issue)

### Audio: beep vs winsound

**With beep package:**
- Full control over frequency (Hz) and duration (ms)
- Requires `beep` package installation
- May require permissions configuration on some systems

**Without beep package:**
- Falls back to terminal bell character (`\a`)
- No frequency/duration control
- Works everywhere but may be silent if terminal bell is disabled

## Testing Recommendations

1. **Basic functionality:**
   ```bash
   wincountdown 10s
   ```

2. **Config file creation:**
   ```bash
   ls -la ~/.config/wincountdown/config.json
   ```

3. **Audio with beep:**
   ```bash
   wincountdown 5s -f 1000 -b 3
   ```

4. **Audio fallback (without beep):**
   ```bash
   # Uninstall beep temporarily
   wincountdown 5s
   ```

5. **Clock mode:**
   ```bash
   wincountdown --clock
   ```

6. **Debug logging:**
   ```bash
   wincountdown 5s --debug
   cat ~/.cache/wincountdown/debug.log
   ```

## Known Issues & Limitations

1. **Beep permissions:** On some systems, `beep` requires special permissions or kernel module configuration
2. **Terminal compatibility:** Requires ANSI-capable terminal (virtually all modern terminals)
3. **No Windows support:** This version is Linux-only (original Windows version remains separate)

## Future Considerations

1. **Cross-platform version:** Could use platform detection to support both OSes in one codebase
2. **Alternative audio:** Could use PyAudio, pygame, or other libraries for audio without `beep` dependency
3. **Curses library:** Could use `curses` for more robust terminal control (adds complexity)
4. **Config migration:** Tool to migrate old Windows config to Linux XDG locations

## AUR Submission Checklist

Before submitting to AUR:

- [ ] Update GitHub URL in PKGBUILD and setup.py
- [ ] Create GitHub release with version tag (e.g., v1.0.0)
- [ ] Calculate and update sha256sum in PKGBUILD
- [ ] Regenerate .SRCINFO: `makepkg --printsrcinfo > .SRCINFO`
- [ ] Test build: `makepkg -si`
- [ ] Update maintainer info in PKGBUILD
- [ ] Create AUR repository
- [ ] Push PKGBUILD and .SRCINFO to AUR

## Resources

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [AUR Submission Guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
