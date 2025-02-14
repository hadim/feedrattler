import os
import logging
import ruamel.yaml


logger = logging.getLogger(__name__)


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
