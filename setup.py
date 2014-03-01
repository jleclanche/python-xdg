#!/usr/bin/env python

import os.path
from distutils.core import setup

#README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()

CLASSIFIERS = [
	"Development Status :: 3 - Alpha",
	"Intended Audience :: Developers",
	"License :: OSI Approved :: MIT License",
	"Programming Language :: Python",
]

import xdg

setup(
	name = "python-xdg",
	packages = ["xdg"],
	author = xdg.__author__,
	author_email = xdg.__email__,
	classifiers = CLASSIFIERS,
	description = "Implementation of various Freedesktop xdg specs",
	download_url = "https://github.com/jleclanche/python-xdg/tarball/master",
	#long_description = README,
	url = "https://github.com/jleclanche/python-xdg",
	version = xdg.__version__,
)
