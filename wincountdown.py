#!/usr/bin/env python3
"""
wincountdown - A countdown timer and clock for Linux
with large ASCII art display and customizable alerts
"""

import sys
import time
import os
import argparse
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONSTANTS
# ============================================================================

# Console constants
BORDER_WIDTH = 115
ASCII_HEIGHT = 8

# Time constants  
MAX_STANDARD_SECONDS = 359999  # 99:59:59
MAX_METRIC_MILLISECONDS = 999999000  # 99:99:99 metric

# Display constants
UPDATE_INTERVAL_STANDARD = 0.05
UPDATE_INTERVAL_METRIC = 0.01

# Default ASCII art for digits
DEFAULT_ASCII_DIGITS = {
    '0': [
        " ######### ",
        "###     ###",
        "###     ###",
        "###     ###",
        "###     ###",
        "###     ###",
        "###     ###",
        " ######### "
    ],
    '1': [
        "    ###    ",
        "  #####    ",
        "    ###    ",
        "    ###    ",
        "    ###    ",
        "    ###    ",
        "    ###    ",
        "###########"
    ],
    '2': [
        " ######### ",
        "###     ###",
        "        ###",
        "      ###  ",
        "    ###    ",
        "  ###      ",
        " ###       ",
        "###########"
    ],
    '3': [
        "###########",
        "        ###",
        "        ###",
        "  #########",
        "        ###",
        "        ###",
        "        ###",
        "###########"
    ],
    '4': [
        "     ##### ",
        "    ###### ",
        "   ### ### ",
        "  ###  ### ",
        " ###   ### ",
        "###########",
        "       ### ",
        "       ### "
    ],
    '5': [
        "###########",
        "###        ",
        "###        ",
        "###########",
        "        ###",
        "        ###",
        "###     ###",
        " ######### "
    ],
    '6': [
        "  #########",
        " ###       ",
        "###        ",
        "###########",
        "###     ###",
        "###     ###",
        "###     ###",
        " ######### "
    ],
    '7': [
        "###########",
        "        ###",
        "       ### ",
        "      ###  ",
        "     ###   ",
        "    ###    ",
        "   ###     ",
        "   ###     "
    ],
    '8': [
        " ######### ",
        "###     ###",
        "###     ###",
        " ######### ",
        "###     ###",
        "###     ###",
        "###     ###",
        " ######### "
    ],
    '9': [
        " ######### ",
        "###     ###",
        "###     ###",
        "###     ###",
        " ##########",
        "        ###",
        "       ### ",
        "########   "
    ],
    ':': [
        "           ",
        "    ###    ",
        "    ###    ",
        "           ",
        "           ",
        "    ###    ",
        "    ###    ",
        "           "
    ]
}

# Default configuration
DEFAULT_CONFIG = {
    "debug_mode": False,
    "default_frequency": 800,
    "default_beeps": 3,
    "default_duration": 1000,
    "default_gap": 300,
    "default_silent": False,
    "default_loop": False,
    "default_metric": False,
    "enable_no_args_default": False,
    "no_args_default_command": "help",
    "enable_time_only_defaults": False,
    "time_only_default_flags": [],
    "ascii_digits": DEFAULT_ASCII_DIGITS
}

# ============================================================================
# ANSI ESCAPE CODES FOR TERMINAL CONTROL
# ============================================================================

ANSI_HIDE_CURSOR = '\033[?25l'
ANSI_SHOW_CURSOR = '\033[?25h'
ANSI_CLEAR_SCREEN = '\033[2J\033[H'

def ansi_move_cursor(x, y):
    """Generate ANSI escape code to move cursor to position (x, y)"""
    return f'\033[{y+1};{x+1}H'

# ============================================================================
# LOGGER CLASS
# ============================================================================

class Logger:
    """Simple logger that can be enabled/disabled via config"""
    
    def __init__(self):
        self.enabled = False
        self.file_path = None
        
    def setup(self, enabled, file_path):
        """Setup logger with debug mode and file path"""
        self.enabled = enabled
        self.file_path = file_path
        
        if enabled and file_path and os.path.exists(file_path):
            os.remove(file_path)
    
    def log(self, message):
        """Log message if debugging is enabled"""
        if not self.enabled:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}\n"
        
        if self.file_path:
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        print(log_message.rstrip())

# Global logger instance
logger = Logger()

# ============================================================================
# CONSOLE MANAGER CLASS
# ============================================================================

class ConsoleManager:
    """Handles all console/terminal operations using ANSI escape codes"""

    def __init__(self):
        pass

    def hide_cursor(self):
        """Hide the console cursor to prevent flickering"""
        print(ANSI_HIDE_CURSOR, end='', flush=True)

    def show_cursor(self):
        """Show the console cursor again"""
        print(ANSI_SHOW_CURSOR, end='', flush=True)

    def set_position(self, x, y):
        """Move cursor to specific position without clearing"""
        print(ansi_move_cursor(x, y), end='', flush=True)

    def clear_screen(self):
        """Clear screen"""
        print(ANSI_CLEAR_SCREEN, end='', flush=True)

    def __enter__(self):
        """Context manager entry - hide cursor"""
        self.hide_cursor()
        return self

    def __exit__(self, *args):
        """Context manager exit - show cursor"""
        self.show_cursor()

# ============================================================================
# CONFIG MANAGER CLASS
# ============================================================================

class ConfigManager:
    """Handles configuration loading and creation"""

    def __init__(self, script_dir=None):
        # Use XDG Base Directory specification for Linux
        config_dir = Path.home() / '.config' / 'wincountdown'
        cache_dir = Path.home() / '.cache' / 'wincountdown'

        # Create directories if they don't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = str(config_dir / 'config.json')
        self.debug_log_file = str(cache_dir / 'debug.log')
        
    def create_config_content(self):
        """Create a configuration file with detailed comments"""
        return '''{
    "//": "================================================================",
    "//1": "WINCOUNTDOWN CONFIGURATION FILE",
    "//2": "================================================================",
    "//3": "Customize default settings for wincountdown timer and clock.",
    "//4": "All settings can be overridden by command-line flags.",
    "//5": "",

    "//debug_section": "--- DEBUG MODE ---",
    "//debug_note1": "Logs detailed execution info to ~/.cache/wincountdown/debug.log",
    "//debug_note2": "Can also be enabled with --debug flag (recommended for troubleshooting)",

    "debug_mode": false,

    "//separator1": "",
    "//defaults_section": "--- DEFAULT SETTINGS ---",
    "//defaults_note": "These values are used unless overridden by command-line flags",

    "//beep_header": "",
    "//beep_desc": "Beep Alert Configuration",

    "default_frequency": 800,
    "//freq_note": "Frequency in Hz (37-32767). Examples: 440 (musical A), 800 (default), 1000 (high pitch)",

    "default_beeps": 3,
    "//beeps_note": "Number of times to beep when countdown finishes (minimum: 1)",

    "default_duration": 1000,
    "//duration_note": "How long each beep lasts in milliseconds (1000ms = 1 second)",

    "default_gap": 300,
    "//gap_note": "Pause between beeps in milliseconds (only used when beeps > 1)",

    "//mode_header": "",
    "//mode_desc": "Default Mode Settings",

    "default_silent": false,
    "//silent_note": "Silent mode: true = no beeps, false = beeps enabled. Override with -s flag.",

    "default_loop": false,
    "//loop_note": "Loop mode: true = auto-restart timer, false = stop after finish. Override with -l flag.",

    "default_metric": false,
    "//metric_note": "Metric time (joke mode): true = display in base-100 time (1h=100m, 1m=100s), false = normal time",

    "//separator2": "",
    "//advanced_section": "--- ADVANCED BEHAVIORS ---",
    "//advanced_note": "These options enable power-user features and custom workflows",

    "//noargs_header": "",
    "//noargs_desc": "No-Arguments Behavior",
    "//noargs_explain": "Controls what happens when you type 'wincountdown' with no arguments",

    "enable_no_args_default": false,
    "//enable_noargs_note": "Set to true to run a custom command instead of showing help screen",

    "no_args_default_command": "help",
    "//noargs_cmd_note1": "Options:",
    "//noargs_cmd_note2": "  'help' = show help screen (default behavior)",
    "//noargs_cmd_note3": "  '25m' = start 25-minute timer immediately",
    "//noargs_cmd_note4": "  '5m -l -s' = start 5-minute silent looping timer",
    "//noargs_cmd_note5": "  '--clock' = launch clock mode",
    "//noargs_cmd_example": "Example: Set to '25m' for instant Pomodoro timer",

    "//timeonly_header": "",
    "//timeonly_desc": "Time-Only Arguments Behavior",
    "//timeonly_explain": "Auto-inject flags when user provides ONLY a time (no other flags)",
    "//timeonly_example": "Example: Make 'wincountdown 5m' behave like 'wincountdown 5m -l -s'",

    "enable_time_only_defaults": false,
    "//enable_timeonly_note": "Set to true to automatically add flags when only time is provided",

    "time_only_default_flags": [],
    "//timeonly_flags_note1": "Flags to auto-add when user types just time (e.g., 'wincountdown 5m'):",
    "//timeonly_flags_note2": "  [\\"-l\\\", \\\"-s\\\"] = always loop and silent",
    "//timeonly_flags_note3": "  [\\"-l\\\"] = always loop",
    "//timeonly_flags_note4": "  [\\"-f\\\", \\\"1000\\\", \\\"-b\\\", \\\"5\\\"] = custom beep pattern",
    "//timeonly_flags_note5": "Available flags: -s -l -m -f -b -d -g",
    "//timeonly_flags_note6": "Note: Only works when NO flags are typed. Manual flags disable this behavior.",

    "//separator3": "",
    "//ascii_section": "--- ASCII ART CUSTOMIZATION ---",
    "//ascii_note1": "Customize how digits (0-9) and colon (:) appear in the display",
    "//ascii_note2": "Use any characters: # * @ █ ░ ▓ or plain text",
    "//ascii_note3": "",
    "//ascii_rules": "Rules:",
    "//ascii_rules1": "  - Each digit must be exactly 8 lines tall",
    "//ascii_rules2": "  - Keep all digits the same width (11 characters recommended)",
    "//ascii_rules3": "  - Invalid/missing digits automatically fall back to defaults",
    "//ascii_rules4": "",
    "//ascii_tip": "Tip: Test your changes with: wincountdown 10s",
    "//ascii_blank": "",

    "ascii_digits": ''' + json.dumps(DEFAULT_ASCII_DIGITS, indent=8) + '''
}'''
    
    def load(self):
        """Load configuration from file, create with defaults if it doesn't exist"""
        logger.log(f"Loading config from: {self.config_file}")
        logger.log(f"Config file exists: {os.path.exists(self.config_file)}")
        
        if not os.path.exists(self.config_file):
            logger.log("Config file does not exist, creating new one")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(self.create_config_content())
            print(f"Created default configuration file: {self.config_file}")
            print("You can edit this file to customize default settings.\n")
            return DEFAULT_CONFIG.copy()
        
        try:
            logger.log("Attempting to read config file")
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.log(f"Raw config loaded from file: {config}")
            
            # Filter out comment fields (they start with //)
            filtered_config = {k: v for k, v in config.items() if not k.startswith('//')}
            logger.log(f"Filtered config (comments removed): {filtered_config}")
            
            # Merge with defaults to ensure all keys exist
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(filtered_config)
            
            # Validate ascii_digits if present
            if 'ascii_digits' in filtered_config:
                self._validate_ascii_digits(filtered_config['ascii_digits'], merged_config)
            
            # Setup logger with debug mode from config
            logger.setup(merged_config.get('debug_mode', False), self.debug_log_file)
            logger.log(f"DEBUG mode set to: {merged_config.get('debug_mode', False)}")
            logger.log(f"Final merged config: {merged_config}")
            
            return merged_config
            
        except (json.JSONDecodeError, IOError) as e:
            error_msg = f"Warning: Could not read config file ({e}), using defaults"
            logger.log(error_msg)
            print(error_msg)
            return DEFAULT_CONFIG.copy()
    
    def _validate_ascii_digits(self, ascii_digits, merged_config):
        """Validate ASCII art digits configuration"""
        for digit in '0123456789:':
            if digit not in ascii_digits:
                logger.log(f"Warning: Missing ASCII art for '{digit}', using default")
                ascii_digits[digit] = DEFAULT_ASCII_DIGITS[digit]
            elif not isinstance(ascii_digits[digit], list) or len(ascii_digits[digit]) != ASCII_HEIGHT:
                logger.log(f"Warning: Invalid ASCII art for '{digit}' (must be {ASCII_HEIGHT} lines), using default")
                ascii_digits[digit] = DEFAULT_ASCII_DIGITS[digit]

# ============================================================================
# DISPLAY MANAGER CLASS
# ============================================================================

class DisplayManager:
    """Handles all display formatting and rendering"""
    
    def __init__(self, ascii_art):
        self.ascii_art = ascii_art
        
    def draw_border(self, char='='):
        """Draw a border line"""
        return f"  +{char * BORDER_WIDTH}+"
    
    def draw_line(self, content='', centered=False):
        """Draw a line with optional centered content"""
        if centered and content:
            padding = (BORDER_WIDTH - len(content)) // 2
            return f"  |{' ' * padding}{content}{' ' * (BORDER_WIDTH - padding - len(content))}|"
        return f"  |{content:{BORDER_WIDTH}}|"
    
    def get_ascii_digit(self, digit):
        """Return ASCII art for a single digit from config"""
        return self.ascii_art.get(digit, ["           "] * ASCII_HEIGHT)
    
    def render_time(self, hours, minutes, seconds, show_hours, show_minutes):
        """Render time as ASCII art - only show relevant units"""
        if show_hours:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif show_minutes:
            time_str = f"{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{seconds:02d}"
        
        # Use list comprehension and join for better performance
        lines = []
        for i in range(ASCII_HEIGHT):
            line_parts = []
            for char in time_str:
                digit_art = self.get_ascii_digit(char)
                line_parts.append(digit_art[i])
                line_parts.append("  ")
            lines.append(''.join(line_parts))
        
        return lines
    
    def draw_static_ui(self, total_seconds, show_hours, show_minutes, metric=False, 
                      start_time_str="", end_time_str="", console=None):
        """Draw the static parts of the UI once"""
        if console:
            console.clear_screen()
        else:
            os.system('clear')
        
        # Format the initial time for display
        if metric:
            total_metric_seconds = total_seconds // 1000
            hours = total_metric_seconds // 10000
            minutes = (total_metric_seconds % 10000) // 100
            seconds = total_metric_seconds % 100
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
        
        if show_hours:
            time_display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif show_minutes:
            time_display = f"{minutes:02d}:{seconds:02d}"
        else:
            time_display = f"{seconds:02d}"
        
        # Top border with decoration
        print("\n")
        print(self.draw_border())
        print(self.draw_line())
        title = f">>>  C O U N T D O W N  [ {time_display} ]  <<<"
        print(self.draw_line(title, centered=True))
        print(self.draw_line())
        print(self.draw_border())
        print()
        print()
        
        # Reserve space for the time display
        for _ in range(ASCII_HEIGHT):
            print()
        
        print()
        print()
        
        # Bottom decoration with start and end times
        print(self.draw_border())
        
        # First line: labels
        start_label = "Start time:"
        center_text = "Press Ctrl+C to stop"
        end_label = "End time:"
        
        total_side_length = len(start_label) + len(end_label)
        remaining_space = BORDER_WIDTH - total_side_length - len(center_text)
        left_space = remaining_space // 2
        right_space = remaining_space - left_space
        
        print("  |" + start_label + " " * left_space + center_text + 
              " " * right_space + end_label + "|")
        
        # Second line: actual times
        space_between = BORDER_WIDTH - len(start_time_str) - len(end_time_str)
        print("  |" + start_time_str + " " * space_between + end_time_str + "|")
        
        print(self.draw_border())
        print("  stropitor")
    
    def update_time_display(self, hours, minutes, seconds, show_hours, show_minutes, console):
        """Update only the time display portion"""
        lines = self.render_time(hours, minutes, seconds, show_hours, show_minutes)
        
        # Calculate the actual width of the time display
        time_width = len(lines[0])
        
        # Center within the box - pre-calculate padding
        x_offset = 3 + (BORDER_WIDTH - time_width) // 2
        left_padding = " " * x_offset
        right_padding = " " * (120 - x_offset - time_width)
        
        # Draw all lines in one pass
        for i, line in enumerate(lines):
            console.set_position(0, 8 + i)
            # Build the full line more efficiently
            print(f"{left_padding}{line.rstrip()}{right_padding}"[:120], end='', flush=True)
    
    def draw_finished_screen(self, show_hours, show_minutes, loop=False):
        """Draw the time's up screen"""
        os.system('clear')

        print("\n")
        print(self.draw_border())
        print(self.draw_line())

        if loop:
            title = ">>>  R E S T A R T I N G . . .  <<<"
        else:
            title = ">>>  T I M E ' S   U P !  <<<"

        print(self.draw_line(title, centered=True))
        print(self.draw_line())
        print(self.draw_border())
        print()
        print()

        # Show final time (00:00:00 or 00:00 or 00)
        if show_hours:
            lines = self.render_time(0, 0, 0, True, True)
        elif show_minutes:
            lines = self.render_time(0, 0, 0, False, True)
        else:
            lines = self.render_time(0, 0, 0, False, False)

        # Center the final time display
        time_width = len(lines[0])
        x_offset = 2 + (BORDER_WIDTH - time_width) // 2

        for line in lines:
            print(" " * x_offset + line)

        print()
        print()
        print(self.draw_border())
        print(self.draw_line())
        print(self.draw_border())
        print("  stropitor")

    def draw_clock_ui(self, console=None):
        """Draw the static parts of the clock UI once"""
        if console:
            console.clear_screen()
        else:
            os.system('clear')

        # Top border with decoration
        print("\n")
        print(self.draw_border())
        print(self.draw_line())
        title = ">>>  C L O C K   M O D E  <<<"
        print(self.draw_line(title, centered=True))
        print(self.draw_line())
        print(self.draw_border())
        print()
        print()

        # Reserve space for the time display
        for _ in range(ASCII_HEIGHT):
            print()

        print()
        print()

        # Bottom decoration
        print(self.draw_border())

        center_text = "Press Ctrl+C to exit"
        left_space = (BORDER_WIDTH - len(center_text)) // 2
        right_space = BORDER_WIDTH - left_space - len(center_text)

        print("  |" + " " * left_space + center_text + " " * right_space + "|")

        print(self.draw_border())
        print("  stropitor")

# ============================================================================
# TIMER CLASS
# ============================================================================

class CountdownTimer:
    """Main countdown timer logic"""
    
    def __init__(self, config):
        self.config = config
        self.display = DisplayManager(config.get('ascii_digits', DEFAULT_ASCII_DIGITS))
        
    def parse_time(self, time_str, metric=False):
        """Parse time string in various formats"""
        hours = minutes = seconds = 0
        
        # Check if it's in HH:MM:SS format
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            elif len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
        else:
            # Parse format like 1h30m45s - more efficient approach
            time_str = time_str.lower()
            
            # Extract hours
            if 'h' in time_str:
                h_parts = time_str.split('h', 1)
                hours = int(h_parts[0])
                time_str = h_parts[1]
            
            # Extract minutes  
            if 'm' in time_str:
                m_parts = time_str.split('m', 1)
                minutes = int(m_parts[0]) if m_parts[0] else 0
                time_str = m_parts[1]
            
            # Extract seconds
            if 's' in time_str:
                s_parts = time_str.split('s', 1)
                seconds = int(s_parts[0]) if s_parts[0] else 0
        
        # Calculate total seconds
        real_seconds = hours * 3600 + minutes * 60 + seconds
        
        # Return milliseconds for metric, seconds for standard
        return int(real_seconds * 1000) if metric else real_seconds
    
    def play_beeps(self, freq, count, duration, gap, silent, loop):
        """Play beep sounds when timer finishes"""
        if silent:
            return

        beeps_to_play = 1 if loop else count

        # Try using the 'beep' command (requires beep package on Linux)
        try:
            for i in range(beeps_to_play):
                # beep command: -f frequency (Hz), -l length (ms)
                subprocess.run(['beep', '-f', str(freq), '-l', str(duration)],
                             check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if i < beeps_to_play - 1:
                    time.sleep(gap / 1000.0)
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback to terminal bell character if beep command not available
            for i in range(beeps_to_play):
                print('\a', end='', flush=True)
                if i < beeps_to_play - 1:
                    time.sleep(gap / 1000.0)
    
    def run(self, total_seconds, beep_freq=800, beep_count=3, beep_duration=1000, 
            beep_gap=300, silent=False, loop=False, metric=False):
        """Run the countdown timer"""
        
        # Determine what units to show
        if metric:
            show_hours = total_seconds >= 10000000  # >= 1 metric hour
            show_minutes = total_seconds >= 100000   # >= 1 metric minute
        else:
            show_hours = total_seconds >= 3600
            show_minutes = total_seconds >= 60
        
        with ConsoleManager() as console:
            try:
                while True:  # Outer loop for restart functionality
                    # Calculate start and end times
                    import datetime
                    start_datetime = datetime.datetime.now()
                    start_time_str = start_datetime.strftime("%H:%M:%S")
                    
                    # Calculate end time
                    if metric:
                        duration_seconds = total_seconds / 1000
                    else:
                        duration_seconds = total_seconds
                    
                    end_datetime = start_datetime + datetime.timedelta(seconds=duration_seconds)
                    end_time_str = end_datetime.strftime("%H:%M:%S")
                    
                    self.display.draw_static_ui(total_seconds, show_hours, show_minutes, 
                                               metric, start_time_str, end_time_str, console)
                    
                    start_time = time.time()
                    last_remaining = -1
                    
                    while True:
                        if metric:
                            elapsed_ms = int((time.time() - start_time) * 1000)
                            remaining = total_seconds - elapsed_ms
                        else:
                            elapsed = int(time.time() - start_time)
                            remaining = total_seconds - elapsed
                        
                        if remaining < 0:
                            break
                        
                        # Only update display when the second changes
                        if remaining != last_remaining:
                            if metric:
                                total_metric_seconds = remaining // 1000
                                hours = total_metric_seconds // 10000
                                minutes = (total_metric_seconds % 10000) // 100
                                seconds = total_metric_seconds % 100
                            else:
                                hours = remaining // 3600
                                minutes = (remaining % 3600) // 60
                                seconds = remaining % 60
                            
                            self.display.update_time_display(hours, minutes, seconds, 
                                                            show_hours, show_minutes, console)
                            last_remaining = remaining
                        
                        time.sleep(UPDATE_INTERVAL_METRIC if metric else UPDATE_INTERVAL_STANDARD)
                    
                    # Time's up!
                    self.display.draw_finished_screen(show_hours, show_minutes, loop)
                    
                    # Play beeps
                    self.play_beeps(beep_freq, beep_count, beep_duration, beep_gap, silent, loop)
                    
                    if not loop:
                        break
                    
                    time.sleep(1)  # Wait before restarting
                    
            except KeyboardInterrupt:
                raise  # Re-raise to be handled by main

    def run_clock(self):
        """Run the clock mode - displays current system time"""
        with ConsoleManager() as console:
            try:
                # Draw the static UI once
                self.display.draw_clock_ui(console)

                last_second = -1

                while True:
                    # Get current time
                    now = datetime.now()
                    hours = now.hour
                    minutes = now.minute
                    seconds = now.second

                    # Only update display when the second changes
                    if seconds != last_second:
                        # Always show hours and minutes in clock mode
                        self.display.update_time_display(hours, minutes, seconds,
                                                        True, True, console)
                        last_second = seconds

                    time.sleep(0.05)  # Update every 50ms

            except KeyboardInterrupt:
                raise  # Re-raise to be handled by main

# ============================================================================
# ARGUMENT PROCESSING
# ============================================================================

def get_effective_args(config):
    """Get effective arguments considering config defaults"""
    logger.log("get_effective_args called")
    args = sys.argv[1:]
    
    logger.log(f"Initial args: {args}")
    
    # Handle no arguments case
    if not args:
        logger.log(f"No args provided, checking enable_no_args_default")
        if config.get("enable_no_args_default", False):
            cmd = config.get("no_args_default_command", "help")
            logger.log(f"Using no_args_default_command: {cmd}")
            if cmd == "help":
                return None  # Signal to show help
            return shlex.split(cmd)
        return None  # Show help by default
    
    # Handle time-only case
    user_args = [arg for arg in args if not arg.startswith('-')]
    flag_args = [arg for arg in args if arg.startswith('-')]
    
    logger.log(f"user_args: {user_args}, flag_args: {flag_args}")
    
    if len(user_args) == 1 and len(flag_args) == 0:
        if config.get("enable_time_only_defaults", False):
            default_flags = config.get("time_only_default_flags", [])
            logger.log(f"Adding time_only_default_flags: {default_flags}")
            args.extend(default_flags)
    
    logger.log(f"Final effective args: {args}")
    return args

def parse_arguments(args, config):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        prog='wincountdown',
        description='A countdown timer with ASCII art display for Windows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    parser.add_argument('time', nargs='?', help='Time duration')
    parser.add_argument('-s', '--silent', action='store_true', 
                        default=config.get('default_silent', False))
    parser.add_argument('-f', '--freq', type=int, 
                        default=config.get('default_frequency', 800), metavar='HZ')
    parser.add_argument('-b', '--beeps', type=int, 
                        default=config.get('default_beeps', 3), metavar='N')
    parser.add_argument('-d', '--duration', type=int, 
                        default=config.get('default_duration', 1000), metavar='MS')
    parser.add_argument('-g', '--gap', type=int, 
                        default=config.get('default_gap', 300), metavar='MS')
    parser.add_argument('-l', '--loop', action='store_true',
                        default=config.get('default_loop', False))
    parser.add_argument('-m', '--metric', action='store_true',
                        default=config.get('default_metric', False))
    parser.add_argument('-c', '--clock', action='store_true',
                        help='Clock mode - display current system time')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (logs to wincountdown-debug.log)')

    return parser.parse_args(args)

def validate_arguments(args, metric=False):
    """Validate argument constraints"""
    errors = []
    
    if not 37 <= args.freq <= 32767:
        errors.append("Frequency must be between 37 and 32767 Hz")
    
    if args.beeps < 1:
        errors.append("Number of beeps must be at least 1")
    
    if args.duration < 1:
        errors.append("Beep duration must be at least 1 millisecond")
    
    if args.gap < 0:
        errors.append("Beep gap cannot be negative")
    
    return errors

# ============================================================================
# HELP SCREEN
# ============================================================================

def print_help():
    """Print a beautifully formatted help screen"""
    help_text = """
  +===================================================================================================================+
  |                                                                                                                   |
  |      ##      ## #### ##     ##  ####   ####  ##     ## ##     ## ######## ####    ####  ##      ## ##     ##      |
  |      ##  ##  ##  ##  ###    ## ##  ## ##  ## ##     ## ###    ##    ##    ##  ## ##  ## ##  ##  ## ###    ##      |
  |      ##  ##  ##  ##  ####   ## ##     ##  ## ##     ## ####   ##    ##    ##  ## ##  ## ##  ##  ## ####   ##      |
  |      ##  ##  ##  ##  ## ##  ## ##     ##  ## ##     ## ## ##  ##    ##    ##  ## ##  ## ##  ##  ## ## ##  ##      |
  |      ##  ##  ##  ##  ##  ## ## ##     ##  ## ##     ## ##  ## ##    ##    ##  ## ##  ## ##  ##  ## ##  ## ##      |
  |      ##  ##  ##  ##  ##   #### ##  ## ##  ## ##     ## ##   ####    ##    ##  ## ##  ## ##  ##  ## ##   ####      |
  |      ###    ### #### ##    ###  ####   ####   #######  ##    ###    ##    ####    ####   ###  ###  ##    ###      |
  |                                                                                                                   |
  +===================================================================================================================+

  A countdown timer and clock for Windows with large ASCII art display, customizable alerts, and configuration.

  +===================================================================================================================+
  | USAGE                                                                                                             |
  +===================================================================================================================+

    wincountdown <time> [options]      Start a countdown timer
    wincountdown --clock               Display current system time (24-hour format)

  +===================================================================================================================+
  | TIME FORMATS                                                                                                      |
  +===================================================================================================================+

    Seconds only         30s, 90s, 500s
    Minutes only         5m, 45m, 240m
    Hours only           2h, 10h
    Combined             1h30m, 2h15m30s, 45m30s
    Colon format         1:30:00 (HH:MM:SS), 45:30 (MM:SS)

  +===================================================================================================================+
  | OPTIONS                                                                                                           |
  +===================================================================================================================+

    Countdown Options:
      -s, --silent           No beep alert when countdown finishes
      -l, --loop             Auto-restart countdown when it reaches zero
      -m, --metric           Display in metric time: 1h=100m, 1m=100s (joke mode)

    Beep Customization:
      -f HZ, --freq HZ       Beep frequency in Hz (37-32767, default: 800)
      -b N, --beeps N        Number of beeps when finished (default: 3)
      -d MS, --duration MS   Duration of each beep in milliseconds (default: 1000)
      -g MS, --gap MS        Gap between beeps in milliseconds (default: 300)

    Other Modes:
      -c, --clock            Clock mode - display current system time (ignores <time>)

    Utility:
      --debug                Enable debug logging to wincountdown-debug.log
      -h, --help             Show this help message

    Note: All beep settings and defaults can be configured in wincountdown-config.json

  +===================================================================================================================+
  | EXAMPLES                                                                                                          |
  +===================================================================================================================+

    Basic Timers
      wincountdown 30s                       30 second countdown
      wincountdown 5m                        5 minute countdown
      wincountdown 1h30m                     1 hour 30 minute countdown

    Common Use Cases
      wincountdown 25m -l                    Pomodoro timer (loops automatically)
      wincountdown 10m -s                    Silent 10 minute timer
      wincountdown 5m -l -s                  Silent looping timer

    Custom Alerts
      wincountdown 1m -f 440 -b 5            440Hz beep, 5 times
      wincountdown 30s -d 500 -g 200         500ms beeps with 200ms gaps

    Clock Mode
      wincountdown --clock                   Display current time (24-hour format)
      wincountdown -c                        Same as above

    Debug & Troubleshooting
      wincountdown 5m --debug                Run with debug logging enabled

  +===================================================================================================================+
  | CONFIGURATION FILE                                                                                                |
  +===================================================================================================================+

    File: wincountdown-config.json (created automatically on first run)

    Customize:
      - Default beep settings (frequency, count, duration, gap)
      - Default modes (silent, loop, metric)
      - No-args behavior (e.g., auto-run "25m" when no arguments provided)
      - Time-only defaults (e.g., auto-add "-l -s" when only time is specified)
      - ASCII art for digits 0-9 and colon

    The config file includes detailed comments explaining each option.

  +===================================================================================================================+
  | KEY FEATURES                                                                                                      |
  +===================================================================================================================+

    Display
      - Large ASCII art time display with customizable digit styles
      - Smart display: shows only relevant units (59s / 05:30 / 1:30:00)
      - Real-time start and end time shown during countdown
      - Maximum time: 99:59:59 (99:99:99 in metric mode)

    Clock Mode
      - Display current system time in 24-hour format (HH:MM:SS)
      - Always shows 24-hour time regardless of system settings
      - Press Ctrl+C to exit

    Alerts & Modes
      - Customizable beep frequency, duration, count, and gaps
      - Loop mode: auto-restart timer indefinitely
      - Silent mode: countdown without sound
      - Metric time: joke mode displaying base-100 time

    Configuration
      - Persistent settings via JSON config file
      - Advanced behaviors: no-args defaults, time-only flag injection
      - Command-line flags override config file settings

  +===================================================================================================================+
  | QUICK TIPS                                                                                                        |
  +===================================================================================================================+

    - Press Ctrl+C to stop timer or exit clock at any time
    - Edit wincountdown-config.json to set your preferred defaults
    - Use --debug flag if something isn't working as expected
    - Loop mode plays only one beep before restarting (not the full beep count)
    - Metric mode: input is real time, but display shows metric equivalent

  +===================================================================================================================+

  Created by stropitor
"""
    print(help_text)

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main entry point"""
    # Initialize config manager (uses XDG directories on Linux)
    config_manager = ConfigManager()

    # Check for --debug flag early (before full argument parsing)
    debug_flag_enabled = '--debug' in sys.argv
    if debug_flag_enabled:
        logger.setup(True, config_manager.debug_log_file)

    # Setup logger early for debugging
    logger.log("========== STARTING MAIN ==========")
    logger.log(f"Debug flag from command line: {debug_flag_enabled}")

    # Load configuration
    config = config_manager.load()

    # Override config debug mode if --debug flag is present
    if debug_flag_enabled:
        config['debug_mode'] = True
        logger.log("Debug mode enabled via --debug flag")
    
    logger.log(f"sys.argv initial: {sys.argv}")
    
    # Get effective arguments
    effective_args = get_effective_args(config)
    
    # Check for help flag
    if effective_args is None or '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)
    
    # Parse arguments
    args = parse_arguments(effective_args, config)

    # Handle clock mode
    if args.clock:
        timer = CountdownTimer(config)
        try:
            timer.run_clock()
        except KeyboardInterrupt:
            print("\n\nClock stopped!")
            sys.exit(0)

    # Show help if no time provided
    if not args.time:
        print_help()
        sys.exit(1)
    
    # Validate arguments
    errors = validate_arguments(args, args.metric)
    if errors:
        for error in errors:
            print(f"Error: {error}")
        sys.exit(1)
    
    # Initialize timer
    timer = CountdownTimer(config)
    
    try:
        # Parse time
        total_seconds = timer.parse_time(args.time, args.metric)
        if total_seconds <= 0:
            print("Error: Time must be greater than 0")
            sys.exit(1)
        
        # Check maximum time
        max_seconds = MAX_METRIC_MILLISECONDS if args.metric else MAX_STANDARD_SECONDS
        
        if total_seconds > max_seconds:
            print(f"Error: Time exceeds maximum of 99:99:99")
            if args.metric:
                total_metric_seconds = total_seconds // 1000
                hours = total_metric_seconds // 10000
                minutes = (total_metric_seconds % 10000) // 100
                seconds = total_metric_seconds % 100
                print(f"You requested: {hours:02d}:{minutes:02d}:{seconds:02d} (metric)")
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                print(f"You requested: {hours:02d}:{minutes:02d}:{seconds:02d}")
            sys.exit(1)
        
        # Run countdown
        timer.run(total_seconds, args.freq, args.beeps, args.duration, 
                 args.gap, args.silent, args.loop, args.metric)
        
    except ValueError:
        print("Error: Invalid time format")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTimer stopped!")
        sys.exit(0)

if __name__ == "__main__":
    main()