#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from app.lib.pubsub import Publisher


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

    >>> this.perform('/var/web/app/media', 'tmp/12847/avatar.png',
    ...              'tmp/12847/avatar_128x128.png')
    tmp/12847/avatar.png => /var/web/app/media/avatar.png
    tmp/12847/avatar_128x128.png => /var/web/app/media/avatar_128x128.png
    """

    def perform(self, mediadir, *tmppaths):
        self.publish('mediapaths_ready',
                     *zip(tmppaths, map(lambda n: os.path.join(mediadir, n),
                                        map(os.path.basename, tmppaths))))


class ThumbnailGenerator(Publisher):
    """
    >>> class Subscriber(object):
    ...   def thumbnails_ready(self, *thumbnails):
    ...     for t in thumbnails:
    ...       print t
    >>> this = ThumbnailGenerator()
    >>> this.add_subscriber(Subscriber())
    >>> def thumbnail_maker(*args, **kwargs):
    ...   pass

    >>> this.perform(thumbnail_maker, 'image.png')

    >>> this.perform(thumbnail_maker, 'image.png', (128, 128))
    image_128x128.png

    >>> this.perform(thumbnail_maker, 'image.png', (128, 128), (42, 42))
    image_128x128.png
    image_42x42.png
    """

    def perform(self, thumb_maker, imgpath, *sizes):
        """Generates different thumbnails of ``imgpath``, each with one of the
        size specified in ``sizes`` (i.e. tuples containing width and height of
        the thumbnail).

        On success the path of thumbnails created will be published.
        """
        thumbnails = []
        filepath, ext = os.path.splitext(imgpath)
        for (w, h) in sizes:
            dest = '%(path)s_%(width)dx%(height)d%(ext)s'
            dest = dest % dict(path=filepath, width=w, height=h, ext=ext)
            thumb_maker(imgpath, dest, (w, h))
            thumbnails.append(dest)
        self.publish('thumbnails_ready', *thumbnails)


class MediaURLGenerator(Publisher):
    """Generates URLs through which clients can reach media resources.

    >>> class Subscriber(object):
    ...   def invalid_paths(self, *paths):
    ...     for p in paths:
    ...       print p
    ...   def urls_ready(self, *urls):
    ...     for u in urls:
    ...       print u
    >>> this = MediaURLGenerator()
    >>> this.add_subscriber(Subscriber())

    >>> this.perform('/var/web/app/media', 'http://localhost/media',
    ...              '/tmp/12847/avatar.png')
    /tmp/12847/avatar.png

    >>> this.perform('/var/web/app/media', 'http://localhost/media',
    ...              '/tmp/12847/avatar.png', '/tmp/12847/avatar_128x128.png')
    /tmp/12847/avatar.png
    /tmp/12847/avatar_128x128.png

    >>> this.perform('/var/web/app/media', 'http://localhost/media',
    ...              '/var/web/app/media/avatar.png',
    ...              '/var/web/app/media/avatar_128x128.png')
    http://localhost/media/avatar.png
    http://localhost/media/avatar_128x128.png
    """

    def perform(self, mediadir, baseurl, *mediapaths):
        invalid = filter(lambda p: not p.startswith(mediadir), mediapaths)
        if any(invalid):
            self.publish('invalid_paths', *invalid)
        else:
            self.publish('urls_ready',
                         *map(lambda p: p.replace(mediadir, baseurl),
                              mediapaths))
