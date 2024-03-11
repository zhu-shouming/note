import logging
import sys


class Srlog(object):
    def __init__(self, isstdout=False, level=logging.INFO, bformat='%(asctime)s-%(levelname)s :%(message)s'):
        self.__isstdout = isstdout
        self.__level = level
        self.__strformat = bformat
        logging.basicConfig(level=level, format=bformat)
        self.__log = logging.getLogger()
        self.probe()

    def probe(self):
        format = logging.Formatter(self.__strformat)
        if self.__isstdout:
            sh = logging.StreamHandler()
            sh.setLevel(self.__level)
            sh.setFormatter(format)
            self.__log.addHandler(sh)

    def info(self, msg, *args, **kwargs):
        self.__log.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.__log.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.__log.warning(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.__log.log(level, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self.__log.critical(msg, *args, **kwargs)
        sys.exit(-1)

    def error(self, msg, *args, **kwargs):
        self.__log.error(msg, *args, **kwargs)


logger = Srlog()
