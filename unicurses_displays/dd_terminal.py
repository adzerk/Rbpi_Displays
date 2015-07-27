import time
import math
from unicurses import *
from datadog import initialize, api, statsd, ThreadStats
from collections import deque
import copy
from config import config
from datetime import datetime
import os
from glob import glob
from sys import stderr

class Graph():
    
    def __init__(self, win, H, W, y , x, i):
        ###WINDOW-SPECIFIC INFORMATION
        self.win = win
        self.w_startx = x
        self.w_starty = y
        self.w_height, self.w_width = H, W
        self.index = i
        self.label = None
        ###GRAPH-SPECIFIC VARIABLES:
        self.height = int(self.w_height-3)
        self.width = self.w_width - 6
        self.startx = 6
        self.starty = int(self.w_height-3)
        self.maxx = self.startx + self.width
        ###DATA-SPECIFIC VARIABLES: (these are stored once per graph right now)
        self.dmin = 0
        self.dmax = 0
        self.tmin = 0
        self.tmax = 0
        self.vscale = 0
        self.hscale = 0
        ###GRAPHING:
        self.point_queu = deque()
        self.first = True
        self.num_points = 0
        self.cont_graph = True


    def win_show(self):
        wattron(self.win, color_pair(self.index + 1))
        box(self.win, 0, 0)
        self.drawAxis()
        wattroff(self.win, color_pair(self.index + 1))
 
    def drawAxis(self):
        y0 = self.starty
        x0 = self.startx
        mvwhline(self.win, y0, 1, ACS_HLINE, self.w_width - 2)
        mvwvline(self.win, 1, x0, ACS_VLINE, self.w_height - 2)       
    
    def data_labels(self):
        t_int = int(self.height/4)
        wattron(self.win, color_pair(self.index + 1))
        for i in range(1, 4):
            y = int(i*t_int)
            value = str(round((y)*(self.vscale), 2)).replace('0.', '.')
            mvwaddstr(self.win, self.starty-y, 1, value)
        if (self.num_points!=0):
            time_interval = int(600/self.num_points)
            output_string = str(time_interval) + " seconds/point"
            mvwaddstr(self.win, self.w_height - 1, self.w_width - int((self.w_width)/3), output_string)
        wattroff(self.win, color_pair(self.index + 1))

    def labels(self):
        wattron(self.win, color_pair(self.index + 1))
        label = str(self.label)
        mvwaddstr(self.win, self.w_height - 2, 7, label)
        wattroff(self.win, color_pair(self.index + 1))

    def mkscale_h(self):
        hscale = float((self.width)/(self.tmax - self.tmin))
        self.hscale = hscale

    def mkscale_v(self):
        vscale = float((self.height)/(self.dmax - self.dmin))
        self.vscale = vscale

    def is_in_range(self, data):
        return data <= self.dmax and data >= self.dmin

    def data_to_screen(self, d):
        """convert data into screen coordinates (y=0 is at the top!)"""
        y_value = (d - self.dmin) * self.vscale
        return y_value
    
    def time_to_screen(self, t):
        time1 = (t- self.tmin) * self.hscale
        time = self.startx + time1
        return time

    def in_range(self, x):
        if (x < self.startx):
            return False
        return True

    def x_range(self, x_min, x_max):
        self.tmin, self.tmax = x_min, x_max

    def y_range(self, y_min, y_max):
        self.dmin, self.dmax = y_min - 1, y_max + 1

    def set_y(self, data):
        miny = min(y[1] for y in data)
        maxy = max(y[1] for y in data)
        self.y_range(miny, maxy)

    def set_x(self, data):
        minx = min(x[0]for x in data)
        maxx = max(x[0] for x in data)
        self.x_range(minx, maxx)

    def transpose_data(self, data):
        if (self.first == True):
            self.set_x(data)
            self.mkscale_h()
        self.set_y(data)
        self.mkscale_v()
        self.data_labels()
        self.labels()
        point = data.popleft()
        n = 0
        y1 = int(self.data_to_screen(point[1]))
        y = self.starty - y1
        x = int(self.time_to_screen(point[0]))
        old = len(self.point_queu)
        while (len(data) != 0):
            x0 = x
            y0 = y
            n+=1
            point = data.popleft()
            y1 = int(self.data_to_screen(point[1]))
            y = self.starty - y1
            x = int(self.time_to_screen(point[0]))
            self.fill_points(x0, x, y0, y)
        if (self.first == True):
            self.num_points = len(self.point_queu)
            self.first = False
            temp = copy.copy(self.point_queu)
            self.make_graph(temp)
            self.win.refresh()

    def fill_points(self, x0, x1, y0, y1):
        n = x1-x0
        slope = ((y1-y0)/(x1-x0))
        for x in range(x0, x1):
            y = self.starty - (int((slope)*(x - x0)) + y0)
            self.point_queu.append((x, y))

    def make_graph(self, temp):
        i = 0
        while (temp):
            point = temp.popleft()
            x = self.startx + i
            y = point[1]
            h = self.starty - y
            self.graph_point(y, x, h)
            i += 1
        self.win.refresh()

    def graph_point(self, y, x, h):
        wattron(self.win, color_pair(self.index + 1))
        mvwvline(self.win, y, x, ACS_VLINE, h)
        wattroff(self.win, color_pair(self.index + 1))
    
    def move_graph(self):
        '''Move graph through until last point is out of range''' 
        temp = deque()
        point = self.point_queu.popleft()
        x_start = point[0]
        y = point[1]
        x_last = self.maxx
        while(self.point_queu):
            point = self.point_queu.popleft()
            x_temp = point[0]
            y_temp = point[1]
            interval = x_temp - x_start
            if (x_temp != x_start):
                x_last = x_temp
                x = x_temp - interval
                y = y_temp
            else:
                x = x_last
                y = y_temp
            if (self.in_range(x)):
                temp.append((x, y))
        self.point_queu = temp

def graph(g):
    '''new data gets passed to graph'''
    if (len(g.point_queu) > g.num_points):
        g.move_graph()
        new_win = newwin(g.w_height, g.w_width, g.w_starty, g.w_startx)
        g.win = new_win
        g.win_show()
        g.labels()
        g.data_labels()
        temp = copy.copy(g.point_queu)
        g.make_graph(temp)
    else:
        g.cont_graph = False
    return g

def rotate_graphs(graphs, datasets):
    '''next set of data is prepared to be graphed'''
    to_graph = []
    #make the initial graphs
    for i in range(len(graphs)):
        g = graphs[i]
        data = datasets[i]
        g.transpose_data(data)
        g.cont_graph = True
        to_graph.append(g)
    graphs = push_graphs(to_graph)
    return graphs

###TODO: move graphs through time period
###TODO: split this out into another function so that you can graph longer time period and then move them through w/ shorter updates
def push_graphs(to_graph):
    grph = len(to_graph)
    while(grph != 0):
        for g in to_graph:
            sleep_time = int(600/(g.num_points))
            if (g.cont_graph == False):
                grph -= 1
            else:
                g = graph(g)
        time.sleep(sleep_time)
    return to_graph

def data_dog_query(query):
    try:
        options = {'api_key':config['api_key'],'app_key':config['app_key']}
    except:
        sys.stderr.write('Config not found, using pre-stored test data instead.')
        ddq_test()
    initialize(**options)
    start = int(time.time()) - 600
    end = start + 600
    avgs = deque()
    status = ''
    while (status!='ok'):
        results = api.Metric.query(start=start, end=end, query=query)
        status = results['status']
        sys.stderr.write("Status: %s \n" % status)
    points = results['series'][0]['pointlist']
    unit = results['series'][0]['unit']
    sys.stderr.write("The query returned %s points \n" % str(len(points)))
    for item in points:
        x = item[0]/1000
        y = item[1]
        avgs.append((x, y))
    return avgs, unit

#use this for testing
def ddq_test():
    avgs = deque([(1434379740.0, 54.364407368195366), (1434379750.0, 51.67413633297651), (1434379760.0, 50.24604679987981), (1434379770.0, 50.33439381917318), (1434379780.0, 50.762425544934395), (1434379790.0, 50.49690989958934), (1434379800.0, 47.95996064406175), (1434379810.0, 51.564790138831505), (1434379820.0, 52.07391709547777), (1434379830.0, 51.61038936712803), (1434379840.0, 49.79181436391977), (1434379850.0, 49.89993364383013), (1434379860.0, 50.43370848435622), (1434379870.0, 52.444759368896484), (1434379880.0, 52.07711460085011)])
    data_sets = [avgs, avgs, avgs, avgs]
    return data_sets

def new_config(num):
    '''Get the datadog endpoints from txt file or config'''
    files = glob('./*_graph_2.txt')
    config['graphs'] = []
    if (len(files) != 0):
        filename = str(files[0])
        try:
            f_in = open(filename, 'r')
            config['graphs'] = []
            for line in f_in:
                if (len(config['graphs'])< (num + 1)):
                    config['graphs'].append(line)
            f_in.close()
            log_file = filename.replace('./','./done/').replace('graph_2','graph_log')
            os.rename(filename, log_file)
            return config['graphs']
        except IOError as e:
            sys.stderr.write(log_file + str(e.value))
        except IndexError as i:
            sys.stderr.write(str(i))
    else:
        i = 0
        while (i < num):
            config['graphs'].append(config['default_graphs'][i])
            i += 1
    return config['graphs']

def make_labels(windows, queries, units):
    for i in range(len(windows)):
        label = str(queries[i]).strip('{*}')
        name = label.split(':')
        name = name[1]
        unit = str(units[i])
        sys.stderr.write('Units : %s \n' % str(units[i]))
        if 'None' not in unit:
            name = name + unit
        windows[i].label = name
    return windows

def init_wins(windows, height, width, num_rows, num_cols):
    """init windows with given dimensions"""
    i = 0
    y = 0
    x = 0
    max_width = width * num_cols
    max_height = height * num_rows
    while y< max_height:
        while x < max_width:
            sys.stderr.write('Init Window %s at:  X : %s , Y: %s \n' % (i, x , y))
            w = newwin(height, width, y, x)
            windows[i] = Graph(w, height, width,y, x, i)
            x += width
            i += 1
        y += height
        x = 0
    
    for window in windows:
        window.win_show()

def main():
    def start_curses(stdscr):
        try:
            W_rows = 2
            W_cols = 2
            W_num = W_rows*W_cols
            windows = [0] * W_num
            start_color()
            colors = [COLOR_BLACK, COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_CYAN]
            for i in range(1, W_num+1):
                init_pair(i, colors[i], COLOR_BLACK)
                sys.stderr.write('Color %s : %s \n' % (i, str(colors[i])))
                i += 1
            LINES, COLS = getmaxyx(stdscr)
            
            height = int(LINES/W_rows)
            width = int(COLS/W_cols)
            init_wins(windows, height, width, W_rows, W_cols)
            doupdate()
            
            while((datetime.now().hour) != 17):
                queries = new_config(W_num)
                sys.stderr.write('Data dog stats : %s\n' % queries)
                n = len(queries)
                datasets = []
                units = []
                for count in range(len(windows)):
                    q_list = data_dog_query(queries[count])
                    units.append(q_list[1])
                    datasets.append(q_list[0])
                windows = make_labels(windows, queries, units)
                windows = rotate_graphs(windows, datasets)
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
