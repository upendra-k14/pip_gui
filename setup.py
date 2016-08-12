from setuptools import setup, find_packages

setup(
    name='pip_tkinter',
    version='0.0.1',
    description='A Tk GUI for pip',
    author='Upendra Kumar',
    author_email='upendra.k14@iiits.in',
    packages=find_packages(exclude=['test','test.*','_vendor','_vendor.*']),
    install_requires=['pip>=8.1.2',],
    entry_points={
        'gui_scripts': [
            'pip_tkinter = pip_tkinter.__main__:main'
        ]
    },
    package_data={'pip_tkinter': ['resources/*',]},
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ]
)

#package_data={'pip_tkinter':'resources/*'},
