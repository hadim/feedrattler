# `feedrattler` 🐍

[release-badge]: https://img.shields.io/github/v/release/hadim/feedrattler?logo=github
[test-badge]: https://github.com/hadim/feedrattler/actions/workflows/test.yaml/badge.svg?branch=main
[lint-badge]: https://github.com/hadim/feedrattler/actions/workflows/lint.yaml/badge.svg?branch=main

[![GitHub Release][release-badge]](https://github.com/hadim/feedrattler/releases)
[![Test CI][test-badge]](https://github.com/hadim/feedrattler/actions/workflows/test.yaml)
[![Lint CI][lint-badge]](https://github.com/hadim/feedrattler/actions/workflows/lint.yaml)

Convert conda-forge feedstock to rattler-build.

## Usage 🚀

The below command will convert the feedstock `https://github.com/conda-forge/my-awesome-package-feedstock` to a **v1 recipe** using [`rattler-build`](https://rattler.build). The converted branch will be pushed to the **`gh_user` fork** of the feedstock (`https://github.com/gh_user/my-awesome-package-feedstock`) (it will be created if it does not exist).

```bash
pixi exec feedrattler my-awesome-package-feedstock
```

Credentials for the github API will either be taken from the `GITHUB_TOKEN` environment variable.
Alternatively, if you have the official [`gh`](https://cli.github.com/) CLI installed and configured credentials will be taken from there.

If you would rather run without GitHub API access, ensure you already have a fork on the feedstock.

The package is also available as a conda package:

```bash
conda install -c conda-forge feedrattler
# or
conda install -c conda-forge feedrattler
# or
pixi add feedrattler
```

## Options ⚙️

Use `feedrattler --help` to see all available options.

```bash
$ feedrattler --help

 Usage: feedrattler [OPTIONS] FEEDSTOCK_NAME [GITHUB_USERNAME]

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    feedstock_name       TEXT               [default: None] [required]                                                                 │
│      github_username      [GITHUB_USERNAME]  [default: None]                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --use-pixi                       --no-use-pixi                                         [default: use-pixi]                              │
│ --local-clone-dir                                                    TEXT              [default: None]                                  │
│ --local-clone-dir-force-erase    --no-local-clone-dir-force-erase                      [default: no-local-clone-dir-force-erase]        │
│ --branch-name                                                        TEXT              [default: convert_feedstock_to_v1_recipe_format] │
│ --rerender                       --no-rerender                                         [default: rerender]                              │
│ --enable-rerender-logs           --no-enable-rerender-logs                             [default: no-enable-rerender-logs]               │
│ --log-level                                                          TEXT              [default: INFO]                                  │
│ --github-token                                                       TEXT              [env var: GITHUB_TOKEN] [default: None]          │
│ --dotenv                                                             TEXT              [default: None]                                  │
│ --clone-type                                                         [auto|ssh|https]  [default: auto]                                  │
│ --help                                                                                 Show this message and exit.                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Development 🛠️

You need to use [pixi](https://pixi.sh).

```bash
# Execute feedrattler CLI
pixi run -e dev feedrattler

# Install package in editable mode
pixi run -e dev install-dev

# Run tests
pixi run -e dev test

# Format code
pixi run -e dev format
```

## Release 🚢

The package is **not** released on PyPi but only on conda-forge at <https://github.com/conda-forge/feedrattler-feedstock>.

To cut a new release:

- Trigger [the `release` workflow on the main branch](https://github.com/hadim/feedrattler/actions/workflows/release.yaml).
- A new GitHub Release will be created with the new version.
- The conda-forge bot will create a PR to update the [feedstock](https://github.com/conda-forge/feedrattler-feedstock).
- Once the conda-forge PR merged, the new conda version will be available.
