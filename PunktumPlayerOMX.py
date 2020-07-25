#!/usr/bin/python3
import subprocess

from PunktumPlayer import PunktumPlayer


class PunktumPlayerOMX(PunktumPlayer):
    def __init__(self):
        super().__init__()
        self.killstring = "killall -9 omxplayer.bin"

    def play (self, filename):
        # args = ['omxplayer', filename, '--loop', '--adev', 'hdmi', '--deinterlace', '--no-osd', 'fps', '50', '--pos', str(offset), '&']
        args = ['omxplayer', filename, '--loop', '--deinterlace', '--no-osd', '--pos', str(self.offset)]
        self.playerproc = subprocess.Popen(args, stdout=subprocess.PIPE)
        super().play(filename)

    def checkPlayerStatus(self):
        rval = False
        if self.playerproc is not None:
            rc = self.playerproc.poll()
            if rc is None:
                rval = True
        self.pf.logger.debug("checkOMXStatus {} ".format(str(rval)))
        return rval

ppo = PunktumPlayerOMX()
ppo.run()

