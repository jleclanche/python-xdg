"""
Ini file format
Base for .desktop file format
"""

try:
	from configparser import RawConfigParser, NoOptionError, NoSectionError
except ImportError:
	from ConfigParser import RawConfigParser, NoOptionError, NoSectionError


class IniFile(RawConfigParser):
	def read_merged(self, filenames, encoding=None):
		cfg = []
		for filename in filenames:
			_cfg = RawConfigParser()
			_cfg.read(filename)
			cfg.append(_cfg)

		for _cfg in cfg:
			for section in _cfg.sections():
				if not self.has_section(section):
					self.add_section(section)

				for option in _cfg.options(section):
					value = _cfg.get(section, option)
					if ";" in value:
						current = self.getdefault(section, option, "")
						if ";" in current:
							val = []
							for v in value.split(";"):
								if v and v not in val:
									val.append(v)

							for v in self.getlist(section, option):
								if v and v not in val:
									val.append(v)

							self.set(section, option, ";".join(val) + ";")
							continue
					self.set(section, option, value)

	def getdefault(self, section, option, default=None):
		try:
			return self.get(section, option)
		except (NoOptionError, NoSectionError):
			return default

	def getlist(self, section, option, default=None):
		try:
			ret = self.get(section, option)
		except (NoOptionError, NoSectionError):
			return default

		if ";" not in ret:
			return [ret]
		return [x for x in ret.split(";") if x]
