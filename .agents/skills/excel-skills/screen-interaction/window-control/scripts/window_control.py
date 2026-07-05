#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Optional


DEFAULT_STATE_FILE = "/tmp/window-control-state.json"


def applescript_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def run_osascript(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True)


def load_state(state_file: str) -> dict:
    if not os.path.exists(state_file):
        return {}
    try:
        with open(state_file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def save_state(state_file: str, state: dict) -> None:
    with open(state_file, "w", encoding="utf-8") as handle:
        json.dump(state, handle)


def get_frontmost_app() -> str:
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = run_osascript(script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def build_window_match_clause(title: str, match_mode: str) -> str:
    escaped_title = applescript_escape(title)
    if match_mode == "contains":
        return f'(name of w) contains "{escaped_title}"'
    return f'(name of w) is "{escaped_title}"'


def get_front_window_info() -> Optional[dict]:
    script = """
tell application "System Events"
    set frontApp to first application process whose frontmost is true
    tell frontApp
        if (count of windows) is 0 then
            return ""
        end if
        set winName to name of front window
        set winPos to position of front window
        set winSize to size of front window
        return (name of frontApp as text) & "||" & winName & "||" & (item 1 of winPos as text) & "||" & (item 2 of winPos as text) & "||" & (item 1 of winSize as text) & "||" & (item 2 of winSize as text)
    end tell
end tell
"""
    result = run_osascript(script)
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    parts = raw.split("||")
    if len(parts) != 6:
        return None
    try:
        return {
            "app": parts[0],
            "title": parts[1],
            "left": int(float(parts[2])),
            "top": int(float(parts[3])),
            "width": int(float(parts[4])),
            "height": int(float(parts[5])),
        }
    except ValueError:
        return None


def activate_app(app_name: str, delay: float = 0.2) -> int:
    escaped = applescript_escape(app_name)
    result = run_osascript(f'tell application "{escaped}" to activate')
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if delay > 0:
        time.sleep(delay)
    return 0


def activate_window_by_title(title: str, match_mode: str = "contains", delay: float = 0.2) -> int:
    match_clause = build_window_match_clause(title, match_mode)
    script = f'''
tell application "System Events"
    repeat with p in every process whose background only is false
        repeat with w in every window of p
            try
                if {match_clause} then
                    tell p
                        set frontmost to true
                        perform action "AXRaise" of w
                        return "ok"
                    end tell
                end if
            end try
        end repeat
    end repeat
end tell
return "not-found"
'''
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def set_window_bounds(title: str, match_mode: str, left: int, top: int, width: int, height: int, delay: float = 0.2) -> int:
    match_clause = build_window_match_clause(title, match_mode)
    script = f'''
tell application "System Events"
    repeat with p in every process whose background only is false
        repeat with w in every window of p
            try
                if {match_clause} then
                    tell p
                        set position of w to {{{left}, {top}}}
                        set size of w to {{{width}, {height}}}
                        set frontmost to true
                        perform action "AXRaise" of w
                        return "ok"
                    end tell
                end if
            end try
        end repeat
    end repeat
end tell
return "not-found"
'''
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def get_window_bounds_by_title(title: str, match_mode: str) -> Optional[dict]:
    match_clause = build_window_match_clause(title, match_mode)
    script = f'''
tell application "System Events"
    repeat with p in every process whose background only is false
        repeat with w in every window of p
            try
                if {match_clause} then
                    set winPos to position of w
                    set winSize to size of w
                    return (name of p as text) & "||" & (name of w as text) & "||" & (item 1 of winPos as text) & "||" & (item 2 of winPos as text) & "||" & (item 1 of winSize as text) & "||" & (item 2 of winSize as text)
                end if
            end try
        end repeat
    end repeat
end tell
return ""
'''
    result = run_osascript(script)
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return None
    parts = raw.split("||")
    if len(parts) != 6:
        return None
    try:
        return {
            "app": parts[0],
            "title": parts[1],
            "left": int(float(parts[2])),
            "top": int(float(parts[3])),
            "width": int(float(parts[4])),
            "height": int(float(parts[5])),
        }
    except ValueError:
        return None


def exact_window_action_script(app_name: str, window_title: str, body: str) -> str:
    escaped_app = applescript_escape(app_name)
    escaped_title = applescript_escape(window_title)
    return f'''
tell application "System Events"
    if not (exists process "{escaped_app}") then
        return "missing-app"
    end if
    tell process "{escaped_app}"
        if not (exists window "{escaped_title}") then
            return "not-found"
        end if
        tell window "{escaped_title}"
{body}
        end tell
        set frontmost to true
        try
            perform action "AXRaise" of window "{escaped_title}"
        end try
    end tell
end tell
return "ok"
'''


def move_window(title: str, match_mode: str, x: int, y: int, delay: float) -> int:
    bounds = get_window_bounds_by_title(title, match_mode)
    if not bounds:
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    script = exact_window_action_script(
        bounds["app"],
        bounds["title"],
        f"            set position to {{{x}, {y}}}\n",
    )
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def resize_window(title: str, match_mode: str, width: int, height: int, delay: float) -> int:
    bounds = get_window_bounds_by_title(title, match_mode)
    if not bounds:
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    script = exact_window_action_script(
        bounds["app"],
        bounds["title"],
        f"            set size to {{{width}, {height}}}\n",
    )
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def set_window_attribute(title: str, match_mode: str, attribute_name: str, attribute_value: str, delay: float = 0.2) -> int:
    match_clause = build_window_match_clause(title, match_mode)
    script = f'''
tell application "System Events"
    repeat with p in every process whose background only is false
        repeat with w in every window of p
            try
                if {match_clause} then
                    tell process (name of p)
                        set value of attribute "{attribute_name}" of w to {attribute_value}
                        set frontmost to true
                        perform action "AXRaise" of w
                        return "ok"
                    end tell
                end if
            end try
        end repeat
    end repeat
end tell
return "not-found"
'''
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def minimize_window(title: str, match_mode: str, delay: float) -> int:
    bounds = get_window_bounds_by_title(title, match_mode)
    if not bounds:
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    script = exact_window_action_script(
        bounds["app"],
        bounds["title"],
        '            set value of attribute "AXMinimized" to true\n',
    )
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def restore_window(title: str, match_mode: str, delay: float) -> int:
    bounds = get_window_bounds_by_title(title, match_mode)
    if not bounds:
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    escaped_app = applescript_escape(bounds["app"])
    escaped_title = applescript_escape(bounds["title"])
    script = f'''
tell application "System Events"
    if not (exists process "{escaped_app}") then
        return "missing-app"
    end if
    tell process "{escaped_app}"
        if not (exists window "{escaped_title}") then
            return "not-found"
        end if
        try
            set value of attribute "AXMinimized" of window "{escaped_title}" to false
        end try
        try
            set value of attribute "AXFullScreen" of window "{escaped_title}" to false
        end try
        set frontmost to true
        try
            perform action "AXRaise" of window "{escaped_title}"
        end try
    end tell
end tell
try
    tell application "{escaped_app}"
        tell window "{escaped_title}" to set zoomed to false
        activate
    end tell
end try
return "ok"
'''
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def maximize_window(title: str, match_mode: str, delay: float) -> int:
    bounds = get_window_bounds_by_title(title, match_mode)
    if not bounds:
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    escaped_app = applescript_escape(bounds["app"])
    escaped_title = applescript_escape(bounds["title"])
    script = f'''
tell application "{escaped_app}"
    tell window "{escaped_title}" to set zoomed to true
    activate
end tell
return "ok"
'''
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    if result.stdout.strip() != "ok":
        sys.stderr.write(f'No window found for title "{title}"\n')
        return 1
    if delay > 0:
        time.sleep(delay)
    return 0


def restore_saved_window(window_state: dict) -> int:
    escaped_app = applescript_escape(window_state["app"])
    escaped_title = applescript_escape(window_state["title"])
    script = f'''
tell application "System Events"
    if not (exists process "{escaped_app}") then
        return "missing-app"
    end if
    tell process "{escaped_app}"
        repeat with w in windows
            try
                if (name of w) is "{escaped_title}" then
                    set position of w to {{{window_state["left"]}, {window_state["top"]}}}
                    set size of w to {{{window_state["width"]}, {window_state["height"]}}}
                    perform action "AXRaise" of w
                    return "ok"
                end if
            end try
        end repeat
    end tell
end tell
return "not-found"
'''
    result = run_osascript(script)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.strip() + "\n")
        return result.returncode
    return 0 if result.stdout.strip() == "ok" else 1


def command_save_state(state_file: str) -> int:
    state = {
        "frontmost_app": get_frontmost_app(),
        "front_window": get_front_window_info(),
    }
    save_state(state_file, state)
    print(json.dumps(state, indent=2))
    return 0


def command_restore_state(state_file: str, delay: float) -> int:
    state = load_state(state_file)
    if not state:
        sys.stderr.write(f"No saved state found at {state_file}\n")
        return 1

    app_name = state.get("frontmost_app")
    if app_name:
        result = activate_app(app_name, delay=delay)
        if result != 0:
            return result

    window_state = state.get("front_window")
    if window_state:
        restore_saved_window(window_state)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="macOS window and app control helper.")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE, help="Path for saved state")
    parser.add_argument("--delay", type=float, default=0.2, help="Settle delay after activation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("get-frontmost-app", help="Print the current frontmost app")
    subparsers.add_parser("get-front-window", help="Print front window details as JSON")

    activate_app_parser = subparsers.add_parser("activate-app", help="Activate an app by name")
    activate_app_parser.add_argument("--app", required=True)

    activate_window_parser = subparsers.add_parser("activate-window", help="Activate a window by title")
    activate_window_parser.add_argument("--title", required=True)
    activate_window_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")

    move_parser = subparsers.add_parser("move-window", help="Move a window to a new screen position")
    move_parser.add_argument("--title", required=True)
    move_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
    move_parser.add_argument("--x", type=int, required=True)
    move_parser.add_argument("--y", type=int, required=True)

    resize_parser = subparsers.add_parser("resize-window", help="Resize a window")
    resize_parser.add_argument("--title", required=True)
    resize_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
    resize_parser.add_argument("--width", type=int, required=True)
    resize_parser.add_argument("--height", type=int, required=True)

    bounds_parser = subparsers.add_parser("set-window-bounds", help="Set exact window bounds")
    bounds_parser.add_argument("--title", required=True)
    bounds_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")
    bounds_parser.add_argument("--x", type=int, required=True)
    bounds_parser.add_argument("--y", type=int, required=True)
    bounds_parser.add_argument("--width", type=int, required=True)
    bounds_parser.add_argument("--height", type=int, required=True)

    minimize_parser = subparsers.add_parser("minimize-window", help="Minimize a window")
    minimize_parser.add_argument("--title", required=True)
    minimize_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")

    maximize_parser = subparsers.add_parser("maximize-window", help="Maximize or zoom a window")
    maximize_parser.add_argument("--title", required=True)
    maximize_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")

    restore_window_parser = subparsers.add_parser("restore-window", help="Restore a minimized or maximized window")
    restore_window_parser.add_argument("--title", required=True)
    restore_window_parser.add_argument("--match-mode", choices=["contains", "exact"], default="contains")

    subparsers.add_parser("save-state", help="Save frontmost app and window state")
    subparsers.add_parser("restore-state", help="Restore saved app and window state")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "get-frontmost-app":
        print(get_frontmost_app())
        return 0

    if args.command == "get-front-window":
        print(json.dumps(get_front_window_info(), indent=2))
        return 0

    if args.command == "activate-app":
        return activate_app(args.app, delay=args.delay)

    if args.command == "activate-window":
        return activate_window_by_title(args.title, match_mode=args.match_mode, delay=args.delay)

    if args.command == "move-window":
        return move_window(args.title, args.match_mode, args.x, args.y, delay=args.delay)

    if args.command == "resize-window":
        return resize_window(args.title, args.match_mode, args.width, args.height, delay=args.delay)

    if args.command == "set-window-bounds":
        return set_window_bounds(args.title, args.match_mode, args.x, args.y, args.width, args.height, delay=args.delay)

    if args.command == "minimize-window":
        return minimize_window(args.title, args.match_mode, delay=args.delay)

    if args.command == "maximize-window":
        return maximize_window(args.title, args.match_mode, delay=args.delay)

    if args.command == "restore-window":
        return restore_window(args.title, args.match_mode, delay=args.delay)

    if args.command == "save-state":
        return command_save_state(args.state_file)

    if args.command == "restore-state":
        return command_restore_state(args.state_file, delay=args.delay)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
