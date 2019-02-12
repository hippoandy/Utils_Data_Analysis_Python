#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='utils_da_py',
    version='0.0.1',
    description='This package has shared classes and functions for data analysis and scraping purposes.',
    author='Yu-Chang Ho (Andy)',
    author_email='ycaho@ucdavis.edu',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=open('README.md').read()
    # license='LICENSE.txt',
)