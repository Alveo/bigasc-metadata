
if __name__=='__main__':
    
    import sys
    import os
    from annotate.maus import make_maus_processor, make_bpf_generator
    from data import site_sessions, map_session
    import configmanager
    import ingest
    
    if len(sys.argv) not in [2,3]:
        print "Usage: maus_session.py maus|bpf <limit>?"
        exit()  
        
    datadir = configmanager.get_config("DATA_DIR")
    outdir = configmanager.get_config("OUTPUT_DIR")
    what = sys.argv[1]
    if len(sys.argv) == 3:
        limit = int(sys.argv[2])
    else:
        limit = 10000000
    
    server_url = configmanager.get_config("SESAME_SERVER")
    server = ingest.SesameServer(server_url) 

    for d in os.listdir(datadir):
        
        sitedir = os.path.join(datadir, d)
        
        if os.path.isdir(sitedir):
            for session in site_sessions(sitedir):
                print "Session: ", session
                
                if what == 'maus':
                    result = [i for i in map_session(session, make_maus_processor(server, outdir))]
                else:
                    result = [i for i in map_session(session, make_bpf_generator(server, outdir))]
                print ""
                
                limit -= 1
                if limit <= 0:
                    print "Stopping after hitting limit"
                    exit()  
        
