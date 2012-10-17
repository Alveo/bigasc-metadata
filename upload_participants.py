'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''

import ingest

if __name__ == '__main__':
    
    server_url = "http://sesame.stevecassidy.net//openrdf-sesame/repositories/bigasc" 
    
    server = ingest.SesameServer(server_url)
    
    ingest.ingest_participants(server)
    
    