import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import queue
import threading
import time
from typing import Any, Dict, List, Set
import pyautogui
import yaml


@dataclass(frozen=True)
class Skill:
    key: str
    cooldown: float
    animation_delay: float = 0.2


# Default Configuration
CONFIG_PATH = Path("config.yaml")

DEFAULT_AFK_INTERVAL = 60
DEFAULT_AFK_SEQUENCE = [
    {"action": "press", "key": "f", "delay": 0.1},
    {"action": "click", "button": "left", "delay": 0.1},
]

DEFAULT_FARM_SKILLS = [
    Skill("e", 12.0, 0.2),
    Skill("r", 3.0, 0.2),
    Skill("f", 15.0, 0.2),
    Skill("x", 60.0, 0.2),
]
DEFAULT_FARM_CONFIG = {
    "auto_click": True,
    "auto_click_button": "left",
    "auto_click_interval": 0.15,
    "skills_delay": 0.1,
    "skills": DEFAULT_FARM_SKILLS,
}


def release_keys() -> None:
    """Ensure any potentially stuck keys are released."""
    for key in ["w", "a", "s", "d", "space", "e", "r", "f", "x", "q", "c", "v", "z", "1", "2", "3", "4", "5"]:
        try:
            pyautogui.keyUp(key)
        except Exception:
            pass


def load_farm_config(config_path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """Load farming configuration from a YAML file, falling back to defaults if missing or invalid."""
    if not config_path.exists():
        return DEFAULT_FARM_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        farm_cfg = data.get("farm", {})
        skills_raw = farm_cfg.get("skills")

        if skills_raw is not None:
            parsed_skills = []
            for s in skills_raw:
                if isinstance(s, dict) and "key" in s:
                    parsed_skills.append(
                        Skill(
                            key=str(s["key"]),
                            cooldown=float(s.get("cooldown", 0.0)),
                            animation_delay=float(s.get("animation_delay", 0.2)),
                        )
                    )
        else:
            parsed_skills = DEFAULT_FARM_SKILLS

        return {
            "auto_click": bool(farm_cfg.get("auto_click", DEFAULT_FARM_CONFIG["auto_click"])),
            "auto_click_button": str(farm_cfg.get("auto_click_button", DEFAULT_FARM_CONFIG["auto_click_button"])),
            "auto_click_interval": float(farm_cfg.get("auto_click_interval", DEFAULT_FARM_CONFIG["auto_click_interval"])),
            "skills_delay": float(farm_cfg.get("skills_delay", DEFAULT_FARM_CONFIG["skills_delay"])),
            "skills": parsed_skills,
        }
    except Exception as e:
        print(f"Warning: Failed to load farm config from {config_path} ({e}). Using default farm config.")
        return DEFAULT_FARM_CONFIG


def countdown(seconds: int = 5) -> None:
    """Countdown timer to allow switching to the target window."""
    print(f"Switch to your target window now. You have {seconds} seconds.")
    for i in range(seconds, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    print("\nScript is now running. Press CTRL+C in this terminal to stop.\n")


def load_afk_config(config_path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """Load AFK configuration from a YAML file, falling back to defaults if missing or invalid."""
    if not config_path.exists():
        return {"interval_seconds": DEFAULT_AFK_INTERVAL, "sequence": DEFAULT_AFK_SEQUENCE}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        afk_cfg = data.get("afk", {})
        interval = afk_cfg.get(
            "interval_seconds",
            afk_cfg.get("interval", DEFAULT_AFK_INTERVAL),
        )
        sequence = afk_cfg.get("sequence", DEFAULT_AFK_SEQUENCE)
        return {
            "interval_seconds": interval,
            "sequence": sequence,
        }
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path} ({e}). Using default AFK config.")
        return {"interval_seconds": DEFAULT_AFK_INTERVAL, "sequence": DEFAULT_AFK_SEQUENCE}


def execute_afk_step(step: Dict[str, Any]) -> None:
    """Execute a single action from the AFK sequence."""
    action = step.get("action")
    delay = float(step.get("delay", 0.0))

    # Resolve shorthand notation if action is not explicitly specified
    if not action:
        if "key" in step or "press" in step:
            action = "press"
        elif "click" in step:
            action = "click"
        elif "hold" in step:
            action = "hold"
        elif "sleep" in step:
            action = "sleep"

    if action == "press":
        key = step.get("key") or step.get("press")
        if key:
            pyautogui.press(str(key))
    elif action == "click":
        button = step.get("button") or step.get("click")
        if button is True or button is None:
            button = "left"
        pyautogui.click(button=str(button))
    elif action == "hold":
        key = step.get("key") or step.get("hold")
        duration = float(step.get("duration", 0.2))
        if key:
            try:
                pyautogui.keyDown(str(key))
                time.sleep(duration)
            finally:
                pyautogui.keyUp(str(key))
    elif action == "sleep":
        duration = float(step.get("duration") or step.get("sleep", 0.0))
        time.sleep(duration)

    if delay > 0:
        time.sleep(delay)


def anti_afk(sequence: List[Dict[str, Any]]) -> None:
    """Executes the configured sequence of anti-AFK actions."""
    for step in sequence:
        execute_afk_step(step)


def farming_mode(config_path: Path = CONFIG_PATH) -> None:
    """Auto-farming mode: casts skills when off cooldown and performs auto-attack clicks."""
    cfg = load_farm_config(config_path)
    skills = cfg["skills"]
    auto_click = cfg["auto_click"]
    auto_click_button = cfg["auto_click_button"]
    auto_click_interval = cfg["auto_click_interval"]
    skills_delay = cfg["skills_delay"]

    latest_skills: Dict[Skill, datetime] = {}
    pending_skills: Set[Skill] = set()
    state_lock = threading.Lock()
    q: queue.Queue[Skill] = queue.Queue()

    print("Farming script started.")
    print(f"Loaded Farm config from '{config_path}' with {len(skills)} skills:")
    for skill in skills:
        print(f"  - Skill '{skill.key}': cooldown={skill.cooldown}s, animation_delay={skill.animation_delay}s")
    if auto_click:
        print(f"  - Auto-clicking enabled: button='{auto_click_button}', interval={auto_click_interval}s")
    else:
        print("  - Auto-clicking disabled.")
    countdown(5)

    # Initialize all skills so they are ready immediately at start
    with state_lock:
        for skill in skills:
            latest_skills[skill] = datetime.min

    def worker() -> None:
        """Worker thread that executes skill keypresses sequentially without blocking main loop."""
        while True:
            skill = q.get()
            try:
                with state_lock:
                    latest_skills[skill] = datetime.now()

                pyautogui.press(skill.key)
                time.sleep(skill.animation_delay + skills_delay)
            finally:
                with state_lock:
                    pending_skills.discard(skill)
                q.task_done()

    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()

    while True:
        now = datetime.now()
        with state_lock:
            for skill in skills:
                latest = latest_skills.get(skill, datetime.min)
                diff = (now - latest).total_seconds()

                if diff >= skill.cooldown and skill not in pending_skills:
                    print(f"[{now.strftime('%I:%M:%S %p')}] Skill '{skill.key}' off cooldown. Executing...")
                    pending_skills.add(skill)
                    q.put(skill)

        if auto_click:
            pyautogui.click(button=auto_click_button)
        time.sleep(auto_click_interval)


def afk_mode(config_path: Path = CONFIG_PATH) -> None:
    """Anti-AFK mode: prevents idle disconnection by executing the configured sequence."""
    cfg = load_afk_config(config_path)
    interval = cfg["interval_seconds"]
    sequence = cfg["sequence"]

    print("Anti-AFK script started.")
    print(f"Loaded AFK sequence ({len(sequence)} steps) from '{config_path}' with interval: {interval}s")
    countdown(5)

    while True:
        anti_afk(sequence)
        current_time = time.strftime("%I:%M:%S %p")
        print(f"[{current_time}] Executed Anti-AFK sequence. Next check in {interval}s.")
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automation utility for Anti-AFK sequences and Auto-Farming."
    )
    parser.add_argument(
        "mode",
        type=str,
        choices=["afk", "farm"],
        help="Mode to run: 'afk' for anti-idle sequence, 'farm' for auto-attacking and skill rotation.",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=CONFIG_PATH,
        help="Path to YAML configuration file (default: config.yaml).",
    )
    args = parser.parse_args()

    try:
        if args.mode == "afk":
            afk_mode(config_path=args.config)
        elif args.mode == "farm":
            farming_mode(config_path=args.config)
    except KeyboardInterrupt:
        print("\nScript stopped by user. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        release_keys()


if __name__ == "__main__":
    main()
