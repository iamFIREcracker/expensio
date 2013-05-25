#!/usr/lib/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import uuid
from app.lib.pubsub import Publisher


class TempFileCreator(Publisher):
    """
    >>> from mock import Mock, MagicMock
    >>> class Subscriber(object):
    ...   def tempfile_created(self, tmppath):
    ...     print 'Created %(file)s' % dict(file=tmppath)
    ...   def tempfile_error(self, exception):
    ...     print 'Error: %(error)s' % dict(error=exception)
    >>> this = TempFileCreator()
    >>> this.add_subscriber(Subscriber())

    >>> fsa = Mock(tempfile=Mock(side_effect=ValueError('Oh noes!')))
    >>> this.perform(fsa, None, 'avatar.png')
    Traceback (most recent call last):
      ...
    ValueError: Oh noes!

    >>> fsa = Mock(tempfile=Mock(side_effect=OSError('Oh noes!')))
    >>> this.perform(fsa, None, 'avatar.png')
    Error: Oh noes!

    >>> fsa = Mock(tempfile=MagicMock(return_value='/tmp/document.pdf'))
    >>> this.perform(fsa, None, 'document.pdf')
    Created /tmp/document.pdf
    """
    
    def perform(self, fsadapter, file, suffix):
        """Creates a temporary file with the given suffix and dump ``file`` into
        it.

        On error the method emits a 'tempfile_error' followed by the error
        cause.  On success the method will emit a 'tempfile_created' message
        followed by the name of temporary file created.
        """
        try:
            tmppath = fsadapter.tempfile(file, suffix)
            self.publish('tempfile_created', tmppath)
        except OSError as e:
            self.publish('tempfile_error', e)


class BulkRenamer(Publisher):
    """
    >>> class Subscriber(object):
    ...   def files_renamed(self, *mappings):
    ...     for (s, d) in mappings:
    ...       print 'Renamed %(source)s => %(dest)s' % dict(source=s, dest=d)
    >>> this = BulkRenamer()
    >>> this.add_subscriber(Subscriber())

    >>> this.perform(NullFileSystemAdapter('/tmp'),
    ...              ('/tmp/foo.png', '/var/foo.png'))
    Renamed /tmp/foo.png => /var/foo.png
    """

    def perform(self, fsadapter, *mappings):
        """Applies all the _renaming_ transformations defined into ``mappings``.

        ``mappings`` is a collection of tuples, each defining a rename
        operation:  tuples are made by two elements, the first containing the
        file to be renamed and the second containing the destination file.

        On success the method will emit a 'files_renamed' message containing the
        the collection of _renaming_ transformations (i.e. ``mappings``).
        """
        mappings = fsadapter.rename(*mappings)
        self.publish('files_renamed', *mappings)


class FileSystemAdapter(object):

    def tempfile(self, file, suffix):
        """Creates a temporary file with the given suffix and dump ``file`` into
        it.

        On success the method will emit a 'tempfile_created' message followed by
        the name of temporary file created.
        """
        suffix = '%(uuid)s_%(suffix)s' % dict(uuid=uuid.uuid4(), suffix=suffix)
        with tempfile.NamedTemporaryFile("w+b", suffix=suffix, delete=False) as tmp:
            tmp.write(file.read())
            return tmp.name

    def rename(self, *mappings):
        """Applies all the _renaming_ transformations defined into ``mappings``.

        ``mappings`` is a collection of tuples, each defining a rename
        operation:  tuples are made by two elements, the first containing the
        file to be renamed and the second containing the destination file.

        On success the method will emit a 'files_renamed' message containing the
        the collection of _renaming_ transformations (i.e. ``mappings``).
        """
        map(lambda (s, d): os.rename(s, d), mappings)
        return mappings


class NullFileSystemAdapter(object):
    """FS adapter skipping all the interactions with the disk."""

    def __init__(self, basedir):
        self.basedir = basedir

    def tempfile(self, file, suffix):
        return os.path.join(self.basedir, suffix)

    def rename(self, *mappings):
        return mappings
