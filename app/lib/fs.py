#!/usr/lib/env python
# -*- coding: utf-8 -*-

import os
import tempfile
from app.lib.publisher import Publisher


class FileSystemAdapter(Publisher):

    def tempfile(self, file, ext):
        """Creates a temporary file with extension ``ext`` and dump ``file``
        into it.

        On success, the writer will emit a 'tempfile_created' message followed
        by the name of temporary file created.
        """
        suffix = '.' + ext
        with tempfile.NamedTemporaryFile("w+b", suffix=suffix, delete=False) as tmp:
            tmp.write(file.read())
            self.publish('tempfile_created', tmp.name)

    def rename(self, source, destination):
        """Rename ``source`` into ``destination``.

        If ``destination`` is a directory, this method will throw an
        ``OSError``."""
        os.rename(source, destination)
