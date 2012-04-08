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
		self.sections = {}

	def __repr__(self):
		return self.sections.__repr__()

	def get(self, section, key, default=None):
		return self.sections[section].get(key, default)

	def parse(self, path):
		with open(path, "r", encoding="utf-8") as file:
			self.cfg = RawConfigParser()
			self.cfg.readfp(file)
			self.parseKeys()
