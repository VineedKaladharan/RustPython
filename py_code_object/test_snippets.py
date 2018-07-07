
# This is a python unittest class automatically populating with all tests
# in the tests folder.


import os
import unittest
import glob
import logging
import subprocess
import contextlib

import compile_code


logger = logging.getLogger('tests')
TEST_DIR = os.path.abspath(os.path.join('..', 'tests'))
CPYTHON_RUNNER_DIR = os.path.abspath(os.path.join('..', 'vm', 'RustPython'))


@contextlib.contextmanager
def pushd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


def perform_test(filename):
    logger.info('Running %s', filename)
    # Step1: Create bytecode file:
    bytecode_filename = filename + '.bytecode'
    with open(bytecode_filename, 'w') as f:
        compile_code.compile_to_bytecode(filename, out_file=f)

    # Step2: run cpython bytecode:
    with pushd(CPYTHON_RUNNER_DIR):
        subprocess.check_call(['cargo', 'run', bytecode_filename])


def create_test_function(cls, filename):
    """ Create a test function for a single snippet """
    core_test_directory, snippet_filename = os.path.split(filename)
    test_function_name = 'test_' \
        + os.path.splitext(snippet_filename)[0] \
        .replace('.', '_').replace('-', '_')

    def test_function(self):
        perform_test(filename)

    if hasattr(cls, test_function_name):
        raise ValueError('Duplicate test case {}'.format(test_function_name))
    setattr(cls, test_function_name, test_function)


def populate(cls):
    """ Decorator function which can populate a unittest.TestCase class """
    for filename in get_test_files():
        create_test_function(cls, filename)
    return cls


def get_test_files():
    """ Retrieve test files """
    for filename in sorted(glob.iglob(os.path.join(
            TEST_DIR, '*.py'))):
        yield os.path.abspath(filename)


@populate
class SampleTestCase(unittest.TestCase):
    pass
