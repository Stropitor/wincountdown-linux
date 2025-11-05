# Complete Codebase Overview - wincountdown

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [File Structure](#file-structure)
3. [Code Structure (wincountdown.py)](#code-structure)
4. [Data Flow](#data-flow)
5. [Class Details](#class-details)
6. [Key Functions](#key-functions)
7. [Configuration System](#configuration-system)
8. [Display System](#display-system)
9. [Execution Flow](#execution-flow)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│              (Command line args + config file)              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    ConfigManager                            │
│  • Loads/creates ~/.config/wincountdown/config.json        │
│  • Merges defaults with user config                        │
│  • Validates ASCII art                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Argument Processing                        │
│  • Parse command line args                                  │
│  • Apply config defaults                                    │
│  • Validate inputs                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
                   ┌────┴─────┐
                   │          │
                   ▼          ▼
        ┌──────────────┐  ┌──────────────┐
        │ Clock Mode   │  │ Timer Mode   │
        └──────┬───────┘  └──────┬───────┘
               │                 │
               ▼                 ▼
    ┌─────────────────┐  ┌─────────────────┐
    │ DisplayManager  │  │ CountdownTimer  │
    │ ConsoleManager  │  │ DisplayManager  │
    │                 │  │ ConsoleManager  │
    └─────────────────┘  └─────────────────┘
```

---

## File Structure

```
wincountdown-linux/
├── wincountdown.py          # Main application (1,132 lines) - ALL CODE
├── setup.py                 # Python packaging configuration
├── LICENSE                  # GNU GPLv3 license
├── README.md                # User documentation
├── .gitignore               # Git ignore rules
│
├── docs/                    # Documentation
│   ├── INSTALL.md           # Installation & testing guide
│   ├── PORTING_NOTES.md     # Windows→Linux porting details
│   └── CODEBASE_OVERVIEW.md # This file
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

**Note:** On Linux, config is created at `~/.config/wincountdown/config.json`

---

## Code Structure (wincountdown.py)

The entire application is in one file (1,132 lines):

```
wincountdown.py
├── Lines 1-16     : Shebang, docstring, imports
├── Lines 17-162   : Constants & Default Data
│   ├── BORDER_WIDTH, ASCII_HEIGHT
│   ├── MAX_STANDARD_SECONDS, MAX_METRIC_MILLISECONDS
│   ├── UPDATE_INTERVAL_STANDARD, UPDATE_INTERVAL_METRIC
│   ├── DEFAULT_ASCII_DIGITS (0-9, :)
│   └── DEFAULT_CONFIG
├── Lines 164-174  : ANSI Escape Codes
│   ├── ANSI_HIDE_CURSOR, ANSI_SHOW_CURSOR
│   ├── ANSI_CLEAR_SCREEN
│   └── ansi_move_cursor(x, y)
├── Lines 176-208  : Logger Class
├── Lines 210-242  : ConsoleManager Class
├── Lines 244-408  : ConfigManager Class
├── Lines 410-622  : DisplayManager Class
├── Lines 624-794  : CountdownTimer Class
├── Lines 796-1024 : Helper Functions
│   ├── get_effective_args()
│   ├── parse_arguments()
│   ├── validate_arguments()
│   └── print_help()
├── Lines 1026-1132: main() Function
└── Lines 1134-1136: if __name__ == '__main__'
```

---

## Data Flow

### Startup Flow
```
main()
  └─> ConfigManager()
       └─> Load or create ~/.config/wincountdown/config.json
            └─> Return config dict

  └─> get_effective_args(config)
       └─> Apply no-args defaults if enabled
       └─> Apply time-only defaults if enabled
       └─> Return modified sys.argv

  └─> parse_arguments(effective_args)
       └─> Use argparse to parse arguments
       └─> Return args object

  └─> validate_arguments(args)
       └─> Check frequency, beep count, time limits
       └─> Exit if invalid

  └─> Branch to Clock Mode or Timer Mode
```

### Timer Mode Flow
```
CountdownTimer.run()
  └─> DisplayManager.draw_static_ui()
       └─> ConsoleManager.clear_screen()
       └─> Print borders, title, time labels

  └─> Loop until countdown reaches 0:
       └─> Calculate remaining time
       └─> DisplayManager.update_time_display()
            └─> ConsoleManager.set_position()
            └─> DisplayManager.render_time()
                 └─> Convert time to ASCII art
                 └─> Print large digits
       └─> time.sleep(UPDATE_INTERVAL)

  └─> DisplayManager.draw_finished_screen()
       └─> Show "Time's Up!" message

  └─> play_beeps()
       └─> Try: subprocess.run(['beep', ...])
       └─> Except: print('\a')  # Terminal bell

  └─> If loop mode: Restart from beginning
```

### Clock Mode Flow
```
CountdownTimer.run_clock()
  └─> DisplayManager.draw_clock_ui()
       └─> ConsoleManager.clear_screen()
       └─> Print borders, title

  └─> Loop forever (until Ctrl+C):
       └─> Get current time from datetime.now()
       └─> DisplayManager.update_time_display()
            └─> Render current time as ASCII art
       └─> time.sleep(UPDATE_INTERVAL)
```

---

## Class Details

### 1. Logger (Lines 176-208)

**Purpose:** Simple debug logging system

**Attributes:**
- `enabled` (bool) - Whether logging is active
- `file_path` (str) - Path to `~/.cache/wincountdown/debug.log`

**Methods:**
- `setup(enabled, file_path)` - Initialize logger
- `log(message)` - Write timestamped message to log file

**Usage:**
```python
logger = Logger()  # Global instance
logger.setup(True, "/path/to/debug.log")
logger.log("Debug message")
```

---

### 2. ConsoleManager (Lines 210-242)

**Purpose:** Terminal control using ANSI escape codes

**Methods:**

| Method | Purpose | ANSI Code |
|--------|---------|-----------|
| `hide_cursor()` | Hide cursor to prevent flicker | `\033[?25l` |
| `show_cursor()` | Restore cursor visibility | `\033[?25h` |
| `set_position(x, y)` | Move cursor to coordinates | `\033[{y+1};{x+1}H` |
| `clear_screen()` | Clear entire screen | `\033[2J\033[H` |

**Context Manager:**
```python
with ConsoleManager() as console:
    # Cursor is hidden
    console.set_position(10, 5)
    print("Text at position")
# Cursor automatically shown on exit
```

---

### 3. ConfigManager (Lines 244-408)

**Purpose:** Load, create, and manage configuration

**Attributes:**
- `config_file` - `~/.config/wincountdown/config.json`
- `debug_log_file` - `~/.cache/wincountdown/debug.log`

**Methods:**

#### `__init__(script_dir=None)`
- Creates config and cache directories using XDG standard
- `~/.config/wincountdown/` for config
- `~/.cache/wincountdown/` for logs

#### `create_config_content()`
- Returns JSON string with detailed comments
- Includes all default values
- Documents each configuration option

#### `load()`
- Checks if config file exists
- If not: creates it with defaults
- If yes: loads and parses JSON
- Filters out comment lines (keys starting with "//")
- Validates ASCII digits
- Returns config dictionary

#### `_validate_ascii_digits(config)`
- Ensures each digit (0-9, :) is exactly 8 lines
- Each line must be exactly 11 characters
- Falls back to DEFAULT_ASCII_DIGITS if invalid

**Configuration Options:**
```json
{
    "debug_mode": false,
    "default_frequency": 800,        // Beep frequency in Hz
    "default_beeps": 3,              // Number of beeps
    "default_duration": 1000,        // Beep duration in ms
    "default_gap": 300,              // Gap between beeps in ms
    "default_silent": false,         // Silent mode by default
    "default_loop": false,           // Loop mode by default
    "default_metric": false,         // Metric time by default
    "enable_no_args_default": false, // Custom behavior when no args
    "no_args_default_command": "help",
    "enable_time_only_defaults": false,
    "time_only_default_flags": [],
    "ascii_digits": { ... }          // Custom ASCII art
}
```

---

### 4. DisplayManager (Lines 410-622)

**Purpose:** Render all UI elements and ASCII art

**Attributes:**
- `ascii_digits` - Dictionary of ASCII art for 0-9 and :

**Methods:**

#### `render_time(time_str)`
Returns 8 lines of ASCII art for time string.

**Input:** `"12:34:56"`
**Output:** List of 8 strings (large ASCII art)

**Process:**
1. Get ASCII art for each character
2. Concatenate horizontally line-by-line
3. Return 8-line list

#### `draw_border()`
Returns string of `=` characters (115 chars wide)

#### `draw_line()`
Returns empty line with borders: `|` + spaces + `|`

#### `draw_static_ui(total_seconds, show_hours, show_minutes, metric, start_time_str, end_time_str, console)`
Draws initial countdown screen:
```
  +================================================+
  |                                                |
  |  >>>  COUNTDOWN [ HH:MM:SS ]  <<<            |
  |                                                |
  +================================================+

  [8 lines of ASCII art for initial time]

  +================================================+
  | Start time: 12:00:00  Press Ctrl+C  End: 12:05|
  +================================================+
```

#### `update_time_display(time_str, console)`
Efficiently updates only the time portion (ASCII art area):
1. Move cursor to line 8
2. Render new time as ASCII art
3. Print each line at correct position
4. Avoids redrawing entire screen

#### `draw_finished_screen(show_hours, show_minutes, loop)`
Displays "Time's Up!" message after countdown completes:
```
  +================================================+
  |  >>>   TIME'S UP!   <<<                      |
  +================================================+

  [ASCII art showing 00:00:00]
```

#### `draw_clock_ui(console)`
Displays clock mode interface:
```
  +================================================+
  |  >>>   CURRENT TIME   <<<                    |
  +================================================+
```

---

### 5. CountdownTimer (Lines 624-794)

**Purpose:** Core timer logic and execution

**Methods:**

#### `parse_time(time_str, metric=False)`
Parses various time formats into seconds (or milliseconds for metric).

**Supported Formats:**
- `5m` → 300 seconds
- `30s` → 30 seconds
- `1h30m` → 5400 seconds
- `2h15m30s` → 8130 seconds
- `01:30:00` → 5400 seconds
- `90:00` → 5400 seconds (90 minutes)

**Returns:** Integer (seconds for standard, milliseconds for metric)

**Validation:**
- Standard mode: Max 99:59:59 (359999 seconds)
- Metric mode: Max 99:99:99 metric (999999000 ms)

#### `play_beeps(freq, count, duration, gap, silent, loop)`
Plays audio alerts when timer finishes.

**Process:**
1. Check if silent mode → return early
2. Determine beep count (1 if loop mode, else count)
3. Try Linux `beep` command:
   ```python
   subprocess.run(['beep', '-f', str(freq), '-l', str(duration)])
   ```
4. If `beep` not found → fallback to terminal bell (`\a`)
5. Sleep for gap duration between beeps

#### `run(total_seconds, beep_freq, beep_count, beep_duration, beep_gap, silent, loop, metric)`
Main countdown execution loop.

**Parameters:**
- `total_seconds` - Countdown duration
- `beep_freq` - Frequency in Hz (37-32767)
- `beep_count` - Number of beeps (1-100)
- `beep_duration` - Beep length in ms
- `beep_gap` - Gap between beeps in ms
- `silent` - Disable beeps
- `loop` - Auto-restart when finished
- `metric` - Use base-100 time display

**Process:**
1. Determine which time units to show (hours/minutes/seconds)
2. Calculate start and end times
3. Create DisplayManager and ConsoleManager
4. Draw static UI
5. **Main loop:**
   - Calculate remaining time
   - Format time string
   - Update display
   - Check if time <= 0
   - Sleep for update interval (50ms standard, 10ms metric)
6. Draw finished screen
7. Play beeps
8. If loop: restart from step 5

**Loop Mode:**
- Restarts countdown automatically
- Plays only 1 beep (not full count)
- Continues until Ctrl+C

#### `run_clock()`
Clock mode - displays current time continuously.

**Process:**
1. Create DisplayManager and ConsoleManager
2. Draw clock UI
3. **Infinite loop:**
   - Get current time: `datetime.now()`
   - Format as HH:MM:SS
   - Update display with current time
   - Sleep 50ms
4. Runs until Ctrl+C (KeyboardInterrupt)

---

## Key Functions

### get_effective_args(config) (Lines 798-842)

**Purpose:** Apply config defaults to command-line arguments

**Logic:**

1. **No-args default:**
   - If `enable_no_args_default` is True
   - And user provides no arguments
   - Replace with `no_args_default_command` (e.g., "help")

2. **Time-only defaults:**
   - If `enable_time_only_defaults` is True
   - And user provides only time (no flags)
   - Auto-inject flags from `time_only_default_flags`
   - Example: `wincountdown 5m` → `wincountdown 5m -l -s`

**Returns:** Modified sys.argv list

---

### parse_arguments(effective_args) (Lines 844-898)

**Purpose:** Parse command-line arguments using argparse

**Arguments:**

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `time` | positional | Time string (5m, HH:MM:SS) | required |
| `-s, --silent` | flag | Disable beeps | False |
| `-l, --loop` | flag | Auto-restart countdown | False |
| `-m, --metric` | flag | Base-100 time display | False |
| `-f HZ` | int | Beep frequency (37-32767 Hz) | 800 |
| `-b COUNT` | int | Number of beeps (1-100) | 3 |
| `-d MS` | int | Beep duration (ms) | 1000 |
| `-g MS` | int | Gap between beeps (ms) | 300 |
| `-c, --clock` | flag | Clock mode | False |
| `--debug` | flag | Enable debug logging | False |

**Returns:** argparse.Namespace object

---

### validate_arguments(args) (Lines 900-932)

**Purpose:** Validate parsed arguments

**Checks:**

1. **Frequency:** 37 ≤ freq ≤ 32767 Hz
2. **Beep count:** 1 ≤ count ≤ 100
3. **Time limits:**
   - Standard mode: ≤ 99:59:59 (359999 seconds)
   - Metric mode: ≤ 99:99:99 metric

**On Error:** Prints error message and exits

---

### print_help() (Lines 934-1028)

**Purpose:** Display comprehensive help text

**Sections:**
1. ASCII art title
2. Description
3. Usage examples
4. Syntax
5. Arguments table
6. Time format examples
7. Advanced features (loop, metric, config)
8. Beep customization
9. File locations
10. Credits

---

## Configuration System

### File Locations (XDG Base Directory)

```
~/.config/wincountdown/config.json    # User configuration
~/.cache/wincountdown/debug.log       # Debug logs
```

### Config Creation Flow

```
User runs wincountdown first time
  └─> ConfigManager.load()
       └─> Check if ~/.config/wincountdown/config.json exists
            └─> NO: Create directories
                 └─> Generate JSON with create_config_content()
                 └─> Write to config.json
                 └─> Load and return config

            └─> YES: Read file
                 └─> Parse JSON (skip "//"-prefixed comment lines)
                 └─> Validate ASCII digits
                 └─> Merge with DEFAULT_CONFIG (for new keys)
                 └─> Return config
```

### Comment System

Config uses JSON with pseudo-comments:
```json
{
    "//": "This is a comment line",
    "//note": "Comment lines start with //",
    "actual_setting": true
}
```

ConfigManager filters out keys starting with `"//"` during parsing.

---

## Display System

### ASCII Art Structure

Each digit is **8 lines tall × 11 characters wide**:

```
" ######### "   ← Line 0 (11 chars)
"###     ###"   ← Line 1
"###     ###"   ← Line 2
"###     ###"   ← Line 3
"###     ###"   ← Line 4
"###     ###"   ← Line 5
"###     ###"   ← Line 6
" ######### "   ← Line 7
```

### Time Rendering Process

**Input:** `"12:34:56"` (8 characters)

**Process:**
1. Get ASCII art for each character: `1`, `2`, `:`, `3`, `4`, `:`, `5`, `6`
2. For each of 8 lines:
   - Concatenate line 0 from all characters
   - Result: line 0 of final display (88 chars: 8 × 11)
3. Return list of 8 concatenated lines

**Output:**
```
    ###     ######### ........(88 chars total)
  #####    ###     ###........
    ###    ###     ###........
    ###     ######### ........
    ###    ###     ###........
    ###    ###     ###........
    ###    ###     ###........
#####################........
```

### Display Update Efficiency

**Inefficient Approach (not used):**
- Clear entire screen
- Redraw all UI elements
- Causes flicker

**Efficient Approach (actual implementation):**
- Draw static UI once (borders, labels)
- **Only update time display area:**
  - Move cursor to line 8
  - Overwrite 8 lines of ASCII art
  - Leave borders/labels untouched

**Update Frequency:**
- Standard mode: 50ms (20 FPS)
- Metric mode: 10ms (100 FPS) - needed for fast metric seconds

---

## Execution Flow

### Complete Program Flow Diagram

```
START
  │
  ├─> main()
  │     │
  │     ├─> ConfigManager()
  │     │     └─> Load ~/.config/wincountdown/config.json
  │     │
  │     ├─> Logger.setup() if --debug flag
  │     │
  │     ├─> get_effective_args(config)
  │     │     ├─> Apply no-args default?
  │     │     └─> Apply time-only defaults?
  │     │
  │     ├─> parse_arguments(effective_args)
  │     │     └─> argparse creates args object
  │     │
  │     ├─> Check for --help flag
  │     │     └─> YES: print_help() → EXIT
  │     │
  │     ├─> validate_arguments(args)
  │     │     └─> Invalid? → Print error → EXIT
  │     │
  │     ├─> Create DisplayManager(ascii_digits)
  │     │
  │     ├─> Create CountdownTimer()
  │     │
  │     └─> Branch:
  │           │
  │           ├─> --clock flag?
  │           │     └─> YES: timer.run_clock() → Loop forever
  │           │
  │           └─> NO: Timer mode
  │                 ├─> timer.parse_time(args.time)
  │                 ├─> timer.run(total_seconds, ...)
  │                 │     │
  │                 │     ├─> display.draw_static_ui()
  │                 │     │
  │                 │     ├─> LOOP: Until time = 0
  │                 │     │     ├─> Calculate remaining
  │                 │     │     ├─> Format time string
  │                 │     │     ├─> display.update_time_display()
  │                 │     │     └─> sleep(UPDATE_INTERVAL)
  │                 │     │
  │                 │     ├─> display.draw_finished_screen()
  │                 │     │
  │                 │     ├─> timer.play_beeps()
  │                 │     │
  │                 │     └─> Loop mode?
  │                 │           └─> YES: Restart countdown
  │                 │           └─> NO: Exit
  │                 │
  │                 └─> Ctrl+C (KeyboardInterrupt)
  │                       └─> console.show_cursor()
  │                       └─> EXIT
  │
EXIT
```

### Error Handling

**Graceful Exit:**
```python
try:
    # Main timer loop
except KeyboardInterrupt:
    # User pressed Ctrl+C
    console.show_cursor()  # Restore cursor
    sys.exit(0)            # Clean exit
```

**Config Errors:**
- Missing config → Auto-create with defaults
- Invalid JSON → Print warning, use DEFAULT_CONFIG
- Invalid ASCII digits → Fall back to DEFAULT_ASCII_DIGITS

**Audio Errors:**
- `beep` command not found → Use terminal bell (`\a`)
- `beep` permission error → Use terminal bell

---

## Key Algorithms

### Time Parsing Algorithm

```python
def parse_time(time_str):
    # Try colon format first (HH:MM:SS or MM:SS)
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

    # Try component format (1h30m45s)
    hours = minutes = seconds = 0
    current_num = ""

    for char in time_str:
        if char.isdigit():
            current_num += char
        elif char in 'hms':
            if char == 'h':
                hours = int(current_num)
            elif char == 'm':
                minutes = int(current_num)
            elif char == 's':
                seconds = int(current_num)
            current_num = ""

    total = hours * 3600 + minutes * 60 + seconds
    return total * 1000 if metric else total  # Metric uses milliseconds
```

### Metric Time Conversion

**Real Time → Metric Time:**
- 1 real second = 1.1574 metric seconds
- 1 metric hour = 100 metric minutes
- 1 metric minute = 100 metric seconds

```python
# Total real milliseconds → Total metric milliseconds
metric_ms = real_seconds * 1000

# Display as MM:HH:SS
metric_seconds = metric_ms // 1000
metric_hours = metric_seconds // 10000
metric_minutes = (metric_seconds // 100) % 100
metric_secs = metric_seconds % 100
```

---

## Performance Considerations

1. **Update Intervals:**
   - Standard: 50ms (plenty for 1-second countdown)
   - Metric: 10ms (100 updates/sec for smooth metric display)

2. **String Building:**
   - Uses list comprehension + join (not concatenation)
   - Example: `''.join([line for line in ascii_lines])`

3. **Display Updates:**
   - Only redraws time portion (8 lines)
   - Doesn't redraw static borders/labels
   - Reduces flicker and improves performance

4. **Cursor Management:**
   - Hides cursor during updates
   - Shows on exit (even on error via context manager)
   - Prevents cursor flicker

---

## Summary

**Total Lines:** 1,136 lines (excluding blank lines)

**Core Components:**
1. **Logger** - Debug logging
2. **ConsoleManager** - Terminal control (ANSI)
3. **ConfigManager** - XDG-compliant config management
4. **DisplayManager** - ASCII art rendering
5. **CountdownTimer** - Timer logic & execution

**Key Features:**
- Flexible time input parsing
- Customizable ASCII art
- XDG directory compliance
- Efficient display updates
- Graceful error handling
- Loop mode for repeated timers
- Clock mode for time display
- Metric time "joke mode"

**Dependencies:**
- Python 3.6+ standard library only
- Optional: `beep` command for audio

**File Locations:**
- Config: `~/.config/wincountdown/config.json`
- Logs: `~/.cache/wincountdown/debug.log`
