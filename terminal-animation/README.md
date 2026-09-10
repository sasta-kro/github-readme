# Terminal Animation Module

This module owns the animated wordmark, ticker, rotating ASCII crest, Fedora
terminal sequence, theme, and profile copy. It publishes all profile-facing
artwork through the repository-level `output/` directory.

## Configuration

Edit [`config/profile.toml`](config/profile.toml) to change:

- GitHub username and display name
- technology shield labels, logos, colors, and order
- ticker messages
- login banner, prompt, command, system details, stack, and sign-off text
- gold or dark-blue color palettes
- terminal dimensions, frame rate, holds, and rotation duration

`typing_speed` controls how many frames each typing step remains visible.
`typing_chars_per_frame` controls how many characters appear in each step, so
values greater than `1` provide faster typing than the renderer's built-in limit.

For the animated wordmark, `type_seconds` controls the reveal duration and
`hold_seconds` controls how long the completed name stays visible before the
loop restarts. `cursor_blink_seconds` controls only the cursor blink.

## Fedora Animation Source

[`assets/fedora-logo-ascii-animation.sh`](assets/fedora-logo-ascii-animation.sh)
is the source of the 24-frame Fedora animation. The terminal renderer parses
those frames, applies the configured terminal palette, and loops them through
the final hold of the fastfetch panel. The default 72-frame hold shows three
complete Fedora loops at 18 FPS.

## Generate Locally

Run from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python terminal-animation/scripts/update_readme_badges.py
.venv/bin/python terminal-animation/scripts/gen_hero.py
.venv/bin/python terminal-animation/scripts/gen_terminal.py --mock
```

The generators write intermediate PNG frames beneath `terminal-animation/.build/`
and publish the wordmark, ticker, crest, and terminal GIF beneath `output/`.

Without `--mock`, `GITHUB_TOKEN` is required for live GitHub statistics.

## Credits

The terminal sequence and rotating crest are adapted from
[`syamxm/syamxm`](https://github.com/syamxm/syamxm). Rendering is provided by
[`github-readme-terminal`](https://github.com/x0rzavi/github-readme-terminal).
