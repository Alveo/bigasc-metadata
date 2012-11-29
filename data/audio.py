'''
Resampling audio files

Created on Oct 31, 2012

@author: steve
'''

import sys, os, time, signal, shutil
import subprocess

SOX_PROGRAM = ''
for d in ['/usr/bin/', '/usr/local/']:
    if os.path.exists(os.path.join(d, 'sox')):
        SOX_PROGRAM = os.path.join(d, 'sox')
        break
if SOX_PROGRAM == '':
    print "Can't find sox executable"
    exit()
    

def resample(sourcefile, outdir=None):
    """Generate a 16 bit, 16kHz version of this audio file
    and store it with the same basename but with a -16 postfix.
    
    1_1121_1_12_001-ch6-speaker.wav -> 1_1121_1_12_001-ch6-speaker-16.wav
    
    if outdir is given, the new file is written to this directory
    otherwise it is written to the same location as sourcefile
    
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
 
    if outdir==None:
        outdir = indir
    else:
        # make sure outdir exists
        try:
            os.makedirs(outdir)
        except:
            pass
    
    newfilename = filename.replace('ch6-speaker', 'ch6-speaker16')
    
    targetfile = os.path.join(outdir, newfilename)
        
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

def resampled_metadata(audiofile):
    """Generate metadata to describe the newly created
    resampled audio file, 
    basedir is the speaker directory that this audio file is found within
    audiofile is the full path to the new audio file
    
    Return a list of triples that can be added to
    a graph"""
    
    # audiofile is like 1_123_1_2_003-ch6speaker16.wav
    
    item_uri = 
    file_uri = 
    info = parse_media_filename(os.path.basename(audiofile))
    
    result = [(item_uri, NS.media, file_uri),
              (file_uri, RDF.type, NS.MediaFile),
              (file_uri, NS.type, info['type']),
              (file_uri, NS.channel, info['channel']),
              (file_uri, NS.version, info['version']),
              ]
    
    return result

if __name__=='__main__':
        
        import doctest
        doctest.testmod()
        
    