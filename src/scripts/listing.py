"""Lists all the local Odoo databases in PostgreSQL."""

from clint.textui import puts, colored

from .database import LocalDBCommand
from .. import utils


class ListingScript(LocalDBCommand):
    command = "list"
    aliases = ("ls",)
    help = """
        Lists all the local Odoo databases. If a database is defined in PostgreSQL
        but not initialized with Odoo, it will not appear in this list.
    """
    database_required = False

    def run(self):
        """
        Lists local Odoo databases.
        """

        # details = '--details' in options.flags
        databases = self.db_list()

        utils.log('info', 'Listing local Odoo databases...')

        for database in databases:
            db = {
                'name': database,
                'version': self.db_config_get(database, 'version_clean'),
                'enterprise': self.db_config_get(database, 'enterprise'),
                'running': self.db_runs(database),
            }

            if not db["version"]:
                db["version"] = self.db_config(
                    database,
                    version_clean=self.db_version_clean(database),
                )["version_clean"]

            # TODO: replace "standard" with "community"
            if not db["enterprise"]:
                db["enterprise"] = self.db_config(
                    database,
                    enterprise="enterprise" if self.db_enterprise(database) else "standard",
                )["enterprise"]

            db['status'] = colored.green('⬤') if db['running'] else colored.red('⬤')
            db['name'] = '%s %s' % (db['name'], colored.black('.') * (25 - len(db['name'])))
            db['version'] = '(%s - %s)' % (db['version'], db['enterprise'])
            db['url'] = '[%s]' % (self.db_url(database)) if db['running'] else ''

            puts(' %s  %s %s %s' % (db['status'], db['name'], db['version'], db['url']))

        return 0
