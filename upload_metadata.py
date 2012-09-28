'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''

import ingest

if __name__ == '__main__':
    
    server_url = "http://115.146.94.199/openrdf-sesame/repositories/bigasc"
    session_url = "https://austalk.edu.au/dav/bigasc/data/real/Australian_National_University,_Canberra/Spkr1_178/Spkr1_178_Session1"
    
    server = ingest.SesameServer(server_url)
    
    server.clear()
    
    ingest.ingest_protocol(server)
    ingest.ingest_participants(server)
    
    # this should really be iterating over sessions
    #ingest.ingest_session(server, session_url)
    

    