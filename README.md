# `feedrattler` 🐍

[release-badge]: https://img.shields.io/github/v/release/hadim/feedrattler?logo=github
[conda-badge]: https://anaconda.org/conda-forge/feedrattler/badges/version.svg?cache-control=no-cache
[conda-downloads-badge]: https://anaconda.org/conda-forge/feedrattler/badges/downloads.svg?cache-control=no-cache
[test-badge]: https://github.com/hadim/feedrattler/actions/workflows/test.yml/badge.svg?branch=main
[lint-badge]: https://github.com/hadim/feedrattler/actions/workflows/lint.yml/badge.svg?branch=main

[![GitHub Release][release-badge]](https://github.com/hadim/feedrattler/releases)
[![Conda Package][conda-badge]](https://anaconda.org/conda-forge/feedrattler/)
[![GitHub Downloads][conda-downloads-badge]](https://anaconda.org/conda-forge/feedrattler/)
[![Test CI][test-badge]](https://github.com/hadim/feedrattler/actions/workflows/test.yml)
[![Lint CI][lint-badge]](https://github.com/hadim/feedrattler/actions/workflows/lint.yml)

Convert conda-forge feedstock to rattler-build.

> [!IMPORTANT]
> This project uses [Conda Recipe Manager (CRM)](https://github.com/conda-incubator/conda-recipe-manager) to upgrade V0 (`meta.yaml`) recipe files to the new V1 (`recipe.yaml`) files.
> If you run into issues when it comes to upgrading to the `recipe.yaml` file specifically, **please consult the list of open [CRM Issues](https://github.com/conda-incubator/conda-recipe-manager/issues)** and submit a new ticket if you don't see an existing issue that describes your problem.

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
# or installed globally
pixi global install feedrattler
# or install latest (main) version from soure
pixi global install --git https://github.com/hadim/feedrattler
```

## Options ⚙️

<!-- Generate and edit with `pixi run typer feedrattler.cli utils docs --name feedrattler` -->

Use `feedrattler --help` to see all available options.

```console
feedrattler [OPTIONS] FEEDSTOCK_NAME [GITHUB_USERNAME]
```

**Arguments**:

- `FEEDSTOCK_NAME`: 📦 The name of the feedstock repository. [required]
- `[GITHUB_USERNAME]`: 👤 The GitHub username or organization that owns the feedstock.

**Options**:

- `--use-pixi / --no-use-pixi`: 🚀 Add `pixi` to the conda-forge configuration `conda_install_tool` to manage the conda environment. [default: use-pixi]
- `--local-clone-dir TEXT`: 📁 Path to a local clone of the feedstock repository. A temporary dir will be created if not set.
- `--local-clone-dir-force-erase / --no-local-clone-dir-force-erase`: 💥 Force erase the local clone directory if it exists. [default: no-local-clone-dir-force-erase]
- `--git-rev TEXT`: 📌 The git SHA to clone the feedstock. The default branch HEAD is used when not set.
- `--branch-name TEXT`: 🌿 The name of the branch to create for the converted recipe. [default: convert_feedstock_to_v1_recipe_format]
- `--rerender / --no-rerender`: 🔄 Whether to re-render the feedstock after conversion. [default: rerender]
- `--draft-pr / --no-draft-pr`: 📝 Whether to create a draft pull request or not. [default: draft-pr]
- `--enable-rerender-logs / --no-enable-rerender-logs`: 📝 Enable detailed logs from the re-rendering process. [default: no-enable-rerender-logs]
- `--log-level TEXT`: 🚦 The log level to use. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL [default: INFO]
- `--github-token TEXT`: 🔑 GitHub token. Defaults to the GITHUB_TOKEN environment variable or gh cli. [env var: GITHUB_TOKEN]
- `--dotenv TEXT`: 📄 Path to a .env file containing environment variables.
- `--clone-type [auto|ssh|https]`: 🐑 The type of clone to use (ssh or https). [default: auto]
- `--version`: Show the version of the application.
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

## Development 🛠️

You need to use [pixi](https://pixi.sh).

```bash
# Execute feedrattler CLI
pixi run feedrattler

# Run tests
pixi run tests

# Format code
pixi run format

# Lint code
pixi run lint

# Lint and format code
pixi run lint-format
```

## Release 🚢

The package is **not** released on PyPi but only on conda-forge at <https://github.com/conda-forge/feedrattler-feedstock>.

To cut a new release:

- Trigger [the `release` workflow on the main branch](https://github.com/hadim/feedrattler/actions/workflows/release.yaml).
- A new GitHub Release will be created with the new version.
- The conda-forge bot will create a PR to update the [feedstock](https://github.com/conda-forge/feedrattler-feedstock).
- Once the conda-forge PR merged, the new conda version will be available.

<!--- dummy edit --->
