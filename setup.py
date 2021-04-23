# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in proceso/__init__.py
from proceso import __version__ as version

setup(
	name='proceso',
	version=version,
	description='A customization app for Proceso',
	author='Lewin Villar',
	author_email='lewinvillar@tzcode.tech',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
