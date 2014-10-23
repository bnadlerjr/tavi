# -*- coding: utf-8 -*-
from tavi import Connection
import logging

Connection.setup("test_database")


class LogCapture(logging.Handler):
    MSG_TYPES = ["debug", "info", "warning", "error", "critical"]

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def __enter__(self):
        logging.getLogger().addHandler(self)
        return self

    def __exit__(self, type_, value, traceback):
        logging.getLogger().removeHandler(self)
        self.close()

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {t: [] for t in self.MSG_TYPES}
