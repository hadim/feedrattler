"""
feedrattler.py - Convert conda-forge feedstocks from v0 to v1 recipe format

```bash
# conda-forge dependencies
pixi add python pygithub gitpython typer rich conda-smithy conda-recipe-manager ruamel.yaml python-dotenv
```

You need a GH fine-grained token with "Read and Write access to administration and code"
"""

import logging
import os
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv
from github import Github
from rich.logging import RichHandler

from .convert import convert_feedstock_to_v1
from .utils import (
    CloneType,
    auto_detect_clone_type,
    detect_username_ssh,
    token_from_gh_cli,
)

logger = logging.getLogger(__name__)

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool):
    if value:
        from . import __version__

        typer.echo(f"feedrattler {__version__}")
        raise typer.Exit()


@app.command()
def main(
    feedstock_name: Annotated[str, typer.Argument(help="📦 The name of the feedstock repository.")],
    github_username: Annotated[
        Optional[str], typer.Argument(help="👤 The GitHub username or organization that owns the feedstock.")
    ] = None,
    use_pixi: Annotated[
        bool,
        typer.Option(
            help="🚀 Add `pixi` to the conda-forge configuration `conda_install_tool` to manage the conda environment."
        ),
    ] = True,
    local_clone_dir: Annotated[
        Optional[str],
        typer.Option(
            help="📁 Path to a local clone of the feedstock repository. A temporary dir will be created if not set."
        ),
    ] = None,
    local_clone_dir_force_erase: Annotated[
        bool, typer.Option(help="💥 Force erase the local clone directory if it exists.")
    ] = False,
    git_rev: Annotated[
        Optional[str],
        typer.Option(
            help="📌 The git SHA to clone the feedstock. The default branch HEAD is used when not set."
        ),
    ] = None,
    branch_name: Annotated[
        str, typer.Option(help="🌿 The name of the branch to create for the converted recipe.")
    ] = "convert_feedstock_to_v1_recipe_format",
    rerender: Annotated[
        bool, typer.Option(help="🔄 Whether to re-render the feedstock after conversion.")
    ] = True,
    draft_pr: Annotated[bool, typer.Option(help="📝 Whether to create a draft pull request or not.")] = True,
    enable_rerender_logs: Annotated[
        bool, typer.Option(help="📝 Enable detailed logs from the re-rendering process.")
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(help="🚦 The log level to use. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL"),
    ] = "INFO",
    github_token: Annotated[
        Optional[str],
        typer.Option(
            envvar="GITHUB_TOKEN",
            help="🔑 GitHub token. Defaults to the GITHUB_TOKEN environment variable or gh cli.",
        ),
    ] = None,
    dotenv: Annotated[
        Optional[str], typer.Option(help="📄 Path to a .env file containing environment variables.")
    ] = None,
    clone_type: Annotated[
        CloneType, typer.Option(help="🐑 The type of clone to use (ssh or https).")
    ] = CloneType.auto,
    version: Annotated[
        bool,
        typer.Option("--version", callback=version_callback, help="Show the version of the application."),
    ] = False,
):
    load_dotenv(dotenv)
    github_token = os.getenv("GITHUB_TOKEN", github_token)
    if not github_token:
        github_token = token_from_gh_cli(github_username)

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    gh = Github(login_or_token=github_token)
    # If we have a token, check if it's valid and corresponds to the username
    if github_token:
        github_username_api = gh.get_user().login
        if github_username is None:
            github_username = github_username_api
        if github_username != github_username_api:
            raise ValueError(f"GitHub username mismatch: {github_username} != {github_username_api}")

    # If we still don't have a username, try to detect it from SSH
    if github_username is None:
        github_username = detect_username_ssh()

    # Automatic detection failed so give up
    if github_username is None:
        raise ValueError("GitHub username couldn't be auto detected")

    # If a clone type wasn't specified, try to auto-detect it
    if clone_type == CloneType.auto:
        clone_type = auto_detect_clone_type(github_username)

    convert_feedstock_to_v1(
        gh=gh,
        feedstock_name=feedstock_name,
        github_username=github_username,
        use_pixi=use_pixi,
        local_clone_dir=local_clone_dir,
        local_clone_dir_force_erase=local_clone_dir_force_erase,
        git_rev=git_rev,
        branch_name=branch_name,
        enable_rerender_logs=enable_rerender_logs,
        do_rerender=rerender,
        clone_type=clone_type,
        draft_pr=draft_pr,
    )
