#!/usr/bin/python3

import time
import telnetlib
import subprocess
from PunktumPlayer import PunktumPlayer


class PunktumPlayerVLC(PunktumPlayer):
    def __init__(self):
        super().__init__()
        self.lastpos = 0
        self.currpos = 0
        self.killstring = "killall -9 vlc"

    def play(self, filename):
        args = ['cvlc', '-I', 'rc', '--rc-host=localhost:4444', '--no-video-title-show', '--no-keyboard-events',
                '--no-video-deco', '--fullscreen', '--deinterlace', '1', '--repeat', filename, '&']
        self.playerproc = subprocess.Popen(args, stdout=subprocess.PIPE)
        # verwendet man --start - time = % s, dann fängt der Clip immer wieder an dieser Stelle an
        time.sleep(2)  # time to start the telnet server
        self.vlcSeek(self.offset + 2)
        super().play(filename)

    def vlcSeek(self, sec):
        HOST = "127.0.0.1"
        PORT = 4444
        tn = telnetlib.Telnet(HOST, PORT)
        data = tn.read_until(">".encode('ascii'), 1)
        data = tn.read_eager()
        while True:
            data = tn.read_eager()
            print(str(data, 'utf-8'))
            if len(data) == 0:
                break
        seekstr = "seek " + str(sec) + "\n"
        tn.write(seekstr.encode('ascii'))
        data = tn.read_until(">".encode('ascii'), 1)
        print(str(data, 'utf-8'))
        while True:
            data = tn.read_eager()
            print(str(data, 'utf-8'))
            if len(data) == 0:
                break
        tn.close()
        # avoid killing vlc
        self.offset = 0
        self.pf.logger.info("seek for clip %d" % sec)

    def checkPlayerStatus(self):
        rval = False
        try:
            HOST = "127.0.0.1"
            PORT = 4444
            tn = telnetlib.Telnet(HOST, PORT)
            data = tn.read_until(">".encode('ascii'), 1)
            while True:
                data = tn.read_eager()
                if len(data) == 0:
                    break
            tn.write("get_time\n".encode('ascii'))
            data = tn.read_until(">".encode('ascii'), 1)
            datastr = str(data, 'utf-8')
            self.currpos = int(datastr.split('\r')[0])
            tn.close()
        except Exception as ex:
            self.pf.logger.error("checkPlayerStatus exception: ".format(ex))
        self.pf.logger.debug("gettime currpos: {0} lastpos: {1}".format(self.currpos, self.lastpos))
        if self.currpos != self.lastpos:
            rval = True
        self.lastpos = self.currpos
        # check if windows is not closed --> for this: sudo apt install wmctrl
        process = subprocess.Popen(['wmctrl', '-l'], stdout=subprocess.PIPE)
        out = process.stdout.read()
        self.pf.logger.debug(out)
        # read liefert bytes deshalb casten
        if not b'VLC media player' in out:
            rval = False
        self.pf.logger.debug("checkPlayerStatus {} ".format(str(rval)))
        return rval


ppv = PunktumPlayerVLC()
ppv.run()


