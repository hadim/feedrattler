"""
feedrattler.py - Convert conda-forge feedstocks from v0 to v1 recipe format

```bash
# conda-forge dependencies
pixi add python pygithub gitpython typer rich conda-smithy conda-recipe-manager ruamel.yaml python-dotenv
```

You need a GH fine-grained token with "Read and Write access to administration and code"
"""

from typing import Annotated, Optional
import os
import logging
import typer

from github import Github

from dotenv import load_dotenv
from rich.logging import RichHandler

from .convert import convert_feedstock_to_v1
from .utils import (
    auto_detect_clone_type,
    detect_username_ssh,
    token_from_gh_cli,
    CloneType,
)


logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def main(
    feedstock_name: str,
    github_username: Annotated[Optional[str], typer.Argument()] = None,
    use_pixi: bool = True,
    local_clone_dir: Optional[str] = None,
    local_clone_dir_force_erase: bool = False,
    git_rev: Annotated[
        Optional[str],
        typer.Option(help="The git SHA to clone the feedstock. The default branch HEAD is used when None."),
    ] = None,
    branch_name: str = "convert_feedstock_to_v1_recipe_format",
    rerender: bool = True,
    enable_rerender_logs: bool = False,
    log_level: str = "INFO",
    github_token: Optional[str] = typer.Option(None, envvar="GITHUB_TOKEN"),
    dotenv: Optional[str] = None,
    clone_type: CloneType = CloneType.auto,
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
    )
