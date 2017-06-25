#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='grill-checkin-control',
    version='0.1.0',
    packages=find_packages(exclude=("*.tests", "*.tests.*", "tests.*", "tests", "*.docs", "*.docs.*", "docs.*", "docs")),
    description='Checkin data to any filesystem.',
    author='Christian Lopez Barron',
    author_email='chris.gfz@gmail.com',
    url='https://github.com/thegrill/checkin-control',
    download_url='https://github.com/thegrill/checkin-control/releases/tag/0.1.0',
    classifiers=['Programming Language :: Python :: 3.6'],
    extras_require={'docs': ['sphinx_autodoc_typehints']},
    install_requires=['fs'],
    namespace_packages=['grill']
)
