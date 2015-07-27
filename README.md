Both displays use unicurses, a python wrapper for ncurses, which can be found
here: https://github.com/Chiel92/unicurses. To run the application on your
computer you can follow the install instructions for unicurses or move the
unicurses.py file from the raspberry pi into your directory.

#ASCII art chat leaderboard/trello tickets:

A dashboard displaying stats. This is kind of a temporary dashboard (maybe a
click map or something will take its place later)!

Dashboard currently displays a slack leader board for the #engineering channel
and the number of tickets that have moved to the "CRUSHED!" board this month
(according to the slack trello channel).

The launch script for this is ll.sh (only works on rbpi and must be run with
sudo) or you can run it with `python stats_dash.py 2> err`. The file
`fonts_list.txt` contains a list of the fonts provided by the pyfiglet library
and how they look printed out (quick reference if you are trying to change the
fonts on the display).

#Graph Display:

Make an application that plots datadog stats in real (ish) time. There's a 5
minute delay. Right now, there are four graphs displayed using datadog data. 

To run, make sure to redirect the error messages or they will show up on the
screen. They're still useful when stuff goes wrong.

`python dd_terminal.py 2> err` 

##Make the request file:

To display different graphs from data dog, put the request names in a file
called `yourName_graphs_{#}.txt`. (TODO: changing the number of graphs isn't
impemented yet).

There should be one request per line, no blank lines, and a maximum of 4 graphs
will be displayed (if you have more than this in the file, nothing bad will
happen, but they won't be graphed). There's no error checking for now, so make
sure that the requests are in the correct format and that they actually exist.
An example file, called `audrey_graphs_2.txt` :

``` 
avg:adserver.api.request.avg{*} 
avg:adserver.ados.request.avg{*}
```
Example for four `audrey_graphs_4.txt`:
```
sum:adserver.api.request.count{*} 
avg:adserver.api.request.avg{*} 
avg:adserver.ados.request.avg{*}
sum:eventserver.events.impression{*} 
```

Also, there's no ordering of who's files are graphed right now, so if there are
multiple files they'll each get ~5 minutes on the screen and then the last one
will stay on the screen until a new file shows up.

##Get the file to the Raspberry Pi:

Put this file in the right directory on the raspberry pi
`/home/pi/rbpi/unicurses_display/`. You can do this with scp:

```
scp /path/to/your/file pi@<IP_Adress>:/home/pi/rbpi/unicurses_displays/. 
```

After a file has been logged, it will appear in the 'done' folder in the
directory that contains the python script on the Raspberry Pi, and the name will
appear as `yourname_graph_log.txt`.

##Running display on login (this should already be setup):

###Auto Login

`sudo vim /etc/inittab`

Navigate to the following line `1:2345:respawn:/sbin/getty 115200 tty1` and
comment it out.

Add this just below the commented line:

`1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1`

This will run the login program with pi user and without any authentication.

###Run a Script after login:

`sudo vim /etc/profile`

If you are trying to run the graphs:

`sudo /home/pi/rbpi/unicurses\_displays/launcher.sh`

Or, if you are trying to do the chat leaderboard:

`sudo /home/pi/rbpi/unicurses\_displays/ll.sh`

###Prevent Sleep:

`sudo vim /etc/kbd/config`

Replace BLANK\_TIME and POWERDOWN\_TIME with the appropriate values:

```
#BLANK_TIME=30 BLANK_TIME=0 ...  #POWERDOWN_TIME=30 POWERDOWN_TIME=0
```
Then, enter `sudo vim /etc/lightdm/lightdm.conf` and add the line:
`xserver-command=X -s 0 dpms`.

###Crontab:

This should already be set up. If not, there is a shell script (launcher.sh)
that allows you to run the program when the rbpi boots. To do this, make sure
that '/home/pi/logs' exists on your pi. If it doesn't, go ahead and create it.
Now, make sure that crontab is set up. 

``` 
sudo crontab -e 
``` 
Make sure that the following line is at the bottom of
the file, if it isn't, add it:

``` 
@reboot sh /home/pi/rbpi/unicurses_displays/launcher.sh >/home/pi/logs/cronlog 2>&1

```
