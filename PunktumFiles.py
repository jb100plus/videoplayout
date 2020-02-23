#!/usr/bin/python3

import datetime
import os
import sqlite3
import logging
from logging.handlers import RotatingFileHandler


class PunktumFiles:
    wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    relativeTage = ["heute", "morgen", "gestern"]

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.handlers.RotatingFileHandler("punktum.log", 'a', maxBytes=32 * 1024,
                                                            backupCount=1)
        #self.formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)-7s %(filename)s %(funcName)s %(lineno)d:  %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.createDB()

    def getFilesNeeded(self) -> dict:
        filesNeeded = {}
        offset = [0, 1, -1]
        start = 0
        for _ in self.relativeTage:
            date = datetime.datetime.today() - datetime.timedelta(days=-offset[start]) - datetime.timedelta(hours=17)
            # date = datetime.now() - datetime.timedelta(days=1)
            wt = date.weekday()
            t = date.day
            m = date.month
            fn = ("%02d%02d%s.mp4" % (t, m, self.wochentage[wt]))
            filesNeeded[self.relativeTage[start]] = fn
            start += 1
        return filesNeeded


    def deleteFile(self, filename):
        dictFn = self.getFilesNeeded()
        fna = [dictFn["gestern"], dictFn["heute"], dictFn["morgen"]]
        if not filename in fna:
            file_removed = False
            try:
                os.remove(filename)
                file_removed = True
            except OSError:
                pass
            dbentry_deleted = self.deleteFileEntryFromDB(filename)
            if file_removed or dbentry_deleted:
                self.logger.info('deleted clip {0} {1} {2}'.format(filename, file_removed, dbentry_deleted))


    def deleteFileEntryFromDB(self, filename):
        conn = sqlite3.connect('fwsps.db')
        c = conn.cursor()
        fn = (filename,)
        dbentry_deleted = bool(c.execute("DELETE FROM clips WHERE filename = ?", fn).rowcount)
        conn.commit()
        conn.close()
        if dbentry_deleted:
            self.logger.info('dbentry_deleted  clip {0}'.format(filename))
        return dbentry_deleted


    def deleteOldFiles(self):
        filesToDelete = []
        for t in range(-180, -1):
            date = datetime.datetime.today() - datetime.timedelta(days=-t)
            # date = datetime.now() - datetime.timedelta(days=1)
            wt = date.weekday()
            t = date.day
            m = date.month
            fn = ("%02d%02d%s.mp4" % (t, m, self.wochentage[wt]))
            self.logger.debug('try to delete clip %s' % fn)
            self.deleteFile(fn)
        return filesToDelete

    def setCompleteInDB(self, filename, isComplete):
        conn = sqlite3.connect('fwsps.db')
        c = conn.cursor()
        fn = (filename,)
        c.execute("SELECT filename FROM clips WHERE filename = ?", fn)
        count = 0
        for r in c:
            count += 1
            break
        if count < 1:
            fnt = (filename, str(isComplete),)
            c.execute("INSERT INTO clips VALUES (?, ?)", fnt)
        else:
            fnt = (str(isComplete), filename,)
            c.execute("UPDATE clips SET complete = ? WHERE filename = ? ", fnt)
        conn.commit()
        conn.close()

    def createDB(self):
        rval = False
        if not os.path.exists('fwsps.db'):
            conn = sqlite3.connect('fwsps.db')
            c = conn.cursor()
            c.execute("CREATE TABLE clips (filename text, complete text)")
            # be sure any changes have been committed or they will be lost.
            conn.commit()
            conn.close()
            rval = True
            self.logger.info('DB created')
        return rval

    def isFileAvailable(self, filename):
        rval = False
        conn = sqlite3.connect('fwsps.db')
        c = conn.cursor()
        fn = (filename,)
        c.execute("SELECT complete FROM clips WHERE filename = ?", fn)
        for row in c:
            ic = row[0]
            rval = (ic.upper() == "TRUE")
            break
        if not os.path.exists(filename):
            self.deleteFile(filename)
            rval = False
        return rval
