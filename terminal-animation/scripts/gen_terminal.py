#!/usr/bin/env python3
"""Render the configurable README terminal animation.

Run with ``--mock`` for an offline preview. Without ``--mock``, the script uses
GITHUB_TOKEN to populate the GitHub stats section.
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import gen_hero


MODULE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = MODULE_ROOT.parent
PROFILE_CONFIG = MODULE_ROOT / "config" / "profile.toml"
FEDORA_LOGO_SOURCE = MODULE_ROOT / "assets" / "fedora.txt"
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
ANSI_TOKEN_PATTERN = re.compile(r"(\x1b\[[0-9;]*m)")

ACCENT = "\x1b[93m"
ACCENT_DEEP = "\x1b[33m"
INK = "\x1b[97m"
MUTED = "\x1b[34m"
BANNER = "\x1b[30;103m"
RESET = "\x1b[0m"


def load_config():
    with PROFILE_CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def configure_gifos_environment(config):
    """Feed the profile theme to gifos before the package is imported."""
    build_dir = MODULE_ROOT / ".build"
    output_dir = PROJECT_ROOT / "output"
    build_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    profile = config["profile"]
    theme = config["theme"]["dark"]
    settings = {
        "GIFOS_GENERAL_USER_NAME": profile["username"],
        "GIFOS_GENERAL_COLOR_SCHEME": "yoru",
        "GIFOS_FILES_FRAME_BASE_NAME": "frame_",
        "GIFOS_FILES_FRAME_FOLDER_NAME": str(build_dir / "frames"),
        "GIFOS_FILES_OUTPUT_GIF_NAME": str(output_dir / "terminal"),
        "GIFOS_YORU_DEFAULT_COLORS_FG": theme["foreground"],
        "GIFOS_YORU_DEFAULT_COLORS_BG": theme["background"],
        "GIFOS_YORU_NORMAL_COLORS_BLACK": theme["background"],
        "GIFOS_YORU_NORMAL_COLORS_BLUE": theme["muted"],
        "GIFOS_YORU_NORMAL_COLORS_YELLOW": theme["accent"],
        "GIFOS_YORU_NORMAL_COLORS_WHITE": theme["foreground"],
        "GIFOS_YORU_BRIGHT_COLORS_BLACK": theme["border"],
        "GIFOS_YORU_BRIGHT_COLORS_BLUE": theme["muted"],
        "GIFOS_YORU_BRIGHT_COLORS_YELLOW": theme["accent_soft"],
        "GIFOS_YORU_BRIGHT_COLORS_WHITE": theme["foreground"],
    }
    os.environ.update(settings)


def mock_stats():
    return SimpleNamespace(
        user_rank=SimpleNamespace(level="A"),
        total_stargazers=12,
        total_commits_last_year=432,
        total_pull_requests_merged=24,
        total_pull_requests_made=27,
        total_repo_contributions=8,
    )


def crest_frames(frame_count):
    model = gen_hero.build_model(gen_hero.read_art("ascii-art.txt"))
    return [
        gen_hero.render_frame(model, (index / frame_count) * 2.0 * math.pi)
        for index in range(frame_count)
    ]


def fedora_logo():
    with FEDORA_LOGO_SOURCE.open(encoding="utf-8") as handle:
        lines = handle.read().rstrip("\n").split("\n")
    return [line.replace("$1", ACCENT_DEEP).replace("$2", INK) + RESET for line in lines]


def visible_width(line):
    return len(ANSI_PATTERN.sub("", line))


def type_text(terminal, text, row, *, contin, speed, chars_per_frame):
    """Type text with configurable visible-character batching."""
    if chars_per_frame <= 1:
        terminal.gen_typing_text(text, row, contin=contin, speed=speed)
        return

    frame_count = speed if speed in (1, 2, 3) else 1
    continue_line = contin
    for token in filter(None, ANSI_TOKEN_PATTERN.split(text)):
        if ANSI_PATTERN.fullmatch(token):
            terminal.gen_text(token, row, count=0, contin=continue_line)
            continue_line = True
            continue

        for start in range(0, len(token), chars_per_frame):
            terminal.gen_text(
                token[start : start + chars_per_frame],
                row,
                count=frame_count,
                contin=continue_line,
            )
            continue_line = True


def post_screen(terminal, config, year):
    terminal_config = config["terminal"]
    profile = config["profile"]
    hold = terminal_config["hold_short_frames"]
    terminal.gen_text("", 1, count=hold)
    terminal.toggle_show_cursor(False)
    terminal.gen_text(f"{profile['display_name']} Modular BIOS v1.0", 1)
    terminal.gen_text(f"Copyright (C) {year}, {ACCENT}{profile['username']}{RESET}", 2)
    terminal.gen_text(f"{ACCENT_DEEP}GitHub Profile Terminal{RESET}", 4)
    terminal.gen_text("Fedora GIFCPU - 250Hz", 6)
    terminal.gen_text(
        f"Press {ACCENT_DEEP}DEL{RESET} to enter SETUP, "
        f"{ACCENT_DEEP}ESC{RESET} to cancel Memory Test",
        terminal.num_rows,
    )

    memory_total = 65536
    memory_step = terminal_config["memory_step"]
    for used in range(0, memory_total + memory_step, memory_step):
        terminal.delete_row(8)
        terminal.gen_text(f"Memory Test: {min(used, memory_total)}", 8, contin=True)

    terminal.delete_row(8)
    terminal.gen_text("Memory Test: 64KB OK", 8, count=hold, contin=True)
    terminal.gen_text("", 10, count=hold, contin=True)


def boot_screen(terminal, config, gifos):
    terminal_config = config["terminal"]
    header = "Initiating Boot Sequence ....."
    speed = terminal_config["typing_speed"]
    chars_per_frame = terminal_config["typing_chars_per_frame"]
    hold = terminal_config["hold_short_frames"]

    terminal.clear_frame()
    terminal.gen_text("Initiating Boot Sequence ", 1, contin=True)
    type_text(
        terminal,
        ".....",
        1,
        contin=True,
        speed=speed,
        chars_per_frame=chars_per_frame,
    )

    indent = " " * ((terminal.num_cols - gen_hero.COLUMNS) // 2)
    terminal.toggle_show_cursor(False)
    for frame in crest_frames(terminal_config["rotation_frames"]):
        terminal.clear_frame()
        terminal.gen_text(
            [header, ""] + [f"{indent}{ACCENT}{line}{RESET}" for line in frame],
            1,
        )

    tagline = config["ticker"]["messages"][0]
    tagline_col = (terminal.num_cols - len(tagline)) // 2 + 1
    tagline_row = terminal.num_rows
    for line in gifos.effects.text_scramble_effect_lines(
        tagline, 3, include_special=False
    ):
        terminal.delete_row(tagline_row)
        terminal.gen_text(f"{ACCENT_DEEP}{line}{RESET}", tagline_row, tagline_col)

    terminal.gen_text("", tagline_row, count=hold * 2)


def login_screen(terminal, config, stamp, prompt):
    terminal_config = config["terminal"]
    username = config["profile"]["username"]
    hold = terminal_config["hold_short_frames"]
    speed = terminal_config["typing_speed"]
    chars_per_frame = terminal_config["typing_chars_per_frame"]

    terminal.clear_frame()
    terminal.set_prompt(prompt)
    terminal.clone_frame(hold)
    terminal.toggle_show_cursor(False)
    terminal.gen_text(
        f"{ACCENT_DEEP}{terminal_config['login_banner']}{RESET}", 1, count=hold
    )
    terminal.gen_text("login: ", 3, count=hold)
    terminal.toggle_show_cursor(True)
    type_text(
        terminal,
        username,
        3,
        contin=True,
        speed=speed,
        chars_per_frame=chars_per_frame,
    )
    terminal.gen_text("", 4, count=hold)
    terminal.toggle_show_cursor(False)
    terminal.gen_text("password: ", 4, count=hold)
    terminal.toggle_show_cursor(True)
    type_text(
        terminal,
        "************",
        4,
        contin=True,
        speed=speed,
        chars_per_frame=chars_per_frame,
    )
    terminal.toggle_show_cursor(False)
    terminal.gen_text(f"Last login: {stamp} on tty1", 6, count=hold)


def fetch_panel(terminal, config, stats, year, prompt):
    terminal_config = config["terminal"]
    profile = config["profile"]
    logo = fedora_logo()
    hold = terminal_config["hold_short_frames"]
    speed = terminal_config["typing_speed"]
    chars_per_frame = terminal_config["typing_chars_per_frame"]
    details_column = 43

    def field(label, value):
        return f"{ACCENT_DEEP}{label.ljust(17)}{INK}{value}{RESET}"

    details = [
        f"{BANNER} {profile['username']}@GitHub {RESET}",
        "------------------",
    ]
    details.extend(field(item["label"], item["value"]) for item in terminal_config["details"])
    details.extend(
        [
            "",
            f"{BANNER} GitHub Stats {RESET}",
            "------------------",
            field("Rank:", stats.user_rank.level),
            field("Stars:", stats.total_stargazers),
            field(f"Commits ({year}):", stats.total_commits_last_year),
            field(
                "Pull Requests:",
                f"{stats.total_pull_requests_merged} merged of {stats.total_pull_requests_made}",
            ),
            field("Contributions:", stats.total_repo_contributions),
            field("Stack:", terminal_config["stack"]),
        ]
    )

    terminal.clear_frame()
    terminal.set_prompt(prompt)
    terminal.gen_prompt(1)
    prompt_col = terminal.curr_col
    terminal.clone_frame(hold)
    terminal.toggle_show_cursor(True)

    command = terminal_config["command"]
    if command.startswith("fastfetch"):
        type_text(
            terminal,
            "\x1b[91mfastfetc",
            1,
            contin=True,
            speed=speed,
            chars_per_frame=chars_per_frame,
        )
        terminal.delete_row(1, prompt_col)
        terminal.gen_text(f"{ACCENT_DEEP}fastfetch{RESET}", 1, contin=True)
        type_text(
            terminal,
            command[len("fastfetch") :],
            1,
            contin=True,
            speed=speed,
            chars_per_frame=chars_per_frame,
        )
    else:
        type_text(
            terminal,
            command,
            1,
            contin=True,
            speed=speed,
            chars_per_frame=chars_per_frame,
        )

    terminal.toggle_show_cursor(False)
    for offset in range(max(len(logo), len(details))):
        art = logo[offset] if offset < len(logo) else ""
        info = details[offset] if offset < len(details) else ""
        gap = " " * max(1, details_column - 1 - visible_width(art))
        terminal.gen_text(f"{art}{gap}{info}", 3 + offset)

    terminal.gen_text("", 3 + max(len(logo), len(details)), count=hold)
    terminal.toggle_show_cursor(True)
    terminal.gen_prompt(terminal.curr_row + 2)
    type_text(
        terminal,
        f"{MUTED}{terminal_config['signoff']}{RESET}",
        terminal.curr_row,
        contin=True,
        speed=speed,
        chars_per_frame=chars_per_frame,
    )
    terminal.gen_text(
        "", terminal.curr_row, count=terminal_config["final_hold_frames"], contin=True
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mock", action="store_true", help="use deterministic placeholder GitHub stats"
    )
    args = parser.parse_args()

    config = load_config()
    configure_gifos_environment(config)

    import gifos

    profile = config["profile"]
    terminal_config = config["terminal"]
    token = os.getenv("GITHUB_TOKEN")
    if args.mock:
        stats = mock_stats()
    else:
        if not token:
            sys.exit("GITHUB_TOKEN is required unless --mock is used")
        stats = gifos.utils.fetch_github_stats(
            user_name=profile["username"], ignore_repos=[profile["username"]]
        )

    local_timezone = timezone(
        timedelta(hours=profile["timezone_offset_hours"]),
        name=profile["timezone_name"],
    )
    now = datetime.now(local_timezone)
    year = now.strftime("%Y")
    stamp = now.strftime("%a %b %d %I:%M:%S %p %Z %Y")
    prompt = (
        f"{ACCENT}{profile['username']}@{terminal_config['prompt_host']}"
        f"{RESET} ~> "
    )

    terminal = gifos.Terminal(
        terminal_config["width"],
        terminal_config["height"],
        terminal_config["padding"],
        terminal_config["padding"],
    )
    terminal.set_fps(terminal_config["fps"])
    post_screen(terminal, config, year)
    boot_screen(terminal, config, gifos)
    login_screen(terminal, config, stamp, prompt)
    fetch_panel(terminal, config, stats, year, prompt)
    terminal.gen_gif()


if __name__ == "__main__":
    main()
