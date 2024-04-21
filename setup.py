from os.path import join, dirname
import re
import setuptools

with open(join(dirname(__file__), "CHANGELOG.md"), "r") as file:
    changelog = file.read()

    # We fetch the version number from CHANGELOG.md
    # so that we don't have to maintain it in multiple places.
    match = re.search(r"## \[(?P<version>\d+\.\d+\.\d+)]", changelog, re.MULTILINE)
    if not match:
        raise ValueError("Could not find the latest version in CHANGELOG.md")

    version = match["version"]

setuptools.setup(version=version)
