"""
  utilities for parsing item filenames and generating 
  the right paths for storing data
  
"""

import sys
import os
import re


def parse_media_filename(filename, errorlog=sys.stderr):
     """Extract the channel name, media type and -n status from a filename
     return a dictionary.
 

 >>> parse_media_filename('1_178_1_2_150-ch1-maptask.wav')
 {'basename': '1_178_1_2_150', 'version': 1, 'type': 'audio', 'channel': 'ch1-maptask'}
     
 >>> parse_media_filename('1_178_1_2_150-n-ch1-maptask.wav')
 {'basename': '1_178_1_2_150', 'version': 2, 'type': 'audio', 'channel': 'ch1-maptask'}
     
 >>> parse_media_filename('1_178_1_2_150-n-n-ch1-maptask.wav')
 {'basename': '1_178_1_2_150', 'version': 3, 'type': 'audio', 'channel': 'ch1-maptask'}
 
 >>> parse_media_filename('1_178_1_2_150-n-n-n-n-n-ch1-maptask.wav')
 {'basename': '1_178_1_2_150', 'version': 6, 'type': 'audio', 'channel': 'ch1-maptask'}
 
 >>> parse_media_filename('1_178_1_2_150-camera-0-left.mp4')
 {'basename': '1_178_1_2_150', 'version': 1, 'type': 'video', 'channel': 'camera-0-left'}
 
 >>> parse_media_filename('1_178_2_16_001-camera-0-right.mp4')
 {'basename': '1_178_2_16_001', 'version': 1, 'type': 'video', 'channel': 'camera-0-right'}
 
 >>> parse_media_filename('1_1121_1_12_001-ch4-c2Left.wav')
 {'basename': '1_1121_1_12_001', 'version': 1, 'type': 'audio', 'channel': 'ch4-c2Left'}
 
 >>> parse_media_filename('1_1121_1_12_001-ch6-speaker-yes.wav')
 {'basename': '1_1121_1_12_001', 'version': 1, 'type': 'audio', 'response': 'yes', 'channel': 'ch6-speaker'}
 
 >>> parse_media_filename('1_178_1_2_150-camera-0-no-left.mp4')
 {'basename': '1_178_1_2_150', 'version': 1, 'type': 'video', 'response': 'no', 'channel': 'camera-0-left'}
 
 >>> parse_media_filename('1_178_1_2_150-n-n-camera-0-yes-left.mp4')
 {'basename': '1_178_1_2_150', 'version': 3, 'type': 'video', 'response': 'yes', 'channel': 'camera-0-left'}
 
 >>> parse_media_filename('1_178_1_2_150-ch6-speaker16.wav')
 {'basename': '1_178_1_2_150', 'version': 1, 'type': 'audio', 'channel': 'ch6-speaker16'}
     """
     
     
     pattern_wav = "([0-9_]+)-((n-)*)(ch[0-9]-[a-zA-Z0-9]+)(-(yes|no))?\.wav"
     
     pattern_mp4 = "([0-9_]+)-((n-)*)((camera-[0-9])(-(yes|no))?(-left|-right))\.mp4"
     
     m_wav = re.match(pattern_wav, filename)
     m_mp4 = re.match(pattern_mp4, filename)
     
     if m_wav:
         (base, alln, n, channel, ignore, yesno) =  m_wav.groups() #@UnusedVariable
         type = 'audio'
     elif m_mp4:
         (base, alln, n, ignore, camera, ignore, yesno, leftright ) = m_mp4.groups()
         #print "MATCH: ", (base, alln, n, ignore, camera, ignore, yesno, leftright )
         channel = camera + leftright
         type = 'video'
     else:
         # unknown file pattern
         errorlog.write("filename doesn't match media pattern: %s\n" % filename)
         return dict()
             
     if n == None:
         version = 1
     else:
         version = len(alln)/2 + 1
     
     result = {'basename': base, 'channel': channel, 'type': type, 'version': version}
     if yesno != None:
         result['response'] = yesno
         
     #print "PMF: ", filename, result
     return result
 
 
 
def parse_item_filename(filename, errorlog=sys.stderr):
    """Get the session, component and item ids
    from the file name, return a dictionary with keys 'session', 'component', 'item'"""

    import re
    result = dict()
    parse_it = re.compile(r'^(\d*)_(\d*)_(\d*)_(\d*)_(\d*)')
    match = parse_it.search(filename)
    if match:
        groups = match.groups() 
        result['colour'] = groups[0]
        result['animal'] = groups[1]
        result['speaker'] = groups[0]+"_"+groups[1]
        result['session']   = groups[2]
        result['component'] = groups[3]
        result['item']      = str(int(groups[4]))  # do this to trim leading zeros
    else:
        errorlog.write("'%s' doesn't match the filename pattern\n" % filename )
        
    return result
