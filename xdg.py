"""
Shared definitions and helper functions for xdg
"""

import os
try:
	from configparser import RawConfigParser
except ImportError:
	from ConfigParser import RawConfigParser

from .basedir import *

FREEDESKTOP_NS = "http://www.freedesktop.org/standards/shared-mime-info"




def getFiles(name):
	ret = []
	for dir in XDG_DATA_DIRS:
		path = os.path.join(dir, name)
		if os.path.exists(path):
			ret.append(path)
	return ret

def getDesktopFilePath(name):
	ret = None
	for path in getFiles(os.path.join("applications", name)):
		if os.path.exists(path):
			ret = path

	return ret

def updateDesktopDatabase(base):
	from subprocess import Popen
	Popen(["update-desktop-database", base])

def updateMimeDatabase(base):
	from subprocess import Popen
	Popen(["update-mime-database", base])

class IniFile(object):
	def __init__(self):
		self.keys = {}

	def __repr__(self):
		return self.keys.__repr__()

	def get(self, key, default=None):
		return self.keys.get(key, default)

	def parse(self, path):
		with open(path, "r") as file:
			self.cfg = RawConfigParser()
			self.cfg.readfp(file)
			self.parseKeys()
