# 3D Contributions Module

This module fetches a GitHub contribution calendar and renders light and dark
isometric SVGs for a profile README.

It is inspired by
[`colincode0/github-readme`](https://github.com/colincode0/github-readme) and has
been adapted into an independent module for this repository.

## Public Outputs

The generator writes its production assets to the repository-level output
directory:

- `output/contribs-light.svg`
- `output/contribs-dark.svg`

Those paths remain stable so the separate `sasta-kro/sasta-kro` profile README
can embed their raw `main` branch URLs.

## Rendering Model

Color and height represent different parts of the contribution data:

- Color follows GitHub's native `contributionLevel` intensity buckets.
- Height uses the raw daily `contributionCount` with a logarithmic curve.

This keeps a single contribution visible while preventing unusually active days
from creating disproportionate spikes.

## Local Preview

Run these commands from the repository root. A temporary output directory keeps
experiments separate from the tracked production SVGs.

```bash
python3 3d-contributions/generate_contribs.py --mock --out ./tmp/mock-contributions
```

For live data:

```bash
GH_README_TOKEN=your_token GITHUB_USER=sasta-kro \
  python3 3d-contributions/generate_contribs.py --out ./tmp/live-contributions
```

The token falls back from `GH_README_TOKEN` to `GITHUB_TOKEN`. Private
contributions require a token with suitable repository access.

## Automation

The root workflow runs every day at `06:17 UTC`, renders both SVG variants into
`output/`, and commits changes back to the branch that ran the workflow. On the
default branch, this preserves the URLs already used by the profile README.
