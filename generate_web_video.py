"""
@author : Suren
@date : 21 May 2014

Variable Names:
video_file_name     :   to find the exact video to merge (similar to basename), 
                        basename cannot be used initially because the exact filename is hardcoded
audio_file_name     :   original audio file name without extension
original_video_source : location of main video file specified by datadir
original_audio_source : location of main audio file specified by datadir

resampled_video_source : resampled video file with 30 frames per second (original : 48)
resampled_audio_source : downsampled audio file with 16 KHz

converted_video_source : h264 video

merged_target_file  : h264 video + resampled audio

Steps:
1. Resample audio
2. Resample video
3. Convert video to h264
4. Merge video and audio

"""
import os, glob
import multiprocessing
import thread
import ingest 
from data import pub_site_speakers, parse_session_dir
from rdflib import Graph
from convert import item_file_versions, item_file_basename, change_item_file_basename, item_file_path, item_files, generate_file_metadata
from data import resample
import configmanager
configmanager.configinit()

## generate a component map, do this only once and we'll use it below
from convert.session import component_map
COMPONENT_MAP = component_map()

from data.video import *
import time

def check_create_directory(path):
    if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                                
def process_speaker(speaker_dir):
    """Generate a sample video for a single speaker given the 
    root directory containing this speakers data
    Outputs a combined audio/video file and file metadata"""
        
    outdir =  configmanager.get_config('OUTPUT_DIR') 
    
    
    graph = Graph()        
    # Get speaker id to create the exact file name 
    # input : /University_of_Canberra,_Canberra/Spkr1_109
    # speaker_id : 1_109        

    m = re.search('Spkr(\d_\d+)', speaker_dir)

    if not m:
        return
    
    speaker_id = m.groups()[0]

    print "SPEAKER:", speaker_id

    # create the exact video and audio source file names
    video_file_name = speaker_id + video_component
    audio_file_name = speaker_id + audio_component

    video_source = item_path = os.path.join(speaker_dir, 'Spkr'+speaker_id+'_Session1', 'Session1_3', video_file_name)
    audio_source = os.path.join(speaker_dir, 'Spkr'+speaker_id+'_Session1', 'Session1_3', audio_file_name)
        
    basename = item_file_basename(item_path)

    merged_video = os.path.join(outdir, item_file_path(basename + "-webvideo.mp4", "webvideo"))



    if os.path.exists(video_source) and os.path.exists(audio_source):
      
        if not os.path.exists(os.path.dirname(merged_video)):
            os.makedirs(os.path.dirname(merged_video))
                
        # don't regenerate if it's already there
        if not os.path.exists(merged_video):
            m = merge_video_audio(video_source,  audio_source, merged_video)

        # generate metadata
        generate_file_metadata(graph, merged_video, "webvideo") 
        server.output_graph(graph, item_file_path(basename+"-wv", "webvideo-metadata"))
            
    else:
        print "Could not find audio and/or video to process: ", speaker_id




            

           

'''
@ todo  : Run the script in the server and test the execution speed
        : Since server has 16 CPUs, multiprocessing would be effective I believe
        : Test with only 8 CPUs
'''
def run_thread(speakers):

    i = 0
    pool = multiprocessing.Pool(multiprocessing.cpu_count()/2)

    pool.map(process_item, speakers)

    






if __name__=='__main__':
    start_time = time.time()
    import sys 
    import fnmatch
    if len(sys.argv) > 2:
        print "Usage: generate_web_video.py <limit>?"
        exit()

    datadir = configmanager.get_config('DATA_DIR')
    outdir =  configmanager.get_config('OUTPUT_DIR') 

    # declaring the variables to select the exact audio and video files.
    # can just change this section to choose different video / audio
    video_component = '_1_3_001-camera-0-right.mp4'
    audio_component = '_1_3_001-ch6-speaker.wav'

    if len(sys.argv) == 2:
        limit = int(sys.argv[1])

    else:
        limit = 1000000
    
    if configmanager.get_config("USE_BLAZE_SERVER",'no')=='no':
        server_url = configmanager.get_config("SESAME_SERVER")
        server = ingest.SesameServer(server_url)
    else:
        server_url = configmanager.get_config("BLAZE_SERVER")
        server = ingest.BlazeServer(server_url)
 

    for d in os.listdir(datadir):
        
        sitedir = os.path.join(datadir, d)        
        if os.path.isdir(sitedir):
            # Get all the speakers in the data source directory
            for sdir in os.listdir(sitedir):
                process_speaker(os.path.join(sitedir, sdir))
            
            if limit <= 0:
                print "Stopping after hitting limit"
                break  
            limit -= 1
                
    
    print 'time taken to execute: ', time.time() - start_time
