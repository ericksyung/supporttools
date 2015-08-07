'''
Created on Aug 7, 2015

@author: eric.yung
'''

import sys
import getopt
import time
import re
import select
from datetime import datetime

series=[]
last_v= None
min_v = None
max_v = None

blue_palette = {0:15, 1:51, 2:45, 3:39, 4:33, 5:27, 6:21}        # shades of blue: white-light blue-dark blue
red_palette  = {0:15, 1:226, 2:220, 3:214, 4:208, 5:202, 6:196}  # white-yellow-red palette


class GlobalParameters:
    def __init__(self):
        self.verbose="0"
        self.delimiter=","
        self.mode = "last"       # "last", "avg" , "max"
        self.field=0
        self.refresh=2
        self.keeplast=False
        self.color_palette = blue_palette;
        self.yaxis_size = 25
        self.xaxis_size = 50
        
    def get_options(self): 
        opts, args = getopt.getopt(sys.argv[1:],
                                "m:kc:hv:d:f:n:x:y:",
                                ["mode","color", "help","verbose","delimiter","field","refresh","point","row"]
                                )
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                self.usage()
                sys.exit(1)
            elif opt in ('-v', '--verbose'):
                self.verbose = arg
            elif opt in ('-k', '--keeplast'):
                self.keeplast = True
                
            elif opt in ('-c', '--color'):
                if (arg == "red"):
                    self.color_palette = red_palette
                elif (arg == "red"):
                    self.color_palette = blue_palette
                elif (arg == "none"):
                    self.color_palette = None

            elif opt in ('-d', '--delimiter'):
                self.delimiter = arg
            elif opt in ('-f', '--field'):
                self.field = int(arg)
            elif opt in ('-n', '--refresh'):
                self.refresh = int(arg)    
            elif opt in ('-x', '--xaxis'):
                self.xaxis_size = int(arg)    
            elif opt in ('-y', '--yaxis'):
                self.yaxis_size = int(arg)    
            elif opt in ('-m', '--mode'):
                self.mode = arg    

    def usage(self):
        print "term_realchart.py  [ -h ] [ -v ] [ -c red|blue|none ] [ -d delimiter ] [ -f field ] " + \
        "[ -n refresh ] [ -x x-axis size ] [ -y y-axis size ] [ -m last|max|avg ]"

g_params = GlobalParameters()
        
def printLine():
    print "-" * max( 80, g_params.xaxis_size + 21 )

def clearScr():
    global g_params
    line = chr(27) + '[0m' + chr(27) + '[2J' + chr(27) + '[H'   # clear screen and move cursor to top line
    line += "Real Chart (refresh = %ds)  (mode=%s)                                           " % ( g_params.refresh, g_params.mode)  
    line += datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print line
    printLine()
  
def read_data():
    global series
    global g_params
    
    f = sys.stdin
    
    v = None    
    temp_series = []    
    while f in select.select([f], [], [], 0)[0]:
        line = f.readline()
        line = line.strip()
        # remove multiple space if using space as delimiter
        if g_params.delimiter == ' ':
            line = re.sub(' +', ' ', line)
        if line:
            arr=line.split(g_params.delimiter)
            if g_params.verbose != "0":
                print arr
            if len(arr)< ( g_params.field+ 1) :
                continue
            if re.match("[0-9.]+", arr[g_params.field]):
                #v = float(arr[field])
                temp_series.append(float(arr[g_params.field]))
        else: # an empty line means stdin has been closed
            #print('eof')
            break

    if (len(temp_series) > 0):
        if (g_params.mode == "last"):
            v = temp_series[-1]
        elif (g_params.mode == "avg"):
            v = sum(temp_series) / float(len(temp_series))
        elif (g_params.mode == "max"):
            v = max(temp_series) 
        else: # default last
            v = temp_series[-1]
        
    if (g_params.keeplast):
        if (v is not None):
            last_v =v 
        else:
            v = last_v
       
    if (v == None):
        v = 0.0
        
    series.append(v)

def draw_chart():
    global series
    global min_v
    global max_v
    global g_params
    
    if g_params.verbose != "0":
        print series    
    
    if  min_v == None or min(series) < min_v:
        min_v = max(min(series), 0 )       # bound or zero
        
    if  max_v == None or max(series) > max_v:
        max_v = max(series)
    
    interval =  (max_v - min_v) * 1.0 / g_params.yaxis_size
 
    for i in range(g_params.yaxis_size, 0, -1):
        #print "%d, %f" % ( i , min_v + i * interval)
        line = "%2d - %11.2f | " % ( i , min_v + i * interval)

        for v in series[::-1]:
            bound = (min_v + (i-1) * interval) 
            
            if v > bound:
                
                if (g_params.color_palette):
                
                    color_interval = g_params.yaxis_size * 1.0 / len(g_params.color_palette)
                     
                    #  print color_interval
                    color_code = g_params.color_palette[ min( int(i / color_interval),  len(g_params.color_palette) - 1 )
                                         ]                 
                    color = (chr(27) + '[48;5;' + str(color_code) + 'm')
                    asciiescape_backtonormal = chr(27) + '[0m'
                    
                    # line += "+"
                    line += color + " " + asciiescape_backtonormal
                else:
                    line += "+"
            else: 
                line += " "
                
        print line
    
    line = "%2d - %11.2f | " % (0 , 0)

    for v in series[::-1]:
        if v is not None:
            
            if (g_params.color_palette):
                   
                color_code = g_params.color_palette[0                                         ]                 
                color = (chr(27) + '[48;5;' + str(color_code) + 'm')
                asciiescape_backtonormal = chr(27) + '[0m'
                
                # line += "+"
                line += color + " " + asciiescape_backtonormal
            else:
                line += "-"
    print line                

def print_summary():
    global series

    printLine()   
    print "last: %10.2f  ; Min: %10.2f ; Max: %10.2f" % ( series[-1], min(series), max(series))


def roll_data():
    global g_params
    global series
    global MAX_SERIES
    if len(series) > g_params.xaxis_size:
        series.pop(0)
    
    
if __name__ == "__main__":
    
    try:
        g_params.get_options()
    except getopt.GetoptError:
        g_params.usage()
        sys.exit() 
        
    for i in range(g_params.xaxis_size):
        series.append(0)
    
    while True:
        clearScr()
        read_data()
        draw_chart()
        print_summary()
        roll_data()
        sys.stdout.flush()
        time.sleep(g_params.refresh)
