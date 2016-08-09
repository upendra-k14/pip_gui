from __future__ import absolute_import

import os
import re
import sys
import platform

#Resource and logging dir for pip_tkinter
RESOURCE_DIR = '.pip_tkinter'

def get_build_platform():
    """
    Get OS of the device
    """
    return platform.system()

def find_bit_of_python():
    """
    Find whether system is running in 32 bit or 64 bit mode
    """
    if sys.maxsize > 2**32:
        return '64bit'
    else:
        return '32bit'

def get_python_distributions_in_linux():
    """
    Return path of Python executables in Linux
    Related information : PEP 3149 and PEP 3147
    For example, Python3.4 may have multiple entries in /usr/bin :

    1. python3.4
    2. python3.4m
    3. python3.4d
    4. python3.4b
    5. python3

    Although it is not clear whether they are symlinked, all of them used the
    same executable when they were tried to be executed
    """
    executable_paths = []
    pattern = re.compile('python\d\.\d$')
    for executable in os.listdir('/usr/bin/'):
        if re.match(pattern, executable):
            executable_paths.append('/usr/bin/{}'.format(executable))

    return executable_paths


def get_python_distributions_in_macos():
    """
    Return path of Python executables in Mac OS
    Common install locations in python :

    1. /usr/bin/
    2. /usr/local/bin/
    3. /opt/local/bin (Homebrew installation)
    """

    executable_paths = []
    pattern = re.compile('python\d\.\d$')

    python_install_dirs = [
        '/usr/bin/',
        '/usr/local/bin/',
        '/opt/local/bin/']

    for install_dir in python_install_dirs:
        for executable in os.listdir(install_dir):
            if re.match(pattern, executable):
                executable_paths.append('{}{}'.format(install_dir, executable))

    return executable_paths

def get_python_distributions_in_windows():
    """
    Return path of Python executables in Windows. Install locations can be
    found from windows registry.
    Possible registry keys :

    1. HKEY_CURRENT_USER\Software\Python\<Company>\<Tag>\<InstallPath>
    2. HKEY_LOCAL_MACHINE\Software\Python\<Company>\<Tag>\<InstallPath>
    3. HKEY_LOCAL_MACHINE\Wow6432Node\Python\<Company>\<Tag>\<InstallPath>

    """
    pass


if __name__ == "__main__":

    print (get_python_distributions_in_linux())
    print (find_bit_of_python())
