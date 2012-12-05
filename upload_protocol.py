'''
Created on Sep 25, 2012

@author: steve

upload protocol metadata to the server

'''

import ingest

import configmanager
configmanager.configinit()

if __name__ == '__main__':
    
    server_url = configmanager.get_config("SESAME_SERVER")
    
    server = ingest.SesameServer(server_url)
    
    # clear the store if the second arg is 'clear
    if len(sys.argv) == 2 and sys.argv[1] == "clear":
        server.clear()
    elif len(sys.argv) != 1:
        print "Usage upload_protocol.py clear?"
        print "  if first arg is 'clear' then the store is cleared before uploading"
    
    
    ingest.ingest_protocol(server)
    
    