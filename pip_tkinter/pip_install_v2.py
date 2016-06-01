from io import StringIO
import pip
from pip import main
#from pip import SearchCommand
from pip import parseopts
from pip.commands.search import SearchCommand
from pip.commands.show import ShowCommand, search_packages_info
from pip.commands.completion import CompletionCommand
from pip.commands.freeze import FreezeCommand
from pip.commands.help import HelpCommand
from pip.commands.list import ListCommand
from pip.commands.search import SearchCommand
from pip.commands.show import ShowCommand
from pip.commands.install import InstallCommand
from pip.commands.uninstall import UninstallCommand
from pip.commands.wheel import WheelCommand
from pip.exceptions import InstallationError, CommandError, PipError
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import sys
import logging
import os

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
    '''Run pip with argument string containing command and options.

    Argstring is quoted version of what would follow 'pip'
    on command line.
    '''
    with redirect('stdout', sysout) as f1, redirect('stderr', syserr) as f2:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, base)
        status = main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err

def runpip_using_subprocess(argstring):
    '''Run pip with argument string containing command and options.
    Argstring is quoted version of what would follow 'pip' on command line.
    '''
    with redirect('stdout', sysout) as f1, redirect('stderr', syserr) as f2:
        status = subprocess.Popen(
                    ["pip"]+argstring.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        out, err = status.communicate()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return out.decode('utf-8'), err.decode('utf-8')

logger = logging.getLogger(__name__)

commands_dict = {
    CompletionCommand.name: CompletionCommand,
    FreezeCommand.name: FreezeCommand,
    HelpCommand.name: HelpCommand,
    SearchCommand.name: SearchCommand,
    ShowCommand.name: ShowCommand,
    InstallCommand.name: InstallCommand,
    UninstallCommand.name: UninstallCommand,
    ListCommand.name: ListCommand,
    WheelCommand.name: WheelCommand,
}


def check_isolated(args):
    isolated = False

    if "--isolated" in args:
        isolated = True

    return isolated

if __name__=="__main__":
    package='wheel'
    #print (runpip_using_subprocess('show {}'.format(package)))

    '''cmd_name, cmd_args = parseopts(['show','--log','hello.txt',package])
    print("Command name : {}".format(cmd_name))
    print(cmd_args)
    hh = search_packages_info(cmd_args)
    for x in hh:
        print (x)
    print (dir(hh))
    stat, out, err = runpip('show %s'%package)
    print('stat: {}\n\n{}\nerr: {}'.format(stat, out, err))
    '''
    args = ['show',package]

    try:
        cmd_name, cmd_args = parseopts(args)
    except PipError as exc:
        sys.stderr.write("ERROR: %s" % exc)
        sys.stderr.write(os.linesep)
        sys.exit(1)

    command = commands_dict[cmd_name]()
    command.main(cmd_args)
