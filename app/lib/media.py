#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from app.lib.publisher import Publisher


class MediaContentMapper(Publisher):
    """Generates the media folder destination path associated with the uploaded
    avatar (actually parked in the temporary folder).

    >>> class Subscriber(object):
    ...   def mediapaths_ready(self, *mappings):
    ...     for s, d in mappings:
    ...       message = '%(source)s => %(destination)s'
    ...       message = message % dict(source=s, destination=d)
    ...       print message
    >>> this = MediaContentMapper()
    >>> this.add_subscriber(Subscriber())

    >>> this.perform('/var/web/app/media', '/tmp/12847/avatar.png')
    /tmp/12847/avatar.png => /var/web/app/media/avatar.png

    >>> paths = ['tmp/12847/avatar.png',  'tmp/12847/avatar_128x128.png']
    >>> this.perform('/var/web/app/media', *paths)
    tmp/12847/avatar.png => /var/web/app/media/avatar.png
    tmp/12847/avatar_128x128.png => /var/web/app/media/avatar_128x128.png
    """

    def perform(self, destdir, *tmppaths):
        self.publish('mediapaths_ready',
                     *zip(tmppaths, map(lambda n: os.path.join(destdir, n),
                                        map(os.path.basename, tmppaths))))
