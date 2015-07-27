###Basics:

Shutdown:
`sudo shutdown -h now` (or `sudo halt`)
Reboot:
`sudo reboot`

username: pi
password: raspberry

To configure display settings, go to /boot/config.txt

###Basics Setup (first boot):

_Reconfigure keyboard + set local time_
`sudo dpkg-reconfigure keyboard-configuration`

(I set it to Macbook pro, Ctrl+Alt+Backspace stops the x server, or try ctrl-alt-F1 if that doesn't work)

You can also just enter `sudo raspi-config` and go to "Internalization" and pick your settings.

Internationalisation Options > Change Timezone > US > Eastern

Internationalisation Options > Change Keyboard Layout > ... 

_Set up wifi_

Edit wpa\_supplicant.conf:

`sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`

```
network={
    ssid="Wifi"
    psk="Your_wifi_password"
}
```

If it doesn't connect automatically:

```
sudo ifdown wlan0
sudo ifup wlan0
```

Check whether it has connected with `ifconfig wlan0`.

_Update_:

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
```

_Get some tools_:

`sudo apt-get install git-core vim`

_SSH_:

Find rbpi IP address from another computer: `nmap -sP xxx.xxx.0.0/24`. Or do `hostname -I` on the rbpi to find its IP address.

From another computer you can now do: `ssh pi@IP_ADDRESS`.

_From here, there are two options, you can install screenly to display online dashboards (sales display and the Raspberry Pi 2), or you can display unicurses dashboards. Instructions for setting up the two dashboards are below. Don't do both because they conflict_

###Setup for Screenly (to display online dashboards):

Screenly is an open source tool that lets you control what is displayed on the Raspberry Pi. To install screenly, first follow the Basic Setup Instructions. Then:

_Set memory split to 50/50_:

Use `vcgencmd get_mem arm && vcgencmd get_mem gpu` to check the memory split.

Go to the configuraion GUI with `sudo raspi-config` and set the memory split under Advanced Settings > Memory Split.

Now do `sudo reboot`.

Finally, _Install Screenly_ and reboot again:

```
$ curl -sL https://raw.github.com/wireload/screenly-ose/master/misc/install.sh | bash
$ sudo reboot
```
You can also set times for the screen to turn on/off:

```
# minute   hour   day of month     month   day of week       command
#  0-59    0-23   1-31             1-12    0-7 (0/7 is Sun) 
30         18     *                *       *                 /opt/vc/bin/tvservice -p ; /opt/vc/bin/tvservice -o
30         9      *                *       1-5               /opt/vc/bin/tvservice -p ; sudo chvt 6; sudo chvt 7
```

###Setup for Unicurses Displays:

You need to install the necessary python packages for this to work. 

`sudo apt-get install python-pip`

Then clone the github repository and install requirements:

`git clone -b master --single-branch https://github.com/adzerk/rbpi`

`cd rbpi`

`sudo pip install -r requirements.txt` 

####Auto Login

`sudo vim /etc/inittab`

Navigate to the following line `1:2345:respawn:/sbin/getty 115200 tty1` and comment it out.

Add this just below the commented line:

`1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1`

This will run the login program with pi user and without any authentication.

####Run a Script after login:

`sudo vim /etc/profile`

If you are trying to run the graphs:

`sudo /home/pi/rbpi/unicurses\_displays/launcher.sh`

Or, if you are trying to do the chat leaderboard:

`sudo /home/pi/rbpi/unicurses\_displays/ll.sh`

####Prevent Sleep:

`sudo vim /etc/kbd/config`

Replace BLANK\_TIME and POWERDOWN\_TIME with the appropriate values:

```
#BLANK_TIME=30
BLANK_TIME=0
...
#POWERDOWN_TIME=30
POWERDOWN_TIME=0
```
Then, enter `sudo vim /etc/lightdm/lightdm.conf` and add the line: `xserver-command=X -s 0 dpms`.

####Crontab:

This should already be set up. If not, there is a shell script (launcher.sh) that allows you to run the program when the rbpi boots. To do this, make sure that '/home/pi/logs' exists on your pi. If it doesn't, go ahead and create it. Now, make sure that crontab is set up. 

```
sudo crontab -e
```
Make sure that the following line is at the bottom of the file, if it isn't, add it (replace launcher.sh with ll.sh for chat leaderboard).

```
@reboot sh /home/pi/rbpi/unicurses_displays/launcher.sh >/home/pi/logs/cronlog 2>&1

```


####VNC Server (TODO):

https://learn.adafruit.com/downloads/pdf/adafruit-raspberry-pi-lesson-7-remote-control-with-vnc.pdf
https://www.raspberrypi.org/documentation/remote-access/vnc/README.md

Service mode vs. virtual mode:
https://www.realvnc.com/products/vnc/raspberrypi/

###Other potentially useful setup stuff:

#### Options for speeding up the pi:

_Enable Overclock_:

sudo raspi-config > Overclock

_remove wolfram alpha_:

```
$ sudo apt-get remove wolfram-engine  
$ sudo apt-get autoremove 
```
#### Nodm + Uzbl + Matchbox-Window-Manager + Xinit:

To display a webpage on login, followed these [instructions]("http://blog.qruizelabs.com/2014/04/29/raspberrypi-kiosk-matchbox-uzbl/"), the summary/tools are below. Worked much better on rbpi 2 than on rbpi 1.

_nodm (auto login)_:

NODM is cool, but it creates its own settings so don't install if you have other auto-login configurations.

`sudo apt-get install nodm -y`

`sudo vim /etc/default/nodm`

```

NODM_ENABLED=true
NODM_USER=pi

```

_matchbox-window-manager_:

`sudo apt-get install -y matchbox-window-manager`

_uzbl (a light browser)_:

`sudo apt-get -y install uzbl`

_xinit_:

`sudo apt-get -y install xinit`

To display a webpage on the screen when the rbpi boots make a file `/home/pi/.xsession` with the following (replace google with the page you want to display).

```
#!/bin/bash

uzbl -u http://google.com/ -c /home/pi/uzbl.conf &
exec matchbox-window-manager  -use_titlebar no

```

###Prevent Sleep:

`sudo vim /etc/kbd/config`

Replace BLANK\_TIME and POWERDOWN\_TIME with the appropriate values:

```
#BLANK_TIME=30
BLANK_TIME=0
#POWERDOWN_TIME=30
POWERDOWN_TIME=0
```

###Cool links:

Cron jobs to switch on and off :https://parall.ax/blog/view/3045/tutorial-realtime-tv-monitoring-with-raspberry-pi

