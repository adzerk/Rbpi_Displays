import time
import math
from unicurses import *
import copy
from config import config
from datetime import datetime
import os
from glob import glob
import random
from sys import stderr
import slack_stats as s
from pyfiglet import figlet_format

def trello_tickets():
    ##function that returns the number of tickets in a category
    pass

class InfoWindow():
    def __init__(self):
        self.win = None
        self.HEIGHT = 0
        self.WIDGHT = 0
        self.STARTX = 0
        self.STARTY = 0
        self.INDEX = 0
        self.info_type = None
        self.text_lines = 0       
        self.cp = None 


    def get_query_info(self):
        if (self.INDEX == 0):
            self.info_type = "slack"
        elif (self.INDEX == 1):
            self.info_type = "trello"
        #else:
        #    self.info_type = "dummy"

    def make_text(self):
        n = random.randint(1,10)
        self.text_lines = n
        line_chars = random.sample(range(1,15),n)
        lines = []
        for i in range(n):
            my_str = []
            for a in range(line_chars[i]):
                my_str.append('a')
            to_str = ''.join(my_str)
            lines.append(to_str)
        return lines

    def slack_leaderboard(self):
        leader_board = s.make_leaderboard()
        lb = []
        i = len(leader_board.items())
        for key, value in sorted(leader_board.items()):
            rec = str(i) + ". " + str(value['name']) + ": " + str(key)
            lb.append(rec)
            i -= 1
        while (len(lb)>10):
            lb.pop(0)
        self.text_lines = len(lb)
        return lb

    def write_lines(self):
        lines = []
        if self.info_type is "dummy":
            lines = self.make_text()
        if self.info_type is "slack":
            lines = self.slack_leaderboard()
        h = int((self.HEIGHT-1)/(self.text_lines))
        y = self.STARTY + self.HEIGHT
        for i in range(self.text_lines):
            y = y - h
            x = 2
            my_str = str(lines[i])
            fancy = (figlet_format(my_str, font='straight'))
            self.win = self.add_text(x, y, fancy)
        title = "engineering"
        formatted_title = (figlet_format(title, font='speed'))
        line_length = len((formatted_title.split('\n'))[0])
        stx = self.WIDTH-line_length-1
        self.win = self.add_text(stx, 0, formatted_title)
        tag = (figlet_format('#', font='speed'))
        ll = len((tag.split('\n'))[0])
        stx = stx - ll
        self.win = self.add_text(stx, 0, tag)
        wattron(self.win, self.cp)
        box(self.win, 0, 0)
        wattroff(self.win, self.cp)
        #mvwaddstr(self.win, 1, 5, formatted_title)
        return self.win

    ##adds text at specified location in win
    def add_text(self, x, y, text, *args):
        if len(args)>0:
            n = args[0]
            cp = color_pair(n)
        else:
            cp = self.cp
            print >> sys.stderr, ("assinged color")
        wattron(self.win, cp)
        text_lines=text.split('\n')
        for line in text_lines:
            l = str(line)
            mvwaddstr(self.win, y, x, l)
            y = y + 1
            x = x
        wattroff(self.win, cp)
        print >> sys.stderr, ("wrote text: " , text)
        return self.win

    def trello_count(self):
        count = str(s.get_trello())
        print >> stderr, count
        self.text_lines = 1
        wattron(self.win, self.cp)
        title = "CRUSHED"
        formatted_title = (figlet_format(title, font='starwars'))
        the_lines = formatted_title.split('\n')
        y = 1
        x = 3
        for line in the_lines:
            formatted_title = str(line)
            mvwaddstr(self.win, y, x, formatted_title)
            y = y+1
            x = x
        this_month = datetime.now().strftime("%B")
        this_month = "(" + this_month + ")"
        sub_title = (figlet_format(this_month, font='standard'))
        sub = sub_title.split('\n')
        line_length = len(sub[0])
        y = y - 1
        x = int(self.WIDTH - (line_length + 1))
        for line in sub:
            sline = str(line)
            mvwaddstr(self.win, y, x, sline)
            y = y+1
            x = x
        y = int(self.HEIGHT/3)
        x = int(self.WIDTH/3) 
        my_str = (figlet_format(count, font='doh'))
        the_lines = my_str.split('\n')
        for line in the_lines:
            my_str = str(line)
            mvwaddstr(self.win, y, x, my_str)
            y = y + 1
            x = x
        wattroff(self.win, self.cp)
        return self.win

    def update_data(self):
        win = newwin(self.HEIGHT, self.WIDTH, self.STARTY, self.STARTX)
        wattron(win, self.cp)
        box(win, 0, 0)
        wattroff(win, self.cp)
        self.get_query_info()
        if self.info_type is "slack":
            self.win = win
            self.win = self.write_lines()
        elif self.info_type is "trello":
            self.win = win
            self.win = self.trello_count()
        wrefresh(self.win)
        return self

    def make_win(self, height, width, starty, startx, index):
        self.HEIGHT = height
        self.WIDTH = width
        self.STARTY = starty
        self.STARTX = startx
        self.INDEX = index
        self.cp = color_pair(index+1)
        return self
    
    #trello_api = TrelloApi(config.key, token=None)
    def win_show(self):
        self.win = newwin(self.HEIGHT, self.WIDTH, self.STARTY, self.STARTX)
        wattron(self.win, self.cp)
        box(self.win, 0, 0)
        wattroff(self.win, self.cp)
        wrefresh(self.win)
        return self

####TO DO : Make custom # of windows
def init_wins(windows, height, width):
    i = 0
    y = 0
    x = 0

    g = InfoWindow().make_win(height, width, y, x, i) 
    windows[i] = g.win_show()
    
    x += width
    i += 1
    g = InfoWindow().make_win(height, width, y, x, i)
    windows[i] = g.win_show()
    
    #y += height
    #x -= width
    #i += 1
    #g = InfoWindow().make_win(height, width, y, x, i)
    #windows[i] = g.win_show()
    #x += width
    #i += 1
    #g = InfoWindow().make_win(height, width, y, x, i)
    #windows[i] = g.win_show()
    return windows

def main():
    def start_curses(stdscr):
        print "starting currses"
        try:
            windows = [0] * 4
            start_color()
            init_pair(1, COLOR_GREEN, COLOR_BLACK)
            init_pair(2, COLOR_CYAN, COLOR_BLACK)
            init_pair(3, COLOR_RED, COLOR_BLACK)
            init_pair(4, COLOR_BLUE, COLOR_BLACK)
            LINES, COLS = getmaxyx(stdscr)
            #height = int(LINES/2)
            ##two vertical boxes instead of 4 boxes
            height = int(LINES)
            width = int(COLS/2) 
            starty = int((LINES - height) / 2)
            startx = int((COLS - width) / 2)
            addstr("Press s to show windows, press Q to exit")
            refresh()
            ch = -1
            windows = init_wins(windows, height, width)
            refresh()
            #time.sleep(3)
            while (ch!= CCHAR('q')):
                windows[0] = windows[0].update_data()
                windows[1] = windows[1].update_data()
                time.sleep(5)
                #windows[2] = windows[2].update_data()
                #windows[3] = windows[3].update_data()
        except KeyboardInterrupt:
            pass

    ###initialize curses
    stdscr = initscr()
    curs_set(0)
    cbreak()
    noecho()
    keypad(stdscr, True)
    ###curses function is called
    start_curses(stdscr)
    ###closes window at exit of curses
    endwin()

if __name__ == "__main__":
    main()
