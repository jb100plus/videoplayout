#!/usr/bin/python3

import time
import telnetlib
import subprocess
from PunktumPlayer import PunktumPlayer

'''
under Linux there can be problems with hardware acceleration, in this case disable hardware acceleration
in then vlc preferences: 
Tools → Preferences → Input & Codecs → Codecs → Hardware-accelerated decoding. To disable, select Disable.
https://wiki.videolan.org/VLC_GPU_Decoding/
'''
class PunktumPlayerVLC(PunktumPlayer):
    def __init__(self):
        super().__init__()
        self.killstring = "killall -9 vlc"

    def play(self, filename):
        #if self.playerproc == None:
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
        # avoid killing vlc (omx player can not seek)
        self.offset = 0
        self.pf.logger.info("seek for clip %d and set offset to 0 (avoid killing vlc)" % sec)

    def checkPlayerStatus(self):
        rval = False
        HOST = "127.0.0.1"
        PORT = 4444
        tn = telnetlib.Telnet(HOST, PORT)
        data = tn.read_until(">".encode('ascii'), 1)
        data = tn.read_eager()
        while True:
            data = tn.read_eager()
            if len(data) == 0:
                break
        tn.write("status\n".encode('ascii'))
        data = tn.read_until(">".encode('ascii'), 1)
        datastr = str(data, 'utf-8')
        self.pf.logger.debug(datastr)
        # sudo apt install wmctrl
        # check if a vlc output window is displayed
        if 'playing' in datastr:
            process = subprocess.Popen(['wmctrl', '-l'], stdout=subprocess.PIPE)
            out = process.stdout.read()
            self.pf.logger.debug(out)
            # read liefert bytes deshalb casten
            if b'VLC media player' in out:
                rval = True
                # be sure to run in fullscreen
                tn.write("fullscreen on\n".encode('ascii'))
        tn.close()
        self.pf.logger.debug("checkPlayerStatus {} ".format(str(rval)))
        return rval


ppv = PunktumPlayerVLC()
ppv.run()
