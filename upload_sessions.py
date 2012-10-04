'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''

import ingest

if __name__ == '__main__':
    
    import sys
    
    if len(sys.argv) != 2:
        print "Usage upload_sessions.py <sessions file>"
        exit()
        
    sessionsfile = sys.argv[1]
    
    server_url = "http://115.146.94.199/openrdf-sesame/repositories/bigasc"
    session_url_prefix = "https://austalk.edu.au/dav/bigasc/data/real/"
    
    server = ingest.SesameServer(server_url)
    
    h = open(sessionsfile)
    sessions = h.read().split() 
    for session in sessions:
        session_url = session_url_prefix + session
        print "Session", session
        try:
            ingest.ingest_session(server, session_url)
        except:
            print "\tProblem with session..."
    