#!/usr/bin/python
'''
@author : Suren
@desc : This file is used to merge audio and video into h264 format for the web. Audio is first downsampled before merging with the video.

'''
try:
    from django.conf import settings
    FFMPEG_PROGRAM = settings.FFMPEG_PROGRAM
    FFMPEG_OPTIONS = settings.FFMPEG_OPTIONS
except:
    #FFMPEG_PROGRAM = "/Applications/ffmpegX.app/Contents/Resources/ffmpeg"
    FFMPEG_PROGRAM = "/usr/local/bin/ffmpeg"
    #FFMPEG_OPTIONS = ["-vcodec", "libx264", "-an", "-vpre", "hq", "-crf", "22", "-threads", "0"]
    FFMPEG_OPTIONS = ["-vcodec", "h264", "-an"]

import sys, os, time, signal, shutil
from subprocess import Popen, PIPE
import re
from data import resample
    
def parse_ffmpeg_output(text):
    """Get relevant info from the ffmpeg output"""
    
    state = None
    result = {'input': '', 'output': ''}
    for line in text.split('\n'):
        if line.startswith("Input"):
            state = "INPUT"
        elif line.startswith("Output"):
            state = "OUTPUT"
        elif line.startswith("Stream mapping:"):
            state = "OTHER"
        
        if state == "INPUT":
            result['input'] += line + "\n"

        if state == "OUTPUT":
            result['output'] += line + "\n"
            
    # check for video input format
    m = re.search("Video: ([^,]+),", result['input'])
    if m:
        result['inputvideoformat'] = m.groups()[0]
    else:
        result['inputvideoformat'] = 'unknown'
        
    return result
            
    
def ffmpeg(sourcefile, targetfile, timeout=2160, options=[]):
    """Run FFMPEG with some command options, returning the output"""

    errormsg = ""
    
    ffmpeg = [FFMPEG_PROGRAM, "-y", "-i", sourcefile]
    ffmpeg += options
    ffmpeg += [targetfile]
 
    print " ".join(ffmpeg)
    
    process =  Popen(ffmpeg, stdout=PIPE, stderr=PIPE)
    start = time.time()
    
    while process.poll() == None: 
        if time.time()-start > timeout:
            # we've gone over time, kill the process  
            os.kill(process.pid, signal.SIGKILL)
            print "Killing ffmpeg process for", sourcefile
            errormsg = "Conversion of video took too long.  This site is only able to host relatively short videos."
            return errormsg
        
    status = process.poll()
    out,err = process.communicate()
    
    # should check status
    
    # return the error output - messages from ffmpeg
    return err

def extract_frame(sourcefile, targetfile):
    """Extract a single frame from the source video and 
    write it to the target file"""
    
    options = ["-s", "320x240", "-r", "1", "-f", "mjpeg"]
    
    err = ffmpeg(sourcefile, targetfile, options=options)


def probe_format(file):
    """Find the format of a video file via ffmpeg,
    return a format name, eg mpeg4, h264"""
    
    # for info, convert just one second to a null output format
    info_options = ["-f", "null", "-t", "1"]
    
    b = ffmpeg(file, "tmp", options=info_options)
    r = parse_ffmpeg_output(b)
     
    return r['inputvideoformat']



def convert_video(sourcefile, targetfile, force=False):
    """convert a video to h264 format
    if force=True, do the conversion even if the video is already
    h264 encoded, if False, then just copy the file in this case"""
    
    if not force:
        format = probe_format(sourcefile)
    else:
        format = 'force'
    
    if format == "h264":
        # just do a copy of the file
        shutil.copy(sourcefile, targetfile) 
    else: 
        # convert the video
        b = ffmpeg(sourcefile, targetfile, options=FFMPEG_OPTIONS)

    format = probe_format(targetfile)
    if  'h264' in format:
        return True
    else:
        print format
        return False 

def resample_video(sourcefile, targetfile, rate='24'):
    b = ffmpeg(sourcefile, targetfile, options=['-r', rate])
    #print 'b  from ffmeg : ' , b
    return True



def merge_video_audio(video_sourcefile, audio_sourcefile, targetfile, timeout=1560):
    errormsg = ""
    ffmpeg = [FFMPEG_PROGRAM, "-y", "-i", video_sourcefile, "-i", audio_sourcefile, "-vcodec", "h264", targetfile]
 
    #print " ".join(ffmpeg)
    
    process =  Popen(ffmpeg, stdout=PIPE, stderr=PIPE)
    start = time.time()
    
    while process.poll() == None: 
        if time.time()-start > timeout:
            # we've gone over time, kill the process  
            os.kill(process.pid, signal.SIGKILL)
            print "Killing ffmpeg process for merge"
            errormsg = "Conversion of video took too long."
            return errormsg
        
    status = process.poll()
    
    out,err = process.communicate()
    
    exit_code = process.wait()
    
    # should check status
    
    # return the error output - messages from ffmpeg
    return exit_code

        
if __name__=='__main__':
    import sys
    
    #if len(sys.argv) != 3:
    #   print "Usage: merge_video_audio.py <sourcefile> <targetfile>"
    #    exit()
        
    #sourcefile = sys.argv[1]
    #targetfile = sys.argv[2]
    
    #resample('/Users/surendrashrestha/Desktop/1_109_1_3_005-ch6-speaker.wav', '/Users/surendrashrestha/Desktop/Output/1_109_1_3_005-ch6-speaker-downsampled.wav')
    video_source = '/Users/surendrashrestha/Projects/BIGASC/BIGASC-Metadata/test/University_of_Canberra,_Canberra/Spkr1_109/Spkr1_109_Session1/Session1_3/1_109_1_3_001-camera-0-right.mp4'
    audio_source = '/Users/surendrashrestha/Desktop/Output/1_109_1_3_001-ch6-speaker.wav'
    converted_video_source = '/Users/surendrashrestha/Desktop/Output/converted/1_109_1_3_001-camera-0-right.mp4' 
    final_video_path = '/Users/surendrashrestha/Desktop/Output/merged/1_109_1_3_001-camera-0-right.mp4' 
    
    c = convert_video(video_source, converted_video_source)
    if c == True:
        print 'convert successful'
        m = merge_video_audio(converted_video_source, audio_source, final_video_path)
        if m == True:
            print 'merge and convert successful'
        else:
            print ' failed'
    else:
        print ' conversion failed'