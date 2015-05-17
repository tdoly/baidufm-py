#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from baidufm import version, __project__, __license__


def read(filename):
    ret = ''
    if os.path.exists(filename):
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            ret = f.read()
    return ret


meta = dict(
    name=__project__,
    version=version,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.md'),
    platforms=('Any'),
    author='tdoly',
    author_email='hi@tdoly.com',
    url='https://github.com/tdoly/baidufm-py',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'rsa',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'baidufm = baidufm.baidufm:main',
        ]
    },
)


if __name__ == "__main__":
    setup(**meta)