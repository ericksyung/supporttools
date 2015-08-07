
'''
percentile.py [ -d delimited ] [ -f field ] [ -b bucket size ] [ -v ] [ <data file> ]   

'''
import sys
import getopt
import math
import re

def percentile(N, percent):
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return N[int(k)]
    d0 = N[int(f)] * (c-k)
    d1 = N[int(c)] * (k-f)
    return d0+d1


def printLine():
    print "------------------------------------------------------------------------------"
    
def usage():
    print "percentile [ -d delimiter ] [ -f field ] [ -b bucket ] [ -v verbose] [ <data file> ] "

def printPercentitle(sortedarr):
    cnt_v = len(sortedarr)
    min_v = sortedarr[0]
    max_v = sortedarr[-1]
    avg_v = sum(sortedarr) / float(len(sortedarr))
       
    percentileList= [0.25, 0.50, 0.75, 0.80, 0.95, 0.99, 0.995, 0.999, 0.9999]
    precentitleValue=[]
    
    printLine()
    
    print " Percentile"
    print 
    print "  Cnt = %d; Min = %f; Max = %f; Avg = %f" % (cnt_v, min_v, max_v, avg_v)
    print 
    for p in percentileList:
        v = percentile(sortedarr, p )
        precentitleValue.append(v)
        #print "P%.2f, %f" %  ( p * 100, v )
        print "  P%.2f - %18f" %  ( p * 100, v )   

def printHistogram(sortedarr, bucket):
    
    cnt_v = len(sortedarr)
    min_v = sortedarr[0]
    max_v = sortedarr[-1]
    
    printLine()
    print " Histogram - bucket[%d] " %  bucket
    print 
    
    boundaries = []
    bucket_counts = []
    
    step = (max_v - min_v) /  bucket
    bucket_counts = [0 for x in range(bucket)]
            
    for x in range(bucket):
        boundaries.append(min_v + (step * (x + 1)))
    for v in sortedarr:
        
        for bucket_postion, boundary in enumerate(boundaries):
            if v <= boundary:
                bucket_counts[bucket_postion] += 1
                break
    bucket_max=0
    for bucket in range(bucket):
        bucket_min = bucket_max
        bucket_max = boundaries[bucket]
        bucket_count = bucket_counts[bucket]
        
        pct= "(%.2f%%)" %  (bucket_count * 100.0/cnt_v)
        
        print " %18.4f  - %18.4f  [%5d] %s" % (bucket_min, bucket_max, bucket_count, pct.rjust(9) )
            
    
if __name__ == "__main__":
    
    verbose="0"
    delimiter=","
    field=0
    bucket=10
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                      "hv:d:f:b:",
                        ["help","verbose","delimiter","field","bucket"]
                        )
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(1)
            elif opt in ('-v', '--verbose'):
                verbose = arg
            elif opt in ('-d', '--delimiter'):
                delimiter = arg
            elif opt in ('-f', '--field'):
                field = int(arg)  
            elif opt in ('-b', '--bucket'):
                bucket = int(arg)
            
    except getopt.GetoptError:
        usage()
        sys.exit() 

    #print "args=" + str(args) 
    #print "verbose=" + verbose
    #print "delimiter=" + delimiter
    #print "field=%d" % field
    #print "bucket=%d" % bucket
    
    s = []
    
    f = sys.stdin
    if len(args) > 0:
        f = open(args[0],"r")
    
    for line in f:
        line=line.strip()
        #print line
        if len(line)==0:
            continue
        arr=line.split(delimiter)
        
        if len(arr)< ( field+ 1) :
            continue
        if re.match("[0-9.]+", arr[field]):
            v = float(arr[field])
            s.append(v)
        
    sortedarr=sorted(s)
        
    printPercentitle(sortedarr)
    
    printHistogram(sortedarr, bucket)
