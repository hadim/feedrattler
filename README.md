[test]: https://github.com/hadim/feedrattler/actions/workflows/test.yaml/badge.svg?branch=main
[lint]: https://github.com/hadim/feedrattler/actions/workflows/lint.yaml/badge.svg?branch=main
[release]: https://img.shields.io/github/v/release/hadim/feedrattler?logo=github

# `feedrattler`

Convert conda-forge feedstock to rattler-build.

## Usage

The below command will convert the feedstock <https://github.com/conda-forge/my-awesome-package-feedstock> to a v1 recipe using `rattler-build`. The converted branch will be pushed to the `gh_user` fork of the feedstock (it will be created if it does not exist).

```bash
pixi exec feedrattler my-awesome-package-feedstock gh_user
```

The package is also available as a conda package:

```bash
conda install -c conda-forge feedrattler
```

## Options

Use `feedrattler --help` to see all available options.

```bash
$ feedrattler --help

 Usage: feedrattler [OPTIONS] FEEDSTOCK_NAME GITHUB_USERNAME

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    feedstock_name       TEXT  [default: None] [required]                                                      │
│ *    github_username      TEXT  [default: None] [required]                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --use-pixi                       --no-use-pixi                             [default: use-pixi]                  │
│ --local-clone-dir                                                    TEXT  [default: None]                      │
│ --local-clone-dir-force-erase    --no-local-clone-dir-force-erase          [default:                            │
│                                                                            no-local-clone-dir-force-erase]      │
│ --branch-name                                                        TEXT  [default:                            │
│                                                                            convert_feedstock_to_v1_recipe_form… │
│ --rerender                       --no-rerender                             [default: rerender]                  │
│ --enable-rerender-logs           --no-enable-rerender-logs                 [default: no-enable-rerender-logs]   │
│ --log-level                                                          TEXT  [default: INFO]                      │
│ --github-token                                                       TEXT  [env var: GITHUB_TOKEN]              │
│                                                                            [default: None]                      │
│ --dotenv                                                             TEXT  [default: None]                      │
│ --install-completion                                                       Install completion for the current   │
│                                                                            shell.                               │
│ --show-completion                                                          Show completion for the current      │
│                                                                            shell, to copy it or customize the   │
│                                                                            installation.                        │
│ --help                                                                     Show this message and exit.          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Development

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
