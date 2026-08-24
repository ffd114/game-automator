# Game Automator

A lightweight Python command-line utility for desktop and game automation, featuring customizable Anti-AFK sequences and an Auto-Farming mode with skill rotations.

> **Note:** This repository is forked and refactored from [nwsynx/roblox-tools](https://github.com/nwsynx/roblox-tools), built with [pi.dev](https://pi.dev) agents.

---

## Features

- **Customizable Anti-AFK Mode**:
  - Prevent idle disconnection by executing custom action sequences.
  - Supports key presses, mouse clicks, key holds, and custom delays.
  - Configurable execution interval and sequence via `config.yaml`.
- **Auto-Farming Mode**:
  - Continuous auto-attack mouse clicking.
  - Thread-safe, non-blocking skill cooldown rotations (e.g., keys `e`, `r`, `f`, `x`).
- **Safety First**:
  - Includes a 5-second countdown to switch to the target window.
  - Safe key release cleanup upon interruption (`Ctrl+C`).

---

## Requirements

- **Python**: `>= 3.13`
- **Dependencies**:
  - `pyautogui`
  - `pyyaml`

---

## Installation

### Using `uv` (Recommended)

Clone the repository and install dependencies:

```bash
git clone https://github.com/ffd114/game-automator.git
cd game-automator
uv sync
```

### Using `pip`

```bash
git clone https://github.com/ffd114/game-automator.git
cd game-automator
pip install pyautogui pyyaml
```

---

## Usage

Run the tool using `uv run python main.py` or standard `python main.py`:

### 1. Anti-AFK Mode

Runs the configured anti-idle sequence at set intervals:

```bash
# Using default config.yaml
uv run python main.py afk

# Using a custom YAML configuration file
uv run python main.py afk --config path/to/custom_config.yaml
```

### 2. Auto-Farming Mode

Rotates configured skills off cooldown while auto-clicking:

```bash
uv run python main.py farm
```

### Stopping the Script

Press <kbd>Ctrl</kbd> + <kbd>C</kbd> in your terminal at any time. The tool will cleanly stop and release any held keys.

---

## Configuration (`config.yaml`)

Both Anti-AFK and Auto-Farming behaviors are configured in `config.yaml`:

```yaml
# Anti-AFK Configuration
afk:
  # Interval between sequence executions in seconds (default: 60)
  interval_seconds: 60

  # Ordered list of actions to execute
  sequence:
    # 1. Press 'f' key
    - action: press
      key: "f"
      delay: 0.1

    # 2. Left click
    - action: click
      button: "left"
      delay: 0.1

# Auto-Farming Configuration
farm:
  # Enable or disable auto-clicking while farming
  auto_click: true
  # Mouse button for auto-clicking ("left", "right", or "middle")
  auto_click_button: "left"
  # Interval between auto-attack clicks (in seconds)
  auto_click_interval: 0.15
  # Small delay added after executing each skill (in seconds)
  skills_delay: 0.1

  # Skills to rotate when off cooldown
  skills:
    - key: "e"
      cooldown: 12.0
      animation_delay: 0.2

    - key: "r"
      cooldown: 3.0
      animation_delay: 0.2

    - key: "f"
      cooldown: 15.0
      animation_delay: 0.2

    - key: "x"
      cooldown: 60.0
      animation_delay: 0.2
```

### Supported AFK Sequence Actions

| Action | Parameters | Default | Description |
| :--- | :--- | :--- | :--- |
| `press` | `key` (string)<br>`delay` (float) | `delay: 0.0` | Simulates pressing and releasing a key. |
| `click` | `button` (`"left" \| "right" \| "middle"`)<br>`delay` (float) | `button: "left"`<br>`delay: 0.0` | Simulates a mouse click. |
| `hold` | `key` (string)<br>`duration` (float)<br>`delay` (float) | `duration: 0.2`<br>`delay: 0.0` | Holds down a key for `duration` seconds, then releases it. |
| `sleep` | `duration` (float) | `duration: 0.0` | Pauses execution for `duration` seconds. |

### Shorthand AFK Syntax

Shorthand key-value pairs are also supported for AFK sequences in `config.yaml`:

```yaml
afk:
  interval_seconds: 60
  sequence:
    - key: "f"
      delay: 0.1
    - click: "left"
      delay: 0.1
    - hold: "w"
      duration: 0.5
    - sleep: 1.0
```

### Farming Configuration Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `auto_click` | boolean | `true` | Enables or disables automated mouse clicking during farming. |
| `auto_click_button` | string | `"left"` | Mouse button used for auto-clicking (`"left"`, `"right"`, or `"middle"`). |
| `auto_click_interval`| float | `0.15` | Interval in seconds between auto-clicks. |
| `skills_delay` | float | `0.1` | Small delay added after skill animation delay. |
| `skills` | list of objects | *(see config)* | Skill rotation list (`key`, `cooldown`, and optional `animation_delay`). |

---

## CLI Options

```text
usage: main.py [-h] [--config CONFIG] {afk,farm}

Automation utility for Anti-AFK sequences and Auto-Farming.

positional arguments:
  {afk,farm}           Mode to run: 'afk' for anti-idle sequence, 'farm' for auto-attacking and skill rotation.

options:
  -h, --help           show this help message and exit
  --config, -c CONFIG  Path to YAML configuration file (default: config.yaml).
```

---

## Acknowledgements

- Originally forked from [nwsynx/roblox-tools](https://github.com/nwsynx/roblox-tools) and subsequently refactored into a general-purpose, YAML-configured CLI automation tool.
- Built with [pi.dev](https://pi.dev) AI coding agents.

---

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

```text
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
```

See [https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html) for full details.
