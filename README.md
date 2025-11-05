![wincountdown screenshot](screenshots/screenshot_1.png)

# wincountdown

A command-line countdown timer for Linux with ASCII art display, customizable alerts, and configuration file support.

## Features

- Large ASCII art countdown display with customizable digit styles
- Clock mode displays current system time in 24-hour format
- Real-time start and end time display
- Customizable beep alerts (frequency, duration, count, gap)
- Configuration file for persistent settings
- Advanced behaviors: auto-run commands, default flags
- Loop mode for repeating countdowns
- Silent mode option
- Metric time mode (1 hour = 100 minutes, 1 minute = 100 seconds)
- Smart display (shows only relevant time units)
- XDG Base Directory compliant (follows Linux standards)
- Debug mode for troubleshooting (config file or command-line flag)

## Usage
```bash
wincountdown <time> [options]
```

### Time Formats

- Seconds only: `30s`, `90s`, `500s`
- Minutes only: `5m`, `45m`, `240m`
- Hours only: `2h`, `10h`
- Combined: `1h30m`, `2h15m30s`, `45m30s`
- Colon format: `1:30:00` (HH:MM:SS), `45:30` (MM:SS)

### Options

| Option | Description |
|--------|-------------|
| `-s, --silent` | Silent mode (no beep alert) |
| `-f HZ, --freq HZ` | Beep frequency in Hz (default: from config, or 800) |
| `-b N, --beeps N` | Number of beeps when finished (default: from config, or 3) |
| `-d MS, --duration MS` | Duration of each beep in milliseconds (default: from config, or 1000) |
| `-g MS, --gap MS` | Gap between beeps in milliseconds (default: from config, or 300) |
| `-l, --loop` | Automatically restart countdown when it reaches 0 |
| `-m, --metric` | Display in metric time (1h=100m, 1m=100s) |
| `-c, --clock` | Clock mode - display current system time (ignores `<time>` argument) |
| `--debug` | Enable debug mode (logs to ~/.cache/wincountdown/debug.log) |
| `-h, --help` | Show help message |

### Examples
```bash
# Basic countdowns
wincountdown 30s
wincountdown 5m
wincountdown 1h30m
wincountdown 90s

# Silent mode
wincountdown 10m --silent
wincountdown 5m -s

# Loop mode
wincountdown 25m --loop
wincountdown 3m -l

# Custom beep patterns
wincountdown 1m --freq 440
wincountdown 30s --beeps 5
wincountdown 1h --duration 500
wincountdown 5m --gap 100
wincountdown 1m -f 880 -b 3 -d 200 -g 100

# Metric time
wincountdown 5m --metric
wincountdown 1h -m

# Clock mode
wincountdown --clock
wincountdown -c

# Debug mode
wincountdown 5m --debug
wincountdown --clock --debug

# Combinations
wincountdown 25m -l -s
wincountdown 10s -f 1000 -b 1 -d 2000
```

## Installation

### Arch Linux (AUR)

**Coming soon!** Once published to AUR:

```bash
yay -S wincountdown
# or
paru -S wincountdown
```

### Manual Installation (Any Linux Distribution)

#### Option 1: Install with pip (Recommended)

```bash
git clone https://github.com/Stropitor/wincountdown-linux.git
cd wincountdown-linux
pip install .
```

Now you can run `wincountdown` from anywhere!

#### Option 2: Install with setup.py

```bash
git clone https://github.com/Stropitor/wincountdown-linux.git
cd wincountdown-linux
python setup.py install
```

#### Option 3: Run as Standalone Script

```bash
git clone https://github.com/Stropitor/wincountdown-linux.git
cd wincountdown-linux
chmod +x wincountdown.py

# Run directly
./wincountdown.py 5m

# Or create a symlink for system-wide access
sudo ln -s "$(pwd)/wincountdown.py" /usr/local/bin/wincountdown
```

### Optional Dependencies

For enhanced audio alerts with customizable frequency and duration:

```bash
# Arch Linux
sudo pacman -S beep

# Debian/Ubuntu
sudo apt install beep

# Fedora
sudo dnf install beep
```

**Note:** Without the `beep` package, the program will fall back to the terminal bell (`\a`) character, which may not produce sound depending on your terminal emulator settings.

## Configuration File

Configuration file location depends on how you run wincountdown:

**When installed via pip:**
```
~/.config/wincountdown/config.json    # Configuration
~/.cache/wincountdown/debug.log       # Debug logs
```

**When running standalone (./wincountdown.py):**
```
./config.json      # Configuration (in script directory)
./debug.log        # Debug logs (in script directory)
```

The configuration file is automatically created on first run.

### Basic Settings

```json
{
  "debug_mode": false,
  "default_frequency": 800,
  "default_beeps": 3,
  "default_duration": 1000,
  "default_gap": 300,
  "default_silent": false,
  "default_loop": false,
  "default_metric": false
}
```

### ASCII Art Customization

Digits (0-9) and colon (:) can be customized in the `ascii_digits` section.

**Requirements:**
- Each digit must be exactly 8 lines tall
- All digits should have consistent width (11 characters recommended)
- Any characters can be used: `#`, `*`, `@`, `█`, `░`, `▓`, etc.

**Example - Default style:**
```json
{
  "ascii_digits": {
    "0": [
      " ######### ",
      "###     ###",
      "###     ###",
      "###     ###",
      "###     ###",
      "###     ###",
      "###     ###",
      " ######### "
    ],
    "1": [
      "    ###    ",
      "  #####    ",
      "    ###    ",
      "    ###    ",
      "    ###    ",
      "    ###    ",
      "    ###    ",
      "###########"
    ]
  }
}
```

**Example - Block style:**
```json
{
  "ascii_digits": {
    "0": [
      " █████████ ",
      "███     ███",
      "███     ███",
      "███     ███",
      "███     ███",
      "███     ███",
      "███     ███",
      " █████████ "
    ]
  }
}
```

If a digit is malformed or missing, the default style is used automatically.

### Advanced Behaviors

#### No Arguments Behavior

Controls behavior when running `wincountdown` with no arguments.

```json
{
  "enable_no_args_default": true,
  "no_args_default_command": "25m"
}
```

Options for `no_args_default_command`:
- `"help"` - Show help screen (default)
- Any time string: `"5m"`, `"25m"`, `"1h30m"`
- With flags: `"10m -l"` (10-minute looping timer)

#### Time-Only Arguments Behavior

Automatically adds flags when only a time argument is provided.

```json
{
  "enable_time_only_defaults": true,
  "time_only_default_flags": ["-l", "-s"]
}
```

Common flag combinations:
- `["-l", "-s"]` - Loop and silent
- `["-l"]` - Loop only
- `["-f", "1000", "-b", "5"]` - Custom frequency and beep count
- `["-m"]` - Metric mode

Note: This only applies when providing just the time. Manual flags disable these defaults.

### Configuration Examples

**Pomodoro Timer:**
```json
{
  "enable_no_args_default": true,
  "no_args_default_command": "25m",
  "enable_time_only_defaults": true,
  "time_only_default_flags": ["-l"]
}
```

**Silent Work Timer:**
```json
{
  "default_silent": true,
  "default_loop": true
}
```

**Custom Alert:**
```json
{
  "enable_no_args_default": true,
  "no_args_default_command": "5m -f 1000 -b 5"
}
```

## Debug Mode

Debug mode can be enabled in two ways:

**Option 1: Command-line flag (recommended)**
```bash
wincountdown 5m --debug
wincountdown --clock --debug
```

**Option 2: Configuration file**
```json
{
  "debug_mode": true
}
```

When enabled:
- Creates `~/.cache/wincountdown/debug.log`
- Logs detailed execution information with timestamps
- Clears the log file on each run
- Command-line `--debug` flag overrides config file setting

## Notes

- Maximum time: 99:59:59 (or 99:99:99 in metric mode)
- **Clock mode:** Displays current system time in 24-hour format (HH:MM:SS). Always shows 24-hour time regardless of system settings. Press Ctrl+C to exit.
- Timer automatically shows only relevant units (seconds, MM:SS, or HH:MM:SS)
- Start time and end time are displayed at the bottom
- Beep alert plays when countdown finishes (requires `beep` package for customizable sounds)
- Loop mode plays only one beep before restarting
- Metric mode: 1 hour = 100 minutes, 1 minute = 100 seconds. Each metric second = 1 real second. Input time is in real time.
- Press Ctrl+C to stop the timer or exit clock mode
- Configuration file is created automatically on first run at `~/.config/wincountdown/config.json`
- Command-line flags override config file settings
- ASCII art digits can be customized in the config file
- Debug mode: Use `--debug` flag or enable in config file. Logs to `~/.cache/wincountdown/debug.log`
- Follows XDG Base Directory specification for Linux compliance

## Troubleshooting

**Config not working:**
1. Enable debug mode (set `"debug_mode": true` in `~/.config/wincountdown/config.json`)
2. Check `~/.cache/wincountdown/debug.log` for errors
3. Verify config file is valid JSON
4. Delete the config file to regenerate with defaults

**ASCII art looks wrong:**
- Each digit must be exactly 8 lines tall
- All digits should have consistent width
- All lines in a digit should have the same character width
- Invalid digits automatically fall back to default style
- Delete the config file to regenerate with defaults

**Timer not visible:**
- Terminal window must be at least 120 characters wide
- Maximize the terminal window or use a larger font

**No sound:**
- Install the `beep` package (see Installation section)
- Check that `"default_silent": false` in config
- Verify system volume is not muted
- Try a different frequency with `-f` flag
- Without `beep` package, falls back to terminal bell (may be silent in some terminals)

**Beep requires sudo/permissions:**
```bash
# Option 1: Add your user to the audio group
sudo usermod -a -G audio $USER
# Log out and log back in

# Option 2: Configure beep permissions
sudo chmod u+s /usr/bin/beep
```

**Unicode characters not displaying:**
- Ensure your terminal supports UTF-8 encoding
- Modern terminals (gnome-terminal, konsole, alacritty, kitty) support Unicode
- Try simpler ASCII characters if Unicode blocks don't display
- Config file must be saved as UTF-8 encoding

**Debug log not created:**
- Use `--debug` flag: `wincountdown 5m --debug`
- Alternatively, ensure `"debug_mode": true` is set in the config file
- Check write permissions: `ls -la ~/.cache/wincountdown/`
- Ensure `~/.cache/wincountdown/` directory exists (created automatically on first run)

**ANSI escape codes visible (garbled output):**
- Your terminal may not support ANSI escape sequences
- Try a modern terminal emulator (most support ANSI)
- Verify `TERM` environment variable is set correctly

## Development

### Project Structure

```
wincountdown-linux/
├── wincountdown.py          # Main application (single file)
├── setup.py                 # Python packaging
├── LICENSE                  # GNU GPLv3
├── README.md                # This file
├── .gitignore               # Git ignore rules
│
├── docs/                    # Documentation
│   ├── INSTALL.md           # Installation & testing guide
│   ├── PORTING_NOTES.md     # Windows→Linux porting details
│   └── CODEBASE_OVERVIEW.md # Complete code documentation
│
├── packaging/               # Distribution packages
│   ├── arch/                # Arch Linux AUR
│   │   ├── PKGBUILD         # AUR package build script
│   │   └── .SRCINFO         # AUR metadata
│   └── examples/            # Example configurations
│       └── wincountdown-config.json
│
└── screenshots/             # Example screenshots
    └── screenshot_1.png
```

### Additional Documentation

For more detailed information, see:
- **[Installation Guide](docs/INSTALL.md)** - Detailed installation instructions and troubleshooting
- **[Codebase Overview](docs/CODEBASE_OVERVIEW.md)** - Complete code documentation and architecture
- **[Porting Notes](docs/PORTING_NOTES.md)** - Details about the Windows→Linux port

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE) file for details.

## Credits

Created by stropitor

## Related Projects

- [wincountdown](https://github.com/Stropitor/wincountdown-windows) - Original Windows version
