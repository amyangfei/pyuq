#!/usr/bin/env python
# coding: utf-8

import os
from setuptools import setup, find_packages

from uq import __version__

requirements = [
    'python-etcd >= 0.4.3',
    'pymemcache >= 1.3.5',
    'redis >= 2.10.5',
]

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    name='uq',
    version=__version__,
    description='Python library for uq cluster',
    long_description=long_description,
    url='http://github.com/amyangfei/pyuq',
    author='Yang Fei',
    author_email='amyangfei@gmail.com',
    maintainer='Yang Fei',
    maintainer_email='amyangfei@gmail.com',
    keywords=['Uq', 'message queue'],
    license='MIT',
    packages=find_packages(),
    install_requires=requirements,
)
