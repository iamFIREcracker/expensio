#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ResponseContent(Exception):
    """The content of the response to be sent back to the client.

    It has been modeled as an exception because in certain situations it could
    be handy to return something to the user no matter if you are in the request
    controller."""

    def __init__(self, content):
        self.content = content
