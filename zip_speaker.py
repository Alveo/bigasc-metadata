"""
Resample the audio for a site/session/speaker and
save a copy in a new location
"""
import os, glob

import ingest 
from data import site_sessions, map_session, resample
from rdflib import Graph
import convert
import zipfile

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
    
    outfile = spkrid + ".zip"
    zfile = zipfile.ZipFile(outfile, 'w')
    
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
                                mauspath = os.path.join(site, sdir, sessiondir, cdir, item)
                                mausfile = os.path.join(mausdir, mauspath)
                                audioname = os.path.basename(item) + ".wav"
                                audiopath = os.path.join(site, sdir, sessiondir, cdir, audioname)
                                audiofile = os.path.join(audiodir, audiopath)
                                
                                # add mausfile and audiofile to zip
                                zfile.write(audiofile, audiopath)
                                zfile.write(mausfile, mauspath)
    zfile.close()
    



