'''

Map operations over Austalk session data

Created on Nov 6, 2012

@author: steve
'''

import re, os


def site_sessions(dirname):
    """
    Returns a sequence of sessions for the given
    site directory.  We look for speaker directories
    first then sessions within those.

>>> list(site_sessions('../test/'))
['../test/Spkr2_2/Spkr2_2_Session1']

    """
    for spkrdir in os.listdir(dirname):
        if os.path.isdir(os.path.join(dirname, spkrdir)):
            for sessiondir in os.listdir(os.path.join(dirname, spkrdir)):
                if parse_session_dir(sessiondir):
                    yield(os.path.join(dirname, spkrdir, sessiondir))
    


def parse_session_dir(dirname):
    """Return a pair (speakerid, sessionid) for this 
    session directory name or None if it doesn't match the pattern

>>> parse_session_dir("Spkr1_123_Session3")
('1_123', '3')
>>> parse_session_dir("Not a Session Dir")
>>> parse_session_dir("Spkr1_1_Session4")
('1_1', '4')
    """
    
    SESSION_DIR_PATTERN = "Spkr([1234]+_[0-9]+)_Session([0-4]+)"
    
    match = re.match(SESSION_DIR_PATTERN, dirname)
    if match:
        return match.groups()
    else:
        return None
        
def parse_component_dir(dirname):
    """Return a pair (sessionid, componentid) for this 
    component directory or None if it doesn't match the pattern

>>> parse_component_dir("Session2_22")
('2', '22')
>>> parse_component_dir("Doesn't match")
>>> parse_component_dir("Session1_2")
('1', '2')
    """

    match = re.match(r'^Session(\d*)_(\d*)$', dirname)
    if match:
        return match.groups()
    else:
        return None

def item_files(path):
    """Given the base path of an item, return a list
    of the files associated with that item - ie. all
    files starting with this prefix except the .xml
    metadata file.

>>> item_files('../test/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003')
['../test/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003camera-1.raw16', '../test/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003left.wav', '../test/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003right.wav']
    """
    
    from glob import glob
    
    files = glob(path + '*')
    return [f for f in files if not f.endswith('.xml')]

    

def map_session(sessiondir, fn):
    """Call fn for every item in the given session
    fn is a callable that takes arguments:
    
    fn(spkr, session, component, item_path)
    
     - spkr is speaker id 1_123
     - session is session id [1, 2, 3, 4]
     - component is numerical component id
     - item_path is the base path to the item /home/foo/Spkr1_123/2/22/1_123_2_22
     
    return value is an iterator over the results of the individual
    function calls (calls are lazy via yield)
    
>>> paths = list(map_session('../test/Spkr2_2/Spkr2_2_Session1', lambda a, b, c, d: d ))
>>> len(paths)
54
>>> paths[2]
'../test/Spkr2_2/Spkr2_2_Session1/Session1_11/2_2_1_11_003'
    """
    
    (spath, sdirname) = os.path.split(sessiondir)
    (spkrid, sessionid) = parse_session_dir(sdirname)
    
    for cdir in os.listdir(sessiondir):
        if parse_component_dir(cdir) != None:
            (ss, componentid) = parse_component_dir(cdir)
            
            for ifile in os.listdir(os.path.join(sessiondir, cdir)):

                if ifile.endswith(".xml"):
                    (basename, ext) = os.path.splitext(os.path.basename(ifile))
                    path = os.path.join(sessiondir, cdir, basename)
                    
                    yield( fn(spkrid, sessionid, componentid, path) )


if __name__=='__main__':
        
        import doctest
        doctest.testmod()
    
    
    
    