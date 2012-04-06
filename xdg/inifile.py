"""
Ini file format
Base for .desktop file format
"""

try:
	from configparser import RawConfigParser
except ImportError:
	from ConfigParser import RawConfigParser


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
