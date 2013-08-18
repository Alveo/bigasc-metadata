"""
Resample the audio for a site/session/speaker and
save a copy in a new location
"""
import os, glob

import ingest 
from data import site_sessions, map_session, resample
from rdflib import Graph
from convert import generate_file_metadata, item_file_versions

import configmanager
configmanager.configinit()

## generate a component map, do this only once and we'll use it below
from convert.session import component_map
COMPONENT_MAP = component_map()

def make_processor(sessiondir, outdir, server):
    """Return a function to generate output to the given dir"""
     
    
    def process_item(site, spkr, session, component, item_path):
        """Process a single item - convert the audio 
        and write out to the new location
        take care to get all -n* files if present
        return a list of metadata triples that
        describe the new audio files and link
        them to the items.
        Return a count of the number of audio files processed
        """
        
        n = 0
        
        graph = Graph()
        goodfiles, badfiles = item_file_versions(item_path)
        
        for fn in goodfiles:
            # only worry about ch6-speaker
            if fn.find('ch6-speaker') >= 0:
                
                basename = os.path.basename(fn)
                # where do we put this new file
                newname = basename.replace('ch6-speaker', 'ch6-speaker16')
                newpath = item_file_path(basename, "downsampled")
                
                # generate metadata
                meta = generate_file_metadata(newpath)
                
                # skip generating the downsampled file if it's already there
                if not os.path.exists(os.path.join(outdir, newpath)):
                    resample(fn, os.path.join(outdir, newpath))
                    n += 1
                    
                # add in metadata for newly created audio tracks
                for tr in newmeta:
                    graph.add(tr)
        # upload the lot to the server
        server.output_graph(graph, item_file_path(basename+"-file", "metadata"))
        return n
    
    return process_item
    

if __name__=='__main__':
    
    import sys 
    
    if len(sys.argv) > 1:
        print "Usage: resample_audio.py <limit>?"
        exit()

    datadir = configmanager.get_config('DATA_DIR')
    outdir =  configmanager.get_config('OUTPUT_DIR')

    if len(sys.argv) == 2:
        limit = int(sys.argv[1])
    else:
        limit = 1000000
    
    server_url = configmanager.get_config("SESAME_SERVER")
    server = ingest.SesameServer(server_url)

    for d in os.listdir(datadir):
        
        sitedir = os.path.join(datadir, d)
        
        if os.path.isdir(sitedir):
            for session in site_sessions(sitedir):
                if configmanager.get_config('SHOW_PROGRESS', '') == 'yes':
                    print "Session: ", session
                
                files = [m for m in map_session(session, make_processor(sitedir, outdir, server))]
                
                if configmanager.get_config('SHOW_PROGRESS', '') == 'yes':
                    print sum(files)
                
                limit -= 1
                if limit <= 0:
                    print "Stopping after hitting limit"
                    exit()  
            
