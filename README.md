# videoplayout
Broadcast control for our local TV station "PUNKTum Fernsehen und Co KG "
https://www.punktum-fernsehen.de/

Our local TV station produces one hour of broadcast every day, which is then repeated 24 times. Starting at 17:00 every day.
At the headends of the cable networks this program is played over a Raspi.
For this, the broadcast is downloaded from an FTP server and then restarted every hour.
The credentials for the ftp server must be provided in a secrets.py file, see secrets_example.py
