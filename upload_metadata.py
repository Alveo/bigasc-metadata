'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''

import ingest

if __name__ == '__main__':
    
    server_url = "http://115.146.94.199/openrdf-sesame/repositories/bigasc" 
    
    server = ingest.SesameServer(server_url)
    
    server.clear()
    
    ingest.ingest_protocol(server)
    ingest.ingest_participants(server)
    
    