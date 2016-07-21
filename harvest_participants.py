'''
Created on Sep 25, 2012

@author: steve

upload metadata to the server

'''
import sys
import ingest
from convert.namespaces import NS

import configmanager
configmanager.configinit()

if __name__ == '__main__':
    
    if configmanager.get_config("USE_BLAZE_SERVER",'no')=='no':
        server_url = configmanager.get_config("SESAME_SERVER")
        server = ingest.SesameServer(server_url)
    else:
        server_url = configmanager.get_config("BLAZE_SERVER")
        server = ingest.BlazeServer(server_url)
    
    ingest.ingest_participants(server)
    
    