"""
Resample the audio for a site/session/speaker and
save a copy in a new location
"""
import os, glob

import ingest 
from data import site_sessions, map_session, resample
from rdflib import Graph
import convert

import configmanager
configmanager.configinit()

if __name__=='__main__':
    
    import sys 
    
    if len(sys.argv) != 2:
        print "Usage: zip_speaker.py <spkrid>"
        exit()

    datadir = configmanager.get_config('DATA_DIR')
    outdir =  configmanager.get_config('OUTPUT_DIR')

    spkrid = sys.argv[1]
    
    audiodir = os.path.join(outdir, 'downsampled')
    mausdir = os.path.join(outdir, 'MAUS')
    
    for site in os.listdir(mausdir):
        
        sitedir = os.path.join(mausdir, site)
        
        if os.path.isdir(sitedir):
            for sdir in os.listdir(sitedir):
                if sdir == spkrid:
                    speakerdir = os.path.join(sitedir, sdir)
                    for sessiondir in os.listdir(speakerdir):
                        for cdir in os.listdir(os.path.join(speakerdir, sessiondir)):
                            compdir = os.path.join(speakerdir, sessiondir, cdir)
                            for item in os.listdir(compdir):
                                mausfile = os.path.join(compdir, item)
                                audioname = os.path.basename(item) + ".wav"
                                audiofile = os.path.join(audiodir, site, sdir, sessiondir, cdir, audioname)
                                
                                # add mausfile and audiofile to zip
                                
                                
            
