#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='utilsDAWS',
    version='2.13.8',
    description='This package has shared classes and functions for data analysis and web scraping purposes.',
    author='Yu-Chang Ho (Andy)',
    author_email='ycaho@ucdavis.edu',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=open('README.md').read(),
    install_requires=[
        'pathlib',
        'requests',
        'pandas',
        'numpy',
        'googletrans'
    ],
    # license='LICENSE.txt',
)

'''
To Install:
$ pip install git+https://github.com/hippoandy/Utils_Data_Analysis_Python
'''