# -*- coding: utf-8 -*-
"""Support for timing blocks of code."""
from __future__ import with_statement
import time


class Timer(object):
    """An object use to time a block of code."""
    def __init__(self):
        self._start = None
        self._finish = None

    def __enter__(self):
        self._start = time.time()

    def __exit__(self, type_, value, traceback):
        self._finish = time.time()

    def duration_in_seconds(self):
        """The amount of time taken to execute block of code. Rounded to
        nearest millisecond.

        """
        return round(self._finish - self._start, 3)
