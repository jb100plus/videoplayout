#!/usr/bin/python3
import datetime
import os
import time
from PunktumFiles import PunktumFiles


class PunktumPlayer:
    def __init__(self):
        self.pf = PunktumFiles()
        self.playerproc = None
        self.offset = 0
        self.killstring = ""

    def play(self, filename):
        self.pf.logger.info("started playing clip {} offset {}".format(filename, str(self.offset)))

    def checkPlayerStatus(self):
        rval = False
        self.pf.logger.debug("checkPlayerStatus %s " % str(rval))
        return rval

    def run(self):
        currentFile = ""
        while True:
            shouldsleep = True
            try:
                self.pf.logger.debug("do loop")
                dictFn = self.pf.getFilesNeeded()
                fn = dictFn["heute"]
                if not self.pf.isFileAvailable(fn):
                    fn = dictFn["gestern"]
                    self.pf.logger.info("clip %s not available trying %s" % (dictFn["heute"], dictFn["gestern"]))
                ct = datetime.datetime.now()
                # restart every hour, otherwise the clip start at the offset from the first start
                # restart only if there was a significant offset (>10)
                if ct.minute == 0:
                    if self.offset > 10:
                        currentFile = ""
                if fn != currentFile:
                    if self.pf.isFileAvailable(fn):
                        self.pf.logger.debug('kill proc and play the new file {}'.format(fn))
                        os.system(self.killstring)
                        # time.sleep(1)
                        self.offset = ct.minute * 60 + ct.second
                        currentFile = fn
                        # falls die Sendung nur 58 min lang ist
                        self.offset = min([58 * 60, self.offset])
                        self.play(currentFile)
                # if somthing went wrong and the player isn't playing do a restart
                if not self.checkPlayerStatus():
                    currentFile = ""
                    shouldsleep = False
            except Exception as e:
                self.pf.logger.error("fatal error %s" % e)
            if shouldsleep:
                time.sleep(60 - datetime.datetime.now().second)
