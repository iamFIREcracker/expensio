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
    >>> this = MediaContentMapper('/var/web/app/media')
    >>> this.add_subscriber(Subscriber())

    >>> this.perform('/tmp/12847/avatar.png')
    /tmp/12847/avatar.png => /var/web/app/media/avatar.png

    >>> this.perform('tmp/12847/avatar.png',  'tmp/12847/avatar_128x128.png')
    tmp/12847/avatar.png => /var/web/app/media/avatar.png
    tmp/12847/avatar_128x128.png => /var/web/app/media/avatar_128x128.png
    """

    def __init__(self, mediadir):
        super(MediaContentMapper, self).__init__()
        self.mediadir = mediadir

    def perform(self, *tmppaths):
        self.publish('mediapaths_ready',
                     *zip(tmppaths, map(lambda n: os.path.join(self.mediadir, n),
                                        map(os.path.basename, tmppaths))))
