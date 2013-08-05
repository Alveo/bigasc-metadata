'''
Created on Sep 25, 2012

@author: steve

upload metadata about some or all sessions for a site to the server

'''

import ingest

import configmanager
configmanager.configinit()

if __name__ == '__main__':

    import sys

    if len(sys.argv) not in [2, 3]:
        print "Usage output_graphs.py <directory> <server uri>?"
        print "  upload all RDF graphs in the given directory and sub-directories"
        print "  use the configured server URI unless one is specified on the command line"
        exit()

    dirname = sys.argv[1]
    if len(sys.argv) == 3:
        server_url = sys.argv[2]
    else:
        server_url = configmanager.get_config("SESAME_SERVER")

    server = ingest.SesameServer(server_url)

    server.upload_dir(dirname)

