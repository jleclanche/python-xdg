#!/usr/bin/env python
"""
Tests for python-mime

>>> import os
>>> from xdg.mime import MimeType
>>> mime = MimeType.fromName("foo.txt")
>>> mime.name()
'text/plain'
>>> mime.comment()
'plain text document'
>>> mime.comment(lang="fr")
'document texte brut'
>>> mime.type()
'text'
>>> mime.subtype()
'plain'
>>> mime.genericMime()
<MimeType: text/x-generic>
>>> mime.genericMime().name()
'text/x-generic'
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
>>> MimeType(MimeType("inode/directory")).name()
'inode/directory'
>>> MimeType("application/x-bzip").extensions()
['.bz2', '.bz']
>>> MimeType("inode/directory").name() is MimeType(MimeType("inode/directory")).name()
True
>>> MimeType("text/x-lua").comment()
'Lua script'
>>> MimeType("application/x-does-not-exist")
<MimeType: application/x-does-not-exist>
>>> MimeType("application/x-does-not-exist").comment()
>>> MimeType.fromName("foo.mkv").name()
'video/x-matroska'
>>> MimeType("application/javascript").aliases()
[<MimeType: application/x-javascript>, <MimeType: text/javascript>]
>>> MimeType("text/xml").aliasOf()
<MimeType: application/xml>
>>> MimeType("text/x-python").subClassOf()
[<MimeType: application/x-executable>, <MimeType: text/plain>]
>>> MimeType("application/zip").genericIcon()
'package-x-generic'
>>> MimeType("application/zip").icon()
'application-zip'
>>> MimeType("text/plain").genericIcon()
'text-x-generic'
>>> MimeType("text/x-python").isInstance("text/x-python")
True
>>> MimeType("text/x-python").isInstance("text/plain")
True
>>> MimeType("text/x-python").isInstance("application/x-executable")
True
>>> MimeType("text/plain").isInstance("application/zip")
False
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
