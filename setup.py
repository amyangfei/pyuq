#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

exec(open('uq/version.py').read())

requirements = [
    'python-etcd >= 0.4.3',
    'python-memcached >= 1.57',
    'redis >= 2.10.5',
]

setup(
    name='uq',
    version=version,
    description='redis library for uq cluster',
    packages=find_packages(),
    install_requires=requirements,
)
