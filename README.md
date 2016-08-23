# pip_tkinter
A GUI for "pip"

# GSoC Related Links
* `pip_tkinter` repository : https://github.com/upendra-k14/pip_gui
* Pythonlibs Crawler :
    - Repo link : https://github.com/upendra-k14/pythonlibs_modules/issues
    - Deployment link ( a cron app ) : http://pythonlibscron-piptrial.rhcloud.com/
* GSoC Blog : http://www.scorython.wordpress.com/

# Documentation

https://upendra-k14.github.io/pip_gui/

# Installation

From Source
-----------

1. Ensure that you have `python3.3+` and `python3-pip` with latest version(8.1.2+)
2. Clone the repo from https://github.com/upendra-k14/pip_gui.git. Otherwise run the following command : `git clone https://github.com/upendra-k14/pip_gui.git <download_location>`
3. Navigate to `<download_location>/<pip_gui>/` folder
5. From inside the pip_gui folder run : `python3 -m pip_tkinter`
6. To install and run using entry point: `sudo python3 setup.py install`
`

# Motivation
This project is intended to provide a GUI version for "pip". It is currently a command line based package manager used to install and manage software packages written in Python. But, many users are not familiar with the command line and thus find difficulties using and accessing PIP. People who still don’t have enough exposure to command line tools(specially in case of Windows) find installing packages using PIP very cumbersome. Therefore, the main motivation behind this project is to make various functionalities provided by PIP accessible to Windows/LINUX/Mac based users through a tkinter based GUI interface which could be further integrated with IDLE. As a whole, it would help beginners to focus more on learning and using new Python packages rather than getting in unavoidable trouble of configuring various paths and configurations in order to install new Python Packages from PyPI.

The product developed will be a GUI for pip to make various functionalities of pip ( a command line tool for installing Python packages) easily accessible to users. Main motivation behind the need for GUI version of Python Package Manager is :

* Make various functionalities provided by PIP easily accessible to Windows/LINUX/Mac based users
* Help people to focus only on fulfilling the task of installing Python packages rather than getting in unavoidable trouble of configuring various paths, versions and configurations

# Target Users

* Windows Users ( who have difficulty using command prompt )
* Novice Python users ( on MacOS or Linux )

# Targeted Tasks

* Search, select version and install package
* Check for new updates and install them
* Uninstall a package
* Support different installation methods :
  * Requirements.txt files
  * .whl files
  * From local archives
  * From Pythonlibs

# Design Principles

The design of the pip gui should adhere to these principles :

* User goals and preferences should be completed by through the application
* Use cases should be clearly identified
* UI should be self explanatory
* UI should be task centric, not feature centric
* The UI elements should be consistent, not over-creative

# Simple User Model

A very simple navigation based minimalistic GUI is intended to be designed. The aim of this user work flow is to help user to easily navigate through proper options in order to complete their tasks easily.

![Unable to load image](https://github.com/upendra-k14/pip_gui/blob/master/UserWorkFlow.png)

# TODO list

* fix bugs
* improve search functionality
* decide whether to implement venv feature

# Bug Tracker

* http://bugs.python.org/issue27051
