'''
Resampling audio files

Created on Oct 31, 2012

@author: steve
'''

import sys, os, time, signal, shutil
import subprocess


SOX_PROGRAM = "/usr/bin/sox"

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
'../test/1_1121_1_12_001-ch6-speaker-16.wav'
>>> os.path.exists(fn16)
True
>>> os.unlink(fn16)
>>> fn16a = resample(fn, '/tmp')
>>> fn16a
'/tmp/1_1121_1_12_001-ch6-speaker-16.wav'
>>> os.unlink(fn16a)
    """
    
    (indir, filename) = os.path.split(sourcefile)
    (basename, ext) = os.path.splitext(filename)
 
    if outdir==None:
        outdir = indir
    else:
        # make sure outdir exists
        try:
            os.makedirs(outdir)
        except:
            pass
        
    targetfile = os.path.join(outdir, basename + "-16" + ext)
        
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
    



if __name__=='__main__':
        
        import doctest
        doctest.testmod()
        
    