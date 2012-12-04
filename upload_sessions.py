'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''

import ingest
from convert.ra_maptask import RAMapTask
from data import site_sessions

server_url = "http://115.146.93.47/openrdf-sesame/repositories/bigasc"

    
if __name__ == '__main__':
    
    import sys, os
    
    if len(sys.argv) not in [2, 3]:
        print "Usage upload_sessions.py <sessions file> | <site directory>  <limit>?"
        print " where <limit> gives the maximum number of sessions to upload"
        exit()

    if len(sys.argv) == 3:
        limit = int(sys.argv[2])
    else:
        limit = 1000
        
    server = ingest.SesameServer(server_url)
    # get RA spreadsheet data on maptasks
    maptask = RAMapTask()
    (spkr, map) = maptask.read_all()  
    
    
    if os.path.isdir(sys.argv[1]):
        sitedir = sys.argv[1]
        print "Finding sessions in site directory: ", sitedir
       
        for session in site_sessions(sitedir):
            print "Session: ", session  
            try:
                ingest.ingest_session(server, session, map)
            except Exception as ex:
                print "\tProblem with session...", ex
                
            limit += -1
            if limit <= 0:
                print "Stopping after hitting limit"
                exit()        
    else:
        sessionfile = sys.argv[1]
        print "Reading sessions from file:", sessionfile

        session_url_prefix = "https://austalk.edu.au/dav/bigasc/data/real/"
    
        h = open(sessionsfile)
        sessions = h.read().split() 
        
        for session in sessions:
            session_url = session_url_prefix + session
            print "Session", session
    
            try:
                ingest.ingest_session(server, session_url, map)
            except Exception as ex:
                print "\tProblem with session...", ex
            
            limit += -1
            if limit <= 0:
                print "Stopping after hitting limit"
                exit()  
    