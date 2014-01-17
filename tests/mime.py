#!/usr/bin/env python
"""
MIME type tests for python-xdg

>>> import os
>>> from xdg.mime import MimeType
>>> mime = MimeType.fromName("foo.txt")
>>> mime.name()
'text/plain'
>>> mime.type()
'text'
>>> mime.subtype()
'plain'
>>> mime.genericMime()
<MimeType: text/x-generic>
>>> mime.genericMime().name()
'text/x-generic'
>>> mime = MimeType("text/plain; charset=UTF-8")
>>> mime.name()
'text/plain'
>>> mime.type()
'text'
>>> mime.subtype()
'plain'
>>> MimeType.fromName("foo.TXT").name()
'text/plain'
>>> MimeType.fromName("foo.C").name()
'text/x-c++src'
>>> MimeType.fromName("foo.c").name()
'text/x-csrc'
>>> print(MimeType.fromName("no-such-file"))
None
>>> MimeType.fromInode("/dev/sda").name()
'inode/blockdevice'
>>> MimeType.fromInode("/dev/null").name()
'inode/chardevice'
>>> MimeType.fromInode("/").name()
'inode/mount-point'
>>> MimeType.fromInode(".").name()
'inode/directory'
>>> print(MimeType.fromInode("no-such-file"))
None
>>> MimeType(MimeType("inode/directory")).name()
'inode/directory'

# Localized attributes
>>> mime.comment()
'plain text document'
>>> mime.comment(lang="en") == mime.comment()
True
>>> mime.comment(lang="fr")
'document texte brut'
>>> MimeType("application/xml").comment()
'XML document'
>>> MimeType("application/xml").acronym()
'XML'
>>> MimeType("application/xml").expandedAcronym()
'eXtensible Markup Language'

# Non-existant mime types
>>> MimeType("application/x-does-not-exist")
<MimeType: application/x-does-not-exist>
>>> MimeType("application/x-does-not-exist").comment()

# Aliases / subclasses
>>> MimeType("application/javascript").aliases()
[<MimeType: application/x-javascript>, <MimeType: text/javascript>]
>>> MimeType("text/xml").aliasOf()
<MimeType: application/xml>
>>> MimeType("text/x-python").subClassOf()
[<MimeType: application/x-executable>, <MimeType: text/plain>]
>>> MimeType("text/x-python").isInstance("text/x-python")
True
>>> MimeType("text/x-python").isInstance("text/plain")
True
>>> MimeType("text/x-python").isInstance("application/x-executable")
True
>>> MimeType("text/plain").isInstance("application/zip")
False
>>> MimeType("application/vnd.android.package-archive").subClassOf()
[<MimeType: application/x-java-archive>]
>>> MimeType("application/vnd.android.package-archive").isInstance("application/x-java-archive")
True
>>> MimeType("application/vnd.android.package-archive").isInstance("application/zip")
True

# icons / extensions
>>> MimeType("application/zip").genericIcon()
'package-x-generic'
>>> MimeType("application/zip").icon()
'application-zip'
>>> MimeType("text/plain").genericIcon()
'text-x-generic'
>>> MimeType("application/x-bzip").extensions()
['.bz', '.bz2']
>>> MimeType("application/x-java-archive").extensions()
['.jar']

# test for globs weights
>>> MimeType.fromName("foo.png")
<MimeType: image/png>

# from* classmethods
>>> MimeType.fromName("foo.TXT").name()
'text/plain'
>>> MimeType.fromName("foo.C").name()
'text/x-c++src'
>>> MimeType.fromName("foo.c").name()
'text/x-csrc'
>>> MimeType.fromInode("/dev/sda").name()
'inode/blockdevice'
>>> MimeType.fromInode("/dev/null").name()
'inode/chardevice'
>>> MimeType.fromInode("/").name()
'inode/mount-point'
>>> MimeType.fromInode(".").name()
'inode/directory'
>>> MimeType.fromScheme("http://example.com").name()
'x-scheme-handler/http'
>>> MimeType.fromScheme("ftp://example.com").name()
'x-scheme-handler/ftp'
>>> MimeType.fromScheme("mailto:user@example.com").name()
'x-scheme-handler/mailto'
>>> MimeType.fromScheme("file:///").name()
'x-scheme-handler/file'
>>> f = open("test.tmp", "w")
>>> MimeType.fromContent(f.name).name()
'application/x-zerosize'
>>> _ = f.write("foo")
>>> f.close()
>>> MimeType.fromContent(f.name).name()
'text/plain'
>>> os.remove(f.name)
"""


if __name__ == "__main__":
	import doctest
	doctest.testmod()
