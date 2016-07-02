# coding=utf-8
from os.path import dirname

def load_tests(loader, standard_tests, test_pattern):
    """
    Load tests
    """
    
    current_directory = dirname(__file__)
    root_directory = dirname(dirname(current_directory))
    package_tests = loader.discover(
        start_dir=current_directory,
        pattern='test_*.py',
        top_level_dir=root_directory)
    standard_tests.addTests(package_tests)

    return standard_tests
