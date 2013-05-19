#!/usr/lib/env python
# -*- coding: utf-8 -*-

import os
import tempfile
from app.lib.publisher import Publisher


class FileSystemAdapter(Publisher):

    def tempfile(self, file, ext):
        """Creates a temporary file with extension ``ext`` and dump ``file``
        into it.

        On success the method will emit a 'tempfile_created' message followed by
        the name of temporary file created.
        """
        suffix = '.' + ext
        with tempfile.NamedTemporaryFile("w+b", suffix=suffix, delete=False) as tmp:
            tmp.write(file.read())
            self.publish('tempfile_created', tmp.name)

    def rename(self, *mappings):
        """Applies all the _renaming_ transformations defined into ``mappings``.

        ``mappings`` is a collection of tuples, each defining a rename
        operation:  tuples are made by two elements, the first containing the
        file to be renamed and the second containing the destination file.

        On success the method will emit a 'files_renamed' message containing the
        the collection of _renaming_ transformations (i.e. ``mappings``).
        """
        map(lambda s, d: os.rename(s, d), mappings)
        self.publish('files_renamed', *mappings)
