'''
Resampling audio files

Created on Oct 31, 2012

@author: steve
'''

import sys, os, time, signal, shutil
import subprocess
from convert.namespaces import *
from convert import parse_media_filename

from rdflib import Literal

SOX_PROGRAM = ''
for d in ['/usr/bin/', '/usr/local/']:
    if os.path.exists(os.path.join(d, 'sox')):
        SOX_PROGRAM = os.path.join(d, 'sox')
        break
if SOX_PROGRAM == '':
    print "Can't find sox executable"
    exit()
    
## generate a component map, do this only once and we'll use it below
from convert.session import component_map
COMPONENT_MAP = component_map()

def resample(sourcefile, targetfile):
    """Generate a 16 bit, 16kHz version of this audio file
    
    return the name of the new file or None if something went wrong
    
>>> fn = "../test/1_1121_1_12_001-ch6-speaker.wav"
>>> fn16 = resample(fn)
>>> fn16
'../test/1_1121_1_12_001-ch6-speaker16.wav'
>>> os.path.exists(fn16)
True
>>> os.unlink(fn16)
>>> fn16a = resample(fn, '/tmp')
>>> fn16a
'/tmp/1_1121_1_12_001-ch6-speaker16.wav'
>>> os.unlink(fn16a)
    """
    
    (indir, filename) = os.path.split(sourcefile)
 
    outdir = os.path.dirname(targetfile)
    # make sure outdir exists
    try:
        os.makedirs(outdir)
    except:
        pass
    
    # convert to 16kHz/16 bit and normalise amplitude to -3db
    soxcmd = [SOX_PROGRAM, sourcefile, "-b16", targetfile, "rate", "-I", "16k", "gain", "-n", "-3" ] 
    
    #print " ".join(soxcmd) 

    # send err output to nowhere
    devnull = open(os.devnull, "w")
    process =  subprocess.Popen(soxcmd, stdout=devnull, stderr=devnull)

    while process.poll() == None:
        pass
 
    
    if os.path.exists(targetfile):
        return targetfile
    else:
        return None

def resampled_metadata(site, spkr, session, component, audiofile):
    """Generate metadata to describe the newly created
    resampled audio file, 
    basedir is the speaker directory that this audio file is found within
    audiofile is the basename of the old audio file
    
    We generate a new name for the audio file by adding 16 to the channel
    name:
    
    1_1121_1_12_001-ch6-speaker.wav -> 1_1121_1_12_001-ch6-speaker16.wav
    
    Return a tuple (path, meta) where
    path is the path name to the new file relative to some base directory
    meta is a list of triples that can be added to
    a graph"""
    
    # audiofile is like 1_123_1_2_003-ch6speaker.wav
    
    info = parse_media_filename(os.path.basename(audiofile))

    newfilename = audiofile.replace('ch6-speaker', 'ch6-speaker16')
    
    info['filename'] = newfilename
    info['site'] = site
    info['speaker'] = spkr
    info['session'] = session
    info['component'] = component
    info['componentName'] = COMPONENT_MAP[int(component)]
    
    # need to rewrite the channel in metadata
    info['channel'] = 'ch6-speaker16'
    path = DATA_URI_TEMPLATE % info
    
    # we add 'downsampled' to the front of the path since this will be kept separate
    # from the main data
    path = os.path.join('downsampled', path)
    
    item_uri = generate_item_uri(info['basename'])
    file_uri = DATA_NS[path]
    
    meta = [(item_uri, NS.media, file_uri),
              (file_uri, RDF.type, NS.MediaFile),
              (file_uri, NS.type, Literal(info['type'])),
              (file_uri, NS.channel, Literal(info['channel'])),
              (file_uri, NS.version, Literal(info['version'])),
              ]
    
    return (path, meta)

if __name__=='__main__':
        
        import doctest
        doctest.testmod()
        
    