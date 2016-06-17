from __future__ import absolute_import

import sys
import copy

from io import StringIO

from pip.commands.search import SearchCommand, transform_hits, highest_version
from pip.commands.list import ListCommand
from pip.exceptions import CommandError
from pip.basecommand import SUCCESS
from pip import main

from pip_tkinter.utils import Redirect

# For GUI version, redirects would be here, done once.
# Put in runpip for prototype testing in text mode, so can print.
def runpip(argstring):
    """Run pip with argument string containing command and options.

    :param argstring: is quoted version of what would follow 'pip'
      on command line.
    """
    with Redirect('stdout', sysout) as f1, Redirect('stderr', syserr) as f2:
        status = main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err


class GUISearchCommand(SearchCommand):
    """
    Inherited the class : pip.commands.search.SearchCommand to override
    run method

    Advantage of inheriting the class is that we can have better control of
    pip. For example, currently pip search gives output for latest version.
    But, we can retrieve output for all available versions.

    Another advantage is that search can now be done with less time lag as
    compared to pip.main().
    """

    def run(self, options, args):
        if not args:
            raise CommandError('Missing required argument (search query).')
        query = args
        try:
            # The developer version of pip uses options as argument
            pypi_hits = self.search(query,options)
        except TypeError:
            # But, the stable version of pip uses options.index as argument
            pypi_hits = self.search(query,options.index)
        self.hits = transform_hits(pypi_hits)
        return SUCCESS

    def get_search_results(self):
        """
        This code is taken from pip.commands.search.print_results(). It is modified
        to return results in dictionary format instead of printing results
        For all the search results obtained, we can check if a package is already
        installed or not. If installed then the version of installed package is
        found and stored.
        """
        if not self.hits:
            return None

        # Here pkg_resources is a module of pip._vendor. It has been included
        # in pip gui because as mentioned by pip, this module is considered to
        # be 'immutable'. There are very less chances that it will changed in future
        from pip_tkinter._vendor import pkg_resources
        self.installed_packages = [p.project_name for p in pkg_resources.working_set]
        for hit in self.hits:
            hit['latest'] = highest_version(hit['versions'])
            name = hit['name']
            if name in self.installed_packages:
                dist = pkg_resources.get_distribution(name)
                hit['installed'] = dist.version

        return self.hits

class GUIListCommand(ListCommand):
    """
    Extending the pip ListCommand to show list of packages :

    1. For uninstall : retrieves list of installed packages with their versions
    2. For update : retrieved list of installed packages which are outdated
    """

    self.installed_packages_list = []
    self.outdated_packages_list = []
    self.find_outdated = False

    def output_package_listing(self, installed_packages):

        installed_packages = sorted(
            installed_packages,
            key=lambda dist: dist.project_name.lower(),
        )

        for dist in installed_packages:
            self.installed_packages_list.append(dist.project_name, dist.version)

    def run_outdated(self, options):

        if options.outdated:
            self.find_outdated = True

        for dist, latest_version, typ in sorted(
                self.find_packages_latest_versions(options),
                key=lambda p: p[0].project_name.lower()):
            if latest_version > dist.parsed_version:
                self.outdated_packages_list.append((
                    dist.project_name,
                    dist.version,
                    str(latest_version),
                ))

    def get_installed_packages_list(self):

        if self.find_outdated:
            return self.outdated_packages_list

        else:
            return self.installed_packages_list
