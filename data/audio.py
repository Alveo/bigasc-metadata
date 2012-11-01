'''
Resampling audio files

Created on Oct 31, 2012

@author: steve
'''

import sys, os, time, signal, shutil
import subprocess


SOX_PROGRAM = "/usr/local/bin/sox"

def resample(sourcefile):
    """Generate a 16 bit, 16kHz version of this audio file
    and store it with the same basename but with a -16 postfix.
    
    1_1121_1_12_001-ch6-speaker.wav -> 1_1121_1_12_001-ch6-speaker-16.wav
    
    return the name of the new file or None if something went wrong
    
>>> fn = "../test/1_1121_1_12_001-ch6-speaker.wav"
>>> fn16 = resample(fn)
>>> fn16
'../test/1_1121_1_12_001-ch6-speaker-16.wav'
>>> os.path.exists(fn16)
True
>>>os.unlink(fn16)
    """

    (basename, ext) = os.path.splitext(sourcefile)
    targetfile = basename + "-16" + ext
 

    soxcmd = [SOX_PROGRAM, sourcefile, "-b16", targetfile, "rate", "-I", "16k"] 

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
        
    