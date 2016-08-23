Manage Installed Packages Page
==============================

It provided options for dealing with already installed packages. Most common
ways in which user wants to deal with already installed packages is ei:ther to
uninstall or update it. Therefore, currently two options are implemented:

a) Update Installed Packages Page
b) Uninstall Package Page
c) Freeze Requirements Page

The page layout is similar to Install Page layout.

Update Installed Packages Page
------------------------------

.. image:: updatepage.png

Similar to InstallPage.InstallFromPyPI page.

Uninstall Package Page
----------------------

The page layout is very similar to Update Installed Packages Page except the
treeview has only two headers : package name and installed version.

Freeze Requirements Page
------------------------

The page lists all installed packages where user can select multiple packages
and generate a requirement file out of the selected packages. It is needed
so that if user has to move everything to another system, then the user can
generate a requirements file and again install it using requirements file.


.. toctree::
    :maxdepth: 2
