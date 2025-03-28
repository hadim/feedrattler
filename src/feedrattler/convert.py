import contextlib
import logging
import os
import pathlib
import shutil
import tempfile
import time
from typing import Optional

from conda_recipe_manager.commands.convert import convert_file
from conda_recipe_manager.commands.utils.types import ExitCode
from conda_smithy import configure_feedstock
from git import Repo
from github import Github, UnknownObjectException

from . import __version__
from .utils import (
    CloneType,
    initialize_yaml,
    remove_empty_script_test,
    rename_bld_bat_to_build_bat,
    update_python_min_in_recipe,
    update_python_version_in_tests,
)

logger = logging.getLogger(__name__)


def convert_feedstock_to_v1(
    gh: Github,
    feedstock_name: str,
    github_username: str,
    use_pixi: bool = False,
    local_clone_dir: Optional[str] = None,
    local_clone_dir_force_erase: bool = False,
    git_rev: Optional[str] = None,
    branch_name: str = "convert_feedstock_to_v1_recipe_format",
    enable_rerender_logs: bool = False,
    do_rerender: bool = True,
    clone_type: CloneType = CloneType.https,
    draft_pr: bool = True,
):
    # Step 0: Initialize

    logging.info(
        f"🚀 Start converting conda-forge/{feedstock_name} to v1 recipe using GH user '{github_username}'"
    )
    logging.info(f"📦 feedstock_name={feedstock_name}")
    logging.info(f"👤 github_username={github_username}")
    logging.info(f"🔧 use_pixi={use_pixi}")

    org = gh.get_organization("conda-forge")
    gh_repo = org.get_repo(feedstock_name)

    # Step 1: Check if feedstock is already a v1 feedstock

    logging.info(f"🔍 Checking if {feedstock_name} is already a v1 feedstock with `recipe/recipe.yaml`")
    try:
        if git_rev is not None:
            gh_repo.get_contents("recipe/recipe.yaml", ref=git_rev)
        else:
            gh_repo.get_contents("recipe/recipe.yaml")
        is_v1_feedstock = True
    except UnknownObjectException:
        is_v1_feedstock = False

    if is_v1_feedstock:
        raise Exception(f"❗ {feedstock_name} is already a v1 feedstock since `recipe/recipe.yaml` exists.")

    logging.info(f"✅ {feedstock_name} is not a v1 feedstock.")

    # Step 2: Clone the repository

    if local_clone_dir is None:
        repo_dir_temp_parent = pathlib.Path(tempfile.mkdtemp())
    else:
        repo_dir_temp_parent = pathlib.Path(local_clone_dir)

        if repo_dir_temp_parent.exists():
            if local_clone_dir_force_erase:
                # delete the directory if it already exists
                logging.info(f"🗑️ Deleting existing directory {repo_dir_temp_parent}")
                shutil.rmtree(repo_dir_temp_parent)
            else:
                raise Exception(f"❗ Directory {repo_dir_temp_parent} already exists")

    # conda-smithy requires the clone directory to be named after the feedstock
    repo_dir_temp = repo_dir_temp_parent / feedstock_name

    logger.info(f"🔄 Cloning {gh_repo.clone_url} to {repo_dir_temp}")
    git_repo = Repo.clone_from(gh_repo.clone_url, repo_dir_temp)

    # If git_rev is set then checkout the revision
    if git_rev is not None:
        logging.info(f"🔄 Checking out git revision {git_rev}")
        git_repo.git.checkout(git_rev)

    # Create a new branch and checkout
    new_branch = git_repo.create_head(branch_name)
    new_branch.checkout()

    # Step 3: Convert `meta.yaml` to `recipe.yaml`

    logging.info("🔄 Converting `meta.yaml` to `recipe.yaml`")
    meta_yaml_path = repo_dir_temp / "recipe" / "meta.yaml"
    recipe_yaml_path = repo_dir_temp / "recipe" / "recipe.yaml"
    result = convert_file(meta_yaml_path, output=recipe_yaml_path, print_output=False, debug=False)

    if result.code == ExitCode.RENDER_WARNINGS:
        warning_msg = f"❗ Warning while converting {meta_yaml_path} to {recipe_yaml_path}"
        # NOTE: not super clean to directly call `_tbl` but it's a quick way to get the error message
        warning_msg += "\n" + str(result.msg_tbl._tbl)
        logging.warning(warning_msg)
    elif result.code != ExitCode.SUCCESS:
        error_msg = f"❗ Failed to convert {meta_yaml_path} to {recipe_yaml_path}"
        # NOTE: not super clean to directly call `_tbl` but it's a quick way to get the error message
        error_msg += str(result.msg_tbl._tbl)
        raise Exception(error_msg)

    # Delete meta.yaml file
    os.remove(meta_yaml_path)

    logging.info(f"✅ Successfully converted {meta_yaml_path} to {recipe_yaml_path}")

    # Step 4: Edit `conda-forge.yml` to use `rattler-build` and `pixi`

    conda_forge_config_path = repo_dir_temp / "conda-forge.yml"
    logging.info(f"📄 Loading {conda_forge_config_path}")

    yaml = initialize_yaml()

    with open(conda_forge_config_path, "r") as f:
        conda_forge_config = yaml.load(f)

    # Whether to use pixi as conda install tool
    if use_pixi:
        if conda_forge_config.get("conda_install_tool", None) != "pixi":
            logging.info("🔧 Setting conda_install_tool to 'pixi'")
            conda_forge_config["conda_install_tool"] = "pixi"

    logging.info("🔧 Setting conda_build_tool to 'rattler-build'")
    conda_forge_config["conda_build_tool"] = "rattler-build"

    logging.info(f"💾 Writing updated {conda_forge_config_path}")
    with open(conda_forge_config_path, "w") as f:
        yaml.dump(conda_forge_config, f)

    # Step 5: bump the build number

    logging.info(f"🔢 Bumping build number in {recipe_yaml_path}")

    yaml = initialize_yaml()

    with open(recipe_yaml_path, "r") as f:
        recipe_yaml = yaml.load(f)

    build_number_raw = recipe_yaml["build"]["number"]
    try:
        build_number = int(build_number_raw) + 1
    except ValueError:
        raise Exception(f"❗ Failed to bump build number: {build_number_raw} is not an integer")

    recipe_yaml["build"]["number"] = build_number

    logging.info(f"💾 Writing updated {recipe_yaml_path}")
    with open(recipe_yaml_path, "w") as f:
        yaml.dump(recipe_yaml, f)

    # fix #1: replace `python ${{ python_min }}` by `python ${{ python_min }}.*`
    # NOTE: waiting for upstream fix at https://github.com/conda-incubator/conda-recipe-manager/issues/308
    update_python_min_in_recipe(recipe_yaml_path)

    # fix #2: if noarch=python then add python_min to tests[].python.python_version
    # NOTE: waiting for upstream fix at https://github.com/conda-incubator/conda-recipe-manager/issues/309
    update_python_version_in_tests(recipe_yaml_path)

    # fix #3: remove script test if tests[].script does not exist
    # NOTE: waiting for upstream fix at https://github.com/hadim/feedrattler/issues/7
    remove_empty_script_test(recipe_yaml_path)

    # fix #4: if present rename bld.bat to build.bat
    # NOTE: waiting for upstream discussion at https://github.com/conda-incubator/conda-recipe-manager/issues/314
    rename_bld_bat_to_build_bat(recipe_yaml_path)

    # Step 6: Commit changes

    logging.info("📝 Committing changes")

    commit_message = "Convert to v1 feedstock"
    if use_pixi:
        commit_message += " and use pixi as conda install tool"

    git_repo = Repo(repo_dir_temp)

    # Add and commit changes
    git_repo.git.add(".")
    git_repo.git.commit("-m", commit_message)

    # Step 7: Rerender the feedstock

    if do_rerender:
        logging.info("🔄 Rerendering the feedstock")
        with open(os.devnull, "w") as devnull:
            with (
                contextlib.redirect_stdout(None if enable_rerender_logs else devnull),
                contextlib.redirect_stderr(None if enable_rerender_logs else devnull),
            ):
                configure_feedstock.main(
                    forge_file_directory=repo_dir_temp,
                    forge_yml=None,
                    no_check_uptodate=True,  # NOTE: ok or not?
                    commit=True,
                    exclusive_config_file=None,
                    check=False,
                    temporary_directory=None,
                )

    # Step 8: Check if the user has a fork of the feedstock, if not create it

    gh_user = gh.get_user(github_username)
    try:
        fork_repo = gh_user.get_repo(feedstock_name)
    except UnknownObjectException:
        logging.info(f"🔀 Creating fork for {github_username}/{feedstock_name}")
        fork_repo = gh_repo.create_fork()
        time.sleep(2)

        # Wait for the fork to be created
        # NOTE: might be overkill...
        max_retries = 30
        for attempt in range(max_retries):
            try:
                gh_user.get_repo(feedstock_name)
                logging.info(f"✅ Fork created successfully on attempt {attempt + 1}")
                break
            except UnknownObjectException:
                logging.info(f"⏳ Waiting for fork creation... attempt {attempt + 1}/{max_retries}")
                time.sleep(2)
        else:
            raise Exception(
                f"❗ Fork creation for {github_username}/{feedstock_name} failed after {max_retries} attempts"
            )

    # Let's sleep 2 more seconds before pushing to the fork
    time.sleep(2)

    # Step 9: Push changes to the fork
    if clone_type == CloneType.ssh:
        fork_clone_url = fork_repo.ssh_url
    elif clone_type == CloneType.https:
        fork_clone_url = fork_repo.clone_url
    else:
        raise NotImplementedError(f"❗ {clone_type=} is not implemented")

    git_repo.remotes.origin.set_url(fork_clone_url)
    git_repo.remotes.origin.push(refspec=f"{branch_name}:{branch_name}")
    logging.info(f"🚀 Pushed changes to {github_username}/{feedstock_name}:{branch_name}")

    # Step 10: Create a PR to the conda-forge feedstock

    pr_title = f"Convert {feedstock_name} to v1 feedstock"
    pr_body = f"""This PR converts {feedstock_name} to a v1 recipe and switch the conda build tool to rattler-build.
It has been automatically generated with [feedrattler v{__version__}](https://github.com/hadim/feedrattler).

Changes:
- [x] 📝 Converted `meta.yaml` to `recipe.yaml`
- [x] Used a [personal fork of the feedstock to propose changes](https://conda-forge.org/docs/maintainer/updating_pkgs.html#forking-and-pull-requests)
- [x] 🔧 Updated `conda-forge.yml` to use `rattler-build` and `pixi` (optional)
- [x] 🔢 Bumped the build number
- [x] 🐍 Applied temporary fixes for `python_min` and `python_version`
- [x] 🔄 Rerender the feedstock with conda-smithy
- [ ] Ensured the license file is being packaged.
"""

    logging.info("Creating a pull request to the conda-forge feedstock")
    try:
        pr = gh_repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=f"{github_username}:{branch_name}",
            base="main",
            draft=draft_pr,
        )
        logging.info(f"Created pull request: {pr.html_url}")
    except Exception as e:
        logging.error(f"❗ Failed to create a pull request: {e}")
        pr_url = (
            f"https://github.com/conda-forge/{feedstock_name}/compare/main...{github_username}:{branch_name}"
        )
        logging.info(f"Create a PR manually at {pr_url} 🚀")
        print(f"PR title: {pr_title} 🎉")
        print(f"PR body:\n{pr_body} ✨")
