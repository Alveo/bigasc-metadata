"""
Resample the audio for a site/session/speaker and
save a copy in a new location
"""
import os, glob

import ingest 
from data import site_sessions, map_session, resample, resampled_metadata
from rdflib import Graph
import convert 

import configmanager
configmanager.configinit()


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
        for audio in glob.glob(item_path + "*-ch6-speaker*.wav"):
            path = os.path.join(outdir, item_path[(len(os.path.dirname(sessiondir))+1):])
            path = os.path.dirname(path) 
            
            (newpath, newmeta) = resampled_metadata(site, spkr, session, component, os.path.basename(audio))
            # skip generating the downsampled file if it's already there
            if not os.path.exists(os.path.join(outdir, newpath)):
                resample(audio, os.path.join(outdir, newpath))
                n += 1
                
            # add in metadata for newly created audio tracks
            for tr in newmeta:
                graph.add(tr)
        # upload the lot to the server
        server.output_graph(graph, os.path.join(site, spkr, session, component, os.path.basename(item_path)+"-ds"))
        
        if configmanager.get_config('SHOW_PROGRESS', '') == 'yes':
            # progress...
            sys.stdout.write('.')
            sys.stdout.flush()
            
             
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
            
