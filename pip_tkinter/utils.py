from __future__ import absolute_import

import sys

from pip.commands.search import highest_version

from pip import parseopts, main

from io import StringIO

search_hits = {}
sysout = StringIO()
syserr = StringIO()


class redirect:
    """Context manager for temporarily redirecting stdout/err.
    Simplified and generalize from contextlib.redirect_stdout.
    """

    def __init__(self, stdfile, new_target):
        self._stdfile = stdfile  # 'stdout' or 'stderr'
        self._new_target = new_target

    def __enter__(self):
        self._old = getattr(sys, self._stdfile)
        setattr(sys, self._stdfile, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stdfile, self._old)


# For GUI version, redirects would be here, done once.
# Put in runpip for prototype testing in text mode, so can print.
def runpip(argstring):
    """Run pip with argument string containing command and options.

    :param argstring: is quoted version of what would follow 'pip'
      on command line.
    """
    with redirect('stdout', sysout) as f1, redirect('stderr', syserr) as f2:
        status = main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err


def get_search_results(hits):
    """
    This code is taken from pip.commands.search.print_results(). It is modified
    to return results in dictionary format instead of printing results
    For all the search results obtained, we can check if a package is already
    installed or not. If installed then the version of installed package is
    found and stored.
    """
    if not hits:
        return None

    # Here pkg_resources is a module of pip._vendor. It has been included
    # in pip gui because as mentioned by pip, this module is considered to
    # be 'immutable'. There are very less chances that it will changed in future
    from pip_tkinter._vendor import pkg_resources
    installed_packages = [p.project_name for p in pkg_resources.working_set]
    for hit in hits:
        hit['latest'] = highest_version(hit['versions'])
        name = hit['name']
        if name in installed_packages:
            dist = pkg_resources.get_distribution(name)
            hit['installed'] = dist.version

    return hits


def pip_search_command(package_name):
    """
    Uses pip.commands.search.SearchCommand to retrieve results of 'pip search'
    """
    from pip_tkinter.pip_extensions import GUISearchCommand
    search_object = GUISearchCommand()
    cmd_name, cmd_args = parseopts(['search', package_name])
    search_object.main(cmd_args)
    return get_search_results(search_hits)


def pip_install_command_PyPI(package_args):
    """
    Wrapper for installing pip package from PyPI
    """
    return runpip('install -U {}'.format(package_args))
