#!/usr/bin/python3

from setuptools import setup

setup(
    name='wayround_org_socketserver',
    version='0.1.3',
    description='socket server realisation',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_socketserver',
    packages=[
        'wayround_org.socketserver'
        ],
    install_requires=[
        'wayround_org_utils'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        ]
    )
