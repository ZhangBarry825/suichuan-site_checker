#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

try:
    README = open('README.md').read()
except Exception:
    README = ""
VERSION = "0.0.1"

requirments = ["cpyder", "pandas"]

setup(
    name='site_checker',
    version=VERSION,
    description='site_checker',
    url="http://github.com/spenly/site_checker",
    long_description=README,
    author='zhongxian.jia',
    author_email='i@spenly.com',
    packages=find_packages(),
    install_requires=requirments,
    extras_require={
        # "extra": ["extra_requirments"],
    },
    entry_points={
        'console_scripts': [
            'crawl=site_checker.commands:main'
        ]
    },
)