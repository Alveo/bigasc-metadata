"""
Resample the audio for a site/session/speaker and
save a copy in a new location
"""
import os, glob

from data import site_sessions, map_session, resample, resampled_metadata

def make_processor(sessiondir, outdir):
    """Return a function to generate output to the given dir"""
    
    def process_item(spkr, session, component, item_path):
        """Process a single item - convert the audio 
        and write out to the new location
        take care to get all -n* files if present
        return a list of metadata triples that
        describe the new audio files and link
        them to the items.
        """
        
        meta = []
        for audio in glob.glob(item_path + "*-ch6-speaker*.wav"):
            path = os.path.join(outdir, item_path[(len(os.path.dirname(sessiondir))+1):])
            path = os.path.dirname(path) 
            
            results = resample(audio, path)
            
            for newaudio in results:
                meta.extend(resampled_metadata(site, spkr, session, component, newaudio))
            
        return meta
    
    return process_item
    

if __name__=='__main__':
    
    import sys 
    
    if len(sys.argv) != 3:
        print "Usage: resample_audio.py <site_dir> <output_dir>"
        exit()  
        
    sitedir = sys.argv[1]
    outdir = sys.argv[2]
    
    for session in site_sessions(sitedir):
        print "Session: ", session
        
        files = [m for m in map_session(session, make_processor(sitedir, outdir))]
        
        print "Processed ", len(files), "items"
        
            
