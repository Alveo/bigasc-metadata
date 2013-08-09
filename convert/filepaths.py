"""
  utilities for parsing item filenames and generating 
  the right paths for storing data
  
"""

import sys
import os
import re
import urllib2
import json

from session import component_map
from participant import item_site_name, participant_uri
from namespaces import DATA_URI_TEMPLATE, DATA_NS

import configmanager
configmanager.configinit()

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
 
 >>> parse_media_filename('1_178_1_2_150-ch6-speaker16.raw16')
 {'basename': '1_178_1_2_150', 'version': 1, 'type': 'raw16', 'channel': 'ch6-speaker16'}
     """
     
     basename = os.path.basename(filename)
     
     pattern_general = "([0-9_]+)-((n-)*)(ch[0-9]-[a-zA-Z0-9]+)(-(yes|no))?\.(.*)"
     
     pattern_video = "([0-9_]+)-((n-)*)((camera-[0-9])(-(yes|no))?(-left|-right))\.(.*)"
     
     m_gen = re.match(pattern_general, basename)
     m_vid = re.match(pattern_video, basename)
     
     if m_gen:
         (base, alln, n, channel, ignore, yesno, ext) =  m_gen.groups() #@UnusedVariable
         if ext == 'wav':
             type = 'audio'
         else:
             type = ext
     elif m_vid:
         (base, alln, n, ignore, camera, ignore, yesno, leftright, ext) = m_vid.groups()
         #print "MATCH: ", (base, alln, n, ignore, camera, ignore, yesno, leftright )
         channel = camera + leftright
         if ext == 'mp4':
             type = 'video'
         else:
             type = ext
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
>>> parse_item_filename('../test/University_of_Tasmania,_Hobart/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003')
{'basename': '2_2_1_11_003', 'component': '11', 'item': '3', 'session': '1', 'speaker': '2_2', 'animal': '2', 'colour': '2'}
    """

    import re
    basename = os.path.basename(filename)
    result = dict()
    parse_it = re.compile(r'^((\d*)_(\d*)_(\d*)_(\d*)_(\d*))')
    match = parse_it.search(basename)
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
>>> item_file_basename('../test/University_of_Tasmania,_Hobart/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003')
'2_2_1_11_003'

    """
    
    info = parse_item_filename(filename)
    return info['basename']
    



def versionselect():
    """Load versionselect data from the website (or a chached
    copy) and return the dictionary"""
    
    global VERSIONS
    
    try:
        return VERSIONS
    except:
        # VERSIONS not bound
        url = configmanager.get_config("VERSIONSELECT_URL")
        cache = configmanager.get_config("VERSIONSELECT_CACHE", "versionselect.json")
        
        if os.path.exists(cache):
            h = open(cache)
            json_text = h.read()
            h.close()
        else:
            h = urllib2.urlopen(url)
            json_text = h.read()
            h.close()
            # cache a copy
            h = open(cache, 'w')
            h.write(json_text)
            h.close()
        
        VERSIONS = json.loads(json_text)
        return VERSIONS


def item_file_versions(path):
    """Given the base path of an item, return a tuple
    that contains two lists (good, bad) where good is a 
    list of files that should be kept and bad is a list
    of files that should not.  The data comes from
    the versionselect application where there are more
    than one version of a recording for an item
    
>>> item_file_versions('test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016')
(['test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-camera-0-left.mp4', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-camera-0-right.mp4', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-ch1-maptask.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-ch2-boundary.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-ch3-strobe.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-ch4-c2Left.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-ch5-c2Right.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_016-ch6-speaker.wav'], [])

# fake this a little
>>> versions = versionselect()
>>> versions['1_1216_1_4_001'] = [2]
>>> item_file_versions('test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001')
(['test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-camera-0-left.mp4', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-camera-0-right.mp4', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-ch1-maptask.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-ch2-boundary.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-ch3-strobe.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-ch4-c2Left.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-ch5-c2Right.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-n-ch6-speaker.wav'], ['test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-camera-0-left.mp4', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-camera-0-right.mp4', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-ch1-maptask.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-ch2-boundary.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-ch3-strobe.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-ch4-c2Left.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-ch5-c2Right.wav', 'test/University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_4/1_1216_1_4_001-ch6-speaker.wav'])
    """
    
    versions = versionselect()
    
    basename = item_file_basename(path)
    all_files = item_files(path)
    
    # do we have more than one version
    fv = dict()
    for fn in all_files:
        props = parse_media_filename(fn)
        v = props['version']
        if fv.has_key(v):
            fv[v].append(fn)
        else:
            fv[v] = [fn]
    
    
    
    if len(fv) == 1:
        # we only have one version
        return (all_files, [])
    
    # see if we have versionselect data for this item    
    if versions.has_key(basename):
        goodversions = versions[basename]
        goodfiles = []
        badfiles = []
        for v in goodversions:
            goodfiles.extend(fv[v])
            del fv[v]
        # now badfiles is the rest
        for v in fv.keys():
            badfiles.extend(fv[v])

        return (goodfiles, badfiles)

    else:
        print "Duplicate recordings and no version info for ", basename
        return ([], [])
        


def item_files(path):
    """Given the base path of an item, return a list
    of the files associated with that item - ie. all
    files starting with this prefix except the .xml
    metadata file.

>>> sorted(item_files('University_of_the_Sunshine_Coast,_Maroochydore/Spkr1_1216/Spkr1_1216_Session1/Session1_11/1_1216_1_11_003'))
[]
    """
    
    from glob import glob
    
    files = glob(path + '*')
    return [f for f in files if not f.endswith('.xml')]





if __name__=='__main__':
        
    import doctest
    doctest.testmod()


    
        
        

