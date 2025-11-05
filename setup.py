#!/usr/bin/env python3
"""
Setup script for wincountdown
"""

from setuptools import setup
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='wincountdown',
    version='1.0.0',
    description='A countdown timer and clock for Linux with large ASCII art display',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='stropitor',
    url='https://github.com/Stropitor/wincountdown-linux',
    license='GPL-3.0',
    py_modules=['wincountdown'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'wincountdown=wincountdown:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Utilities',
    ],
    keywords='countdown timer clock terminal cli ascii',
)
