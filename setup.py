# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 16:23:15 2016

@author: alex
"""
from setuptools import setup
from setuptools.command.install import install
from subprocess import call
import os
from distutils.spawn import find_executable
import time

VERSION = '0.1.0'
'''
class CustomInstall(install):
    def run(self):
        install.run(self)
        time.sleep(5)
        test_for_webdriver = find_executable('chromedriver')
        if not test_for_webdriver:
            call(['pip', 'install', 'chromedriver_installer', '--install-option=chromedriver-version=2.10'])
'''
def write_version_py(filename=None):
    """
    This constructs a version file for the project
    """
    doc = "\"\"\"\nThis is a VERSION file and should NOT be manually altered\n\"\"\""
    doc += "\nversion = '%s'" % VERSION

    if not filename:
        filename = os.path.join(os.path.dirname(__file__), 'scrapedyno', 'version.py')

    fl = open(filename, 'w')
    try:
        fl.write(doc)
    finally:
        fl.close()

write_version_py()  # This is a file used to control the qe.__version__ attribute



DESCRIPTION = "scrapedyno is a package to support data retrieval from dynamic webpage databases that do not use dynamic URLs"       

LICENSE = 'BSD'

CLASSIFIERS = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP '
       ]

setup(name='scrapedyno',
      packages=[
      'scrapedyno',
      ],
      install_requires = [
      'scrapely==0.12.0',
      'selenium',
      'bs4',
      ],
      version=VERSION,
      description=DESCRIPTION,
      long_description=open('README.txt').read(),
      license=LICENSE,
      classifiers=CLASSIFIERS,
      author='Alex B. Kaufman',
      author_email='akaufman10@gmail.com',
      url='https://github.com/akaufman10/scrapedyno',  # URL to the repo
      keywords=['scraping', 'data'],
      )