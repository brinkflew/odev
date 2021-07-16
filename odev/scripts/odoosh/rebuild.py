import logging
from typing import ClassVar, Optional, Type, Any, Mapping

from .odoosh import OdooSHBranch, OdooSHSubRoot
from ...cli import CliCommandsSubRoot, CommandType


__all__ = ["OdooSHRebuild"]


logger = logging.getLogger(__name__)


class OdooSHRebuild(OdooSHBranch):
    """
    Command class for uploading and importing a database dump on a odoo.sh branch.
    """

    parent: ClassVar[Optional[Type[CliCommandsSubRoot]]] = OdooSHSubRoot
    command: ClassVar[CommandType] = "rebuild"
    help: ClassVar[Optional[str]] = "Rebuilds an SH branch."
    help_short: ClassVar[Optional[str]] = help

    def run(self) -> Any:
        branch_info: Optional[Mapping[str, Any]]
        branch_info = self.sh_connector.branch_info(self.sh_repo, self.sh_branch)

        if branch_info["stage"] == "production":
            raise RuntimeError(
                f'Branch "{self.sh_branch}" of "{self.sh_repo}" is production '
                f"and cannot be rebuilt"
            )

        logger.info(f'Rebuilding SH project "{self.sh_repo}" branch "{self.sh_branch}"')
        result: Any = self.sh_connector.branch_rebuild(self.sh_repo, self.sh_branch)
        if not isinstance(result, bool) or not result:
            result_info: str = str(result)
            if isinstance(result, dict) and "error" in result:
                result_info = str(result["error"])
            raise RuntimeError(
                f'Failed rebuilding branch "{self.sh_branch}" of "{self.sh_repo}":\n'
                + result_info
            )

        logger.info(f"Waiting for SH rebuild to complete")
        # TODO: make sure it's the right build, and doesn't get swapped
        self.wait_for_build(check_success=True)

        logger.success(
            f'Branch "{self.sh_branch}" of "{self.sh_repo}" rebuilt successfully'
        )
