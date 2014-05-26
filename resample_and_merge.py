"""
@author : Suren
@date : 21 May 2014


"""
import os, glob
from multiprocessing import Process, Queue
import thread
#import ingest 
from data import pub_site_speakers, parse_session_dir
#from rdflib import Graph
#from convert import item_file_versions, item_file_basename, change_item_file_basename, item_file_path, item_files
from data import resample
#import configmanager
#configmanager.configinit()

## generate a component map, do this only once and we'll use it below
#from convert.session import component_map
#COMPONENT_MAP = component_map()


from merge_video_audio import *
import time

def process_item(speakers):
    print len(speakers), ' Speakers Found'
    for speaker in speakers:
        #graph = Graph()
        #versions = item_file_versions(item_path)
        #basename = item_file_basename(item_path)

        #print speaker
        #video_source = ''
        #audio_source = ''
        #session_dir =  os.path.join(speaker, 'Session1_3')
        #print ('session directory : ', session_dir)
        

        # Get speaker id to create the exact file name 
        # input : /University_of_Canberra,_Canberra/Spkr1_109/Spkr1_109_Session1
        # speaker_id : 1_109
        speaker_id = parse_session_dir(speaker.split('/')[-1])[0]

        # create the exact video and audio source file names
        video_file_name = speaker_id + video_component
        audio_file_name = speaker_id + audio_component

        video_source = os.path.join(speaker, 'Session1_3', video_file_name)
        original_audio_source = os.path.join(speaker, 'Session1_3', audio_file_name)
        
        # Temporary output for resampled audio
        resampled_audio_source = os.path.join(outdir, audio_file_name)

        if not os.path.exists(resampled_audio_source):
            print 'resampling audio'
            resample(original_audio_source, resampled_audio_source)
            print 'resample complete successful'



        # print 'video source: ', video_source
        # print 'audio source: ',resampled_audio_source

        # Only process to convert and merge files if the actual source files are present
        if (os.path.isfile(resampled_audio_source)  and os.path.isfile(video_source)) :
            print 'converting video to h264'
            converted_video_source = os.path.join('/Users/surendrashrestha/Desktop/Output/converted', video_file_name )
            #m = merge_video_audio( '/Users/surendrashrestha/Desktop/Output/1_109_1_3_005-camera-0-right.mp4','/Users/surendrashrestha/Desktop/Output/1_109_1_3_005-ch6-speaker.wav')
            
            try:
                #print 'video source: ', video_source
                #print 'converted video source: ', converted_video_source
                # convert the video to h264 format for web
                c = convert_video(video_source, converted_video_source)    
                
                if c == True:
                    merged_target_file = os.path.join('/Users/surendrashrestha/Desktop/Output/merged', video_file_name)    
                    print 'convert successful.. now trying to merge'
                    # merge the converted h264 video and resampled audio 

                    m = merge_video_audio(converted_video_source,  resampled_audio_source, merged_target_file)
                    # if exit code is 0 , the merging executed successfully
                    if m == 0:
                        # generate metadata
                        #convert.generate_file_metadata(graph, merged_target_file, "audio video merged")
                        # output metadata if any
                        #server.output_graph(bgraph, convert.item_file_path(basename+"-av", "versionselect-meta"))
                        
                        print ('merge successful')
                        # Delete temporary video and audio files
                        os.remove(converted_video_source)
                        os.remove(resampled_audio_source)
                        #final_file = os.path.join('/Users/surendrashrestha/Desktop/Output/merged/final', filename)
                    else: 
                        # exit code is not 0. so the merge process failed.
                        print 'merge failed'
                    
                else:
                    print 'video conversion to h264 failed'
                    #print m
            except:
                print 'unkown error'

'''           

def run_thread(speakers):
  proc = []
  q = Queue()
  for speaker in speakers:
    print 'inside thread'
    p = thread.start_new_thread(process_item(speaker))
    p.daemon = True
    proc.append(p)
    p.start()
  
  for p in proc:
    
    p.join()

'''




if __name__=='__main__':
    start_time = time.time()
    import sys 
    import fnmatch
    if len(sys.argv) > 2:
        print "Usage: resample_audio.py <limit>?"
        exit()

    #datadir = configmanager.get_config('DATA_DIR')
    #outdir =  configmanager.get_config('OUTPUT_DIR')
    datadir = '/Users/surendrashrestha/Projects/BIGASC/BIGASC-Metadata/test/data'
    outdir = '/Users/surendrashrestha/Desktop/Output'

    # declaring the variables to select the exact audio and video files.
    # can just change this section to choose different video / audio
    video_component = '_1_3_001-camera-0-right.mp4'
    audio_component = '_1_3_001-ch6-speaker.wav'

    if len(sys.argv) == 2:
        limit = int(sys.argv[1])

    else:
        limit = 1000000
    
    #server_url = configmanager.get_config("SESAME_SERVER")
    #server = ingest.SesameServer(server_url)

    #resample('/Users/surendrashrestha/Desktop/1_109_1_3_005-ch6-speaker.wav', '/Users/surendrashrestha/Desktop/Output/1_109_1_3_005-ch6-speaker-downsampled.wav')

    for d in os.listdir(datadir):
        
        sitedir = os.path.join(datadir, d)
        #print sitedir
        #print d
        if os.path.isdir(sitedir):
            # Get all the speakers in the data source directory
            speakers =[m for m in pub_site_speakers(sitedir)] 
            #print speakers
            #files = [m for m in map_session(session, make_processor(sitedir, outdir))]
            process_item(speakers)
            #run_thread(speakers)


            #if configmanager.get_config('SHOW_PROGRESS', '') == 'yes':
            #    print sum(files)
            
            limit -= 1
            if limit <= 0:
                print "Stopping after hitting limit"
                exit()  
        
    print 'time taken to execute: ', time.time() - start_time
