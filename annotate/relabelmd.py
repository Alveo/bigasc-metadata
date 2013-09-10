'''Code for relabelling the Mitchell & Delbridge data
which has ESPS format label files that are offset by an
unknown amount.
'''

def read_esps(labfile):
    """Read labels from an ESPS format label file
    return a list of segments or events.
    
    If the first label is H# then assume that these are
    segments where H# marks the start of the first segment.
    If the first label is something else, then assume that
    these are events. 
    
    """
    
    
    h = open(labfile)
    inheader = True
    firstlabel = None
    lasttime = None
    labels = []
    
    for line in h.readlines():
        line = line.strip()
        
        if inheader:
            if line == "#":
                inheader = False
                continue
        else:
            (time, colour, label) = line.split()
            time = float(time)
            label = label.strip()
            
            if firstlabel == None:
                firstlabel = label
                
            if label == "H#" and lasttime == None:
                lasttime = time
                continue
                
            if firstlabel == "H#":
                labels.append((lasttime, time, label))
            else:
                labels.append((time, label))
                
            lasttime = time
    return labels

import os
from maus import maus

def make_phb(segments):
    """Given a set of segments, make a PHB format
    label file"""
    
    words = [seg[2] for seg in segments if seg[2] not in ("B", "#", "+")]

    return " ".join(words)

if __name__=='__main__':
    import sys
    
    wavfile = sys.argv[1]
    basename, ext = os.path.splitext(wavfile)
    
    if os.path.exists(basename + ".word"):
        labfile = basename + ".word"
    elif os.path.exists(basename + ".fword"):
        labfile = basename + ".fword"
    else:
         print "No fword file for ", basename
         sys.exit()


    l = read_esps(labfile)
    text = make_phb(l)
    
    textgrid = maus(wavfile, text, outformat='TextGrid')
    h = open(basename+".TextGrid", 'w')
    h.write(textgrid)
    h.close()
        
        
        
        
    