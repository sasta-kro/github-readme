#!/usr/bin/env python3
"""Render the profile technology shields in the root README from TOML."""

from __future__ import annotations

import argparse
import html
import tomllib
from pathlib import Path
from urllib.parse import urlencode


MODULE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = MODULE_ROOT.parent
PROFILE_CONFIG = MODULE_ROOT / "config" / "profile.toml"
README = PROJECT_ROOT / "README.md"
START_MARKER = "<!-- profile-shields:start -->"
END_MARKER = "<!-- profile-shields:end -->"


def load_shields():
    with PROFILE_CONFIG.open("rb") as handle:
        return tomllib.load(handle)["shields"]


def shield_slug(label):
    """Escape a Shields.io static badge message for use in the URL path."""
    return label.replace("_", "__").replace("-", "--").replace(" ", "_")


def render_badges(config):
    style = config["style"]
    background = config["background"].lstrip("#")
    default_logo_color = config["logo_color"].lstrip("#")
    lines = ["<p>"]

    for item in config["items"]:
        label = item["label"]
        logo = item["logo"]
        color = item.get("background", background).lstrip("#")
        logo_color = item.get("logo_color", default_logo_color).lstrip("#")
        query = urlencode(
            {
                "style": item.get("style", style),
                "logo": logo,
                "logoColor": logo_color,
            }
        )
        url = f"https://img.shields.io/badge/{shield_slug(label)}-{color}?{query}"
        lines.append(
            f'  <img alt="{html.escape(label, quote=True)}" '
            f'src="{html.escape(url, quote=True)}">'
        )

    lines.append("</p>")
    return "\n".join(lines)


def updated_readme(source, badge_block):
    start = source.find(START_MARKER)
    end = source.find(END_MARKER)
    if start < 0 or end < 0 or end < start:
        raise ValueError("README profile shield markers are missing or out of order")

    content_start = start + len(START_MARKER)
    return (
        source[:content_start]
        + "\n"
        + badge_block
        + "\n"
        + source[end:]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if README shields do not match the TOML configuration",
    )
    args = parser.parse_args()

    source = README.read_text(encoding="utf-8")
    rendered = updated_readme(source, render_badges(load_shields()))
    if rendered == source:
        print("README technology shields are current")
        return 0

    if args.check:
        print("README technology shields need regeneration")
        return 1

    README.write_text(rendered, encoding="utf-8")
    print("Updated README technology shields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
