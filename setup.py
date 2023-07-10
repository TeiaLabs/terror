from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

import setuptools


def read_multiline_as_list(file_path: Path | str) -> list[str]:
    with open(file_path) as fh:
        contents = fh.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


def get_version() -> str:
    raw_git_cmd = "git describe --tags"
    git_cmd = shlex.split(raw_git_cmd)
    fmt_cmd = shlex.split("cut -d '-' -f 1,2")
    git = subprocess.Popen(git_cmd, stdout=subprocess.PIPE)
    cut = subprocess.check_output(fmt_cmd, stdin=git.stdout)
    ret_code = git.wait()
    assert ret_code == 0, f"{raw_git_cmd!r} failed with exit code {ret_code}."
    return cut.decode().strip()


with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = read_multiline_as_list("requirements.txt")

setuptools.setup(
    name="terror",
    version=get_version(),
    author="TeiaLabs",
    author_email="contato@teialabs.com",
    description="FastAPI Compatible Error Handling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeiaLabs/terror",
    packages=setuptools.find_packages(),
    python_requires=">=3.11",
    install_requires=requirements,
)
