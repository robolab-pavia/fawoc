#!/usr/bin/env python

from setuptools import setup

__version__ = ''

exec(open('fawoc/version.py').read())

setup(
    name='fawoc',
    version=__version__
)
