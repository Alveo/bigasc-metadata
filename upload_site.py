'''
Created on Sep 25, 2012

@author: steve

upload metadata about some or all sessions for a site to the server

'''

import ingest
from convert.ra_maptask import RAMapTask
from data import site_sessions

import configmanager
configmanager.configinit()
    
if __name__ == '__main__':
    
    import sys, os
    
    if len(sys.argv) not in [2, 3]:
        print "Usage upload_site.py <site directory>  <limit>?"
        print " where <limit> gives the maximum number of sessions to upload"
        exit()

    if len(sys.argv) == 3:
        limit = int(sys.argv[2])
    else:
        limit = 1000
    
    server_url = configmanager.get_config("SESAME_SERVER") 
    
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
                ingest.ingest_session_map(server, session, map)
            except Exception as ex:
                print "\tProblem with session...", ex
                
            limit += -1
            if limit <= 0:
                print "Stopping after hitting limit"
                exit()        
    