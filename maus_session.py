
if __name__=='__main__':
    
    import sys 
    from annotate.maus import make_maus_processor
    from data import site_sessions, map_session
    import configmanager
    import ingest
    
    if len(sys.argv) not in [3,4]:
        print "Usage: maus_session.py <site_dir> <output_dir> <limit>?"
        exit()  
        
    sitedir = sys.argv[1]
    outdir = sys.argv[2] 
    if len(sys.argv) == 4:
        limit = int(sys.argv[3])
    else:
        limit = 10000
    
    server_url = configmanager.get_config("SESAME_SERVER")
    server = ingest.SesameServer(server_url) 

    for session in site_sessions(sitedir):
        print "Session: ", session
        
        result = [i for i in map_session(session, make_maus_processor(server, outdir))]
        print ""
        
        limit -= 1
        if limit <= 0:
            print "Stopping after hitting limit"
            exit()  
        
