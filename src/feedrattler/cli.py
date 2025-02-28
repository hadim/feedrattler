"""
feedrattler.py - Convert conda-forge feedstocks from v0 to v1 recipe format

```bash
# conda-forge dependencies
pixi add python pygithub gitpython typer rich conda-smithy conda-recipe-manager ruamel.yaml python-dotenv
```

You need a GH fine-grained token with "Read and Write access to administration and code"
"""

from typing import Optional
import os
import logging
import typer

from github import Github

from dotenv import load_dotenv
from rich.logging import RichHandler

from .convert import convert_feedstock_to_v1, CloneType


logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def main(
    feedstock_name: str,
    github_username: Optional[str] = None,
    use_pixi: bool = True,
    local_clone_dir: Optional[str] = None,
    local_clone_dir_force_erase: bool = False,
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

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    gh = Github(login_or_token=github_token)

    convert_feedstock_to_v1(
        gh=gh,
        feedstock_name=feedstock_name,
        github_username=github_username,
        use_pixi=use_pixi,
        local_clone_dir=local_clone_dir,
        local_clone_dir_force_erase=local_clone_dir_force_erase,
        branch_name=branch_name,
        enable_rerender_logs=enable_rerender_logs,
        do_rerender=rerender,
        clone_type=clone_type,
    )
