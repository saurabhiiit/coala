#!/usr/bin/env python3

import locale
import sys
from os import getenv
from subprocess import call

# Start ignoring PyImportSortBear as imports below may yield syntax errors
from coalib import assert_supported_version

assert_supported_version()
# Stop ignoring

import setuptools.command.build_py
from coalib.misc import Constants
from coalib.misc.BuildManPage import BuildManPage
from coalib.output.dbus.BuildDbusService import BuildDbusService
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

try:
    locale.getlocale()
except (ValueError, UnicodeError):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class BuildPyCommand(setuptools.command.build_py.build_py):

    def run(self):
        self.run_command('build_manpage')
        self.run_command('build_dbus')
        setuptools.command.build_py.build_py.run(self)


class PyTestCommand(TestCommand):

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main([])
        sys.exit(errno)


class BuildDocsCommand(setuptools.command.build_py.build_py):
    apidoc_command = ('sphinx-apidoc', '-f', '-o', 'docs/API/',
                      'coalib')
    doc_command = ('make', '-C', 'docs', 'html')

    def run(self):
        call(self.apidoc_command)
        call(self.doc_command)


# Generate API documentation only if we are running on readthedocs.org
on_rtd = getenv('READTHEDOCS', None) != None
if on_rtd:
    call(BuildDocsCommand.apidoc_command)

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

with open('test-requirements.txt') as requirements:
    test_required = requirements.read().splitlines()


if __name__ == "__main__":
    data_files = [('.', ['coala.1']), ('.', [Constants.BUS_NAME + '.service'])]

    setup(name='coala',
          version=Constants.VERSION,
          description='Code Analysis Application (coala)',
          author="The coala developers",
          maintainer="Lasse Schuirmann, Fabian Neuschmidt, Mischa Kr\xfcger"
                      if not on_rtd else "L.S., F.N., M.K.",
          maintainer_email=('lasse.schuirmann@gmail.com, '
                            'fabian@neuschmidt.de, '
                            'makman@alice.de'),
          url='http://coala.rtfd.org/',
          platforms='any',
          packages=find_packages(exclude=["build.*", "tests", "tests.*"]),
          install_requires=required,
          tests_require=test_required,
          package_data={'coalib': ['default_coafile', "VERSION",
                                   'bearlib/languages/definitions/*.coalang']},
          license="AGPL-3.0",
          data_files=data_files,
          long_description="coala is a simple COde AnaLysis Application. Its "
                           "goal is to make static code analysis easy while "
                           "remaining completely modular and therefore "
                           "extendable and language independent. Code analysis"
                           " happens in python scripts while coala manages "
                           "these, tries to provide helpful libraries and "
                           "provides a user interface. Please visit "
                           "http://coala.rtfd.org/ for more information or "
                           "our development repository on "
                           "https://github.com/coala-analyzer/coala/.",
          entry_points={
              "console_scripts": [
                  "coala = coalib.coala:main",
                  "coala-ci = coalib.coala_ci:main",
                  "coala-dbus = coalib.coala_dbus:main",
                  "coala-json = coalib.coala_json:main",
                  "coala-format = coalib.coala_format:main",
                  "coala-delete-orig = coalib.coala_delete_orig:main"]},
          # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=[
              'Development Status :: 4 - Beta',

              'Environment :: Console',
              'Environment :: MacOS X',
              'Environment :: Win32 (MS Windows)',
              'Environment :: X11 Applications :: Gnome',

              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',

              'License :: OSI Approved :: GNU Affero General Public License '
              'v3 or later (AGPLv3+)',

              'Operating System :: OS Independent',

              'Programming Language :: Python :: Implementation :: CPython',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3 :: Only',

              'Topic :: Scientific/Engineering :: Information Analysis',
              'Topic :: Software Development :: Quality Assurance',
              'Topic :: Text Processing :: Linguistic'],
          cmdclass={'build_manpage': BuildManPage,
                    'build_dbus': BuildDbusService,
                    'build_py': BuildPyCommand,
                    'docs': BuildDocsCommand,
                    'test': PyTestCommand})
