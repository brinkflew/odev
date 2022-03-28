"""Prepare odoo.sh and local repo to use `util` and `custom_util`"""

import os.path
import re
from argparse import Namespace
from typing import List, Set

from git import Repo, Submodule

from odev.commands.odoo_sh import sh_submodule
from odev.utils import logging


_logger: logging.Logger = logging.getLogger(__name__)


class OdooSHPrepareUtilCommand(sh_submodule.OdooSHSubmoduleCommand):
    """
    Prepare an odoo.sh project and its local repository clone for using `util` and `custom_util`
    (from the `util_package` repository) when doing builds and running modules' migration scripts.
    """

    name = "prepare-util"
    arguments = [
        {
            "name": "module_url",
            "nargs": "?",
            "default": "git@github.com:odoo-ps/util_package.git",
            "help": "URL to the `util_package` repository",
        },
        {
            "name": "module_path",
        },
        {
            "name": "commit",
            "aliases": ["--commit"],
            "default": "[UPG] add `util_package` submodule",
            "help": "Commit to the local repo after preparing the submodule with the given message",
        },
    ]

    base_path_on_sh: str = "/home/odoo/src/user"
    requirements_magic_comment: str = "generated by odev prepare-util"

    def __init__(self, args: Namespace):
        if args.no_local:
            args.commit = None

        super().__init__(args)

    def _add_requirements(self, git_submodule: Submodule) -> str:
        requirements_filename: str = "requirements.txt"
        requirements_path: str = os.path.join(self.local_repo_path, requirements_filename)

        _logger.info("Adding 'util_package' to local repo's 'requirements.txt'")

        requirements: List[str] = []
        if os.path.exists(requirements_path):
            with open(requirements_path, "r") as fp:
                requirements = fp.readlines()

            requirements = [
                line
                for line in requirements
                if not re.search(rf"#\s*{self.requirements_magic_comment}$", line.strip(), re.I)
            ]

        util_package_sh_path: str = f"{self.base_path_on_sh}/{git_submodule.path}"
        util_package_requirement: str = f"file:{util_package_sh_path}"
        requirements.append(f"{util_package_requirement}  # {self.requirements_magic_comment}\n")

        with open(requirements_path, "w") as fp:
            fp.writelines(requirements)

        return requirements_filename

    def _add_local_submodule(self, repo: Repo, paths_to_commit: Set[str]) -> Submodule:
        git_submodule: Submodule = super()._add_local_submodule(repo, paths_to_commit)

        requirements_filename: str = self._add_requirements(git_submodule)
        paths_to_commit.add(requirements_filename)

        return git_submodule
