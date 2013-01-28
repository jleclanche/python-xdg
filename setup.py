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

setup(
	name = "python-xdg",
	packages = ["xdg"],
	author = "Jerome Leclanche",
	author_email = "adys.wh@gmail.com",
	classifiers = CLASSIFIERS,
	description = "Implementation of various Freedesktop xdg specs",
	download_url = "https://github.com/Adys/python-xdg/tarball/master",
	#long_description = README,
	url = "http://github.com/Adys/python-xdg",
	version = "0.8",
)
