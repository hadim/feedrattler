import logging
import os
import re
import shutil
import subprocess
from enum import Enum
from typing import Optional

import ruamel.yaml

logger = logging.getLogger(__name__)


class CloneType(str, Enum):
    auto = "auto"
    ssh = "ssh"
    https = "https"


def initialize_yaml():
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    yaml.preserve_quotes = True
    return yaml


def update_python_min_in_recipe(yaml_file_path: os.PathLike):
    """
    Loads a YAML file using ruamel, updates 'requirements.host' and 'tests' sections
    to replace 'python ${{ python_min }}' with 'python ${{ python_min }}.*'.

    Args:
        yaml_file_path: The path to the YAML file.
    """

    yaml = initialize_yaml()

    with open(yaml_file_path, "r") as f:
        data = yaml.load(f)

    # Only proceed if build.noarch is set to python
    if data.get("build", {}).get("noarch", "") != "python":
        return

    logging.info("🔄 Updating `recipe.yaml` to use `${{ python_min }}.*`")

    def replace_python_min(value):
        if (
            isinstance(value, str)
            and "python ${{ python_min }}" in value
            and "python ${{ python_min }}.*" not in value
        ):
            return value.replace("${{ python_min }}", "${{ python_min }}.*")
        return value

    # Update requirements.host
    if "host" in data.get("requirements", {}):
        data["requirements"]["host"] = [replace_python_min(v) for v in data["requirements"]["host"]]

    # Update tests[].requirements.run and tests[].python.python_version
    for test in data.get("tests", []):
        if "requirements" in test and "run" in test["requirements"]:
            test["requirements"]["run"] = [replace_python_min(v) for v in test["requirements"]["run"]]
        if "python" in test and "python_version" in test["python"]:
            test["python"]["python_version"] = replace_python_min(test["python"]["python_version"])

    with open(yaml_file_path, "w") as f:
        yaml.dump(data, f)


def update_python_version_in_tests(yaml_file_path: os.PathLike):
    """
    Loads a YAML file using ruamel, checks the 'tests' section for 'python' elements,
    and sets 'python_min' if it's not already present.

    Args:
        yaml_file_path: The path to the YAML file.
    """

    yaml = initialize_yaml()

    with open(yaml_file_path, "r") as f:
        data = yaml.load(f)

    # Only proceed if build.noarch is set to python
    if data.get("build", {}).get("noarch", "") != "python":
        return

    logging.info("🔄 Updating `recipe.yaml` to add `python_min` to tests[].python")

    # Handle both SimpleRecipe and ComplexRecipe structures
    if "tests" in data:
        tests_section = data["tests"]
    elif "outputs" in data:
        tests_section = []
        for output in data["outputs"]:
            if "tests" in output:
                tests_section.extend(output["tests"])
    else:
        tests_section = []

    # Iterate through each test element

    for test_element in tests_section:
        if isinstance(test_element, ruamel.yaml.CommentedMap) and "python" in test_element:
            python_section = test_element["python"]
            if isinstance(python_section, ruamel.yaml.CommentedMap) and "imports" in python_section:
                if "python_version" not in python_section:
                    python_section["python_version"] = r"${{ python_min }}.*"

    with open(yaml_file_path, "w") as f:
        yaml.dump(data, f)


def token_from_gh_cli(github_username: Optional[str]) -> Optional[str]:
    if not shutil.which("gh"):
        return
    logger.info("🔍 Found gh CLI, trying to get auth token")
    cmd = ["gh", "auth", "token", "-h", "github.com"]
    if github_username:
        cmd.extend(["-u", github_username])
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        logger.info("⚠️ Failed to get token from gh CLI")
        return
    logger.info("🔑 Got token from gh CLI")
    return proc.stdout.strip()


def detect_username_ssh() -> Optional[str]:
    try:
        proc = subprocess.run(
            ["ssh", "ssh://git@github.com"],
            check=False,
            capture_output=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        logger.warning("❗ Timeout while trying to detect GitHub username/SSH access")
    else:
        match = re.search(rb"Hi ([^!]+)! You've successfully authenticated", proc.stderr)
        if match:
            username = match.group(1).decode()
            logger.info(f"🔍 Detected GitHub username: {username}")
            return username


def auto_detect_clone_type(github_username: str) -> CloneType:
    # If gh CLI is available, prefer its settings
    if shutil.which("gh"):
        cmd = ["gh", "auth", "status", "-h", "github.com"]
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if proc.returncode == 0:
            match = re.search(r"Git operations protocol: (\w+)", proc.stdout)
            if match:
                git_protocol = match.group(1)
                logger.info(f"🔍 Detected git_protocol from gh CLI: {git_protocol}")
                return CloneType(git_protocol)
        logger.warning("⚠️ Failed to detect git_protocol from gh CLI")

    # If we have SSH access to GitHub, use SSH
    github_username_ssh = detect_username_ssh()
    if github_username_ssh:
        if github_username_ssh != github_username:
            raise ValueError(f"GitHub username mismatch with SSH: {github_username} != {github_username_ssh}")
        return CloneType.ssh

    return CloneType.https


def remove_empty_script_test(yaml_file_path: os.PathLike):
    """Remove the test section if it is empty."""

    yaml = initialize_yaml()

    with open(yaml_file_path, "r") as f:
        data = yaml.load(f)

    # Only proceed if build.noarch is set to python
    if data.get("build", {}).get("noarch", "") != "python":
        return

    logging.info("🔄 Remove empty script test section if needed")

    # Handle both SimpleRecipe and ComplexRecipe structures
    if "tests" in data:
        tests_section = data["tests"]
    elif "outputs" in data:
        tests_section = []
        for output in data["outputs"]:
            if "tests" in output:
                tests_section.extend(output["tests"])
    else:
        tests_section = []

    # Iterate through each test element

    for test_element in tests_section:
        if isinstance(test_element, ruamel.yaml.CommentedMap) and "requirements" in test_element:
            if "script" not in test_element:
                tests_section.remove(test_element)

    with open(yaml_file_path, "w") as f:
        yaml.dump(data, f)

def rename_bld_bat_to_build_bat(yaml_file_path: os.PathLike):
    """If present, rename bld.bat to build.bat"""

    yaml_file_folder = os.path.dirname(yaml_file_path)
    candidate_bld_bat_path = os.path.join(yaml_file_folder, "bld.bat")

    if not os.path.exists(candidate_bld_bat_path):
        return

    build_bat_path = os.path.join(yaml_file_folder, "build.bat")

    # If bld.bat exists but build.bat already exits, do not rename and print a warning
    if os.path.exists(build_bat_path):
        raise Exception(f"❗ both `bld.bat` and `build.bat` script already exists so it is not possible to rename `bld.bat` to `build.bat`")

    logging.info("🔄 Renaming `bld.bat` script to `build.bat`")

    os.rename(candidate_bld_bat_path, build_bat_path)
