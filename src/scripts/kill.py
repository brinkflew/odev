"""Kills a running Odoo database."""

import logging
import os

from .database import LocalDBCommand


_logger = logging.getLogger(__name__)


class KillScript(LocalDBCommand):
    command = "kill"
    help = """
        Kills a running Odoo database. Useful if the process crashed because of
        a forgotten IPDB or if you lost your terminal and don't want to search
        for the process' PID.
    """

    def run(self):
        """
        Kills the process of a running local database.
        """

        self.db_is_valid()
        self.ensure_running()

        _logger.info(f'Stopping database {self.database}')
        pid = self.db_pid()

        while pid:
            os.system('kill -9 %s' % (pid))

        return 0
