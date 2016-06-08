from __future__ import absolute_import

import sys

from pip.commands.search import highest_version
from pip import parseopts, main
from io import StringIO

search_hits = {}

class Redirect:
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
    sysout = StringIO()
    syserr = StringIO()

    with Redirect('stdout', sysout) as f1, Redirect('stderr', syserr) as f2:
        status = main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err


def pip_search_command(package_name):
    """
    Uses pip.commands.search.SearchCommand to retrieve results of 'pip search'
    """
    from pip_tkinter.pip_extensions import GUISearchCommand
    search_object = GUISearchCommand()
    cmd_name, cmd_args = parseopts(['search', package_name])
    search_object.main(cmd_args)
    return search_object.get_search_results()


def pip_install_from_PyPI(package_args):
    """
    Wrapper for installing pip package from PyPI
    """
    return runpip('install -U {}'.format(package_args))

def pip_install_from_local_archive(package_args):
    """
    Wrapper for installing pip package from local Archive
    """
    return runpip('install {}'.format(package_args))

def pip_install_from_requirements(package_args):
    """
    Wrapper for installing pip package from requirements file
    """
    return runpip('install -r {}'.format(package_args))

def pip_install_from_alternate_repo(package_args):
    """
    Wrapper for installing pip package from Pythonlibs
    """
    return runpip('install --index-url{}'.format(package_args))

def pip_uninstall(package_args):
    """
    Uninstall packages
    """
    return runpip('uninstall {}'.format(package_args))
