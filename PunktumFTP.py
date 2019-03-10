#!/usr/bin/python3

import fnmatch
import ftplib
import os
import random
import re
import time
import secrets

from PunktumFiles import PunktumFiles


class PunktumFTP:
    def __init__(self):
        self.pf = PunktumFiles()

    def DownloadFileFromFTPServer(self, server, username, password, remotedir, filename, offset):
        self.pf.logger.debug(
            'try to connect to %s try download %s with offset %s' % (server, filename, "{:,}".format(offset)))
        rval = False
        try:
            f = ftplib.FTP(server, timeout=60)
        except Exception as e:
            self.pf.logger.error('unable to connect to %s %s' % (server, e))
            return rval
        try:
            f.login(username, password)
            f.cwd(remotedir)
        except Exception as e:
            f.quit()
            self.pf.logger.error("ftp cmd failed %s" % e)
            return rval
        lines = []
        f.dir(lines.append)
        remoteFiles = []
        remoteFilesSizes = []
        for line in lines:
            self.pf.logger.debug("remote dir " + line)
            size = 0
            se = re.search('\d{6,}', line)
            if se:
                size = int(se.group())
            splitter = line.split()
            fn = fnmatch.filter(splitter, '*.mp4')
            if fn:
                assert isinstance(fn[0], str)
                remoteFiles.append(fn[0])
                remoteFilesSizes.append(size)
        for rf in remoteFiles:
            self.pf.logger.debug("available files %s %d" % (rf, remoteFilesSizes[remoteFiles.index(rf)],))
        if not filename in remoteFiles:
            self.pf.logger.debug("file not available %s" % filename)
            return rval
        if remoteFilesSizes[remoteFiles.index(filename)] > offset:
            try:
                count = 0

                def writeLokalFile(data):
                    nonlocal count
                    file = open(filename, 'ab')
                    file.write(data)
                    count += len(data)
                    # print("written %s" % ("{:,}".format(count)))

                self.pf.setCompleteInDB(filename, False)
                f.retrbinary('RETR %s' % filename, writeLokalFile, rest=offset)
                self.pf.setCompleteInDB(filename, True)
                self.pf.logger.info('file %s downloaded successfully' % filename)
                rval = True
            except ftplib.all_errors as e:
                self.pf.logger.error("ftp error %s" % e)
        else:
            self.pf.logger.info("file already downloaded %s" % filename)
            self.pf.setCompleteInDB(filename, True)
        f.quit()
        return rval

    def run(self):
        self.pf.createDB()
        random.seed(None)
        while True:
            try:
                self.pf.deleteOldFiles()
                fn = self.pf.getFilesNeeded()
                for rt in self.pf.relativeTage:
                    existingFileSize = 0
                    file_name = fn[rt]
                    if not self.pf.isFileAvailable(file_name):
                        if os.path.exists(file_name):
                            statinfo = os.stat(file_name)
                            existingFileSize = statinfo.st_size
                        # print("lokal %s %d" % (file_name, existingFileSize))
                        self.DownloadFileFromFTPServer(secrets.ftpserver, secrets.username, secrets.password,
                                                       '.', file_name, existingFileSize)
            except Exception as e:
                self.pf.logger.error("fatal error %s" % e)
            time.sleep(881 + random.randrange(180))


pftp = PunktumFTP()
pftp.run()
