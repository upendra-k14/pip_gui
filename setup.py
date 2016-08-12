from setuptools import setup, find_packages

setup(
    name='pip_tkinter',
    version='0.0.1',
    description='A Tk GUI for pip',
    author='Upendra Kumar',
    author_email='upendra.k14@iiits.in',
    packages=find_packages(exclude=['test','test.*','_vendor','_vendor.*']),
    package_data={'pip_tkinter':'resources/*'},
)
