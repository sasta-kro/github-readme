# Terminal Animation Module

This module owns the animated wordmark, ticker, rotating ASCII crest, Fedora
terminal sequence, theme, and profile copy. It publishes the generated terminal
GIF to the repository-level `output/terminal.gif` path.

## Configuration

Edit [`config/profile.toml`](config/profile.toml) to change:

- GitHub username and display name
- ticker messages
- login banner, prompt, command, system details, stack, and sign-off text
- gold or dark-blue color palettes
- terminal dimensions, frame rate, holds, and rotation duration

`typing_speed` uses the renderer's built-in values where `1` is its fastest
setting. Faster typing will require batching multiple characters into a rendered
frame rather than lowering that value.

## Fedora Animation Source

[`assets/fedora-logo-ascii-animation.sh`](assets/fedora-logo-ascii-animation.sh)
is the proven 24-frame Fedora animation used as the reference implementation.
It loops at 0.05 seconds per frame and stops on a keypress.

The current generated fastfetch panel still reads the static
[`assets/fedora.txt`](assets/fedora.txt). The shell animation is preserved here
so its frames can be integrated into the Python renderer without depending on a
separate repository.

## Generate Locally

Run from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r terminal-animation/requirements.txt
.venv/bin/python terminal-animation/scripts/gen_hero.py
.venv/bin/python terminal-animation/scripts/gen_terminal.py --mock
```

The terminal generator writes intermediate PNG frames beneath
`terminal-animation/.build/` and the finished GIF to `output/terminal.gif`.

Without `--mock`, `GITHUB_TOKEN` is required for live GitHub statistics.

## Credits

The terminal sequence and rotating crest are adapted from
[`syamxm/syamxm`](https://github.com/syamxm/syamxm). Rendering is provided by
[`github-readme-terminal`](https://github.com/x0rzavi/github-readme-terminal).
