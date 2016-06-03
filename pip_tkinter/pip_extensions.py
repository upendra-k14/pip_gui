from __future__ import absolute_import

import sys
import copy

from pip.commands.search import SearchCommand, transform_hits, highest_version
from pip.exceptions import CommandError
from pip.basecommand import SUCCESS
from pip import main

from io import StringIO


search_hits = {}
sysout = StringIO()
syserr = StringIO()


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
        hits = transform_hits(pypi_hits)
        global search_hits
        search_hits = copy.deepcopy(hits)
        return SUCCESS

