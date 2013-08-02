
if __name__=='__main__':
    
    import sys 
    from annotate.maus import make_maus_processor, make_bpf_generator
    from data import site_sessions, map_session
    import configmanager
    import ingest
    
    if len(sys.argv) not in [4,5]:
        print "Usage: maus_session.py <site_dir> <output_dir> maus|bpf <limit>?"
        exit()  
        
    sitedir = sys.argv[1]
    outdir = sys.argv[2] 
    what = sys.argv[3]
    if len(sys.argv) == 5:
        limit = int(sys.argv[4])
    else:
        limit = 10000
    
    server_url = configmanager.get_config("SESAME_SERVER")
    server = ingest.SesameServer(server_url) 

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
        
