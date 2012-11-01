'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''

import ingest
from convert.ra_maptask import RAMapTask

if __name__ == '__main__':
    
    import sys
    
    if len(sys.argv) != 2:
        print "Usage upload_sessions.py <sessions file>"
        exit()
        
    sessionsfile = sys.argv[1]
    
    server_url = "http://115.146.93.47/openrdf-sesame/repositories/bigasc"
    session_url_prefix = "https://austalk.edu.au/dav/bigasc/data/real/"
    
    server = ingest.SesameServer(server_url)
    
    # get RA spreadsheet data on maptasks
    maptask = RAMapTask()
    (spkr, map) = maptask.read_all()
    
    h = open(sessionsfile)
    sessions = h.read().split() 
    for session in sessions:
        session_url = session_url_prefix + session
        print "Session", session

        try:
            ingest.ingest_session(server, session_url, map)
        except Exception as ex:
            print "\tProblem with session...", ex
    