#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import errno

from config import EXPORT_DIR


def mkdir_p(path):
    """Taken from stackoverflow:
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python/600612#600612
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class ExportManager(object):

    def __init__(self, wdir):
        self._wdir = wdir

    def add(self, user_id, filename, iterable):
        relativedir = os.path.join(EXPORT_DIR, user_id)
        relativepath = os.path.join(relativedir, filename)
        absolutepath = os.path.join(self._wdir, relativepath)

        mkdir_p(relativedir)
        with open(absolutepath, 'wb') as f:
            for item in iterable:
                f.write(repr(item))

        return os.path.join('/', relativepath)
