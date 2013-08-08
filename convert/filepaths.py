"""
  utilities for parsing item filenames and generating 
  the right paths for storing data
  
"""

import sys
import os
import re

from session import component_map
from participant import item_site_name, participant_uri
from namespaces import DATA_URI_TEMPLATE, DATA_NS


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
    from the file name, return a dictionary with keys 'session', 'component', 'item'
    
>>> parse_item_filename('1_178_1_2_150.xml')
{'basename': '1_178_1_2_150', 'component': '2', 'item': '150', 'session': '1', 'speaker': '1_178', 'animal': '178', 'colour': '1'}
    
    """

    import re
    result = dict()
    parse_it = re.compile(r'^((\d*)_(\d*)_(\d*)_(\d*)_(\d*))')
    match = parse_it.search(filename)
    if match:
        groups = match.groups() 
        result['basename'] = groups[0]
        result['colour'] = groups[1]
        result['animal'] = groups[2]
        result['speaker'] = groups[1]+"_"+groups[2]
        result['session']   = groups[3]
        result['component'] = groups[4]
        result['item']      = str(int(groups[5]))  # do this to trim leading zeros
    else:
        errorlog.write("'%s' doesn't match the filename pattern\n" % filename )
        
    return result



def item_file_uri(filename, dirname=None):
    """Given a filename for one of the files in an item, return a URI for
     this file on the data server
     
>>> item_file_uri('1_178_1_2_150-ch6-speaker16.wav')
rdflib.term.URIRef(u'http://data.austalk.edu.au/audio/ANU/1_178/1/words-1/1_178_1_2_150-ch6-speaker16.wav')

     """
    path = item_file_path(filename, dirname)
    
    return DATA_NS[path]

def item_file_path(filename, dirname=None):
    """Given a filename for one of the files in an item, return a path that we can 
    use to store it in the right place. This is a relative path, you still
    need to add OUTPUT_DIR to get an absolute path.
    
>>> item_file_path('1_178_1_2_150-ch6-speaker16.wav')
'audio/ANU/1_178/1/words-1/1_178_1_2_150-ch6-speaker16.wav'
>>> item_file_path('1_178_1_2_150.nt', 'metadata')
'metadata/ANU/1_178/1/words-1/1_178_1_2_150.nt'
   
    """
    
    info = parse_item_filename(filename)
    info['filename'] = filename
            
    m = component_map()
    info['componentName'] = m[int(info['component'])]
    info['site'] = item_site_name(participant_uri(info['colour'], info['animal']))
    
    path = DATA_URI_TEMPLATE % info
    
    if dirname == None:
        
        # we modify the path based on the file type since we're splitting
        # audio and video data
        minfo = parse_media_filename(filename)
        if minfo.has_key('type'):
            dirname = minfo['type']
        else:
            raise Exception("Can't work out directory name in item_file_path(%s)" % filename)
        
    path = os.path.join(dirname, path)
    
    return path

def item_file_basename(filename):
    """Given a filename for one of the files in an item, return the basename
    of the item
    
>>> item_file_basename('1_178_1_2_150-ch6-speaker16.wav')
'1_178_1_2_150'
>>> item_file_basename('2_267_1_2_001-ch6-speaker.TextGrid')
'2_267_1_2_001'
    
    """
    
    info = parse_item_filename(filename)
    return info['basename']
    
    
    
    

if __name__=='__main__':
        
        import doctest
        doctest.testmod()
        
        

