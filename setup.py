# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from distutils.core import Command
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='snes2asm',
    version='0.0.3',
    description='Disassembles SNES cartridges into practical projects',
    long_description=long_description,
    author="Nathan Cassano",
    license="Apache 2",
    packages=find_packages(exclude=['snes2asm/tests']),
    include_package_data=True,
    package_data = {'snes2asm':['template/*']},
    scripts=['bin/snes2asm','bin/bmp2chr'],
    install_requires=['PyYAML'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Programming Language :: Assembly',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Assemblers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Embedded Systems',
    ],
    url='https://github.com/nathancassano/snes2asm',
)
